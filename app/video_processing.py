from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageFilter
from rembg import new_session, remove

from .asset_store import PROCESSED_DIR


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    raw_frames_dir: Path
    transparent_frames_dir: Path
    frame_count: int
    frame_interval_ms: int


def process_video_to_transparent_frames(
    video_path: Path,
    fps: int = 15,
    height: int = 360,
    model_name: str = "u2netp",
    edge_cleanup: bool = True,
) -> ProcessingResult:
    video_path = video_path.expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video does not exist: {video_path}")

    output_root = _output_root_for(video_path)
    raw_frames_dir = output_root / "raw_frames"
    transparent_frames_dir = output_root / "transparent_frames"
    _prepare_output_dir(output_root)
    raw_frames_dir.mkdir(parents=True, exist_ok=True)
    transparent_frames_dir.mkdir(parents=True, exist_ok=True)

    _extract_frames(video_path, raw_frames_dir, fps=fps, height=height)
    raw_frames = sorted(raw_frames_dir.glob("frame_*.png"))
    if not raw_frames:
        raise RuntimeError("No frames were extracted from the video.")

    session = new_session(model_name)
    for index, raw_frame in enumerate(raw_frames, start=1):
        output_frame = transparent_frames_dir / raw_frame.name
        output_bytes = remove(raw_frame.read_bytes(), session=session)
        output_frame.write_bytes(output_bytes)
        if edge_cleanup:
            _clean_alpha_edge(output_frame)
        print(f"processed {index}/{len(raw_frames)}: {output_frame.name}", flush=True)

    return ProcessingResult(
        raw_frames_dir=raw_frames_dir,
        transparent_frames_dir=transparent_frames_dir,
        frame_count=len(raw_frames),
        frame_interval_ms=max(1, round(1000 / fps)),
    )


def _output_root_for(video_path: Path) -> Path:
    safe_stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in video_path.stem)
    return PROCESSED_DIR / safe_stem


def _prepare_output_dir(output_root: Path) -> None:
    output_root = output_root.resolve()
    processed_root = PROCESSED_DIR.resolve()
    if processed_root not in output_root.parents and output_root != processed_root:
        raise RuntimeError(f"Refusing to clear path outside processed dir: {output_root}")
    if output_root.exists():
        shutil.rmtree(output_root)


def _extract_frames(video_path: Path, raw_frames_dir: Path, fps: int, height: int) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output_pattern = raw_frames_dir / "frame_%04d.png"
    command = [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps},scale=-2:{height}",
        str(output_pattern),
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg frame extraction failed")


def _clean_alpha_edge(frame_path: Path, threshold: int = 18, padding: int = 20) -> None:
    image = Image.open(frame_path).convert("RGBA")
    r, g, b, alpha = image.split()

    # Remove low-confidence transparent residue that often appears as dark outlines.
    alpha = alpha.point(lambda value: 0 if value < threshold else value)
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.35))

    rgb = Image.merge("RGB", (r, g, b))
    rgb = _neutralize_semitransparent_dark_pixels(rgb, alpha)
    cleaned = Image.merge("RGBA", (*rgb.split(), alpha))

    bbox = alpha.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        cleaned = cleaned.crop((left, top, right, bottom))
        canvas = Image.new("RGBA", (cleaned.width + padding * 2, cleaned.height + padding * 2), (0, 0, 0, 0))
        canvas.alpha_composite(cleaned, (padding, padding))
        cleaned = canvas

    cleaned.save(frame_path)


def _neutralize_semitransparent_dark_pixels(rgb: Image.Image, alpha: Image.Image) -> Image.Image:
    rgb_data = list(rgb.getdata())
    alpha_data = list(alpha.getdata())
    output: list[tuple[int, int, int]] = []

    for (red, green, blue), opacity in zip(rgb_data, alpha_data, strict=True):
        if 0 < opacity < 230:
            lift = round((255 - opacity) * 0.45)
            output.append(
                (
                    min(255, red + lift),
                    min(255, green + lift),
                    min(255, blue + lift),
                )
            )
        elif opacity == 0:
            output.append((0, 0, 0))
        else:
            output.append((red, green, blue))

    cleaned = Image.new("RGB", rgb.size)
    cleaned.putdata(output)
    return cleaned

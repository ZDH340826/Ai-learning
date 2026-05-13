from __future__ import annotations

import argparse
from pathlib import Path

from app.config import load_config, save_config
from app.video_processing import process_video_to_transparent_frames


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract cat video frames and remove background.",
    )
    parser.add_argument("video", nargs="?", type=Path, help="Imported cat video path.")
    parser.add_argument("--fps", type=int, default=15, help="Output animation FPS.")
    parser.add_argument("--height", type=int, default=360, help="Processing frame height.")
    parser.add_argument("--model", default="u2netp", help="rembg model name.")
    parser.add_argument("--no-edge-cleanup", action="store_true", help="Disable alpha edge cleanup.")
    args = parser.parse_args()

    config = load_config()
    video = args.video or (Path(config.active_asset_path) if config.active_asset_path else None)
    if video is None:
        raise SystemExit("No video path provided and no active asset is configured.")
    if not video.exists():
        raise SystemExit(f"Video does not exist: {video}")

    result = process_video_to_transparent_frames(
        video,
        fps=args.fps,
        height=args.height,
        model_name=args.model,
        edge_cleanup=not args.no_edge_cleanup,
    )
    config.active_asset_path = str(video.resolve())
    config.active_asset_name = video.name
    config.asset_status = "processed_transparent_frames"
    config.processed_frames_dir = str(result.transparent_frames_dir)
    config.frame_interval_ms = result.frame_interval_ms
    save_config(config)

    print(f"frames: {result.frame_count}")
    print(f"transparent_frames_dir: {result.transparent_frames_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

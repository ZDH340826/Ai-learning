from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .asset_store import ensure_asset_dirs
from .config import load_config
from .pet_window import PetWindow


def main() -> int:
    ensure_asset_dirs()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = PetWindow(load_config())
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


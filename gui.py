import sys
from src.gui.desktop_app import PhotoOrganizerGUI


def main() -> None:
    app = PhotoOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()

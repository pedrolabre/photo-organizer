import threading
import time
import webbrowser
from app import app
from src.utils.logger import init_logger


def open_browser(url: str, delay: float = 1.0) -> None:
    time.sleep(delay)
    webbrowser.open(url)


def main() -> None:
    init_logger(level="INFO")
    host = "127.0.0.1"
    port = 5000
    url = f"http://{host}:{port}"
    browser_thread = threading.Thread(
        target=open_browser,
        args=(url, 1.2),
        daemon=True,
    )
    browser_thread.start()
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

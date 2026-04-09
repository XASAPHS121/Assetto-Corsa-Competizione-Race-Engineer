"""
ACC Race Engineer — Dev Mode (Hot Reload)
Watches for file changes and auto-restarts the app.

Usage:
    python dev.py
"""

import sys
import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

APP_DIR = Path(__file__).parent
WATCH_DIRS = [APP_DIR / "ui", APP_DIR / "core", APP_DIR / "data"]
MAIN_SCRIPT = APP_DIR / "main.py"


class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_reload = 0

    def start_app(self):
        self.stop_app()
        print("\n[+] Starting ACC Race Engineer...")
        self.process = subprocess.Popen([sys.executable, str(MAIN_SCRIPT)])

    def stop_app(self):
        if self.process and self.process.poll() is None:
            print("[-] Stopping app...")
            self.process.terminate()
            self.process.wait(timeout=5)

    def on_modified(self, event):
        if not event.src_path.endswith(".py") and not event.src_path.endswith(".json"):
            return
        # Debounce: ignore events within 1 second of last reload
        now = time.time()
        if now - self.last_reload < 1.0:
            return
        self.last_reload = now
        print(f"\n[~] Changed: {Path(event.src_path).name}")
        self.start_app()


def main():
    print("=" * 50)
    print("  ACC Race Engineer — Dev Mode (Hot Reload)")
    print("=" * 50)
    print(f"  Watching: ui/, core/, data/")
    print(f"  Edit any .py or .json file to auto-restart")
    print(f"  Press Ctrl+C to stop")
    print("=" * 50)

    handler = ReloadHandler()
    handler.start_app()

    observer = Observer()
    for watch_dir in WATCH_DIRS:
        if watch_dir.exists():
            observer.schedule(handler, str(watch_dir), recursive=True)
    # Also watch main.py and theme changes
    observer.schedule(handler, str(APP_DIR), recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[x] Shutting down dev mode...")
        handler.stop_app()
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

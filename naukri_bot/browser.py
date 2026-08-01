import os
import shutil
import subprocess
import sys
import threading
import time

from .logger import log


def get_active_app_macos() -> str:
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of first application process whose frontmost is true',
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def restore_focus_macos(app_name: str) -> None:
    if sys.platform != "darwin" or not app_name:
        return
    try:
        subprocess.run(
            ["osascript", "-e", f'tell application "{app_name}" to activate'],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _focus_guard_loop(app_name: str, duration: float = 5.0) -> None:
    end_time = time.time() + duration
    while time.time() < end_time:
        restore_focus_macos(app_name)
        time.sleep(0.15)


def start_focus_guard(app_name: str, duration: float = 5.0) -> None:
    if sys.platform != "darwin" or not app_name:
        return
    t = threading.Thread(
        target=_focus_guard_loop, args=(app_name, duration), daemon=True
    )
    t.start()


def hide_browser_on_macos() -> None:
    if sys.platform != "darwin":
        return
    script = """
    tell application "System Events"
        repeat with procName in {"Chromium", "Google Chrome", "Chrome"}
            try
                if exists process procName then
                    set visible of process procName to false
                end if
            end try
        end repeat
    end tell
    """
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _offscreen_launch_args() -> list:
    args = [
        "--window-position=-32000,-32000",
        "--window-size=1280,900",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-infobars",
        "--disable-extensions",
        "--start-minimized",
    ]
    if sys.platform == "linux":
        args += [
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]
    return args


class XvfbDisplay:
    """Manages a virtual X display (Xvfb) for headless Linux servers."""

    def __init__(self, display: str = ":99"):
        self.display = display
        self._proc = None

    def start(self) -> bool:
        if sys.platform != "linux":
            return False
        if not shutil.which("Xvfb"):
            log(
                "Xvfb not found. Install it with: sudo apt-get install xvfb\n"
                "Then rerun the script."
            )
            return False
        env = os.environ.copy()
        env["DISPLAY"] = self.display
        self._proc = subprocess.Popen(
            ["Xvfb", self.display, "-screen", "0", "1280x900x24"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.environ["DISPLAY"] = self.display
        time.sleep(0.8)
        log(f"Xvfb virtual display started on {self.display}")
        return True

    def stop(self) -> None:
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
            log("Xvfb virtual display stopped.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


def open_offscreen_browser(p, session_file: str = None):
    """
    Launch a non-headless Chromium positioned off-screen.
    Naukri blocks true headless; off-screen is invisible and works.
    Returns (browser, context, page).
    """
    previous_app = get_active_app_macos()
    start_focus_guard(previous_app, duration=5.0)

    args = _offscreen_launch_args()
    browser = p.chromium.launch(headless=False, args=args)

    time.sleep(0.5)
    hide_browser_on_macos()

    ctx_kwargs = {}
    if session_file and os.path.exists(session_file):
        ctx_kwargs["storage_state"] = session_file
    context = browser.new_context(**ctx_kwargs)
    page = context.new_page()
    return browser, context, page

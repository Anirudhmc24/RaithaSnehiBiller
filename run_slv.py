"""
SLV Traders — Standalone Launcher
Runs Streamlit in-process and opens a native-feeling desktop window.
"""
import os
import sys
import time
import socket
import subprocess
import threading
import webbrowser

def resolve_path(path):
    """Resolve path whether running frozen (.exe) or from source."""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(os.path.join(sys._MEIPASS, path))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def wait_for_server(port, timeout=30):
    """Block until the Streamlit server is accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False

def find_browser_exe():
    """Try to locate Edge or Chrome on Windows."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None

def open_app_window(port):
    """Open the app in a native-feeling window (no URL bar, no tabs)."""
    url = f"http://localhost:{port}"
    browser_exe = find_browser_exe()
    if browser_exe:
        subprocess.Popen([
            browser_exe,
            f"--app={url}",
            "--new-window",
            f"--window-size=1280,800",
        ])
    else:
        webbrowser.open(url)

def open_browser_when_ready(port):
    """Background thread: wait for server, then open the window."""
    print("[*] Waiting for server to start...")
    if wait_for_server(port):
        print(f"[✓] Server ready! Opening application window...")
        open_app_window(port)
    else:
        print(f"[!] Server did not start in time. Open manually: http://localhost:{port}")

def main():
    # Prevent multiprocessing fork-bomb in frozen exe
    import multiprocessing
    multiprocessing.freeze_support()

    port = find_free_port()
    script_path = resolve_path("main.py")

    print("╔══════════════════════════════════════════════════╗")
    print("║   Sri Lakshmi Venkateshwara Traders              ║")
    print("║   Fertilizer & Pesticide Management System       ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║   Starting on port {port}...                     ║")
    print("║   Close this window to stop the application.     ║")
    print("╚══════════════════════════════════════════════════╝")

    # Launch browser-opener in a background thread
    t = threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True)
    t.start()

    # Run Streamlit IN-PROCESS (not as a subprocess)
    # This avoids the sys.executable fork-bomb issue with frozen exes
    from streamlit.web import bootstrap
    flag_options = {
        "server.port": port,
        "server.headless": True,
        "global.developmentMode": False,
        "browser.gatherUsageStats": False,
        "server.fileWatcherType": "none",  # no file watcher in frozen exe
    }
    bootstrap.run(script_path, False, [], flag_options)

if __name__ == "__main__":
    main()

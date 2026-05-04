"""
SLV Traders — Standalone Launcher
Opens the Streamlit app in a native-feeling desktop window
using Edge/Chrome's --app mode (no URL bar, no tabs).
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
    """
    Try to locate Edge or Chrome on Windows.
    Returns the path if found, else None.
    """
    candidates = [
        # Microsoft Edge (preferred — present on all Win10/11)
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        # Google Chrome
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None

def open_app_window(port):
    """
    Open the app in a native-feeling window.
    Uses --app flag on Edge/Chrome to hide the URL bar and tabs.
    Falls back to the default browser if neither is found.
    """
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
        # Fallback: open in default browser
        webbrowser.open(url)

def main():
    port = find_free_port()
    script_path = resolve_path("main.py")

    print("╔══════════════════════════════════════════════════╗")
    print("║   Sri Lakshmi Venkateshwara Traders              ║")
    print("║   Fertilizer & Pesticide Management System       ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║   Starting on port {port}...                     ║")
    print("║   Close this window to stop the application.     ║")
    print("╚══════════════════════════════════════════════════╝")

    # Launch Streamlit server in the background
    env = os.environ.copy()
    server_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", script_path,
            "--global.developmentMode=false",
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        env=env,
    )

    # Wait for server to be ready, then open window
    print("[*] Waiting for server to start...")
    if wait_for_server(port):
        print(f"[✓] Server ready! Opening application window...")
        open_app_window(port)
    else:
        print("[!] Server did not start in time. Please open manually:")
        print(f"    http://localhost:{port}")

    # Keep alive until server exits (user closes the console)
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server_proc.terminate()
        server_proc.wait()

if __name__ == "__main__":
    main()

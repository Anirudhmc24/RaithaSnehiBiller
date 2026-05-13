"""
SLV Traders — Standalone Launcher
Opens the Streamlit app as a tab in your default browser.
"""
import os
import sys
import multiprocessing

def resolve_path(path):
    """Resolve path whether running frozen (.exe) or from source."""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(os.path.join(sys._MEIPASS, path))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

if __name__ == "__main__":
    multiprocessing.freeze_support()

    script_path = resolve_path("main.py")

    print("+--------------------------------------------------+")
    print("|   Raitha Snehi Biller                            |")
    print("|   Fertilizer & Pesticide Management System       |")
    print("+--------------------------------------------------+")
    print("|   Starting... App will open in your browser.     |")
    print("|   Close this window to stop the application.     |")
    print("+--------------------------------------------------+")

    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit", "run", script_path,
        "--global.developmentMode=false",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())

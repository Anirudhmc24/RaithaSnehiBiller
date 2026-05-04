import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # The application is not frozen
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    # Path to the streamlit main app
    script_path = resolve_path("main.py")
    
    sys.argv = [
        "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
        "--server.port=8501",
        "--server.headless=true"
    ]
    sys.exit(stcli.main())

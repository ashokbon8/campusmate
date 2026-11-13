"""Start one local CampusMate server and open the website when it is ready."""
from pathlib import Path
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if not (root/'frontend/dist/index.html').is_file():
        print('Built website missing. Extract the complete CampusMate_Final.zip again.')
        return 1
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
        if probe.connect_ex(('127.0.0.1',5173)) == 0:
            print('Port 5173 is already in use. Close the old CampusMate server window and run again.')
            return 1
    os.chdir(root/'backend')
    sys.path.insert(0,str(root/'backend'))
    os.environ.setdefault('CAMPUSMATE_DATASET','jscoe')
    os.environ.setdefault('CAMPUSMATE_SEED','1')
    import uvicorn
    from app.local import create_local_app

    def open_when_ready():
        for _ in range(80):
            try:
                with urllib.request.urlopen('http://127.0.0.1:5173/api/health',timeout=1) as response:
                    if response.status == 200:
                        webbrowser.open('http://localhost:5173')
                        return
            except (OSError,urllib.error.URLError):
                pass
            time.sleep(.25)

    print('CampusMate: http://localhost:5173')
    print('Keep this terminal open. Press Ctrl+C to stop the website.')
    threading.Thread(target=open_when_ready,daemon=True).start()
    uvicorn.run(create_local_app(),host='127.0.0.1',port=5173)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

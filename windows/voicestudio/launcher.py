"""Start the local VoiceStudio backend, then optionally serve its stdio MCP."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESOURCE=ROOT/'VoiceStudio/resources'
PYTHON=RESOURCE/'.venv/Scripts/python.exe'
PORT=3917
BASE=f'http://127.0.0.1:{PORT}'

def environment():
    env=os.environ.copy()
    env.update(json.loads((HERE/'environment.json').read_text(encoding='utf-8')))
    return env

def healthy():
    try:
        with urllib.request.urlopen(BASE+'/health',timeout=2) as response:
            return response.status==200
    except (OSError,urllib.error.URLError):
        return False

def ensure_backend():
    if healthy(): return
    import msvcrt
    HERE.mkdir(parents=True,exist_ok=True)
    with (HERE/'startup.lock').open('a+b') as lock:
        lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
        deadline=time.monotonic()+180
        while True:
            try:
                msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError:
                if healthy(): return
                if time.monotonic()>deadline: raise RuntimeError('VoiceStudio startup lock timed out')
                time.sleep(1)
        try:
            if healthy(): return
            with (HERE/'backend-out.log').open('ab') as out, (HERE/'backend-error.log').open('ab') as err:
                process=subprocess.Popen([str(PYTHON),'-u',str(RESOURCE/'backend/main.py')],
                    cwd=RESOURCE,env=environment(),stdin=subprocess.DEVNULL,stdout=out,stderr=err,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
            (HERE/'backend.pid').write_text(str(process.pid))
            while time.monotonic()<deadline:
                if healthy(): return
                if process.poll() is not None:
                    raise RuntimeError(f'VoiceStudio exited {process.returncode}; see {HERE / "backend-error.log"}')
                time.sleep(1)
            raise RuntimeError(f'VoiceStudio did not become ready; see {HERE / "backend-error.log"}')
        finally:
            lock.seek(0); msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--mcp',action='store_true'); p.add_argument('--start',action='store_true')
    args=p.parse_args()
    ensure_backend()
    if args.mcp:
        return subprocess.call([str(PYTHON),str(RESOURCE/'backend/mcp_server.py')],cwd=RESOURCE,env=environment())
    print('VoiceStudio ready at '+BASE)
    return 0

if __name__=='__main__':
    raise SystemExit(main())

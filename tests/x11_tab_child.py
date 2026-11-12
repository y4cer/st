"""Controlled real PTY child used only by test_tabs_x11.py."""
import base64
import json
import os
from pathlib import Path
import select
import signal
import struct
import termios
import tty
import fcntl

root=Path(os.environ['ST_X11_TEST_DIR']); stem=root/str(os.getpid())
path=stem.with_suffix('.cmd');os.mkfifo(path)
control=os.open(path,os.O_RDWR|os.O_NONBLOCK)
tty.setraw(0)
def size(*_):
    rows,cols,_,_=struct.unpack('HHHH',fcntl.ioctl(0,termios.TIOCGWINSZ,b'\0'*8))
    stem.with_suffix('.size').write_text(json.dumps([cols,rows]))
signal.signal(signal.SIGWINCH,size);size()
os.write(1,f'\x1b]2;session-{os.getpid()}\x07Tab {os.getpid()} ready\r\n'.encode())
stem.with_suffix('.ready').touch()
pending=b''
with stem.with_suffix('.input').open('ab',buffering=0) as log:
    while True:
        readable,_,_=select.select([0,control],[],[])
        if 0 in readable:
            data=os.read(0,65536)
            if not data:break
            log.write(data)
        if control in readable:
            pending+=os.read(control,65536)
            while b'\n' in pending:
                line,pending=pending.split(b'\n',1);cmd=json.loads(line)
                if cmd['op']=='exit':raise SystemExit(0)
                os.write(1,base64.b64decode(cmd['data']))

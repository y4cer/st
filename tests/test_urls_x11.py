#!/usr/bin/env python3
"""Plain-URI scenarios adapted from Shitty, through real st/X11/PTY events.
A private fake xdg-open records argv; no browser or external URL is contacted.
"""
from test_tabs_x11 import (C, I, U, ROOT, open_display, close_display,
                          rootwindow, window, prop, focus, flush, chord, keycode,
                          keysym, keyevent, button, motion, translate, screenshot, until)
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def main():
    xvfb = os.environ.get('ST_XVFB') or shutil.which('Xvfb')
    if not xvfb:
        raise SystemExit('Xvfb required for make test-x11')
    display = server = st = None
    out = ROOT / 'tests/bin'
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='st-urls-x11-') as directory:
        data = Path(directory)
        opener = data / 'xdg-open'
        opener.write_text('#!' + sys.executable + '\nimport json,os,sys\n'
                          'with open(os.environ["ST_URL_LOG"],"a") as f: '
                          'f.write(json.dumps(sys.argv[1:])+"\\n")\n')
        opener.chmod(0o755)
        opened = data / 'opened.jsonl'
        with (out / 'urls-x11.log').open('wb') as log:
            try:
                read, write = os.pipe()
                server = subprocess.Popen([xvfb, '-displayfd', str(write), '-screen', '0',
                                           '1024x768x24', '-nolisten', 'tcp'],
                                          pass_fds=[write], stdout=log, stderr=log)
                os.close(write)
                with os.fdopen(read) as stream:
                    name = ':' + stream.readline().strip()
                display = until(lambda: open_display(name.encode()), 'X server')
                env = dict(os.environ, DISPLAY=name, ST_X11_TEST_DIR=directory,
                           ST_URL_LOG=str(opened), PATH=directory + ':' + os.environ['PATH'])
                st = subprocess.Popen([str(ROOT / 'st'), '-g', '40x10', '-e', sys.executable,
                                       str(ROOT / 'tests/x11_tab_child.py')],
                                      env=env, stdout=log, stderr=log)
                w = until(lambda: window(display, st.pid), 'st window')
                focus(display, w, 1, 0); flush(display, 0)
                def pids(): return {int(p.stem) for p in data.glob('*.ready')}
                until(lambda: len(pids()) == 1, 'PTY')
                child = next(iter(pids()))
                def output(payload, pid=None):
                    with (data / f'{pid or child}.cmd').open('w') as f:
                        f.write(json.dumps({'op': 'write', 'data': base64.b64encode(payload).decode()}) + '\n')
                    time.sleep(.1)
                def inputs(): return (data / f'{child}.input').read_bytes()
                def calls(): return [json.loads(x) for x in opened.read_text().splitlines()] if opened.exists() else []
                def frame(name): return screenshot(display, w, out / ('urls-' + name + '.png'))
                image = frame('initial')
                cw = (image.width - 4) // 40
                ch = (image.height - 4) // 10
                bar = 0
                def point(x, y):
                    rx, ry, sub = I(), I(), U()
                    translate(display, w, rootwindow(display), 2 + x * cw + cw // 2,
                              bar + 2 + y * ch + ch // 2, C.byref(rx), C.byref(ry), C.byref(sub))
                    motion(display, -1, rx.value, ry.value, 0); flush(display, 0)
                ctrl = keycode(display, keysym(b'Control_L'))
                def press(x, y, control=True):
                    point(x, y)
                    if control: keyevent(display, ctrl, 1, 0)
                    button(display, 1, 1, 0); flush(display, 0); time.sleep(.03)
                def release(control=True):
                    button(display, 1, 0, 0)
                    if control: keyevent(display, ctrl, 0, 0)
                    flush(display, 0); time.sleep(.1)
                def click(x, y, expected=None, control=True):
                    before = len(calls()); press(x, y, control); release(control)
                    if expected:
                        until(lambda: len(calls()) == before + 1, 'xdg-open')
                        assert calls()[-1] == [expected], calls()
                    else:
                        assert len(calls()) == before, 'unexpected URL opened'
                def blue_line(image, start, end, row):
                    return any(all(image.getpixel((x, y)) == (137, 180, 250)
                                   for x in range(2 + start * cw, 2 + end * cw))
                               for y in range(bar + 2 + row * ch, bar + 2 + (row + 1) * ch))
                # Compare hover with actual SGR bold, without holding Ctrl.
                uri = b'https://same.test'
                output(b'\x1bc\x1b[?25l' + uri + b'\r\n' + uri + b'\r\n\x1b[1m' + uri + b'\x1b[0m')
                point(35, 8); time.sleep(.1)
                plain = frame('hover-normal')
                def rowpixels(img, row, length=len(uri), start=0):
                    return img.crop((2+start*cw, bar+2+row*ch, 2+length*cw, bar+2+(row+1)*ch)).tobytes()
                normal, bold = rowpixels(plain, 0), rowpixels(plain, 2)
                assert normal != bold, 'reference font has no visible bold'
                point(5, 0); time.sleep(.1)
                hover = frame('hover-bold')
                assert rowpixels(hover, 0) == bold, 'hover did not use bold font'
                assert rowpixels(hover, 1) == normal, 'identical URL elsewhere also became bold'
                assert not calls(), 'hover opened a URL'
                motion(display, -1, 900, 700, 0); flush(display, 0); time.sleep(.1)
                assert rowpixels(frame('hover-left'), 0) == normal, 'leave retained bold'
                point(5, 0); time.sleep(.1)
                output(b'\x1b[H\x1b[2Kplain')
                stationary = rowpixels(frame('hover-changed'), 0)
                point(35, 8); time.sleep(.1)
                assert rowpixels(frame('hover-changed-away'), 0) == stationary
                point(5, 0); time.sleep(.1)
                output(b'\x1b[H\x1b[2K' + uri)
                assert rowpixels(frame('hover-new'), 0) == bold, 'new text under stationary pointer not hovered'
                # A wrapped link uses bold on both visible rows.
                longuri = b'https://example.test/' + b'a' * 33
                output(b'\x1bc\x1b[?25l' + longuri + b'\x1b[4;1H\x1b[1m' + longuri + b'\x1b[0m')
                point(5, 1); time.sleep(.1)
                wrapped_hover = frame('hover-wrap')
                assert rowpixels(wrapped_hover, 0, 40) == rowpixels(wrapped_hover, 3, 40)
                assert rowpixels(wrapped_hover, 1, 13) == rowpixels(wrapped_hover, 4, 13)
                output(b'\x1bc\x1b[?25lsee(HTTPS://Host.test/a(b)c), plain\r\nwww.example.org.\r\n\x1b[8mhttps://hidden.test\x1b[0m')
                image = frame('links')
                assert blue_line(image, 4, 27, 0), 'URL lacks continuous blue underline'
                assert not blue_line(image, 27, 28, 0), 'punctuation is underlined'
                assert not blue_line(image, 0, 19, 2), 'concealed URL is visible'
                click(10, 0, 'HTTPS://Host.test/a(b)c')
                click(4, 1, 'https://www.example.org')
                click(27, 0); click(2, 2); click(10, 0, control=False)
                chord(display, 'Escape')
                press(10, 0); point(11, 0); point(10, 0); release()
                assert len(calls()) == 2, 'drag opened URL'
                press(10, 0); output(b'\x1b[H\x1b[2Khttps://changed.test'); release()
                assert len(calls()) == 2, 'changed target opened URL'
                payload = 'https://host.test/a?x=1&y=$(id)'
                output(b'\x1bc\x1b[?25l' + payload.encode())
                click(10, 0, payload)  # shell metacharacters remain inside one argv
                # URL gesture takes priority over application mouse reporting.
                output(b'\x1b[?1000h\x1b[?1006h')
                before = inputs(); point(6, 0); time.sleep(.1)
                assert inputs() == before, 'hover leaked motion in button-only mode'
                click(10, 0, payload)
                assert inputs() == before, 'URL click leaked application mouse reports'
                click(35, 2)
                until(lambda: len(inputs()) > len(before), 'ordinary mouse report')
                output(b'\x1b[?1003h')
                before = inputs(); point(7, 0)
                until(lambda: len(inputs()) > len(before), 'application all-motion reporting')
                output(b'\x1b[?1003l\x1b[?1000l\x1b[?1006l\x1bc\x1b[?25l')
                wrapped = 'https://example.test/' + 'a' * 33
                output(wrapped.encode())
                image = frame('wrapped')
                assert blue_line(image, 0, 40, 0) and blue_line(image, 0, len(wrapped)-40, 1)
                click(5, 1, wrapped)
                output(b'\x1b[?25h\x1b[1;10H')
                output(b'\x1b[3;1H\x1b[?25l')
                assert blue_line(frame('cursor'), 0, 40, 0), 'old cursor erased URL styling'
                output(b'\x1b[1;40H\x1b[K')
                assert not blue_line(frame('disconnected'), 0, len(wrapped)-40, 1), 'erased wrap left stale styling'
                output(b'\x1bc\x1b[?25l' + wrapped.encode())
                # Changing a continuation must repaint the prefix as well.
                output(b'\x1b[2;1H\x1b[8mZ\x1b[0m')
                assert not blue_line(frame('invalidated'), 0, 40, 0)
                click(5, 0)
                wide = 'https://host.test/' + '界' * 11 + '/tail'
                output(b'\x1bc\x1b[?25l' + wide.encode())
                image = frame('wide-wrap')
                assert blue_line(image, 0, 40, 0) and blue_line(image, 0, 5, 1)
                click(1, 1, wide)
                output(b'\x1bc\x1b[?25l' + wrapped.encode() + b'\r\n' * 9)
                chord(display, 'Shift_L', 'Prior'); time.sleep(.1)
                point(3, 0); time.sleep(.1)
                assert rowpixels(frame('hover-history'), 0, 40) == rowpixels(wrapped_hover, 0, 40)
                click(3, 0, wrapped)
                chord(display, 'Control_L', 'Shift_L', 'space'); chord(display, 'g'); chord(display, 'g')
                time.sleep(.1)
                assert rowpixels(frame('hover-copy'), 0, 40, 1) == rowpixels(wrapped_hover, 0, 40, 1)
                click(3, 0, wrapped)
                chord(display, 'q')
                # Independent tab targets, correct vertical offset with the tab bar.
                firsttitle = prop(display, w, '_NET_WM_NAME')
                chord(display, 'Control_L', 'Shift_L', 't')
                until(lambda: len(pids()) == 2, 'second PTY')
                other = next(iter(pids() - {child})); bar = ch + 12
                output(b'\x1bc\x1b[?25lhttps://second.test', other)
                click(4, 0, 'https://second.test')
                before = len(calls()); press(4, 0)
                # Child exit closes the pressed tab while the button is held.
                with (data / f'{other}.cmd').open('w') as f:
                    f.write(json.dumps({'op': 'exit'}) + '\n')
                until(lambda: prop(display, w, '_NET_WM_NAME') == firsttitle, 'tab closed')
                bar = 0
                release()
                assert len(calls()) == before, 'tab close opened stale target'
                output(b'\x1bc\x1b[?25lhttps://first.test')
                click(4, 0, 'https://first.test')
                print('PASS X11 URLs: blue underline, punctuation, conceal, argv, mouse protocol, '
                      'drag/change cancellation, wrap invalidation, history/copy, tabs')
            finally:
                if st and st.poll() is None: st.terminate(); st.wait(timeout=5)
                if display: close_display(display)
                if server: server.terminate(); server.wait(timeout=5)


if __name__ == '__main__':
    main()

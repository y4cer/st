#!/usr/bin/env python3
"""Real Xft regression for the Pi / RenderAddGlyphs BadLength crash.

Inspired by pg83/shitty test_color_font_render.py at 509bd3f95778729d9890c68ab150d94bff372a0e.
This checks st survival/rendering, not Shitty's color pixels or ZWJ shaping.
Only escaped codepoints are used so diagnostics remain safe in an unfixed st.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from test_tabs_x11 import (
    ROOT, close_display, open_display, prop, screenshot, until, window,
)


def main():
    xvfb = os.environ.get('ST_XVFB') or shutil.which('Xvfb')
    if not xvfb:
        raise SystemExit('Xvfb required for make test-x11')
    colors = subprocess.check_output(['fc-list', ':color=true', '-f', '%{file}\n'])
    if not colors.strip():
        raise SystemExit('A color emoji font (e.g. Noto Color Emoji) is required')
    binary = Path(os.environ.get('ST_TEST_ST', ROOT / 'st')).resolve()
    out = ROOT / 'tests/bin'
    out.mkdir(exist_ok=True)
    server = display = child = None
    with tempfile.TemporaryDirectory(prefix='st-fonts-x11-') as directory:
        data = Path(directory)
        with (out / 'fonts-x11.log').open('wb') as log:
            try:
                read, write = os.pipe()
                server = subprocess.Popen(
                    [xvfb, '-displayfd', str(write), '-screen', '0',
                     '1024x768x24', '-nolisten', 'tcp'],
                    pass_fds=[write], stdout=log, stderr=log)
                os.close(write)
                with os.fdopen(read) as stream:
                    number = stream.readline().strip()
                assert number, 'Xvfb failed to start'
                name = ':' + number
                display = until(lambda: open_display(name.encode()), 'X server')
                env = dict(os.environ, DISPLAY=name)
                # The first three codepoints were in the exact crashing bash
                # result at 2026-11-13T10:12:30.911Z. Exercise all font styles,
                # mixed scripts and the reference's woman-technologist ZWJ.
                text = '\U0001f4dd \U0001f50d \U0001f6ab \U0001f469\u200d\U0001f4bb'
                rows = ''.join('\033[' + style + 'm' + text +
                               ' ASCII \u0410\u0411 \u4e2d\033[0m\r\n'
                               for style in ('0', '1', '3', '1;3'))
                payload = (rows * 3 + '\033]2;glyphs-ready\007').encode()
                # Wait for a file before writing, so even a slow startup renders
                # into an already mapped window. Keep the PTY alive afterwards.
                gate = data / 'go'
                code = ('import os,time,pathlib; '
                        f'p=pathlib.Path({str(gate)!r}); '
                        '\nwhile not p.exists(): time.sleep(.01)\n'
                        f'os.write(1, {payload!r}); time.sleep(60)')
                for label, args in (
                    ('fallback', []),
                    ('primary-color', ['-f', 'Noto Color Emoji:size=11']),
                    ('large', ['-f', 'monospace:pixelsize=32']),
                ):
                    child = subprocess.Popen(
                        [str(binary), *args, '-g', '80x24', '-e',
                         sys.executable, '-c', code],
                        env=env, stdout=log, stderr=log)
                    w = until(lambda: window(display, child.pid), label + ' window')
                    gate.touch()
                    until(lambda: prop(display, w, '_NET_WM_NAME') == b'glyphs-ready',
                          label + ' output consumed')
                    # Xft/XRender errors are asynchronous; let redraws and
                    # server round trips complete, rather than just checking
                    # that the child managed to write to its PTY.
                    for _ in range(10):
                        time.sleep(.05)
                        assert child.poll() is None, f'{label}: st exited {child.returncode}'
                    image = screenshot(display, w, out / f'fonts-{label}.png')
                    assert len(image.getcolors(image.width * image.height)) > 1
                    assert child.poll() is None, label + ': st died after rendering'
                    child.terminate()
                    child.wait(timeout=5)
                    child = None
                    gate.unlink()
                    print('PASS fonts-x11 ' + label)
            finally:
                if child is not None:
                    if child.poll() is None:
                        child.terminate()
                    child.wait(timeout=5)
                if display:
                    close_display(display)
                if server is not None:
                    server.terminate()
                    server.wait(timeout=5)
        errors = (out / 'fonts-x11.log').read_text(errors='replace')
        assert 'X Error' not in errors and 'BadLength' not in errors, ascii(errors)


if __name__ == '__main__':
    main()

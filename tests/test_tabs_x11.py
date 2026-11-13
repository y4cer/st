#!/usr/bin/env python3
"""Isolated real X11 window, real keyboard/mouse events and multiple real PTYs."""
import base64
import ctypes as C
import ctypes.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
X=C.CDLL(ctypes.util.find_library('X11'));T=C.CDLL(ctypes.util.find_library('Xtst'))
P=C.c_void_p;U=C.c_ulong;I=C.c_int

def api(lib,name,restype,*args):
    f=getattr(lib,name);f.restype=restype;f.argtypes=list(args);return f
open_display=api(X,'XOpenDisplay',P,C.c_char_p)
close_display=api(X,'XCloseDisplay',I,P)
rootwindow=api(X,'XDefaultRootWindow',U,P)
querytree=api(X,'XQueryTree',I,P,U,C.POINTER(U),C.POINTER(U),C.POINTER(C.POINTER(U)),C.POINTER(C.c_uint))
atom=api(X,'XInternAtom',U,P,C.c_char_p,I)
property_=api(X,'XGetWindowProperty',I,P,U,U,C.c_long,C.c_long,I,U,C.POINTER(U),C.POINTER(I),C.POINTER(U),C.POINTER(U),C.POINTER(P))
free=api(X,'XFree',I,P)
flush=api(X,'XSync',I,P,I)
focus=api(X,'XSetInputFocus',I,P,U,I,U)
keysym=api(X,'XStringToKeysym',U,C.c_char_p)
keycode=api(X,'XKeysymToKeycode',C.c_ubyte,P,U)
keyevent=api(T,'XTestFakeKeyEvent',I,P,C.c_uint,I,U)
button=api(T,'XTestFakeButtonEvent',I,P,C.c_uint,I,U)
motion=api(T,'XTestFakeMotionEvent',I,P,I,I,I,U)
resize=api(X,'XResizeWindow',I,P,U,C.c_uint,C.c_uint)
translate=api(X,'XTranslateCoordinates',I,P,U,U,I,I,C.POINTER(I),C.POINTER(I),C.POINTER(U))
geometry=api(X,'XGetGeometry',I,P,U,C.POINTER(U),C.POINTER(I),C.POINTER(I),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint),C.POINTER(C.c_uint))


def until(check,label,seconds=8):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        result=check()
        if result:return result
        time.sleep(.025)
    raise AssertionError('timeout: '+label)


def prop(d,w,name):
    typ=U();fmt=I();n=U();after=U();data=P()
    property_(d,w,atom(d,name.encode(),0),0,4096,0,0,C.byref(typ),C.byref(fmt),C.byref(n),C.byref(after),C.byref(data))
    if not data:return b''
    value=C.string_at(data,n.value*(C.sizeof(U) if fmt.value==32 else max(1,fmt.value//8)))
    free(data);return value


def window(d,child):
    r=U();p=U();items=C.POINTER(U)();n=C.c_uint()
    querytree(d,rootwindow(d),C.byref(r),C.byref(p),C.byref(items),C.byref(n))
    found=None
    for i in range(n.value):
        value=prop(d,items[i],'_NET_WM_PID')
        if value and int.from_bytes(value,sys.byteorder)==child:found=items[i]
    if items:free(items)
    return found


def chord(d,*names):
    codes=[keycode(d,keysym(n.encode())) for n in names]
    assert all(codes)
    for c in codes:keyevent(d,c,1,0)
    for c in reversed(codes):keyevent(d,c,0,0)
    flush(d,0)


def screenshot(d,w,path):
    from PIL import Image
    class XImage(C.Structure):
        _fields_=[('width',I),('height',I),('xoffset',I),('format',I),('data',P),('byte_order',I),('bitmap_unit',I),('bitmap_bit_order',I),('bitmap_pad',I),('depth',I),('bytes_per_line',I),('bits_per_pixel',I),('red_mask',U),('green_mask',U),('blue_mask',U)]
    r=U();x=I();y=I();width=C.c_uint();height=C.c_uint();border=C.c_uint();depth=C.c_uint()
    geometry(d,w,C.byref(r),C.byref(x),C.byref(y),C.byref(width),C.byref(height),C.byref(border),C.byref(depth))
    getimage=api(X,'XGetImage',C.POINTER(XImage),P,U,I,I,C.c_uint,C.c_uint,U,I)
    destroy=api(X,'XDestroyImage',I,C.POINTER(XImage))
    img=getimage(d,w,0,0,width.value,height.value,0xffffffff,2)
    assert img and img.contents.bits_per_pixel==32 and img.contents.byte_order==0
    raw=C.string_at(img.contents.data,img.contents.bytes_per_line*height.value)
    image=Image.frombytes('RGB',(width.value,height.value),raw,'raw','BGRX',img.contents.bytes_per_line)
    image.save(path);destroy(img)
    return image


def main():
    xvfb=os.environ.get('ST_XVFB') or shutil.which('Xvfb')
    if not xvfb:raise SystemExit('Xvfb required for make test-x11')
    display=None;server=None;st=None
    out=ROOT/'tests/bin';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='st-tabs-x11-') as directory:
        data=Path(directory)
        with (out/'tabs-x11.log').open('wb') as log:
            try:
                # Xvfb chooses a free display and reports it through this pipe.
                read,write=os.pipe()
                server=subprocess.Popen([xvfb,'-displayfd',str(write),'-screen','0','1024x768x24','-nolisten','tcp'],pass_fds=[write],stdout=log,stderr=log)
                os.close(write)
                with os.fdopen(read) as stream:number=stream.readline().strip()
                assert number,'Xvfb failed to start'
                name=':'+number
                display=until(lambda:open_display(name.encode()),'X server')
                env=dict(os.environ,DISPLAY=name,ST_X11_TEST_DIR=directory)
                st=subprocess.Popen([str(ROOT/'st'),'-g','80x24','-e',sys.executable,str(ROOT/'tests/x11_tab_child.py')],env=env,stdout=log,stderr=log)
                w=until(lambda:window(display,st.pid),'st window')
                focus(display,w,1,0);flush(display,0)
                def pids():return {int(p.stem) for p in data.glob('*.ready')}
                def title():return prop(display,w,'_NET_WM_NAME').decode()
                def input_(pid):
                    p=data/f'{pid}.input';return p.read_bytes() if p.exists() else b''
                def output(pid,payload=b'',exit=False):
                    command={'op':'exit'} if exit else {'op':'write','data':base64.b64encode(payload).decode()}
                    with (data/f'{pid}.cmd').open('w') as f:f.write(json.dumps(command)+'\n')
                until(lambda:len(pids())==1,'first PTY');a=next(iter(pids()))
                until(lambda:title()==f'session-{a}','first title')
                chord(display,'Control_L','Shift_L','t')
                until(lambda:len(pids())==2,'second PTY');b=next(iter(pids()-{a}))
                until(lambda:title()==f'[2/2] session-{b}','second title')
                # A WM can adjust pixel geometry without changing cell counts
                # after the tab bar changes its size hints. Preserve old text.
                time.sleep(.1)
                original=screenshot(display,w,out/'tabs-before-pixel-resize.png')
                cellheight=(original.height-4)//24
                barheight=cellheight+12
                resize(display,w,original.width+2,original.height);flush(display,0)
                time.sleep(.1)
                before_resize=screenshot(display,w,out/'tabs-before-pixel-resize.png')
                old_size=json.loads((data/f'{b}.size').read_text())
                resize(display,w,before_resize.width-1,before_resize.height);flush(display,0)
                time.sleep(.1)
                after_resize=screenshot(display,w,out/'tabs-after-pixel-resize.png')
                assert json.loads((data/f'{b}.size').read_text())==old_size
                region=(2,barheight+2,after_resize.width-2,after_resize.height-2)
                assert before_resize.crop(region).tobytes()==after_resize.crop(region).tobytes(), 'pixel resize erased existing terminal rows'
                chord(display,'x');until(lambda:input_(b)==b'x','input only to second')
                assert input_(a)==b''
                output(a,b'\x1b]2;background\x07\x1b[6n')
                until(lambda:b'R' in input_(a),'background reply')
                assert title()==f'[2/2] session-{b}' and input_(b)==b'x'
                chord(display,'Control_L','Shift_L','Tab')
                until(lambda:title()=='[1/2] background','previous tab')
                # Window actions remain usable in copy mode.
                chord(display,'Control_L','Shift_L','space')
                chord(display,'Control_L','Shift_L','t')
                until(lambda:len(pids())==3,'new tab from copy mode');c=next(iter(pids()-{a,b}))
                until(lambda:title()==f'[3/3] session-{c}','third title')
                output(b,b'\x1b[31mBACKGROUND OUTPUT\x1b[0m\r\n')
                output(c,b'\x1b[32mACTIVE TAB\x1b[0m\r\n')
                resize(display,w,720,420);flush(display,0)
                def sizes():
                    try:return [json.loads((data/f'{p}.size').read_text()) for p in (a,b,c)]
                    except (ValueError,FileNotFoundError):return []
                until(lambda:len(sizes())==3 and len({tuple(x) for x in sizes()})==1 and sizes()[0][0]!=80,'resize all PTYs')
                time.sleep(.1)
                screenshot(display,w,out/'tabs-three.png')
                # Dynamic Xft palettes are session-local, including replies.
                query=b'\x1b]4;1;?\x07'
                before=len(input_(c));output(c,query)
                until(lambda:len(input_(c))>before and input_(c).endswith(b'\x07'),'active palette reply')
                original=input_(c)[before:]
                before_a=len(input_(a));output(a,b'\x1b]4;1;#ff0000\x07'+query)
                until(lambda:b'rgb:ffff/0000/0000' in input_(a)[before_a:],'background palette reply')
                before=len(input_(c));output(c,query)
                until(lambda:len(input_(c))>before and input_(c).endswith(b'\x07'),'palette isolation reply')
                assert input_(c)[before:]==original
                # A real pointer click selects the first tab and never reaches a shell.
                x=I();y=I();child=U();translate(display,w,rootwindow(display),10,5,C.byref(x),C.byref(y),C.byref(child))
                motion(display,-1,x.value,y.value,0);button(display,1,1,0);button(display,1,0,0);flush(display,0)
                until(lambda:title()=='[1/3] background','click first tab')
                # Closing a background child keeps the active tab; indices update.
                output(b,exit=True)
                until(lambda:title()=='[1/2] background','background child exit')
                output(a,b'\x1b[2h')
                time.sleep(.05)  # Let KAM arrive: tab actions must still work.
                chord(display,'Alt_L','2');until(lambda:title()==f'[2/2] session-{c}','ordinal shortcut')
                time.sleep(.1)
                two_tabs=screenshot(display,w,out/'tabs-before-close-first.png')
                chord(display,'Alt_L','1')
                until(lambda:title()=='[1/2] background','select first tab to close')
                chord(display,'Control_L','Shift_L','w')
                until(lambda:title()==f'session-{c}','close first tab and hide bar')
                time.sleep(.1)
                one_tab=screenshot(display,w,out/'tabs-one.png')
                # The surviving tab's greeting and old output move up with the
                # viewport; they must not disappear when the bar is removed.
                before=(2,barheight+2,two_tabs.width-2,barheight+2+2*cellheight)
                after=(2,2,one_tab.width-2,2+2*cellheight)
                assert two_tabs.crop(before).tobytes()==one_tab.crop(after).tobytes(), 'closing first tab erased survivor output'
                # A subsequent WM size adjustment must preserve it as well.
                resize(display,w,one_tab.width+2,one_tab.height);flush(display,0)
                time.sleep(.1)
                resize(display,w,one_tab.width+1,one_tab.height);flush(display,0)
                time.sleep(.1)
                adjusted=screenshot(display,w,out/'tabs-one-after-pixel-resize.png')
                assert one_tab.crop(after).tobytes()==adjusted.crop(after).tobytes(), 'pixel resize after hiding bar erased output'
                # Once output reaches the bottom, the last line follows the
                # lower window edge and a shrink/grow cycle retains history.
                def active_size():
                    try:return json.loads((data/f'{c}.size').read_text())
                    except (ValueError,FileNotFoundError):return []
                oldrows=active_size()[1]
                before=len(input_(c))
                output(c,b'\x1b[H\x1b[2J'+b'\r\n'.join(f'line-{i}'.encode() for i in range(oldrows+5))+b'\r\nBOTTOM\x1b[6n')
                until(lambda:len(input_(c))>before and input_(c).endswith(b'R'),'bottom output processed')
                time.sleep(.1)
                bottom=screenshot(display,w,out/'resize-bottom-before.png')
                tail=(2,2+(oldrows-1)*cellheight,bottom.width-2,2+oldrows*cellheight)
                resize(display,w,bottom.width,bottom.height+3*cellheight);flush(display,0)
                until(lambda:active_size()[1:]==[oldrows+3],'grow bottom viewport')
                time.sleep(.1)
                grown=screenshot(display,w,out/'resize-bottom-grown.png')
                moved=(2,tail[1]+3*cellheight,tail[2],tail[3]+3*cellheight)
                assert bottom.crop(tail).tobytes()==grown.crop(moved).tobytes(), 'last output row did not follow lower edge'
                resize(display,w,bottom.width,bottom.height);flush(display,0)
                until(lambda:active_size()[1:]==[oldrows],'restore bottom viewport')
                time.sleep(.1)
                restored=screenshot(display,w,out/'resize-bottom-restored.png')
                body=(2,2,bottom.width-2,2+oldrows*cellheight)
                assert bottom.crop(body).tobytes()==restored.crop(body).tobytes(), 'height roundtrip changed visible output'
                before=len(input_(c))
                output(c,b'\x1b[H\x1b[2J\x1b[6n')
                until(lambda:len(input_(c))>before and input_(c).endswith(b'R'),'screen clear processed')
                chord(display,'Shift_L','Prior')
                time.sleep(.1)
                history=screenshot(display,w,out/'clear-scrollback.png')
                # PageUp moves rows-1 lines. Compare old rows 1..rows-2,
                # excluding the cursor which is hidden in scrollback.
                old_text=(2,2+cellheight,bottom.width-2,2+(oldrows-1)*cellheight)
                saved_text=(2,2,bottom.width-2,2+(oldrows-2)*cellheight)
                assert restored.crop(old_text).tobytes()==history.crop(saved_text).tobytes(), 'clear discarded visible rows instead of pushing history'
                # Vim operator composition reaches real PRIMARY/CLIPBOARD and
                # never sends its keys to the live PTY beneath the snapshot.
                create=api(X,'XCreateSimpleWindow',U,P,U,I,I,C.c_uint,C.c_uint,C.c_uint,U,U)
                convert=api(X,'XConvertSelection',I,P,U,U,U,U,U)
                deleteprop=api(X,'XDeleteProperty',I,P,U,U)
                destroy=api(X,'XDestroyWindow',I,P,U)
                requestor=create(display,rootwindow(display),0,0,1,1,0,0,0)
                target=atom(display,b'UTF8_STRING',0);clipprop=atom(display,b'ST_TEST_COPY',0)
                def clipboard(selection='CLIPBOARD'):
                    deleteprop(display,requestor,clipprop)
                    convert(display,atom(display,selection.encode(),0),target,clipprop,requestor,0)
                    flush(display,0)
                    return until(lambda:prop(display,requestor,'ST_TEST_COPY'),'copy selection')
                source=b'one two three four five six seven'
                output(c,b'\x1bc\x1b[?25l'+source+b'\r\nsecond line\r\nthird')
                time.sleep(.1);before=input_(c)
                chord(display,'Control_L','Shift_L','space')
                for k in ('g','g','0'):chord(display,k)
                for sequence,expected in [('yw',b'one '),('ye',b'one'),('yW',b'one '),('y$',source),
                                          ('2yw',b'one two '),('y2w',b'one two '),
                                          ('2y3w',b'one two three four five six '),
                                          ('yG',source+b'\nsecond line\nthird\n'+b'\n'*(active_size()[1]-3)),
                                          ('yy',source+b'\n')]:
                    for k in sequence:
                        if k=='$':chord(display,'Shift_L','4')
                        elif k.isupper():chord(display,'Shift_L',k.lower())
                        else:chord(display,k)
                    time.sleep(.05)
                    actual=clipboard()
                    assert actual==expected, (sequence,actual,expected)
                    assert clipboard('PRIMARY')==expected, sequence+' PRIMARY'
                chord(display,'y');chord(display,'Escape')
                assert clipboard()==source+b'\n', 'cancelled operator changed clipboard'
                for k in ('y','w'):chord(display,k)
                time.sleep(.05);assert clipboard()==b'one ', 'Escape left copy mode'
                assert input_(c)==before, 'copy commands leaked into PTY'
                chord(display,'q');chord(display,'x')
                until(lambda:input_(c)==before+b'x','normal input after copy mode')
                destroy(display,requestor)
                output(c,exit=True)
                assert st.wait(timeout=5)==0
                print('PASS X11: real PTYs, input/replies, palettes, resize, preserved pixels/rows, close-first, Vim yank operators and last-child exit')
            finally:
                if st and st.poll() is None:st.terminate();st.wait(timeout=5)
                if display:close_display(display)
                if server:server.terminate();server.wait(timeout=5)
if __name__=='__main__':main()

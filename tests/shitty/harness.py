"""Shitty's public test API backed by a subprocess executing the real st core.

Only representation/coordinate conversions live here; escape handling, screen
editing, history, selection and replies are all executed by st.c.
"""
import json
import ctypes
import hashlib
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
from scope import API_EXCLUSIONS
from dataclasses import dataclass
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
SHITTY = Path(os.environ.get('ST_TEST_BRIDGE', ROOT / 'tests/bin/shitty-bridge'))
TEST_PLATFORM = 'x11'


def put_rows(*values):
    return b''.join(f'\x1b[{row};1H'.encode() + value for row, value in enumerate(values, 1))


class Unsupported(unittest.SkipTest):
    """Explicit capability boundary, never an assertion-failure catch-all."""


def unsupported(feature):
    raise Unsupported(feature)


PALETTE = [(0,0,0),(170,0,0),(0,170,0),(170,85,0),(0,0,170),(170,0,170),(0,170,170),(170,170,170),
           (85,85,85),(255,85,85),(85,255,85),(255,255,85),(85,85,255),(255,85,255),(85,255,255),(255,255,255)]


def color(index):
    if index & (1 << 24):
        return ((index >> 16) & 255, (index >> 8) & 255, index & 255)
    if index == 258: return (255,255,255)
    if index == 259: return (0,0,0)
    if index < 16: return PALETTE[index]
    if index < 232:
        n = index - 16
        def channel(v): return 0 if v == 0 else 55 + 40*v
        return channel(n//36),channel(n//6%6),channel(n%6)
    return (8 + 10*(index-232),)*3


@dataclass(init=False)
class Cell:
    char: str
    double_width: bool
    double_width_continuation: bool
    bold: bool
    faint: bool
    italic: bool
    underline: bool
    blink: bool
    inverse: bool
    conceal: bool
    strike: bool
    wrapped: bool
    foreground: tuple
    background: tuple
    foreground_index: int
    background_index: int
    underline_style: int
    def __init__(self, raw=None, **fields):
        if raw is None:
            self.__dict__.update(fields)
            return
        u, m, fg, bg = raw
        self.char = chr(u) if u else ' '
        self.double_width = bool(m & 512)
        self.double_width_continuation = bool(m & 1024)
        for name, bit in [('bold',1),('faint',2),('italic',4),('underline',8),('blink',16),
                          ('inverse',32),('conceal',64),('strike',128),('wrapped',256)]:
            setattr(self,name,bool(m & bit))
        self.foreground = color(fg)
        self.background = color(bg)
        self.foreground_index = -2 if fg == 258 else (-1 if fg & (1<<24) else fg)
        self.background_index = -2 if bg == 259 else (-1 if bg & (1<<24) else bg)
        self.underline_style = int(self.underline)
    def __getattr__(self, name):
        features = {'grapheme':'grapheme clusters', 'hyperlink':'OSC 8 hyperlinks',
                    'semantic':'shell semantic metadata','protected':'protected cells / selective erase',
                    'line_attribute':'double-height/width lines','drawn':'written-cell metadata',
                    'overline':'SGR overline', 'underline_color':'colored underline', 'underline_index':'colored underline'}
        if name in features: unsupported('st does not implement ' + features[name])
        raise AttributeError(name)


@dataclass
class Snapshot:
    columns: int
    rows: int
    cursor_x: int
    cursor_y: int
    cursor_style: int
    view_offset: int
    selection: tuple
    rectangular_selection: bool
    cells: list
    lines: list
    refresh_count: int = 0  # renderer counters are excluded by the case manifest

    def cell(self, column, row):
        if not 0 <= column < self.columns or not 0 <= row < self.rows:
            raise IndexError('cell coordinate is outside the page')
        return self.cells[row*self.columns+column]


class Shitty:
    def __init__(self, columns=80, rows=24, save_lines=500, glyph_px=1, glyph_py=1,
                 font_size_env=None, extra_arguments=(), extra_environment=None,
                 binary=None, pin_vga=True, pin_border=True):
        if save_lines>2000: unsupported('fixture requires history capacity above st HISTSIZE=2000')
        self._bold_colors = False
        windowops = False
        args = list(extra_arguments)
        while args:
            option = args.pop(0)
            if option in ('-boldColors', '+boldColors'):
                self._bold_colors = option == '-boldColors'
            elif option == '-allowWindowOps' and args and args[0] in ('true','false'):
                windowops = args.pop(0) == 'true'
            else:
                unsupported('Shitty-specific launch options: ' + str(extra_arguments))
        if extra_environment or font_size_env is not None or binary is not None or not pin_vga or not pin_border:
            unsupported('Shitty-specific launch environment / renderer configuration')
        # st has a compile-time history capacity; tests asserting a different
        # capacity remain visible differences, never emulated here.
        self._stderr = tempfile.TemporaryFile()
        self.process = subprocess.Popen([str(SHITTY),str(columns),str(rows)], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,stderr=self._stderr)
        self._selector = selectors.DefaultSelector()
        self._selector.register(self.process.stdout,selectors.EVENT_READ)
        self._pending = b''
        self._selections = {}
        self._frontend = None
        self._glyph_px, self._glyph_py = glyph_px, glyph_py
        self._selection_type = 1
        self._selection_anchor = (0,0)
        self._selection_end = (0,0)
        self._buttons=0
        self._snap=0
        self._clipboard=b''
        self._primary=b''
        self._read()
        self.command(f'O {int(windowops)}')
    def _read(self):
        if not self._selector.select(10):
            self.process.kill()
            raise TimeoutError('st reference bridge did not respond within 10 seconds')
        line = self.process.stdout.readline()
        if not line:
            self._stderr.seek(0)
            raise RuntimeError('st reference bridge exited: '+self._stderr.read().decode(errors='replace'))
        value = json.loads(line)
        if isinstance(value,dict) and 'unsupported' in value:
            unsupported(value['unsupported'])
        return value
    def command(self, command):
        self.process.stdin.write(command.encode()+b'\n')
        self.process.stdin.flush()
        return self._read()
    def close(self):
        if self._frontend is not None:
            self._frontend.stdin.close()
            code = self._frontend.wait(timeout=10)
            self._frontend.stdout.close()
            self._frontend_error.seek(0)
            errors = self._frontend_error.read().decode(errors='replace')
            self._frontend_error.close()
            if code: raise RuntimeError(f'frontend bridge exit {code}: {errors}')
        if self.process.poll() is None:
            self.process.stdin.write(b'Q\n'); self.process.stdin.flush()
        try: code = self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill(); self.process.wait(); raise
        finally:
            self._selector.close(); self.process.stdin.close(); self.process.stdout.close()
        self._stderr.seek(0); errors = self._stderr.read().decode(errors='replace'); self._stderr.close()
        if code: raise RuntimeError(f'st bridge exit {code}: {errors}')
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
    def session_state(self): return tuple(self.command('Y'))
    def _session_action(self,command):
        self._selections[self._state()['session_id']]=(self._selection_anchor,self._selection_end,self._selection_type,self._snap)
        self.command(command)
        self._selection_anchor,self._selection_end,self._selection_type,self._snap=self._selections.get(self._state()['session_id'],((0,0),(0,0),1,0))
    def new_session(self): self._session_action('N')
    def close_session(self,index): self._session_action(f'L {index}')
    def chord_next_tab(self):
        count,at=self.session_state();self._session_action(f'Z {(at+1)%count}')
    def chord_prev_tab(self):
        count,at=self.session_state();self._session_action(f'Z {(at-1)%count}')
    def chord_close_tab(self): self.close_session(self.session_state()[1])
    def chord_clear(self): self.frontend_control('L')
    def write_to(self,index,data):
        if isinstance(data,str):data=data.encode()
        self.command(f'w {index} '+data.hex())
    def read_input_of(self,index): return bytes.fromhex(self.command(f'I {index}'))
    def present(self): self.command('P')
    def winsize(self):
        s=self._state();return s['columns'],s['rows']
    def write(self,data):
        if isinstance(data,str): data=data.encode()
        self.command('W '+data.hex())
    def write_chunks(self,*chunks):
        for chunk in chunks: self.write(chunk)
    feed_chunks = write_chunks
    def resize(self,columns,rows): self.command(f'R {columns} {rows}')
    def read_input(self): return bytes.fromhex(self.command('I'))
    read_all_input = read_input
    def _state(self): return self.command('S 0')
    def _cell(self, raw):
        cell=Cell(raw)
        # Profile projection of st's renderer rule; never changes core state.
        if self._bold_colors and cell.bold and not cell.faint and 0 <= cell.foreground_index < 8:
            cell.foreground_index += 8
            cell.foreground = color(cell.foreground_index)
        return cell
    def snapshot(self):
        s=self._state(); cells=[self._cell(c) for c in s['cells']]
        lines=[''.join(c.char for c in cells[i:i+s['columns']]) for i in range(0,len(cells),s['columns'])]
        # Shitty exposes half-open selection endpoints; st uses inclusive cells.
        selection=tuple(s['selection'])
        if selection[0] == -1: selection=(-1,)*4
        else: selection=(*selection[:2],selection[2]+1,selection[3])
        # Shitty cursor style enum: none=0, block=1, underline=3, bar=4.
        style=0 if s['frontend'] & 128 else (3 if s['cursor_style'] in (3,4) else 4 if s['cursor_style'] in (5,6) else 1)
        return Snapshot(columns=s['columns'],rows=s['rows'],cursor_x=s['cursor_x'],cursor_y=s['cursor_y'],
                        cursor_style=style,view_offset=s['view_offset'],selection=selection,
                        rectangular_selection=bool(s['rectangular_selection']),cells=cells,lines=lines)
    model_snapshot = snapshot
    def pen_state(self): return self._cell(self._state()['pen'])
    def cursor_pending_wrap(self): return bool(self._state()['pending'])
    def wheel_up(self,count=1): self.command(f'U {count}')
    def wheel_down(self,count=1): self.command(f'D {count}')
    def page_up(self): self.wheel_up(self._state()['rows'])
    def page_down(self): self.wheel_down(self._state()['rows'])
    def scrollback_state(self):
        s=self._state(); h=s['history']; r=s['rows']
        return h,h+r,r,h-s['view_offset']
    def all_text(self):
        return tuple(''.join(Cell(c).char for c in row).rstrip() for row in self.command('A'))
    def screen_text(self): return '\n'.join(self.snapshot().lines)
    def window_title(self): return bytes.fromhex(self.command('T')).decode()
    def tab_stop(self,column):
        tabs=self._state()['tabs']
        return bool(tabs[column]) if 0<=column<len(tabs) else False
    def tab_stops(self,columns=None): return tuple(bool(x) for x in self._state()['tabs'][:columns])
    def hard_reset(self): self.write(b'\x1bc')
    def last_update_rows(self): return tuple(i for i,v in enumerate(self._state()['dirty']) if v)
    def select_start(self,x,y,cycle=False):
        self._selection_anchor=(x,y); self._selection_type=1
        self._snap=1 if cycle else 0
        self.command(f'B {x} {y} {self._snap}')
    def select_extend(self,x,y,cycle=False):
        if cycle:
            self._snap=self._snap%2+1
            self.command(f'B {x} {y} {self._snap}')
        else: self.select_update(x,y)

    def select_update(self,x,y):
        self._selection_end=(x,y)
        # Convert the right edge of a half-open range to st's inclusive end.
        ax,ay=self._selection_anchor
        if (y,x)>=(ay,ax): x-=1
        self.command(f'E {max(0,x)} {y} {self._selection_type} 0')
    def select_rectangular(self): self._selection_type=2
    def select_finish(self): return bytes.fromhex(self.command('G'))
    def select_clear(self): self.command('C')
    def has_selection(self): return self._state()['selection'][0]!=-1
    def state(self):
        s=self._state(); m=s['frontend']
        tracking=4 if m&32768 else 3 if m&16 else 2 if m&8 else 1 if m&16384 else 0
        return tracking,2 if m&512 else 0,int(bool(m&8192)),0
    def ansi_mode(self,mode):
        s=self._state()
        if mode==4:return bool(s['mode']&2)
        if mode==20:return bool(s['mode']&8)
        unsupported('ANSI mode inspection '+str(mode))
    def private_mode(self,mode):
        s=self._state()
        if mode==6:return bool(s['origin'])
        if mode==7:return bool(s['mode']&1)
        if mode in (47,1047,1049):return bool(s['mode']&4)
        masks={1:256,5:32,25:128,1000:8,1002:16,1003:32768,1004:8192,1006:512,2004:65536}
        if mode in masks:return bool(s['frontend']&masks[mode]) != (mode==25)
        unsupported('DEC mode inspection '+str(mode))
    def _event(self,op,sym=0,mods=0,text=b'',extra='',mode_override=None,deliver=True):
        if self._frontend is None:
            self._frontend_error=tempfile.TemporaryFile()
            binary=os.environ.get('ST_TEST_FRONTEND',str(ROOT/'tests/bin/shitty-frontend'))
            self._frontend=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self._frontend_error)
        mode=self._state()['frontend'] if mode_override is None else mode_override
        # GLFW modifier bits -> X11 masks; CapsLock/NumLock are platform state.
        xmods=(mods&1)|((mods&2)<<1)|((mods&4)<<1)|((mods&8)<<3)|((mods&16)>>3)|((mods&32)>>1)
        self._frontend.stdin.write(f'{op} {mode} {xmods} {sym} {extra or text.hex()}\n'.encode())
        self._frontend.stdin.flush()
        with selectors.DefaultSelector() as ready:
            ready.register(self._frontend.stdout,selectors.EVENT_READ)
            if not ready.select(10): raise TimeoutError('X11 bridge deadline')
        line=self._frontend.stdout.readline()
        if not line: raise RuntimeError('X11 bridge exited during event')
        encoded=json.loads(line)
        if encoded is None: unsupported('st UI shortcut consumes this key before terminal input')
        if deliver:self.command('J '+encoded)
        return bytes.fromhex(encoded)
    def focus(self,focused):
        self._event('F',int(focused));self.command(f'F {int(focused)}')
    def paste(self,data):
        if isinstance(data,str):data=data.encode()
        if b'\0' in data: unsupported('binary clipboard payload requires X11 property fixture')
        self._event('P',text=data)
    def key(self,name,modifiers=0):
        sym=keysym(name)
        text={'RETURN':b'\r','ENTER':b'\r','TAB':b'\t','BACKSPACE':b'\x7f','ESCAPE':b'\x1b','SPACE':b' '}.get(name,b'')
        if name.startswith('KP_') and name[3:].isdigit():text=name[3:].encode()
        self._event('K',sym,modifiers,text)
    def frontend_key_event(self,key,action,scancode=0,modifiers=0):
        if action==0:return
        if key>=340:return  # modifier key itself has no composed X11 text
        if key>=256:
            names={256:'ESCAPE',257:'ENTER',258:'TAB',259:'BACKSPACE',260:'INSERT',261:'DELETE',262:'RIGHT',263:'LEFT',264:'DOWN',265:'UP',266:'PAGE_UP',267:'PAGE_DOWN',268:'HOME',269:'END',280:'CAPS_LOCK',281:'SCROLL_LOCK',282:'NUM_LOCK',283:'PRINT',284:'PAUSE',330:'KP_DOT',331:'KP_SLASH',332:'KP_STAR',333:'KP_MINUS',334:'KP_PLUS',335:'KP_ENTER',336:'KP_EQUAL'}
            if 290<=key<=314:name='F'+str(key-289)
            elif 320<=key<=329:name='KP_'+str(key-320)
            else:name=names.get(key)
            if name is None: unsupported('unmapped platform key '+str(key))
            return self.key(name,modifiers)
        if modifiers&6:
            char=chr(key)
            if char.isalpha() and not modifiers&1:char=char.lower()
            self.char(char,modifiers)
    def layout_key(self,key,layout,base,modifiers=0,action=1,shifted=0):
        if action==0:return
        if isinstance(key,str):key=ord(key)
        if key>=256:return self.frontend_key_event(key,action,modifiers=modifiers)
        if modifiers&2:
            char=base or layout or key
            if isinstance(char,int):char=chr(char)
            self.char(char,modifiers)
    def char(self,character,modifiers=0):
        if isinstance(character,int):character=chr(character)
        text=character.encode()
        # This is XLookupString's ASCII control translation, supplied at the
        # platform boundary; terminal key routing remains in real kpress().
        code=ord(character)
        if modifiers&2 and code<128:
            if character in ' @`' or character=='2':text=b'\0'
            elif 65<=code<=95 or 97<=code<=122:text=bytes([code&31])
            elif character in '34567':text=bytes([code-24])
            elif character in '/_':text=b'\x1f'
            elif character=='?' or character=='8':text=b'\x7f'
        self._event('K',code,modifiers,text)
    def frontend_text_event(self,character,modifiers=0):
        # GLFW separates text from key events; Ctrl combinations were already
        # delivered by the key event, like a single composed X11 KeyPress.
        if not modifiers&2:self.char(character,modifiers)
    def frontend_control(self,character,shifted=False,alt=False):
        self.char(character,2|int(shifted)|(4 if alt else 0))
    def model_digest(self):
        state=self._state(); raw=json.dumps(state['cells'],separators=(',',':')).encode()
        value=hashlib.sha256(raw).digest()
        return int.from_bytes(value[:8],'big'),int.from_bytes(value[8:16],'big')
    def selection_state(self):
        s=self.snapshot(); raw=(*self._selection_anchor,*self._selection_end)
        return {'raw':raw,'normalized':s.selection,'raw_rectangular':self._selection_type==2,'rectangular':s.rectangular_selection,'snapped':s.selection,'snapped_rectangular':s.rectangular_selection}
    def charset_state(self): return tuple(self._state()['charset'])
    def cursor_state(self):
        s=self._state()
        return int(not s['frontend']&128),int(s['cursor_style'] in (0,1,3,5)),self.snapshot().cursor_style
    def set_wrapped(self,row): self.command(f'V {row}')
    def user_input(self,data):
        if isinstance(data,str):data=data.encode()
        self.command('J '+data.hex())
    def mouse_encode(self,encoding,event,modifiers,motion_button,button,column,row):
        if encoding not in (0,2): unsupported('st mouse encoding: only legacy and SGR supported')
        mode=32768|(512 if encoding==2 else 0)
        held=1<<(motion_button-1) if motion_button else 0
        return self._event('M',mods=modifiers,mode_override=mode,deliver=False,
            extra=f'{event} {button} {column-1} {row-1} {max(column,1)} {max(row,1)} {held}')
    def _mouse(self,event,button,x,y,modifiers=0):
        s=self._state()
        self._event('M',mods=modifiers,extra=f'{event} {button} {int(x)} {int(y)} {s["columns"]} {s["rows"]} {self._buttons}')
    def button(self,button,pressed,x=2,y=2,modifiers=0,time=0,scale_x=1,scale_y=1):
        cx=int((x-2)/self._glyph_px);cy=int((y-2)/self._glyph_py)
        native={0:1,1:3,2:2}.get(button,button+1)
        if self._state()['frontend']&(8|16|16384|32768) and not modifiers&1:
            self._mouse(0 if pressed else 1,native,cx,cy,modifiers)
            if pressed:self._buttons|=1<<(native-1)
            else:self._buttons&=~(1<<(native-1))
            return b''
        unsupported('platform mouse-selection gestures: use direct st selection cases')
    def pointer(self,x,y,modifiers=0,scale_x=1,scale_y=1):
        if self._state()['frontend']&(8|16|16384|32768):
            self._mouse(2,0,int((x-2)/self._glyph_px),int((y-2)/self._glyph_py),modifiers)
        else:unsupported('platform pointer gestures: use direct st selection cases')
    def scroll(self,x,y,modifiers=0,pixel_x=2,pixel_y=2,phase='none',precise=False,momentum=False,time=0):
        import math
        if not math.isfinite(x) or not math.isfinite(y): unsupported('non-finite smooth-scroll input is not an X11 button event')
        if precise or momentum or phase!='none':unsupported('Wayland/Cocoa smooth wheel phases; st receives X11 buttons')
        if self._state()['frontend']&(8|16|16384|32768):
            for _ in range(int(abs(y))):self._mouse(0,4 if y>0 else 5,pixel_x-2,pixel_y-2,modifiers)
            for _ in range(int(abs(x))):self._mouse(0,6 if x>0 else 7,pixel_x-2,pixel_y-2,modifiers)
        elif y>0:self.wheel_up(int(y)*3)
        else:self.wheel_down(-int(y)*3)
    def __getattr__(self,name):
        # Audit runner records unimplemented APIs separately from unsupported
        # terminal features, so adapter coverage cannot masquerade as a pass.
        if name in API_EXCLUSIONS: unsupported(API_EXCLUSIONS[name])
        raise NotImplementedError('adapter API: '+name)

PRETTY = SHITTY

def run_startup_failure(*args, **kwargs):
    unsupported('Shitty CLI/startup configuration is not the st CLI')


_X11=ctypes.CDLL('libX11.so.6')
_X11.XStringToKeysym.argtypes=[ctypes.c_char_p]
_X11.XStringToKeysym.restype=ctypes.c_ulong

def keysym(name):
    names={'UP':'Up','DOWN':'Down','LEFT':'Left','RIGHT':'Right','HOME':'Home','END':'End',
           'INSERT':'Insert','DELETE':'Delete','PAGE_UP':'Prior','PAGE_DOWN':'Next',
           'ENTER':'Return','RETURN':'Return','BACKSPACE':'BackSpace','TAB':'Tab','BACKTAB':'ISO_Left_Tab',
           'ESCAPE':'Escape','SPACE':'space','KP_DOT':'KP_Decimal','KP_SLASH':'KP_Divide',
           'KP_STAR':'KP_Multiply','KP_PLUS':'KP_Add','KP_MINUS':'KP_Subtract','KP_COMMA':'KP_Separator',
           'KP_ENTER':'KP_Enter','KP_EQUAL':'KP_Equal','KP_PAGE_UP':'KP_Prior','KP_PAGE_DOWN':'KP_Next',
           'KP_INSERT':'KP_Insert','KP_END':'KP_End','KP_DOWN':'KP_Down','KP_LEFT':'KP_Left',
           'KP_BEGIN':'KP_Begin','KP_RIGHT':'KP_Right','KP_HOME':'KP_Home','KP_UP':'KP_Up',
           'KP_SPACE':'KP_Space','KP_TAB':'KP_Tab','CAPS_LOCK':'Caps_Lock','SCROLL_LOCK':'Scroll_Lock',
           'NUM_LOCK':'Num_Lock','PRINT':'Print','PAUSE':'Pause'}
    value=_X11.XStringToKeysym(names.get(name,name).encode())
    if not value: raise ValueError('unknown X11 keysym '+name)
    return value

#!/usr/bin/env python3
"""Run nested Shitty corpora against the same st adapter, without network."""
import argparse
import concurrent.futures
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tarfile
import traceback
import unittest

HERE=Path(__file__).resolve().parent
CACHE=HERE.parent/'bin/shitty-corpora'
sys.path.insert(0,str(HERE))
import harness
from harness import Shitty,Cell,Unsupported,color
from types import SimpleNamespace


def unpack():
    archive=HERE/'corpora.tar.gz'
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    marker=CACHE/'.archive-sha256'
    if marker.exists() and marker.read_text()==digest:return
    CACHE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            if not member.isfile() or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                raise ValueError('unsafe corpus archive entry '+member.name)
        tar.extractall(CACHE)
    marker.write_text(digest)


def catalog():
    entries=[]
    for path in sorted(CACHE.glob('*/*file_names.txt')):
        suite=path.parent.name
        variant=path.name.removesuffix('file_names.txt').rstrip('_')
        for case in path.read_text().splitlines():
            if not case.strip() or case.startswith('#'):continue
            entries.append({'id':f'{suite}/{variant or "main"}/{case}', 'suite':suite,'variant':variant,'case':case})
    for row in json.loads((CACHE/'termless/cases.json').read_text()):
        entries.append({'id':'termless/main/'+row[0],'suite':'termless','variant':'','case':row[0]})
    for row in json.loads((CACHE/'wraptest/cases.json').read_text()):
        entries.append({'id':'wraptest/main/'+row[0],'suite':'wraptest','variant':'','case':row[0]})
    for path in sorted((CACHE/'fuzz_corpus').glob('seed-*')):
        entries.append({'id':'fuzz_corpus/main/'+path.name,'suite':'fuzz_corpus','variant':'','case':path.name})
    return entries


def load(path,name='corpus_adapter'):
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod


def equal(actual,expected,label):
    if actual!=expected:raise AssertionError(f'{label}: got {str(actual)[:700]!r}; expected {str(expected)[:700]!r}')


def observable(t):
    s=t._state()
    return {k:s[k] for k in ('columns','rows','cursor_x','cursor_y','mode','frontend','pending','origin','top','bottom','history','pen','tabs','cells')},t.all_text(),t.read_input()


def chunk_case(payload,chunks=None):
    with Shitty(columns=80,rows=24) as t:
        t.write(payload);whole=observable(t)
    with Shitty(columns=80,rows=24) as t:
        if chunks is None:chunks=[payload[i:i+1] for i in range(len(payload))]
        t.write_chunks(*chunks);split=observable(t)
    equal(split,whole,'whole/chunked real-st state and replies')


def realworld(root,case):
    codec=load(root/'zstd_codec.py','zstd_codec')
    corpus=load(root/'corpus.py','corpus')
    spec=corpus.read_cases(root/'cases.json')[case]
    raw=codec.decompress((root/'input'/f'{case}.input.zst').read_bytes())
    expected=json.loads((root/'screen'/f'{case}.screen.json').read_text())
    # Explicit projection to st's cell fields; no grapheme/semantic/underline
    # color/drawn/renderer-private fields are claimed by this comparison.
    with Shitty(columns=spec['columns'],rows=spec['rows']) as t:
        for offset in range(0,len(raw),4096):t.write(raw[offset:offset+4096])
        snap=t.model_snapshot()
    equal([snap.columns,snap.rows],expected['geometry'],'geometry')
    equal([snap.cursor_x,snap.cursor_y],expected['cursor'][:2],'cursor')
    golden=[]
    mask=sum(1<<b for b in (0,1,2,3,4,5,6,7,8,10,11))
    for count,record in expected['cells_rle']:
        golden.extend([(record[0] or 32,record[2]&mask,tuple(record[4]),tuple(record[5]))]*count)
    actual=[]
    for c in snap.cells:
        flags=sum(int(v)<<b for b,v in enumerate((c.double_width,c.double_width_continuation,c.bold,c.italic,c.underline,c.faint,c.blink,c.conceal,c.strike,False,c.inverse,c.wrapped)))
        fg=color(c.foreground_index+8) if c.bold and not c.faint and 0<=c.foreground_index<8 else c.foreground
        actual.append((ord(c.char),flags,fg,c.background))
    equal(len(actual),len(golden),'cell count')
    for i,(a,e) in enumerate(zip(actual,golden)):
        equal(a,e,f'cell {i%snap.columns},{i//snap.columns}')


def alacritty(root,case):
    path=root/case; size=json.loads((path/'size.json').read_text())
    grid=json.loads((path/'grid.json').read_text())['raw']
    expected=[row['inner'] for row in reversed(grid['inner'][:grid['len']])]
    with Shitty(columns=size['columns'],rows=size['screen_lines']) as t:
        raw=(path/'alacritty.recording').read_bytes()
        for i in range(0,len(raw),4096):t.write(raw[i:i+4096])
        rows=[[Cell(c) for c in row] for row in t.command('A')]
    # Alacritty pads unused history capacity. Compare its populated tail and
    # require all unpopulated padding to be blank.
    if len(expected)>len(rows):
        padding=expected[:-len(rows)]
        if any(c['c'] not in (' ','\t') for row in padding for c in row):
            raise AssertionError('nonblank expected history missing from st')
        expected=expected[-len(rows):]
    equal(len(rows),len(expected),'history + screen row count')
    flags={'WIDE_CHAR':'double_width','WIDE_CHAR_SPACER':'double_width_continuation','WRAPLINE':'wrapped',
           'BOLD':'bold','ITALIC':'italic','UNDERLINE':'underline','DIM':'faint','HIDDEN':'conceal','STRIKEOUT':'strike','INVERSE':'inverse'}
    names=['Black','Red','Green','Yellow','Blue','Magenta','Cyan','White','BrightBlack','BrightRed','BrightGreen','BrightYellow','BrightBlue','BrightMagenta','BrightCyan','BrightWhite']
    for y,(ar,er) in enumerate(zip(rows,expected)):
        for x,(a,e) in enumerate(zip(ar,er)):
            equal(a.char,' ' if e['c']=='\t' else e['c'],f'char {x},{y}')
            ef=set(e['flags'].split(' | '))
            for flag,attr in flags.items():equal(getattr(a,attr),flag in ef,f'{attr} {x},{y}')
            for channel,key in [('foreground','fg'),('background','bg')]:
                value=e[key]
                if 'Indexed' in value:index=value['Indexed']
                elif 'Spec' in value:
                    equal(getattr(a,channel),tuple(value['Spec'][k] for k in ('r','g','b')),f'{channel} {x},{y}');continue
                elif value['Named'] in ('Foreground','Background'):index=-2
                else:index=names.index(value['Named'])
                equal(getattr(a,channel+'_index'),index,f'{channel} index {x},{y}')


EXCLUDE = {
    ('contour',''):'interactive vttest driver tied to Shitty child/window APIs; equivalent screen/cursor/BCE cases are in root Contour ports',
    ('tack',''):'interactive terminfo UI driver; portable terminal operations covered by root/editing and esctest cases',
    ('wraptest',''):'interactive helper requiring cursor-query PTY driver; delayed-wrap cases covered by root and libvterm tests',
    ('windows_terminal',''):'source inventory duplicated by root test_windows_terminal_* executable ports',
    ('vte',''):'VTE parser-token callback contract has no equivalent st callback API',
    ('vte','width'):'VTE internal Unicode width table API; st uses libc wcwidth',
    ('konsole','width'):'Konsole internal Unicode width table API; st uses libc wcwidth',
    ('konsole','pty'):'Konsole-specific process environment fixture',
    ('vtebench',''):'performance workloads/throughput, not correctness assertions',
}


def execute(item):
    suite,variant,case=item['suite'],item['variant'],item['case'];root=CACHE/suite
    if (suite,variant) in EXCLUDE:raise Unsupported(EXCLUDE[suite,variant])
    if suite=='fuzz_corpus':return chunk_case((root/case).read_bytes())
    if suite=='realworld':return realworld(root,case)
    if suite=='alacritty':return alacritty(root,case)
    if suite in ('kitty','wezterm') and not variant:
        mod=load(root/'catalog.py','catalog');return chunk_case(mod.case_payload(case))
    if suite=='ghostty' and variant=='semantic':
        mod=load(root/'semantic_catalog.py','semantic_catalog');_,chunks=mod.case_payload(case)
        return chunk_case(b''.join(chunks),chunks)
    if suite=='konsole' and not variant:
        mod=load(root/'catalog.py','catalog');_,mode,payload,_=mod.case_spec(case)
        if mode!='ansi':raise Unsupported('st has no VT52 mode')
        return chunk_case(payload)
    if suite=='xtermjs':
        with Shitty(columns=80,rows=25) as t:
            t.write(b'\x1bc\x1b[H'); t.write((root/f'{case}.in').read_bytes().replace(b'\n',b'\r\n'))
            actual='\n'.join(s.rstrip() for s in t.snapshot().lines)+'\n'
        expected=(root/f'{case}.text').read_text()
        equal('\n'.join(s.rstrip() for s in actual.split('\n')),'\n'.join(s.rstrip() for s in expected.split('\n')),'screen golden')
        return
    path=root/(variant+'_adapter.py' if variant else 'adapter.py')
    if not path.exists():raise NotImplementedError('missing corpus adapter '+str(path))
    mod=load(path)
    if suite=='termless':
        cases_module=sys.modules[mod.CASES[case].__module__]
        backend_module=sys.modules[cases_module.Backend.__module__]
        class StBackend(cases_module.Backend):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs)
                self.capabilities=backend_module.Capabilities(reflow=False)
            def feed(self,data):
                self.terminal.write(data.encode() if isinstance(data,str) else data)
                self.title=self.terminal.window_title()
            def mode(self,name):
                modes={'altScreen':1049,'applicationCursor':1,'autoWrap':7,'mouseTracking':1000,'focusTracking':1004}
                if name not in modes:raise ValueError('unsupported Termless mode: '+name)
                return self.terminal.private_mode(modes[name])
        cases_module.Backend=StBackend
        # The upstream CLI swallows every Exception. Call the original case
        # directly so skips, adapter gaps and crashes retain their real type.
        return mod.CASES[case]()
    if suite=='libvterm':
        class LibvtermTerminal(Shitty):
            def _cell(self,raw):
                cell=super()._cell(raw)
                for field in ('foreground','background'):
                    index=getattr(cell,field+'_index')
                    if index==-2:value=(240,240,240) if field=='foreground' else (0,0,0)
                    elif 0<=index<16:value=mod.LIBVTERM_PALETTE[index]
                    else:continue
                    setattr(cell,field,value)
                # st has single-codepoint cells, no protected/double-height flags.
                return SimpleNamespace(**vars(cell),grapheme=(),protected=False,line_attribute=0)
        mod.Shitty=LibvtermTerminal
        # st has no written-vs-erased-space bit. Compare the explicit text
        # projection on both sides, preserving interior spaces and line breaks.
        def row_text(snapshot,row,start=0,end=None):
            end=min(snapshot.columns,end if end is not None else snapshot.columns)
            return ''.join(mod.cell_text(snapshot.cell(x,row)) for x in range(start,end)).rstrip(' ')
        mod.row_text=row_text
        original_compare=mod.compare_assertion
        def compare_assertion(terminal,assertion,expected):
            if assertion.startswith(('screen_row ','screen_chars ','screen_text ')):
                value=''.join(mod.codepoints(expected))
                value='\n'.join(line.rstrip(' ') for line in value.split('\n'))
                expected=','.join(f'{ord(c):x}' for c in value)
            return original_compare(terminal,assertion,expected)
        mod.compare_assertion=compare_assertion
        # Source INIT/RESET installs this fixed palette as fixture setup.
        # Project indices to that palette; dynamic OSC commands still exclude.
        mod.configure_libvterm_colors=lambda terminal: None
        checked,skipped,mismatches=mod.run_fixture(root/'upstream'/case)
        if not checked:raise Unsupported('no st-compatible golden assertions in libvterm fixture')
        if mismatches:
            error=AssertionError('; '.join(mismatches[:5]));error.coverage={'checked':checked,'skipped':skipped}
            raise error
        return {'checked':checked,'skipped':skipped}
    if suite=='esctest':
        mod.configure_args(case)
        with Shitty(columns=80,rows=25) as terminal:
            class Backend(mod.ControlBackend):
                def rectangle_origin(self):
                    state=self.terminal._state()
                    return (state['top'] if state['origin'] else 0,0,state['bottom'],state['columns']-1)
                def snapshot(self):
                    snap=self.terminal.model_snapshot()
                    # The golden esctest assertions inspect printable screen
                    # characters. st stores one codepoint per cell.
                    snap.cells=[SimpleNamespace(**vars(c),grapheme=()) for c in snap.cells]
                    return snap
            mod.install_backend(Backend(terminal));mod.reset(terminal);mod.find_case(case)()
            if not mod.escutil.gHaveAsserted:raise AssertionError('esctest made no assertion')
        return
    # The source adapters keep their original assertions. Only CLI plumbing
    # and the Shitty fixture implementation are replaced.
    source=path.read_text();match=re.search(r'usage: [^ ]+ (.+?)"',source)
    if not match:raise NotImplementedError('cannot determine corpus adapter CLI '+str(path))
    fields=match.group(1).split();empty=CACHE/'empty-xfail.txt';empty.touch()
    stamp=CACHE/'stamps'/f'{os.getpid()}.stamp'
    values={'CASE':case,'SCRIPT':case,'FIXTURE':case,'XFAIL':str(empty),'XFAIL_FILE':str(empty),'STAMP':str(stamp)}
    if any(field not in values for field in fields):raise Unsupported('external interactive helper CLI: '+str(fields))
    sys.argv=[str(path),*[values[field] for field in fields]]
    rc=mod.main()
    if rc:raise AssertionError('upstream adapter returned '+str(rc))


def worker(item,path):
    # A fresh interpreter per case also isolates the upstream modules' globals.
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('corpus case deadline')))
    signal.alarm(30)
    stream=io.StringIO()
    try:
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):coverage=execute(item)
        result={'status':'pass'}
        if coverage is not None:result['coverage']=coverage
    except Unsupported as e:result={'status':'excluded','reason':str(e)}
    except (NotImplementedError,AttributeError,TypeError,ImportError) as e:
        result={'status':'adapter-gap','reason':str(e),'trace':traceback.format_exc()}
    except Exception as e:
        result={'status':'failure','reason':str(e),'error_type':type(e).__name__,'trace':traceback.format_exc(),'output':stream.getvalue()[-5000:]}
        if hasattr(e,'coverage'):result['coverage']=e.coverage
    finally:signal.alarm(0)
    Path(path).write_text(json.dumps(result,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',nargs=2);p.add_argument('--audit',action='store_true');p.add_argument('--suite');p.add_argument('--output',default=str(HERE.parent/'bin/shitty-corpora-report.json'));args=p.parse_args()
    if args.worker:worker(json.loads(args.worker[0]),args.worker[1]);return
    unpack();items=catalog()
    if args.suite:items=[i for i in items if i['suite']==args.suite]
    output=Path(args.output);results={};work=output.parent/(output.stem+'-cases');work.mkdir(exist_ok=True)
    def run(item):
        path=work/(hashlib.sha256(item['id'].encode()).hexdigest()+'.json')
        try:
            p=subprocess.run([sys.executable,__file__,'--worker',json.dumps(item),str(path)],capture_output=True,text=True,timeout=45,env=dict(os.environ,PYTHONHASHSEED='0'))
            if p.returncode:return item['id'],{'status':'failure','reason':p.stderr[-2000:]}
            return item['id'],json.loads(path.read_text())
        except subprocess.TimeoutExpired:return item['id'],{'status':'failure','reason':'corpus subprocess deadline'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for id,result in pool.map(run,items):results[id]=result;print(id,result['status'],flush=True)
    output.write_text(json.dumps(results,indent=2)+'\n')
    from collections import Counter
    print(dict(Counter(v['status'] for v in results.values())))
    if not args.audit and any(v['status'] in ('failure','adapter-gap') for v in results.values()):sys.exit(1)
if __name__=='__main__':main()

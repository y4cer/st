#!/usr/bin/env python3
"""Inventory and execute vendored reference tests, retaining every disposition."""
import argparse
import concurrent.futures
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest
from scope import case_reasons

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'upstream'))
sys.path.insert(0,str(HERE))

# These modules exercise another implementation's build system, UI/backend,
# or internal APIs, not shared terminal behavior. Mixed modules are run.
EXCLUDED = {
    'test_config':'Shitty TOML configuration and options',
    'test_toml':'Shitty TOML parser',
    'test_build_metadata':'Shitty build metadata',
    'test_release_bundle_archive':'Shitty distribution archive',
    'test_ci_report':'Shitty CI report generator',
    'test_run_timed':'Shitty test runner',
    'test_unittest_group':'Shitty test runner',
    'test_unicode_data_generator':'Shitty Unicode table generator',
    'test_terminal_colors_data':'Shitty palette source generator',
    'test_embed_example':'Shitty C++ embedding API',
    'test_startup':'Shitty application startup and platform backends',
    'test_perf_mode':'Shitty performance CLI',
    'test_options':'Shitty command-line options',
    'test_desktop_identity':'Shitty desktop integration',
    'test_debug_trace':'Shitty trace instrumentation',
    'test_dump':'Shitty dump CLI',
    'test_sixel':'Sixel graphics (absent in st)',
    'test_contour_kitty_clipboard':'Kitty OSC 5522 clipboard protocol (absent in st)',
    'test_unicode_grapheme_matrix':'Unicode grapheme storage/conformance API (absent in st)',
    'test_unicode':'Shitty Unicode 17 grapheme/emoji data; st uses libc wcwidth',
    'test_utf8_run_seams':'Shitty Unicode 17 emoji/grapheme tables; st uses libc wcwidth',
    'test_kitty_text_sizing':'Kitty multicell text sizing (absent in st)',
}
for name in ('font_resize','font_fallback','font_optical','font_ligature','font_resolver','font_miss_storm',
             'system_emoji_fallback','color_font_render','bitmap_font_render','wide_ligature_overflow',
             'italic_overhang','nerd_icon_render','output_scale','preedit','soft_render','vulkan_smoke',
             'vulkan_parity','renderer_replacement','render_contract','damage_only_frames','block_elements',
             'synthesized_symbols','reference_decorations','terminal_layout'):
    EXCLUDED['test_'+name]='Shitty font shaping / software, Vulkan or Wayland/Cocoa renderer; st uses Xft/X11'

class Result(unittest.TestResult):
    def __init__(self): super().__init__(); self.records={}; self.current=None
    def startTest(self,test):
        super().startTest(test); self.current=test.id(); self.records[self.current]={'status':'pass'}
        signal.alarm(15)
    def stopTest(self,test): signal.alarm(0); super().stopTest(test)
    def addSuccess(self,test): super().addSuccess(test)
    def addSkip(self,test,reason):
        super().addSkip(test,reason)
        if self.records[self.current]['status'] in ('pass','excluded'):
            self.records[self.current]={'status':'excluded','reason':reason}
    def problem(self,test,err):
        kind='adapter-gap' if issubclass(err[0],(NotImplementedError,AttributeError,TypeError)) else 'failure'
        record=self.records[self.current]
        problems=record.get('problems',[])
        problems.append({'type':err[0].__name__,'reason':str(err[1])})
        self.records[self.current]={'status':kind,'reason':str(err[1]),'problems':problems,'trace':self._exc_info_to_string(err,test)}
    def addError(self,test,err): super().addError(test,err); self.problem(test,err)
    def addFailure(self,test,err): super().addFailure(test,err); self.problem(test,err)
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err is not None:self.problem(test,err)

def flatten(suite):
    for t in suite:
        if isinstance(t,unittest.TestSuite):yield from flatten(t)
        else:yield t

def worker(module,path):
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('test deadline: 15s')))
    try:
        mod=importlib.import_module(module)
        cases=list(flatten(unittest.defaultTestLoader.loadTestsFromModule(mod)))
        scope=case_reasons(HERE/'upstream'/(module+'.py'))
        for case in cases:
            fn=getattr(type(case),case._testMethodName)
            if getattr(fn,'__unittest_expecting_failure__',False): fn.__unittest_expecting_failure__=False
        result=Result()
        active=[]
        for case in cases:
            if case.id() in scope:
                result.records[case.id()]={'status':'excluded','reason':'; '.join(scope[case.id()])}
            else:active.append(case)
        unittest.TestSuite(active).run(result)
        data=result.records
    except Exception as e:
        data={'__import__':{'status':'adapter-gap','reason':str(e)}}
    Path(path).write_text(json.dumps(data,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--worker',nargs=2); p.add_argument('--audit',action='store_true'); p.add_argument('--output',default=str(HERE.parent/'bin/shitty-report.json')); p.add_argument('--module'); args=p.parse_args()
    if args.worker: worker(*args.worker); return
    inventory=json.loads((HERE/'inventory.json').read_text())['tests']
    modules=sorted({r['id'].split('.')[0] for r in inventory})
    if args.module:modules=[m for m in modules if args.module in m]
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    work=output.parent/(output.stem+'-cases');work.mkdir(exist_ok=True)
    def run(module):
        if module in EXCLUDED:return module,{'__all__':{'status':'excluded','reason':EXCLUDED[module]}}
        path=work/(module+'.json')
        try:
            r=subprocess.run([sys.executable,__file__,'--worker',module,str(path)],capture_output=True,text=True,timeout=180,env=dict(os.environ,PYTHONHASHSEED='0'))
            if r.returncode:return module,{'__all__':{'status':'failure','reason':r.stderr[-2000:]}}
            return module,json.loads(path.read_text())
        except subprocess.TimeoutExpired:return module,{'__all__':{'status':'failure','reason':'module deadline: 180s'}}
    results={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for module,data in pool.map(run,modules):
            for item in inventory:
                if item['id'].split('.')[0]==module:
                    results[item['id']]=data.get(item['id'],data.get('__all__',data.get('__import__',{'status':'adapter-gap','reason':'not collected'})))
            print(module,flush=True)
    output.write_text(json.dumps(results,indent=2)+'\n')
    from collections import Counter
    print(dict(Counter(r['status'] for r in results.values())))
    if not args.audit and any(r['status'] in ('failure','adapter-gap') for r in results.values()):sys.exit(1)
if __name__=='__main__':main()

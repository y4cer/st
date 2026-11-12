"""Each session regression owns its processes and dies on sanitizer errors."""
import os
import subprocess
import sys

env=dict(os.environ)
env['ASAN_OPTIONS']=env.get('ASAN_OPTIONS','')+':detect_leaks=1:halt_on_error=1'
env['UBSAN_OPTIONS']=env.get('UBSAN_OPTIONS','')+':halt_on_error=1:print_stacktrace=1'
for case in ('isolation','copy_history','resize_lifetime','backpressure_close','child_exit','focus_routing','refused_spawn'):
    subprocess.run([sys.argv[1],case],check=True,timeout=15,env=env)
    print('session:',case,flush=True)

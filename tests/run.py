#!/usr/bin/env python3
"""Run each test in a fresh process, with deadlines and visible failures."""
import os
from pathlib import Path
import resource
import subprocess
import sys

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
env = dict(os.environ)
env.setdefault("ASAN_OPTIONS", "detect_leaks=1:halt_on_error=1")
env.setdefault("UBSAN_OPTIONS", "halt_on_error=1:print_stacktrace=1")
failed = []
count = 0
for binary in sys.argv[1:]:
    binary = str(Path(binary).resolve())
    names = subprocess.check_output([binary], text=True, env=env, timeout=10).splitlines()
    for name in names:
        count += 1
        try:
            result = subprocess.run([binary, name], text=True, capture_output=True,
                                    timeout=20, env=env)
            if result.returncode:
                failed.append(name)
                print(f"FAIL {name} (exit {result.returncode})\n{result.stdout}{result.stderr}")
            else:
                print(result.stdout.strip())
        except subprocess.TimeoutExpired:
            failed.append(name)
            print(f"FAIL {name}: timed out")
print(f"\n{count - len(failed)}/{count} passed")
if failed:
    print("Failed: " + ", ".join(failed))
    sys.exit(1)

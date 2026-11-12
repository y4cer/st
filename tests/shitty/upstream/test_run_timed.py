# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import subprocess
import sys
import unittest
from pathlib import Path


RUN_TIMED = Path(__file__).with_name("run_timed.py")


class RunTimedTest(unittest.TestCase):
    def run_timed(self, limit, source):
        return subprocess.run(
            [
                sys.executable,
                str(RUN_TIMED),
                str(limit),
                sys.executable,
                "-c",
                source,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def test_propagates_command_failure(self):
        result = self.run_timed(10, "raise SystemExit(7)")

        self.assertEqual(result.returncode, 7)
        self.assertIn("(exit 7)", result.stderr)

    def test_kills_timed_out_command(self):
        result = self.run_timed(0.1, "import time; time.sleep(10)")

        self.assertEqual(result.returncode, 124)
        self.assertIn("timed out after", result.stderr)


if __name__ == "__main__":
    unittest.main()

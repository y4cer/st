# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import os
import subprocess
import tempfile
import unittest

from harness import SHITTY


def run_perf(*arguments):
    environment = os.environ.copy()
    environment["XDG_CONFIG_HOME"] = "/nonexistent"
    return subprocess.run(
        [str(SHITTY), "perf", *map(str, arguments)],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


class PerfModeTest(unittest.TestCase):
    def test_perf_replays_a_directory_and_reports_throughput(self):
        with tempfile.TemporaryDirectory() as corpus:
            with open(os.path.join(corpus, "sample.vt"), "wb") as sample:
                sample.write(b"\x1b[2J\x1b[Hplain text\r\n" * 64)
                sample.write(b"\x1b[31mred\x1b[0m\x1b[1;1H\x1b[K")
            os.mkdir(os.path.join(corpus, "nested"))
            completed = run_perf(corpus)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(b"MiB/s", completed.stderr)

    def test_perf_without_directories_reports_usage(self):
        completed = run_perf()

        self.assertEqual(completed.returncode, 1)
        self.assertIn(b"Error: usage:", completed.stderr)
        self.assertIn(b"perf DIRECTORY", completed.stderr)

    def test_perf_with_a_missing_directory_fails_loudly(self):
        completed = run_perf("/nonexistent-perf-corpus")

        self.assertEqual(completed.returncode, 1)
        self.assertIn(b"Error:", completed.stderr)


if __name__ == "__main__":
    unittest.main()

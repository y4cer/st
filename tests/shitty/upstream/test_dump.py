# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import errno
import tempfile
import unittest
from pathlib import Path

from harness import Shitty


class DumpTest(unittest.TestCase):
    def test_dump_records_raw_pty_reads_exactly_and_truncates_file(self):
        chunks = (
            b"plain\0text",
            b"\x1b[?2026hanimated\x1b[?2026l",
            b"\xff\xfe\x80",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pty.dump"
            path.write_bytes(b"stale contents")

            with Shitty(extra_arguments=("-dump", path)) as terminal:
                terminal.script_pty_reads(
                    *chunks,
                    ("error", errno.EAGAIN),
                )
                for _ in chunks:
                    self.assertFalse(terminal.read_pty())

            self.assertEqual(path.read_bytes(), b"".join(chunks))


if __name__ == "__main__":
    unittest.main()

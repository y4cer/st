# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""UTF-8 run placement across feed seams: sequences split between
reads, malformed bytes inside a run, and wide pairs against the last
column."""

import unittest

from harness import Shitty


class Utf8RunSeamTest(unittest.TestCase):
    def test_multibyte_sequences_resume_across_feeds(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(b"\xe4\xbd", b"\xa0")
            terminal.write_chunks(b"\xf0\x9f", b"\x98", b"\x80")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "你")
            self.assertEqual(snapshot.cell(2, 0).char, "\U0001f600")

    def test_malformed_bytes_do_not_derail_the_run(self):
        with Shitty(columns=12, rows=2) as terminal:
            # A lone continuation, an overlong slash, a truncated lead
            # cut off by an escape sequence - the printable tail must
            # still land.
            terminal.write(b"A\x80B\xc0\xafC\xe4\xbd\x1b[1mD")
            text = terminal.snapshot().lines[0]
            self.assertIn("A", text)
            self.assertIn("B", text)
            self.assertIn("C", text)
            self.assertIn("D", text)
            self.assertLess(text.index("C"), text.index("D"))

    def test_wide_pair_wraps_off_the_last_column(self):
        with Shitty(columns=4, rows=3) as terminal:
            # Three columns filled, the wide pair cannot split: it wraps
            # whole onto the next row and the orphan column stays plain.
            terminal.write("ABC你D".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0].rstrip(), "ABC")
            self.assertEqual(snapshot.cell(0, 1).char, "你")
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertEqual(snapshot.cell(2, 1).char, "D")

    def test_combining_marks_join_the_seamed_base(self):
        with Shitty(columns=8, rows=2) as terminal:
            # The combining acute arrives in its own feed after the base.
            terminal.write_chunks(b"e", b"\xcc\x81", b"x")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(1, 0).char, "x")


if __name__ == "__main__":
    unittest.main()

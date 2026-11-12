# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import errno
import unittest

from harness import Shitty


class PtyStreamingTest(unittest.TestCase):
    def test_incomplete_sequences_do_not_publish_spurious_frames(self):
        fragments = (
            b"\x1b[31",
            b"\x1b]2;unfinished",
            "界".encode()[:2],
        )
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(b"\x1b[0m")
                    before = terminal.snapshot().refresh_count
                    terminal.script_pty_reads(
                        fragment, ("error", errno.EAGAIN)
                    )
                    self.assertFalse(terminal.read_pty())
                    self.assertEqual(
                        terminal.snapshot().refresh_count,
                        before,
                    )

    def test_synchronized_update_spans_multiple_pty_readiness_cycles(self):
        with Shitty(columns=8, rows=2) as terminal:
            before = terminal.snapshot()
            terminal.script_pty_reads(
                b"\x1b[?2026hfirst", ("error", errno.EAGAIN)
            )
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.snapshot(), before)

            terminal.script_pty_reads(b"+second", ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.snapshot(), before)

            terminal.script_pty_reads(
                b"\x1b[?2026l", ("error", errno.EAGAIN)
            )
            self.assertFalse(terminal.read_pty())
            after = terminal.snapshot()
            self.assertEqual(after.lines, ["first+se", "cond    "])
            self.assertEqual(after.refresh_count, before.refresh_count + 1)

    def test_csi_split_across_readiness_cycles_keeps_parser_state(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_reads(b"\x1b[3", ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.snapshot().lines[0], "        ")

            terminal.script_pty_reads(b"1mR", ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.char, "R")
            self.assertEqual(cell.foreground, (170, 0, 0))

    def test_utf8_split_across_readiness_cycles_is_not_replaced(self):
        encoded = "界".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_reads(encoded[:2], ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.snapshot().lines[0], "        ")

            terminal.script_pty_reads(encoded[2:], ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "界")

    def test_osc_split_across_readiness_cycles_dispatches_only_when_complete(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_reads(
                b"\x1b]2;split title", ("error", errno.EAGAIN)
            )
            self.assertFalse(terminal.read_pty())
            self.assertEqual(terminal.read_actions(), [])

            terminal.script_pty_reads(b"\x1b\\", ("error", errno.EAGAIN))
            self.assertFalse(terminal.read_pty())
            self.assertEqual(
                terminal.read_actions(),
                ["OSC 2 73706c6974207469746c65"],
            )


if __name__ == "__main__":
    unittest.main()

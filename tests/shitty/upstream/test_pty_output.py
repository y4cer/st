# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import errno
import unittest

from harness import Shitty


class PtyOutputTest(unittest.TestCase):
    max_write = 64 * 1024

    def test_one_flush_writes_at_most_64_kib(self):
        payload = b"x" * (self.max_write + 7)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(len(payload))
            terminal.input(payload)

            self.assertEqual(len(terminal.read_written_pty()), self.max_write)

            terminal.script_pty_writes(7)
            self.assertTrue(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"x" * 7)

    def test_simultaneous_read_and_write_flushes_older_bytes_before_reply(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(("error", errno.EAGAIN))
            terminal.input(b"older")
            terminal.script_pty_writes(64)
            terminal.script_pty_reads(b"\x1b[5n", ("error", errno.EAGAIN))

            self.assertFalse(terminal.service_pty(readable=True, writable=True))
            self.assertEqual(terminal.read_written_pty(), b"older")
            terminal.script_pty_writes(64)
            self.assertTrue(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"\x1b[0n")

    def test_partial_writes_resume_at_exact_unsent_byte_after_backpressure(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(2)
            terminal.input(b"abcdefghi")
            self.assertEqual(terminal.read_written_pty(), b"ab")

            terminal.script_pty_writes(3)
            self.assertFalse(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"cde")

            terminal.script_pty_writes(("error", errno.EAGAIN))
            self.assertFalse(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"")

            terminal.script_pty_writes(4)
            self.assertTrue(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"fghi")

    def test_interrupted_write_is_left_for_next_callback_without_duplication(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(("error", errno.EINTR))
            terminal.input(b"retry")
            self.assertEqual(terminal.read_written_pty(), b"")

            terminal.script_pty_writes(5)
            self.assertTrue(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"retry")

    def test_fatal_write_drops_payload_instead_of_retrying_forever(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(("error", errno.EPIPE))
            terminal.input(b"discarded")
            self.assertEqual(terminal.read_written_pty(), b"")

            terminal.script_pty_writes(9)
            self.assertTrue(terminal.flush_output_result())
            self.assertEqual(terminal.read_written_pty(), b"")

    def test_pending_output_does_not_stop_pty_reading(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.script_pty_writes(("error", errno.EAGAIN))
            terminal.input(b"x" * 64)
            terminal.script_pty_reads(b"visible", ("error", errno.EAGAIN))

            self.assertFalse(
                terminal.service_pty(readable=True, writable=True)
            )
            self.assertTrue(terminal.screen_text().startswith("visible"))


if __name__ == "__main__":
    unittest.main()

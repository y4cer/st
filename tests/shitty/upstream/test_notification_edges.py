# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""OSC 99 assembly off the happy path: broken base64, continuations of
identities never opened, mixed encodings and closes for nobody."""

import unittest

from harness import Shitty


class NotificationEdgeTest(unittest.TestCase):
    def test_broken_base64_drops_the_notification(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]99;i=bad:p=title:e=1:d=1;@@@@\x1b\\")
            self.assertEqual(terminal.read_actions(), [])

    def test_continuation_without_an_opening_chunk_stands_alone(self):
        with Shitty(columns=8, rows=2) as terminal:
            # d=1 with an identity nobody opened: the chunk is the whole
            # notification.
            terminal.write(b"\x1b]99;i=ghost:p=title:d=1;boo\x1b\\")
            self.assertEqual(
                terminal.read_actions(),
                ["NOTIFY 67686f7374 626f6f "],
            )

    def test_encoded_and_plain_chunks_mix_within_one_identity(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]99;i=mix:p=title:e=1:d=0;aGV4\x1b\\"
                b"\x1b]99;i=mix:p=title:d=1; tail\x1b\\"
            )
            self.assertEqual(
                terminal.read_actions(),
                ["NOTIFY 6d6978 686578207461696c "],
            )

    def test_close_of_an_unknown_identity_is_silent(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]99;i=nobody:p=close;\x1b\\")
            self.assertEqual(terminal.read_actions(), ["NOTIFY_CLOSE 6e6f626f6479"])


if __name__ == "__main__":
    unittest.main()

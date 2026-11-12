# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


RELEASE = 0
PRESS = 1
REPEAT = 2
KEY_A = 65
KEY_UP = 265


class KeyboardRepeatTest(unittest.TestCase):
    def test_decarm_controls_printable_and_special_key_repeats(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?8l")

            terminal.frontend_key_event(KEY_A, PRESS)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(KEY_A, REPEAT)
            terminal.frontend_text_event("a")
            terminal.frontend_text_event("b")
            terminal.frontend_key_event(KEY_UP, REPEAT)
            self.assertEqual(terminal.read_input(), b"a")

            terminal.write(b"\x1b[?8h")
            terminal.frontend_key_event(KEY_A, REPEAT)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(KEY_UP, REPEAT)
            self.assertEqual(terminal.read_input(), b"a\x1b[A")

    def test_nonrepeat_event_ends_text_suppression(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?8l")
            terminal.frontend_key_event(KEY_A, REPEAT)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(KEY_A, RELEASE)
            terminal.frontend_key_event(KEY_A, PRESS)
            terminal.frontend_text_event("a")
            self.assertEqual(terminal.read_input(), b"a")

    def test_decarm_precedes_kitty_repeat_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>2u\x1b[?8l")
            terminal.frontend_key_event(KEY_UP, REPEAT)
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x1b[?8h")
            terminal.frontend_key_event(KEY_UP, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[1;1:2A")

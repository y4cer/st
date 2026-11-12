# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""The pad keys that arrive under their navigation identities: without
NumLock a frontend reports KP7 as keypad-Home, and in numeric keypad
mode the terminal still types the digit the key wears."""

import unittest

from harness import Shitty


PRESS = 1
NUM_LOCK = 32

KEY_KP_0 = 320
KEY_KP_ENTER = 335
KEY_KP_EQUAL = 336
KEY_KP_SEPARATOR = 337
KEY_KP_INSERT = 350
KEY_KP_DELETE = 351
KEY_KP_UP = 352
KEY_KP_DOWN = 353
KEY_KP_LEFT = 354
KEY_KP_RIGHT = 355
KEY_KP_HOME = 356
KEY_KP_END = 357
KEY_KP_PAGE_UP = 358
KEY_KP_PAGE_DOWN = 359
KEY_KP_BEGIN = 360
KEY_KP_SPACE = 361
KEY_KP_TAB = 362

NUMERIC_KEYPAD = (
    (KEY_KP_INSERT, b"0"),
    (KEY_KP_END, b"1"),
    (KEY_KP_DOWN, b"2"),
    (KEY_KP_PAGE_DOWN, b"3"),
    (KEY_KP_LEFT, b"4"),
    (KEY_KP_BEGIN, b"5"),
    (KEY_KP_RIGHT, b"6"),
    (KEY_KP_HOME, b"7"),
    (KEY_KP_UP, b"8"),
    (KEY_KP_PAGE_UP, b"9"),
    (KEY_KP_DELETE, b"."),
    (KEY_KP_SEPARATOR, b","),
    (KEY_KP_SPACE, b" "),
    (KEY_KP_TAB, b"\t"),
    (KEY_KP_ENTER, b"\r"),
    (KEY_KP_EQUAL, b"="),
)


class KeypadVariantTest(unittest.TestCase):
    def test_navigation_identities_type_digits_in_numeric_mode(self):
        for key, expected in NUMERIC_KEYPAD:
            with self.subTest(key=key):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.frontend_key_event(key, PRESS)
                    self.assertEqual(terminal.read_input(), expected)

    def test_num_lock_keeps_digits_in_application_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b=")
            terminal.frontend_key_event(KEY_KP_0, PRESS, modifiers=NUM_LOCK)
            self.assertEqual(terminal.read_input(), b"0")


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Keypad tail and cursor head from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
ALT = 4

KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264
KEY_UP = 265
KEY_KP_0 = 320


PORTED_CASES = (
    ("regress/tty-keys.sh:SS3-v:KP6", "test_keypad_6"),
    ("regress/tty-keys.sh:ESC-SS3-v:M-KP6", "test_alt_keypad_6"),
    ("regress/tty-keys.sh:SS3-w:KP7", "test_keypad_7"),
    ("regress/tty-keys.sh:ESC-SS3-w:M-KP7", "test_alt_keypad_7"),
    ("regress/tty-keys.sh:SS3-x:KP8", "test_keypad_8"),
    ("regress/tty-keys.sh:ESC-SS3-x:M-KP8", "test_alt_keypad_8"),
    ("regress/tty-keys.sh:SS3-y:KP9", "test_keypad_9"),
    ("regress/tty-keys.sh:ESC-SS3-y:M-KP9", "test_alt_keypad_9"),
    ("regress/tty-keys.sh:SS3-A:Up", "test_application_up"),
    ("regress/tty-keys.sh:ESC-SS3-A:M-Up", "test_alt_application_up"),
    ("regress/tty-keys.sh:SS3-B:Down", "test_application_down"),
    ("regress/tty-keys.sh:ESC-SS3-B:M-Down", "test_alt_application_down"),
    ("regress/tty-keys.sh:SS3-C:Right", "test_application_right"),
    ("regress/tty-keys.sh:ESC-SS3-C:M-Right", "test_alt_application_right"),
    ("regress/tty-keys.sh:SS3-D:Left", "test_application_left"),
    ("regress/tty-keys.sh:ESC-SS3-D:M-Left", "test_alt_application_left"),
    ("regress/tty-keys.sh:CSI-A:Up", "test_normal_up"),
    ("regress/tty-keys.sh:ESC-CSI-A:M-Up", "test_alt_normal_up"),
    ("regress/tty-keys.sh:CSI-B:Down", "test_normal_down"),
    ("regress/tty-keys.sh:ESC-CSI-B:M-Down", "test_alt_normal_down"),
)


class TmuxRegressTtyKeysKeypadCursorTest(unittest.TestCase):
    def _assert_keypad(self, key, suffix, meta):
        modifiers = ALT if meta else 0
        modifier = b"3" if meta else b""
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b=")
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(
                terminal.read_input(), b"\x1bO" + modifier + suffix
            )

    def _assert_cursor(self, key, suffix, meta, application):
        modifiers = ALT if meta else 0
        with Shitty(columns=8, rows=2) as terminal:
            if application:
                terminal.write(b"\x1b[?1h")
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            if meta:
                expected = b"\x1b[1;3" + suffix
            elif application:
                expected = b"\x1bO" + suffix
            else:
                expected = b"\x1b[" + suffix
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_keypad_6(self):
        self._assert_keypad(KEY_KP_0 + 6, b"v", False)

    def test_alt_keypad_6(self):
        self._assert_keypad(KEY_KP_0 + 6, b"v", True)

    def test_keypad_7(self):
        self._assert_keypad(KEY_KP_0 + 7, b"w", False)

    def test_alt_keypad_7(self):
        self._assert_keypad(KEY_KP_0 + 7, b"w", True)

    def test_keypad_8(self):
        self._assert_keypad(KEY_KP_0 + 8, b"x", False)

    def test_alt_keypad_8(self):
        self._assert_keypad(KEY_KP_0 + 8, b"x", True)

    def test_keypad_9(self):
        self._assert_keypad(KEY_KP_0 + 9, b"y", False)

    def test_alt_keypad_9(self):
        self._assert_keypad(KEY_KP_0 + 9, b"y", True)

    def test_application_up(self):
        self._assert_cursor(KEY_UP, b"A", False, True)

    def test_alt_application_up(self):
        self._assert_cursor(KEY_UP, b"A", True, True)

    def test_application_down(self):
        self._assert_cursor(KEY_DOWN, b"B", False, True)

    def test_alt_application_down(self):
        self._assert_cursor(KEY_DOWN, b"B", True, True)

    def test_application_right(self):
        self._assert_cursor(KEY_RIGHT, b"C", False, True)

    def test_alt_application_right(self):
        self._assert_cursor(KEY_RIGHT, b"C", True, True)

    def test_application_left(self):
        self._assert_cursor(KEY_LEFT, b"D", False, True)

    def test_alt_application_left(self):
        self._assert_cursor(KEY_LEFT, b"D", True, True)

    def test_normal_up(self):
        self._assert_cursor(KEY_UP, b"A", False, False)

    def test_alt_normal_up(self):
        self._assert_cursor(KEY_UP, b"A", True, False)

    def test_normal_down(self):
        self._assert_cursor(KEY_DOWN, b"B", False, False)

    def test_alt_normal_down(self):
        self._assert_cursor(KEY_DOWN, b"B", True, False)


if __name__ == "__main__":
    unittest.main()

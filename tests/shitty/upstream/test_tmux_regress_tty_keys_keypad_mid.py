# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Application keypad continuation from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
ALT = 4

KEY_KP_0 = 320
KEY_KP_DECIMAL = 330
KEY_KP_DIVIDE = 331
KEY_KP_SUBTRACT = 333
KEY_KP_ADD = 334


PORTED_CASES = (
    ("regress/tty-keys.sh:SS3-k:KP+", "test_keypad_add"),
    ("regress/tty-keys.sh:ESC-SS3-k:M-KP+", "test_alt_keypad_add"),
    ("regress/tty-keys.sh:SS3-m:KP-", "test_keypad_subtract"),
    ("regress/tty-keys.sh:ESC-SS3-m:M-KP-", "test_alt_keypad_subtract"),
    ("regress/tty-keys.sh:SS3-n:KP.", "test_keypad_decimal"),
    ("regress/tty-keys.sh:ESC-SS3-n:M-KP.", "test_alt_keypad_decimal"),
    ("regress/tty-keys.sh:SS3-o:KP/", "test_keypad_divide"),
    ("regress/tty-keys.sh:ESC-SS3-o:M-KP/", "test_alt_keypad_divide"),
    ("regress/tty-keys.sh:SS3-p:KP0", "test_keypad_0"),
    ("regress/tty-keys.sh:ESC-SS3-p:M-KP0", "test_alt_keypad_0"),
    ("regress/tty-keys.sh:SS3-q:KP1", "test_keypad_1"),
    ("regress/tty-keys.sh:ESC-SS3-q:M-KP1", "test_alt_keypad_1"),
    ("regress/tty-keys.sh:SS3-r:KP2", "test_keypad_2"),
    ("regress/tty-keys.sh:ESC-SS3-r:M-KP2", "test_alt_keypad_2"),
    ("regress/tty-keys.sh:SS3-s:KP3", "test_keypad_3"),
    ("regress/tty-keys.sh:ESC-SS3-s:M-KP3", "test_alt_keypad_3"),
    ("regress/tty-keys.sh:SS3-t:KP4", "test_keypad_4"),
    ("regress/tty-keys.sh:ESC-SS3-t:M-KP4", "test_alt_keypad_4"),
    ("regress/tty-keys.sh:SS3-u:KP5", "test_keypad_5"),
    ("regress/tty-keys.sh:ESC-SS3-u:M-KP5", "test_alt_keypad_5"),
)


class TmuxRegressTtyKeysKeypadMidTest(unittest.TestCase):
    def _assert_keypad(self, key, suffix, meta):
        modifiers = ALT if meta else 0
        modifier = b"3" if meta else b""
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b=")
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(
                terminal.read_input(), b"\x1bO" + modifier + suffix
            )

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_keypad_add(self):
        self._assert_keypad(KEY_KP_ADD, b"k", False)

    def test_alt_keypad_add(self):
        self._assert_keypad(KEY_KP_ADD, b"k", True)

    def test_keypad_subtract(self):
        self._assert_keypad(KEY_KP_SUBTRACT, b"m", False)

    def test_alt_keypad_subtract(self):
        self._assert_keypad(KEY_KP_SUBTRACT, b"m", True)

    def test_keypad_decimal(self):
        self._assert_keypad(KEY_KP_DECIMAL, b"n", False)

    def test_alt_keypad_decimal(self):
        self._assert_keypad(KEY_KP_DECIMAL, b"n", True)

    def test_keypad_divide(self):
        self._assert_keypad(KEY_KP_DIVIDE, b"o", False)

    def test_alt_keypad_divide(self):
        self._assert_keypad(KEY_KP_DIVIDE, b"o", True)

    def test_keypad_0(self):
        self._assert_keypad(KEY_KP_0, b"p", False)

    def test_alt_keypad_0(self):
        self._assert_keypad(KEY_KP_0, b"p", True)

    def test_keypad_1(self):
        self._assert_keypad(KEY_KP_0 + 1, b"q", False)

    def test_alt_keypad_1(self):
        self._assert_keypad(KEY_KP_0 + 1, b"q", True)

    def test_keypad_2(self):
        self._assert_keypad(KEY_KP_0 + 2, b"r", False)

    def test_alt_keypad_2(self):
        self._assert_keypad(KEY_KP_0 + 2, b"r", True)

    def test_keypad_3(self):
        self._assert_keypad(KEY_KP_0 + 3, b"s", False)

    def test_alt_keypad_3(self):
        self._assert_keypad(KEY_KP_0 + 3, b"s", True)

    def test_keypad_4(self):
        self._assert_keypad(KEY_KP_0 + 4, b"t", False)

    def test_alt_keypad_4(self):
        self._assert_keypad(KEY_KP_0 + 4, b"t", True)

    def test_keypad_5(self):
        self._assert_keypad(KEY_KP_0 + 5, b"u", False)

    def test_alt_keypad_5(self):
        self._assert_keypad(KEY_KP_0 + 5, b"u", True)


if __name__ == "__main__":
    unittest.main()

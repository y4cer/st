# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Cursor and numeric-keypad cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
ALT = 4

KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264
KEY_KP_0 = 320
KEY_KP_DECIMAL = 330
KEY_KP_DIVIDE = 331
KEY_KP_MULTIPLY = 332
KEY_KP_SUBTRACT = 333
KEY_KP_ADD = 334


PORTED_CASES = (
    ("regress/input-keys.sh:Down", "test_down"),
    ("regress/input-keys.sh:Right", "test_right"),
    ("regress/input-keys.sh:Left", "test_left"),
    ("regress/input-keys.sh:KP*", "test_kp_multiply"),
    ("regress/input-keys.sh:M-KP*", "test_meta_kp_multiply"),
    ("regress/input-keys.sh:KP+", "test_kp_add"),
    ("regress/input-keys.sh:M-KP+", "test_meta_kp_add"),
    ("regress/input-keys.sh:KP-", "test_kp_subtract"),
    ("regress/input-keys.sh:M-KP-", "test_meta_kp_subtract"),
    ("regress/input-keys.sh:KP.", "test_kp_decimal"),
    ("regress/input-keys.sh:M-KP.", "test_meta_kp_decimal"),
    ("regress/input-keys.sh:KP/", "test_kp_divide"),
    ("regress/input-keys.sh:M-KP/", "test_meta_kp_divide"),
    ("regress/input-keys.sh:KP0", "test_kp_0"),
    ("regress/input-keys.sh:M-KP0", "test_meta_kp_0"),
    ("regress/input-keys.sh:KP1", "test_kp_1"),
    ("regress/input-keys.sh:M-KP1", "test_meta_kp_1"),
    ("regress/input-keys.sh:KP2", "test_kp_2"),
    ("regress/input-keys.sh:M-KP2", "test_meta_kp_2"),
    ("regress/input-keys.sh:KP3", "test_kp_3"),
    ("regress/input-keys.sh:M-KP3", "test_meta_kp_3"),
    ("regress/input-keys.sh:KP4", "test_kp_4"),
    ("regress/input-keys.sh:M-KP4", "test_meta_kp_4"),
    ("regress/input-keys.sh:KP5", "test_kp_5"),
    ("regress/input-keys.sh:M-KP5", "test_meta_kp_5"),
    ("regress/input-keys.sh:KP6", "test_kp_6"),
    ("regress/input-keys.sh:M-KP6", "test_meta_kp_6"),
    ("regress/input-keys.sh:KP7", "test_kp_7"),
    ("regress/input-keys.sh:M-KP7", "test_meta_kp_7"),
    ("regress/input-keys.sh:KP8", "test_kp_8"),
    ("regress/input-keys.sh:M-KP8", "test_meta_kp_8"),
    ("regress/input-keys.sh:KP9", "test_kp_9"),
    ("regress/input-keys.sh:M-KP9", "test_meta_kp_9"),
)


class TmuxRegressInputKeysKeypadTest(unittest.TestCase):
    def _assert_named(self, key, expected, modifiers=0):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                key,
                PRESS,
                modifiers=modifiers,
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_keypad(self, key, expected, meta):
        modifiers = ALT if meta else 0
        expected = (b"\x1b" if meta else b"") + expected
        self._assert_named(key, expected, modifiers)

    def test_upstream_inventory_has_33_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 33)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 33)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 33)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_down(self):
        self._assert_named(KEY_DOWN, b"\x1b[B")

    def test_right(self):
        self._assert_named(KEY_RIGHT, b"\x1b[C")

    def test_left(self):
        self._assert_named(KEY_LEFT, b"\x1b[D")

    def test_kp_multiply(self):
        self._assert_keypad(KEY_KP_MULTIPLY, b"*", False)

    def test_meta_kp_multiply(self):
        self._assert_keypad(KEY_KP_MULTIPLY, b"*", True)

    def test_kp_add(self):
        self._assert_keypad(KEY_KP_ADD, b"+", False)

    def test_meta_kp_add(self):
        self._assert_keypad(KEY_KP_ADD, b"+", True)

    def test_kp_subtract(self):
        self._assert_keypad(KEY_KP_SUBTRACT, b"-", False)

    def test_meta_kp_subtract(self):
        self._assert_keypad(KEY_KP_SUBTRACT, b"-", True)

    def test_kp_decimal(self):
        self._assert_keypad(KEY_KP_DECIMAL, b".", False)

    def test_meta_kp_decimal(self):
        self._assert_keypad(KEY_KP_DECIMAL, b".", True)

    def test_kp_divide(self):
        self._assert_keypad(KEY_KP_DIVIDE, b"/", False)

    def test_meta_kp_divide(self):
        self._assert_keypad(KEY_KP_DIVIDE, b"/", True)

    def test_kp_0(self):
        self._assert_keypad(KEY_KP_0, b"0", False)

    def test_meta_kp_0(self):
        self._assert_keypad(KEY_KP_0, b"0", True)

    def test_kp_1(self):
        self._assert_keypad(KEY_KP_0 + 1, b"1", False)

    def test_meta_kp_1(self):
        self._assert_keypad(KEY_KP_0 + 1, b"1", True)

    def test_kp_2(self):
        self._assert_keypad(KEY_KP_0 + 2, b"2", False)

    def test_meta_kp_2(self):
        self._assert_keypad(KEY_KP_0 + 2, b"2", True)

    def test_kp_3(self):
        self._assert_keypad(KEY_KP_0 + 3, b"3", False)

    def test_meta_kp_3(self):
        self._assert_keypad(KEY_KP_0 + 3, b"3", True)

    def test_kp_4(self):
        self._assert_keypad(KEY_KP_0 + 4, b"4", False)

    def test_meta_kp_4(self):
        self._assert_keypad(KEY_KP_0 + 4, b"4", True)

    def test_kp_5(self):
        self._assert_keypad(KEY_KP_0 + 5, b"5", False)

    def test_meta_kp_5(self):
        self._assert_keypad(KEY_KP_0 + 5, b"5", True)

    def test_kp_6(self):
        self._assert_keypad(KEY_KP_0 + 6, b"6", False)

    def test_meta_kp_6(self):
        self._assert_keypad(KEY_KP_0 + 6, b"6", True)

    def test_kp_7(self):
        self._assert_keypad(KEY_KP_0 + 7, b"7", False)

    def test_meta_kp_7(self):
        self._assert_keypad(KEY_KP_0 + 7, b"7", True)

    def test_kp_8(self):
        self._assert_keypad(KEY_KP_0 + 8, b"8", False)

    def test_meta_kp_8(self):
        self._assert_keypad(KEY_KP_0 + 8, b"8", True)

    def test_kp_9(self):
        self._assert_keypad(KEY_KP_0 + 9, b"9", False)

    def test_meta_kp_9(self):
        self._assert_keypad(KEY_KP_0 + 9, b"9", True)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Extended Down, Right and Left cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264


PORTED_CASES = (
    ("regress/input-keys.sh:S-Down", "test_shift_down"),
    ("regress/input-keys.sh:M-Down", "test_alt_down"),
    ("regress/input-keys.sh:S-M-Down", "test_shift_alt_down"),
    ("regress/input-keys.sh:C-Down", "test_control_down"),
    ("regress/input-keys.sh:S-C-Down", "test_shift_control_down"),
    ("regress/input-keys.sh:C-M-Down", "test_control_alt_down"),
    ("regress/input-keys.sh:S-C-M-Down", "test_shift_control_alt_down"),
    ("regress/input-keys.sh:S-Right", "test_shift_right"),
    ("regress/input-keys.sh:M-Right", "test_alt_right"),
    ("regress/input-keys.sh:S-M-Right", "test_shift_alt_right"),
    ("regress/input-keys.sh:C-Right", "test_control_right"),
    ("regress/input-keys.sh:S-C-Right", "test_shift_control_right"),
    ("regress/input-keys.sh:C-M-Right", "test_control_alt_right"),
    ("regress/input-keys.sh:S-C-M-Right", "test_shift_control_alt_right"),
    ("regress/input-keys.sh:S-Left", "test_shift_left"),
    ("regress/input-keys.sh:M-Left", "test_alt_left"),
    ("regress/input-keys.sh:S-M-Left", "test_shift_alt_left"),
    ("regress/input-keys.sh:C-Left", "test_control_left"),
    ("regress/input-keys.sh:S-C-Left", "test_shift_control_left"),
    ("regress/input-keys.sh:C-M-Left", "test_control_alt_left"),
    ("regress/input-keys.sh:S-C-M-Left", "test_shift_control_alt_left"),
)


class TmuxRegressInputKeysExtendedCursorHeadTest(unittest.TestCase):
    def _assert_cursor(self, key, final, modifiers):
        modifier_code = 1 + bool(modifiers & SHIFT) + 2 * bool(modifiers & ALT) + 4 * bool(modifiers & CONTROL)
        expected = f"\x1b[1;{modifier_code}{final}".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_shift_down(self):
        self._assert_cursor(KEY_DOWN, "B", SHIFT)

    def test_alt_down(self):
        self._assert_cursor(KEY_DOWN, "B", ALT)

    def test_shift_alt_down(self):
        self._assert_cursor(KEY_DOWN, "B", SHIFT | ALT)

    def test_control_down(self):
        self._assert_cursor(KEY_DOWN, "B", CONTROL)

    def test_shift_control_down(self):
        self._assert_cursor(KEY_DOWN, "B", SHIFT | CONTROL)

    def test_control_alt_down(self):
        self._assert_cursor(KEY_DOWN, "B", CONTROL | ALT)

    def test_shift_control_alt_down(self):
        self._assert_cursor(KEY_DOWN, "B", SHIFT | CONTROL | ALT)

    def test_shift_right(self):
        self._assert_cursor(KEY_RIGHT, "C", SHIFT)

    def test_alt_right(self):
        self._assert_cursor(KEY_RIGHT, "C", ALT)

    def test_shift_alt_right(self):
        self._assert_cursor(KEY_RIGHT, "C", SHIFT | ALT)

    def test_control_right(self):
        self._assert_cursor(KEY_RIGHT, "C", CONTROL)

    def test_shift_control_right(self):
        self._assert_cursor(KEY_RIGHT, "C", SHIFT | CONTROL)

    def test_control_alt_right(self):
        self._assert_cursor(KEY_RIGHT, "C", CONTROL | ALT)

    def test_shift_control_alt_right(self):
        self._assert_cursor(KEY_RIGHT, "C", SHIFT | CONTROL | ALT)

    def test_shift_left(self):
        self._assert_cursor(KEY_LEFT, "D", SHIFT)

    def test_alt_left(self):
        self._assert_cursor(KEY_LEFT, "D", ALT)

    def test_shift_alt_left(self):
        self._assert_cursor(KEY_LEFT, "D", SHIFT | ALT)

    def test_control_left(self):
        self._assert_cursor(KEY_LEFT, "D", CONTROL)

    def test_shift_control_left(self):
        self._assert_cursor(KEY_LEFT, "D", SHIFT | CONTROL)

    def test_control_alt_left(self):
        self._assert_cursor(KEY_LEFT, "D", CONTROL | ALT)

    def test_shift_control_alt_left(self):
        self._assert_cursor(KEY_LEFT, "D", SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

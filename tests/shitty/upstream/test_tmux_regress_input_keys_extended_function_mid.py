# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Second extended function-key block from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_F4 = 293
KEY_F5 = 294
KEY_F6 = 295


PORTED_CASES = (
    ("regress/input-keys.sh:S-F4", "test_shift_f4"),
    ("regress/input-keys.sh:M-F4", "test_alt_f4"),
    ("regress/input-keys.sh:S-M-F4", "test_shift_alt_f4"),
    ("regress/input-keys.sh:C-F4", "test_control_f4"),
    ("regress/input-keys.sh:S-C-F4", "test_shift_control_f4"),
    ("regress/input-keys.sh:C-M-F4", "test_control_alt_f4"),
    ("regress/input-keys.sh:S-C-M-F4", "test_shift_control_alt_f4"),
    ("regress/input-keys.sh:S-F5", "test_shift_f5"),
    ("regress/input-keys.sh:M-F5", "test_alt_f5"),
    ("regress/input-keys.sh:S-M-F5", "test_shift_alt_f5"),
    ("regress/input-keys.sh:C-F5", "test_control_f5"),
    ("regress/input-keys.sh:S-C-F5", "test_shift_control_f5"),
    ("regress/input-keys.sh:C-M-F5", "test_control_alt_f5"),
    ("regress/input-keys.sh:S-C-M-F5", "test_shift_control_alt_f5"),
    ("regress/input-keys.sh:S-F6", "test_shift_f6"),
    ("regress/input-keys.sh:M-F6", "test_alt_f6"),
    ("regress/input-keys.sh:S-M-F6", "test_shift_alt_f6"),
    ("regress/input-keys.sh:C-F6", "test_control_f6"),
    ("regress/input-keys.sh:S-C-F6", "test_shift_control_f6"),
    ("regress/input-keys.sh:C-M-F6", "test_control_alt_f6"),
    ("regress/input-keys.sh:S-C-M-F6", "test_shift_control_alt_f6"),
)


class TmuxRegressInputKeysExtendedFunctionMidTest(unittest.TestCase):
    def _assert_function(self, key, base, final, modifiers):
        modifier_code = 1 + bool(modifiers & SHIFT) + 2 * bool(modifiers & ALT) + 4 * bool(modifiers & CONTROL)
        expected = f"\x1b[{base};{modifier_code}{final}".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_shift_f4(self):
        self._assert_function(KEY_F4, 1, "S", SHIFT)

    def test_alt_f4(self):
        self._assert_function(KEY_F4, 1, "S", ALT)

    def test_shift_alt_f4(self):
        self._assert_function(KEY_F4, 1, "S", SHIFT | ALT)

    def test_control_f4(self):
        self._assert_function(KEY_F4, 1, "S", CONTROL)

    def test_shift_control_f4(self):
        self._assert_function(KEY_F4, 1, "S", SHIFT | CONTROL)

    def test_control_alt_f4(self):
        self._assert_function(KEY_F4, 1, "S", CONTROL | ALT)

    def test_shift_control_alt_f4(self):
        self._assert_function(KEY_F4, 1, "S", SHIFT | CONTROL | ALT)

    def test_shift_f5(self):
        self._assert_function(KEY_F5, 15, "~", SHIFT)

    def test_alt_f5(self):
        self._assert_function(KEY_F5, 15, "~", ALT)

    def test_shift_alt_f5(self):
        self._assert_function(KEY_F5, 15, "~", SHIFT | ALT)

    def test_control_f5(self):
        self._assert_function(KEY_F5, 15, "~", CONTROL)

    def test_shift_control_f5(self):
        self._assert_function(KEY_F5, 15, "~", SHIFT | CONTROL)

    def test_control_alt_f5(self):
        self._assert_function(KEY_F5, 15, "~", CONTROL | ALT)

    def test_shift_control_alt_f5(self):
        self._assert_function(KEY_F5, 15, "~", SHIFT | CONTROL | ALT)

    def test_shift_f6(self):
        self._assert_function(KEY_F6, 17, "~", SHIFT)

    def test_alt_f6(self):
        self._assert_function(KEY_F6, 17, "~", ALT)

    def test_shift_alt_f6(self):
        self._assert_function(KEY_F6, 17, "~", SHIFT | ALT)

    def test_control_f6(self):
        self._assert_function(KEY_F6, 17, "~", CONTROL)

    def test_shift_control_f6(self):
        self._assert_function(KEY_F6, 17, "~", SHIFT | CONTROL)

    def test_control_alt_f6(self):
        self._assert_function(KEY_F6, 17, "~", CONTROL | ALT)

    def test_shift_control_alt_f6(self):
        self._assert_function(KEY_F6, 17, "~", SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Third extended function-key block from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_F8 = 297
KEY_F9 = 298
KEY_F10 = 299


PORTED_CASES = (
    ("regress/input-keys.sh:S-F8", "test_shift_f8"),
    ("regress/input-keys.sh:M-F8", "test_alt_f8"),
    ("regress/input-keys.sh:S-M-F8", "test_shift_alt_f8"),
    ("regress/input-keys.sh:C-F8", "test_control_f8"),
    ("regress/input-keys.sh:S-C-F8", "test_shift_control_f8"),
    ("regress/input-keys.sh:C-M-F8", "test_control_alt_f8"),
    ("regress/input-keys.sh:S-C-M-F8", "test_shift_control_alt_f8"),
    ("regress/input-keys.sh:S-F9", "test_shift_f9"),
    ("regress/input-keys.sh:M-F9", "test_alt_f9"),
    ("regress/input-keys.sh:S-M-F9", "test_shift_alt_f9"),
    ("regress/input-keys.sh:C-F9", "test_control_f9"),
    ("regress/input-keys.sh:S-C-F9", "test_shift_control_f9"),
    ("regress/input-keys.sh:C-M-F9", "test_control_alt_f9"),
    ("regress/input-keys.sh:S-C-M-F9", "test_shift_control_alt_f9"),
    ("regress/input-keys.sh:S-F10", "test_shift_f10"),
    ("regress/input-keys.sh:M-F10", "test_alt_f10"),
    ("regress/input-keys.sh:S-M-F10", "test_shift_alt_f10"),
    ("regress/input-keys.sh:C-F10", "test_control_f10"),
    ("regress/input-keys.sh:S-C-F10", "test_shift_control_f10"),
    ("regress/input-keys.sh:C-M-F10", "test_control_alt_f10"),
    ("regress/input-keys.sh:S-C-M-F10", "test_shift_control_alt_f10"),
)


class TmuxRegressInputKeysExtendedFunctionMoreTest(unittest.TestCase):
    def _assert_function(self, key, base, modifiers):
        modifier_code = 1 + bool(modifiers & SHIFT) + 2 * bool(modifiers & ALT) + 4 * bool(modifiers & CONTROL)
        expected = f"\x1b[{base};{modifier_code}~".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_shift_f8(self):
        self._assert_function(KEY_F8, 19, SHIFT)

    def test_alt_f8(self):
        self._assert_function(KEY_F8, 19, ALT)

    def test_shift_alt_f8(self):
        self._assert_function(KEY_F8, 19, SHIFT | ALT)

    def test_control_f8(self):
        self._assert_function(KEY_F8, 19, CONTROL)

    def test_shift_control_f8(self):
        self._assert_function(KEY_F8, 19, SHIFT | CONTROL)

    def test_control_alt_f8(self):
        self._assert_function(KEY_F8, 19, CONTROL | ALT)

    def test_shift_control_alt_f8(self):
        self._assert_function(KEY_F8, 19, SHIFT | CONTROL | ALT)

    def test_shift_f9(self):
        self._assert_function(KEY_F9, 20, SHIFT)

    def test_alt_f9(self):
        self._assert_function(KEY_F9, 20, ALT)

    def test_shift_alt_f9(self):
        self._assert_function(KEY_F9, 20, SHIFT | ALT)

    def test_control_f9(self):
        self._assert_function(KEY_F9, 20, CONTROL)

    def test_shift_control_f9(self):
        self._assert_function(KEY_F9, 20, SHIFT | CONTROL)

    def test_control_alt_f9(self):
        self._assert_function(KEY_F9, 20, CONTROL | ALT)

    def test_shift_control_alt_f9(self):
        self._assert_function(KEY_F9, 20, SHIFT | CONTROL | ALT)

    def test_shift_f10(self):
        self._assert_function(KEY_F10, 21, SHIFT)

    def test_alt_f10(self):
        self._assert_function(KEY_F10, 21, ALT)

    def test_shift_alt_f10(self):
        self._assert_function(KEY_F10, 21, SHIFT | ALT)

    def test_control_f10(self):
        self._assert_function(KEY_F10, 21, CONTROL)

    def test_shift_control_f10(self):
        self._assert_function(KEY_F10, 21, SHIFT | CONTROL)

    def test_control_alt_f10(self):
        self._assert_function(KEY_F10, 21, CONTROL | ALT)

    def test_shift_control_alt_f10(self):
        self._assert_function(KEY_F10, 21, SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

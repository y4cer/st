# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First extended function-key cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_F1 = 290
KEY_F2 = 291
KEY_F3 = 292


PORTED_CASES = (
    ("regress/input-keys.sh:S-F1", "test_shift_f1"),
    ("regress/input-keys.sh:M-F1", "test_alt_f1"),
    ("regress/input-keys.sh:S-M-F1", "test_shift_alt_f1"),
    ("regress/input-keys.sh:C-F1", "test_control_f1"),
    ("regress/input-keys.sh:S-C-F1", "test_shift_control_f1"),
    ("regress/input-keys.sh:C-M-F1", "test_control_alt_f1"),
    ("regress/input-keys.sh:S-C-M-F1", "test_shift_control_alt_f1"),
    ("regress/input-keys.sh:S-F2", "test_shift_f2"),
    ("regress/input-keys.sh:M-F2", "test_alt_f2"),
    ("regress/input-keys.sh:S-M-F2", "test_shift_alt_f2"),
    ("regress/input-keys.sh:C-F2", "test_control_f2"),
    ("regress/input-keys.sh:S-C-F2", "test_shift_control_f2"),
    ("regress/input-keys.sh:C-M-F2", "test_control_alt_f2"),
    ("regress/input-keys.sh:S-C-M-F2", "test_shift_control_alt_f2"),
    ("regress/input-keys.sh:S-F3", "test_shift_f3"),
    ("regress/input-keys.sh:M-F3", "test_alt_f3"),
    ("regress/input-keys.sh:S-M-F3", "test_shift_alt_f3"),
    ("regress/input-keys.sh:C-F3", "test_control_f3"),
    ("regress/input-keys.sh:S-C-F3", "test_shift_control_f3"),
    ("regress/input-keys.sh:C-M-F3", "test_control_alt_f3"),
    ("regress/input-keys.sh:S-C-M-F3", "test_shift_control_alt_f3"),
)


class TmuxRegressInputKeysExtendedFunctionHeadTest(unittest.TestCase):
    def _assert_function(self, key, final, modifiers):
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

    def test_shift_f1(self):
        self._assert_function(KEY_F1, "P", SHIFT)

    def test_alt_f1(self):
        self._assert_function(KEY_F1, "P", ALT)

    def test_shift_alt_f1(self):
        self._assert_function(KEY_F1, "P", SHIFT | ALT)

    def test_control_f1(self):
        self._assert_function(KEY_F1, "P", CONTROL)

    def test_shift_control_f1(self):
        self._assert_function(KEY_F1, "P", SHIFT | CONTROL)

    def test_control_alt_f1(self):
        self._assert_function(KEY_F1, "P", CONTROL | ALT)

    def test_shift_control_alt_f1(self):
        self._assert_function(KEY_F1, "P", SHIFT | CONTROL | ALT)

    def test_shift_f2(self):
        self._assert_function(KEY_F2, "Q", SHIFT)

    def test_alt_f2(self):
        self._assert_function(KEY_F2, "Q", ALT)

    def test_shift_alt_f2(self):
        self._assert_function(KEY_F2, "Q", SHIFT | ALT)

    def test_control_f2(self):
        self._assert_function(KEY_F2, "Q", CONTROL)

    def test_shift_control_f2(self):
        self._assert_function(KEY_F2, "Q", SHIFT | CONTROL)

    def test_control_alt_f2(self):
        self._assert_function(KEY_F2, "Q", CONTROL | ALT)

    def test_shift_control_alt_f2(self):
        self._assert_function(KEY_F2, "Q", SHIFT | CONTROL | ALT)

    def test_shift_f3(self):
        self._assert_function(KEY_F3, "R", SHIFT)

    def test_alt_f3(self):
        self._assert_function(KEY_F3, "R", ALT)

    def test_shift_alt_f3(self):
        self._assert_function(KEY_F3, "R", SHIFT | ALT)

    def test_control_f3(self):
        self._assert_function(KEY_F3, "R", CONTROL)

    def test_shift_control_f3(self):
        self._assert_function(KEY_F3, "R", SHIFT | CONTROL)

    def test_control_alt_f3(self):
        self._assert_function(KEY_F3, "R", CONTROL | ALT)

    def test_shift_control_alt_f3(self):
        self._assert_function(KEY_F3, "R", SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

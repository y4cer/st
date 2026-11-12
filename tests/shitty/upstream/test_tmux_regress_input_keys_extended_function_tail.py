# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Last extended function keys and first cursor key from tmux input-keys."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_UP = 265
KEY_F11 = 300
KEY_F12 = 301


PORTED_CASES = (
    ("regress/input-keys.sh:S-F11", "test_shift_f11"),
    ("regress/input-keys.sh:M-F11", "test_alt_f11"),
    ("regress/input-keys.sh:S-M-F11", "test_shift_alt_f11"),
    ("regress/input-keys.sh:C-F11", "test_control_f11"),
    ("regress/input-keys.sh:S-C-F11", "test_shift_control_f11"),
    ("regress/input-keys.sh:C-M-F11", "test_control_alt_f11"),
    ("regress/input-keys.sh:S-C-M-F11", "test_shift_control_alt_f11"),
    ("regress/input-keys.sh:S-F12", "test_shift_f12"),
    ("regress/input-keys.sh:M-F12", "test_alt_f12"),
    ("regress/input-keys.sh:S-M-F12", "test_shift_alt_f12"),
    ("regress/input-keys.sh:C-F12", "test_control_f12"),
    ("regress/input-keys.sh:S-C-F12", "test_shift_control_f12"),
    ("regress/input-keys.sh:C-M-F12", "test_control_alt_f12"),
    ("regress/input-keys.sh:S-C-M-F12", "test_shift_control_alt_f12"),
    ("regress/input-keys.sh:S-Up", "test_shift_up"),
    ("regress/input-keys.sh:M-Up", "test_alt_up"),
    ("regress/input-keys.sh:S-M-Up", "test_shift_alt_up"),
    ("regress/input-keys.sh:C-Up", "test_control_up"),
    ("regress/input-keys.sh:S-C-Up", "test_shift_control_up"),
    ("regress/input-keys.sh:C-M-Up", "test_control_alt_up"),
    ("regress/input-keys.sh:S-C-M-Up", "test_shift_control_alt_up"),
)


class TmuxRegressInputKeysExtendedFunctionTailTest(unittest.TestCase):
    def _assert_key(self, key, base, final, modifiers):
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

    def test_shift_f11(self):
        self._assert_key(KEY_F11, 23, "~", SHIFT)

    def test_alt_f11(self):
        self._assert_key(KEY_F11, 23, "~", ALT)

    def test_shift_alt_f11(self):
        self._assert_key(KEY_F11, 23, "~", SHIFT | ALT)

    def test_control_f11(self):
        self._assert_key(KEY_F11, 23, "~", CONTROL)

    def test_shift_control_f11(self):
        self._assert_key(KEY_F11, 23, "~", SHIFT | CONTROL)

    def test_control_alt_f11(self):
        self._assert_key(KEY_F11, 23, "~", CONTROL | ALT)

    def test_shift_control_alt_f11(self):
        self._assert_key(KEY_F11, 23, "~", SHIFT | CONTROL | ALT)

    def test_shift_f12(self):
        self._assert_key(KEY_F12, 24, "~", SHIFT)

    def test_alt_f12(self):
        self._assert_key(KEY_F12, 24, "~", ALT)

    def test_shift_alt_f12(self):
        self._assert_key(KEY_F12, 24, "~", SHIFT | ALT)

    def test_control_f12(self):
        self._assert_key(KEY_F12, 24, "~", CONTROL)

    def test_shift_control_f12(self):
        self._assert_key(KEY_F12, 24, "~", SHIFT | CONTROL)

    def test_control_alt_f12(self):
        self._assert_key(KEY_F12, 24, "~", CONTROL | ALT)

    def test_shift_control_alt_f12(self):
        self._assert_key(KEY_F12, 24, "~", SHIFT | CONTROL | ALT)

    def test_shift_up(self):
        self._assert_key(KEY_UP, 1, "A", SHIFT)

    def test_alt_up(self):
        self._assert_key(KEY_UP, 1, "A", ALT)

    def test_shift_alt_up(self):
        self._assert_key(KEY_UP, 1, "A", SHIFT | ALT)

    def test_control_up(self):
        self._assert_key(KEY_UP, 1, "A", CONTROL)

    def test_shift_control_up(self):
        self._assert_key(KEY_UP, 1, "A", SHIFT | CONTROL)

    def test_control_alt_up(self):
        self._assert_key(KEY_UP, 1, "A", CONTROL | ALT)

    def test_shift_control_alt_up(self):
        self._assert_key(KEY_UP, 1, "A", SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

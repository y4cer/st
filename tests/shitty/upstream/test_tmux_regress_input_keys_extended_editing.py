# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Extended Insert and Delete aliases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_INSERT = 260
KEY_DELETE = 261


PORTED_CASES = (
    ("regress/input-keys.sh:S-Insert", "test_shift_insert"),
    ("regress/input-keys.sh:M-Insert", "test_alt_insert"),
    ("regress/input-keys.sh:S-M-Insert", "test_shift_alt_insert"),
    ("regress/input-keys.sh:C-Insert", "test_control_insert"),
    ("regress/input-keys.sh:S-C-Insert", "test_shift_control_insert"),
    ("regress/input-keys.sh:C-M-Insert", "test_control_alt_insert"),
    ("regress/input-keys.sh:S-C-M-Insert", "test_shift_control_alt_insert"),
    ("regress/input-keys.sh:S-DC", "test_shift_dc"),
    ("regress/input-keys.sh:M-DC", "test_alt_dc"),
    ("regress/input-keys.sh:S-M-DC", "test_shift_alt_dc"),
    ("regress/input-keys.sh:C-DC", "test_control_dc"),
    ("regress/input-keys.sh:S-C-DC", "test_shift_control_dc"),
    ("regress/input-keys.sh:C-M-DC", "test_control_alt_dc"),
    ("regress/input-keys.sh:S-C-M-DC", "test_shift_control_alt_dc"),
    ("regress/input-keys.sh:S-Delete", "test_shift_delete"),
    ("regress/input-keys.sh:M-Delete", "test_alt_delete"),
    ("regress/input-keys.sh:S-M-Delete", "test_shift_alt_delete"),
    ("regress/input-keys.sh:C-Delete", "test_control_delete"),
    ("regress/input-keys.sh:S-C-Delete", "test_shift_control_delete"),
    ("regress/input-keys.sh:C-M-Delete", "test_control_alt_delete"),
    ("regress/input-keys.sh:S-C-M-Delete", "test_shift_control_alt_delete"),
)


class TmuxRegressInputKeysExtendedEditingTest(unittest.TestCase):
    def _assert_editing(self, key, base, modifiers):
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

    def test_shift_insert(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_primary_selection(b"selection")
            terminal.set_system_clipboard(b"selection")
            terminal.frontend_key_event(KEY_INSERT, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"selection")

    def test_alt_insert(self):
        self._assert_editing(KEY_INSERT, 2, ALT)

    def test_shift_alt_insert(self):
        self._assert_editing(KEY_INSERT, 2, SHIFT | ALT)

    def test_control_insert(self):
        self._assert_editing(KEY_INSERT, 2, CONTROL)

    def test_shift_control_insert(self):
        self._assert_editing(KEY_INSERT, 2, SHIFT | CONTROL)

    def test_control_alt_insert(self):
        self._assert_editing(KEY_INSERT, 2, CONTROL | ALT)

    def test_shift_control_alt_insert(self):
        self._assert_editing(KEY_INSERT, 2, SHIFT | CONTROL | ALT)

    def test_shift_dc(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT)

    def test_alt_dc(self):
        self._assert_editing(KEY_DELETE, 3, ALT)

    def test_shift_alt_dc(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | ALT)

    def test_control_dc(self):
        self._assert_editing(KEY_DELETE, 3, CONTROL)

    def test_shift_control_dc(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | CONTROL)

    def test_control_alt_dc(self):
        self._assert_editing(KEY_DELETE, 3, CONTROL | ALT)

    def test_shift_control_alt_dc(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | CONTROL | ALT)

    def test_shift_delete(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT)

    def test_alt_delete(self):
        self._assert_editing(KEY_DELETE, 3, ALT)

    def test_shift_alt_delete(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | ALT)

    def test_control_delete(self):
        self._assert_editing(KEY_DELETE, 3, CONTROL)

    def test_shift_control_delete(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | CONTROL)

    def test_control_alt_delete(self):
        self._assert_editing(KEY_DELETE, 3, CONTROL | ALT)

    def test_shift_control_alt_delete(self):
        self._assert_editing(KEY_DELETE, 3, SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Extended Home, End and PPage cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_HOME = 268
KEY_END = 269
KEY_PAGE_UP = 266


PORTED_CASES = (
    ("regress/input-keys.sh:S-Home", "test_shift_home"),
    ("regress/input-keys.sh:M-Home", "test_alt_home"),
    ("regress/input-keys.sh:S-M-Home", "test_shift_alt_home"),
    ("regress/input-keys.sh:C-Home", "test_control_home"),
    ("regress/input-keys.sh:S-C-Home", "test_shift_control_home"),
    ("regress/input-keys.sh:C-M-Home", "test_control_alt_home"),
    ("regress/input-keys.sh:S-C-M-Home", "test_shift_control_alt_home"),
    ("regress/input-keys.sh:S-End", "test_shift_end"),
    ("regress/input-keys.sh:M-End", "test_alt_end"),
    ("regress/input-keys.sh:S-M-End", "test_shift_alt_end"),
    ("regress/input-keys.sh:C-End", "test_control_end"),
    ("regress/input-keys.sh:S-C-End", "test_shift_control_end"),
    ("regress/input-keys.sh:C-M-End", "test_control_alt_end"),
    ("regress/input-keys.sh:S-C-M-End", "test_shift_control_alt_end"),
    ("regress/input-keys.sh:S-PPage", "test_shift_ppage"),
    ("regress/input-keys.sh:M-PPage", "test_alt_ppage"),
    ("regress/input-keys.sh:S-M-PPage", "test_shift_alt_ppage"),
    ("regress/input-keys.sh:C-PPage", "test_control_ppage"),
    ("regress/input-keys.sh:S-C-PPage", "test_shift_control_ppage"),
    ("regress/input-keys.sh:C-M-PPage", "test_control_alt_ppage"),
    ("regress/input-keys.sh:S-C-M-PPage", "test_shift_control_alt_ppage"),
)


class TmuxRegressInputKeysExtendedNavigationHeadTest(unittest.TestCase):
    def _assert_navigation(self, key, base, final, modifiers):
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

    def test_shift_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", SHIFT)

    def test_alt_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", ALT)

    def test_shift_alt_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", SHIFT | ALT)

    def test_control_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", CONTROL)

    def test_shift_control_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", SHIFT | CONTROL)

    def test_control_alt_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", CONTROL | ALT)

    def test_shift_control_alt_home(self):
        self._assert_navigation(KEY_HOME, 1, "H", SHIFT | CONTROL | ALT)

    def test_shift_end(self):
        self._assert_navigation(KEY_END, 1, "F", SHIFT)

    def test_alt_end(self):
        self._assert_navigation(KEY_END, 1, "F", ALT)

    def test_shift_alt_end(self):
        self._assert_navigation(KEY_END, 1, "F", SHIFT | ALT)

    def test_control_end(self):
        self._assert_navigation(KEY_END, 1, "F", CONTROL)

    def test_shift_control_end(self):
        self._assert_navigation(KEY_END, 1, "F", SHIFT | CONTROL)

    def test_control_alt_end(self):
        self._assert_navigation(KEY_END, 1, "F", CONTROL | ALT)

    def test_shift_control_alt_end(self):
        self._assert_navigation(KEY_END, 1, "F", SHIFT | CONTROL | ALT)

    def test_shift_ppage(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"0\r\n1\r\n2\r\n3\r\n4")
            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.frontend_key_event(KEY_PAGE_UP, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"")
            self.assertGreater(terminal.snapshot().view_offset, 0)

    def test_alt_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", ALT)

    def test_shift_alt_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", SHIFT | ALT)

    def test_control_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", CONTROL)

    def test_shift_control_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", SHIFT | CONTROL)

    def test_control_alt_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", CONTROL | ALT)

    def test_shift_control_alt_ppage(self):
        self._assert_navigation(KEY_PAGE_UP, 5, "~", SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

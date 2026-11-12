# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Extended PageDown aliases and IC from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_INSERT = 260
KEY_PAGE_UP = 266
KEY_PAGE_DOWN = 267


PORTED_CASES = (
    ("regress/input-keys.sh:S-PageDown", "test_shift_page_down"),
    ("regress/input-keys.sh:M-PageDown", "test_alt_page_down"),
    ("regress/input-keys.sh:S-M-PageDown", "test_shift_alt_page_down"),
    ("regress/input-keys.sh:C-PageDown", "test_control_page_down"),
    ("regress/input-keys.sh:S-C-PageDown", "test_shift_control_page_down"),
    ("regress/input-keys.sh:C-M-PageDown", "test_control_alt_page_down"),
    ("regress/input-keys.sh:S-C-M-PageDown", "test_shift_control_alt_page_down"),
    ("regress/input-keys.sh:S-PgDn", "test_shift_pgdn"),
    ("regress/input-keys.sh:M-PgDn", "test_alt_pgdn"),
    ("regress/input-keys.sh:S-M-PgDn", "test_shift_alt_pgdn"),
    ("regress/input-keys.sh:C-PgDn", "test_control_pgdn"),
    ("regress/input-keys.sh:S-C-PgDn", "test_shift_control_pgdn"),
    ("regress/input-keys.sh:C-M-PgDn", "test_control_alt_pgdn"),
    ("regress/input-keys.sh:S-C-M-PgDn", "test_shift_control_alt_pgdn"),
    ("regress/input-keys.sh:S-IC", "test_shift_ic"),
    ("regress/input-keys.sh:M-IC", "test_alt_ic"),
    ("regress/input-keys.sh:S-M-IC", "test_shift_alt_ic"),
    ("regress/input-keys.sh:C-IC", "test_control_ic"),
    ("regress/input-keys.sh:S-C-IC", "test_shift_control_ic"),
    ("regress/input-keys.sh:C-M-IC", "test_control_alt_ic"),
    ("regress/input-keys.sh:S-C-M-IC", "test_shift_control_alt_ic"),
)


class TmuxRegressInputKeysExtendedPagingInsertTest(unittest.TestCase):
    def _assert_navigation(self, key, base, modifiers):
        modifier_code = 1 + bool(modifiers & SHIFT) + 2 * bool(modifiers & ALT) + 4 * bool(modifiers & CONTROL)
        expected = f"\x1b[{base};{modifier_code}~".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def _assert_page_down_scrolls(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"0\r\n1\r\n2\r\n3\r\n4")
            terminal.frontend_key_event(KEY_PAGE_UP, PRESS, modifiers=SHIFT)
            before = terminal.snapshot().view_offset
            self.assertGreater(before, 0)
            terminal.frontend_key_event(KEY_PAGE_DOWN, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"")
            self.assertLess(terminal.snapshot().view_offset, before)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_shift_page_down(self):
        self._assert_page_down_scrolls()

    def test_alt_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, ALT)

    def test_shift_alt_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | ALT)

    def test_control_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL)

    def test_shift_control_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL)

    def test_control_alt_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL | ALT)

    def test_shift_control_alt_page_down(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL | ALT)

    def test_shift_pgdn(self):
        self._assert_page_down_scrolls()

    def test_alt_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, ALT)

    def test_shift_alt_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | ALT)

    def test_control_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL)

    def test_shift_control_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL)

    def test_control_alt_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL | ALT)

    def test_shift_control_alt_pgdn(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL | ALT)

    def test_shift_ic(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_primary_selection(b"selection")
            terminal.set_system_clipboard(b"selection")
            terminal.frontend_key_event(KEY_INSERT, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"selection")

    def test_alt_ic(self):
        self._assert_navigation(KEY_INSERT, 2, ALT)

    def test_shift_alt_ic(self):
        self._assert_navigation(KEY_INSERT, 2, SHIFT | ALT)

    def test_control_ic(self):
        self._assert_navigation(KEY_INSERT, 2, CONTROL)

    def test_shift_control_ic(self):
        self._assert_navigation(KEY_INSERT, 2, SHIFT | CONTROL)

    def test_control_alt_ic(self):
        self._assert_navigation(KEY_INSERT, 2, CONTROL | ALT)

    def test_shift_control_alt_ic(self):
        self._assert_navigation(KEY_INSERT, 2, SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Extended PageUp aliases and NPage from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_PAGE_UP = 266
KEY_PAGE_DOWN = 267


PORTED_CASES = (
    ("regress/input-keys.sh:S-PageUp", "test_shift_page_up"),
    ("regress/input-keys.sh:M-PageUp", "test_alt_page_up"),
    ("regress/input-keys.sh:S-M-PageUp", "test_shift_alt_page_up"),
    ("regress/input-keys.sh:C-PageUp", "test_control_page_up"),
    ("regress/input-keys.sh:S-C-PageUp", "test_shift_control_page_up"),
    ("regress/input-keys.sh:C-M-PageUp", "test_control_alt_page_up"),
    ("regress/input-keys.sh:S-C-M-PageUp", "test_shift_control_alt_page_up"),
    ("regress/input-keys.sh:S-PgUp", "test_shift_pgup"),
    ("regress/input-keys.sh:M-PgUp", "test_alt_pgup"),
    ("regress/input-keys.sh:S-M-PgUp", "test_shift_alt_pgup"),
    ("regress/input-keys.sh:C-PgUp", "test_control_pgup"),
    ("regress/input-keys.sh:S-C-PgUp", "test_shift_control_pgup"),
    ("regress/input-keys.sh:C-M-PgUp", "test_control_alt_pgup"),
    ("regress/input-keys.sh:S-C-M-PgUp", "test_shift_control_alt_pgup"),
    ("regress/input-keys.sh:S-NPage", "test_shift_npage"),
    ("regress/input-keys.sh:M-NPage", "test_alt_npage"),
    ("regress/input-keys.sh:S-M-NPage", "test_shift_alt_npage"),
    ("regress/input-keys.sh:C-NPage", "test_control_npage"),
    ("regress/input-keys.sh:S-C-NPage", "test_shift_control_npage"),
    ("regress/input-keys.sh:C-M-NPage", "test_control_alt_npage"),
    ("regress/input-keys.sh:S-C-M-NPage", "test_shift_control_alt_npage"),
)


class TmuxRegressInputKeysExtendedPagingTest(unittest.TestCase):
    def _assert_navigation(self, key, base, modifiers):
        modifier_code = 1 + bool(modifiers & SHIFT) + 2 * bool(modifiers & ALT) + 4 * bool(modifiers & CONTROL)
        expected = f"\x1b[{base};{modifier_code}~".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def _fill_history(self, terminal):
        terminal.write(b"0\r\n1\r\n2\r\n3\r\n4")
        self.assertEqual(terminal.snapshot().view_offset, 0)

    def _assert_page_up_scrolls(self):
        with Shitty(columns=8, rows=2) as terminal:
            self._fill_history(terminal)
            terminal.frontend_key_event(KEY_PAGE_UP, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"")
            self.assertGreater(terminal.snapshot().view_offset, 0)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_shift_page_up(self):
        self._assert_page_up_scrolls()

    def test_alt_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, ALT)

    def test_shift_alt_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | ALT)

    def test_control_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, CONTROL)

    def test_shift_control_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | CONTROL)

    def test_control_alt_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, CONTROL | ALT)

    def test_shift_control_alt_page_up(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | CONTROL | ALT)

    def test_shift_pgup(self):
        self._assert_page_up_scrolls()

    def test_alt_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, ALT)

    def test_shift_alt_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | ALT)

    def test_control_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, CONTROL)

    def test_shift_control_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | CONTROL)

    def test_control_alt_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, CONTROL | ALT)

    def test_shift_control_alt_pgup(self):
        self._assert_navigation(KEY_PAGE_UP, 5, SHIFT | CONTROL | ALT)

    def test_shift_npage(self):
        with Shitty(columns=8, rows=2) as terminal:
            self._fill_history(terminal)
            terminal.frontend_key_event(KEY_PAGE_UP, PRESS, modifiers=SHIFT)
            before = terminal.snapshot().view_offset
            self.assertGreater(before, 0)
            terminal.frontend_key_event(KEY_PAGE_DOWN, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"")
            self.assertLess(terminal.snapshot().view_offset, before)

    def test_alt_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, ALT)

    def test_shift_alt_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | ALT)

    def test_control_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL)

    def test_shift_control_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL)

    def test_control_alt_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, CONTROL | ALT)

    def test_shift_control_alt_npage(self):
        self._assert_navigation(KEY_PAGE_DOWN, 6, SHIFT | CONTROL | ALT)


if __name__ == "__main__":
    unittest.main()

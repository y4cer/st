# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Function and navigation cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2

KEY_TAB = 258
KEY_INSERT = 260
KEY_DELETE = 261
KEY_UP = 265
KEY_PAGE_UP = 266
KEY_PAGE_DOWN = 267
KEY_HOME = 268
KEY_END = 269
KEY_F1 = 290


PORTED_CASES = (
    ("regress/input-keys.sh:F8", "test_f8"),
    ("regress/input-keys.sh:F9", "test_f9"),
    ("regress/input-keys.sh:F10", "test_f10"),
    ("regress/input-keys.sh:F11", "test_f11"),
    ("regress/input-keys.sh:F12", "test_f12"),
    ("regress/input-keys.sh:IC", "test_ic"),
    ("regress/input-keys.sh:Insert", "test_insert"),
    ("regress/input-keys.sh:DC", "test_dc"),
    ("regress/input-keys.sh:Delete", "test_delete"),
    ("regress/input-keys.sh:Home", "test_home"),
    ("regress/input-keys.sh:End", "test_end"),
    ("regress/input-keys.sh:NPage", "test_npage"),
    ("regress/input-keys.sh:PageDown", "test_page_down"),
    ("regress/input-keys.sh:PgDn", "test_pgdn"),
    ("regress/input-keys.sh:PPage", "test_ppage"),
    ("regress/input-keys.sh:PageUp", "test_page_up"),
    ("regress/input-keys.sh:PgUp", "test_pgup"),
    ("regress/input-keys.sh:BTab", "test_backtab"),
    ("regress/input-keys.sh:C-S-Tab", "test_control_shift_tab"),
    ("regress/input-keys.sh:Up", "test_up"),
)


class TmuxRegressInputKeysNavigationHeadTest(unittest.TestCase):
    def _assert_named(self, key, expected, modifiers=0):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                key,
                PRESS,
                modifiers=modifiers,
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_f8(self):
        self._assert_named(KEY_F1 + 7, b"\x1b[19~")

    def test_f9(self):
        self._assert_named(KEY_F1 + 8, b"\x1b[20~")

    def test_f10(self):
        self._assert_named(KEY_F1 + 9, b"\x1b[21~")

    def test_f11(self):
        self._assert_named(KEY_F1 + 10, b"\x1b[23~")

    def test_f12(self):
        self._assert_named(KEY_F1 + 11, b"\x1b[24~")

    def test_ic(self):
        self._assert_named(KEY_INSERT, b"\x1b[2~")

    def test_insert(self):
        self._assert_named(KEY_INSERT, b"\x1b[2~")

    def test_dc(self):
        self._assert_named(KEY_DELETE, b"\x1b[3~")

    def test_delete(self):
        self._assert_named(KEY_DELETE, b"\x1b[3~")

    def test_home(self):
        self._assert_named(KEY_HOME, b"\x1b[H")

    def test_end(self):
        self._assert_named(KEY_END, b"\x1b[F")

    def test_npage(self):
        self._assert_named(KEY_PAGE_DOWN, b"\x1b[6~")

    def test_page_down(self):
        self._assert_named(KEY_PAGE_DOWN, b"\x1b[6~")

    def test_pgdn(self):
        self._assert_named(KEY_PAGE_DOWN, b"\x1b[6~")

    def test_ppage(self):
        self._assert_named(KEY_PAGE_UP, b"\x1b[5~")

    def test_page_up(self):
        self._assert_named(KEY_PAGE_UP, b"\x1b[5~")

    def test_pgup(self):
        self._assert_named(KEY_PAGE_UP, b"\x1b[5~")

    def test_backtab(self):
        self._assert_named(KEY_TAB, b"\x1b[Z", SHIFT)

    def test_control_shift_tab(self):
        self._assert_named(KEY_TAB, b"\x1b[Z", CONTROL | SHIFT)

    def test_up(self):
        self._assert_named(KEY_UP, b"\x1b[A")


if __name__ == "__main__":
    unittest.main()

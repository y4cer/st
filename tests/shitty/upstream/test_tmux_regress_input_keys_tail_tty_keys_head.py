# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Tail input-keys and first tty-keys cases from current tmux regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_TAB = 258


PORTED_CASES = (
    ("regress/input-keys.sh:extended:C-Tab", "test_extended_control_tab"),
    (
        "regress/input-keys.sh:extended:C-S-Tab",
        "test_extended_control_shift_tab",
    ),
    ("regress/tty-keys.sh:0x00:C-Space", "test_tty_control_space"),
    ("regress/tty-keys.sh:0x01:C-a", "test_tty_control_a"),
    ("regress/tty-keys.sh:ESC-0x01:C-M-a", "test_tty_control_alt_a"),
    ("regress/tty-keys.sh:0x02:C-b", "test_tty_control_b"),
    ("regress/tty-keys.sh:ESC-0x02:C-M-b", "test_tty_control_alt_b"),
    ("regress/tty-keys.sh:0x03:C-c", "test_tty_control_c"),
    ("regress/tty-keys.sh:ESC-0x03:C-M-c", "test_tty_control_alt_c"),
    ("regress/tty-keys.sh:0x04:C-d", "test_tty_control_d"),
    ("regress/tty-keys.sh:ESC-0x04:C-M-d", "test_tty_control_alt_d"),
    ("regress/tty-keys.sh:0x05:C-e", "test_tty_control_e"),
    ("regress/tty-keys.sh:ESC-0x05:C-M-e", "test_tty_control_alt_e"),
    ("regress/tty-keys.sh:0x06:C-f", "test_tty_control_f"),
    ("regress/tty-keys.sh:ESC-0x06:C-M-f", "test_tty_control_alt_f"),
    ("regress/tty-keys.sh:0x07:C-g", "test_tty_control_g"),
    ("regress/tty-keys.sh:ESC-0x07:C-M-g", "test_tty_control_alt_g"),
    ("regress/tty-keys.sh:0x08:C-h", "test_tty_control_h"),
    ("regress/tty-keys.sh:ESC-0x08:C-M-h", "test_tty_control_alt_h"),
    ("regress/tty-keys.sh:0x09:Tab", "test_tty_tab"),
    ("regress/tty-keys.sh:ESC-0x09:M-Tab", "test_tty_alt_tab"),
    ("regress/tty-keys.sh:0x0A:C-j", "test_tty_control_j"),
)


class TmuxRegressInputKeysTailTtyKeysHeadTest(unittest.TestCase):
    def _assert_character(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_named(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_extended_control_tab(self):
        self._assert_named(KEY_TAB, CONTROL, b"\x1b[27;5;9~")

    def test_extended_control_shift_tab(self):
        self._assert_named(KEY_TAB, CONTROL | SHIFT, b"\x1b[Z")

    def test_tty_control_space(self):
        self._assert_character(" ", CONTROL, b"\x00")

    def test_tty_control_a(self):
        self._assert_character("a", CONTROL, b"\x01")

    def test_tty_control_alt_a(self):
        self._assert_character("a", CONTROL | ALT, b"\x1b\x01")

    def test_tty_control_b(self):
        self._assert_character("b", CONTROL, b"\x02")

    def test_tty_control_alt_b(self):
        self._assert_character("b", CONTROL | ALT, b"\x1b\x02")

    def test_tty_control_c(self):
        self._assert_character("c", CONTROL, b"\x03")

    def test_tty_control_alt_c(self):
        self._assert_character("c", CONTROL | ALT, b"\x1b\x03")

    def test_tty_control_d(self):
        self._assert_character("d", CONTROL, b"\x04")

    def test_tty_control_alt_d(self):
        self._assert_character("d", CONTROL | ALT, b"\x1b\x04")

    def test_tty_control_e(self):
        self._assert_character("e", CONTROL, b"\x05")

    def test_tty_control_alt_e(self):
        self._assert_character("e", CONTROL | ALT, b"\x1b\x05")

    def test_tty_control_f(self):
        self._assert_character("f", CONTROL, b"\x06")

    def test_tty_control_alt_f(self):
        self._assert_character("f", CONTROL | ALT, b"\x1b\x06")

    def test_tty_control_g(self):
        self._assert_character("g", CONTROL, b"\x07")

    def test_tty_control_alt_g(self):
        self._assert_character("g", CONTROL | ALT, b"\x1b\x07")

    def test_tty_control_h(self):
        self._assert_character("h", CONTROL, b"\x08")

    def test_tty_control_alt_h(self):
        self._assert_character("h", CONTROL | ALT, b"\x1b\x08")

    def test_tty_tab(self):
        self._assert_named(KEY_TAB, 0, b"\x09")

    def test_tty_alt_tab(self):
        self._assert_named(KEY_TAB, ALT, b"\x1b\x09")

    def test_tty_control_j(self):
        self._assert_character("j", CONTROL, b"\x0a")


if __name__ == "__main__":
    unittest.main()

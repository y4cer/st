# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Next legacy control cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
CONTROL = 2
ALT = 4

KEY_ENTER = 257


PORTED_CASES = (
    ("regress/tty-keys.sh:ESC-0x0A:C-M-j", "test_control_alt_j"),
    ("regress/tty-keys.sh:0x0B:C-k", "test_control_k"),
    ("regress/tty-keys.sh:ESC-0x0B:C-M-k", "test_control_alt_k"),
    ("regress/tty-keys.sh:0x0C:C-l", "test_control_l"),
    ("regress/tty-keys.sh:ESC-0x0C:C-M-l", "test_control_alt_l"),
    ("regress/tty-keys.sh:0x0D:Enter", "test_enter"),
    ("regress/tty-keys.sh:ESC-0x0D:M-Enter", "test_alt_enter"),
    ("regress/tty-keys.sh:0x0E:C-n", "test_control_n"),
    ("regress/tty-keys.sh:ESC-0x0E:C-M-n", "test_control_alt_n"),
    ("regress/tty-keys.sh:0x0F:C-o", "test_control_o"),
    ("regress/tty-keys.sh:ESC-0x0F:C-M-o", "test_control_alt_o"),
    ("regress/tty-keys.sh:0x10:C-p", "test_control_p"),
    ("regress/tty-keys.sh:ESC-0x10:C-M-p", "test_control_alt_p"),
    ("regress/tty-keys.sh:0x11:C-q", "test_control_q"),
    ("regress/tty-keys.sh:ESC-0x11:C-M-q", "test_control_alt_q"),
    ("regress/tty-keys.sh:0x12:C-r", "test_control_r"),
    ("regress/tty-keys.sh:ESC-0x12:C-M-r", "test_control_alt_r"),
    ("regress/tty-keys.sh:0x13:C-s", "test_control_s"),
    ("regress/tty-keys.sh:ESC-0x13:C-M-s", "test_control_alt_s"),
    ("regress/tty-keys.sh:0x14:C-t", "test_control_t"),
    ("regress/tty-keys.sh:ESC-0x14:C-M-t", "test_control_alt_t"),
)


class TmuxRegressTtyKeysControlMidTest(unittest.TestCase):
    def _assert_character(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_control(self, key, byte):
        self._assert_character(key, CONTROL, bytes((byte,)))

    def _assert_control_alt(self, key, byte):
        self._assert_character(key, CONTROL | ALT, bytes((0x1B, byte)))

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_alt_j(self):
        self._assert_control_alt("j", 0x0A)

    def test_control_k(self):
        self._assert_control("k", 0x0B)

    def test_control_alt_k(self):
        self._assert_control_alt("k", 0x0B)

    def test_control_l(self):
        self._assert_control("l", 0x0C)

    def test_control_alt_l(self):
        self._assert_control_alt("l", 0x0C)

    def test_enter(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_ENTER, PRESS)
            self.assertEqual(terminal.read_input(), b"\r")

    def test_alt_enter(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_ENTER, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b\r")

    def test_control_n(self):
        self._assert_control("n", 0x0E)

    def test_control_alt_n(self):
        self._assert_control_alt("n", 0x0E)

    def test_control_o(self):
        self._assert_control("o", 0x0F)

    def test_control_alt_o(self):
        self._assert_control_alt("o", 0x0F)

    def test_control_p(self):
        self._assert_control("p", 0x10)

    def test_control_alt_p(self):
        self._assert_control_alt("p", 0x10)

    def test_control_q(self):
        self._assert_control("q", 0x11)

    def test_control_alt_q(self):
        self._assert_control_alt("q", 0x11)

    def test_control_r(self):
        self._assert_control("r", 0x12)

    def test_control_alt_r(self):
        self._assert_control_alt("r", 0x12)

    def test_control_s(self):
        self._assert_control("s", 0x13)

    def test_control_alt_s(self):
        self._assert_control_alt("s", 0x13)

    def test_control_t(self):
        self._assert_control("t", 0x14)

    def test_control_alt_t(self):
        self._assert_control_alt("t", 0x14)


if __name__ == "__main__":
    unittest.main()

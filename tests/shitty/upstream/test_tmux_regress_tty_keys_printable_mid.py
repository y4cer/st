# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Next printable cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x2B:+", "test_plus"),
    ("regress/tty-keys.sh:ESC-0x2B:M-+", "test_alt_plus"),
    ("regress/tty-keys.sh:0x2C:,", "test_comma"),
    ("regress/tty-keys.sh:ESC-0x2C:M-,", "test_alt_comma"),
    ("regress/tty-keys.sh:0x2D:-", "test_minus"),
    ("regress/tty-keys.sh:ESC-0x2D:M--", "test_alt_minus"),
    ("regress/tty-keys.sh:0x2E:.", "test_period"),
    ("regress/tty-keys.sh:ESC-0x2E:M-.", "test_alt_period"),
    ("regress/tty-keys.sh:0x2F:/", "test_slash"),
    ("regress/tty-keys.sh:ESC-0x2F:M-/", "test_alt_slash"),
    ("regress/tty-keys.sh:0x30:0", "test_zero"),
    ("regress/tty-keys.sh:ESC-0x30:M-0", "test_alt_zero"),
    ("regress/tty-keys.sh:0x31:1", "test_one"),
    ("regress/tty-keys.sh:ESC-0x31:M-1", "test_alt_one"),
    ("regress/tty-keys.sh:0x32:2", "test_two"),
    ("regress/tty-keys.sh:ESC-0x32:M-2", "test_alt_two"),
    ("regress/tty-keys.sh:0x33:3", "test_three"),
    ("regress/tty-keys.sh:ESC-0x33:M-3", "test_alt_three"),
    ("regress/tty-keys.sh:0x34:4", "test_four"),
    ("regress/tty-keys.sh:ESC-0x34:M-4", "test_alt_four"),
    ("regress/tty-keys.sh:0x35:5", "test_five"),
    ("regress/tty-keys.sh:ESC-0x35:M-5", "test_alt_five"),
)


class TmuxRegressTtyKeysPrintableMidTest(unittest.TestCase):
    def _assert_printable(self, base, output, shifted, meta):
        modifiers = (SHIFT if shifted else 0) | (ALT if meta else 0)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                base,
                base,
                base,
                modifiers=modifiers,
                shifted=output if shifted else 0,
            )
            terminal.frontend_text_event(output, modifiers=modifiers)
            expected = (b"\x1b" if meta else b"") + output.encode()
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_plus(self):
        self._assert_printable("=", "+", True, False)

    def test_alt_plus(self):
        self._assert_printable("=", "+", True, True)

    def test_comma(self):
        self._assert_printable(",", ",", False, False)

    def test_alt_comma(self):
        self._assert_printable(",", ",", False, True)

    def test_minus(self):
        self._assert_printable("-", "-", False, False)

    def test_alt_minus(self):
        self._assert_printable("-", "-", False, True)

    def test_period(self):
        self._assert_printable(".", ".", False, False)

    def test_alt_period(self):
        self._assert_printable(".", ".", False, True)

    def test_slash(self):
        self._assert_printable("/", "/", False, False)

    def test_alt_slash(self):
        self._assert_printable("/", "/", False, True)

    def test_zero(self):
        self._assert_printable("0", "0", False, False)

    def test_alt_zero(self):
        self._assert_printable("0", "0", False, True)

    def test_one(self):
        self._assert_printable("1", "1", False, False)

    def test_alt_one(self):
        self._assert_printable("1", "1", False, True)

    def test_two(self):
        self._assert_printable("2", "2", False, False)

    def test_alt_two(self):
        self._assert_printable("2", "2", False, True)

    def test_three(self):
        self._assert_printable("3", "3", False, False)

    def test_alt_three(self):
        self._assert_printable("3", "3", False, True)

    def test_four(self):
        self._assert_printable("4", "4", False, False)

    def test_alt_four(self):
        self._assert_printable("4", "4", False, True)

    def test_five(self):
        self._assert_printable("5", "5", False, False)

    def test_alt_five(self):
        self._assert_printable("5", "5", False, True)


if __name__ == "__main__":
    unittest.main()

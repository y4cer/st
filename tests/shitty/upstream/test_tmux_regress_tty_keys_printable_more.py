# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""More printable cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x36:6", "test_six"),
    ("regress/tty-keys.sh:ESC-0x36:M-6", "test_alt_six"),
    ("regress/tty-keys.sh:0x37:7", "test_seven"),
    ("regress/tty-keys.sh:ESC-0x37:M-7", "test_alt_seven"),
    ("regress/tty-keys.sh:0x38:8", "test_eight"),
    ("regress/tty-keys.sh:ESC-0x38:M-8", "test_alt_eight"),
    ("regress/tty-keys.sh:0x39:9", "test_nine"),
    ("regress/tty-keys.sh:ESC-0x39:M-9", "test_alt_nine"),
    ("regress/tty-keys.sh:0x3A::", "test_colon"),
    ("regress/tty-keys.sh:ESC-0x3A:M-:", "test_alt_colon"),
    ("regress/tty-keys.sh:0x3B:;", "test_semicolon"),
    ("regress/tty-keys.sh:ESC-0x3B:M-;", "test_alt_semicolon"),
    ("regress/tty-keys.sh:0x3C:<", "test_less_than"),
    ("regress/tty-keys.sh:ESC-0x3C:M-<", "test_alt_less_than"),
    ("regress/tty-keys.sh:0x3D:=", "test_equals"),
    ("regress/tty-keys.sh:ESC-0x3D:M-=", "test_alt_equals"),
    ("regress/tty-keys.sh:0x3E:>", "test_greater_than"),
    ("regress/tty-keys.sh:ESC-0x3E:M->", "test_alt_greater_than"),
    ("regress/tty-keys.sh:0x3F:?", "test_question"),
    ("regress/tty-keys.sh:ESC-0x3F:M-?", "test_alt_question"),
    ("regress/tty-keys.sh:0x40:@", "test_at"),
    ("regress/tty-keys.sh:ESC-0x40:M-@", "test_alt_at"),
)


class TmuxRegressTtyKeysPrintableMoreTest(unittest.TestCase):
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

    def test_six(self):
        self._assert_printable("6", "6", False, False)

    def test_alt_six(self):
        self._assert_printable("6", "6", False, True)

    def test_seven(self):
        self._assert_printable("7", "7", False, False)

    def test_alt_seven(self):
        self._assert_printable("7", "7", False, True)

    def test_eight(self):
        self._assert_printable("8", "8", False, False)

    def test_alt_eight(self):
        self._assert_printable("8", "8", False, True)

    def test_nine(self):
        self._assert_printable("9", "9", False, False)

    def test_alt_nine(self):
        self._assert_printable("9", "9", False, True)

    def test_colon(self):
        self._assert_printable(";", ":", True, False)

    def test_alt_colon(self):
        self._assert_printable(";", ":", True, True)

    def test_semicolon(self):
        self._assert_printable(";", ";", False, False)

    def test_alt_semicolon(self):
        self._assert_printable(";", ";", False, True)

    def test_less_than(self):
        self._assert_printable(",", "<", True, False)

    def test_alt_less_than(self):
        self._assert_printable(",", "<", True, True)

    def test_equals(self):
        self._assert_printable("=", "=", False, False)

    def test_alt_equals(self):
        self._assert_printable("=", "=", False, True)

    def test_greater_than(self):
        self._assert_printable(".", ">", True, False)

    def test_alt_greater_than(self):
        self._assert_printable(".", ">", True, True)

    def test_question(self):
        self._assert_printable("/", "?", True, False)

    def test_alt_question(self):
        self._assert_printable("/", "?", True, True)

    def test_at(self):
        self._assert_printable("2", "@", True, False)

    def test_alt_at(self):
        self._assert_printable("2", "@", True, True)


if __name__ == "__main__":
    unittest.main()

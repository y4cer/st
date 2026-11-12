# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Uppercase tail and punctuation from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x57:W", "test_w"),
    ("regress/tty-keys.sh:ESC-0x57:M-W", "test_alt_w"),
    ("regress/tty-keys.sh:0x58:X", "test_x"),
    ("regress/tty-keys.sh:ESC-0x58:M-X", "test_alt_x"),
    ("regress/tty-keys.sh:0x59:Y", "test_y"),
    ("regress/tty-keys.sh:ESC-0x59:M-Y", "test_alt_y"),
    ("regress/tty-keys.sh:0x5A:Z", "test_z"),
    ("regress/tty-keys.sh:ESC-0x5A:M-Z", "test_alt_z"),
    ("regress/tty-keys.sh:0x5B:[", "test_left_bracket"),
    ("regress/tty-keys.sh:ESC-0x5B:M-[", "test_alt_left_bracket"),
    ("regress/tty-keys.sh:0x5C:backslash", "test_backslash"),
    ("regress/tty-keys.sh:ESC-0x5C:M-backslash", "test_alt_backslash"),
    ("regress/tty-keys.sh:0x5D:]", "test_right_bracket"),
    ("regress/tty-keys.sh:ESC-0x5D:M-]", "test_alt_right_bracket"),
    ("regress/tty-keys.sh:0x5E:^", "test_caret"),
    ("regress/tty-keys.sh:ESC-0x5E:M-^", "test_alt_caret"),
    ("regress/tty-keys.sh:0x5F:_", "test_underscore"),
    ("regress/tty-keys.sh:ESC-0x5F:M-_", "test_alt_underscore"),
    ("regress/tty-keys.sh:0x60:backtick", "test_backtick"),
    ("regress/tty-keys.sh:ESC-0x60:M-backtick", "test_alt_backtick"),
    ("regress/tty-keys.sh:0x61:a", "test_a"),
    ("regress/tty-keys.sh:ESC-0x61:M-a", "test_alt_a"),
)


class TmuxRegressTtyKeysPrintableUpperTailTest(unittest.TestCase):
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

    def test_w(self):
        self._assert_printable("w", "W", True, False)

    def test_alt_w(self):
        self._assert_printable("w", "W", True, True)

    def test_x(self):
        self._assert_printable("x", "X", True, False)

    def test_alt_x(self):
        self._assert_printable("x", "X", True, True)

    def test_y(self):
        self._assert_printable("y", "Y", True, False)

    def test_alt_y(self):
        self._assert_printable("y", "Y", True, True)

    def test_z(self):
        self._assert_printable("z", "Z", True, False)

    def test_alt_z(self):
        self._assert_printable("z", "Z", True, True)

    def test_left_bracket(self):
        self._assert_printable("[", "[", False, False)

    def test_alt_left_bracket(self):
        self._assert_printable("[", "[", False, True)

    def test_backslash(self):
        self._assert_printable("\\", "\\", False, False)

    def test_alt_backslash(self):
        self._assert_printable("\\", "\\", False, True)

    def test_right_bracket(self):
        self._assert_printable("]", "]", False, False)

    def test_alt_right_bracket(self):
        self._assert_printable("]", "]", False, True)

    def test_caret(self):
        self._assert_printable("6", "^", True, False)

    def test_alt_caret(self):
        self._assert_printable("6", "^", True, True)

    def test_underscore(self):
        self._assert_printable("-", "_", True, False)

    def test_alt_underscore(self):
        self._assert_printable("-", "_", True, True)

    def test_backtick(self):
        self._assert_printable("`", "`", False, False)

    def test_alt_backtick(self):
        self._assert_printable("`", "`", False, True)

    def test_a(self):
        self._assert_printable("a", "a", False, False)

    def test_alt_a(self):
        self._assert_printable("a", "a", False, True)


if __name__ == "__main__":
    unittest.main()

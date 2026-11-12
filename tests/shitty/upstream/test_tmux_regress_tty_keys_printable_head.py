# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First printable cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x20:Space", "test_space"),
    ("regress/tty-keys.sh:ESC-0x20:M-Space", "test_alt_space"),
    ("regress/tty-keys.sh:0x21:!", "test_exclamation"),
    ("regress/tty-keys.sh:ESC-0x21:M-!", "test_alt_exclamation"),
    ('regress/tty-keys.sh:0x22:"', "test_double_quote"),
    ('regress/tty-keys.sh:ESC-0x22:M-"', "test_alt_double_quote"),
    ("regress/tty-keys.sh:0x23:#", "test_number_sign"),
    ("regress/tty-keys.sh:ESC-0x23:M-#", "test_alt_number_sign"),
    ("regress/tty-keys.sh:0x24:$", "test_dollar"),
    ("regress/tty-keys.sh:ESC-0x24:M-$", "test_alt_dollar"),
    ("regress/tty-keys.sh:0x25:%", "test_percent"),
    ("regress/tty-keys.sh:ESC-0x25:M-%", "test_alt_percent"),
    ("regress/tty-keys.sh:0x26:&", "test_ampersand"),
    ("regress/tty-keys.sh:ESC-0x26:M-&", "test_alt_ampersand"),
    ("regress/tty-keys.sh:0x27:apostrophe", "test_apostrophe"),
    ("regress/tty-keys.sh:ESC-0x27:M-apostrophe", "test_alt_apostrophe"),
    ("regress/tty-keys.sh:0x28:(", "test_left_parenthesis"),
    ("regress/tty-keys.sh:ESC-0x28:M-(", "test_alt_left_parenthesis"),
    ("regress/tty-keys.sh:0x29:)", "test_right_parenthesis"),
    ("regress/tty-keys.sh:ESC-0x29:M-)", "test_alt_right_parenthesis"),
    ("regress/tty-keys.sh:0x2A:*", "test_asterisk"),
    ("regress/tty-keys.sh:ESC-0x2A:M-*", "test_alt_asterisk"),
)


class TmuxRegressTtyKeysPrintableHeadTest(unittest.TestCase):
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

    def test_space(self):
        self._assert_printable(" ", " ", False, False)

    def test_alt_space(self):
        self._assert_printable(" ", " ", False, True)

    def test_exclamation(self):
        self._assert_printable("1", "!", True, False)

    def test_alt_exclamation(self):
        self._assert_printable("1", "!", True, True)

    def test_double_quote(self):
        self._assert_printable("'", '"', True, False)

    def test_alt_double_quote(self):
        self._assert_printable("'", '"', True, True)

    def test_number_sign(self):
        self._assert_printable("3", "#", True, False)

    def test_alt_number_sign(self):
        self._assert_printable("3", "#", True, True)

    def test_dollar(self):
        self._assert_printable("4", "$", True, False)

    def test_alt_dollar(self):
        self._assert_printable("4", "$", True, True)

    def test_percent(self):
        self._assert_printable("5", "%", True, False)

    def test_alt_percent(self):
        self._assert_printable("5", "%", True, True)

    def test_ampersand(self):
        self._assert_printable("7", "&", True, False)

    def test_alt_ampersand(self):
        self._assert_printable("7", "&", True, True)

    def test_apostrophe(self):
        self._assert_printable("'", "'", False, False)

    def test_alt_apostrophe(self):
        self._assert_printable("'", "'", False, True)

    def test_left_parenthesis(self):
        self._assert_printable("9", "(", True, False)

    def test_alt_left_parenthesis(self):
        self._assert_printable("9", "(", True, True)

    def test_right_parenthesis(self):
        self._assert_printable("0", ")", True, False)

    def test_alt_right_parenthesis(self):
        self._assert_printable("0", ")", True, True)

    def test_asterisk(self):
        self._assert_printable("8", "*", True, False)

    def test_alt_asterisk(self):
        self._assert_printable("8", "*", True, True)


if __name__ == "__main__":
    unittest.main()

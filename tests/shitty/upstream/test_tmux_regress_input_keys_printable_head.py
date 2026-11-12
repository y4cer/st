# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First printable cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:Space", "test_space"),
    ("regress/input-keys.sh:M-Space", "test_meta_space"),
    ("regress/input-keys.sh:!", "test_exclamation"),
    ("regress/input-keys.sh:M-!", "test_meta_exclamation"),
    ('regress/input-keys.sh:"', "test_double_quote"),
    ('regress/input-keys.sh:M-"', "test_meta_double_quote"),
    ("regress/input-keys.sh:#", "test_number_sign"),
    ("regress/input-keys.sh:M-#", "test_meta_number_sign"),
    ("regress/input-keys.sh:$", "test_dollar"),
    ("regress/input-keys.sh:M-$", "test_meta_dollar"),
    ("regress/input-keys.sh:%", "test_percent"),
    ("regress/input-keys.sh:M-%", "test_meta_percent"),
    ("regress/input-keys.sh:&", "test_ampersand"),
    ("regress/input-keys.sh:M-&", "test_meta_ampersand"),
    ("regress/input-keys.sh:'", "test_apostrophe"),
    ("regress/input-keys.sh:M-'", "test_meta_apostrophe"),
    ("regress/input-keys.sh:(", "test_left_parenthesis"),
    ("regress/input-keys.sh:M-(", "test_meta_left_parenthesis"),
    ("regress/input-keys.sh:)", "test_right_parenthesis"),
    ("regress/input-keys.sh:M-)", "test_meta_right_parenthesis"),
)


class TmuxRegressInputKeysPrintableHeadTest(unittest.TestCase):
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

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_space(self):
        self._assert_printable(" ", " ", False, False)

    def test_meta_space(self):
        self._assert_printable(" ", " ", False, True)

    def test_exclamation(self):
        self._assert_printable("1", "!", True, False)

    def test_meta_exclamation(self):
        self._assert_printable("1", "!", True, True)

    def test_double_quote(self):
        self._assert_printable("'", '"', True, False)

    def test_meta_double_quote(self):
        self._assert_printable("'", '"', True, True)

    def test_number_sign(self):
        self._assert_printable("3", "#", True, False)

    def test_meta_number_sign(self):
        self._assert_printable("3", "#", True, True)

    def test_dollar(self):
        self._assert_printable("4", "$", True, False)

    def test_meta_dollar(self):
        self._assert_printable("4", "$", True, True)

    def test_percent(self):
        self._assert_printable("5", "%", True, False)

    def test_meta_percent(self):
        self._assert_printable("5", "%", True, True)

    def test_ampersand(self):
        self._assert_printable("7", "&", True, False)

    def test_meta_ampersand(self):
        self._assert_printable("7", "&", True, True)

    def test_apostrophe(self):
        self._assert_printable("'", "'", False, False)

    def test_meta_apostrophe(self):
        self._assert_printable("'", "'", False, True)

    def test_left_parenthesis(self):
        self._assert_printable("9", "(", True, False)

    def test_meta_left_parenthesis(self):
        self._assert_printable("9", "(", True, True)

    def test_right_parenthesis(self):
        self._assert_printable("0", ")", True, False)

    def test_meta_right_parenthesis(self):
        self._assert_printable("0", ")", True, True)


if __name__ == "__main__":
    unittest.main()

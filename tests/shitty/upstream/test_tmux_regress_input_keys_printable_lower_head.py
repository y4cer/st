# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Punctuation and lowercase cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:\\", "test_backslash"),
    ("regress/input-keys.sh:M-\\", "test_meta_backslash"),
    ("regress/input-keys.sh:]", "test_right_bracket"),
    ("regress/input-keys.sh:M-]", "test_meta_right_bracket"),
    ("regress/input-keys.sh:^", "test_caret"),
    ("regress/input-keys.sh:M-^", "test_meta_caret"),
    ("regress/input-keys.sh:_", "test_underscore"),
    ("regress/input-keys.sh:M-_", "test_meta_underscore"),
    ("regress/input-keys.sh:`", "test_grave"),
    ("regress/input-keys.sh:M-`", "test_meta_grave"),
    ("regress/input-keys.sh:a", "test_lower_a"),
    ("regress/input-keys.sh:M-a", "test_meta_lower_a"),
    ("regress/input-keys.sh:b", "test_lower_b"),
    ("regress/input-keys.sh:M-b", "test_meta_lower_b"),
    ("regress/input-keys.sh:c", "test_lower_c"),
    ("regress/input-keys.sh:M-c", "test_meta_lower_c"),
    ("regress/input-keys.sh:d", "test_lower_d"),
    ("regress/input-keys.sh:M-d", "test_meta_lower_d"),
    ("regress/input-keys.sh:e", "test_lower_e"),
    ("regress/input-keys.sh:M-e", "test_meta_lower_e"),
)


class TmuxRegressInputKeysPrintableLowerHeadTest(unittest.TestCase):
    def _assert_text(self, base, output, shifted, meta):
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

    def test_backslash(self):
        self._assert_text("\\", "\\", False, False)

    def test_meta_backslash(self):
        self._assert_text("\\", "\\", False, True)

    def test_right_bracket(self):
        self._assert_text("]", "]", False, False)

    def test_meta_right_bracket(self):
        self._assert_text("]", "]", False, True)

    def test_caret(self):
        self._assert_text("6", "^", True, False)

    def test_meta_caret(self):
        self._assert_text("6", "^", True, True)

    def test_underscore(self):
        self._assert_text("-", "_", True, False)

    def test_meta_underscore(self):
        self._assert_text("-", "_", True, True)

    def test_grave(self):
        self._assert_text("`", "`", False, False)

    def test_meta_grave(self):
        self._assert_text("`", "`", False, True)

    def test_lower_a(self):
        self._assert_text("a", "a", False, False)

    def test_meta_lower_a(self):
        self._assert_text("a", "a", False, True)

    def test_lower_b(self):
        self._assert_text("b", "b", False, False)

    def test_meta_lower_b(self):
        self._assert_text("b", "b", False, True)

    def test_lower_c(self):
        self._assert_text("c", "c", False, False)

    def test_meta_lower_c(self):
        self._assert_text("c", "c", False, True)

    def test_lower_d(self):
        self._assert_text("d", "d", False, False)

    def test_meta_lower_d(self):
        self._assert_text("d", "d", False, True)

    def test_lower_e(self):
        self._assert_text("e", "e", False, False)

    def test_meta_lower_e(self):
        self._assert_text("e", "e", False, True)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Printable tail and first functional cases from tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
ALT = 4

KEY_TAB = 258
KEY_BACKSPACE = 259
KEY_F1 = 290


PORTED_CASES = (
    ("regress/input-keys.sh:z", "test_lower_z"),
    ("regress/input-keys.sh:M-z", "test_meta_lower_z"),
    ("regress/input-keys.sh:{", "test_left_brace"),
    ("regress/input-keys.sh:M-{", "test_meta_left_brace"),
    ("regress/input-keys.sh:|", "test_vertical_bar"),
    ("regress/input-keys.sh:M-|", "test_meta_vertical_bar"),
    ("regress/input-keys.sh:}", "test_right_brace"),
    ("regress/input-keys.sh:M-}", "test_meta_right_brace"),
    ("regress/input-keys.sh:~", "test_tilde"),
    ("regress/input-keys.sh:M-~", "test_meta_tilde"),
    ("regress/input-keys.sh:Tab", "test_tab"),
    ("regress/input-keys.sh:M-Tab", "test_meta_tab"),
    ("regress/input-keys.sh:BSpace", "test_backspace"),
    ("regress/input-keys.sh:M-BSpace", "test_meta_backspace"),
    ("regress/input-keys.sh:F1", "test_f1"),
    ("regress/input-keys.sh:F2", "test_f2"),
    ("regress/input-keys.sh:F3", "test_f3"),
    ("regress/input-keys.sh:F4", "test_f4"),
    ("regress/input-keys.sh:F5", "test_f5"),
    ("regress/input-keys.sh:F6", "test_f6"),
)


class TmuxRegressInputKeysPrintableTailFunctionHeadTest(unittest.TestCase):
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

    def test_lower_z(self):
        self._assert_text("z", "z", False, False)

    def test_meta_lower_z(self):
        self._assert_text("z", "z", False, True)

    def test_left_brace(self):
        self._assert_text("[", "{", True, False)

    def test_meta_left_brace(self):
        self._assert_text("[", "{", True, True)

    def test_vertical_bar(self):
        self._assert_text("\\", "|", True, False)

    def test_meta_vertical_bar(self):
        self._assert_text("\\", "|", True, True)

    def test_right_brace(self):
        self._assert_text("]", "}", True, False)

    def test_meta_right_brace(self):
        self._assert_text("]", "}", True, True)

    def test_tilde(self):
        self._assert_text("`", "~", True, False)

    def test_meta_tilde(self):
        self._assert_text("`", "~", True, True)

    def test_tab(self):
        self._assert_named(KEY_TAB, b"\t")

    def test_meta_tab(self):
        self._assert_named(KEY_TAB, b"\x1b\t", ALT)

    def test_backspace(self):
        self._assert_named(KEY_BACKSPACE, b"\x7f")

    def test_meta_backspace(self):
        self._assert_named(KEY_BACKSPACE, b"\x1b\x7f", ALT)

    def test_f1(self):
        self._assert_named(KEY_F1, b"\x1bOP")

    def test_f2(self):
        self._assert_named(KEY_F1 + 1, b"\x1bOQ")

    def test_f3(self):
        self._assert_named(KEY_F1 + 2, b"\x1bOR")

    def test_f4(self):
        self._assert_named(KEY_F1 + 3, b"\x1bOS")

    def test_f5(self):
        self._assert_named(KEY_F1 + 4, b"\x1b[15~")

    def test_f6(self):
        self._assert_named(KEY_F1 + 5, b"\x1b[17~")


if __name__ == "__main__":
    unittest.main()

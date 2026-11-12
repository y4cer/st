# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Third printable batch from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:4", "test_four"),
    ("regress/input-keys.sh:M-4", "test_meta_four"),
    ("regress/input-keys.sh:5", "test_five"),
    ("regress/input-keys.sh:M-5", "test_meta_five"),
    ("regress/input-keys.sh:6", "test_six"),
    ("regress/input-keys.sh:M-6", "test_meta_six"),
    ("regress/input-keys.sh:7", "test_seven"),
    ("regress/input-keys.sh:M-7", "test_meta_seven"),
    ("regress/input-keys.sh:8", "test_eight"),
    ("regress/input-keys.sh:M-8", "test_meta_eight"),
    ("regress/input-keys.sh:9", "test_nine"),
    ("regress/input-keys.sh:M-9", "test_meta_nine"),
    ("regress/input-keys.sh::", "test_colon"),
    ("regress/input-keys.sh:M-:", "test_meta_colon"),
    ("regress/input-keys.sh:;", "test_semicolon"),
    ("regress/input-keys.sh:M-;", "test_meta_semicolon"),
    ("regress/input-keys.sh:<", "test_less_than"),
    ("regress/input-keys.sh:M-<", "test_meta_less_than"),
    ("regress/input-keys.sh:=", "test_equals"),
    ("regress/input-keys.sh:M-=", "test_meta_equals"),
)


class TmuxRegressInputKeysPrintableMoreTest(unittest.TestCase):
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

    def test_four(self):
        self._assert_printable("4", "4", False, False)

    def test_meta_four(self):
        self._assert_printable("4", "4", False, True)

    def test_five(self):
        self._assert_printable("5", "5", False, False)

    def test_meta_five(self):
        self._assert_printable("5", "5", False, True)

    def test_six(self):
        self._assert_printable("6", "6", False, False)

    def test_meta_six(self):
        self._assert_printable("6", "6", False, True)

    def test_seven(self):
        self._assert_printable("7", "7", False, False)

    def test_meta_seven(self):
        self._assert_printable("7", "7", False, True)

    def test_eight(self):
        self._assert_printable("8", "8", False, False)

    def test_meta_eight(self):
        self._assert_printable("8", "8", False, True)

    def test_nine(self):
        self._assert_printable("9", "9", False, False)

    def test_meta_nine(self):
        self._assert_printable("9", "9", False, True)

    def test_colon(self):
        self._assert_printable(";", ":", True, False)

    def test_meta_colon(self):
        self._assert_printable(";", ":", True, True)

    def test_semicolon(self):
        self._assert_printable(";", ";", False, False)

    def test_meta_semicolon(self):
        self._assert_printable(";", ";", False, True)

    def test_less_than(self):
        self._assert_printable(",", "<", True, False)

    def test_meta_less_than(self):
        self._assert_printable(",", "<", True, True)

    def test_equals(self):
        self._assert_printable("=", "=", False, False)

    def test_meta_equals(self):
        self._assert_printable("=", "=", False, True)


if __name__ == "__main__":
    unittest.main()

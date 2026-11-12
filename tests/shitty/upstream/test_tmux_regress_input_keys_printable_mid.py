# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Second printable batch from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:*", "test_asterisk"),
    ("regress/input-keys.sh:M-*", "test_meta_asterisk"),
    ("regress/input-keys.sh:+", "test_plus"),
    ("regress/input-keys.sh:M-+", "test_meta_plus"),
    ("regress/input-keys.sh:,", "test_comma"),
    ("regress/input-keys.sh:M-,", "test_meta_comma"),
    ("regress/input-keys.sh:-", "test_minus"),
    ("regress/input-keys.sh:M--", "test_meta_minus"),
    ("regress/input-keys.sh:.", "test_period"),
    ("regress/input-keys.sh:M-.", "test_meta_period"),
    ("regress/input-keys.sh:/", "test_slash"),
    ("regress/input-keys.sh:M-/", "test_meta_slash"),
    ("regress/input-keys.sh:0", "test_zero"),
    ("regress/input-keys.sh:M-0", "test_meta_zero"),
    ("regress/input-keys.sh:1", "test_one"),
    ("regress/input-keys.sh:M-1", "test_meta_one"),
    ("regress/input-keys.sh:2", "test_two"),
    ("regress/input-keys.sh:M-2", "test_meta_two"),
    ("regress/input-keys.sh:3", "test_three"),
    ("regress/input-keys.sh:M-3", "test_meta_three"),
)


class TmuxRegressInputKeysPrintableMidTest(unittest.TestCase):
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

    def test_asterisk(self):
        self._assert_printable("8", "*", True, False)

    def test_meta_asterisk(self):
        self._assert_printable("8", "*", True, True)

    def test_plus(self):
        self._assert_printable("=", "+", True, False)

    def test_meta_plus(self):
        self._assert_printable("=", "+", True, True)

    def test_comma(self):
        self._assert_printable(",", ",", False, False)

    def test_meta_comma(self):
        self._assert_printable(",", ",", False, True)

    def test_minus(self):
        self._assert_printable("-", "-", False, False)

    def test_meta_minus(self):
        self._assert_printable("-", "-", False, True)

    def test_period(self):
        self._assert_printable(".", ".", False, False)

    def test_meta_period(self):
        self._assert_printable(".", ".", False, True)

    def test_slash(self):
        self._assert_printable("/", "/", False, False)

    def test_meta_slash(self):
        self._assert_printable("/", "/", False, True)

    def test_zero(self):
        self._assert_printable("0", "0", False, False)

    def test_meta_zero(self):
        self._assert_printable("0", "0", False, True)

    def test_one(self):
        self._assert_printable("1", "1", False, False)

    def test_meta_one(self):
        self._assert_printable("1", "1", False, True)

    def test_two(self):
        self._assert_printable("2", "2", False, False)

    def test_meta_two(self):
        self._assert_printable("2", "2", False, True)

    def test_three(self):
        self._assert_printable("3", "3", False, False)

    def test_meta_three(self):
        self._assert_printable("3", "3", False, True)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Start of uppercase printable cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:>", "test_greater_than"),
    ("regress/input-keys.sh:M->", "test_meta_greater_than"),
    ("regress/input-keys.sh:?", "test_question"),
    ("regress/input-keys.sh:M-?", "test_meta_question"),
    ("regress/input-keys.sh:@", "test_at"),
    ("regress/input-keys.sh:M-@", "test_meta_at"),
    ("regress/input-keys.sh:A", "test_upper_a"),
    ("regress/input-keys.sh:M-A", "test_meta_upper_a"),
    ("regress/input-keys.sh:B", "test_upper_b"),
    ("regress/input-keys.sh:M-B", "test_meta_upper_b"),
    ("regress/input-keys.sh:C", "test_upper_c"),
    ("regress/input-keys.sh:M-C", "test_meta_upper_c"),
    ("regress/input-keys.sh:D", "test_upper_d"),
    ("regress/input-keys.sh:M-D", "test_meta_upper_d"),
    ("regress/input-keys.sh:E", "test_upper_e"),
    ("regress/input-keys.sh:M-E", "test_meta_upper_e"),
    ("regress/input-keys.sh:F", "test_upper_f"),
    ("regress/input-keys.sh:M-F", "test_meta_upper_f"),
    ("regress/input-keys.sh:G", "test_upper_g"),
    ("regress/input-keys.sh:M-G", "test_meta_upper_g"),
)


class TmuxRegressInputKeysPrintableUpperHeadTest(unittest.TestCase):
    def _assert_shifted(self, base, output, meta):
        modifiers = SHIFT | (ALT if meta else 0)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                base,
                base,
                base,
                modifiers=modifiers,
                shifted=output,
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

    def test_greater_than(self):
        self._assert_shifted(".", ">", False)

    def test_meta_greater_than(self):
        self._assert_shifted(".", ">", True)

    def test_question(self):
        self._assert_shifted("/", "?", False)

    def test_meta_question(self):
        self._assert_shifted("/", "?", True)

    def test_at(self):
        self._assert_shifted("2", "@", False)

    def test_meta_at(self):
        self._assert_shifted("2", "@", True)

    def test_upper_a(self):
        self._assert_shifted("a", "A", False)

    def test_meta_upper_a(self):
        self._assert_shifted("a", "A", True)

    def test_upper_b(self):
        self._assert_shifted("b", "B", False)

    def test_meta_upper_b(self):
        self._assert_shifted("b", "B", True)

    def test_upper_c(self):
        self._assert_shifted("c", "C", False)

    def test_meta_upper_c(self):
        self._assert_shifted("c", "C", True)

    def test_upper_d(self):
        self._assert_shifted("d", "D", False)

    def test_meta_upper_d(self):
        self._assert_shifted("d", "D", True)

    def test_upper_e(self):
        self._assert_shifted("e", "E", False)

    def test_meta_upper_e(self):
        self._assert_shifted("e", "E", True)

    def test_upper_f(self):
        self._assert_shifted("f", "F", False)

    def test_meta_upper_f(self):
        self._assert_shifted("f", "F", True)

    def test_upper_g(self):
        self._assert_shifted("g", "G", False)

    def test_meta_upper_g(self):
        self._assert_shifted("g", "G", True)


if __name__ == "__main__":
    unittest.main()

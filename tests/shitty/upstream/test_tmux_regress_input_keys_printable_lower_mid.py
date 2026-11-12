# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Middle lowercase cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:f", "test_lower_f"),
    ("regress/input-keys.sh:M-f", "test_meta_lower_f"),
    ("regress/input-keys.sh:g", "test_lower_g"),
    ("regress/input-keys.sh:M-g", "test_meta_lower_g"),
    ("regress/input-keys.sh:h", "test_lower_h"),
    ("regress/input-keys.sh:M-h", "test_meta_lower_h"),
    ("regress/input-keys.sh:i", "test_lower_i"),
    ("regress/input-keys.sh:M-i", "test_meta_lower_i"),
    ("regress/input-keys.sh:j", "test_lower_j"),
    ("regress/input-keys.sh:M-j", "test_meta_lower_j"),
    ("regress/input-keys.sh:k", "test_lower_k"),
    ("regress/input-keys.sh:M-k", "test_meta_lower_k"),
    ("regress/input-keys.sh:l", "test_lower_l"),
    ("regress/input-keys.sh:M-l", "test_meta_lower_l"),
    ("regress/input-keys.sh:m", "test_lower_m"),
    ("regress/input-keys.sh:M-m", "test_meta_lower_m"),
    ("regress/input-keys.sh:n", "test_lower_n"),
    ("regress/input-keys.sh:M-n", "test_meta_lower_n"),
    ("regress/input-keys.sh:o", "test_lower_o"),
    ("regress/input-keys.sh:M-o", "test_meta_lower_o"),
)


class TmuxRegressInputKeysPrintableLowerMidTest(unittest.TestCase):
    def _assert_text(self, output, meta):
        modifiers = ALT if meta else 0
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(output, output, output, modifiers=modifiers)
            terminal.frontend_text_event(output, modifiers=modifiers)
            expected = (b"\x1b" if meta else b"") + output.encode()
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_lower_f(self):
        self._assert_text("f", False)

    def test_meta_lower_f(self):
        self._assert_text("f", True)

    def test_lower_g(self):
        self._assert_text("g", False)

    def test_meta_lower_g(self):
        self._assert_text("g", True)

    def test_lower_h(self):
        self._assert_text("h", False)

    def test_meta_lower_h(self):
        self._assert_text("h", True)

    def test_lower_i(self):
        self._assert_text("i", False)

    def test_meta_lower_i(self):
        self._assert_text("i", True)

    def test_lower_j(self):
        self._assert_text("j", False)

    def test_meta_lower_j(self):
        self._assert_text("j", True)

    def test_lower_k(self):
        self._assert_text("k", False)

    def test_meta_lower_k(self):
        self._assert_text("k", True)

    def test_lower_l(self):
        self._assert_text("l", False)

    def test_meta_lower_l(self):
        self._assert_text("l", True)

    def test_lower_m(self):
        self._assert_text("m", False)

    def test_meta_lower_m(self):
        self._assert_text("m", True)

    def test_lower_n(self):
        self._assert_text("n", False)

    def test_meta_lower_n(self):
        self._assert_text("n", True)

    def test_lower_o(self):
        self._assert_text("o", False)

    def test_meta_lower_o(self):
        self._assert_text("o", True)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Middle uppercase printable cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:H", "test_upper_h"),
    ("regress/input-keys.sh:M-H", "test_meta_upper_h"),
    ("regress/input-keys.sh:I", "test_upper_i"),
    ("regress/input-keys.sh:M-I", "test_meta_upper_i"),
    ("regress/input-keys.sh:J", "test_upper_j"),
    ("regress/input-keys.sh:M-J", "test_meta_upper_j"),
    ("regress/input-keys.sh:K", "test_upper_k"),
    ("regress/input-keys.sh:M-K", "test_meta_upper_k"),
    ("regress/input-keys.sh:L", "test_upper_l"),
    ("regress/input-keys.sh:M-L", "test_meta_upper_l"),
    ("regress/input-keys.sh:M", "test_upper_m"),
    ("regress/input-keys.sh:M-M", "test_meta_upper_m"),
    ("regress/input-keys.sh:N", "test_upper_n"),
    ("regress/input-keys.sh:M-N", "test_meta_upper_n"),
    ("regress/input-keys.sh:O", "test_upper_o"),
    ("regress/input-keys.sh:M-O", "test_meta_upper_o"),
    ("regress/input-keys.sh:P", "test_upper_p"),
    ("regress/input-keys.sh:M-P", "test_meta_upper_p"),
    ("regress/input-keys.sh:Q", "test_upper_q"),
    ("regress/input-keys.sh:M-Q", "test_meta_upper_q"),
)


class TmuxRegressInputKeysPrintableUpperMidTest(unittest.TestCase):
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

    def test_upper_h(self):
        self._assert_shifted("h", "H", False)

    def test_meta_upper_h(self):
        self._assert_shifted("h", "H", True)

    def test_upper_i(self):
        self._assert_shifted("i", "I", False)

    def test_meta_upper_i(self):
        self._assert_shifted("i", "I", True)

    def test_upper_j(self):
        self._assert_shifted("j", "J", False)

    def test_meta_upper_j(self):
        self._assert_shifted("j", "J", True)

    def test_upper_k(self):
        self._assert_shifted("k", "K", False)

    def test_meta_upper_k(self):
        self._assert_shifted("k", "K", True)

    def test_upper_l(self):
        self._assert_shifted("l", "L", False)

    def test_meta_upper_l(self):
        self._assert_shifted("l", "L", True)

    def test_upper_m(self):
        self._assert_shifted("m", "M", False)

    def test_meta_upper_m(self):
        self._assert_shifted("m", "M", True)

    def test_upper_n(self):
        self._assert_shifted("n", "N", False)

    def test_meta_upper_n(self):
        self._assert_shifted("n", "N", True)

    def test_upper_o(self):
        self._assert_shifted("o", "O", False)

    def test_meta_upper_o(self):
        self._assert_shifted("o", "O", True)

    def test_upper_p(self):
        self._assert_shifted("p", "P", False)

    def test_meta_upper_p(self):
        self._assert_shifted("p", "P", True)

    def test_upper_q(self):
        self._assert_shifted("q", "Q", False)

    def test_meta_upper_q(self):
        self._assert_shifted("q", "Q", True)


if __name__ == "__main__":
    unittest.main()

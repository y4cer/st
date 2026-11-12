# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First lowercase batch from current tmux tty-keys regress."""

import unittest

from harness import Shitty


ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x62:b", "test_b"),
    ("regress/tty-keys.sh:ESC-0x62:M-b", "test_alt_b"),
    ("regress/tty-keys.sh:0x63:c", "test_c"),
    ("regress/tty-keys.sh:ESC-0x63:M-c", "test_alt_c"),
    ("regress/tty-keys.sh:0x64:d", "test_d"),
    ("regress/tty-keys.sh:ESC-0x64:M-d", "test_alt_d"),
    ("regress/tty-keys.sh:0x65:e", "test_e"),
    ("regress/tty-keys.sh:ESC-0x65:M-e", "test_alt_e"),
    ("regress/tty-keys.sh:0x66:f", "test_f"),
    ("regress/tty-keys.sh:ESC-0x66:M-f", "test_alt_f"),
    ("regress/tty-keys.sh:0x67:g", "test_g"),
    ("regress/tty-keys.sh:ESC-0x67:M-g", "test_alt_g"),
    ("regress/tty-keys.sh:0x68:h", "test_h"),
    ("regress/tty-keys.sh:ESC-0x68:M-h", "test_alt_h"),
    ("regress/tty-keys.sh:0x69:i", "test_i"),
    ("regress/tty-keys.sh:ESC-0x69:M-i", "test_alt_i"),
    ("regress/tty-keys.sh:0x6A:j", "test_j"),
    ("regress/tty-keys.sh:ESC-0x6A:M-j", "test_alt_j"),
    ("regress/tty-keys.sh:0x6B:k", "test_k"),
    ("regress/tty-keys.sh:ESC-0x6B:M-k", "test_alt_k"),
    ("regress/tty-keys.sh:0x6C:l", "test_l"),
    ("regress/tty-keys.sh:ESC-0x6C:M-l", "test_alt_l"),
)


class TmuxRegressTtyKeysPrintableLowerHeadTest(unittest.TestCase):
    def _assert_lower(self, letter, meta):
        modifiers = ALT if meta else 0
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                letter, letter, letter, modifiers=modifiers
            )
            terminal.frontend_text_event(letter, modifiers=modifiers)
            expected = (b"\x1b" if meta else b"") + letter.encode()
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_b(self):
        self._assert_lower("b", False)

    def test_alt_b(self):
        self._assert_lower("b", True)

    def test_c(self):
        self._assert_lower("c", False)

    def test_alt_c(self):
        self._assert_lower("c", True)

    def test_d(self):
        self._assert_lower("d", False)

    def test_alt_d(self):
        self._assert_lower("d", True)

    def test_e(self):
        self._assert_lower("e", False)

    def test_alt_e(self):
        self._assert_lower("e", True)

    def test_f(self):
        self._assert_lower("f", False)

    def test_alt_f(self):
        self._assert_lower("f", True)

    def test_g(self):
        self._assert_lower("g", False)

    def test_alt_g(self):
        self._assert_lower("g", True)

    def test_h(self):
        self._assert_lower("h", False)

    def test_alt_h(self):
        self._assert_lower("h", True)

    def test_i(self):
        self._assert_lower("i", False)

    def test_alt_i(self):
        self._assert_lower("i", True)

    def test_j(self):
        self._assert_lower("j", False)

    def test_alt_j(self):
        self._assert_lower("j", True)

    def test_k(self):
        self._assert_lower("k", False)

    def test_alt_k(self):
        self._assert_lower("k", True)

    def test_l(self):
        self._assert_lower("l", False)

    def test_alt_l(self):
        self._assert_lower("l", True)


if __name__ == "__main__":
    unittest.main()

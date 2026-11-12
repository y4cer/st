# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First uppercase cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x41:A", "test_a"),
    ("regress/tty-keys.sh:ESC-0x41:M-A", "test_alt_a"),
    ("regress/tty-keys.sh:0x42:B", "test_b"),
    ("regress/tty-keys.sh:ESC-0x42:M-B", "test_alt_b"),
    ("regress/tty-keys.sh:0x43:C", "test_c"),
    ("regress/tty-keys.sh:ESC-0x43:M-C", "test_alt_c"),
    ("regress/tty-keys.sh:0x44:D", "test_d"),
    ("regress/tty-keys.sh:ESC-0x44:M-D", "test_alt_d"),
    ("regress/tty-keys.sh:0x45:E", "test_e"),
    ("regress/tty-keys.sh:ESC-0x45:M-E", "test_alt_e"),
    ("regress/tty-keys.sh:0x46:F", "test_f"),
    ("regress/tty-keys.sh:ESC-0x46:M-F", "test_alt_f"),
    ("regress/tty-keys.sh:0x47:G", "test_g"),
    ("regress/tty-keys.sh:ESC-0x47:M-G", "test_alt_g"),
    ("regress/tty-keys.sh:0x48:H", "test_h"),
    ("regress/tty-keys.sh:ESC-0x48:M-H", "test_alt_h"),
    ("regress/tty-keys.sh:0x49:I", "test_i"),
    ("regress/tty-keys.sh:ESC-0x49:M-I", "test_alt_i"),
    ("regress/tty-keys.sh:0x4A:J", "test_j"),
    ("regress/tty-keys.sh:ESC-0x4A:M-J", "test_alt_j"),
    ("regress/tty-keys.sh:0x4B:K", "test_k"),
    ("regress/tty-keys.sh:ESC-0x4B:M-K", "test_alt_k"),
)


class TmuxRegressTtyKeysPrintableUpperHeadTest(unittest.TestCase):
    def _assert_upper(self, letter, meta):
        modifiers = SHIFT | (ALT if meta else 0)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                letter, letter.lower(), letter.lower(),
                modifiers=modifiers, shifted=letter,
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

    def test_a(self):
        self._assert_upper("A", False)

    def test_alt_a(self):
        self._assert_upper("A", True)

    def test_b(self):
        self._assert_upper("B", False)

    def test_alt_b(self):
        self._assert_upper("B", True)

    def test_c(self):
        self._assert_upper("C", False)

    def test_alt_c(self):
        self._assert_upper("C", True)

    def test_d(self):
        self._assert_upper("D", False)

    def test_alt_d(self):
        self._assert_upper("D", True)

    def test_e(self):
        self._assert_upper("E", False)

    def test_alt_e(self):
        self._assert_upper("E", True)

    def test_f(self):
        self._assert_upper("F", False)

    def test_alt_f(self):
        self._assert_upper("F", True)

    def test_g(self):
        self._assert_upper("G", False)

    def test_alt_g(self):
        self._assert_upper("G", True)

    def test_h(self):
        self._assert_upper("H", False)

    def test_alt_h(self):
        self._assert_upper("H", True)

    def test_i(self):
        self._assert_upper("I", False)

    def test_alt_i(self):
        self._assert_upper("I", True)

    def test_j(self):
        self._assert_upper("J", False)

    def test_alt_j(self):
        self._assert_upper("J", True)

    def test_k(self):
        self._assert_upper("K", False)

    def test_alt_k(self):
        self._assert_upper("K", True)


if __name__ == "__main__":
    unittest.main()

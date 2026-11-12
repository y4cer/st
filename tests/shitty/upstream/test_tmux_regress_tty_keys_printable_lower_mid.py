# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Next lowercase batch from current tmux tty-keys regress."""

import unittest

from harness import Shitty


ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x6D:m", "test_m"),
    ("regress/tty-keys.sh:ESC-0x6D:M-m", "test_alt_m"),
    ("regress/tty-keys.sh:0x6E:n", "test_n"),
    ("regress/tty-keys.sh:ESC-0x6E:M-n", "test_alt_n"),
    ("regress/tty-keys.sh:0x6F:o", "test_o"),
    ("regress/tty-keys.sh:ESC-0x6F:M-o", "test_alt_o"),
    ("regress/tty-keys.sh:0x70:p", "test_p"),
    ("regress/tty-keys.sh:ESC-0x70:M-p", "test_alt_p"),
    ("regress/tty-keys.sh:0x71:q", "test_q"),
    ("regress/tty-keys.sh:ESC-0x71:M-q", "test_alt_q"),
    ("regress/tty-keys.sh:0x72:r", "test_r"),
    ("regress/tty-keys.sh:ESC-0x72:M-r", "test_alt_r"),
    ("regress/tty-keys.sh:0x73:s", "test_s"),
    ("regress/tty-keys.sh:ESC-0x73:M-s", "test_alt_s"),
    ("regress/tty-keys.sh:0x74:t", "test_t"),
    ("regress/tty-keys.sh:ESC-0x74:M-t", "test_alt_t"),
    ("regress/tty-keys.sh:0x75:u", "test_u"),
    ("regress/tty-keys.sh:ESC-0x75:M-u", "test_alt_u"),
    ("regress/tty-keys.sh:0x76:v", "test_v"),
    ("regress/tty-keys.sh:ESC-0x76:M-v", "test_alt_v"),
    ("regress/tty-keys.sh:0x77:w", "test_w"),
    ("regress/tty-keys.sh:ESC-0x77:M-w", "test_alt_w"),
)


class TmuxRegressTtyKeysPrintableLowerMidTest(unittest.TestCase):
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

    def test_m(self):
        self._assert_lower("m", False)

    def test_alt_m(self):
        self._assert_lower("m", True)

    def test_n(self):
        self._assert_lower("n", False)

    def test_alt_n(self):
        self._assert_lower("n", True)

    def test_o(self):
        self._assert_lower("o", False)

    def test_alt_o(self):
        self._assert_lower("o", True)

    def test_p(self):
        self._assert_lower("p", False)

    def test_alt_p(self):
        self._assert_lower("p", True)

    def test_q(self):
        self._assert_lower("q", False)

    def test_alt_q(self):
        self._assert_lower("q", True)

    def test_r(self):
        self._assert_lower("r", False)

    def test_alt_r(self):
        self._assert_lower("r", True)

    def test_s(self):
        self._assert_lower("s", False)

    def test_alt_s(self):
        self._assert_lower("s", True)

    def test_t(self):
        self._assert_lower("t", False)

    def test_alt_t(self):
        self._assert_lower("t", True)

    def test_u(self):
        self._assert_lower("u", False)

    def test_alt_u(self):
        self._assert_lower("u", True)

    def test_v(self):
        self._assert_lower("v", False)

    def test_alt_v(self):
        self._assert_lower("v", True)

    def test_w(self):
        self._assert_lower("w", False)

    def test_alt_w(self):
        self._assert_lower("w", True)


if __name__ == "__main__":
    unittest.main()

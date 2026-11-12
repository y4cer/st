# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Next uppercase cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/tty-keys.sh:0x4C:L", "test_l"),
    ("regress/tty-keys.sh:ESC-0x4C:M-L", "test_alt_l"),
    ("regress/tty-keys.sh:0x4D:M", "test_m"),
    ("regress/tty-keys.sh:ESC-0x4D:M-M", "test_alt_m"),
    ("regress/tty-keys.sh:0x4E:N", "test_n"),
    ("regress/tty-keys.sh:ESC-0x4E:M-N", "test_alt_n"),
    ("regress/tty-keys.sh:0x4F:O", "test_o"),
    ("regress/tty-keys.sh:ESC-0x4F:M-O", "test_alt_o"),
    ("regress/tty-keys.sh:0x50:P", "test_p"),
    ("regress/tty-keys.sh:ESC-0x50:M-P", "test_alt_p"),
    ("regress/tty-keys.sh:0x51:Q", "test_q"),
    ("regress/tty-keys.sh:ESC-0x51:M-Q", "test_alt_q"),
    ("regress/tty-keys.sh:0x52:R", "test_r"),
    ("regress/tty-keys.sh:ESC-0x52:M-R", "test_alt_r"),
    ("regress/tty-keys.sh:0x53:S", "test_s"),
    ("regress/tty-keys.sh:ESC-0x53:M-S", "test_alt_s"),
    ("regress/tty-keys.sh:0x54:T", "test_t"),
    ("regress/tty-keys.sh:ESC-0x54:M-T", "test_alt_t"),
    ("regress/tty-keys.sh:0x55:U", "test_u"),
    ("regress/tty-keys.sh:ESC-0x55:M-U", "test_alt_u"),
    ("regress/tty-keys.sh:0x56:V", "test_v"),
    ("regress/tty-keys.sh:ESC-0x56:M-V", "test_alt_v"),
)


class TmuxRegressTtyKeysPrintableUpperMidTest(unittest.TestCase):
    def _assert_upper(self, letter, meta):
        modifiers = SHIFT | (ALT if meta else 0)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                letter,
                letter.lower(),
                letter.lower(),
                modifiers=modifiers,
                shifted=letter,
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

    def test_l(self):
        self._assert_upper("L", False)

    def test_alt_l(self):
        self._assert_upper("L", True)

    def test_m(self):
        self._assert_upper("M", False)

    def test_alt_m(self):
        self._assert_upper("M", True)

    def test_n(self):
        self._assert_upper("N", False)

    def test_alt_n(self):
        self._assert_upper("N", True)

    def test_o(self):
        self._assert_upper("O", False)

    def test_alt_o(self):
        self._assert_upper("O", True)

    def test_p(self):
        self._assert_upper("P", False)

    def test_alt_p(self):
        self._assert_upper("P", True)

    def test_q(self):
        self._assert_upper("Q", False)

    def test_alt_q(self):
        self._assert_upper("Q", True)

    def test_r(self):
        self._assert_upper("R", False)

    def test_alt_r(self):
        self._assert_upper("R", True)

    def test_s(self):
        self._assert_upper("S", False)

    def test_alt_s(self):
        self._assert_upper("S", True)

    def test_t(self):
        self._assert_upper("T", False)

    def test_alt_t(self):
        self._assert_upper("T", True)

    def test_u(self):
        self._assert_upper("U", False)

    def test_alt_u(self):
        self._assert_upper("U", True)

    def test_v(self):
        self._assert_upper("V", False)

    def test_alt_v(self):
        self._assert_upper("V", True)


if __name__ == "__main__":
    unittest.main()

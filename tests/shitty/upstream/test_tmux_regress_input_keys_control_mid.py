# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Middle legacy control-key cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
CONTROL = 2
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:C-k", "test_control_k"),
    ("regress/input-keys.sh:M-C-k", "test_meta_control_k"),
    ("regress/input-keys.sh:C-l", "test_control_l"),
    ("regress/input-keys.sh:M-C-l", "test_meta_control_l"),
    ("regress/input-keys.sh:C-m", "test_control_m"),
    ("regress/input-keys.sh:M-C-m", "test_meta_control_m"),
    ("regress/input-keys.sh:C-n", "test_control_n"),
    ("regress/input-keys.sh:M-C-n", "test_meta_control_n"),
    ("regress/input-keys.sh:C-o", "test_control_o"),
    ("regress/input-keys.sh:M-C-o", "test_meta_control_o"),
    ("regress/input-keys.sh:C-p", "test_control_p"),
    ("regress/input-keys.sh:M-C-p", "test_meta_control_p"),
    ("regress/input-keys.sh:C-q", "test_control_q"),
    ("regress/input-keys.sh:M-C-q", "test_meta_control_q"),
    ("regress/input-keys.sh:C-r", "test_control_r"),
    ("regress/input-keys.sh:M-C-r", "test_meta_control_r"),
    ("regress/input-keys.sh:C-s", "test_control_s"),
    ("regress/input-keys.sh:M-C-s", "test_meta_control_s"),
    ("regress/input-keys.sh:C-t", "test_control_t"),
    ("regress/input-keys.sh:M-C-t", "test_meta_control_t"),
    ("regress/input-keys.sh:C-u", "test_control_u"),
    ("regress/input-keys.sh:M-C-u", "test_meta_control_u"),
)


class TmuxRegressInputKeysControlMidTest(unittest.TestCase):
    def _assert_key(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_k(self):
        self._assert_key("k", CONTROL, b"\x0b")

    def test_meta_control_k(self):
        self._assert_key("k", ALT | CONTROL, b"\x1b\x0b")

    def test_control_l(self):
        self._assert_key("l", CONTROL, b"\x0c")

    def test_meta_control_l(self):
        self._assert_key("l", ALT | CONTROL, b"\x1b\x0c")

    def test_control_m(self):
        self._assert_key("m", CONTROL, b"\x0d")

    def test_meta_control_m(self):
        self._assert_key("m", ALT | CONTROL, b"\x1b\x0d")

    def test_control_n(self):
        self._assert_key("n", CONTROL, b"\x0e")

    def test_meta_control_n(self):
        self._assert_key("n", ALT | CONTROL, b"\x1b\x0e")

    def test_control_o(self):
        self._assert_key("o", CONTROL, b"\x0f")

    def test_meta_control_o(self):
        self._assert_key("o", ALT | CONTROL, b"\x1b\x0f")

    def test_control_p(self):
        self._assert_key("p", CONTROL, b"\x10")

    def test_meta_control_p(self):
        self._assert_key("p", ALT | CONTROL, b"\x1b\x10")

    def test_control_q(self):
        self._assert_key("q", CONTROL, b"\x11")

    def test_meta_control_q(self):
        self._assert_key("q", ALT | CONTROL, b"\x1b\x11")

    def test_control_r(self):
        self._assert_key("r", CONTROL, b"\x12")

    def test_meta_control_r(self):
        self._assert_key("r", ALT | CONTROL, b"\x1b\x12")

    def test_control_s(self):
        self._assert_key("s", CONTROL, b"\x13")

    def test_meta_control_s(self):
        self._assert_key("s", ALT | CONTROL, b"\x1b\x13")

    def test_control_t(self):
        self._assert_key("t", CONTROL, b"\x14")

    def test_meta_control_t(self):
        self._assert_key("t", ALT | CONTROL, b"\x1b\x14")

    def test_control_u(self):
        self._assert_key("u", CONTROL, b"\x15")

    def test_meta_control_u(self):
        self._assert_key("u", ALT | CONTROL, b"\x1b\x15")


if __name__ == "__main__":
    unittest.main()

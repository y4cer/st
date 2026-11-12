# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First legacy control-key cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
CONTROL = 2
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:C-Space", "test_control_space"),
    ("regress/input-keys.sh:C-a", "test_control_a"),
    ("regress/input-keys.sh:M-C-a", "test_meta_control_a"),
    ("regress/input-keys.sh:C-b", "test_control_b"),
    ("regress/input-keys.sh:M-C-b", "test_meta_control_b"),
    ("regress/input-keys.sh:C-c", "test_control_c"),
    ("regress/input-keys.sh:M-C-c", "test_meta_control_c"),
    ("regress/input-keys.sh:C-d", "test_control_d"),
    ("regress/input-keys.sh:M-C-d", "test_meta_control_d"),
    ("regress/input-keys.sh:C-e", "test_control_e"),
    ("regress/input-keys.sh:M-C-e", "test_meta_control_e"),
    ("regress/input-keys.sh:C-f", "test_control_f"),
    ("regress/input-keys.sh:M-C-f", "test_meta_control_f"),
    ("regress/input-keys.sh:C-g", "test_control_g"),
    ("regress/input-keys.sh:M-C-g", "test_meta_control_g"),
    ("regress/input-keys.sh:C-h", "test_control_h"),
    ("regress/input-keys.sh:M-C-h", "test_meta_control_h"),
    ("regress/input-keys.sh:C-i", "test_control_i"),
    ("regress/input-keys.sh:M-C-i", "test_meta_control_i"),
    ("regress/input-keys.sh:C-j", "test_control_j"),
    ("regress/input-keys.sh:M-C-j", "test_meta_control_j"),
)


class TmuxRegressInputKeysControlTest(unittest.TestCase):
    def _assert_key(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_space(self):
        self._assert_key(" ", CONTROL, b"\x00")

    def test_control_a(self):
        self._assert_key("a", CONTROL, b"\x01")

    def test_meta_control_a(self):
        self._assert_key("a", ALT | CONTROL, b"\x1b\x01")

    def test_control_b(self):
        self._assert_key("b", CONTROL, b"\x02")

    def test_meta_control_b(self):
        self._assert_key("b", ALT | CONTROL, b"\x1b\x02")

    def test_control_c(self):
        self._assert_key("c", CONTROL, b"\x03")

    def test_meta_control_c(self):
        self._assert_key("c", ALT | CONTROL, b"\x1b\x03")

    def test_control_d(self):
        self._assert_key("d", CONTROL, b"\x04")

    def test_meta_control_d(self):
        self._assert_key("d", ALT | CONTROL, b"\x1b\x04")

    def test_control_e(self):
        self._assert_key("e", CONTROL, b"\x05")

    def test_meta_control_e(self):
        self._assert_key("e", ALT | CONTROL, b"\x1b\x05")

    def test_control_f(self):
        self._assert_key("f", CONTROL, b"\x06")

    def test_meta_control_f(self):
        self._assert_key("f", ALT | CONTROL, b"\x1b\x06")

    def test_control_g(self):
        self._assert_key("g", CONTROL, b"\x07")

    def test_meta_control_g(self):
        self._assert_key("g", ALT | CONTROL, b"\x1b\x07")

    def test_control_h(self):
        self._assert_key("h", CONTROL, b"\x08")

    def test_meta_control_h(self):
        self._assert_key("h", ALT | CONTROL, b"\x1b\x08")

    def test_control_i(self):
        self._assert_key("i", CONTROL, b"\x09")

    def test_meta_control_i(self):
        self._assert_key("i", ALT | CONTROL, b"\x1b\x09")

    def test_control_j(self):
        self._assert_key("j", CONTROL, b"\x0a")

    def test_meta_control_j(self):
        self._assert_key("j", ALT | CONTROL, b"\x1b\x0a")


if __name__ == "__main__":
    unittest.main()

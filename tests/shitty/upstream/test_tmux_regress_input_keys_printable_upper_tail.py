# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Tail uppercase printable cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


SHIFT = 1
ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:R", "test_upper_r"),
    ("regress/input-keys.sh:M-R", "test_meta_upper_r"),
    ("regress/input-keys.sh:S", "test_upper_s"),
    ("regress/input-keys.sh:M-S", "test_meta_upper_s"),
    ("regress/input-keys.sh:T", "test_upper_t"),
    ("regress/input-keys.sh:M-T", "test_meta_upper_t"),
    ("regress/input-keys.sh:U", "test_upper_u"),
    ("regress/input-keys.sh:M-U", "test_meta_upper_u"),
    ("regress/input-keys.sh:V", "test_upper_v"),
    ("regress/input-keys.sh:M-V", "test_meta_upper_v"),
    ("regress/input-keys.sh:W", "test_upper_w"),
    ("regress/input-keys.sh:M-W", "test_meta_upper_w"),
    ("regress/input-keys.sh:X", "test_upper_x"),
    ("regress/input-keys.sh:M-X", "test_meta_upper_x"),
    ("regress/input-keys.sh:Y", "test_upper_y"),
    ("regress/input-keys.sh:M-Y", "test_meta_upper_y"),
    ("regress/input-keys.sh:Z", "test_upper_z"),
    ("regress/input-keys.sh:M-Z", "test_meta_upper_z"),
    ("regress/input-keys.sh:[", "test_left_bracket"),
    ("regress/input-keys.sh:M-[", "test_meta_left_bracket"),
)


class TmuxRegressInputKeysPrintableUpperTailTest(unittest.TestCase):
    def _assert_text(self, base, output, shifted, meta):
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

    def test_upper_r(self):
        self._assert_text("r", "R", True, False)

    def test_meta_upper_r(self):
        self._assert_text("r", "R", True, True)

    def test_upper_s(self):
        self._assert_text("s", "S", True, False)

    def test_meta_upper_s(self):
        self._assert_text("s", "S", True, True)

    def test_upper_t(self):
        self._assert_text("t", "T", True, False)

    def test_meta_upper_t(self):
        self._assert_text("t", "T", True, True)

    def test_upper_u(self):
        self._assert_text("u", "U", True, False)

    def test_meta_upper_u(self):
        self._assert_text("u", "U", True, True)

    def test_upper_v(self):
        self._assert_text("v", "V", True, False)

    def test_meta_upper_v(self):
        self._assert_text("v", "V", True, True)

    def test_upper_w(self):
        self._assert_text("w", "W", True, False)

    def test_meta_upper_w(self):
        self._assert_text("w", "W", True, True)

    def test_upper_x(self):
        self._assert_text("x", "X", True, False)

    def test_meta_upper_x(self):
        self._assert_text("x", "X", True, True)

    def test_upper_y(self):
        self._assert_text("y", "Y", True, False)

    def test_meta_upper_y(self):
        self._assert_text("y", "Y", True, True)

    def test_upper_z(self):
        self._assert_text("z", "Z", True, False)

    def test_meta_upper_z(self):
        self._assert_text("z", "Z", True, True)

    def test_left_bracket(self):
        self._assert_text("[", "[", False, False)

    def test_meta_left_bracket(self):
        self._assert_text("[", "[", False, True)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Further lowercase cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


ALT = 4


PORTED_CASES = (
    ("regress/input-keys.sh:p", "test_lower_p"),
    ("regress/input-keys.sh:M-p", "test_meta_lower_p"),
    ("regress/input-keys.sh:q", "test_lower_q"),
    ("regress/input-keys.sh:M-q", "test_meta_lower_q"),
    ("regress/input-keys.sh:r", "test_lower_r"),
    ("regress/input-keys.sh:M-r", "test_meta_lower_r"),
    ("regress/input-keys.sh:s", "test_lower_s"),
    ("regress/input-keys.sh:M-s", "test_meta_lower_s"),
    ("regress/input-keys.sh:t", "test_lower_t"),
    ("regress/input-keys.sh:M-t", "test_meta_lower_t"),
    ("regress/input-keys.sh:u", "test_lower_u"),
    ("regress/input-keys.sh:M-u", "test_meta_lower_u"),
    ("regress/input-keys.sh:v", "test_lower_v"),
    ("regress/input-keys.sh:M-v", "test_meta_lower_v"),
    ("regress/input-keys.sh:w", "test_lower_w"),
    ("regress/input-keys.sh:M-w", "test_meta_lower_w"),
    ("regress/input-keys.sh:x", "test_lower_x"),
    ("regress/input-keys.sh:M-x", "test_meta_lower_x"),
    ("regress/input-keys.sh:y", "test_lower_y"),
    ("regress/input-keys.sh:M-y", "test_meta_lower_y"),
)


class TmuxRegressInputKeysPrintableLowerMoreTest(unittest.TestCase):
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

    def test_lower_p(self):
        self._assert_text("p", False)

    def test_meta_lower_p(self):
        self._assert_text("p", True)

    def test_lower_q(self):
        self._assert_text("q", False)

    def test_meta_lower_q(self):
        self._assert_text("q", True)

    def test_lower_r(self):
        self._assert_text("r", False)

    def test_meta_lower_r(self):
        self._assert_text("r", True)

    def test_lower_s(self):
        self._assert_text("s", False)

    def test_meta_lower_s(self):
        self._assert_text("s", True)

    def test_lower_t(self):
        self._assert_text("t", False)

    def test_meta_lower_t(self):
        self._assert_text("t", True)

    def test_lower_u(self):
        self._assert_text("u", False)

    def test_meta_lower_u(self):
        self._assert_text("u", True)

    def test_lower_v(self):
        self._assert_text("v", False)

    def test_meta_lower_v(self):
        self._assert_text("v", True)

    def test_lower_w(self):
        self._assert_text("w", False)

    def test_meta_lower_w(self):
        self._assert_text("w", True)

    def test_lower_x(self):
        self._assert_text("x", False)

    def test_meta_lower_x(self):
        self._assert_text("x", True)

    def test_lower_y(self):
        self._assert_text("y", False)

    def test_meta_lower_y(self):
        self._assert_text("y", True)


if __name__ == "__main__":
    unittest.main()

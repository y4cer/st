# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Final control and escape cases from current tmux input-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4
KEY_ESCAPE = 256


PORTED_CASES = (
    ("regress/input-keys.sh:C-v", "test_control_v"),
    ("regress/input-keys.sh:M-C-v", "test_meta_control_v"),
    ("regress/input-keys.sh:C-w", "test_control_w"),
    ("regress/input-keys.sh:M-C-w", "test_meta_control_w"),
    ("regress/input-keys.sh:C-x", "test_control_x"),
    ("regress/input-keys.sh:M-C-x", "test_meta_control_x"),
    ("regress/input-keys.sh:C-y", "test_control_y"),
    ("regress/input-keys.sh:M-C-y", "test_meta_control_y"),
    ("regress/input-keys.sh:C-z", "test_control_z"),
    ("regress/input-keys.sh:M-C-z", "test_meta_control_z"),
    ("regress/input-keys.sh:Escape", "test_escape"),
    ("regress/input-keys.sh:M-Escape", "test_meta_escape"),
    ("regress/input-keys.sh:C-backslash", "test_control_backslash"),
    ("regress/input-keys.sh:M-C-backslash", "test_meta_control_backslash"),
    (
        "regress/input-keys.sh:C-right-bracket",
        "test_control_right_bracket",
    ),
    (
        "regress/input-keys.sh:M-C-right-bracket",
        "test_meta_control_right_bracket",
    ),
    ("regress/input-keys.sh:C-caret", "test_control_caret"),
    ("regress/input-keys.sh:M-C-caret", "test_meta_control_caret"),
    ("regress/input-keys.sh:C-underscore", "test_control_underscore"),
    ("regress/input-keys.sh:M-C-underscore", "test_meta_control_underscore"),
)


class TmuxRegressInputKeysControlTailTest(unittest.TestCase):
    def _assert_letter(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_escape(self, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                KEY_ESCAPE, PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_layout_control(
        self, key, shifted, modifiers, expected
    ):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                key,
                key,
                key,
                modifiers=modifiers,
                shifted=shifted,
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_v(self):
        self._assert_letter("v", CONTROL, b"\x16")

    def test_meta_control_v(self):
        self._assert_letter("v", ALT | CONTROL, b"\x1b\x16")

    def test_control_w(self):
        self._assert_letter("w", CONTROL, b"\x17")

    def test_meta_control_w(self):
        self._assert_letter("w", ALT | CONTROL, b"\x1b\x17")

    def test_control_x(self):
        self._assert_letter("x", CONTROL, b"\x18")

    def test_meta_control_x(self):
        self._assert_letter("x", ALT | CONTROL, b"\x1b\x18")

    def test_control_y(self):
        self._assert_letter("y", CONTROL, b"\x19")

    def test_meta_control_y(self):
        self._assert_letter("y", ALT | CONTROL, b"\x1b\x19")

    def test_control_z(self):
        self._assert_letter("z", CONTROL, b"\x1a")

    def test_meta_control_z(self):
        self._assert_letter("z", ALT | CONTROL, b"\x1b\x1a")

    def test_escape(self):
        self._assert_escape(0, b"\x1b")

    def test_meta_escape(self):
        self._assert_escape(ALT, b"\x1b\x1b")

    def test_control_backslash(self):
        self._assert_layout_control("\\", 0, CONTROL, b"\x1c")

    def test_meta_control_backslash(self):
        self._assert_layout_control(
            "\\", 0, ALT | CONTROL, b"\x1b\x1c"
        )

    def test_control_right_bracket(self):
        self._assert_layout_control("]", 0, CONTROL, b"\x1d")

    def test_meta_control_right_bracket(self):
        self._assert_layout_control(
            "]", 0, ALT | CONTROL, b"\x1b\x1d"
        )

    def test_control_caret(self):
        self._assert_layout_control(
            "6", "^", SHIFT | CONTROL, b"\x1e"
        )

    def test_meta_control_caret(self):
        self._assert_layout_control(
            "6", "^", SHIFT | ALT | CONTROL, b"\x1b\x1e"
        )

    def test_control_underscore(self):
        self._assert_layout_control(
            "-", "_", SHIFT | CONTROL, b"\x1f"
        )

    def test_meta_control_underscore(self):
        self._assert_layout_control(
            "-", "_", SHIFT | ALT | CONTROL, b"\x1b\x1f"
        )


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Final C0 control cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_ESCAPE = 256


PORTED_CASES = (
    ("regress/tty-keys.sh:0x15:C-u", "test_control_u"),
    ("regress/tty-keys.sh:ESC-0x15:C-M-u", "test_control_alt_u"),
    ("regress/tty-keys.sh:0x16:C-v", "test_control_v"),
    ("regress/tty-keys.sh:ESC-0x16:C-M-v", "test_control_alt_v"),
    ("regress/tty-keys.sh:0x17:C-w", "test_control_w"),
    ("regress/tty-keys.sh:ESC-0x17:C-M-w", "test_control_alt_w"),
    ("regress/tty-keys.sh:0x18:C-x", "test_control_x"),
    ("regress/tty-keys.sh:ESC-0x18:C-M-x", "test_control_alt_x"),
    ("regress/tty-keys.sh:0x19:C-y", "test_control_y"),
    ("regress/tty-keys.sh:ESC-0x19:C-M-y", "test_control_alt_y"),
    ("regress/tty-keys.sh:0x1A:C-z", "test_control_z"),
    ("regress/tty-keys.sh:ESC-0x1A:C-M-z", "test_control_alt_z"),
    ("regress/tty-keys.sh:0x1B:Escape", "test_escape"),
    ("regress/tty-keys.sh:ESC-0x1B:M-Escape", "test_alt_escape"),
    ("regress/tty-keys.sh:0x1C:C-backslash", "test_control_backslash"),
    (
        "regress/tty-keys.sh:ESC-0x1C:C-M-backslash",
        "test_control_alt_backslash",
    ),
    ("regress/tty-keys.sh:0x1D:C-right-bracket", "test_control_bracket"),
    (
        "regress/tty-keys.sh:ESC-0x1D:C-M-right-bracket",
        "test_control_alt_bracket",
    ),
    ("regress/tty-keys.sh:0x1E:C-caret", "test_control_caret"),
    ("regress/tty-keys.sh:ESC-0x1E:C-M-caret", "test_control_alt_caret"),
    ("regress/tty-keys.sh:0x1F:C-underscore", "test_control_underscore"),
    (
        "regress/tty-keys.sh:ESC-0x1F:C-M-underscore",
        "test_control_alt_underscore",
    ),
)


class TmuxRegressTtyKeysControlTailTest(unittest.TestCase):
    def _assert_letter(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                ord(key.upper()), PRESS, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def _assert_layout(self, key, shifted, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                key, key, key, modifiers=modifiers, shifted=shifted
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_u(self):
        self._assert_letter("u", CONTROL, b"\x15")

    def test_control_alt_u(self):
        self._assert_letter("u", CONTROL | ALT, b"\x1b\x15")

    def test_control_v(self):
        self._assert_letter("v", CONTROL, b"\x16")

    def test_control_alt_v(self):
        self._assert_letter("v", CONTROL | ALT, b"\x1b\x16")

    def test_control_w(self):
        self._assert_letter("w", CONTROL, b"\x17")

    def test_control_alt_w(self):
        self._assert_letter("w", CONTROL | ALT, b"\x1b\x17")

    def test_control_x(self):
        self._assert_letter("x", CONTROL, b"\x18")

    def test_control_alt_x(self):
        self._assert_letter("x", CONTROL | ALT, b"\x1b\x18")

    def test_control_y(self):
        self._assert_letter("y", CONTROL, b"\x19")

    def test_control_alt_y(self):
        self._assert_letter("y", CONTROL | ALT, b"\x1b\x19")

    def test_control_z(self):
        self._assert_letter("z", CONTROL, b"\x1a")

    def test_control_alt_z(self):
        self._assert_letter("z", CONTROL | ALT, b"\x1b\x1a")

    def test_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b")

    def test_alt_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_ESCAPE, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b\x1b")

    def test_control_backslash(self):
        self._assert_layout("\\", 0, CONTROL, b"\x1c")

    def test_control_alt_backslash(self):
        self._assert_layout("\\", 0, CONTROL | ALT, b"\x1b\x1c")

    def test_control_bracket(self):
        self._assert_layout("]", 0, CONTROL, b"\x1d")

    def test_control_alt_bracket(self):
        self._assert_layout("]", 0, CONTROL | ALT, b"\x1b\x1d")

    def test_control_caret(self):
        self._assert_layout("6", "^", CONTROL | SHIFT, b"\x1e")

    def test_control_alt_caret(self):
        self._assert_layout(
            "6", "^", CONTROL | SHIFT | ALT, b"\x1b\x1e"
        )

    def test_control_underscore(self):
        self._assert_layout("-", "_", CONTROL | SHIFT, b"\x1f")

    def test_control_alt_underscore(self):
        self._assert_layout(
            "-", "_", CONTROL | SHIFT | ALT, b"\x1b\x1f"
        )


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Printable tail and keypad head from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
ALT = 4

KEY_BACKSPACE = 259
KEY_KP_MULTIPLY = 332
KEY_KP_ENTER = 335


PORTED_CASES = (
    ("regress/tty-keys.sh:0x78:x", "test_x"),
    ("regress/tty-keys.sh:ESC-0x78:M-x", "test_alt_x"),
    ("regress/tty-keys.sh:0x79:y", "test_y"),
    ("regress/tty-keys.sh:ESC-0x79:M-y", "test_alt_y"),
    ("regress/tty-keys.sh:0x7A:z", "test_z"),
    ("regress/tty-keys.sh:ESC-0x7A:M-z", "test_alt_z"),
    ("regress/tty-keys.sh:0x7B:{", "test_left_brace"),
    ("regress/tty-keys.sh:ESC-0x7B:M-{", "test_alt_left_brace"),
    ("regress/tty-keys.sh:0x7C:pipe", "test_pipe"),
    ("regress/tty-keys.sh:ESC-0x7C:M-pipe", "test_alt_pipe"),
    ("regress/tty-keys.sh:0x7D:}", "test_right_brace"),
    ("regress/tty-keys.sh:ESC-0x7D:M-}", "test_alt_right_brace"),
    ("regress/tty-keys.sh:0x7E:~", "test_tilde"),
    ("regress/tty-keys.sh:ESC-0x7E:M-~", "test_alt_tilde"),
    ("regress/tty-keys.sh:0x7F:BSpace", "test_backspace"),
    ("regress/tty-keys.sh:ESC-0x7F:M-BSpace", "test_alt_backspace"),
    ("regress/tty-keys.sh:SS3-M:KPEnter", "test_keypad_enter"),
    ("regress/tty-keys.sh:ESC-SS3-M:M-KPEnter", "test_alt_keypad_enter"),
    ("regress/tty-keys.sh:SS3-j:KP*", "test_keypad_multiply"),
    ("regress/tty-keys.sh:ESC-SS3-j:M-KP*", "test_alt_keypad_multiply"),
)


class TmuxRegressTtyKeysPrintableTailKeypadTest(unittest.TestCase):
    def _assert_printable(self, base, output, shifted, meta):
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

    def _assert_named(self, key, modifiers, expected, application=False):
        with Shitty(columns=8, rows=2) as terminal:
            if application:
                terminal.write(b"\x1b=")
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_x(self):
        self._assert_printable("x", "x", False, False)

    def test_alt_x(self):
        self._assert_printable("x", "x", False, True)

    def test_y(self):
        self._assert_printable("y", "y", False, False)

    def test_alt_y(self):
        self._assert_printable("y", "y", False, True)

    def test_z(self):
        self._assert_printable("z", "z", False, False)

    def test_alt_z(self):
        self._assert_printable("z", "z", False, True)

    def test_left_brace(self):
        self._assert_printable("[", "{", True, False)

    def test_alt_left_brace(self):
        self._assert_printable("[", "{", True, True)

    def test_pipe(self):
        self._assert_printable("\\", "|", True, False)

    def test_alt_pipe(self):
        self._assert_printable("\\", "|", True, True)

    def test_right_brace(self):
        self._assert_printable("]", "}", True, False)

    def test_alt_right_brace(self):
        self._assert_printable("]", "}", True, True)

    def test_tilde(self):
        self._assert_printable("`", "~", True, False)

    def test_alt_tilde(self):
        self._assert_printable("`", "~", True, True)

    def test_backspace(self):
        self._assert_named(KEY_BACKSPACE, 0, b"\x7f")

    def test_alt_backspace(self):
        self._assert_named(KEY_BACKSPACE, ALT, b"\x1b\x7f")

    def test_keypad_enter(self):
        self._assert_named(KEY_KP_ENTER, 0, b"\x1bOM", application=True)

    def test_alt_keypad_enter(self):
        self._assert_named(KEY_KP_ENTER, ALT, b"\x1bO3M", application=True)

    def test_keypad_multiply(self):
        self._assert_named(KEY_KP_MULTIPLY, 0, b"\x1bOj", application=True)

    def test_alt_keypad_multiply(self):
        self._assert_named(KEY_KP_MULTIPLY, ALT, b"\x1bO3j", application=True)


if __name__ == "__main__":
    unittest.main()

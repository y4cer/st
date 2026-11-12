# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Cursor, Home/End and rxvt cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264
KEY_UP = 265
KEY_HOME = 268
KEY_END = 269


PORTED_CASES = (
    ("regress/tty-keys.sh:CSI-C:Right", "test_normal_right"),
    ("regress/tty-keys.sh:ESC-CSI-C:M-Right", "test_alt_normal_right"),
    ("regress/tty-keys.sh:CSI-D:Left", "test_normal_left"),
    ("regress/tty-keys.sh:ESC-CSI-D:M-Left", "test_alt_normal_left"),
    ("regress/tty-keys.sh:SS3-H:Home", "test_application_home"),
    ("regress/tty-keys.sh:ESC-SS3-H:M-Home", "test_alt_application_home"),
    ("regress/tty-keys.sh:SS3-F:End", "test_application_end"),
    ("regress/tty-keys.sh:ESC-SS3-F:M-End", "test_alt_application_end"),
    ("regress/tty-keys.sh:CSI-H:Home", "test_normal_home"),
    ("regress/tty-keys.sh:ESC-CSI-H:M-Home", "test_alt_normal_home"),
    ("regress/tty-keys.sh:CSI-F:End", "test_normal_end"),
    ("regress/tty-keys.sh:ESC-CSI-F:M-End", "test_alt_normal_end"),
    ("regress/tty-keys.sh:rxvt-SS3-a:C-Up", "test_rxvt_control_up"),
    ("regress/tty-keys.sh:rxvt-SS3-b:C-Down", "test_rxvt_control_down"),
    ("regress/tty-keys.sh:rxvt-SS3-c:C-Right", "test_rxvt_control_right"),
    ("regress/tty-keys.sh:rxvt-SS3-d:C-Left", "test_rxvt_control_left"),
    ("regress/tty-keys.sh:rxvt-CSI-a:S-Up", "test_rxvt_shift_up"),
    ("regress/tty-keys.sh:rxvt-CSI-b:S-Down", "test_rxvt_shift_down"),
    ("regress/tty-keys.sh:rxvt-CSI-c:S-Right", "test_rxvt_shift_right"),
    ("regress/tty-keys.sh:rxvt-CSI-d:S-Left", "test_rxvt_shift_left"),
)


class TmuxRegressTtyKeysCursorHomeRxvtTest(unittest.TestCase):
    def _assert_cursor(self, key, final, modifiers=0, application=False):
        with Shitty(columns=8, rows=2) as terminal:
            if application:
                terminal.write(b"\x1b[?1h")
            terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
            if modifiers:
                code = (
                    1
                    + bool(modifiers & SHIFT)
                    + 2 * bool(modifiers & ALT)
                    + 4 * bool(modifiers & CONTROL)
                )
                expected = f"\x1b[1;{code}".encode() + final
            elif application:
                expected = b"\x1bO" + final
            else:
                expected = b"\x1b[" + final
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_normal_right(self):
        self._assert_cursor(KEY_RIGHT, b"C")

    def test_alt_normal_right(self):
        self._assert_cursor(KEY_RIGHT, b"C", ALT)

    def test_normal_left(self):
        self._assert_cursor(KEY_LEFT, b"D")

    def test_alt_normal_left(self):
        self._assert_cursor(KEY_LEFT, b"D", ALT)

    def test_application_home(self):
        self._assert_cursor(KEY_HOME, b"H", application=True)

    def test_alt_application_home(self):
        self._assert_cursor(KEY_HOME, b"H", ALT, True)

    def test_application_end(self):
        self._assert_cursor(KEY_END, b"F", application=True)

    def test_alt_application_end(self):
        self._assert_cursor(KEY_END, b"F", ALT, True)

    def test_normal_home(self):
        self._assert_cursor(KEY_HOME, b"H")

    def test_alt_normal_home(self):
        self._assert_cursor(KEY_HOME, b"H", ALT)

    def test_normal_end(self):
        self._assert_cursor(KEY_END, b"F")

    def test_alt_normal_end(self):
        self._assert_cursor(KEY_END, b"F", ALT)

    def test_rxvt_control_up(self):
        self._assert_cursor(KEY_UP, b"A", CONTROL)

    def test_rxvt_control_down(self):
        self._assert_cursor(KEY_DOWN, b"B", CONTROL)

    def test_rxvt_control_right(self):
        self._assert_cursor(KEY_RIGHT, b"C", CONTROL)

    def test_rxvt_control_left(self):
        self._assert_cursor(KEY_LEFT, b"D", CONTROL)

    def test_rxvt_shift_up(self):
        self._assert_cursor(KEY_UP, b"A", SHIFT)

    def test_rxvt_shift_down(self):
        self._assert_cursor(KEY_DOWN, b"B", SHIFT)

    def test_rxvt_shift_right(self):
        self._assert_cursor(KEY_RIGHT, b"C", SHIFT)

    def test_rxvt_shift_left(self):
        self._assert_cursor(KEY_LEFT, b"D", SHIFT)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Rxvt function-key decoder cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1

KEY_F1 = 290


PORTED_CASES = (
    ("regress/tty-keys.sh:rxvt-CSI-11:F1", "test_f1"),
    ("regress/tty-keys.sh:rxvt-CSI-12:F2", "test_f2"),
    ("regress/tty-keys.sh:rxvt-CSI-13:F3", "test_f3"),
    ("regress/tty-keys.sh:rxvt-CSI-14:F4", "test_f4"),
    ("regress/tty-keys.sh:rxvt-CSI-15:F5", "test_f5"),
    ("regress/tty-keys.sh:rxvt-CSI-17:F6", "test_f6"),
    ("regress/tty-keys.sh:rxvt-CSI-18:F7", "test_f7"),
    ("regress/tty-keys.sh:rxvt-CSI-19:F8", "test_f8"),
    ("regress/tty-keys.sh:rxvt-CSI-20:F9", "test_f9"),
    ("regress/tty-keys.sh:rxvt-CSI-21:F10", "test_f10"),
    ("regress/tty-keys.sh:rxvt-CSI-23:F11", "test_f11"),
    ("regress/tty-keys.sh:rxvt-CSI-24:F12", "test_f12"),
    ("regress/tty-keys.sh:rxvt-CSI-25:S-F3", "test_shift_f3"),
    ("regress/tty-keys.sh:rxvt-CSI-26:S-F4", "test_shift_f4"),
    ("regress/tty-keys.sh:rxvt-CSI-28:S-F5", "test_shift_f5"),
    ("regress/tty-keys.sh:rxvt-CSI-29:S-F6", "test_shift_f6"),
    ("regress/tty-keys.sh:rxvt-CSI-31:S-F7", "test_shift_f7"),
    ("regress/tty-keys.sh:rxvt-CSI-32:S-F8", "test_shift_f8"),
    ("regress/tty-keys.sh:rxvt-CSI-33:S-F9", "test_shift_f9"),
    ("regress/tty-keys.sh:rxvt-CSI-34:S-F10", "test_shift_f10"),
    ("regress/tty-keys.sh:rxvt-CSI-23$:S-F11", "test_shift_f11"),
    ("regress/tty-keys.sh:rxvt-CSI-24$:S-F12", "test_shift_f12"),
)


FUNCTION_CODES = {
    5: 15,
    6: 17,
    7: 18,
    8: 19,
    9: 20,
    10: 21,
    11: 23,
    12: 24,
}


class TmuxRegressTtyKeysRxvtFunctionTest(unittest.TestCase):
    def _assert_function(self, number, shifted=False):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                KEY_F1 + number - 1,
                PRESS,
                modifiers=SHIFT if shifted else 0,
            )
            if number <= 4:
                final = bytes((ord("P") + number - 1,))
                expected = (
                    b"\x1b[1;2" + final if shifted else b"\x1bO" + final
                )
            else:
                code = FUNCTION_CODES[number]
                modifier = b";2" if shifted else b""
                expected = b"\x1b[" + str(code).encode() + modifier + b"~"
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_22_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 22)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 22)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 22)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_f1(self):
        self._assert_function(1)

    def test_f2(self):
        self._assert_function(2)

    def test_f3(self):
        self._assert_function(3)

    def test_f4(self):
        self._assert_function(4)

    def test_f5(self):
        self._assert_function(5)

    def test_f6(self):
        self._assert_function(6)

    def test_f7(self):
        self._assert_function(7)

    def test_f8(self):
        self._assert_function(8)

    def test_f9(self):
        self._assert_function(9)

    def test_f10(self):
        self._assert_function(10)

    def test_f11(self):
        self._assert_function(11)

    def test_f12(self):
        self._assert_function(12)

    def test_shift_f3(self):
        self._assert_function(3, True)

    def test_shift_f4(self):
        self._assert_function(4, True)

    def test_shift_f5(self):
        self._assert_function(5, True)

    def test_shift_f6(self):
        self._assert_function(6, True)

    def test_shift_f7(self):
        self._assert_function(7, True)

    def test_shift_f8(self):
        self._assert_function(8, True)

    def test_shift_f9(self):
        self._assert_function(9, True)

    def test_shift_f10(self):
        self._assert_function(10, True)

    def test_shift_f11(self):
        self._assert_function(11, True)

    def test_shift_f12(self):
        self._assert_function(12, True)


if __name__ == "__main__":
    unittest.main()

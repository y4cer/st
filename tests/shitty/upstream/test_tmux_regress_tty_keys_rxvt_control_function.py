# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Rxvt control-function decoder cases from current tmux tty-keys."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2

KEY_F1 = 290


PORTED_CASES = tuple(
    (
        f"regress/tty-keys.sh:rxvt-CSI-{code}^:C-F{number}",
        f"test_control_f{number}",
    )
    for number, code in enumerate(
        (11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24),
        start=1,
    )
) + tuple(
    (
        f"regress/tty-keys.sh:rxvt-CSI-{code}@:C-S-F{number}",
        f"test_control_shift_f{number}",
    )
    for number, code in enumerate(
        (11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24),
        start=1,
    )
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


class TmuxRegressTtyKeysRxvtControlFunctionTest(unittest.TestCase):
    def _assert_function(self, number, shifted=False):
        modifiers = CONTROL | (SHIFT if shifted else 0)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                KEY_F1 + number - 1,
                PRESS,
                modifiers=modifiers,
            )
            if number <= 4:
                final = chr(ord("P") + number - 1)
                expected = f"\x1b[1;{6 if shifted else 5}{final}".encode()
            else:
                code = FUNCTION_CODES[number]
                expected = f"\x1b[{code};{6 if shifted else 5}~".encode()
            self.assertEqual(terminal.read_input(), expected)

    def test_upstream_inventory_has_24_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 24)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 24)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 24)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_control_f1(self):
        self._assert_function(1)

    def test_control_f2(self):
        self._assert_function(2)

    def test_control_f3(self):
        self._assert_function(3)

    def test_control_f4(self):
        self._assert_function(4)

    def test_control_f5(self):
        self._assert_function(5)

    def test_control_f6(self):
        self._assert_function(6)

    def test_control_f7(self):
        self._assert_function(7)

    def test_control_f8(self):
        self._assert_function(8)

    def test_control_f9(self):
        self._assert_function(9)

    def test_control_f10(self):
        self._assert_function(10)

    def test_control_f11(self):
        self._assert_function(11)

    def test_control_f12(self):
        self._assert_function(12)

    def test_control_shift_f1(self):
        self._assert_function(1, True)

    def test_control_shift_f2(self):
        self._assert_function(2, True)

    def test_control_shift_f3(self):
        self._assert_function(3, True)

    def test_control_shift_f4(self):
        self._assert_function(4, True)

    def test_control_shift_f5(self):
        self._assert_function(5, True)

    def test_control_shift_f6(self):
        self._assert_function(6, True)

    def test_control_shift_f7(self):
        self._assert_function(7, True)

    def test_control_shift_f8(self):
        self._assert_function(8, True)

    def test_control_shift_f9(self):
        self._assert_function(9, True)

    def test_control_shift_f10(self):
        self._assert_function(10, True)

    def test_control_shift_f11(self):
        self._assert_function(11, True)

    def test_control_shift_f12(self):
        self._assert_function(12, True)


if __name__ == "__main__":
    unittest.main()

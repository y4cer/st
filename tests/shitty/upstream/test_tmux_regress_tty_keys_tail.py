# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Final active cases from current tmux tty-keys regress."""

import unittest

from harness import Shitty


PRESS = 1
SHIFT = 1
CONTROL = 2
ALT = 4

KEY_TAB = 258


PORTED_CASES = (
    ("regress/tty-keys.sh:CSI-I:FocusIn", "test_focus_in"),
    ("regress/tty-keys.sh:CSI-O:FocusOut", "test_focus_out"),
    ("regress/tty-keys.sh:CSI-200:PasteStart", "test_paste_start"),
    ("regress/tty-keys.sh:CSI-201:PasteEnd", "test_paste_end"),
    ("regress/tty-keys.sh:CSI-Z:BTab", "test_backtab"),
    ("regress/tty-keys.sh:CSI-123;5u:C-{", "test_control_left_brace"),
    (
        "regress/tty-keys.sh:CSI-123;7u:C-M-{",
        "test_control_alt_left_brace",
    ),
    ("regress/tty-keys.sh:CSI-32;2u:S-Space", "test_shift_space"),
    ("regress/tty-keys.sh:CSI-9;5u:C-Tab", "test_control_tab"),
    ("regress/tty-keys.sh:CSI-1;5Z:C-S-Tab", "test_control_shift_tab"),
)


class TmuxRegressTtyKeysTailTest(unittest.TestCase):
    def test_upstream_inventory_has_10_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 10)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 10)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 10)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_focus_in(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.focus(False)
            terminal.write(b"\x1b[?1004h")
            terminal.focus(True)
            self.assertEqual(terminal.read_input(), b"\x1b[I")

    def test_focus_out(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.focus(True)
            terminal.write(b"\x1b[?1004h")
            terminal.focus(False)
            self.assertEqual(terminal.read_input(), b"\x1b[O")

    def test_paste_start(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2004h")
            terminal.paste(b"payload")
            self.assertTrue(terminal.read_input().startswith(b"\x1b[200~"))

    def test_paste_end(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2004h")
            terminal.paste(b"payload")
            self.assertTrue(terminal.read_input().endswith(b"\x1b[201~"))

    def test_backtab(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_TAB, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[Z")

    def test_control_left_brace(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_text_event("{", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[27;5;123~")

    def test_control_alt_left_brace(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_text_event("{", modifiers=CONTROL | ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[27;7;123~")

    def test_shift_space(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                " ", " ", " ", modifiers=SHIFT, shifted=" "
            )
            terminal.frontend_text_event(" ", modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b" ")

    def test_control_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(KEY_TAB, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[27;5;9~")

    def test_control_shift_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                KEY_TAB,
                PRESS,
                modifiers=CONTROL | SHIFT,
            )
            self.assertEqual(terminal.read_input(), b"\x1b[Z")


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of Foot legacy and Kitty keyboard unit vectors."""

import unittest

from harness import Shitty


SHIFT = 1
CONTROL = 2
ALT = 4

PRESS = 1

KEY_ENTER = 257
KEY_TAB = 258
KEY_BACKSPACE = 259
KEY_LEFT = 263


UPSTREAM_CASES = (
    "legacy: control shift ISO Left Tab",
    "legacy: alt return in modifyOtherKeys level 1",
    "legacy: alt return in modifyOtherKeys level 2",
    "Kitty Swedish: control shift a reports alternate",
    "Kitty Swedish: alt shift 2 reports alternate",
    "Kitty Swedish: AltGr result reports the base key",
    "Kitty Swedish: alt backspace",
    "Kitty Swedish: control enter",
    "Kitty Swedish: control tab",
    "Kitty Swedish: control shift left",
    "Kitty de(neo): layout key and base key differ",
    "Kitty us(intl): composed double quote keeps shift",
)


def enable_kitty_alternate(terminal):
    terminal.write(b"\x1b[=5u")


class FootKeyboardTest(unittest.TestCase):
    def test_upstream_inventory_has_all_12_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 12)
        self.assertEqual(len(set(UPSTREAM_CASES)), 12)

    def test_legacy_control_shift_iso_left_tab_follows_consensus(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(
                KEY_TAB, PRESS, modifiers=SHIFT | CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[Z")

    def test_legacy_alt_return_in_modify_other_keys_level_1(self):
        with Shitty(
            columns=8, rows=2,
            extra_arguments=("-modifyOtherKeys", "1"),
        ) as terminal:
            terminal.frontend_key_event(KEY_ENTER, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b\r")

    def test_legacy_alt_return_in_modify_other_keys_level_2(self):
        with Shitty(
            columns=8, rows=2,
            extra_arguments=("-modifyOtherKeys", "2"),
        ) as terminal:
            terminal.frontend_key_event(KEY_ENTER, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[27;3;13~")

    def test_kitty_swedish_control_shift_a_reports_alternate(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.layout_key(
                "A", "a", "a", modifiers=SHIFT | CONTROL, shifted="A"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[97:65;6u")

    def test_kitty_swedish_alt_shift_2_reports_alternate(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.layout_key(
                "2", "2", "2", modifiers=SHIFT | ALT, shifted='"'
            )
            self.assertEqual(terminal.read_input(), b"\x1b[50:34;4u")

    def test_kitty_swedish_altgr_result_reports_the_base_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.layout_key(
                "2", "²", "2", modifiers=SHIFT | ALT,
            )
            self.assertEqual(terminal.read_input(), b"\x1b[178::50;4u")

    def test_kitty_swedish_alt_backspace(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.frontend_key_event(KEY_BACKSPACE, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[127;3u")

    def test_kitty_swedish_control_enter(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.frontend_key_event(KEY_ENTER, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[13;5u")

    def test_kitty_swedish_control_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.frontend_key_event(KEY_TAB, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[9;5u")

    def test_kitty_swedish_control_shift_left(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.frontend_key_event(
                KEY_LEFT, PRESS, modifiers=SHIFT | CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[1;6D")

    def test_kitty_de_neo_reports_layout_alternate_and_base(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_kitty_alternate(terminal)
            terminal.layout_key(
                "Y", "k", "y", modifiers=SHIFT | ALT, shifted="K"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[107:75:121;4u")

    def test_kitty_us_intl_composed_quote_keeps_shift(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            terminal.kitty_key(ord('"'), modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[34;2u")


if __name__ == "__main__":
    unittest.main()

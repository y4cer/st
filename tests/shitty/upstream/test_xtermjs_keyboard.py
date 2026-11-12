# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all xterm.js ``Keyboard.test.ts`` cases."""

import unittest

from harness import Shitty


PRESS = 1

SHIFT = 1
CONTROL = 2
ALT = 4

KEY_ESCAPE = 256
KEY_ENTER = 257
KEY_TAB = 258
KEY_BACKSPACE = 259
KEY_INSERT = 260
KEY_DELETE = 261
KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264
KEY_UP = 265
KEY_PAGE_UP = 266
KEY_PAGE_DOWN = 267
KEY_HOME = 268
KEY_END = 269
KEY_F1 = 290
KEY_F2 = 291
KEY_F3 = 292
KEY_F4 = 293
KEY_F5 = 294
KEY_F6 = 295
KEY_F7 = 296
KEY_F8 = 297
KEY_F9 = 298
KEY_F10 = 299
KEY_F11 = 300
KEY_F12 = 301


UPSTREAM_CASES = (
    "unmodified keys use their legacy escape sequences",
    "control delete uses modifier five",
    "shift delete uses modifier two",
    "alt delete uses modifier three",
    "alt enter prefixes carriage return with escape",
    "alt escape emits two escapes",
    "control left uses modifier five",
    "control right uses modifier five",
    "control up uses modifier five",
    "control down uses modifier five",
    "control backspace emits backspace",
    "alt backspace prefixes delete with escape",
    "control alt backspace prefixes backspace with escape",
    "repeated shift delete assertion uses modifier two",
    "repeated alt delete assertion uses modifier three",
    "non-mac alt left uses modifier three",
    "non-mac alt right uses modifier three",
    "non-mac alt up uses modifier three",
    "non-mac alt down uses modifier three",
    "non-mac alt letter prefixes text with escape",
    "non-mac alt space prefixes space with escape",
    "non-mac control alt space prefixes nul with escape",
    "mac alt left uses modifier three",
    "mac alt right uses modifier three",
    "mac alt up uses modifier three",
    "mac alt down uses modifier three",
    "mac native option keeps composed text on the text path",
    "mac option-as-meta alt letter prefixes text with escape",
    "mac option-as-meta alt enter prefixes carriage return with escape",
    "repeated alt up assertion uses modifier three",
    "repeated alt down assertion uses modifier three",
    "modified function keys carry shift alt and control",
    "control alt letter prefixes its control byte with escape",
    "alt zero prefixes both layout levels with escape",
    "alt one prefixes both layout levels with escape",
    "alt two prefixes both layout levels with escape",
    "alt three prefixes both layout levels with escape",
    "alt four prefixes both layout levels with escape",
    "alt five prefixes both layout levels with escape",
    "alt six prefixes both layout levels with escape",
    "alt seven prefixes both layout levels with escape",
    "alt eight prefixes both layout levels with escape",
    "alt nine prefixes both layout levels with escape",
    "alt semicolon prefixes both layout levels with escape",
    "alt equals prefixes both layout levels with escape",
    "alt comma prefixes both layout levels with escape",
    "alt minus prefixes both layout levels with escape",
    "alt period prefixes both layout levels with escape",
    "alt slash prefixes both layout levels with escape",
    "alt grave prefixes both layout levels with escape",
    "alt left bracket prefixes both layout levels with escape",
    "alt backslash prefixes both layout levels with escape",
    "alt right bracket prefixes both layout levels with escape",
    "alt apostrophe prefixes both layout levels with escape",
    "mobile arrow aliases use normal and application cursor modes",
    "lowercase printable text follows the text path",
    "uppercase printable text follows the text path",
    "alt shift letters prefix their selected layout level",
    "control at emits nul",
    "control caret emits record separator",
    "control underscore emits unit separator",
)


def press(terminal, key, modifiers=0):
    terminal.frontend_key_event(key, PRESS, modifiers=modifiers)


class XtermJsKeyboardTest(unittest.TestCase):
    def test_upstream_inventory_has_61_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 61)
        self.assertEqual(len(set(UPSTREAM_CASES)), 61)

    def test_unmodified_keys_use_their_legacy_escape_sequences(self):
        cases = (
            (KEY_BACKSPACE, b"\x7f"),
            (KEY_TAB, b"\t"),
            (KEY_ENTER, b"\r"),
            (KEY_ESCAPE, b"\x1b"),
            (KEY_PAGE_UP, b"\x1b[5~"),
            (KEY_PAGE_DOWN, b"\x1b[6~"),
            (KEY_END, b"\x1b[F"),
            (KEY_HOME, b"\x1b[H"),
            (KEY_LEFT, b"\x1b[D"),
            (KEY_UP, b"\x1b[A"),
            (KEY_RIGHT, b"\x1b[C"),
            (KEY_DOWN, b"\x1b[B"),
            (KEY_INSERT, b"\x1b[2~"),
            (KEY_DELETE, b"\x1b[3~"),
            (KEY_F1, b"\x1bOP"),
            (KEY_F2, b"\x1bOQ"),
            (KEY_F3, b"\x1bOR"),
            (KEY_F4, b"\x1bOS"),
            (KEY_F5, b"\x1b[15~"),
            (KEY_F6, b"\x1b[17~"),
            (KEY_F7, b"\x1b[18~"),
            (KEY_F8, b"\x1b[19~"),
            (KEY_F9, b"\x1b[20~"),
            (KEY_F10, b"\x1b[21~"),
            (KEY_F11, b"\x1b[23~"),
            (KEY_F12, b"\x1b[24~"),
        )
        with Shitty(columns=8, rows=2) as terminal:
            for key, expected in cases:
                with self.subTest(key=key):
                    press(terminal, key)
                    self.assertEqual(terminal.read_input(), expected)

    def assert_key(self, key, modifiers, expected):
        with Shitty(columns=8, rows=2) as terminal:
            press(terminal, key, modifiers)
            self.assertEqual(terminal.read_input(), expected)

    def test_control_delete_uses_modifier_five(self):
        self.assert_key(KEY_DELETE, CONTROL, b"\x1b[3;5~")

    def test_shift_delete_uses_modifier_two(self):
        self.assert_key(KEY_DELETE, SHIFT, b"\x1b[3;2~")

    def test_alt_delete_uses_modifier_three(self):
        self.assert_key(KEY_DELETE, ALT, b"\x1b[3;3~")

    def test_alt_enter_prefixes_carriage_return_with_escape(self):
        self.assert_key(KEY_ENTER, ALT, b"\x1b\r")

    def test_alt_escape_emits_two_escapes(self):
        self.assert_key(KEY_ESCAPE, ALT, b"\x1b\x1b")

    def test_control_left_uses_modifier_five(self):
        self.assert_key(KEY_LEFT, CONTROL, b"\x1b[1;5D")

    def test_control_right_uses_modifier_five(self):
        self.assert_key(KEY_RIGHT, CONTROL, b"\x1b[1;5C")

    def test_control_up_uses_modifier_five(self):
        self.assert_key(KEY_UP, CONTROL, b"\x1b[1;5A")

    def test_control_down_uses_modifier_five(self):
        self.assert_key(KEY_DOWN, CONTROL, b"\x1b[1;5B")

    def test_control_backspace_emits_backspace(self):
        self.assert_key(KEY_BACKSPACE, CONTROL, b"\x08")

    def test_alt_backspace_prefixes_delete_with_escape(self):
        self.assert_key(KEY_BACKSPACE, ALT, b"\x1b\x7f")

    def test_control_alt_backspace_prefixes_backspace_with_escape(self):
        self.assert_key(KEY_BACKSPACE, CONTROL | ALT, b"\x1b\x08")

    def test_repeated_shift_delete_assertion_uses_modifier_two(self):
        self.assert_key(KEY_DELETE, SHIFT, b"\x1b[3;2~")

    def test_repeated_alt_delete_assertion_uses_modifier_three(self):
        self.assert_key(KEY_DELETE, ALT, b"\x1b[3;3~")

    def test_non_mac_alt_left_uses_modifier_three(self):
        self.assert_key(KEY_LEFT, ALT, b"\x1b[1;3D")

    def test_non_mac_alt_right_uses_modifier_three(self):
        self.assert_key(KEY_RIGHT, ALT, b"\x1b[1;3C")

    def test_non_mac_alt_up_uses_modifier_three(self):
        self.assert_key(KEY_UP, ALT, b"\x1b[1;3A")

    def test_non_mac_alt_down_uses_modifier_three(self):
        self.assert_key(KEY_DOWN, ALT, b"\x1b[1;3B")

    def test_non_mac_alt_letter_prefixes_text_with_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=ALT)
            terminal.frontend_text_event("a", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1ba")

    def test_non_mac_alt_space_prefixes_space_with_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(" ", " ", " ", modifiers=ALT)
            terminal.frontend_text_event(" ", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b ")

    def test_non_mac_control_alt_space_prefixes_nul_with_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control(" ", alt=True)
            self.assertEqual(terminal.read_input(), b"\x1b\x00")

    def test_mac_alt_left_uses_modifier_three(self):
        self.assert_key(KEY_LEFT, ALT, b"\x1b[1;3D")

    def test_mac_alt_right_uses_modifier_three(self):
        self.assert_key(KEY_RIGHT, ALT, b"\x1b[1;3C")

    def test_mac_alt_up_uses_modifier_three(self):
        self.assert_key(KEY_UP, ALT, b"\x1b[1;3A")

    def test_mac_alt_down_uses_modifier_three(self):
        self.assert_key(KEY_DOWN, ALT, b"\x1b[1;3B")

    def test_mac_native_option_keeps_composed_text_on_the_text_path(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-altSendsEscape", "false"),
        ) as terminal:
            terminal.frontend_text_event("å", modifiers=ALT)
            self.assertEqual(terminal.read_input(), "å".encode())

    def test_mac_option_as_meta_alt_letter_prefixes_text_with_escape(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=ALT)
            terminal.frontend_text_event("a", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1ba")

    def test_mac_option_as_meta_alt_enter_prefixes_carriage_return(self):
        self.assert_key(KEY_ENTER, ALT, b"\x1b\r")

    def test_repeated_alt_up_assertion_uses_modifier_three(self):
        self.assert_key(KEY_UP, ALT, b"\x1b[1;3A")

    def test_repeated_alt_down_assertion_uses_modifier_three(self):
        self.assert_key(KEY_DOWN, ALT, b"\x1b[1;3B")

    def test_modified_function_keys_carry_shift_alt_and_control(self):
        keys = (
            (KEY_F1, "1", "P"),
            (KEY_F2, "1", "Q"),
            (KEY_F3, "1", "R"),
            (KEY_F4, "1", "S"),
            (KEY_F5, "15", "~"),
            (KEY_F6, "17", "~"),
            (KEY_F7, "18", "~"),
            (KEY_F8, "19", "~"),
            (KEY_F9, "20", "~"),
            (KEY_F10, "21", "~"),
            (KEY_F11, "23", "~"),
            (KEY_F12, "24", "~"),
        )
        modifiers = ((SHIFT, 2), (ALT, 3), (CONTROL, 5))
        with Shitty(columns=8, rows=2) as terminal:
            for modifier, parameter in modifiers:
                for key, number, final in keys:
                    with self.subTest(key=key, modifier=modifier):
                        press(terminal, key, modifier)
                        expected = f"\x1b[{number};{parameter}{final}".encode()
                        self.assertEqual(terminal.read_input(), expected)

    def test_control_alt_letter_prefixes_its_control_byte_with_escape(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-modifyOtherKeys", "0"),
        ) as terminal:
            terminal.frontend_control("A", alt=True)
            self.assertEqual(terminal.read_input(), b"\x1b\x01")

    def assert_alt_digit(self, unshifted, shifted):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(unshifted, unshifted, unshifted, modifiers=ALT)
            terminal.frontend_text_event(unshifted, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b" + unshifted.encode())

            terminal.layout_key(
                unshifted,
                shifted,
                unshifted,
                modifiers=ALT | SHIFT,
                shifted=shifted,
            )
            terminal.frontend_text_event(shifted, modifiers=ALT | SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b" + shifted.encode())

    def test_alt_zero_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("0", ")")

    def test_alt_one_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("1", "!")

    def test_alt_two_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("2", "@")

    def test_alt_three_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("3", "#")

    def test_alt_four_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("4", "$")

    def test_alt_five_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("5", "%")

    def test_alt_six_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("6", "^")

    def test_alt_seven_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("7", "&")

    def test_alt_eight_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("8", "*")

    def test_alt_nine_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_digit("9", "(")

    def assert_alt_printable(self, unshifted, shifted):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                unshifted, unshifted, unshifted, modifiers=ALT
            )
            terminal.frontend_text_event(unshifted, modifiers=ALT)
            self.assertEqual(
                terminal.read_input(), b"\x1b" + unshifted.encode()
            )

            terminal.layout_key(
                unshifted,
                shifted,
                unshifted,
                modifiers=ALT | SHIFT,
                shifted=shifted,
            )
            terminal.frontend_text_event(
                shifted, modifiers=ALT | SHIFT
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b" + shifted.encode()
            )

    def test_alt_semicolon_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable(";", ":")

    def test_alt_equals_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("=", "+")

    def test_alt_comma_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable(",", "<")

    def test_alt_minus_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("-", "_")

    def test_alt_period_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable(".", ">")

    def test_alt_slash_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("/", "?")

    def test_alt_grave_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("`", "~")

    def test_alt_left_bracket_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("[", "{")

    def test_alt_backslash_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("\\", "|")

    def test_alt_right_bracket_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("]", "}")

    def test_alt_apostrophe_prefixes_both_layout_levels_with_escape(self):
        self.assert_alt_printable("'", '"')

    def test_mobile_arrow_aliases_use_normal_and_application_cursor_modes(self):
        arrows = (
            (KEY_UP, "A"),
            (KEY_LEFT, "D"),
            (KEY_RIGHT, "C"),
            (KEY_DOWN, "B"),
        )
        with Shitty(columns=8, rows=2) as terminal:
            for key, final in arrows:
                press(terminal, key)
                self.assertEqual(
                    terminal.read_input(), f"\x1b[{final}".encode()
                )

            terminal.write(b"\x1b[?1h")
            for key, final in arrows:
                press(terminal, key)
                self.assertEqual(
                    terminal.read_input(), f"\x1bO{final}".encode()
                )

    def test_lowercase_printable_text_follows_the_text_path(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_text_event("a")
            self.assertEqual(terminal.read_input(), b"a")
            terminal.frontend_text_event("-")
            self.assertEqual(terminal.read_input(), b"-")

    def test_uppercase_printable_text_follows_the_text_path(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_text_event("A", modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"A")
            terminal.frontend_text_event("!", modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"!")

    def test_alt_shift_letters_prefix_their_selected_layout_level(self):
        with Shitty(columns=8, rows=2) as terminal:
            for unshifted in "ahz":
                shifted = unshifted.upper()
                terminal.layout_key(
                    shifted,
                    shifted,
                    unshifted,
                    modifiers=ALT | SHIFT,
                    shifted=shifted,
                )
                terminal.frontend_text_event(
                    shifted, modifiers=ALT | SHIFT
                )
                self.assertEqual(
                    terminal.read_input(), b"\x1b" + shifted.encode()
                )

            for unshifted in "ahz":
                terminal.layout_key(
                    unshifted,
                    unshifted,
                    unshifted,
                    modifiers=ALT,
                )
                terminal.frontend_text_event(unshifted, modifiers=ALT)
                self.assertEqual(
                    terminal.read_input(), b"\x1b" + unshifted.encode()
                )

    def test_control_at_emits_nul(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control("2", shifted=True)
            self.assertEqual(terminal.read_input(), b"\x00")

    def test_control_caret_emits_record_separator(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control("6", shifted=True)
            self.assertEqual(terminal.read_input(), b"\x1e")

    def test_control_underscore_emits_unit_separator(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control("-", shifted=True)
            self.assertEqual(terminal.read_input(), b"\x1f")

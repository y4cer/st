# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of the first xterm.js KittyKeyboard cases."""

import unittest

from harness import Shitty


RELEASE = 0
PRESS = 1
REPEAT = 2

SHIFT = 1
CONTROL = 2
ALT = 4
SUPER = 8

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
KEY_F13 = 302
KEY_F14 = 303
KEY_F20 = 309
KEY_F24 = 313
KEY_KP_0 = 320
KEY_KP_1 = 321
KEY_KP_5 = 325
KEY_KP_9 = 329
KEY_KP_DECIMAL = 330
KEY_KP_DIVIDE = 331
KEY_KP_MULTIPLY = 332
KEY_KP_SUBTRACT = 333
KEY_KP_ADD = 334
KEY_KP_ENTER = 335
KEY_KP_EQUAL = 336
KEY_LEFT_SHIFT = 340
KEY_LEFT_CONTROL = 341
KEY_LEFT_ALT = 342
KEY_LEFT_SUPER = 343
KEY_RIGHT_SHIFT = 344
KEY_RIGHT_CONTROL = 345
KEY_RIGHT_ALT = 346
KEY_RIGHT_SUPER = 347
KEY_CAPS_LOCK = 280
KEY_SCROLL_LOCK = 281
KEY_NUM_LOCK = 282

UPSTREAM_CASES = (
    "protocol is inactive when flags are zero",
    "protocol is active when any flag is set",
    "shift letter remains plain in disambiguate mode",
    "alt modifier is encoded as three",
    "control modifier is encoded as five",
    "super modifier is encoded as nine",
    "control shift modifiers are encoded as six",
    "control alt modifiers are encoded as seven",
    "control alt shift modifiers are encoded as eight",
    "control super modifiers are encoded as thirteen",
    "all four modifiers are encoded as sixteen",
    "an unmodified escape omits the modifier field",
    "escape is disambiguated as CSI 27 u",
    "enter remains legacy carriage return",
    "tab remains legacy horizontal tab",
    "backspace remains legacy delete",
    "space remains plain text",
    "shift tab is disambiguated as CSI 9;2 u",
    "control enter is disambiguated as CSI 13;5 u",
    "alt escape is disambiguated as CSI 27;3 u",
    "control backspace is disambiguated as CSI 127;5 u",
    "control space is disambiguated as CSI 32;5 u",
    "alt space is disambiguated as CSI 32;3 u",
    "insert retains CSI 2 tilde encoding",
    "delete retains CSI 3 tilde encoding",
    "page up retains CSI 5 tilde encoding",
    "page down retains CSI 6 tilde encoding",
    "home retains CSI H encoding",
    "end retains CSI F encoding",
    "shift page up includes modifier two",
    "control home includes modifier five",
    "up retains CSI A encoding",
    "down retains CSI B encoding",
    "right retains CSI C encoding",
    "left retains CSI D encoding",
    "shift up includes modifier two",
    "control left includes modifier five",
    "control shift right includes modifier six",
    "F1 retains SS3 P encoding",
    "F2 retains SS3 Q encoding",
    "F3 retains SS3 R encoding",
    "F4 retains SS3 S encoding",
    "F5 retains CSI 15 tilde encoding",
    "F6 retains CSI 17 tilde encoding",
    "F7 retains CSI 18 tilde encoding",
    "F8 retains CSI 19 tilde encoding",
    "F9 retains CSI 20 tilde encoding",
    "F10 retains CSI 21 tilde encoding",
    "F11 retains CSI 23 tilde encoding",
    "F12 retains CSI 24 tilde encoding",
    "shift F1 includes modifier two",
    "control F5 includes modifier five",
    "F13 uses private-use code 57376",
    "F14 uses private-use code 57377",
    "F20 uses private-use code 57383",
    "F24 uses private-use code 57387",
    "numpad zero uses private-use code 57399",
    "numpad one uses private-use code 57400",
    "numpad nine uses private-use code 57408",
    "numpad decimal uses private-use code 57409",
    "numpad divide uses private-use code 57410",
    "numpad multiply uses private-use code 57411",
    "numpad subtract uses private-use code 57412",
    "numpad add uses private-use code 57413",
    "numpad enter uses private-use code 57414",
    "numpad equal uses private-use code 57415",
    "control numpad five includes modifier five",
    "left shift uses private-use code 57441",
    "right shift uses private-use code 57447",
    "left control uses private-use code 57442",
    "right control uses private-use code 57448",
    "left alt uses private-use code 57443",
    "right alt uses private-use code 57449",
    "left super uses private-use code 57444",
    "right super uses private-use code 57450",
    "caps lock uses private-use code 57358",
    "num lock uses private-use code 57360",
    "scroll lock uses private-use code 57359",
    "text press event remains plain UTF-8",
    "escape press event omits the event suffix",
    "enter press event remains legacy carriage return",
    "tab press event remains legacy horizontal tab",
    "backspace press event remains legacy delete",
    "modified press event omits the press suffix",
    "text repeat event remains plain UTF-8",
    "escape repeat event includes the repeat suffix",
    "enter repeat event remains legacy carriage return",
    "tab repeat event remains legacy horizontal tab",
    "backspace repeat event remains legacy delete",
    "text release event includes the release suffix",
    "escape release event includes the release suffix",
    "enter release event is not reported",
    "tab release event is not reported",
    "backspace release event is not reported",
    "modified release event includes the release suffix",
    "modified repeat event includes the repeat suffix",
    "functional release event includes the release suffix",
    "modifier release clears its own modifier bit",
    "event-only modified press is not swallowed",
    "event-only modified repeat is not swallowed",
    "event-only modified release is reported",
    "modifier press requires report-all mode",
    "modifier release requires report-all mode",
    "caps lock press requires report-all mode",
    "num lock press requires report-all mode",
    "scroll lock press requires report-all mode",
    "caps lock release requires report-all mode",
    "report-all encodes a lowercase letter",
    "report-all encodes an uppercase letter by its base codepoint",
    "report-all encodes a digit",
    "report-all encodes punctuation",
    "report-all encodes brackets",
    "report-all encodes space",
    "report-all encodes enter press",
    "report-all encodes tab press",
    "report-all encodes backspace press",
    "report-all encodes enter repeat",
    "report-all encodes tab repeat",
    "report-all encodes backspace repeat",
    "report-all encodes enter release",
    "report-all encodes tab release",
    "report-all encodes backspace release",
    "associated text includes a regular key codepoint",
    "associated text includes shifted text",
    "associated text omits a control chord",
    "associated text is absent from a functional key",
    "associated text is absent from a release event",
    "associated text includes a digit",
    "associated text includes a shifted digit symbol",
    "alternate keys include a shifted letter",
    "alternate keys omit an unshifted duplicate",
    "alternate keys include a shifted digit symbol",
    "alternate keys are absent from functional keys",
    "alternate and associated fields coexist on shifted letters",
    "alternate fields survive release without associated text",
    "release is suppressed without report-event-types",
    "shift letter stays plain in disambiguate mode",
    "control shift letter uses the lowercase key codepoint",
    "dead key produces no output",
    "unidentified key produces no output",
    "PrintScreen uses private-use code 57361",
    "Pause uses private-use code 57362",
    "ContextMenu uses private-use code 57363",
    "MediaPlayPause uses private-use code 57430",
    "MediaStop uses private-use code 57432",
    "MediaTrackNext uses private-use code 57435",
    "MediaTrackPrevious uses private-use code 57436",
    "AudioVolumeDown uses private-use code 57438",
    "AudioVolumeUp uses private-use code 57439",
    "AudioVolumeMute uses private-use code 57440",
    "Option f as Alt uses the physical letter",
    "Option b as Alt uses the physical letter",
    "Option d as Alt uses the physical letter",
    "Option n dead key as Alt uses the physical letter",
    "Option e dead key as Alt uses the physical letter",
    "Option u dead key as Alt uses the physical letter",
    "Option 5 as Alt uses the physical digit",
    "Option Shift f as Alt uses the unshifted physical letter",
    "Control Option f as Alt uses the physical letter",
    "Linux Alt keeps the active layout key",
    "Linux AZERTY Alt keeps the active layout key instead of the DOM code",
    "native Option composition remains when Option-as-Alt is disabled",
    "native composed text remains when Alt is not pressed",
    "Option punctuation with a non-letter DOM code falls through",
    "Option f release reports the physical letter and release event",
)


def enable_disambiguation(terminal):
    terminal.write(b"\x1b[=1u")


def send_letter(terminal, modifiers):
    send_letter_event(terminal, modifiers, PRESS)


def send_letter_event(terminal, modifiers, action):
    terminal.layout_key(
        "A",
        "a",
        "a",
        modifiers=modifiers,
        action=action,
        shifted="A" if modifiers & SHIFT else 0,
    )
    if action != RELEASE and not modifiers & (CONTROL | SUPER):
        terminal.frontend_text_event(
            "A" if modifiers & SHIFT else "a",
            modifiers=modifiers,
        )


class XtermJsKittyKeyboardTest(unittest.TestCase):
    def test_upstream_inventory_has_165_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 165)
        self.assertEqual(len(set(UPSTREAM_CASES)), 165)

    def test_protocol_is_inactive_when_flags_are_zero(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?u")
            self.assertEqual(terminal.read_input(), b"\x1b[?0u")
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b")

    def test_protocol_is_active_when_any_flag_is_set(self):
        with Shitty(columns=8, rows=2) as terminal:
            for flags in (1, 2, 31):
                with self.subTest(flags=flags):
                    terminal.write(f"\x1b[={flags}u\x1b[?u".encode())
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1b[?{flags}u".encode(),
                    )

    def test_shift_letter_remains_plain_in_disambiguate_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, SHIFT)
            self.assertEqual(terminal.read_input(), b"A")

    def test_alt_modifier_is_encoded_as_three(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;3u")

    def test_control_modifier_is_encoded_as_five(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5u")

    def test_super_modifier_is_encoded_as_nine(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, SUPER)
            self.assertEqual(terminal.read_input(), b"\x1b[97;9u")

    def test_control_shift_modifiers_are_encoded_as_six(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, CONTROL | SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;6u")

    def test_control_alt_modifiers_are_encoded_as_seven(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, CONTROL | ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;7u")

    def test_control_alt_shift_modifiers_are_encoded_as_eight(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, CONTROL | ALT | SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;8u")

    def test_control_super_modifiers_are_encoded_as_thirteen(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, CONTROL | SUPER)
            self.assertEqual(terminal.read_input(), b"\x1b[97;13u")

    def test_all_four_modifiers_are_encoded_as_sixteen(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            send_letter(terminal, SHIFT | ALT | CONTROL | SUPER)
            self.assertEqual(terminal.read_input(), b"\x1b[97;16u")

    def test_unmodified_escape_omits_the_modifier_field(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[27u")

    def test_escape_is_disambiguated_as_csi_27_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[27u")

    def test_enter_remains_legacy_carriage_return(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_ENTER, PRESS)
            self.assertEqual(terminal.read_input(), b"\r")

    def test_tab_remains_legacy_horizontal_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_TAB, PRESS)
            self.assertEqual(terminal.read_input(), b"\t")

    def test_backspace_remains_legacy_delete(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_BACKSPACE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_space_remains_plain_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key(" ", " ", " ")
            terminal.frontend_text_event(" ")
            self.assertEqual(terminal.read_input(), b" ")

    def test_shift_tab_is_disambiguated_as_csi_9_2_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_TAB, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[9;2u")

    def test_control_enter_is_disambiguated_as_csi_13_5_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_ENTER, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[13;5u")

    def test_alt_escape_is_disambiguated_as_csi_27_3_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_ESCAPE, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[27;3u")

    def test_control_backspace_is_disambiguated_as_csi_127_5_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(
                KEY_BACKSPACE, PRESS, modifiers=CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[127;5u")

    def test_control_space_is_disambiguated_as_csi_32_5_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key(" ", " ", " ", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[32;5u")

    def test_alt_space_is_disambiguated_as_csi_32_3_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key(" ", " ", " ", modifiers=ALT)
            terminal.frontend_text_event(" ", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[32;3u")

    def test_insert_retains_csi_2_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_INSERT, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[2~")

    def test_delete_retains_csi_3_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_DELETE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[3~")

    def test_page_up_retains_csi_5_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_PAGE_UP, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[5~")

    def test_page_down_retains_csi_6_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_PAGE_DOWN, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[6~")

    def test_home_retains_csi_h_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_HOME, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[H")

    def test_end_retains_csi_f_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_END, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[F")

    @unittest.expectedFailure
    def test_shift_page_up_includes_modifier_two(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(
                KEY_PAGE_UP, PRESS, modifiers=SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x1b[5;2~")

    def test_control_home_includes_modifier_five(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_HOME, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[1;5H")

    def test_up_retains_csi_a_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_UP, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[A")

    def test_down_retains_csi_b_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_DOWN, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[B")

    def test_right_retains_csi_c_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_RIGHT, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[C")

    def test_left_retains_csi_d_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_LEFT, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[D")

    def test_shift_up_includes_modifier_two(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_UP, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[1;2A")

    def test_control_left_includes_modifier_five(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_LEFT, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[1;5D")

    def test_control_shift_right_includes_modifier_six(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(
                KEY_RIGHT, PRESS, modifiers=CONTROL | SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x1b[1;6C")

    @unittest.expectedFailure
    def test_f1_retains_ss3_p_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F1, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1bOP")

    @unittest.expectedFailure
    def test_f2_retains_ss3_q_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F2, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1bOQ")

    @unittest.expectedFailure
    def test_f3_retains_ss3_r_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F3, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1bOR")

    @unittest.expectedFailure
    def test_f4_retains_ss3_s_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F4, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1bOS")

    def test_f5_retains_csi_15_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F5, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[15~")

    def test_f6_retains_csi_17_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F6, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[17~")

    def test_f7_retains_csi_18_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F7, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[18~")

    def test_f8_retains_csi_19_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F8, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[19~")

    def test_f9_retains_csi_20_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F9, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[20~")

    def test_f10_retains_csi_21_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F10, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[21~")

    def test_f11_retains_csi_23_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F11, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[23~")

    def test_f12_retains_csi_24_tilde_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F12, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[24~")

    def test_shift_f1_includes_modifier_two(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F1, PRESS, modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[1;2P")

    def test_control_f5_includes_modifier_five(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F5, PRESS, modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[15;5~")

    def test_f13_uses_private_use_code_57376(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F13, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57376u")

    def test_f14_uses_private_use_code_57377(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F14, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57377u")

    def test_f20_uses_private_use_code_57383(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F20, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57383u")

    def test_f24_uses_private_use_code_57387(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_F24, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57387u")

    def test_numpad_zero_uses_private_use_code_57399(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_0, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57399u")

    def test_numpad_one_uses_private_use_code_57400(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_1, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57400u")

    def test_numpad_nine_uses_private_use_code_57408(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_9, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57408u")

    def test_numpad_decimal_uses_private_use_code_57409(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_DECIMAL, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57409u")

    def test_numpad_divide_uses_private_use_code_57410(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_DIVIDE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57410u")

    def test_numpad_multiply_uses_private_use_code_57411(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_MULTIPLY, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57411u")

    def test_numpad_subtract_uses_private_use_code_57412(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_SUBTRACT, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57412u")

    def test_numpad_add_uses_private_use_code_57413(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_ADD, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57413u")

    def test_numpad_enter_uses_private_use_code_57414(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_ENTER, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57414u")

    def test_numpad_equal_uses_private_use_code_57415(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(KEY_KP_EQUAL, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57415u")

    def test_control_numpad_five_includes_modifier_five(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.frontend_key_event(
                KEY_KP_5, PRESS, modifiers=CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57404;5u")

    def test_left_shift_uses_private_use_code_57441(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_LEFT_SHIFT, PRESS, modifiers=SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57441;2u")

    def test_right_shift_uses_private_use_code_57447(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_RIGHT_SHIFT, PRESS, modifiers=SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57447;2u")

    def test_left_control_uses_private_use_code_57442(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_LEFT_CONTROL, PRESS, modifiers=CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57442;5u")

    def test_right_control_uses_private_use_code_57448(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_RIGHT_CONTROL, PRESS, modifiers=CONTROL
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57448;5u")

    def test_left_alt_uses_private_use_code_57443(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(KEY_LEFT_ALT, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[57443;3u")

    def test_right_alt_uses_private_use_code_57449(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(KEY_RIGHT_ALT, PRESS, modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[57449;3u")

    def test_left_super_uses_private_use_code_57444(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_LEFT_SUPER, PRESS, modifiers=SUPER
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57444;9u")

    def test_right_super_uses_private_use_code_57450(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(
                KEY_RIGHT_SUPER, PRESS, modifiers=SUPER
            )
            self.assertEqual(terminal.read_input(), b"\x1b[57450;9u")

    def test_caps_lock_uses_private_use_code_57358(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(KEY_CAPS_LOCK, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57358u")

    def test_num_lock_uses_private_use_code_57360(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(KEY_NUM_LOCK, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57360u")

    def test_scroll_lock_uses_private_use_code_57359(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.frontend_key_event(KEY_SCROLL_LOCK, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[57359u")

    def test_text_press_event_remains_plain_utf8(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter(terminal, 0)
            self.assertEqual(terminal.read_input(), b"a")

    def test_escape_press_event_omits_the_event_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[27u")

    def test_enter_press_event_remains_legacy_carriage_return(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ENTER, PRESS)
            self.assertEqual(terminal.read_input(), b"\r")

    def test_tab_press_event_remains_legacy_horizontal_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_TAB, PRESS)
            self.assertEqual(terminal.read_input(), b"\t")

    def test_backspace_press_event_remains_legacy_delete(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_BACKSPACE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_modified_press_event_omits_the_press_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter_event(terminal, CONTROL, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5u")

    def test_text_repeat_event_remains_plain_utf8(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter_event(terminal, 0, REPEAT)
            self.assertEqual(terminal.read_input(), b"a")

    def test_escape_repeat_event_includes_the_repeat_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ESCAPE, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[27;1:2u")

    def test_enter_repeat_event_remains_legacy_carriage_return(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ENTER, REPEAT)
            self.assertEqual(terminal.read_input(), b"\r")

    def test_tab_repeat_event_remains_legacy_horizontal_tab(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_TAB, REPEAT)
            self.assertEqual(terminal.read_input(), b"\t")

    def test_backspace_repeat_event_remains_legacy_delete(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_BACKSPACE, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_text_release_event_includes_the_release_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter_event(terminal, 0, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[97;1:3u")

    def test_escape_release_event_includes_the_release_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ESCAPE, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[27;1:3u")

    def test_enter_release_event_is_not_reported(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_ENTER, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_tab_release_event_is_not_reported(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_TAB, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_backspace_release_event_is_not_reported(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_BACKSPACE, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_modified_release_event_includes_the_release_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter_event(terminal, CONTROL, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5:3u")

    def test_modified_repeat_event_includes_the_repeat_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            send_letter_event(terminal, SHIFT | ALT, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;4:2u")

    def test_functional_release_event_includes_the_release_suffix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.frontend_key_event(KEY_DELETE, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[3;1:3~")

    def test_modifier_release_clears_its_own_modifier_bit(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=11u")
            terminal.frontend_key_event(KEY_LEFT_SHIFT, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[57441;1:3u")

    def test_event_only_modified_press_is_not_swallowed(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            send_letter_event(terminal, CONTROL, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5u")

    def test_event_only_modified_repeat_is_not_swallowed(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            send_letter_event(terminal, CONTROL, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5:2u")

    def test_event_only_modified_release_is_reported(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            send_letter_event(terminal, CONTROL, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5:3u")

    def test_modifier_press_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            terminal.frontend_key_event(
                KEY_LEFT_SHIFT, PRESS, modifiers=SHIFT
            )
            self.assertEqual(terminal.read_input(), b"")

    def test_modifier_release_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            terminal.frontend_key_event(KEY_LEFT_SHIFT, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_caps_lock_press_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            for flags in (1, 2, 3):
                with self.subTest(flags=flags):
                    terminal.write(f"\x1b[={flags}u".encode())
                    terminal.frontend_key_event(KEY_CAPS_LOCK, PRESS)
                    self.assertEqual(terminal.read_input(), b"")

    def test_num_lock_press_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            terminal.frontend_key_event(KEY_NUM_LOCK, PRESS)
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_scroll_lock_press_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            terminal.frontend_key_event(KEY_SCROLL_LOCK, PRESS)
            self.assertEqual(terminal.read_input(), b"")

    def test_caps_lock_release_requires_report_all_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=2u")
            terminal.frontend_key_event(KEY_CAPS_LOCK, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_report_all_encodes_a_lowercase_letter(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            send_letter_event(terminal, 0, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[97u")

    def test_report_all_encodes_an_uppercase_letter_by_base_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            send_letter_event(terminal, SHIFT, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[97;2u")

    def test_report_all_encodes_a_digit(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.layout_key("5", "5", "5")
            terminal.frontend_text_event("5")
            self.assertEqual(terminal.read_input(), b"\x1b[53u")

    def test_report_all_encodes_punctuation(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            for character in ".,;/":
                with self.subTest(character=character):
                    terminal.layout_key(character, character, character)
                    terminal.frontend_text_event(character)
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1b[{ord(character)}u".encode(),
                    )

    def test_report_all_encodes_brackets(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            for character in "[]":
                with self.subTest(character=character):
                    terminal.layout_key(character, character, character)
                    terminal.frontend_text_event(character)
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1b[{ord(character)}u".encode(),
                    )

    def test_report_all_encodes_space(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=8u")
            terminal.layout_key(" ", " ", " ")
            terminal.frontend_text_event(" ")
            self.assertEqual(terminal.read_input(), b"\x1b[32u")

    def test_report_all_encodes_enter_press(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_ENTER, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[13u")

    def test_report_all_encodes_tab_press(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_TAB, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[9u")

    def test_report_all_encodes_backspace_press(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_BACKSPACE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[127u")

    def test_report_all_encodes_enter_repeat(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_ENTER, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[13;1:2u")

    def test_report_all_encodes_tab_repeat(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_TAB, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[9;1:2u")

    def test_report_all_encodes_backspace_repeat(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_BACKSPACE, REPEAT)
            self.assertEqual(terminal.read_input(), b"\x1b[127;1:2u")

    def test_report_all_encodes_enter_release(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_ENTER, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[13;1:3u")

    def test_report_all_encodes_tab_release(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_TAB, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[9;1:3u")

    def test_report_all_encodes_backspace_release(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            terminal.frontend_key_event(KEY_BACKSPACE, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[127;1:3u")

    def test_associated_text_includes_a_regular_key_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            send_letter(terminal, 0)
            self.assertEqual(terminal.read_input(), b"\x1b[97;;97u")

    def test_associated_text_includes_shifted_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            send_letter(terminal, SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;2;65u")

    def test_associated_text_omits_a_control_chord(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            send_letter(terminal, CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[97;5u")

    def test_associated_text_is_absent_from_a_functional_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            terminal.frontend_key_event(KEY_ESCAPE, PRESS)
            self.assertEqual(terminal.read_input(), b"\x1b[27u")

    def test_associated_text_is_absent_from_a_release_event(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=26u")
            send_letter_event(terminal, 0, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[97;1:3u")

    def test_associated_text_includes_a_digit(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            terminal.layout_key("5", "5", "5")
            terminal.frontend_text_event("5")
            self.assertEqual(terminal.read_input(), b"\x1b[53;;53u")

    def test_associated_text_includes_a_shifted_digit_symbol(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=24u")
            terminal.layout_key(
                "5", "5", "5", modifiers=SHIFT, shifted="%"
            )
            terminal.frontend_text_event("%", modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[53;2;37u")

    def test_alternate_keys_include_a_shifted_letter(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=12u")
            send_letter(terminal, SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97:65;2u")

    def test_alternate_keys_omit_an_unshifted_duplicate(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=12u")
            send_letter(terminal, 0)
            self.assertEqual(terminal.read_input(), b"\x1b[97u")

    def test_alternate_keys_include_a_shifted_digit_symbol(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=12u")
            terminal.layout_key(
                "5", "5", "5", modifiers=SHIFT, shifted="%"
            )
            terminal.frontend_text_event("%", modifiers=SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[53:37;2u")

    def test_alternate_keys_are_absent_from_functional_keys(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=12u")
            terminal.frontend_key_event(
                KEY_ESCAPE, PRESS, modifiers=SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x1b[27;2u")

    def test_alternate_and_associated_fields_coexist_on_shifted_letters(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=28u")
            send_letter(terminal, SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97:65;2;65u")

    def test_alternate_fields_survive_release_without_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=30u")
            send_letter_event(terminal, SHIFT, RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[97:65;2:3u")

    def test_release_is_suppressed_without_report_event_types(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            send_letter_event(terminal, 0, RELEASE)
            self.assertEqual(terminal.read_input(), b"")

    def test_shift_letter_stays_plain_in_disambiguate_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            send_letter(terminal, SHIFT)
            self.assertEqual(terminal.read_input(), b"A")

    def test_control_shift_letter_uses_the_lowercase_key_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            send_letter(terminal, CONTROL | SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;6u")

    def test_dead_key_produces_no_output(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            terminal.frontend_key_event(-1, PRESS)
            self.assertEqual(terminal.read_input(), b"")

    def test_unidentified_key_produces_no_output(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=1u")
            terminal.frontend_key_event(0x7FFFFFFF, PRESS)
            self.assertEqual(terminal.read_input(), b"")

    def test_print_screen_uses_private_use_code_57361(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("PRINT")
            self.assertEqual(terminal.read_input(), b"\x1b[57361u")

    def test_pause_uses_private_use_code_57362(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("PAUSE")
            self.assertEqual(terminal.read_input(), b"\x1b[57362u")

    def test_context_menu_uses_private_use_code_57363(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("MENU")
            self.assertEqual(terminal.read_input(), b"\x1b[57363u")

    def test_media_play_pause_uses_private_use_code_57430(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("MEDIA_PLAY_PAUSE")
            self.assertEqual(terminal.read_input(), b"\x1b[57430u")

    def test_media_stop_uses_private_use_code_57432(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("MEDIA_STOP")
            self.assertEqual(terminal.read_input(), b"\x1b[57432u")

    def test_media_track_next_uses_private_use_code_57435(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("MEDIA_TRACK_NEXT")
            self.assertEqual(terminal.read_input(), b"\x1b[57435u")

    def test_media_track_previous_uses_private_use_code_57436(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("MEDIA_TRACK_PREVIOUS")
            self.assertEqual(terminal.read_input(), b"\x1b[57436u")

    def test_audio_volume_down_uses_private_use_code_57438(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("VOLUME_DOWN")
            self.assertEqual(terminal.read_input(), b"\x1b[57438u")

    def test_audio_volume_up_uses_private_use_code_57439(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("VOLUME_UP")
            self.assertEqual(terminal.read_input(), b"\x1b[57439u")

    def test_audio_volume_mute_uses_private_use_code_57440(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.kitty_special("VOLUME_MUTE")
            self.assertEqual(terminal.read_input(), b"\x1b[57440u")

    def assert_option_as_alt(self, layout, expected, modifiers=ALT):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key(
                layout.upper(), layout, layout, modifiers=modifiers
            )
            self.assertEqual(terminal.read_input(), expected)

    def test_option_f_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("f", b"\x1b[102;3u")

    def test_option_b_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("b", b"\x1b[98;3u")

    def test_option_d_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("d", b"\x1b[100;3u")

    def test_option_n_dead_key_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("n", b"\x1b[110;3u")

    def test_option_e_dead_key_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("e", b"\x1b[101;3u")

    def test_option_u_dead_key_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("u", b"\x1b[117;3u")

    def test_option_5_as_alt_uses_the_physical_digit(self):
        self.assert_option_as_alt("5", b"\x1b[53;3u")

    def test_option_shift_f_as_alt_uses_the_unshifted_physical_letter(self):
        self.assert_option_as_alt("f", b"\x1b[102;4u", ALT | SHIFT)

    def test_control_option_f_as_alt_uses_the_physical_letter(self):
        self.assert_option_as_alt("f", b"\x1b[102;7u", CONTROL | ALT)

    def test_linux_alt_keeps_the_active_layout_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key("A", "a", "a", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;3u")

    def test_linux_azerty_alt_keeps_the_active_layout_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key("A", "a", "q", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[97;3u")

    def test_native_option_composition_remains_when_option_as_alt_is_disabled(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key("F", "ƒ", "f", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[402;3u")

    def test_native_composed_text_remains_when_alt_is_not_pressed(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key("F", "ƒ", "f")
            terminal.frontend_text_event("ƒ")
            self.assertEqual(terminal.read_input(), "ƒ".encode())

    @unittest.expectedFailure
    def test_option_punctuation_with_a_non_letter_dom_code_falls_through(self):
        with Shitty(columns=8, rows=2) as terminal:
            enable_disambiguation(terminal)
            terminal.layout_key(";", ";", ";", modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b[8230;3u")

    def test_option_f_release_reports_the_physical_letter_and_release_event(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=3u")
            terminal.layout_key("F", "f", "f", modifiers=ALT, action=RELEASE)
            self.assertEqual(terminal.read_input(), b"\x1b[102;3:3u")


if __name__ == "__main__":
    unittest.main()

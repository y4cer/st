# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


FUNCTIONAL_KEYS = {
    "F1": (1, b"P"),
    "F2": (1, b"Q"),
    "F3": (13, b"~"),
    "F4": (1, b"S"),
    "F5": (15, b"~"),
    "F6": (17, b"~"),
    "F7": (18, b"~"),
    "F8": (19, b"~"),
    "F9": (20, b"~"),
    "F10": (21, b"~"),
    "F11": (23, b"~"),
    "F12": (24, b"~"),
    **{f"F{number}": (57363 + number, b"u")
       for number in range(13, 36)},
    "KP_0": (57399, b"u"),
    "KP_1": (57400, b"u"),
    "KP_2": (57401, b"u"),
    "KP_3": (57402, b"u"),
    "KP_4": (57403, b"u"),
    "KP_5": (57404, b"u"),
    "KP_6": (57405, b"u"),
    "KP_7": (57406, b"u"),
    "KP_8": (57407, b"u"),
    "KP_9": (57408, b"u"),
    "KP_DOT": (57409, b"u"),
    "KP_SLASH": (57410, b"u"),
    "KP_STAR": (57411, b"u"),
    "KP_MINUS": (57412, b"u"),
    "KP_PLUS": (57413, b"u"),
    "KP_ENTER": (57414, b"u"),
    "KP_EQUAL": (57415, b"u"),
    "KP_COMMA": (57416, b"u"),
    "KP_LEFT": (57417, b"u"),
    "KP_RIGHT": (57418, b"u"),
    "KP_UP": (57419, b"u"),
    "KP_DOWN": (57420, b"u"),
    "KP_PAGE_UP": (57421, b"u"),
    "KP_PAGE_DOWN": (57422, b"u"),
    "KP_HOME": (57423, b"u"),
    "KP_END": (57424, b"u"),
    "KP_INSERT": (57425, b"u"),
    "KP_DELETE": (57426, b"u"),
    "KP_BEGIN": (57427, b"u"),
    "CAPS_LOCK": (57358, b"u"),
    "SCROLL_LOCK": (57359, b"u"),
    "NUM_LOCK": (57360, b"u"),
    "PRINT": (57361, b"u"),
    "PAUSE": (57362, b"u"),
    "MENU": (57363, b"u"),
    "MEDIA_PLAY": (57428, b"u"),
    "MEDIA_PAUSE": (57429, b"u"),
    "MEDIA_PLAY_PAUSE": (57430, b"u"),
    "MEDIA_REVERSE": (57431, b"u"),
    "MEDIA_STOP": (57432, b"u"),
    "MEDIA_FAST_FORWARD": (57433, b"u"),
    "MEDIA_REWIND": (57434, b"u"),
    "MEDIA_TRACK_NEXT": (57435, b"u"),
    "MEDIA_TRACK_PREVIOUS": (57436, b"u"),
    "MEDIA_RECORD": (57437, b"u"),
    "VOLUME_DOWN": (57438, b"u"),
    "VOLUME_UP": (57439, b"u"),
    "VOLUME_MUTE": (57440, b"u"),
}


class KittyKeyboardMatrixTest(unittest.TestCase):
    def test_each_flag_can_be_set_added_removed_and_queried(self):
        with Shitty(columns=8, rows=2) as terminal:
            for flag in (1, 2, 4, 8, 16):
                with self.subTest(flag=flag):
                    terminal.write(
                        f"\x1b[={flag};1u\x1b[?u"
                        f"\x1b[={31 ^ flag};2u\x1b[?u"
                        f"\x1b[={flag};3u\x1b[?u".encode()
                    )
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1b[?{flag}u\x1b[?31u\x1b[?{31 ^ flag}u".encode(),
                    )

    def test_unknown_flags_are_masked_and_invalid_modes_are_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[=3u\x1b[=32;2u\x1b[?u"
                b"\x1b[=8;0u\x1b[?u\x1b[=8;4u\x1b[?u"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[?3u\x1b[?3u\x1b[?3u",
            )

    def test_functional_key_matrix_uses_canonical_codes(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>9u")
            for name, (code, final) in FUNCTIONAL_KEYS.items():
                with self.subTest(key=name):
                    terminal.kitty_special(name, modifiers=5)
                    self.assertEqual(
                        terminal.read_input(),
                        b"\x1b[" + str(code).encode() + b";6" + final,
                    )

    def test_press_repeat_release_for_text_and_functional_keys(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>3u")
            for event in (1, 2, 3):
                terminal.kitty_key(ord("a"), modifiers=4, event=event)
                terminal.kitty_special("UP", modifiers=4, event=event)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[97;5u\x1b[1;5A"
                b"\x1b[97;5:2u\x1b[1;5:2A"
                b"\x1b[97;5:3u\x1b[1;5:3A",
            )

    def test_release_is_suppressed_without_event_type_flag(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_key(ord("a"), event=3)
            terminal.kitty_special("UP", event=3)
            self.assertEqual(terminal.read_input(), b"")

    def test_enter_tab_backspace_stay_legacy_without_report_all(self):
        for flags in (1, 2, 4, 16, 1 | 2 | 4 | 16):
            with self.subTest(flags=flags):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(f"\x1b[>{flags}u".encode())
                    for event in (1, 2, 3):
                        terminal.kitty_special("RETURN", event=event)
                        terminal.kitty_special("TAB", event=event)
                        terminal.kitty_special("BACKSPACE", event=event)
                    self.assertEqual(
                        terminal.read_input(), b"\r\t\x7f\r\t\x7f"
                    )

    def test_report_all_makes_enter_tab_backspace_canonical(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>26u")
            for event in (1, 2, 3):
                terminal.kitty_special("RETURN", event=event)
                terminal.kitty_special("TAB", event=event)
                terminal.kitty_special("BACKSPACE", event=event)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[13u\x1b[9u\x1b[127u"
                b"\x1b[13;1:2u\x1b[9;1:2u\x1b[127;1:2u"
                b"\x1b[13;1:3u\x1b[9;1:3u\x1b[127;1:3u",
            )

    def test_alternate_key_fields_omit_redundant_values(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>5u")
            terminal.kitty_key(97, shifted=65, base=113, modifiers=1)
            terminal.kitty_key(97, base=113)
            terminal.kitty_key(97, shifted=97, base=97)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[97:65:113;2u\x1b[97::113u\x1b[97u",
            )

    def test_associated_text_follows_shift_and_excludes_control_codes(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>24u")
            terminal.kitty_key(97, shifted=65)
            terminal.kitty_key(97, shifted=65, modifiers=1)
            terminal.kitty_key(1)
            terminal.kitty_key(127)
            terminal.kitty_key(160)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[97;;97u\x1b[97;2;65u"
                b"\x1b[1u\x1b[127u\x1b[160;;160u",
            )

    def test_stack_is_lifo_and_pop_count_is_honored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[>1u\x1b[>2u\x1b[>4u"
                b"\x1b[<2u\x1b[?u\x1b[<u\x1b[?u"
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b[?1u\x1b[?0u"
            )

    def test_stack_underflow_resets_flags(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=7u\x1b[<99u\x1b[?u")
            self.assertEqual(terminal.read_input(), b"\x1b[?0u")

    def test_stack_depth_sixteen_discards_oldest_entry(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=31u")
            for value in range(1, 18):
                terminal.write(f"\x1b[>{value}u".encode())
            terminal.write(b"\x1b[<16u\x1b[?u")
            self.assertEqual(terminal.read_input(), b"\x1b[?1u")

    def test_main_and_alternate_stacks_are_independent_and_persistent(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[>1u"
                b"\x1b[?47h\x1b[>2u\x1b[>4u\x1b[?u"
                b"\x1b[?47l\x1b[?u"
                b"\x1b[?47h\x1b[<u\x1b[?u"
                b"\x1b[?47l\x1b[<u\x1b[?u"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[?4u\x1b[?1u\x1b[?2u\x1b[?0u",
            )


if __name__ == "__main__":
    unittest.main()

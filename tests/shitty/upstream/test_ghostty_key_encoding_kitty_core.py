# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "KittySequence: backspace",
    "KittySequence: text",
    "KittySequence: text with control characters",
    "KittySequence: special no mods",
    "KittySequence: special mods only",
    "KittySequence: special mods and event",
    "kitty: plain text",
    "kitty: repeat with just disambiguate",
    "kitty: enter, backspace, tab",
    "kitty: shift+backspace emits CSI u",
    "kitty: shift+enter emits CSI u",
    "kitty: shift+tab emits CSI u",
    "kitty: enter with all flags",
    "kitty: ctrl with all flags",
    "kitty: ctrl release with ctrl mod set",
    "kitty: delete",
    "kitty: composing with no modifier",
    "kitty: composing with modifier",
    "kitty: composed text with report all",
    "kitty: shift+a on US keyboard",
)


class GhosttyKeyEncodingKittyCoreTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_kitty_backspace_sequence_encodes_press_release_and_shift(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>10u")
            terminal.kitty_special("BACKSPACE")
            terminal.kitty_special("BACKSPACE", event=3)
            terminal.kitty_special("BACKSPACE", modifiers=1)

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[127u\x1b[127;1:3u\x1b[127;2u",
            )

    def test_kitty_associated_text_sequence_tracks_event_and_shift(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>26u")
            terminal.kitty_key(ord("a"))
            terminal.kitty_key(ord("a"), event=3)
            terminal.kitty_key(ord("a"), shifted=ord("A"), modifiers=1)

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[97;;97u\x1b[97;1:3u\x1b[97;2;65u",
            )

    def test_kitty_associated_text_omits_control_characters(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>24u")
            terminal.kitty_key(ord("A"))
            terminal.kitty_key(10)

            self.assertEqual(terminal.read_input(), b"\x1b[65;;65u\x1b[10u")

    def test_kitty_special_without_modifiers_uses_short_csi(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("UP")

            self.assertEqual(terminal.read_input(), b"\x1b[A")

    def test_kitty_special_with_modifiers_uses_parameterized_csi(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("UP", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[1;2A")

    def test_kitty_special_release_appends_the_event_subparameter(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>3u")
            terminal.kitty_special("UP", modifiers=1, event=3)

            self.assertEqual(terminal.read_input(), b"\x1b[1;2:3A")

    def test_kitty_plain_text_stays_plain_with_disambiguation_only(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            for character in "abcd":
                terminal.frontend_text_event(character)

            self.assertEqual(terminal.read_input(), b"abcd")

    @unittest.expectedFailure
    def test_kitty_text_repeat_stays_plain_without_event_reporting(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_key(ord("a"), event=2)

            self.assertEqual(terminal.read_input(), b"a")

    @unittest.expectedFailure
    def test_kitty_legacy_controls_and_report_all_release_boundaries(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>3u")
            terminal.kitty_special("RETURN")
            terminal.kitty_special("BACKSPACE")
            terminal.kitty_special("TAB")
            terminal.kitty_special("RETURN", event=3)
            terminal.kitty_special("BACKSPACE", event=3)
            terminal.kitty_special("TAB", event=3)
            self.assertEqual(terminal.read_input(), b"\r\x7f\t")

        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>10u")
            terminal.kitty_special("RETURN", event=3)
            terminal.kitty_special("BACKSPACE", event=3)
            terminal.kitty_special("TAB", event=3)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[13;1:3u\x1b[127;1:3u\x1b[9;1:3u",
            )

        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>3u\x1b[?67h")
            terminal.kitty_special("BACKSPACE")

            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_kitty_shift_backspace_uses_csi_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("BACKSPACE", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[127;2u")

    def test_kitty_shift_enter_uses_csi_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("RETURN", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[13;2u")

    def test_kitty_shift_tab_uses_csi_u(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("TAB", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[9;2u")

    def test_kitty_enter_with_all_flags_is_canonical(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.kitty_special("RETURN")

            self.assertEqual(terminal.read_input(), b"\x1b[13u")

    def test_kitty_control_key_with_all_flags_has_functional_code(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.kitty_special("LEFT_CONTROL", modifiers=4)

            self.assertEqual(terminal.read_input(), b"\x1b[57442;5u")

    def test_kitty_control_release_retains_control_modifier(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.kitty_special("LEFT_CONTROL", modifiers=4, event=3)

            self.assertEqual(terminal.read_input(), b"\x1b[57442;5:3u")

    def test_kitty_delete_keeps_legacy_functional_sequence(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("DELETE")

            self.assertEqual(terminal.read_input(), b"\x1b[3~")

    def test_kitty_composition_preview_without_modifier_writes_no_input(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.preedit("a", 0, 1)

            self.assertEqual(terminal.read_input(), b"")

    def test_kitty_modifier_is_reported_while_composition_is_visible(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>9u")
            terminal.preedit("a", 0, 1)
            terminal.kitty_special("LEFT_SHIFT", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[57441;2u")

    def test_kitty_composed_text_stays_utf8_with_report_all(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.frontend_text_event("û")

            self.assertEqual(terminal.read_input(), "û".encode())

    def test_kitty_shift_a_reports_the_shifted_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>5u")
            terminal.kitty_key(ord("a"), shifted=ord("A"), modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[97:65;2u")


if __name__ == "__main__":
    unittest.main()

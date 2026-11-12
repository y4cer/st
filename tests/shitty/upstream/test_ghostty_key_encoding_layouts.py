# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "kitty: matching unshifted codepoint",
    "kitty: report alternates with caps",
    "kitty: report alternates colon (shift+';')",
    "kitty: report alternates with ru layout",
    "kitty: report alternates with ru layout shifted",
    "kitty: report alternates with ru layout caps lock",
    "kitty: report alternates with hu layout release",
    "kitty: up arrow with utf8",
    "kitty: shift+tab",
    "kitty: left shift",
    "kitty: left shift with report all",
    "kitty: report associated with alt text on macOS with option",
    "kitty: report associated with alt text on macOS with alt",
    "kitty: report associated with modifiers",
    "kitty: report associated",
    "kitty: report associated on release",
    "kitty: alternates omit control characters",
    "kitty: enter with utf8 (dead key state)",
    "kitty: keypad number",
    "kitty: backspace with utf8 (dead key state)",
)


class GhosttyKeyEncodingLayoutsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_matching_layout_codepoint_keeps_distinct_base_layout_field(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>5u")
            terminal.layout_key("A", "A", "a", modifiers=1)
            terminal.frontend_text_event("A", modifiers=1)

            self.assertEqual(terminal.read_input(), b"A")

    @unittest.expectedFailure
    def test_caps_lock_reports_uppercase_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("J", "j", "j", modifiers=16)
            terminal.frontend_text_event("J", modifiers=16)

            self.assertEqual(terminal.read_input(), b"\x1b[106;65;74u")

    def test_shift_semicolon_reports_colon_as_alternate_and_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key(";", ";", ";", modifiers=1)
            terminal.frontend_text_event(":", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[59:58;2;58u")

    def test_russian_layout_reports_the_pc101_base_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key(";", "ч", ";")
            terminal.frontend_text_event("ч")

            self.assertEqual(terminal.read_input(), b"\x1b[1095::59;;1095u")

    def test_shifted_russian_layout_reports_all_three_key_fields(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key(";", "ч", ";", modifiers=1)
            terminal.frontend_text_event("Ч", modifiers=1)

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[1095:1063:59;2;1063u",
            )

    @unittest.expectedFailure
    def test_caps_locked_russian_layout_keeps_shift_out_of_modifiers(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key(";", "ч", ";", modifiers=16)
            terminal.frontend_text_event("Ч", modifiers=16)

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[1095::59;65;1063u",
            )

    def test_hungarian_layout_release_keeps_base_layout_field(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.layout_key("[", "ő", "[", modifiers=2, action=0)

            self.assertEqual(terminal.read_input(), b"\x1b[337::91;5:3u")

    def test_arrow_ignores_spurious_control_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u")
            terminal.kitty_special("UP")

            self.assertEqual(terminal.read_input(), b"\x1b[A")

    def test_shift_tab_stays_csi_u_when_alternates_are_requested(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>5u")
            terminal.kitty_special("TAB", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[9;2u")

    def test_modifier_key_is_silent_without_report_all(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>5u")
            terminal.kitty_special("LEFT_SHIFT")

            self.assertEqual(terminal.read_input(), b"")

    def test_modifier_key_has_a_functional_code_with_report_all(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>9u")
            terminal.kitty_special("LEFT_SHIFT")

            self.assertEqual(terminal.read_input(), b"\x1b[57441u")

    @unittest.expectedFailure
    def test_native_macos_option_text_is_associated_with_the_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("W", "w", "w", modifiers=4)
            terminal.frontend_text_event("∑", modifiers=4)

            self.assertEqual(terminal.read_input(), b"\x1b[119;3;8721u")

    @unittest.expectedFailure
    def test_macos_alt_policy_controls_whether_text_is_associated(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("W", "w", "w")
            terminal.frontend_text_event("∑")
            self.assertEqual(terminal.read_input(), b"\x1b[119;;8721u")

        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("W", "w", "w", modifiers=4)
            terminal.frontend_text_event("∑", modifiers=4)
            self.assertEqual(terminal.read_input(), b"\x1b[119;3u")

    def test_control_modifier_suppresses_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("J", "j", "j", modifiers=2)

            self.assertEqual(terminal.read_input(), b"\x1b[106;5u")

    def test_shifted_key_reports_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>29u")
            terminal.layout_key("J", "j", "j", modifiers=1)
            terminal.frontend_text_event("J", modifiers=1)

            self.assertEqual(terminal.read_input(), b"\x1b[106:74;2;74u")

    def test_release_reports_alternate_but_no_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.kitty_key(106, shifted=74, modifiers=1, event=3)

            self.assertEqual(terminal.read_input(), b"\x1b[106:74;2:3u")

    def test_delete_omits_control_character_alternates(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>13u")
            terminal.kitty_special("DELETE")

            self.assertEqual(terminal.read_input(), b"\x1b[3~")

    def test_dead_key_commit_after_enter_is_plain_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>13u")
            terminal.preedit("A", 0, 1)
            terminal.frontend_text_event("A")

            self.assertEqual(terminal.read_input(), b"A")

    @unittest.expectedFailure
    def test_keypad_number_embeds_its_associated_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.frontend_key_event(321, 1)
            terminal.frontend_text_event("1")

            self.assertEqual(terminal.read_input(), b"\x1b[57400;;49u")

    @unittest.expectedFailure
    def test_backspace_with_dead_key_text_emits_nothing(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.preedit("A", 0, 1)
            terminal.frontend_key_event(259, 1)
            terminal.frontend_text_event("A")

            self.assertEqual(terminal.read_input(), b"")


if __name__ == "__main__":
    unittest.main()

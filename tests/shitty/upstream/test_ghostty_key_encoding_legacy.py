# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "legacy: backspace with utf8 (dead key state)",
    "kitty: backspace (DECBKM reset) (report_all: true)",
    "kitty: backspace (DECBKM set) (report_all: true)",
    "legacy: enter with utf8 (dead key state)",
    "legacy: esc with utf8 (dead key state)",
    "legacy: ctrl+shift+minus (underscore on US)",
    "legacy: ctrl+alt+c",
    "legacy: alt+c",
    "legacy: alt+e only unshifted",
    "legacy: alt+x macos",
    "legacy: shift+alt+. macos",
    "legacy: alt+ф",
    "legacy: ctrl+c",
    "legacy: ctrl+space",
    "legacy: ctrl+shift+backspace",
    "legacy: backspace (DECBKM reset)",
    "legacy: backspace (DECBKM reset, with ctrl)",
    "legacy: backspace (DECBKM set)",
    "legacy: backspace (DECBKM set, with ctrl)",
    "legacy: ctrl+shift+char with modify other state 2",
)


class GhosttyKeyEncodingLegacyTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    @unittest.expectedFailure
    def test_legacy_backspace_with_dead_key_text_emits_nothing(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.preedit("A", 0, 1)
            terminal.frontend_key_event(259, 1)
            terminal.frontend_text_event("A")

            self.assertEqual(terminal.read_input(), b"")

    def test_kitty_report_all_backspace_is_canonical_with_decbkm_reset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u")
            terminal.kitty_special("BACKSPACE")

            self.assertEqual(terminal.read_input(), b"\x1b[127u")

    def test_kitty_report_all_backspace_is_canonical_with_decbkm_set(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>31u\x1b[?67h")
            terminal.kitty_special("BACKSPACE")

            self.assertEqual(terminal.read_input(), b"\x1b[127u")

    @unittest.expectedFailure
    def test_legacy_enter_with_dead_key_text_emits_only_the_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.preedit("A", 0, 1)
            terminal.frontend_key_event(257, 1)
            terminal.frontend_text_event("A")

            self.assertEqual(terminal.read_input(), b"A")

    @unittest.expectedFailure
    def test_legacy_escape_with_dead_key_text_emits_only_the_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.preedit("A", 0, 1)
            terminal.frontend_key_event(256, 1)
            terminal.frontend_text_event("A")

            self.assertEqual(terminal.read_input(), b"A")

    def test_legacy_ctrl_shift_minus_emits_unit_separator(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("-", "-", "-", modifiers=3)

            self.assertEqual(terminal.read_input(), b"\x1f")

    def test_legacy_ctrl_alt_c_prefixes_escape_to_etx(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=6)

            self.assertEqual(terminal.read_input(), b"\x1b\x03")

    def test_legacy_alt_c_prefixes_escape_to_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=4)
            terminal.frontend_text_event("c", modifiers=4)

            self.assertEqual(terminal.read_input(), b"\x1bc")

    @unittest.expectedFailure
    def test_legacy_alt_key_can_fall_back_to_its_unshifted_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("E", "e", "e", modifiers=4)

            self.assertEqual(terminal.read_input(), b"\x1be")

    @unittest.expectedFailure
    def test_legacy_macos_alt_uses_physical_key_when_option_is_alt(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=4)
            terminal.frontend_text_event("≈", modifiers=4)

            self.assertEqual(terminal.read_input(), b"\x1bc")

    def test_legacy_macos_shift_alt_period_uses_shifted_ascii_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(".", ".", ".", modifiers=5)
            terminal.frontend_text_event(">", modifiers=5)

            self.assertEqual(terminal.read_input(), b"\x1b>")

    @unittest.expectedFailure
    def test_legacy_alt_non_ascii_text_has_no_escape_prefix(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("F", "ф", "f", modifiers=4)
            terminal.frontend_text_event("ф", modifiers=4)

            self.assertEqual(terminal.read_input(), "ф".encode())

    def test_legacy_ctrl_c_emits_etx(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=2)

            self.assertEqual(terminal.read_input(), b"\x03")

    def test_legacy_ctrl_space_emits_nul(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(ord(" "), 1, modifiers=2)

            self.assertEqual(terminal.read_input(), b"\x00")

    def test_legacy_ctrl_shift_backspace_emits_bs(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(259, 1, modifiers=3)

            self.assertEqual(terminal.read_input(), b"\x08")

    def test_legacy_decbkm_reset_backspace_emits_del(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.key("BACKSPACE")

            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_legacy_decbkm_reset_ctrl_backspace_emits_bs(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_key_event(259, 1, modifiers=2)

            self.assertEqual(terminal.read_input(), b"\x08")

    def test_legacy_decbkm_set_backspace_emits_bs(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?67h")
            terminal.key("BACKSPACE")

            self.assertEqual(terminal.read_input(), b"\x08")

    def test_legacy_decbkm_set_ctrl_backspace_emits_del(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?67h")
            terminal.frontend_key_event(259, 1, modifiers=2)

            self.assertEqual(terminal.read_input(), b"\x7f")

    def test_modify_other_keys_two_encodes_ctrl_shift_character(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>4;2m")
            terminal.char("H", modifiers=3)

            self.assertEqual(terminal.read_input(), b"\x1b[27;6;72~")


if __name__ == "__main__":
    unittest.main()

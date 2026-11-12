# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Key encoding under non-Latin and Latin-swapped keyboard layouts.

Every event carries two codepoints: what the active layout prints and
what the same physical key prints in the user's Latin layout. The
matrix pins which layer each encoding mode sends to the application:
legacy control bytes, modifyOtherKeys, and the kitty protocol with its
flag combinations.
"""

import unittest

from harness import Shitty


SHIFT = 0x0001
CONTROL = 0x0002
ALT = 0x0004

PRESS = 1
RELEASE = 0

# Physical key -> what a Russian layout prints there.
RUSSIAN = {
    "C": "с",
    "D": "в",
    "V": "м",
}


def cyr(char):
    return char.encode()


class LegacyLayoutTest(unittest.TestCase):
    def test_control_byte_comes_from_the_base_layout(self):
        # Ctrl+<physical C> on a Russian layout is SIGINT's 0x03, exactly
        # as if the Latin layout were active; the Cyrillic layer has no
        # control byte to offer.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            terminal.layout_key("D", RUSSIAN["D"], "d", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x03\x04")

    def test_control_shift_keeps_the_base_control_byte(self):
        # Probed on D: Ctrl+Shift+C is the Copy binding on Linux and
        # never reaches the encoder there.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key(
                "D", RUSSIAN["D"], "d", modifiers=CONTROL | SHIFT
            )
            self.assertEqual(terminal.read_input(), b"\x04")

    def test_typing_sends_the_layout_text(self):
        # Plain typing is the active layout's business: the key event
        # produces nothing, the text event delivers the Cyrillic letter.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("D", RUSSIAN["D"], "d")
            terminal.frontend_text_event(RUSSIAN["D"])
            self.assertEqual(terminal.read_input(), cyr(RUSSIAN["D"]))

    def test_alt_prefixes_escape_to_the_layout_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("D", RUSSIAN["D"], "d", modifiers=ALT)
            terminal.frontend_text_event(RUSSIAN["D"], modifiers=ALT)
            self.assertEqual(terminal.read_input(), b"\x1b" + cyr(RUSSIAN["D"]))

    def test_latin_layouts_keep_their_own_control_bytes(self):
        # QWERTZ swaps Z and Y: the key labeled Z is the physical Y. The
        # user pressing Ctrl+Z must get 0x1a, not the positional 0x19 -
        # when the active layout already prints ASCII, it wins over the
        # base layout (kitty's legacy rule).
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("Y", "z", "y", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1a")

    def test_ascii_layout_is_unaffected(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x03")


class ModifyOtherKeysLayoutTest(unittest.TestCase):
    def test_reports_the_base_layout_codepoint(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>4;2m")
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[27;5;99~")


class KittyLayoutTest(unittest.TestCase):
    def enable(self, terminal, flags):
        terminal.write(b"\x1b[>%du" % flags)

    def test_primary_is_the_layout_codepoint(self):
        # Flags 1 (disambiguate): the packet names the key the layout
        # prints; no alternate field without flag 4.
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 1)
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            self.assertEqual(
                terminal.read_input(), b"\x1b[%d;5u" % ord(RUSSIAN["C"])
            )

    def test_alternate_field_carries_the_base_layout(self):
        # Flags 1|4 (report alternate keys): the base-layout key rides in
        # the second alternate slot - ESC[layout::base;modsu - which is
        # what applications must match shortcuts against.
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 5)
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[%d::99;5u" % ord(RUSSIAN["C"]),
            )

    def test_alternate_is_omitted_when_it_repeats_the_primary(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 5)
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[99;5u")

    def test_latin_swapped_layout_reports_both_layers(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 5)
            terminal.layout_key("Y", "z", "y", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x1b[122::121;5u")

    def test_release_events_report_the_same_layers(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 1 | 2)
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            terminal.layout_key(
                "C", RUSSIAN["C"], "c", modifiers=CONTROL, action=RELEASE
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[%d;5u\x1b[%d;5:3u"
                % (ord(RUSSIAN["C"]), ord(RUSSIAN["C"])),
            )

    def test_plain_typing_stays_text(self):
        # Without report-all-keys the unmodified letter is delivered as
        # text, not as a CSI-u packet.
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 1)
            terminal.layout_key("D", RUSSIAN["D"], "d")
            terminal.frontend_text_event(RUSSIAN["D"])
            self.assertEqual(terminal.read_input(), cyr(RUSSIAN["D"]))

    def test_report_all_keys_packs_the_letter(self):
        # Flags 8: even plain typing becomes CSI-u with the layout
        # codepoint as the key.
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 8)
            terminal.layout_key("D", RUSSIAN["D"], "d")
            terminal.frontend_text_event(RUSSIAN["D"])
            self.assertEqual(
                terminal.read_input(), b"\x1b[%du" % ord(RUSSIAN["D"])
            )

    def test_pop_restores_legacy_translation(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.enable(terminal, 5)
            terminal.write(b"\x1b[<u")
            terminal.layout_key("C", RUSSIAN["C"], "c", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x03")


if __name__ == "__main__":
    unittest.main()

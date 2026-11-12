# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


DEC_SPECIAL_SOURCE = b"`abcdefghijklmnopqrstuvwxyz{|}~"
DEC_SPECIAL_TEXT = "◆▒␉␌␍␊°±␤␋┘┐┌└┼⎺⎻─⎼⎽├┤┴┬│≤≥π≠£·"

NRC_CASES = (
    (b"4", b"#@[\\]{|}~", "£¾ĳ½|¨ƒ¼´"),
    (b"5", b"[\\]^`{|}~", "ÄÖÅÜéäöåü"),
    (b"R", b"#@[\\]{|}~", "£à°ç§éùè¨"),
    (b"9", b"@[\\]^`{|}~", "àâçêîôéùèû"),
    (b"K", b"@[\\]{|}~", "§ÄÖÜäöüß"),
    (b"Y", b"#@[\\]`{|}~", "£§°çéùàòèì"),
    (b"E", b"@[\\]^`{|}~", "ÄÆØÅÜäæøåü"),
    (b"%6", b"[\\]{|}", "ÃÇÕãçõ"),
    (b"Z", b"#@[\\]{|}", "£§¡Ñ¿°ñç"),
    (b"7", b"@[\\]^`{|}~", "ÉÄÖÅÜéäöåü"),
    (b"=", b"#@[\\]^_`{|}~", "ùàéçêîèôäöüû"),
    (b"%3", b"@[\\]^`{|}~", "ŽŠĐĆČžšđćč"),
    (b"%2", b"&@[\\]^`{|}~", "ğİŞÖÇÜĞşöçü"),
)


def line_after(output, columns=128):
    with Shitty(columns=columns, rows=2) as terminal:
        terminal.write(output)
        return terminal.snapshot().lines[0].rstrip()


class UnicodeCharsetMatrixTest(unittest.TestCase):
    def test_designation_and_invocation_do_not_damage_the_screen(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0\x1b*0\x1b+0")
            self.assertEqual(terminal.last_update(), (0, 0))
            terminal.write(b"\x0e")
            self.assertEqual(terminal.last_update(), (0, 0))
            terminal.write(b"`")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "◆")

    def test_all_g_slots_can_be_designated_and_locked_into_gl(self):
        cases = (
            (b"\x1b(0", b""),
            (b"\x1b)0", b"\x0e"),
            (b"\x1b*0", b"\x1bn"),
            (b"\x1b+0", b"\x1bo"),
        )
        for designation, invocation in cases:
            with self.subTest(designation=designation):
                self.assertEqual(line_after(designation + invocation + b"lqk"), "┌─┐")

    def test_si_and_so_switch_persistently_between_g0_and_g1(self):
        self.assertEqual(
            line_after(b"\x1b(B\x1b)0A\x0eqx\x0fB"),
            "A─│B",
        )

    def test_seven_bit_single_shifts_are_one_shot(self):
        self.assertEqual(
            line_after(b"\x1b*0\x1b+0\x1bNqA\x1bOxB"),
            "─A│B",
        )

    def test_eight_bit_single_shifts_are_one_shot(self):
        self.assertEqual(
            line_after(b"\x1b*0\x1b+0\x8eqA\x8fxB"),
            "─A│B",
        )

    def test_all_right_locking_shifts_invoke_94_character_sets(self):
        cases = (
            (b"\x1b)0\x1b~",),
            (b"\x1b*0\x1b}",),
            (b"\x1b+0\x1b|",),
        )
        for (prefix,) in cases:
            with self.subTest(prefix=prefix):
                self.assertEqual(line_after(prefix + bytes((0xF1,))), "─")

    def test_gl_and_gr_invocations_are_independent(self):
        self.assertEqual(
            line_after(b"\x1b(0\x1b)A\x1b~q" + bytes((0xA3,)) + b"x"),
            "─£│",
        )

    def test_iso_latin1_96_set_can_be_invoked_from_g1_g2_and_g3(self):
        cases = (
            b"\x1b-A\x1b~",
            b"\x1b.A\x1b}",
            b"\x1b/A\x1b|",
        )
        for prefix in cases:
            with self.subTest(prefix=prefix):
                self.assertEqual(line_after(prefix + bytes((0xA0, 0xA3, 0xFF))), " £ÿ")

    def test_uk_charset_changes_only_number_sign(self):
        self.assertEqual(line_after(b"\x1b(A!#@[]{}~"), "!£@[]{}~")

    def test_complete_dec_special_graphics_mapping(self):
        self.assertEqual(
            line_after(b"\x1b(0" + DEC_SPECIAL_SOURCE),
            DEC_SPECIAL_TEXT,
        )

    def test_dec_technical_mapping_in_gl_and_gr(self):
        source = bytes(range(0x21, 0x7f))
        expected = (
            "⎷┌─⌠⌡│⎡⎣⎤⎦⎛⎝⎞⎠⎨⎬" + 11 * " " + "≤≠≥∫"
            "∴∝∞÷Δ∇ΦΓ∼≃Θ×Λ⇔⇒≡ΠΨ Σ  √ΩΞΥ⊂⊃∩∪∧∨"
            "¬αβχδεφγηιθκλ ν∂πψρστ ƒωξυζ←↑→↓"
        )
        self.assertEqual(line_after(b"\x1b(>" + source), expected)
        self.assertEqual(
            line_after(b"\x1b)>\x1b~" + bytes(ch | 0x80 for ch in source)),
            expected,
        )

    def test_dec_supplemental_and_user_preferred_sets_match(self):
        high = bytes((0xA1, 0xA3, 0xD7, 0xDD, 0xF7, 0xFD))
        for designation in (b"\x1b)%5", b"\x1b)<"):
            with self.subTest(designation=designation):
                self.assertEqual(line_after(designation + b"\x1b~" + high), "¡£ŒŸœÿ")

    def test_every_nrc_replacement_is_applied(self):
        for designation, source, expected in NRC_CASES:
            with self.subTest(designation=designation):
                self.assertEqual(
                    line_after(b"\x1b[?42h\x1b(" + designation + source),
                    expected,
                )

    def test_full_alphabetic_nrc_sets_are_applied(self):
        cases = (
            (b'">', b"abcdefghijklmnopqrstuvwx", "ΑΒΓΔΕΖΗΘΙΚΛΜΝΧΟΠΡΣΤΥΦΞΨΩ"),
            (b"%=", b"`abcdefghijklmnopqrstuvwxyz", "אבגדהוזחטיךכלםמןנסעףפץצקרשת"),
            (b"&5", b"`abcdefghijklmnopqrstuvwxyz{|}~", "ЮАБЦДЕФГХИЙКЛМНОПЯРСТУЖВЬЫЗШЭЩЧ"),
        )
        for designation, source, expected in cases:
            with self.subTest(designation=designation):
                self.assertEqual(
                    line_after(b"\x1b[?42h\x1b(" + designation + source),
                    expected,
                )

    def test_nrc_designation_is_ascii_when_decnrcm_is_disabled(self):
        for designation, source, _ in NRC_CASES:
            with self.subTest(designation=designation):
                self.assertEqual(
                    line_after(b"\x1b[?42l\x1b(" + designation + source),
                    source.decode("ascii"),
                )

    def test_nrc_works_through_gl_and_gr_locking_shifts(self):
        cases = (
            b"\x1b)K\x0e@",
            b"\x1b*K\x1bn@",
            b"\x1b+K\x1bo@",
            b"\x1b)K\x1b~\xc0",
            b"\x1b*K\x1b}\xc0",
            b"\x1b+K\x1b|\xc0",
        )
        for sequence in cases:
            with self.subTest(sequence=sequence):
                self.assertEqual(line_after(b"\x1b[?42h" + sequence), "§")

    def test_dec_save_and_restore_cursor_restores_charset_state(self):
        self.assertEqual(
            line_after(b"\x1b(0\x1b7\x1b(Bq\x1b8q"),
            "─",
        )

    def test_soft_and_hard_reset_restore_default_charset_state(self):
        for reset in (b"\x1b[!p", b"\x1bc"):
            with self.subTest(reset=reset):
                self.assertEqual(line_after(b"\x1b(0" + reset + b"q"), "q")

    def test_hard_reset_discards_an_incomplete_utf8_character(self):
        self.assertEqual(line_after(b"\xe1\x1bcA"), "A")

    def test_vt52_graphics_toggle_and_ansi_return(self):
        self.assertEqual(
            line_after(b"\x1b[?2l\x1bFq\x1bGq\x1b<q"),
            "─qq",
        )

    def test_designation_and_invocation_survive_every_input_boundary(self):
        chunks = (b"\x1b", b"*", b"0", b"\x1b", b"N", b"q", b"A")
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(*chunks)
            self.assertEqual(terminal.snapshot().lines[0][:2], "─A")

    def test_invalid_designation_recovers_without_leaking_state(self):
        self.assertEqual(line_after(b"\x1b(0q\x1b(9qA"), "─qA")

    def test_percent_default_and_utf8_restore_expected_gr_decoding(self):
        self.assertEqual(
            line_after(
                b"\x1b%@" + bytes((0xA3,))
                + b"\x1b|" + bytes((0xE1,))
                + b"\x1b%G" + "é".encode()
            ),
            "£áé",
        )


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class UnicodeTest(unittest.TestCase):
    def test_control_exposes_stateful_utf8_decoder(self):
        with Shitty() as terminal:
            self.assertEqual(terminal.utf8_push(b"A\xc2"), (ord("A"),))
            self.assertEqual(terminal.utf8_push(b"\xa0"), (0xa0,))
            self.assertEqual(
                terminal.utf8_push(b"\xe0!"),
                (0xfffd, ord("!")),
            )

    def test_batched_width_measurement_uses_terminal_parser(self):
        with Shitty(columns=12, rows=2) as terminal:
            self.assertEqual(
                terminal.measure_widths(
                    b"A",
                    "界".encode(),
                    "\U0001f469\u200d\U0001f4bb".encode(),
                ),
                [(1, 0), (2, 0), (2, 0)],
            )

    def test_full_nrcs_family_and_decnrcm(self):
        samples = [
            (b"4", b"#", "£"), (b"5", b"[", "Ä"),
            (b"R", b"@", "à"), (b"9", b"@", "à"),
            (b"K", b"@", "§"), (b"Y", b"[", "°"),
            (b"E", b"[", "Æ"), (b"%6", b"[", "Ã"),
            (b"Z", b"[", "¡"), (b"7", b"@", "É"),
            (b"=", b"#", "ù"), (b'">', b"a", "Α"),
            (b"%=", b"`", "א"), (b"&5", b"`", "Ю"),
            (b"%3", b"@", "Ž"), (b"%2", b"&", "ğ"),
        ]
        with Shitty(columns=len(samples), rows=2) as terminal:
            terminal.write(b"\x1b[?42h")
            for designation, source, _ in samples:
                terminal.write(b"\x1b(" + designation + source)
            self.assertEqual(
                terminal.snapshot().lines[0],
                "".join(expected for _, _, expected in samples),
            )

            terminal.write(b"\x1b[?42l\x1b[2;1H\x1b(4#")
            self.assertEqual(terminal.snapshot().cell(0, 1).char, "#")

    def test_utf8_decoder_survives_every_byte_boundary(self):
        text = "aé界z".encode()
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(*(bytes([byte]) for byte in text))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:5], "aé界 z")
            self.assertTrue(snapshot.cell(2, 0).double_width)

    def test_dec_special_graphics_charset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b(0lqk\x1b(B")
            self.assertEqual(terminal.snapshot().lines[0][:3], "┌─┐")

    def test_single_shift_uses_selected_charset_once(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b*0\x1bNqx")
            self.assertEqual(terminal.snapshot().lines[0][:2], "─x")

    def test_supplementary_plane_codepoint_is_preserved(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write("😀X".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "😀")
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertEqual(snapshot.cell(2, 0).char, "X")

            terminal.select_start(0, 0)
            terminal.select_update(2, 0)
            self.assertEqual(terminal.select_finish(), "😀".encode())

    def test_combining_sequence_is_one_cell_and_copies_verbatim(self):
        text = "e\N{COMBINING ACUTE ACCENT}X"
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(text.encode())
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertEqual(snapshot.cell(0, 0).char, "e")
            self.assertEqual(snapshot.cell(1, 0).char, "X")

            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(
                terminal.select_finish(),
                "e\N{COMBINING ACUTE ACCENT}".encode(),
            )

    def test_pathological_grapheme_is_limited_to_24_codepoints(self):
        payload = ("A" + "\N{COMBINING ACUTE ACCENT}" * 40 + "X").encode()
        for chunks in ((payload,), tuple(bytes((byte,)) for byte in payload)):
            with self.subTest(chunk_count=len(chunks)):
                with Shitty(columns=6, rows=2) as terminal:
                    terminal.write_chunks(*chunks)
                    snapshot = terminal.model_snapshot()
                    self.assertEqual(
                        snapshot.cell(0, 0).grapheme,
                        (ord("A"),) + (0x301,) * 23,
                    )
                    self.assertEqual(snapshot.cell(1, 0).char, "X")

    def test_variation_selector_is_preserved_in_cluster(self):
        text = "\N{HEAVY BLACK HEART}\N{VARIATION SELECTOR-16}"
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write((text + "X").encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 3)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "X")
            terminal.select_start(0, 0)
            terminal.select_update(2, 0)
            self.assertEqual(terminal.select_finish(), text.encode())

    def test_text_variation_selector_narrows_emoji_presentation(self):
        text = "\N{WATCH}\N{VARIATION SELECTOR-15}"
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write((text + "X").encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 2)
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertEqual(snapshot.cell(1, 0).char, "X")

            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), text.encode())

    def test_zwj_emoji_sequence_occupies_one_wide_cluster(self):
        family = "👩\N{ZERO WIDTH JOINER}👩\N{ZERO WIDTH JOINER}👧"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write((family + "X").encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 3)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "X")

            terminal.select_start(0, 0)
            terminal.select_update(2, 0)
            self.assertEqual(terminal.select_finish(), family.encode())

    def test_grapheme_survives_editing_scrollback_and_resize(self):
        cluster = "a\N{COMBINING DIAERESIS}"
        with Shitty(columns=5, rows=2, save_lines=5) as terminal:
            terminal.write((cluster + "bcde\r\n12345\r\n67890").encode())
            terminal.resize(6, 3)
            terminal.page_up()
            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), cluster.encode())

    def test_invalid_utf8_is_replaced_without_aliasing_unicode(self):
        cases = (
            (b"\xc0\xafX", "��X"),
            (b"\xed\xa0\x80X", "���X"),
            (b"\xf4\x90\x80\x80X", "����X"),
            (b"\xf0\x80\x80\x80X", "����X"),
            (b"\xf5\x80\x80\x80X", "����X"),
        )
        for encoded, expected in cases:
            with self.subTest(encoded=encoded):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(encoded)
                    self.assertEqual(
                        terminal.snapshot().lines[0][: len(expected)],
                        expected,
                    )

    def test_gr_stays_utf8_while_gl_is_designated_away(self):
        # GL in DEC line drawing does not disturb GR: high bytes still
        # decode as UTF-8 through the charset path instead of the bulk
        # decoder.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b(0q" + "\u00e9".encode() + b"\x1b(B")
            line = terminal.snapshot().lines[0]
            self.assertEqual(line[1], "\u00e9")
            self.assertNotEqual(line[0], "q")


    def test_a_truncated_sequence_before_a_graphic_set_byte_is_replaced(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b(0\xc3a\x1b(B")
            self.assertEqual(terminal.snapshot().lines[0], "\ufffd▒      ")

    def test_greek_national_replacement_set(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?42h\x1b(\">abcx\x1b(B\x1b[?42l")
            self.assertEqual(terminal.snapshot().lines[0], "ΑΒΓΩ    ")


if __name__ == "__main__":
    unittest.main()

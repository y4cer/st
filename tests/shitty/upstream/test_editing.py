# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class EditingTest(unittest.TestCase):
    def test_repeat_uses_last_character_from_batched_lines(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"A\r\nB\r\n\r\n\x1b[3b")
            self.assertEqual(terminal.snapshot().lines[3], "BBB     ")

    def test_rectangle_origin_tracks_origin_mode_and_both_margin_pairs(self):
        with Shitty(columns=8, rows=4) as terminal:
            self.assertEqual(terminal.rectangle_origin(), (0, 0, 4, 8))
            terminal.write(b"\x1b[2;3r\x1b[?69h\x1b[3;6s\x1b[?6h")
            self.assertEqual(terminal.rectangle_origin(), (1, 2, 3, 6))

    def test_ecma48_spa_epa_mark_only_guarded_characters(self):
        for prefix, spa, epa in (
            (b"", b"\x1bV", b"\x1bW"),
            (b"\x1b%@", b"\x96", b"\x97"),
        ):
            with self.subTest(spa=spa):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(prefix + b"A" + spa + b"BC" + epa + b"D")
                    snapshot = terminal.snapshot()
                    self.assertFalse(snapshot.cell(0, 0).protected)
                    self.assertTrue(snapshot.cell(1, 0).protected)
                    self.assertTrue(snapshot.cell(2, 0).protected)
                    self.assertFalse(snapshot.cell(3, 0).protected)

    def test_ecma48_erm_controls_normal_erasure(self):
        for erase in (b"\x1b[2J", b"\x1b[2K", b"\x1b[8X"):
            with self.subTest(erase=erase), Shitty(columns=8, rows=2) as terminal:
                terminal.write(b"A\x1bVBC\x1bWDE\x1b[H" + erase)
                self.assertEqual(terminal.snapshot().lines[0], " BC     ")

        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x1bVBC\x1bWDE\x1b[H")
            terminal.write(b"\x1b[6h\x1b[2J\x1b[H")
            self.assertEqual(terminal.snapshot().lines[0], "        ")

            terminal.write(b"A\x1bVBC\x1bWDE\x1b[6l\x1b[2J")
            self.assertEqual(terminal.snapshot().lines[0], " BC     ")

    def test_decstr_disables_iso_protection_for_normal_erasure(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1bVc\x1bW\x1b[!p\x1b[H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["   "])

    def test_ecma48_erm_does_not_treat_decsca_as_iso_protection(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1bVISO\x1bW"
                b"\x1b[1\"qDEC\x1b[0\"q"
                b"\x1b[H\x1b[2J"
            )
            self.assertEqual(terminal.snapshot().lines[0], "ISO     ")

    def test_selective_erase_preserves_decsca_protected_cells(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"ab\x1b[1\"qCD\x1b[0\"qefgh"
                b"\x1b[1;4H\x1b[?2K"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "  CD    ")
            self.assertTrue(snapshot.cell(2, 0).protected)
            self.assertFalse(snapshot.cell(0, 0).protected)

    def test_dec_selective_erase_ignores_iso_guarded_areas(self):
        for erase in (b"\x1b[?2J", b"\x1b[?2K", b"\x1b[1;1;1;6${"):
            with self.subTest(erase=erase), Shitty(columns=6, rows=2) as terminal:
                terminal.write(
                    b"A\x1bVB\x1bWC"
                    b"\x1b[1\"qD\x1b[0\"qE"
                    b"\x1b[H" + erase
                )
                self.assertEqual(terminal.snapshot().lines[0], "   D  ")

    def test_selective_display_erase_obeys_cursor_and_defaults(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"A\x1b[1\"qB\x1b[0\"qCDE\r\n"
                b"F\x1b[1\"qG\x1b[0\"qHIJ"
                b"\x1b[1;3H\x1b[?J"
            )
            self.assertEqual(terminal.snapshot().lines, ["AB   ", " G   "])

    def test_rectangular_fill_erase_and_overlap_safe_copy(self):
        with Shitty(columns=6, rows=3) as terminal:
            terminal.write(b"abcdef\x1b[2;1Hghijkl\x1b[3;1Hmnopqr")
            terminal.write(b"\x1b[88;1;2;2;3$x")
            self.assertEqual(
                terminal.snapshot().lines, ["aXXdef", "gXXjkl", "mnopqr"]
            )
            terminal.write(b"\x1b[2;2;2;4$z")
            self.assertEqual(terminal.snapshot().lines[1], "g   kl")
            terminal.write(b"\x1b[1;1;2;3;1;2;3;1$v")
            self.assertEqual(terminal.snapshot().lines[1], "g aXXl")

    def test_rectangular_attribute_change_and_reverse(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"abcdef\x1b[1;2;1;4;1;4;7$r")
            snapshot = terminal.snapshot()
            self.assertTrue(snapshot.cell(1, 0).bold)
            self.assertTrue(snapshot.cell(1, 0).underline)
            self.assertTrue(snapshot.cell(1, 0).inverse)
            terminal.write(b"\x1b[1;2;1;4;1;4;7$t")
            snapshot = terminal.snapshot()
            self.assertFalse(snapshot.cell(1, 0).bold)
            self.assertFalse(snapshot.cell(1, 0).underline)
            self.assertFalse(snapshot.cell(1, 0).inverse)

    def test_rectangular_checksum_reply_is_stable(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"AB\x1b[7;1;1;1;1;2*y")
            self.assertEqual(terminal.read_input(), b"\x1bP7!~FF7D\x1b\\")
    def test_insert_and_delete_characters(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcdef\x1b[1;3H\x1b[2@XY")
            self.assertEqual(terminal.snapshot().lines[0], "abXYcdef")
            terminal.write(b"\x1b[1;3H\x1b[3P")
            self.assertEqual(terminal.snapshot().lines[0], "abdef   ")

    def test_character_editing_never_leaves_split_wide_cells(self):
        for operation in (b"\x1b[@", b"\x1b[P", b"\x1b[X"):
            with self.subTest(operation=operation):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write("A界BC".encode())
                    terminal.write(b"\x1b[1;3H" + operation)
                    snapshot = terminal.snapshot()
                    for column, cell in enumerate(snapshot.cells[:8]):
                        if cell.double_width:
                            self.assertLess(column + 1, 8)
                            self.assertTrue(
                                snapshot.cell(column + 1, 0).double_width_continuation
                            )
                        if cell.double_width_continuation:
                            self.assertGreater(column, 0)
                            self.assertTrue(
                                snapshot.cell(column - 1, 0).double_width
                            )

    def test_ascii_run_overwrites_both_kinds_of_wide_cell_boundary(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("A界B界C".encode())
            terminal.write(b"\x1b[1;3HXYZ")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "A XYZ C ")
            for column in range(8):
                self.assertFalse(snapshot.cell(column, 0).double_width)
                self.assertFalse(
                    snapshot.cell(column, 0).double_width_continuation
                )

    def test_erase_characters_and_line(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcdefgh\x1b[1;3H\x1b[3X")
            self.assertEqual(terminal.snapshot().lines[0], "ab   fgh")
            terminal.write(b"\x1b[1;5H\x1b[1K")
            self.assertEqual(terminal.snapshot().lines[0], "     fgh")

    def test_erased_cells_keep_colors_but_clear_character_attributes(self):
        for erase in (b"\x1b[2J", b"\x1b[2K", b"\x1b[8X", b"\x1b[4@"):
            with self.subTest(erase=erase), Shitty(columns=8, rows=2) as terminal:
                terminal.write(
                    b"12345678\x1b[H"
                    b"\x1b[1;2;3;4;5;7;8;9;53;31;42m"
                    b"\x1b[1\"q\x1b]8;;https://example.com\x1b\\"
                    + erase
                )
                cell = terminal.snapshot().cell(0, 0)
                self.assertEqual(cell.char, " ")
                self.assertEqual(cell.foreground, (170, 0, 0))
                self.assertEqual(cell.background, (0, 170, 0))
                self.assertFalse(cell.bold)
                self.assertFalse(cell.faint)
                self.assertFalse(cell.italic)
                self.assertFalse(cell.underline)
                self.assertFalse(cell.blink)
                self.assertFalse(cell.inverse)
                self.assertFalse(cell.conceal)
                self.assertFalse(cell.strike)
                self.assertFalse(cell.overline)
                self.assertFalse(cell.protected)
                self.assertEqual(cell.hyperlink, 0)

    def test_erased_bold_palette_cell_uses_base_foreground(self):
        # Asserts bold-brightened palette indices; default off (issue 59).
        with Shitty(
            columns=8, rows=2, extra_arguments=("-boldColors",)
        ) as terminal:
            terminal.write(b"\x1b[1;31mX\x1b[K")
            snapshot = terminal.model_snapshot()

            self.assertEqual(snapshot.cell(0, 0).foreground_index, 9)
            erased = snapshot.cell(1, 0)
            self.assertEqual(erased.foreground_index, 1)
            self.assertFalse(erased.bold)

    def test_cursor_restore_restores_erase_colors(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;31m\x1b7\x1b[32m\x1b8\x1b[K")
            erased = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(erased.foreground_index, 1)
            self.assertFalse(erased.bold)

    def test_erase_characters_outside_horizontal_margins_stays_on_screen(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"ABCDEFGH"
                b"\x1b[?69h\x1b[1;4s"
                b"\x1b[1;8H\x1b[99X"
            )
            self.assertEqual(terminal.snapshot().lines[0], "ABCDEFG ")

    def test_erase_characters_ignores_horizontal_margins(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"ABCDEFGH"
                b"\x1b[?69h\x1b[2;4s"
                b"\x1b[1;3H\x1b[4X"
            )
            self.assertEqual(terminal.snapshot().lines[0], "AB    GH")

    def test_insert_and_delete_lines(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            terminal.write(b"\x1b[2;1H\x1b[L")
            self.assertEqual(
                terminal.snapshot().lines,
                ["one  ", "     ", "two  ", "three"],
            )
            terminal.write(b"\x1b[2;1H\x1b[M")
            self.assertEqual(
                terminal.snapshot().lines,
                ["one  ", "two  ", "three", "     "],
            )

    def test_full_width_line_edits_move_complete_cell_state(self):
        # Asserts bold-brightened palette indices; default off (issue 59).
        with Shitty(
            columns=6, rows=4, extra_arguments=("-boldColors",)
        ) as terminal:
            terminal.write(
                b"\x1b[1;1Hplain"
                b"\x1b[2;1H\x1b[1;3;4;31m"
                + "界".encode()
                + b"B\x1b]8;;https://example.com\x1b\\H"
                b"\x1b[0m\x1b]8;;\x1b\\"
                b"\x1b[3;1Hthird"
                b"\x1b[4;1Hfourth"
                b"\x1b[2;1H\x1b[L"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["plain ", "      ", "界 BH  ", "third "])
            moved = snapshot.cell(0, 2)
            self.assertTrue(moved.double_width)
            self.assertTrue(moved.bold)
            self.assertTrue(moved.italic)
            self.assertTrue(moved.underline)
            self.assertEqual(moved.foreground, (255, 85, 85))
            self.assertNotEqual(snapshot.cell(3, 2).hyperlink, 0)

            terminal.write(b"\x1b[2;1H\x1b[M")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["plain ", "界 BH  ", "third ", "      "])
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertNotEqual(snapshot.cell(3, 1).hyperlink, 0)

    def test_insert_lines_clamps_count_to_remaining_region(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            terminal.write(b"\x1b[1;1H\x1b[999L")
            self.assertEqual(terminal.snapshot().lines, ["     "] * 4)

    def test_insert_and_delete_lines_move_cursor_to_line_home(self):
        for operation in (b"\x1b[L", b"\x1b[M"):
            with self.subTest(operation=operation):
                with Shitty(columns=8, rows=4) as terminal:
                    terminal.write(b"one\r\ntwo\r\nthree\x1b[2;5H")
                    terminal.write(operation + b"X")
                    self.assertEqual(terminal.snapshot().cell(0, 1).char, "X")

    def test_erase_display(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\x1b[2;2H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["one  ", "t    ", "     "])

    def test_insert_mode(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"abcd\x1b[1;2H\x1b[4hX\x1b[4lY")
            self.assertEqual(terminal.snapshot().lines[0], "aXYcd ")

    def test_insert_mode_batches_utf8_with_cell_widths(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"abcdef\x1b[1;2H\x1b[4h" + "é界Z".encode())
            self.assertEqual(terminal.snapshot().lines[0], "aé界 Zbcdef  ")

    def test_scroll_up_and_down(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\x1b[2S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["three", "four ", "     ", "     "],
            )
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\x1b[2T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["     ", "     ", "one  ", "two  "],
            )

    def test_large_scroll_count_is_clamped_to_region(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\x1b[999S")
            self.assertEqual(terminal.snapshot().lines, ["     "] * 3)
            terminal.write(b"one\r\ntwo\r\nthree\x1b[999T")
            self.assertEqual(terminal.snapshot().lines, ["     "] * 3)

    def test_scroll_left_and_right(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abcd\x1b[2;1Hefgh\x1b[2 @")
            self.assertEqual(terminal.snapshot().lines, ["cd  ", "gh  "])
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abcd\x1b[2;1Hefgh\x1b[2 A")
            self.assertEqual(terminal.snapshot().lines, ["  ab", "  ef"])

    def test_repeat_preceding_graphic_character(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x1b[5b")
            self.assertEqual(terminal.snapshot().lines[0], "AAAAAA  ")

    def test_repeat_ignores_zero_width_preceding_character(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("e\N{COMBINING ACUTE ACCENT}\x1b[b".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("e"), 0x301))
            self.assertEqual(snapshot.cell(1, 0).char, " ")

    def test_forward_and_backward_tabulation(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"\x1b[2IX\x1b[20G\x1b[2ZY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(16, 0).char, "X")
            self.assertEqual(snapshot.cell(8, 0).char, "Y")

    def test_insert_and_delete_columns(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"abcdef\x1b[2;1Hghijkl\x1b[1;3H\x1b[2'}")
            self.assertEqual(terminal.snapshot().lines, ["ab  cd", "gh  ij"])
            terminal.write(b"\x1b[2'~")
            self.assertEqual(terminal.snapshot().lines, ["abcd  ", "ghij  "])

    def test_erase_saved_lines_discards_scrollback(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\x1b[3J")
            terminal.page_up()
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_erase_saved_lines_preserves_live_screen(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            before = terminal.snapshot().lines
            terminal.write(b"\x1b[3J")

            self.assertEqual(terminal.snapshot().lines, before)


if __name__ == "__main__":
    unittest.main()

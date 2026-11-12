# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class DecProtocolTest(unittest.TestCase):
    def test_double_width_and_double_height_line_attributes_persist(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"AB\x1b#6\x1b[2K")
            snapshot = terminal.snapshot()
            self.assertTrue(all(snapshot.cell(x, 0).line_attribute == 3 for x in range(8)))

            terminal.write(b"\x1b[2;1Htop\x1b#3\x1b[3;1Hbottom\x1b#4")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 1).line_attribute, 1)
            self.assertEqual(snapshot.cell(0, 2).line_attribute, 2)

            terminal.write(b"\x1b[1;1H\x1b#5")
            self.assertEqual(terminal.snapshot().cell(0, 0).line_attribute, 0)

    def test_reverse_index_creates_single_width_lines(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[2;1H\x1b#3"
                b"\x1b[3;1H\x1b#4"
                b"\x1b[4;1H\x1b#6"
                b"\x1b[2;4r\x1b[2;1H\x1bM"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 1).line_attribute, 0)
            self.assertEqual(snapshot.cell(0, 2).line_attribute, 1)
            self.assertEqual(snapshot.cell(0, 3).line_attribute, 2)

    def test_ed_resets_fully_erased_line_attributes(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2;1H\x1b#3\x1b[2J")
            snapshot = terminal.snapshot()
            self.assertTrue(all(
                snapshot.cell(0, row).line_attribute == 0
                for row in range(3)
            ))

    def test_writing_to_double_width_line_clamps_absolute_cursor_position(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b#6\x1b[8GAB")
            self.assertEqual(terminal.snapshot().lines, ["   A    ", "B       "])

    def test_repeat_on_double_width_line_does_not_overflow_cursor(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b#6\x1b[8GA\x1b[2b")
            self.assertEqual(terminal.snapshot().lines, ["   A    ", "AA      "])

    def test_origin_mode_addresses_relative_to_vertical_margins(self):
        with Shitty(columns=8, rows=6) as terminal:
            terminal.write(b"\x1b[2;5r\x1b[?6hX\x1b[4;1HY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertEqual(snapshot.cell(0, 4).char, "Y")

    def test_origin_mode_addresses_relative_to_both_margin_pairs(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"\x1b[2;5r"
                b"\x1b[?69h"
                b"\x1b[3;8s"
                b"\x1b[?6h"
                b"X"
                b"\x1b[4;6H"
                b"Y"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "X")
            self.assertEqual(snapshot.cell(7, 4).char, "Y")

    def test_origin_mode_horizontal_position_commands_use_margins(self):
        for position in (b"\x1b[1G", b"\x1b[1`"):
            with self.subTest(position=position):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(
                        b"\x1b[2;5r"
                        b"\x1b[?69h"
                        b"\x1b[3;8s"
                        b"\x1b[?6h"
                        b"\x1b[2;4H" + position + b"X"
                    )
                    self.assertEqual(terminal.snapshot().cell(2, 2).char, "X")

        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"\x1b[2;5r"
                b"\x1b[?69h"
                b"\x1b[3;8s"
                b"\x1b[?6h"
                b"\x1b[2;1H"
                b"\x1b[2a"
                b"X"
            )
            self.assertEqual(terminal.snapshot().cell(4, 2).char, "X")

    def test_origin_mode_vertical_position_commands_use_margins(self):
        with Shitty(columns=10, rows=8) as terminal:
            terminal.write(
                b"\x1b[3;6r"
                b"\x1b[?6h"
                b"\x1b[1d"
                b"X"
                b"\x1b[99e"
                b"Y"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 2).char, "X")
            self.assertEqual(snapshot.cell(1, 5).char, "Y")

    def test_resetting_origin_mode_homes_cursor_absolutely(self):
        with Shitty(columns=8, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[?6h\x1b[?6lX")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_vt52_cursor_addressing_and_device_attributes(self):
        with Shitty(columns=8, rows=5) as terminal:
            terminal.write(b"\x1b[?2l\x1bY\x22\x24X\x1bZ")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(4, 2).char, "X")
            self.assertEqual(terminal.read_input(), b"\x1b/Z")

    def test_vt52_home_and_relative_cursor_movement(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?2l\x1bY\x23\x25")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 3))

            terminal.write(b"\x1bH\x1bB\x1bB\x1bC")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))

            terminal.write(b"\x1bA\x1bD\x1b<\x1b[3;4H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 2))

    def test_vt52_erase_to_end_of_line_and_screen(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(
                b"abcd\x1b[2;1Hefgh\x1b[3;1Hijkl"
                b"\x1b[?2l\x1bY\x20\x22\x1bK"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["ab  ", "efgh", "ijkl"],
            )

            terminal.write(b"\x1bY\x21\x22\x1bJ")
            self.assertEqual(
                terminal.snapshot().lines,
                ["ab  ", "ef  ", "    "],
            )

    def test_vt52_can_return_to_ansi_mode(self):
        with Shitty(columns=8, rows=5) as terminal:
            terminal.write(b"\x1b[?2l\x1b<\x1b[2;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_vt52_graphics_blank_advances_and_del_is_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2l\x1bF_\x7f\x1bGX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:2], " X")
            self.assertEqual(snapshot.cursor_x, 2)

    def test_vt52_unknown_c1_escape_finals_recover_to_ground(self):
        unknown = (
            tuple(range(0x80, 0x84))
            + tuple(range(0x86, 0x88))
            + tuple(range(0x89, 0x8D))
            + tuple(range(0x91, 0x96))
            + (0x99,)
        )
        sequence = b"".join(b"\x1b" + bytes((byte,)) for byte in unknown)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2l" + sequence + b"X")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_vt100_compatibility_ignores_decrqss_and_s8c1t(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2l\x1b<\x1bP$q\"p\x1b\\")
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x1b G\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")

    def test_decscl_restores_extended_controls_from_vt100_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[?2l\x1b<"
                b"\x1b[64;1\"p"
                b"\x1bP$q\"p\x1b\\"
            )
            self.assertEqual(terminal.read_input(), b"\x1bP1$r64;1\"p\x1b\\")

    def test_decaln_fills_screen_without_leaking_attributes(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[1;31m\x1b#8X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["XEEEE", "EEEEE", "EEEEE"])
            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(snapshot.cell(1, 0).bold)

    def test_decaln_homes_cursor_and_resets_both_margin_pairs(self):
        with Shitty(columns=12, rows=8) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[3;10s\x1b[3;6r"
                b"\x1b[5;6H\x1b#8"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[3;3H\x1b[9A\x1b[9D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[6;10H\x1b[9B\x1b[9C")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (11, 7))

    def test_horizontal_tab_stop_set_and_clear(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[3g\x1b[1;4H\x1bH\r\tX\x1b[3g\r\tY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(3, 0).char, "X")
            self.assertEqual(snapshot.cell(11, 0).char, "Y")

    def test_ris_resets_screen_modes_and_kitty_flags(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"text\x1b[?7l\x1b[?1003h\x1b[?1006h\x1b[>7u\x1bc"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["        ", "        "])
            self.assertEqual(terminal.state(), (0, 0, 0, 0))

    def test_ris_from_alternate_screen_clears_primary_screen(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?1049halt\x1bc")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines, ["        ", "        "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[?47h")
            self.assertEqual(
                terminal.snapshot().lines,
                ["        ", "        "],
            )

    def test_decstr_restores_default_margins(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"\x1b[2;5r\x1b[?69h\x1b[3;8s\x1b[?6h"
                b"\x1b[!p\x1b[?6hX"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).char, "X")

    def test_single_margin_parameter_uses_screen_end_default(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[3r\x1b[?6hX")
            self.assertEqual(terminal.snapshot().cell(0, 2).char, "X")

            terminal.write(b"\x1b[?6l\x1b[r\x1b[?69h\x1b[4s\x1b[?6hY")
            self.assertEqual(terminal.snapshot().cell(3, 0).char, "Y")

    def test_origin_mode_cpr_is_relative_to_both_margins(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"\x1b[2;5r\x1b[?69h\x1b[3;8s\x1b[?6h\x1b[6n"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")


    def test_alternate_screen_resets_horizontal_margins_with_vertical(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;6s")
            terminal.write(b"\x1b[?1049h\x1b[1;1Habcdefgh")
            self.assertIn("abcdefgh", terminal.screen_text())

    def test_restored_cursor_keeps_palette_indices_for_bold_mapping(self):
        # DECSC/DECRC must save the palette indices along with the
        # resolved colors: bold-color remapping re-resolves from the
        # index, and a stale one paints the wrong bright color.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[31m\x1b7\x1b[32m\x1b8\x1b[1mX")
            terminal.write(b"\x1b[2;1H\x1b[0m\x1b[31m\x1b[1mY")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.cell(0, 0).foreground,
                snapshot.cell(0, 1).foreground,
            )

    def test_restore_without_save_resets_to_initial_state(self):
        # xterm: DECRC with nothing saved homes the cursor and resets the
        # rendition instead of silently doing nothing.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[31m\x1b8\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")
            terminal.write(b"Y\x1b[2;1H\x1b[mZ")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "Y")
            self.assertEqual(
                snapshot.cell(0, 0).foreground,
                snapshot.cell(0, 1).foreground,
            )

    def test_rejected_margins_are_a_complete_noop(self):
        # xterm: DECSTBM/DECSLRM with an invalid region neither changes
        # margins nor homes the cursor.
        for sequence in (b"\x1b[5;2r", b"\x1b[4;4r", b"\x1b[99;100r"):
            with self.subTest(sequence=sequence):
                with Shitty(columns=10, rows=5) as terminal:
                    terminal.write(b"\x1b[3;4H" + sequence + b"\x1b[6n")
                    self.assertEqual(terminal.read_input(), b"\x1b[3;4R")
        for sequence in (b"\x1b[5;2s", b"\x1b[4;4s", b"\x1b[99;100s"):
            with self.subTest(sequence=sequence):
                with Shitty(columns=10, rows=5) as terminal:
                    terminal.write(b"\x1b[?69h\x1b[3;4H" + sequence + b"\x1b[6n")
                    self.assertEqual(terminal.read_input(), b"\x1b[3;4R")


    def test_checksum_request_with_an_inverted_rectangle_is_silent(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[1;1;5;5;3;2*y\x1b[5n")
            self.assertEqual(terminal.read_input(), b"\x1b[0n")

    def test_window_frame_colors_are_accepted_and_ignored(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"A\x1b[2;1;2,|B\x1b[2,|C\x1b[5n")
            self.assertEqual(terminal.read_input(), b"\x1b[0n")
            self.assertEqual(terminal.snapshot().lines[0], "ABC       ")

    def test_tab_stop_restore_skips_columns_beyond_the_grid(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"\x1bP2$t9/70000/17\x1b\\")
            self.assertEqual(
                tuple(i for i, stop in enumerate(terminal.tab_stops()) if stop),
                (8, 16),
            )
            self.assertTrue(terminal.tab_stop(8))
            self.assertFalse(terminal.tab_stop(4))
            self.assertFalse(terminal.tab_stop(100))

    def test_ansi_modes_are_inspectable(self):
        with Shitty(columns=10, rows=4) as terminal:
            self.assertEqual(
                [terminal.ansi_mode(mode) for mode in (4, 6, 12, 20, 3)],
                [False, False, True, False, False],
            )
            terminal.write(b"\x1b[4h\x1b[6h\x1b[12h\x1b[20h")
            self.assertEqual(
                [terminal.ansi_mode(mode) for mode in (4, 6, 12, 20, 3)],
                [True, True, True, True, False],
            )

    def test_double_width_line_clamps_a_cursor_past_the_half_width(self):
        with Shitty(columns=20, rows=4) as terminal:
            # DECDHL halves the line after the cursor was placed beyond
            # the new width: plain text, REP and multibyte text all land
            # on the last visible cell and wrap from there.
            terminal.write(b"\x1b[1;15H\x1b#6abc")
            self.assertEqual(
                terminal.snapshot().lines[:2],
                ["         a          ", "bc                  "],
            )
            terminal.write(b"\x1b[2;15Ha\x1b[2;15H\x1b#6\x1b[3b")
            self.assertEqual(
                terminal.snapshot().lines[1:3],
                ["bc       a    a     ", "aa                  "],
            )
            terminal.write("\x1b[3;15H\x1b#6ééé".encode())
            self.assertEqual(
                terminal.snapshot().lines[2:4],
                ["aa       é          ", "éé                  "],
            )
            terminal.write("\x1b[4;15H\x1b#6日本".encode())
            self.assertEqual(
                terminal.snapshot().lines[2:4],
                ["éé                  ", "日 本                 "],
            )

    def test_bulk_print_in_margins_falls_back_around_special_rows(self):
        # A run longer than the margin width arriving with a pending
        # wrap on the last region row takes the batched path unless a
        # region row carries a line attribute or the run blinks.
        prefix = b"\x1b[?69h\x1b[2;7s\x1b[2;4r"
        for extra in (b"\x1b[3;1H\x1b#6\x1b[4;7Hx", b"\x1b[4;7Hx\x1b[5m"):
            with self.subTest(extra=extra):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(prefix + extra + b"abcdef" * 3)
                    self.assertEqual(
                        terminal.snapshot().lines[1:4],
                        [" abcdef   "] * 3,
                    )


    def test_whole_row_erases_follow_attributes_and_protection(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(
                b"abc\x1b[41m\x1b[2K\x1b[42m\x1b[2K"
                b"\x1b[2;1H\x1b[1\"qP\x1b[0\"q\x1b[2K"
                b"\x1b[3;1H\x1b[1\"q\x1b[2K"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["          "] * 3)
            self.assertEqual(snapshot.cell(0, 0).background, (0, 170, 0))
            self.assertEqual(snapshot.cell(9, 0).background, (0, 170, 0))

    def test_row_moves_carry_double_height_and_wide_rows(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                put_rows(b"aaaa", b"bbbb", b"cccc", b"dddd", b"eeee", b"ffff")
                + b"\x1b[2;1H\x1b#6\x1b[1;1H\x1b[L"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["          ", "aaaa      ", "bbbb      ", "cccc      ", "dddd      ", "eeee      "],
            )
            terminal.write(b"\x1b[1;1H\x1b[M\x1b[1;1H\x1b[M")
            self.assertEqual(
                terminal.snapshot().lines,
                ["bbbb      ", "cccc      ", "dddd      ", "eeee      ", "          ", "          "],
            )
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                put_rows(b"aaaa", "日本".encode(), b"cccc", b"dddd", b"eeee", b"ffff")
                + b"\x1b[1;1H\x1b[L"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["          ", "aaaa      ", "日 本       ", "cccc      ", "dddd      ", "eeee      "],
            )
            terminal.write(b"\x1b[1;1H\x1b[M\x1b[1;1H\x1b[M")
            self.assertEqual(
                terminal.snapshot().lines,
                ["日 本       ", "cccc      ", "dddd      ", "eeee      ", "          ", "          "],
            )

    def test_margin_scrolls_over_special_rows(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                put_rows(b"aaaa", b"bbbb", b"cccc")
                + b"\x1b[?69h\x1b[2;7s\x1b[2;1H\x1b#6\x1b[S\x1b[S"
            )
            self.assertEqual(
                terminal.snapshot().lines[:3],
                ["accc      ", "b         ", "c         "],
            )
            terminal.write(b"\x1b[T\x1b[T")
            self.assertEqual(
                terminal.snapshot().lines[:3],
                ["a         ", "b         ", "cccc      "],
            )
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                put_rows(b"aaaa", "日本".encode(), b"cccc")
                + b"\x1b[?69h\x1b[2;7s\x1b[S\x1b[S\x1b[T"
            )
            self.assertEqual(
                terminal.snapshot().lines[:3],
                ["a         ", " ccc      ", "c         "],
            )


    def test_clearing_the_alternate_screen_from_the_primary(self):
        # Mode 47 leaves the alternate screen intact; a clearing reset
        # issued while on the primary discards it anyway.
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"a\x1b[?47hb\x1b[?47l\x1b[?47hc")
            self.assertEqual(terminal.snapshot().lines[0], " bc       ")
        for clear in (b"\x1b[?1047l", b"\x1b[?1049l", b"\x1bc"):
            with self.subTest(clear=clear):
                with Shitty(columns=10, rows=3) as terminal:
                    terminal.write(b"a\x1b[?47hb\x1b[?47l" + clear + b"\x1b[?47hc")
                    self.assertEqual(terminal.snapshot().lines[0].strip(), "c")


    def test_bulk_print_shorter_than_the_region_scrolls_only_its_lines(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;7s\x1b[2;4r\x1b[4;7Hx" + b"abcdef" * 2)
            self.assertEqual(
                terminal.snapshot().lines[1:4],
                ["      x   ", " abcdef   ", " abcdef   "],
            )

    def test_repeat_carries_blink_and_double_height_stops_a_bulk_run(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[5ma\x1b[3b\x1b[0m")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "aaaa      ")
            self.assertTrue(snapshot.cell(3, 0).blink)
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[2;1H\x1b#6\x1b[1;1H" + b"a" * 25)
            self.assertEqual(
                terminal.snapshot().lines[:3],
                ["aaaaaaaaaa", "aaaaa     ", "aaaaaaaaaa"],
            )

    def test_alternate_screen_tracks_the_saved_cursor_and_scrolls_down(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?1049h\x1b[4;8Hq\x1b7\x1b[1;1H")
            terminal.resize(6, 2)
            terminal.write(b"\x1b8\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[2;6R")
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?1049ha\r\nb\x1b[T")
            self.assertEqual(
                terminal.snapshot().lines[:3],
                ["          ", "a         ", "b         "],
            )

    def test_reflow_keeps_a_double_height_row_whole(self):
        with Shitty(columns=10, rows=6, save_lines=10) as terminal:
            terminal.write(b"a" * 25 + b"\r\n\x1b#6wide\r\ntail")
            terminal.resize(20, 6)
            terminal.resize(8, 6)
            lines = terminal.snapshot().lines
            self.assertEqual(lines[0], "aaaaaaaa")
            self.assertTrue(any(line.startswith("wide") for line in lines))
            self.assertTrue(any(line.startswith("tail") for line in lines))


    def test_deleting_through_a_wrap_point_restores_the_flag_at_the_edge(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"a" * 24 + b"\x1b[2;9H\x1b[5P")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:3], ["aaaaaaaaaa", "aaaaaaaa  ", "aaaa      "])
            self.assertFalse(snapshot.cell(9, 1).wrapped)
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"a" * 24 + b"\x1b[1;1H\x1b[9P")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:3], ["a         ", "aaaaaaaaaa", "aaaa      "])
            self.assertFalse(snapshot.cell(9, 0).wrapped)


if __name__ == "__main__":
    unittest.main()

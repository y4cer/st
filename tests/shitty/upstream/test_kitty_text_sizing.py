# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def osc66(metadata, text):
    return b"\x1b]66;" + metadata + b";" + text + b"\x07"


CONTOUR_PARSER_UPSTREAM_CASES = (
    "TextSizing.parse.defaults",
    "TextSizing.parse.keys_are_colon_separated",
    "TextSizing.parse.text_may_contain_semicolons",
    "TextSizing.parse.rejects_out_of_range",
    "TextSizing.parse.fraction_must_be_proper",
    "TextSizing.parse.ignores_unknown_keys",
    "TextSizing.parse.an_unknown_key_may_carry_a_non_numeric_value",
    "TextSizing.columnsFor",
)

CONTOUR_GRID_UPSTREAM_CASES = (
    "TextSizing.plain_ascii_over_a_block_leaves_no_orphan",
    "TextSizing.plain_ascii_on_a_blocks_continuation_row_leaves_no_orphan",
    "TextSizing.width_advances_scale_times_width",
    "TextSizing.a_run_too_long_to_store_is_refused_not_shortened",
    "TextSizing.ICH_destroys_the_blocks_it_would_shift",
    "TextSizing.DCH_destroys_the_blocks_it_would_shift",
    "TextSizing.ICH_to_the_right_of_a_block_still_destroys_it",
    "TextSizing.DECSERA_over_a_block_erases_it_whole",
    "TextSizing.DECSERA_over_a_wide_char_leaves_no_continuation_behind",
    "TextSizing.a_block_past_the_right_margin_is_still_erased_whole",
    "TextSizing.scale_advances_and_records_the_scale",
    "TextSizing.scale_times_width_compose",
    "TextSizing.without_width_each_cluster_is_scaled",
    "TextSizing.ordinary_text_is_unaffected",
    "TextSizing.a_block_is_never_split_across_lines",
    "TextSizing.malformed_request_writes_nothing",
    "TextSizing.scale_is_reset_by_ordinary_writes",
    "TextSizing.a_block_wider_than_the_line_is_dropped",
    "TextSizing.without_autowrap_a_block_is_placed_against_the_right_edge",
    "TextSizing.overwriting_a_block_destroys_all_of_it",
)

CONTOUR_SELECTION_UPSTREAM_CASES = (
    "TextSizing.selection_yields_the_text_once",
    "TextSizing.a_scaled_block_claims_the_rows_beneath_it",
    "TextSizing.writing_below_a_block_destroys_all_of_it",
    "TextSizing.a_block_with_no_room_below_scrolls_rather_than_being_clipped",
    "TextSizing.a_block_taller_than_the_page_is_dropped",
    "TextSizing.multicellBlockAt_finds_the_block_from_any_of_its_cells",
    "TextSizing.multicellBlockAt_reports_no_block_for_an_ordinary_cell",
    "TextSizing.multicellBlockAt_finds_an_ordinary_wide_character",
    "TextSizing.selecting_one_cell_of_a_block_selects_all_of_it",
    "TextSizing.selection_does_not_leak_across_neighbouring_blocks",
    "TextSizing.the_line_level_selection_test_sees_a_block_reaching_into_the_line",
    "TextSizing.a_block_written_over_a_taller_one_destroys_all_of_it",
    "TextSizing.a_wrapping_run_does_not_corrupt_the_line_above",
    "TextSizing.a_block_over_a_wide_character_clears_both_its_columns",
    "TextSizing.a_neighbouring_block_survives",
    "TextSizing.the_cell_carries_the_whole_sizing",
    "TextSizing.overwriting_a_block_head_releases_its_rows",
    "TextSizing.a_block_honours_insert_mode",
    "TextSizing.insert_mode_shifts_every_row_a_block_claims",
    "TextSizing.insert_mode_does_not_orphan_a_neighbouring_block",
)

CONTOUR_FINAL_UPSTREAM_CASES = (
    "TextSizing.a_purely_fractional_request_leaves_the_line_non_trivial",
    "TextSizing.a_block_below_the_scroll_region_does_not_scroll_it",
    "TextSizing.a_block_takes_a_deferred_wrap_before_placing_itself",
    "TextSizing.copying_a_block_carries_its_scale",
    "TextSizing.a_drag_inside_one_row_of_blocks_stays_on_one_line",
    "TextSizing.a_drag_that_leaves_the_blocks_still_selects_two_lines",
    "TextSizing.copying_a_block_row_yields_no_blank_trailing_line",
    "TextSizing.a_block_stays_a_block_once_scrolled_into_history",
    "TextSizing.every_row_of_a_visible_block_is_emitted_with_its_band",
    "TextSizing.a_block_written_after_the_page_scrolled_still_emits_every_band",
    "TextSizing.a_block_whose_head_scrolled_above_the_viewport_still_draws",
    "TextSizing.erasing_a_block_whose_head_scrolled_off_is_reported",
)


def image_region_has_ink(image, left, top, right, bottom):
    width, height, pixels = image
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("image region is outside the frame")
    for y in range(top, bottom):
        for x in range(left, right):
            offset = (y * width + x) * 3
            if pixels[offset:offset + 3] != b"\0\0\0":
                return True
    return False


class TextSizingInventoryTest(unittest.TestCase):
    def test_contour_parser_inventory_has_first_8_cases(self):
        self.assertEqual(len(CONTOUR_PARSER_UPSTREAM_CASES), 8)
        self.assertEqual(len(set(CONTOUR_PARSER_UPSTREAM_CASES)), 8)

    def test_contour_grid_inventory_has_next_20_cases(self):
        self.assertEqual(len(CONTOUR_GRID_UPSTREAM_CASES), 20)
        self.assertEqual(len(set(CONTOUR_GRID_UPSTREAM_CASES)), 20)
        self.assertTrue(
            set(CONTOUR_PARSER_UPSTREAM_CASES).isdisjoint(
                CONTOUR_GRID_UPSTREAM_CASES
            )
        )

    def test_contour_decsera_over_a_wide_char_leaves_no_orphan(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write("中".encode())
            self.assertEqual(terminal.snapshot().lines[0][:2], "中 ")

            terminal.write(b"\x1b[1;1;1;1${")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:2], "  ")
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())
            self.assertEqual(snapshot.cell(1, 0).grapheme, ())

    def test_contour_selection_inventory_has_next_20_cases(self):
        self.assertEqual(len(CONTOUR_SELECTION_UPSTREAM_CASES), 20)
        self.assertEqual(len(set(CONTOUR_SELECTION_UPSTREAM_CASES)), 20)
        imported = set(CONTOUR_PARSER_UPSTREAM_CASES)
        imported.update(CONTOUR_GRID_UPSTREAM_CASES)
        self.assertTrue(imported.isdisjoint(CONTOUR_SELECTION_UPSTREAM_CASES))

    def test_contour_ordinary_cell_is_not_an_indivisible_block(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"ab")
            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), b"a")

    def test_contour_wide_continuation_resolves_to_the_whole_character(self):
        with Shitty(columns=10, rows=1) as terminal:
            terminal.write("中".encode())
            terminal.select_start(1, 0)
            self.assertEqual(
                terminal.selection_state()["snapped"],
                (0, 0, 2, 0),
            )

    def test_contour_final_inventory_has_last_12_cases(self):
        self.assertEqual(len(CONTOUR_FINAL_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(CONTOUR_FINAL_UPSTREAM_CASES)), 12)
        imported = set(CONTOUR_PARSER_UPSTREAM_CASES)
        imported.update(CONTOUR_GRID_UPSTREAM_CASES)
        imported.update(CONTOUR_SELECTION_UPSTREAM_CASES)
        self.assertTrue(imported.isdisjoint(CONTOUR_FINAL_UPSTREAM_CASES))


class KittyTextSizingTest(unittest.TestCase):
    # OSC 66 is deliberately not implemented yet. Keep the imported oracle
    # executable, but report every case as an expected failure until the
    # protocol has an agreed parser/grid/rendering design.
    __unittest_expecting_failure__ = True

    def test_contour_parser_defaults(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"", b"hello"))
            block = terminal.multicell(0, 0)
            self.assertEqual(terminal.snapshot().cursor_x, 5)
            self.assertEqual((block.scale, block.width), (1, 0))
            self.assertEqual((block.numerator, block.denominator), (0, 0))

    def test_contour_parser_uses_colons_between_metadata_keys(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(osc66(b"s=2:w=3:v=1:h=2", b"x"))
            block = terminal.multicell(0, 0)
            self.assertEqual(
                (
                    block.scale,
                    block.width,
                    block.vertical_alignment,
                    block.horizontal_alignment,
                ),
                (2, 3, 1, 2),
            )
            self.assertEqual(terminal.snapshot().cursor_x, 6)

    def test_contour_parser_preserves_semicolons_in_text(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"s=2", b"a;b"))
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).grapheme,
                tuple(b"a;b"),
            )

    def test_contour_parser_enforces_metadata_ranges(self):
        with Shitty(columns=60, rows=8) as terminal:
            terminal.write(osc66(b"s=7:w=7:n=15:d=16:v=2:h=2", b"x"))
            block = terminal.multicell(0, 0)
            self.assertEqual(
                (
                    block.scale,
                    block.width,
                    block.numerator,
                    block.denominator,
                    block.vertical_alignment,
                    block.horizontal_alignment,
                ),
                (7, 7, 15, 16, 2, 2),
            )

            for metadata in (
                b"s=0", b"s=8", b"w=8", b"n=16", b"v=3", b"s=x", b"s",
            ):
                terminal.write(b"\x1bc" + osc66(metadata, b"x"))
                self.assertEqual(terminal.snapshot().cursor_x, 0)

    def test_contour_parser_requires_a_proper_fraction(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"n=1:d=2", b"x"))
            block = terminal.multicell(0, 0)
            self.assertEqual((block.numerator, block.denominator), (1, 2))

            terminal.write(b"\x1bc" + osc66(b"n=3:d=2", b"x"))
            self.assertEqual(terminal.snapshot().cursor_x, 0)

            terminal.write(osc66(b"n=5", b"x"))
            block = terminal.multicell(0, 0)
            self.assertEqual((block.numerator, block.denominator), (5, 0))

    def test_contour_parser_ignores_an_unknown_numeric_key(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:Q=9", b"x"))
            self.assertEqual(terminal.multicell(0, 0).scale, 2)
            self.assertEqual(terminal.snapshot().cursor_x, 2)

    def test_contour_parser_ignores_unknown_non_numeric_values(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"s=2:name=title", b"Hello"))
            self.assertEqual(terminal.multicell(0, 0).scale, 2)
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).grapheme,
                tuple(b"Hello"),
            )

    def test_contour_columns_for_explicit_derived_and_default_widths(self):
        cases = (
            (b"s=2:w=3", b"x", 6),
            (b"s=2:w=3", "界".encode(), 6),
            (b"s=3", b"x", 3),
            (b"s=3", "界".encode(), 6),
            (b"", b"x", 1),
            (b"", "界".encode(), 2),
        )
        for metadata, text, columns in cases:
            with self.subTest(metadata=metadata, text=text), Shitty(
                columns=20, rows=6
            ) as terminal:
                terminal.write(osc66(metadata, text))
                self.assertEqual(terminal.snapshot().cursor_x, columns)

    def test_contour_plain_ascii_over_block_leaves_no_orphan(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"W"))
            self.assertTrue(terminal.multicell(0, 0).valid)

            terminal.write(b"\x1b[Hhello")
            self.assertEqual(terminal.snapshot().lines[0][:5], "hello")
            for row in range(2):
                for column in range(4):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_plain_ascii_on_continuation_row_leaves_no_orphan(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"W"))
            self.assertTrue(terminal.multicell(1, 0).valid)

            terminal.write(b"\x1b[2;1Hhello")
            self.assertEqual(terminal.snapshot().lines[1][:5], "hello")
            for row in range(2):
                for column in range(4):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_width_advances_scale_times_width(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"w=2", b" "))
            self.assertEqual(terminal.snapshot().cursor_x, 2)
            block = terminal.multicell(0, 0)
            self.assertTrue(block.valid)
            self.assertEqual((block.columns, block.rows), (2, 1))
            self.assertTrue(terminal.multicell(0, 1).valid)

    def test_contour_long_fixed_run_preserves_the_protocol_payload(self):
        # Contour refuses this because its private cell storage is capped at
        # 16 codepoints. OSC 66 permits a payload up to 4096 bytes and leaves
        # fitting policy to the renderer, so storage must not silently define
        # the wire protocol's acceptance boundary.
        with Shitty(columns=40, rows=3) as terminal:
            text = b"The quick brown fox"
            terminal.write(osc66(b"w=7", text))
            self.assertEqual(terminal.snapshot().cursor_x, 7)
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).grapheme,
                tuple(text),
            )

    def test_contour_ich_destroys_the_multiline_block_it_would_shift(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            self.assertTrue(terminal.multicell(1, 0).valid)

            terminal.write(b"\x1b[H\x1b[@")
            for row in range(2):
                for column in range(20):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_dch_destroys_the_multiline_block_it_would_shift(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            self.assertTrue(terminal.multicell(1, 0).valid)

            terminal.write(b"\x1b[H\x1b[P")
            for row in range(2):
                for column in range(20):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_ich_destroys_a_block_to_the_right(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"s=2", b"A"))
            self.assertTrue(terminal.multicell(1, 4).valid)

            terminal.write(b"\x1b[H\x1b[2@")
            for row in range(2):
                for column in range(20):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_decsera_over_block_erases_it_whole(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"s=3", b"X"))
            self.assertTrue(terminal.multicell(2, 0).valid)

            terminal.write(b"\x1b[2;1;3;1${")
            for row in range(3):
                for column in range(3):
                    self.assertFalse(terminal.multicell(row, column).valid)
            self.assertEqual(terminal.snapshot().cell(0, 0).grapheme, ())

    def test_contour_block_past_right_margin_is_erased_whole(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[1;11H" + osc66(b"s=2:w=3", b"A"))
            self.assertTrue(terminal.multicell(1, 15).valid)

            terminal.write(b"\x1b[?69h\x1b[6;13s\x1b[1;12HX")
            for row in range(2):
                for column in range(10, 16):
                    self.assertFalse(terminal.multicell(row, column).valid)
            self.assertEqual(terminal.snapshot().cell(11, 0).char, "X")

    def test_contour_scale_advances_and_records_scale(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"s=2", b" "))
            self.assertEqual(terminal.snapshot().cursor_x, 2)
            for row in range(2):
                for column in range(2):
                    block = terminal.multicell(row, column)
                    self.assertTrue(block.valid)
                    self.assertEqual(block.scale, 2)

    def test_contour_scale_times_explicit_width_compose(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 6)
            block = terminal.multicell(0, 0)
            self.assertEqual(
                (block.valid, block.columns, block.rows, block.scale),
                (True, 6, 2, 2),
            )

    def test_contour_without_width_scales_each_cluster_separately(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"s=2", b"ab"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 4)
            self.assertEqual(snapshot.cell(0, 0).char, "a")
            self.assertEqual(snapshot.cell(2, 0).char, "b")
            self.assertEqual(terminal.multicell(0, 0).column, 0)
            self.assertEqual(terminal.multicell(0, 2).column, 0)

    def test_contour_default_sizing_request_matches_ordinary_text(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"", b"abc"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:3], "abc")
            self.assertEqual(snapshot.cursor_x, 3)
            self.assertEqual(terminal.multicell(0, 0).scale, 1)

    def test_contour_block_wraps_whole_instead_of_splitting(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"abcd" + osc66(b"w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertEqual(terminal.multicell(1, 0).columns, 3)

    def test_contour_malformed_request_writes_nothing(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"s=99", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())

            # Also pin the capability precondition so a terminal that ignores
            # every OSC 66 request cannot turn this into a vacuous success.
            terminal.write(osc66(b"s=2", b"Y"))
            self.assertEqual(terminal.snapshot().cursor_x, 2)

    def test_contour_ordinary_write_resets_scale(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"s=3", b"X"))
            self.assertEqual(terminal.multicell(0, 0).scale, 3)

            terminal.write(b"\x1b[Hy")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "y")
            self.assertFalse(terminal.multicell(0, 0).valid)

    def test_contour_block_wider_than_line_is_dropped(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(osc66(b"s=3:w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())

            # A supported request must still work; otherwise ignoring OSC 66
            # would satisfy the drop assertion without implementing the rule.
            terminal.write(osc66(b"w=2", b"Y"))
            self.assertEqual(terminal.snapshot().cursor_x, 2)

    def test_contour_no_autowrap_clamps_block_to_right_edge(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"\x1b[?7labcde" + osc66(b"w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))
            self.assertEqual(snapshot.cell(3, 0).char, "X")
            self.assertEqual(terminal.multicell(0, 3).columns, 3)

    def test_contour_overwriting_middle_destroys_entire_block(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"w=4", b"X"))
            self.assertEqual(terminal.multicell(0, 0).columns, 4)

            terminal.write(b"\x1b[1;3Hy")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:4], "  y ")
            for column in range(4):
                self.assertFalse(terminal.multicell(0, column).valid)

    def test_contour_selection_emits_sized_payload_once(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X") + b"z")
            terminal.select_start(0, 0)
            terminal.select_update(6, 0)
            self.assertEqual(terminal.select_finish(), b"Xz")

    def test_contour_scaled_block_claims_rows_beneath_it(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=3", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 3)
            for row in range(1, 3):
                for column in range(3):
                    block = terminal.multicell(row, column)
                    self.assertTrue(block.valid)
                    self.assertEqual((block.row, block.column), (row, column))
            self.assertFalse(terminal.multicell(3, 0).valid)

    def test_contour_writing_below_block_destroys_it_whole(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 4)

            terminal.write(b"\x1b[2;2Hy")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(1, 1).char, "y")
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())
            self.assertEqual(snapshot.cell(3, 0).grapheme, ())

    def test_contour_tall_block_scrolls_to_make_vertical_room(self):
        with Shitty(columns=10, rows=4, save_lines=10) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\r\n")
            terminal.write(osc66(b"s=2", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 2).char, "X")
            self.assertTrue(terminal.multicell(3, 0).valid)
            self.assertEqual(terminal.scrollback_state()[0], 2)

    def test_contour_block_taller_than_page_is_dropped(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=4", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())

            terminal.write(osc66(b"w=2", b"Y"))
            self.assertEqual(terminal.snapshot().cursor_x, 2)

    def test_contour_every_block_cell_resolves_to_the_same_payload(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 6)

            for row in range(2):
                for column in range(6):
                    terminal.select_start(column, row)
                    terminal.select_update(column, row)
                    self.assertEqual(
                        terminal.select_finish(),
                        b"X",
                        (row, column),
                    )

    def test_contour_selecting_last_block_cell_selects_payload(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X"))
            terminal.select_start(5, 0)
            terminal.select_update(5, 0)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_contour_selection_does_not_leak_to_neighbouring_block(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(osc66(b"w=2", b"A") + osc66(b"w=2", b"B"))
            terminal.select_start(0, 0)
            terminal.select_update(0, 0)
            self.assertEqual(terminal.select_finish(), b"A")

    def test_contour_selection_resolves_block_from_lower_band(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(osc66(b"s=3:w=2", b"X"))
            terminal.select_start(3, 2)
            terminal.select_update(3, 2)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_contour_short_block_over_tall_block_destroys_old_block(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=3:w=2", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 6)

            terminal.write(b"\x1b[2;3H" + osc66(b"w=2", b"Y"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "Y")
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())
            self.assertEqual(snapshot.cell(5, 0).grapheme, ())

    def test_contour_wrapping_scaled_run_keeps_only_complete_blocks(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(osc66(b"s=2", b"abcdefg"))
            snapshot = terminal.snapshot()
            self.assertNotEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            for row in range(3):
                for column in range(10):
                    block = terminal.multicell(row, column)
                    if not block.valid:
                        continue
                    origin_row = row - block.row
                    origin_column = column - block.column
                    for band_row in range(block.rows):
                        for band_column in range(block.columns):
                            member = terminal.multicell(
                                origin_row + band_row,
                                origin_column + band_column,
                            )
                            self.assertTrue(member.valid)

    def test_contour_sized_block_over_wide_tail_clears_wide_head(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write("中".encode())
            terminal.write(b"\x1b[1;2H" + osc66(b"w=2", b"Z"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())
            self.assertEqual(snapshot.cell(1, 0).char, "Z")
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)

    def test_contour_adjacent_sized_blocks_both_survive(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                osc66(b"s=2:w=2", b"A") + osc66(b"s=2:w=2", b"B")
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(4, 0).char, "B")
            self.assertEqual(snapshot.cursor_x, 8)

    def test_contour_cell_carries_complete_sizing_metadata(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=3:w=1:n=1:d=3:v=2:h=1", b"x"))
            self.assertEqual(terminal.snapshot().cursor_x, 3)
            block = terminal.multicell(0, 0)
            self.assertEqual(
                (
                    block.scale,
                    block.width,
                    block.numerator,
                    block.denominator,
                    block.vertical_alignment,
                    block.horizontal_alignment,
                ),
                (3, 1, 1, 3, 2, 1),
            )

    def test_contour_overwriting_head_releases_claimed_rows(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            self.assertEqual(terminal.snapshot().cursor_x, 2)

            terminal.write(b"\x1b[Hx")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "x")
            for row in range(2):
                for column in range(2):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_sized_block_honours_insert_mode(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"abcdef\x1b[H\x1b[4h" + osc66(b"w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:9], "X  abcdef")
            self.assertEqual(snapshot.cursor_x, 3)

    def test_contour_insert_mode_shifts_every_claimed_row(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abcdef\x1b[2;1Hghijkl\x1b[H\x1b[4h")
            terminal.write(osc66(b"s=2", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual(snapshot.lines[0][2:8], "abcdef")
            self.assertEqual(snapshot.lines[1][2:8], "ghijkl")

    def test_contour_insert_mode_does_not_orphan_neighbouring_block(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"s=2", b"B"))
            self.assertEqual(terminal.snapshot().cursor_x, 6)

            terminal.write(b"\x1b[H\x1b[4h" + osc66(b"s=2", b"X"))
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            for row in range(2):
                for column in range(2, 12):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_contour_delta_updates_sized_text_head_and_continuation_rows(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"W"))

            self.assertEqual(terminal.last_update_rows(), (0, 1))
            block = terminal.multicell(0, 0)
            self.assertEqual((block.columns, block.rows, block.scale), (4, 2, 2))

    def test_width_and_scale_advance_the_cursor(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"w=2", b" "))
            self.assertEqual(terminal.snapshot().cursor_x, 2)
            self.assertEqual(terminal.multicell(0, 0).columns, 2)

            terminal.write(osc66(b"s=2:w=3", b"X"))
            self.assertEqual(terminal.snapshot().cursor_x, 8)
            block = terminal.multicell(0, 2)
            self.assertEqual((block.columns, block.rows, block.scale), (6, 2, 2))

    def test_without_width_each_grapheme_is_a_separate_block(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"s=2", b"ab"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 4)
            self.assertEqual(snapshot.cell(0, 0).char, "a")
            self.assertEqual(snapshot.cell(2, 0).char, "b")
            self.assertTrue(terminal.multicell(0, 0).valid)
            self.assertTrue(terminal.multicell(0, 2).valid)
            self.assertEqual(terminal.multicell(0, 0).column, 0)
            self.assertEqual(terminal.multicell(0, 2).column, 0)

    def test_grapheme_cluster_is_not_split(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"s=2", "a\u0301".encode()))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 2)
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("a"), 0x301))
            self.assertEqual(snapshot.cell(1, 0).grapheme, ())

    def test_default_request_has_ordinary_geometry(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc66(b"", b"abc"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 3)
            self.assertEqual(snapshot.lines[0][:3], "abc")
            self.assertEqual(terminal.multicell(0, 0).scale, 1)

    def test_explicit_width_preserves_the_entire_protocol_payload(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(osc66(b"w=7", b"The quick brown fox"))
            self.assertEqual(terminal.snapshot().cursor_x, 7)
            self.assertTrue(terminal.multicell(0, 0).valid)
            self.assertEqual(
                terminal.model_snapshot().cell(0, 0).grapheme,
                tuple(b"The quick brown fox"),
            )

    def test_long_variable_width_run_is_split_instead_of_refused(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(osc66(b"s=2", b"The quick brown fox"))
            self.assertNotEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            self.assertTrue(
                any(
                    terminal.multicell(row, column).valid
                    for row in range(4)
                    for column in range(20)
                )
            )

    def test_block_moves_whole_to_the_next_line(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"abcd" + osc66(b"w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertEqual(terminal.multicell(1, 0).columns, 3)

    def test_block_larger_than_the_page_is_dropped(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(osc66(b"s=3:w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertFalse(terminal.multicell(0, 0).valid)

        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=4", b"X"))
            self.assertFalse(terminal.multicell(0, 0).valid)

    def test_without_autowrap_block_is_clamped_to_right_edge(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"\x1b[?7labcde" + osc66(b"w=3", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))
            self.assertEqual(snapshot.cell(3, 0).char, "X")
            self.assertEqual(terminal.multicell(0, 3).columns, 3)

    def test_block_scrolls_to_make_vertical_room(self):
        with Shitty(columns=10, rows=4, save_lines=10) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\r\n")
            terminal.write(osc66(b"s=2", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 2).char, "X")
            self.assertEqual(terminal.multicell(2, 0).row, 0)
            self.assertEqual(terminal.multicell(3, 0).row, 1)

    def test_full_sizing_metadata_survives(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=3:w=1:n=1:d=3:v=2:h=1", b"x"))
            block = terminal.multicell(0, 0)
            self.assertEqual(
                (
                    block.columns,
                    block.rows,
                    block.scale,
                    block.width,
                    block.numerator,
                    block.denominator,
                    block.vertical_alignment,
                    block.horizontal_alignment,
                ),
                (3, 3, 3, 1, 1, 3, 2, 1),
            )

    def test_ordinary_write_over_head_clears_the_whole_block(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"X"))
            terminal.write(b"\x1b[Hhello")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:5], "hello")
            for row in range(2):
                for column in range(4):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_ordinary_write_in_lower_band_skips_past_the_block(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"X"))
            terminal.write(b"\x1b[2;2Hy")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual(snapshot.cell(4, 1).char, "y")
            self.assertTrue(terminal.multicell(0, 0).valid)
            self.assertTrue(terminal.multicell(1, 3).valid)

    def test_erase_intersection_clears_the_whole_block(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(osc66(b"s=3", b"X"))
            terminal.write(b"\x1b[2;1;3;1${")
            for row in range(3):
                for column in range(3):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_insert_mode_shifts_each_claimed_row(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abcdef\x1b[2;1Hghijkl\x1b[H\x1b[4h")
            terminal.write(osc66(b"s=2", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "X")
            self.assertEqual(snapshot.cell(2, 0).char, "a")
            self.assertEqual(snapshot.cell(2, 1).char, "g")

    def test_ich_moves_an_intact_single_line_block(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"w=3", b"A"))
            terminal.write(b"\x1b[1;1H\x1b[2@")
            self.assertFalse(terminal.multicell(0, 4).valid)
            block = terminal.multicell(0, 6)
            self.assertTrue(block.valid)
            self.assertEqual((block.columns, block.column), (3, 0))

    def test_dch_moves_an_intact_single_line_block(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"w=3", b"A"))
            terminal.write(b"\x1b[1;1H\x1b[2P")
            block = terminal.multicell(0, 2)
            self.assertTrue(block.valid)
            self.assertEqual((block.columns, block.column), (3, 0))
            self.assertFalse(terminal.multicell(0, 6).valid)

    def test_ich_erases_a_single_line_block_split_by_its_boundary(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"w=3", b"A"))
            terminal.write(b"\x1b[1;6H\x1b[@")
            for column in range(12):
                self.assertFalse(terminal.multicell(0, column).valid)

    def test_dch_erases_a_single_line_block_split_by_its_source_boundary(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"w=3", b"A"))
            terminal.write(b"\x1b[1;4H\x1b[2P")
            for column in range(12):
                self.assertFalse(terminal.multicell(0, column).valid)

    def test_ich_erases_a_multiline_block_anywhere_in_the_shifted_tail(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"s=2", b"A"))
            terminal.write(b"\x1b[1;1H\x1b[2@")
            for row in range(2):
                for column in range(12):
                    self.assertFalse(terminal.multicell(row, column).valid)

    def test_selection_extracts_a_block_payload_once(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X") + b"z")
            terminal.select_start(0, 0)
            terminal.select_update(7, 0)
            self.assertEqual(terminal.select_finish(), b"Xz")

    def test_selection_from_a_top_continuation_extracts_the_block(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X"))
            terminal.select_start(5, 0)
            terminal.select_update(6, 0)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_selection_from_a_lower_band_extracts_the_block(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=2:w=3", b"X"))
            terminal.select_start(4, 1)
            terminal.select_update(5, 1)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_selection_does_not_merge_adjacent_blocks(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"w=2", b"A") + osc66(b"w=2", b"B"))
            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), b"A")

    def test_copying_lower_bands_adds_no_blank_trailing_line(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(osc66(b"s=2:w=2", b"X"))
            terminal.select_start(0, 0)
            terminal.select_update(4, 1)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_block_identity_and_band_survive_in_scrollback(self):
        with Shitty(columns=10, rows=4, save_lines=20) as terminal:
            terminal.write(osc66(b"s=3", b"X"))
            terminal.write(b"\x1b[4;1H\x1b[5S")
            history = terminal.scrollback_state()[0]
            blocks = [
                (row, terminal.multicell(row, 0))
                for row in range(-history, 0)
                if terminal.multicell(row, 0).valid
            ]
            self.assertEqual([row for row, _ in blocks], [-4, -3, -2])
            self.assertEqual([block.row for _, block in blocks], [0, 1, 2])
            self.assertTrue(all(block.rows == 3 for _, block in blocks))

    def test_deccra_copies_a_complete_block_with_every_band(self):
        with Shitty(columns=10, rows=8) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            terminal.write(b"\x1b[1;1;2;2;1;5;1;1$v")
            for row in range(2):
                for column in range(2):
                    block = terminal.multicell(4 + row, column)
                    self.assertTrue(block.valid)
                    self.assertEqual((block.row, block.column), (row, column))
                    self.assertEqual((block.rows, block.columns), (2, 2))

    def test_deccra_drops_a_partial_source_block(self):
        with Shitty(columns=10, rows=8) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            terminal.write(b"\x1b[1;1;1;2;1;5;1;1$v")
            for column in range(2):
                self.assertFalse(terminal.multicell(4, column).valid)
            self.assertTrue(terminal.multicell(0, 0).valid)
            self.assertTrue(terminal.multicell(1, 0).valid)

    def test_deccra_intersection_erases_the_old_destination_block(self):
        with Shitty(columns=10, rows=8) as terminal:
            terminal.write(b"A\x1b[5;1H" + osc66(b"s=2", b"X"))
            terminal.write(b"\x1b[1;1;1;1;1;5;1;1$v")
            for row in range(4, 6):
                for column in range(2):
                    self.assertFalse(terminal.multicell(row, column).valid)
            self.assertEqual(terminal.snapshot().cell(0, 4).char, "A")

    def test_deferred_wrap_happens_before_sized_text(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"abcde" + osc66(b"s=1", b"X"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "abcde")
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertTrue(terminal.multicell(1, 0).valid)

    def test_block_below_scroll_region_does_not_scroll_it(self):
        with Shitty(columns=20, rows=25) as terminal:
            terminal.write(b"\x1b[1;1Hline0\x1b[10;1Hline9")
            terminal.write(b"\x1b[1;10r\x1b[20;1H" + osc66(b"s=3", b"A"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "l")
            self.assertEqual(snapshot.cell(0, 9).char, "l")
            self.assertEqual(snapshot.cell(0, 19).char, "A")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 19))

    def test_erasing_inside_margins_clears_a_block_past_the_margin(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[1;11H" + osc66(b"s=2:w=3", b"A"))
            terminal.write(b"\x1b[?69h\x1b[6;13s\x1b[1;12HX")
            for row in range(2):
                for column in range(10, 16):
                    self.assertFalse(terminal.multicell(row, column).valid)
            self.assertEqual(terminal.snapshot().cell(11, 0).char, "X")

    def test_wrapping_sized_run_leaves_only_complete_blocks(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(osc66(b"s=2", b"abcdefg"))
            for row in range(3):
                for column in range(10):
                    block = terminal.multicell(row, column)
                    if not block.valid:
                        continue
                    origin_row = row - block.row
                    origin_column = column - block.column
                    for band_row in range(block.rows):
                        for band_column in range(block.columns):
                            member = terminal.multicell(
                                origin_row + band_row,
                                origin_column + band_column,
                            )
                            self.assertTrue(member.valid)
                            self.assertEqual(
                                (member.row, member.column),
                                (band_row, band_column),
                            )

    def test_short_block_over_tall_block_erases_the_tall_block_whole(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=3:w=2", b"X"))
            terminal.write(b"\x1b[2;3H" + osc66(b"w=2", b"Y"))
            for row in range(3):
                for column in range(6):
                    if row == 1 and 2 <= column < 4:
                        continue
                    self.assertFalse(terminal.multicell(row, column).valid)
            replacement = terminal.multicell(1, 2)
            self.assertTrue(replacement.valid)
            self.assertEqual((replacement.rows, replacement.columns), (1, 2))

    def test_sized_block_over_wide_continuation_clears_the_wide_head(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write("中".encode())
            terminal.write(b"\x1b[1;2H" + osc66(b"w=2", b"Z"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, " ")
            self.assertEqual(snapshot.cell(1, 0).char, "Z")
            self.assertTrue(terminal.multicell(0, 1).valid)

    def test_insert_mode_does_not_orphan_a_neighbouring_block(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(b"\x1b[1;5H" + osc66(b"s=2", b"B"))
            terminal.write(b"\x1b[H\x1b[4h" + osc66(b"s=2", b"X"))
            for row in range(2):
                for column in range(12):
                    block = terminal.multicell(row, column)
                    if column < 2:
                        self.assertTrue(block.valid)
                        self.assertEqual((block.row, block.column), (row, column))
                    else:
                        self.assertFalse(block.valid)

    def test_adjacent_blocks_keep_distinct_identity(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(osc66(b"w=2", b"A") + osc66(b"w=2", b"B"))
            first = terminal.multicell(0, 0)
            second = terminal.multicell(0, 2)
            self.assertTrue(first.valid)
            self.assertTrue(second.valid)
            self.assertEqual(first.column, 0)
            self.assertEqual(second.column, 0)
            self.assertEqual(terminal.snapshot().lines[0][:4], "A B ")

    def test_contour_final_fractional_text_uses_the_nontrivial_render_path(self):
        with Shitty(
            columns=4, rows=2, glyph_px=8, glyph_py=8
        ) as fractional:
            fractional.write(
                osc66(b"n=1:d=2:w=1", b"Ha") + b"\x1b[?25l"
            )
            self.assertEqual(fractional.snapshot().cursor_x, 1)
            fractional_image = fractional.reference_image()

        with Shitty(
            columns=4, rows=2, glyph_px=8, glyph_py=8
        ) as ordinary:
            ordinary.write(osc66(b"w=1", b"Ha") + b"\x1b[?25l")
            self.assertEqual(ordinary.snapshot().cursor_x, 1)
            ordinary_image = ordinary.reference_image()

        self.assertNotEqual(fractional_image, ordinary_image)

    def test_contour_final_block_below_margins_does_not_scroll_them(self):
        with Shitty(columns=20, rows=25) as terminal:
            for row in range(25):
                terminal.write(f"\x1b[{row + 1};1Hline{row}".encode())
            terminal.write(b"\x1b[1;10r\x1b[20;1H" + osc66(b"s=3", b"A"))
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 19))
            self.assertEqual(snapshot.lines[0].rstrip(), "line0")
            self.assertEqual(snapshot.lines[9].rstrip(), "line9")
            self.assertEqual(snapshot.cell(0, 19).char, "A")

    def test_contour_final_block_honours_a_deferred_wrap(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"abcde" + osc66(b"s=1", b"X"))
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "abcde")
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_contour_final_deccra_copy_preserves_scaled_rendering(self):
        with Shitty(
            columns=10, rows=8, glyph_px=8, glyph_py=8
        ) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            terminal.write(b"\x1b[1;1;2;2;1;5;1;1$v\x1b[?25l")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(0, 4).char, "A")

            image = terminal.reference_image()
            self.assertTrue(image_region_has_ink(image, 2, 2, 18, 18))
            self.assertTrue(image_region_has_ink(image, 2, 34, 18, 50))

    def test_contour_final_drag_inside_one_block_row_stays_logical(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=2", b"ab") + b"  cap")
            terminal.select_start(0, 0)
            terminal.select_update(4, 1)

            self.assertEqual(terminal.select_finish(), b"ab")

    def test_contour_final_drag_leaving_blocks_becomes_multiline(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=2", b"ab") + b"\r\n\r\nplain")
            terminal.select_start(0, 0)
            terminal.select_update(5, 2)

            self.assertEqual(terminal.select_finish(), b"ab\nplain")

    def test_contour_final_copying_all_block_rows_adds_no_blank_line(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(osc66(b"s=2", b"ab"))
            terminal.select_start(0, 0)
            terminal.select_update(4, 1)

            self.assertEqual(terminal.select_finish(), b"ab")

    def test_contour_final_block_lookup_survives_scrollback(self):
        with Shitty(columns=20, rows=5, save_lines=50) as terminal:
            terminal.write(osc66(b"s=4", b"X") + b"\r\n" * 4)
            for index in range(10):
                terminal.write(f"filler{index}\r\n".encode())

            history = terminal.scrollback_state()[0]
            terminal.wheel_up(history)
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            terminal.select_start(0, 2)
            terminal.select_update(1, 2)
            self.assertEqual(terminal.select_finish(), b"X")

    def test_contour_final_renderer_emits_each_visible_block_band(self):
        with Shitty(
            columns=20, rows=6, glyph_px=8, glyph_py=8
        ) as terminal:
            terminal.write(osc66(b"s=2", b"X") + b"\x1b[?25l")
            self.assertEqual(terminal.snapshot().cursor_x, 2)
            image = terminal.reference_image()

            self.assertTrue(image_region_has_ink(image, 2, 2, 18, 10))
            self.assertTrue(image_region_has_ink(image, 2, 10, 18, 18))

    def test_contour_final_renderer_emits_bands_after_page_scroll(self):
        with Shitty(
            columns=20, rows=6, save_lines=50, glyph_px=8, glyph_py=8
        ) as terminal:
            for index in range(12):
                terminal.write(f"filler{index}\r\n".encode())
            terminal.write(osc66(b"s=2", b"X") + b"\x1b[?25l")
            snapshot = terminal.snapshot()
            block_row = next(
                row for row, line in enumerate(snapshot.lines)
                if line.startswith("X")
            )
            image = terminal.reference_image()
            top = 2 + block_row * 8

            self.assertTrue(image_region_has_ink(image, 2, top, 18, top + 8))
            self.assertTrue(
                image_region_has_ink(image, 2, top + 8, 18, top + 16)
            )

    def test_contour_final_visible_bands_draw_with_head_above_viewport(self):
        with Shitty(
            columns=20, rows=5, save_lines=50, glyph_px=8, glyph_py=8
        ) as terminal:
            terminal.write(osc66(b"s=4", b"X") + b"\r\n" * 4)
            for index in range(10):
                terminal.write(f"filler{index}\r\n".encode())

            lines = terminal.all_text()
            head = next(index for index, line in enumerate(lines) if line == "X")
            history = terminal.scrollback_state()[0]
            terminal.wheel_up(history - head - 1)
            terminal.write(b"\x1b[?25l")
            self.assertEqual(terminal.snapshot().lines[0].strip(), "")
            self.assertTrue(
                image_region_has_ink(
                    terminal.reference_image(), 2, 2, 34, 10
                )
            )

    def test_contour_final_erasing_history_head_is_reported(self):
        with Shitty(columns=10, rows=2, save_lines=10) as terminal:
            terminal.write(osc66(b"s=2", b"A"))
            terminal.write(b"\x1b[2;1H\n")
            self.assertTrue(terminal.all_text()[0].startswith("A"))
            terminal.last_update_rows()

            terminal.write(b"\x1b[1;1Hz")

            self.assertFalse(terminal.all_text()[0].startswith("A"))
            self.assertIn(-1, terminal.last_update_rows())


if __name__ == "__main__":
    unittest.main()

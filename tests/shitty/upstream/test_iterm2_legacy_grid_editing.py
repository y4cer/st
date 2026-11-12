# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Legacy iTerm2 VT100Grid cases 33 through 52."""

import unittest

import test_iterm2_vt100_grid as public_grid


PORTED_CASES = (
    (
        "VT100GridTest.testMoveWrappedCursorLineToTopOfGrid",
        "test_move_wrapped_cursor_line_to_top",
    ),
    (
        "VT100GridTest.testAppendCharsAtCursor",
        "test_append_autowrap_insert_and_wide_boundaries",
    ),
    (
        "VT100GridTest.testCoordinateBefore",
        "test_combining_mark_predecessor_across_grid_boundaries",
    ),
    ("VT100GridTest.testDeleteChars_base", "test_dch_base"),
    ("VT100GridTest.testDeleteChars_tooMany", "test_dch_clamps_large_count"),
    ("VT100GridTest.testDeleteChars_delete0", "test_dch_explicit_zero"),
    (
        "VT100GridTest.testDeleteChars_deleteLeftHalfDWC",
        "test_dch_at_wide_head",
    ),
    (
        "VT100GridTest.testDeleteChars_delteRightHalfDWC",
        "test_dch_at_wide_continuation",
    ),
    ("VT100GridTest.testDeleteChars_breakSkip", "test_dch_breaks_wide_pre_wrap"),
    (
        "VT100GridTest.testDeleteChars_scrollRegion",
        "test_dch_inside_horizontal_region",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollRegionDeleteBignum",
        "test_dch_large_count_inside_horizontal_region",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollRegionDeleteRightDWC",
        "test_dch_wide_tail_inside_horizontal_region",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollRegionBoundaryOverlapsLeftHalfDWC",
        "test_dch_repairs_wide_at_right_region_boundary",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollRegionBoundaryOverlapsRightHalfDWC",
        "test_dch_repairs_wide_at_left_region_boundary",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollREgionDWCSkipSurvives",
        "test_dch_region_preserves_wide_pre_wrap",
    ),
    (
        "VT100GridTest.testDeleteChars_scrollRegionOutside",
        "test_dch_outside_horizontal_region_is_noop",
    ),
    (
        "VT100GridTest.testInsertChar",
        "test_ich_insert_mode_regions_wide_cells_and_wrap",
    ),
    (
        "VT100GridTest.testMoveCursorRightToMargin",
        "test_large_cuf_clamps_at_right_margin",
    ),
    (
        "VT100GridTest.testAppendingLongLineAtBottomOfScrollRegionGivesSoftBreak",
        "test_bottom_region_autowrap_preserves_soft_breaks",
    ),
    (
        "VT100GridTest.testGridRunFromRange_basic",
        "test_basic_row_major_grid_range",
    ),
)


APPEND_ADAPTERS = (
    "test_empty_output_is_a_complete_noop",
    "test_bottom_wrap_scrolls_the_completed_row_into_history",
    "test_horizontal_margin_wrap_scrolls_only_its_columns",
    "test_one_row_top_region_wraps_into_history",
    "test_alternate_screen_wrap_has_no_scrollback_backing",
    "test_one_row_rectangular_region_wraps_without_history",
    "test_long_wrap_keeps_every_logical_row_with_large_history",
    "test_wide_glyph_advances_by_two_cells_before_wrapping",
    "test_wide_glyph_that_does_not_fit_wraps_as_a_complete_cell",
    "test_wide_glyph_wraps_at_a_horizontal_margin_without_an_orphan",
    "test_default_wraparound_defers_until_the_following_character",
    "test_horizontal_margin_wrap_uses_its_left_edge_on_the_next_row",
    "test_insert_mode_shifts_plain_text_to_the_right",
    "test_insert_mode_drops_a_wide_glyph_cut_by_the_right_edge",
    "test_insert_mode_replaces_a_wide_wrap_spacer_with_normal_text",
    "test_long_insert_mode_write_wraps_and_keeps_the_shifted_tail",
    "test_long_insert_without_wraparound_keeps_only_the_last_margin_cell",
    "test_insert_mode_shifts_only_inside_horizontal_margins",
    "test_insert_mode_wraps_from_right_to_left_horizontal_margin",
    "test_insert_at_a_horizontal_margin_erases_a_wide_glyph_cut_by_the_shift",
    "test_overwrite_of_a_wide_head_erases_its_continuation",
)


COORDINATE_BEFORE_ADAPTERS = (
    "test_split_combining_mark_attaches_to_the_preceding_narrow_cell",
    "test_leading_combining_mark_never_attaches_forward",
    "test_combining_mark_attaches_to_a_pending_wrap_cell",
    "test_hard_line_break_prevents_combining_with_the_previous_row",
    "test_combining_mark_attaches_to_a_wide_glyph_after_pre_wrap",
    "test_combining_mark_at_a_pending_horizontal_margin_uses_its_right_edge_base",
    "test_combining_mark_skips_a_wide_continuation",
    "test_combining_mark_attaches_to_a_wide_right_margin_cell",
)


INSERT_ADAPTERS = (
    "test_ich_inserts_one_blank_and_shifts_tail_right",
    "test_ich_large_count_clears_to_right_edge",
    "test_insert_mode_inserts_non_blank_graphics",
    "test_zero_ich_parameter_follows_the_terminal_consensus_of_one",
    "test_ich_at_wide_continuation_repairs_both_halves",
    "test_ich_one_cell_keeps_soft_wrap_after_removing_wide_pre_wrap_spacer",
    "test_ich_overflow_keeps_consensus_soft_wrap_after_dropping_pre_wrap_spacer",
    "test_ich_overflow_repairs_wide_cell_and_keeps_consensus_soft_wrap",
    "test_ich_inside_horizontal_margins_shifts_only_to_right_margin",
    "test_ich_large_count_clears_only_to_horizontal_right_margin",
    "test_ich_repairs_wide_glyph_crossing_horizontal_right_margin",
    "test_ich_repairs_wide_glyph_crossing_horizontal_left_margin",
    "test_ich_partial_horizontal_region_preserves_wide_pre_wrap",
    "test_ich_outside_horizontal_margins_is_a_noop",
)


class ITerm2LegacyGridEditingTest(unittest.TestCase):
    _select = staticmethod(public_grid.ITerm2VT100GridTest._select)

    def _run_public_adapters(self, *names):
        for name in names:
            with self.subTest(public_adapter=name):
                operation = getattr(public_grid.ITerm2VT100GridTest, name)
                operation(self)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_move_wrapped_cursor_line_to_top(self):
        self._run_public_adapters(
            "test_standard_scroll_controls_move_a_wrapped_cursor_line_to_the_top"
        )

    def test_append_autowrap_insert_and_wide_boundaries(self):
        self._run_public_adapters(*APPEND_ADAPTERS)

    def test_combining_mark_predecessor_across_grid_boundaries(self):
        self._run_public_adapters(*COORDINATE_BEFORE_ADAPTERS)

    def test_dch_base(self):
        self._run_public_adapters("test_dch_deletes_one_cell_and_shifts_the_tail_left")

    def test_dch_clamps_large_count(self):
        self._run_public_adapters("test_dch_clamps_an_oversized_count_at_the_right_edge")

    def test_dch_explicit_zero(self):
        self._run_public_adapters(
            "test_zero_dch_parameter_follows_the_terminal_consensus_of_one"
        )

    def test_dch_at_wide_head(self):
        self._run_public_adapters("test_dch_at_a_wide_head_repairs_the_cut_glyph")

    def test_dch_at_wide_continuation(self):
        self._run_public_adapters(
            "test_dch_at_a_wide_continuation_repairs_the_cut_glyph"
        )

    def test_dch_breaks_wide_pre_wrap(self):
        self._run_public_adapters(
            "test_dch_removes_a_shifted_pre_wrap_spacer_and_hardens_the_row"
        )

    def test_dch_inside_horizontal_region(self):
        self._run_public_adapters(
            "test_dch_inside_horizontal_margins_shifts_only_to_the_right_margin"
        )

    def test_dch_large_count_inside_horizontal_region(self):
        self._run_public_adapters(
            "test_dch_large_count_clears_only_to_the_horizontal_right_margin"
        )

    def test_dch_wide_tail_inside_horizontal_region(self):
        self._run_public_adapters(
            "test_dch_at_wide_tail_inside_horizontal_margins_repairs_the_glyph"
        )

    def test_dch_repairs_wide_at_right_region_boundary(self):
        self._run_public_adapters(
            "test_dch_repairs_wide_glyph_crossing_horizontal_right_margin"
        )

    def test_dch_repairs_wide_at_left_region_boundary(self):
        self._run_public_adapters(
            "test_dch_repairs_wide_glyph_crossing_horizontal_left_margin"
        )

    def test_dch_region_preserves_wide_pre_wrap(self):
        self._run_public_adapters(
            "test_dch_partial_horizontal_region_preserves_wide_pre_wrap"
        )

    def test_dch_outside_horizontal_region_is_noop(self):
        self._run_public_adapters(
            "test_dch_outside_horizontal_margins_is_a_noop"
        )

    def test_ich_insert_mode_regions_wide_cells_and_wrap(self):
        self._run_public_adapters(*INSERT_ADAPTERS)

    def test_large_cuf_clamps_at_right_margin(self):
        self._run_public_adapters("test_large_cuf_clamps_at_the_page_right_margin")

    def test_bottom_region_autowrap_preserves_soft_breaks(self):
        self._run_public_adapters(
            "test_bottom_region_autowrap_keeps_every_moved_soft_break"
        )

    def test_basic_row_major_grid_range(self):
        self._run_public_adapters("test_row_major_range_starts_at_the_first_cell")


if __name__ == "__main__":
    unittest.main()

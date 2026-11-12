# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Legacy iTerm2 VT100Grid cases 13 through 32."""

import unittest

from harness import Shitty
import test_iterm2_vt100_grid as public_grid


PORTED_CASES = (
    (
        "VT100GridTest.testMoveCursorLeftWrappingAroundSoftEOL",
        "test_cub_across_soft_eol",
    ),
    (
        "VT100GridTest.testMoveCursorLeftWrappingAroundDoubleWideCharEOL",
        "test_cub_across_wide_pre_wrap_eol",
    ),
    (
        "VT100GridTest.testMoveCursorLeftNotWrappingAroundHardEOL",
        "test_cub_does_not_cross_hard_eol",
    ),
    ("VT100GridTest.testMoveCursorRight", "test_cuf_page_and_margin_cases"),
    ("VT100GridTest.testMoveCursorUp", "test_cuu_page_and_margin_cases"),
    ("VT100GridTest.testMoveCursorDown", "test_cud_page_and_margin_cases"),
    (
        "VT100GridTest.testScrollUpIntoLineBuffer",
        "test_su_history_limit_and_horizontal_region",
    ),
    (
        "VT100GridTest.testScrollWholeScreenUpIntoLineBuffer",
        "test_repeated_full_page_su_keeps_newest_history",
    ),
    (
        "VT100GridTest.testScrollRectDownBy",
        "test_rectangular_su_sd_counts_wide_cells_and_wrap_metadata",
    ),
    (
        "VT100GridTest.testSetContentsFromDVRFrame",
        "test_physical_frame_restore_at_smaller_and_larger_geometry",
    ),
    ("VT100GridTest.testDefaultLine", "test_default_blank_line_attributes"),
    (
        "VT100GridTest.testSetBgFgColorInRect",
        "test_rectangular_foreground_and_background_are_independent",
    ),
    (
        "VT100GridTest.testRestoreScreenFromLineBuffer",
        "test_resize_restores_logical_lines_cursor_and_wide_cells",
    ),
    ("VT100GridTest.testRectsForRun", "test_row_major_run_spans_three_rows"),
    (
        "VT100GridTest.testResetScrollRegions",
        "test_ris_resets_vertical_and_horizontal_regions",
    ),
    (
        "VT100GridTest.testScrollRegionRect",
        "test_declrmm_controls_whether_columns_limit_scroll_region",
    ),
    ("VT100GridTest.testEraseDwc", "test_ech_repairs_complete_wide_glyph"),
    (
        "VT100GridTest.testMoveCursorToLeftMargin",
        "test_cr_uses_page_or_active_left_margin",
    ),
    (
        "VT100GridTest.testResetWithLineBufferLeavingBehindZero",
        "test_public_reset_clears_bounded_unbounded_and_empty_history",
    ),
    (
        "VT100GridTest.testResetWithLineBufferLeavingBehindCursorLine",
        "test_public_reset_is_independent_of_cursor_content_position",
    ),
)


SCROLL_RECT_ADAPTERS = (
    "test_wire_zero_scroll_down_defaults_to_one_row",
    "test_rectangular_scroll_down_one_damages_region_rows",
    "test_rectangular_scroll_up_one_damages_region_rows",
    "test_rectangular_scroll_down_two_damages_region_rows",
    "test_rectangular_scroll_up_two_damages_region_rows",
    "test_rectangular_scroll_down_by_region_height_blanks_region",
    "test_rectangular_scroll_up_by_region_height_blanks_region",
    "test_rectangular_scroll_down_clamps_count_to_region_height",
    "test_rectangular_scroll_up_clamps_count_to_region_height",
    "test_partial_scroll_up_clears_a_wide_source_cut_at_left_edge",
    "test_partial_scroll_down_clears_a_wide_source_cut_at_right_edge",
    "test_full_width_scroll_moves_a_wrapped_wide_glyph_intact",
    "test_partial_scroll_cleans_orphaned_wide_cells_on_every_row",
    "test_partial_scroll_repairs_destination_edges_only_inside_vertical_region",
    "test_partial_scroll_to_right_margin_repairs_left_wide_boundary",
    "test_partial_scroll_from_left_margin_repairs_right_wide_boundary",
    "test_invalid_zero_height_scroll_region_is_harmless",
    "test_partial_scroll_preserves_complete_wide_and_repairs_cut_one",
    "test_partial_scroll_down_keeps_complete_wide_at_rectangle_edge",
    "test_partial_scroll_up_keeps_complete_wide_at_rectangle_edge",
    "test_full_width_scroll_down_preserves_moved_soft_wrap_metadata",
    "test_full_width_scroll_down_two_preserves_source_soft_wrap",
    "test_full_width_scroll_up_preserves_moved_soft_wrap_metadata",
    "test_full_width_scroll_up_two_preserves_source_soft_wrap",
    "test_partial_width_scroll_preserves_each_rows_soft_wrap_metadata",
    "test_partial_width_scroll_down_two_preserves_destination_row_endings",
    "test_partial_width_scroll_down_repairs_a_dwc_skip_destination",
    "test_partial_width_scroll_up_one_preserves_destination_row_endings",
    "test_partial_width_scroll_up_repairs_both_dwc_skip_boundaries",
    "test_partial_width_scroll_up_two_preserves_destination_row_endings",
)


class ITerm2LegacyGridCoreTest(unittest.TestCase):
    def _run_public_adapters(self, *names):
        for name in names:
            with self.subTest(public_adapter=name):
                operation = getattr(public_grid.ITerm2VT100GridTest, name)
                operation(self)

    def _assert_ris_clears_page_and_history(self, terminal):
        operation = public_grid.ITerm2VT100GridTest._assert_ris_clears_page_and_history
        operation(self, terminal)

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    @unittest.expectedFailure
    def test_cub_across_soft_eol(self):
        operation = public_grid.ITerm2VT100GridTest.test_iterm_default_cub_wraps_across_soft_eol
        operation(self)

    @unittest.expectedFailure
    def test_cub_across_wide_pre_wrap_eol(self):
        operation = public_grid.ITerm2VT100GridTest.test_iterm_default_cub_wraps_across_early_wide_eol
        operation(self)

    def test_cub_does_not_cross_hard_eol(self):
        self._run_public_adapters("test_cursor_left_does_not_cross_a_hard_eol")

    def test_cuf_page_and_margin_cases(self):
        self._run_public_adapters(
            "test_cursor_right_default_moves_one_column",
            "test_cursor_right_before_horizontal_region_moves_normally",
            "test_cursor_right_can_enter_horizontal_region",
            "test_cursor_right_stops_at_horizontal_region_end",
        )

    def test_cuu_page_and_margin_cases(self):
        self._run_public_adapters(
            "test_cursor_up_default_clamps_at_page_top",
            "test_cursor_up_clamps_at_vertical_region_top",
            "test_cursor_up_above_vertical_region_moves_to_page_top",
        )

    def test_cud_page_and_margin_cases(self):
        self._run_public_adapters(
            "test_cursor_down_default_clamps_at_page_bottom",
            "test_cursor_down_clamps_at_vertical_region_bottom",
            "test_cursor_down_below_vertical_region_moves_to_page_bottom",
        )

    def test_su_history_limit_and_horizontal_region(self):
        self._run_public_adapters(
            "test_scroll_up_moves_top_row_into_history",
            "test_scroll_up_bounded_history_drops_oldest_row",
            "test_horizontal_region_scroll_does_not_create_history",
        )

    def test_repeated_full_page_su_keeps_newest_history(self):
        self._run_public_adapters(
            "test_repeated_whole_screen_scroll_keeps_newest_history_tail"
        )

    def test_rectangular_su_sd_counts_wide_cells_and_wrap_metadata(self):
        self._run_public_adapters(*SCROLL_RECT_ADAPTERS)

    def test_physical_frame_restore_at_smaller_and_larger_geometry(self):
        self._run_public_adapters(
            "test_public_resize_restores_a_frame_at_smaller_and_larger_geometry"
        )

    def test_default_blank_line_attributes(self):
        foreground = (18, 52, 86)
        background = (101, 67, 33)
        with Shitty(
            columns=80,
            rows=2,
            extra_arguments=("-fg", "#123456", "-bg", "#654321"),
        ) as terminal:
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" " * 80, " " * 80])
            for cell in snapshot.cells:
                self.assertFalse(cell.drawn)
                self.assertFalse(cell.wrapped)
                self.assertEqual(cell.foreground, foreground)
                self.assertEqual(cell.background, background)

            # iTerm2 stores ALTSEM_SELECTED as a cell color code.  The other
            # terminals, including Shitty, keep selection as presentation
            # state; exercise that independently without changing blank cells.
            terminal.write(b"\x1b]17;#010203\x1b\\\x1b]19;#040506\x1b\\")
            state = terminal.render_state()
            self.assertEqual(state.selection_background, (1, 2, 3))
            self.assertEqual(state.selection_foreground, (4, 5, 6))
            after = terminal.model_snapshot()
            self.assertEqual(after.lines, snapshot.lines)
            self.assertTrue(all(not cell.drawn for cell in after.cells))

    def test_rectangular_foreground_and_background_are_independent(self):
        self._run_public_adapters(
            "test_deccara_can_apply_foreground_and_background_independently"
        )

    def test_resize_restores_logical_lines_cursor_and_wide_cells(self):
        self._run_public_adapters(
            "test_resize_restores_wrapped_line_buffer_content_and_cursor",
            "test_bounded_wide_reflow_keeps_cursor_on_surviving_glyph",
        )

    def test_row_major_run_spans_three_rows(self):
        self._run_public_adapters(
            "test_stream_write_from_mid_row_spans_the_same_linear_run"
        )

    def test_ris_resets_vertical_and_horizontal_regions(self):
        self._run_public_adapters("test_ris_resets_both_scroll_regions_to_the_page")

    def test_declrmm_controls_whether_columns_limit_scroll_region(self):
        self._run_public_adapters(
            "test_scroll_region_uses_columns_only_while_declrmm_is_enabled"
        )

    def test_ech_repairs_complete_wide_glyph(self):
        self._run_public_adapters(
            "test_ech_on_a_wide_continuation_erases_the_complete_glyph"
        )

    def test_cr_uses_page_or_active_left_margin(self):
        self._run_public_adapters("test_carriage_return_uses_the_active_left_margin")

    def test_public_reset_clears_bounded_unbounded_and_empty_history(self):
        self._run_public_adapters(
            "test_ris_with_bounded_history_leaves_no_saved_rows",
            "test_ris_discards_unbounded_available_scrollback",
            "test_ris_on_an_empty_screen_is_idempotent",
        )

    def test_public_reset_is_independent_of_cursor_content_position(self):
        self._run_public_adapters(
            "test_ris_ignores_a_cursor_below_the_last_nonempty_row",
            "test_ris_ignores_a_cursor_at_the_end_of_content",
            "test_ris_ignores_a_cursor_within_existing_content",
            "test_ris_discards_unbounded_available_scrollback",
            "test_ris_on_an_empty_screen_is_idempotent",
        )


if __name__ == "__main__":
    unittest.main()

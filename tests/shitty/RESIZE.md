# Vertical resize assertion review

Reviewed 2026-11-12 against the pinned Shitty sources, after the user's explicit
choice: move output with the lower edge **only when the cursor is already on the
last row**. This is an intentional UI policy, not a claim of full compatibility.
Short output stays at the top; alternate-screen behavior is unchanged.

Height shrink now saves the displaced primary rows instead of freeing them.
Growth at the bottom retrieves history and then pads above the output when
history is exhausted. Synthetic padding is tracked so a resize cycle does not
create blank scrollback. Explicit writes materialize that padding. Height
changes preserve a parked viewport where history permits. Width-only policy,
fixed HISTSIZE=2000, selection invalidation and lack of reflow/grapheme storage
remain as before.

The final Python delta is 34 former assertion failures now passing, five former
passes becoming deliberate policy differences, and 21 changed assertion
fingerprints. Exclusions and nested corpora are unchanged. Every changed failure
was checked against its source function; all remain AssertionError. No crash,
missing adapter API or sanitizer diagnostic was accepted. Ordinary and sanitized
Python dispositions/fingerprints agree. The five new differences are explicitly
listed below, not hidden by a changed assertion or skip.

Four no/empty-history Ghostty cases require output to remain at the top with
unchanged cursor coordinates after a full 3-row screen grows to 10. Their helper
removes trailing blank rows only: our seven leading blanks therefore fail the
original text assertion. The requested behavior intentionally moves the same
three content rows and cursor to the bottom. Old ConPTY requires history/base to
remain 10 after growing by five rows; st now restores those five history rows,
leaving base 5. Both policies are covered directly by native/X11 tests.

Other changed failures either reach a later assertion after history restoration,
retain a known fixed-capacity/selection/reflow/grapheme difference, or encounter
the same intentional padding-at-top policy. An early assertion failure does not
claim coverage of later checks. This review is a self-review; the independent
review in REVIEW.md predates these changes.

## Former passes with intentional policy differences

- `test_ghostty_pagelist_clone_resize.GhosttyPageListCloneResizeTest.test_no_reflow_height_growth_keeps_existing_rows_and_cursor`
- `test_ghostty_screen_resize_history.GhosttyScreenResizeHistoryTest.test_no_reflow_height_growth_preserves_hard_rows`
- `test_ghostty_screen_resize_history.GhosttyScreenResizeHistoryTest.test_height_growth_without_scrollback_does_not_move_cursor`
- `test_ghostty_screen_resize_history.GhosttyScreenResizeHistoryTest.test_height_growth_with_empty_scrollback_does_not_move_cursor`
- `test_xtermjs_buffer.XtermJsBufferTest.test_old_conpty_growth_preserves_the_base_and_appends_rows`

## Existing assertion differences with changed fingerprints

- `test_alacritty_grid_storage.AlacrittyGridStorageTest.test_rotation_followed_by_shrink_keeps_the_newest_logical_tail`: Fixed history limit (2000) differs from the requested source capacity; displaced rows are now retained.
- `test_alacritty_grid_storage.AlacrittyGridStorageTest.test_growing_rotated_page_pulls_history_before_adding_blanks`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_alacritty_terminal_core.AlacrittyTerminalCoreTest.test_growing_active_screen_pulls_history_and_moves_cursor`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_contour_grid.ContourGridTest.test_height_growth_restores_history_and_appends_blanks`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_contour_grid.ContourGridTest.test_hard_lines_are_reflowed_but_never_joined`: Line reflow remains unsupported; restored history and/or top padding changes the text diagnostic.
- `test_contour_screen.ContourScreenTest.test_unscroll_via_page_growth`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_contour_screen.ContourScreenTest.test_resize_source_contour_scenario`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_ghostty_pagelist_clone_resize.GhosttyPageListCloneResizeTest.test_no_reflow_height_growth_pulls_history_above_a_bottom_cursor`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_ghostty_pagelist_clone_resize.GhosttyPageListCloneResizeTest.test_selection_anchor_can_move_from_active_screen_into_scrollback`: History text now survives; the next assertion still fails because resize invalidates selection.
- `test_ghostty_pagelist_limits.GhosttyPageListLimitsTest.test_history_limit_remains_enforced_across_resize_and_sessions`: Fixed history limit (2000) differs from the requested source capacity; displaced rows are now retained.
- `test_ghostty_pagelist_resize_no_reflow.GhosttyPageListResizeNoReflowTest.test_height_growth_contains_a_previously_parked_viewport`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_ghostty_pagelist_resize_no_reflow.GhosttyPageListResizeNoReflowTest.test_combined_shrink_keeps_a_near_top_anchor_in_scrollback`: History text now survives; the next assertion still fails because resize invalidates selection.
- `test_ghostty_screen_resize_history.GhosttyScreenResizeHistoryTest.test_no_reflow_height_growth_recovers_history_at_cursor_end`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_ghostty_screen_resize_history.GhosttyScreenResizeHistoryTest.test_no_reflow_height_growth_preserves_soft_wrap_flags`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_ghostty_screen_resize_reflow.GhosttyScreenResizeReflowTest.test_growth_in_both_dimensions_undoes_soft_wraps`: Line reflow remains unsupported; restored history and/or top padding changes the text diagnostic.
- `test_ghostty_screen_resize_reflow.GhosttyScreenResizeReflowTest.test_growth_resolves_pending_wrap_to_the_next_insertion_column`: Line reflow remains unsupported; restored history and/or top padding changes the text diagnostic.
- `test_ghostty_screen_resize_wide_prompt.GhosttyScreenResizeWidePromptTest.test_growing_rows_while_shrinking_columns_reflows_history`: Line reflow remains unsupported; restored history and/or top padding changes the text diagnostic.
- `test_resize_cursor_autowrap.ResizeCursorAutowrapTest.test_grow_restores_rows_scrolled_only_for_cursor_visibility`: History is restored, but the source expects excess blanks below the content or an unchanged cursor instead of bottom anchoring.
- `test_resize_history_capacity.ResizeHistoryCapacityTest.test_capacity_keeps_only_newest_rows_after_resize_cycles`: Fixed history limit (2000) differs from the requested source capacity; displaced rows are now retained.
- `test_resize_viewport.ResizeViewportTest.test_a_scrolled_view_survives_growing_and_shrinking`: Fixed history limit (2000) differs from the requested source capacity; displaced rows are now retained.
- `test_resize_wide_grapheme.ResizeWideGraphemeTest.test_grapheme_payload_survives_width_and_height_resize`: Existing grapheme/selection limitation, with changed coordinates after bottom anchoring.

## Former assertion differences now passing

- `test_alacritty_grid_storage.AlacrittyGridStorageTest.test_shrinking_at_bottom_moves_evicted_prefix_into_history`
- `test_alacritty_grid_storage.AlacrittyGridStorageTest.test_shrink_then_grow_reuses_history_in_logical_order`
- `test_alacritty_terminal_core.AlacrittyTerminalCoreTest.test_shrinking_active_screen_pushes_rows_to_history`
- `test_contour_grid.ContourGridTest.test_height_shrink_moves_only_rows_above_cursor_to_history`
- `test_ghostty_pagelist_compression.GhosttyPageListCompressionTest.test_active_boundary_growth_and_shrink_preserve_content`
- `test_ghostty_pagelist_compression.GhosttyPageListCompressionTest.test_history_made_active_by_height_growth_is_restored_on_demand`
- `test_ghostty_screen_resize_reflow.GhosttyScreenResizeReflowTest.test_height_shrink_with_empty_scrollback_retains_clipped_rows`
- `test_ghostty_screen_resize_reflow.GhosttyScreenResizeReflowTest.test_height_shrink_with_history_retains_all_rows`
- `test_ghostty_screen_resize_reflow.GhosttyScreenResizeReflowTest.test_height_shrink_at_capacity_keeps_cursor_bottom_anchored`
- `test_iterm2_legacy_grid_tail_semantic_head.ITerm2LegacyGridTailSemanticHeadTest.test_height_growth_restores_newest_regular_history_line`
- `test_iterm2_legacy_grid_tail_semantic_head.ITerm2LegacyGridTailSemanticHeadTest.test_height_growth_restores_complete_wrapped_history_line`
- `test_iterm2_legacy_grid_tail_semantic_head.ITerm2LegacyGridTailSemanticHeadTest.test_height_growth_restores_empty_history_line`
- `test_iterm2_legacy_grid_tail_semantic_head.ITerm2LegacyGridTailSemanticHeadTest.test_height_growth_restores_history_larger_than_storage_block`
- `test_iterm2_legacy_screen_annotation_restore.ITerm2LegacyScreenAnnotationRestoreTest.test_empty_history_line_restores_background_color`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_height_growth_pops_only_last_segment_of_long_history_line`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_height_growth_pops_whole_short_history_line`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_height_growth_removes_two_newest_wrapped_segments`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_height_growth_can_consume_all_wrapped_history_segments`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_height_growth_removes_only_newest_of_multiple_raw_lines`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_consuming_only_raw_history_line_resets_history_state`
- `test_iterm2_line_block.ITerm2LineBlockTest.test_history_entry_count_tracks_append_and_height_pop`
- `test_iterm2_line_buffer.ITerm2LineBufferTest.test_height_growth_pops_the_newest_history_row_without_mutating_snapshot`
- `test_iterm2_vt100_grid.ITerm2VT100GridTest.test_scrollback_roundtrip_preserves_cursor_column`
- `test_iterm2_vt100_grid.ITerm2VT100GridTest.test_height_growth_consumes_the_newest_regular_history_line`
- `test_iterm2_vt100_grid.ITerm2VT100GridTest.test_height_growth_consumes_a_complete_wrapped_history_line`
- `test_iterm2_vt100_grid.ITerm2VT100GridTest.test_height_growth_consumes_an_empty_newest_history_line`
- `test_iterm2_vt100_grid.ITerm2VT100GridTest.test_height_growth_consumes_a_history_line_larger_than_a_storage_block`
- `test_resize_viewport.ResizeViewportTest.test_height_shrink_keeps_scrolled_view_anchored`
- `test_resize_viewport.ResizeViewportTest.test_height_grow_keeps_same_top_row_when_possible`
- `test_scrollback.ScrollbackTest.test_shrink_moves_clipped_top_rows_to_scrollback`
- `test_scrollback.ScrollbackTest.test_grow_restores_newest_rows_from_scrollback`
- `test_xtermjs_buffer.XtermJsBufferTest.test_height_reduction_exposes_backing_rows_above_the_cursor`
- `test_xtermjs_buffer.XtermJsBufferTest.test_height_growth_reveals_more_backing_rows_above_the_viewport`
- `test_xtermjs_buffer.XtermJsBufferTest.test_height_growth_keeps_a_viewport_parked_at_the_top`

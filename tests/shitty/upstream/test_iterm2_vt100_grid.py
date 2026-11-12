# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 158 iTerm2 VT100Grid cases."""

import unittest

from harness import Shitty, put_rows


PORTED_CASES = (
    "testAppendLineToLineBuffer",
    "testAppendLinesWithContinuationMarks",
    "testAppendSoftContinuationThenHardEolJoinsIntoOneLine",
    "testAppendLinesRespectsCursorPosition",
    "testCursorHoistedFromBlankLineAfterSoftEOL",
    "testLengthOfLineNumber",
    "testMoveCursorDownOneLineNoScroll",
    "testMoveCursorDownOneLineBelowScrollRegionButAboveLastLine",
    "testMoveCursorDownOneLineWholeScreenScrolls",
    "testWholeScreenScrollRespectsSoftEOLs",
    "testScrollRegionFullWidthAtTopScrollsOnlyRegion",
    "testMoveCursorDownOneLineRegionScrollWithoutScrollback",
    "testWholeScreenScrollWithMaxLinesDropsOldLines",
    "testScrollRegionWithRowsAndColsScrollsWithinRegionOnly",
    "testMoveCursorLeft_DefaultBehavior",
    "testMoveCursorLeft_AtScrollRegionLeftEdge_DoesNotMove",
    "testMoveCursorLeft_WithinScrollRegion_MovesLeft",
    "testMoveCursorLeft_OutsideScrollRegion_MovesNormally",
    "testMoveCursorLeftWrappingAroundSoftEOL",
    "testMoveCursorLeftWrappingAroundDoubleWideCharEOL",
    "testMoveCursorLeftNotWrappingAroundHardEOL",
    "testMoveCursorRight_DefaultBehavior",
    "testMoveCursorRight_WithScrollRegion_NoScrollbackBeforeRegion",
    "testMoveCursorRight_WithScrollRegion_EnteringRegion",
    "testMoveCursorRight_WithScrollRegion_AtRegionEnd_NoMove",
    "testMoveCursorUp_DefaultBehavior",
    "testMoveCursorUp_ClampsAtScrollRegionTop",
    "testMoveCursorUp_AboveScrollTop_DoesNotClamp",
    "testMoveCursorDown_DefaultBehavior",
    "testMoveCursorDown_ClampsAtScrollRegionBottom",
    "testMoveCursorDown_BelowScrollRegion_DoesNotClamp",
    "testScrollUpIntoLineBuffer",
    "testScrollUpIntoLineBuffer_DroppedLinesCount",
    "testScrollUpIntoLineBuffer_HorizontalRegion_NoScrollback",
    "testScrollWholeScreenUpIntoLineBuffer_DroppedLinesCountAndContent",
    "testScrollRectDownBy_ZeroDoesNothingAndMarksAllCellsDirty",
    "testScrollRectDownBy_One_MarksRegionLinesDirty",
    "testScrollRectDownBy_NegativeOne_MarksRegionLinesDirty",
    "testScrollRectDownBy_Two_MarksRegionLinesDirty",
    "testScrollRectDownBy_NegativeTwo_MarksRegionLinesDirty",
    "testScrollRectDownBy_Height_EqualsRegionHeight_MarksRegionLinesDirty",
    "testScrollRectDownBy_NegativeHeight_EqualsRegionHeight_MarksRegionLinesDirty",
    "testScrollRectDownBy_GreaterThanRegionHeight_MarksRegionLinesDirty",
    "testScrollRectDownBy_NegativeGreaterThanRegionHeight_MarksRegionLinesDirty",
    "testScrollRectDownBy_NegativeOne_CleansUpBrokenSplitDwc",
    "testScrollRectDownBy_One_CleansSplitDWCAtTop",
    "testScrollRectDownBy_NegativeOne_FullRegion_CleansSplitDwc",
    "testScrollRectDownBy_NegativeOne_CleansUpOrphanedSplitDWCAndMarksDirty",
    "testScrollRectDownBy_NegativeOne_EdgeCaseSplitDwcOrphans",
    "testScrollRectDownBy_NegativeOne_RegionFromCol1ToRightMargin_CleansSplitDwcAndMarksDirty",
    "testScrollRectDownBy_NegativeOneEdgeCaseOrphans",
    "testScrollRectDownBy_EmptyRectIsHarmless",
    "testScrollRectDownBy_NegativeOne_MoveOneDwcReplaced",
    "testScrollRectDownBy_MoveContinuationMarkToEdgeOfRect",
    "testScrollRectDownBy_MoveContinuationMarkToEdgeOfRect_ScrollUp",
    "testScrollRectDownBy_ContinuationMarksCleanedBeforeScrollingDown",
    "testScrollRectDownBy_Two_CleansContinuationMarksInFullWidth",
    "testScrollRectDownBy_NegativeOne_CleansContinuationMarksInFullWidth",
    "testScrollRectDownBy_NegativeTwo_CleansContinuationMarksInFullWidth",
    "testScrollRectDownBy_One_CleansContinuationMarksWithPartialWidth",
    "testScrollRectDownBy_Two_CleansContinuationMarksWithPartialWidth",
    "testScrollRectDownBy_One_CleansContinuationMarksWithPartialWidthAndDwcSkip",
    "testScrollRectDownBy_NegativeOne_CleansContinuationMarksWithPartialWidth",
    "testScrollRectDownBy_NegativeOne_CleansContinuationMarksWithPartialWidthAndDwcSkip",
    "testScrollRectDownBy_NegativeTwo_CleansContinuationMarksWithPartialWidth",
    "testSetContentsFromDVRFrame",
    "testSetBgFgColorInRect",
    "testRestoreScreenFromLineBuffer",
    "testRestoreScreenFromLineBufferCursorAfterPartialDropWithDWC",
    "testRectsForRun",
    "testResetScrollRegions",
    "testScrollRegionRect",
    "testEraseDwc",
    "testMoveCursorToLeftMargin",
    "testResetWithLineBufferLeavingBehindZero",
    "testResetWithLineBufferLeavingBehindCursorLine_CursorBelowContent",
    "testResetWithLineBufferLeavingBehindCursorLine_CursorAtEndOfContent",
    "testResetWithLineBufferLeavingBehindCursorLine_CursorWithinContent",
    "testResetWithLineBufferLeavingBehindCursorLine_UnlimitedScrollback",
    "testResetWithLineBufferLeavingBehindCursorLine_EmptyScreen",
    "testMoveWrappedCursorLineToTopOfGrid",
    "testAppendCharsAtCursor",
    "testAppendCharsAtCursor_ScrollingIntoLineBuffer",
    "testAppendCharsAtCursor_NoScrollingWithVsplit",
    "testAppendCharsAtCursor_ScrollingWithScrollRegion",
    "testAppendCharsAtCursor_NoScrollingWithRegionAndScrollbackDisabled",
    "testAppendCharsAtCursor_NoScrollingWithHVRegions",
    "testAppendCharsAtCursor_UnlimitedScrollback",
    "testAppendCharsAtCursor_DWC",
    "testAppendCharsAtCursor_DWCSplitToNextLine",
    "testAppendCharsAtCursor_DWCSplitAtVsplit",
    "testAppendCharsAtCursor_WraparoundMode",
    "testAppendCharsAtCursor_WraparoundModeWithVsplit",
    "testInsertModeWithPlainText",
    "testInsertOrphaningDWCs",
    "testInsertStompingDWCSkip",
    "testInsertLongStringWithWraparound",
    "testInsertLongStringWithoutWraparound",
    "testInsertModeWithVSplit",
    "testInsertWrappingStringWithVSplit",
    "testInsertOrphaningDWCAtEndOfLineWithVSplit",
    "testOverwriteLeftHalfOfDWC",
    "testAppendCharsWithAnsiTerminalAndWraparoundMode",
    "testAppendCharsWithAnsiTerminalAndWraparoundModeOff",
    "testOverwritingDwcSkipConvertsEolDwcToEolSoft",
    "testOverwritingDwcSkipAndWrapping",
    "testCoordinateBefore_BasicCase",
    "testCoordinateBefore_FailureToMoveBeforeGrid",
    "testCoordinateBefore_WrapBackOverSoftEOL",
    "testCoordinateBefore_FailureToWrapAcrossHardEOL",
    "testCoordinateBefore_WrapBackOverEOLDWC",
    "testCoordinateBefore_ScrollRegionColsAffectsWrap",
    "testCoordinateBefore_MovingBackOverDWC_RIGHT",
    "testCoordinateBefore_WrapAndSkipOverDWC",
    "testDeleteChars_base",
    "testDeleteChars_tooMany",
    "testDeleteChars_delete0",
    "testDeleteChars_deleteLeftHalfDWC",
    "testDeleteChars_deleteRightHalfDWC",
    "testDeleteChars_breakSkip",
    "testDeleteChars_scrollRegion",
    "testDeleteChars_scrollRegionDeleteBignum",
    "testDeleteChars_scrollRegionDeleteRightDWC",
    "testDeleteChars_scrollRegionBoundaryOverlapsLeftHalfDWC",
    "testDeleteChars_scrollRegionBoundaryOverlapsRightHalfDWC",
    "testDeleteChars_scrollRegionDWCSkipSurvives",
    "testDeleteChars_scrollRegionOutside",
    "testInsertChar_base",
    "testInsertChar_tooMany",
    "testInsertChar_nonNullChar",
    "testInsertChar_zero",
    "testInsertChar_middleOfDwc",
    "testInsertChar_removeDwcSkip",
    "testInsertChar_breakDwcSkip",
    "testInsertChar_breakDwcSkipHardWrap",
    "testInsertChar_scrollRegion",
    "testInsertChar_scrollRegionOverflow",
    "testInsertChar_orphanLeftDwc",
    "testInsertChar_orphanRightDwc",
    "testInsertChar_dwcSkipWithScrollRegion",
    "testInsertChar_outsideScrollRegion",
    "testMoveCursorRightToMargin",
    "testAppendingLongLineAtBottomOfScrollRegionGivesSoftBreak",
    "testGridRunFromRangeBasic",
    "testGridRunFromRange_SpansLines",
    "testGridRunFromRange_StartsOnSubsequentLine",
    "testGridRunFromRange_WithPositiveRowOffset",
    "testGridRunFromRange_NegativeRow_NoTruncation",
    "testGridRunFromRange_NegativeRow_TruncatedStart",
    "testGridRunFromRange_NegativeRow_CompletelyTruncated",
    "testSingleColumnLineBuffer",
    "testRemoveLastLineRegular",
    "testRemoveLastRawLineWrapped",
    "testRemoveLastRawLineEmpty",
    "testRemoveLastRawLineLargerThanBlockSize",
    "testRemoveLastRawLineEmptyBuffer",
    "testBCE_ScrollingUsesDefaultCharBackgroundColor",
    "testBCE_ScrollRectUsesDefaultCharBackgroundColor",
)


ROWS = put_rows(b"abcd", b"efgh", b"ijkl", b"mnop")
LARGE_ROWS = put_rows(b"abcde", b"fghij", b"klmno", b"pqrst", b"uvwxy")


class ITerm2VT100GridTest(unittest.TestCase):
    def test_upstream_inventory_has_all_158_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 158)
        self.assertEqual(len(set(PORTED_CASES)), 158)

    def test_append_line_to_line_buffer_is_visible_in_scrollback(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abcd", "efgh"])
            self.assertFalse(snapshot.cell(3, 0).wrapped)

    def test_appended_lines_keep_hard_and_soft_continuation_marks(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"abcd\r\nefghi\x1b[4;1H\x1bD\x1bD")
            terminal.wheel_up(2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abcd", "efgh"])
            self.assertFalse(snapshot.cell(3, 0).wrapped)
            self.assertTrue(snapshot.cell(3, 1).wrapped)

    def test_soft_continuation_then_hard_eol_is_one_logical_line(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"abcdefgh\r\n\x1b[4;1H\x1bD\x1bD")
            terminal.wheel_up(2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abcd", "efgh"])
            self.assertTrue(snapshot.cell(3, 0).wrapped)
            self.assertFalse(snapshot.cell(3, 1).wrapped)

    def test_scrollback_roundtrip_preserves_cursor_column(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[4;3H")
            terminal.resize(4, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))
            self.assertEqual(terminal.scrollback_state()[0], 2)
            terminal.resize(4, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 3))

    def test_blank_cursor_after_soft_eol_reflows_to_logical_line_end(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"abcdefghi\x1b[3;1H\x1b[P")
            terminal.resize(8, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "abcdefgh")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 0))
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"X")
            self.assertEqual(terminal.snapshot().lines[:2], ["abcdefgh", "X       "])

    def test_public_line_lengths_match_drawn_cell_prefixes(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(put_rows(b"abcd", b"efg"))
            snapshot = terminal.snapshot()
            self.assertEqual(
                [
                    sum(snapshot.cell(column, row).drawn for column in range(4))
                    for row in range(3)
                ],
                [4, 3, 0],
            )

    def test_index_without_boundary_moves_down_without_scrolling(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;1H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_index_below_scroll_region_moves_until_page_bottom(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;2r\x1b[3;1H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_index_at_full_screen_bottom_scrolls_into_history(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["efgh", "ijkl", "mnop", "    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[0], "abcd")

    def test_full_screen_scroll_preserves_soft_eol_in_history(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(
                b"abcde"
                b"\x1b[2;1Hefgh"
                b"\x1b[3;1Hijkl"
                b"\x1b[4;1Hmnop"
                b"\x1b[4;1H\x1bD"
            )
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abcd", "efgh"])
            self.assertTrue(snapshot.cell(3, 0).wrapped)

    def test_top_anchored_full_width_region_scrolls_only_its_rows(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[1;2r\x1b[2;1H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["efgh", "    ", "ijkl", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))
            self.assertEqual(terminal.scrollback_state()[0], 1)

    def test_non_top_region_scroll_does_not_create_scrollback(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[2;3r\x1b[3;1H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "ijkl", "    ", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_bounded_scrollback_keeps_only_the_newest_scrolled_line(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD\x1bD\x1bD")
            self.assertEqual(terminal.snapshot().lines, ["mnop", "    ", "    ", "    "])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[:2], ["ijkl", "mnop"])

    def test_row_and_column_region_scrolls_only_the_rectangle(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(
                ROWS
                + b"\x1b[?69h"
                + b"\x1b[2;3s"
                + b"\x1b[2;3r"
                + b"\x1b[3;2H\x1bD"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "ejkh", "i  l", "mnop"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_cursor_left_default_clamps_at_page_edge(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[1;2H\x1b[D\x1b[D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_cursor_left_at_horizontal_margin_does_not_move(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;3s\x1b[1;2H\x1b[D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_cursor_left_within_horizontal_margin_moves_to_margin(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;3s\x1b[1;3H\x1b[D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_cursor_left_right_of_horizontal_margin_moves_once(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;3s\x1b[1;4H\x1b[D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

    @unittest.expectedFailure
    def test_iterm_default_cub_wraps_across_soft_eol(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"abcdef\x1b[4D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

    @unittest.expectedFailure
    def test_iterm_default_cub_wraps_across_early_wide_eol(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write("ab界".encode("utf-8") + b"\x1b[4D")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_cursor_left_does_not_cross_a_hard_eol(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"abc\r\nd\x1b[4D")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abc ", "d   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_cursor_right_default_moves_one_column(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[1;3H\x1b[C")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))

    def test_cursor_right_before_horizontal_region_moves_normally(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;4s\x1b[1;1H\x1b[C")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_cursor_right_can_enter_horizontal_region(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;4s\x1b[1;2H\x1b[C")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

    def test_cursor_right_stops_at_horizontal_region_end(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;4s\x1b[1;4H\x1b[C")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))

    def test_cursor_up_default_clamps_at_page_top(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[3;1H\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 1)
            terminal.write(b"\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 0)
            terminal.write(b"\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 0)

    def test_cursor_up_clamps_at_vertical_region_top(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[2;3r\x1b[3;1H\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 1)
            terminal.write(b"\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 1)

    def test_cursor_up_above_vertical_region_moves_to_page_top(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[3;4r\x1b[2;1H\x1b[A")
            self.assertEqual(terminal.snapshot().cursor_y, 0)

    def test_cursor_down_default_clamps_at_page_bottom(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[3;1H\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 3)
            terminal.write(b"\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 3)

    def test_cursor_down_clamps_at_vertical_region_bottom(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[2;3r\x1b[2;1H\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 2)
            terminal.write(b"\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 2)

    def test_cursor_down_below_vertical_region_moves_to_page_bottom(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"\x1b[1;2r\x1b[3;1H\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 3)
            terminal.write(b"\x1b[B")
            self.assertEqual(terminal.snapshot().cursor_y, 3)

    def test_scroll_up_moves_top_row_into_history(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["efgh", "ijkl", "mnop", "    "])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[0], "abcd")

    def test_scroll_up_bounded_history_drops_oldest_row(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(ROWS)
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(terminal.snapshot().lines, ["ijkl", "mnop", "    ", "    "])
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[:2], ["efgh", "ijkl"])

    def test_horizontal_region_scroll_does_not_create_history(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["afgd", "ejkh", "inol", "m  p"],
            )
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_repeated_whole_screen_scroll_keeps_newest_history_tail(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(ROWS + b"\x1b[S\x1b[4;1Hqrst\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["ijkl", "mnop", "qrst", "    "])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[:2], ["efgh", "ijkl"])

    def test_wire_zero_scroll_down_defaults_to_one_row(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[2;3r")
            terminal.write(b"\x1b[0T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcd", "e  h", "ifgl", "mnop"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2))

    def test_rectangular_scroll_down_one_damages_region_rows(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[2;3r")
            terminal.write(b"\x1b[T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcd", "e  h", "ifgl", "mnop"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2))

    def test_rectangular_scroll_up_one_damages_region_rows(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[2;3r")
            terminal.write(b"\x1b[S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcd", "ejkh", "i  l", "mnop"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2))

    def test_rectangular_scroll_down_two_damages_region_rows(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[2T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "pghit", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_rectangular_scroll_up_two_damages_region_rows(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[2S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "fqrsj", "k   o", "p   t", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_rectangular_scroll_down_by_region_height_blanks_region(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[3T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "p   t", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_rectangular_scroll_up_by_region_height_blanks_region(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[3S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "p   t", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_rectangular_scroll_down_clamps_count_to_region_height(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[4T")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "p   t", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_rectangular_scroll_up_clamps_count_to_region_height(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(LARGE_ROWS + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
            terminal.write(b"\x1b[4S")
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "p   t", "uvwxy"],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_partial_scroll_up_clears_a_wide_source_cut_at_left_edge(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"1234567", b"a" + wide + b"xyz")
                + b"\x1b[?69h\x1b[3;7s"
            )
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["12 xyz ", "a      "])
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_partial_scroll_down_clears_a_wide_source_cut_at_right_edge(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"abc" + wide + b"yz", b"1234567")
                + b"\x1b[?69h\x1b[1;4s"
            )
            terminal.write(b"\x1b[T")
            self.assertEqual(terminal.snapshot().lines, ["     yz", "abc 567"])
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_full_width_scroll_moves_a_wrapped_wide_glyph_intact(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=3,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"ab" + wide + b"cd")
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["界 c", "d  ", "   "])
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))

    def test_partial_scroll_cleans_orphaned_wide_cells_on_every_row(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=6,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(
                    b"a" + wide + b"A" + wide + b"z",
                    b"b" + wide + b"B" + wide + b"y",
                    b"c" + wide + b"C" + wide + b"x",
                    b"d" + wide + b"D" + wide + b"w",
                    b"e" + wide + b"E" + wide + b"v",
                    b"f" + wide + b"F" + wide + b"u",
                )
                + b"\x1b[?69h\x1b[3;5s"
            )
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["a  B  z", "b  C  y", "c  D  x", "d  E  w", "e  F  v", "f     u"],
            )
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))
            self.assertEqual(terminal.last_update_rows(), tuple(range(6)))

    def test_partial_scroll_repairs_destination_edges_only_inside_vertical_region(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(
                    b"a" + wide + b"x" + wide + b"z",
                    b"b" + wide + b"y" + wide + b"q",
                    b"c12v34r",
                )
                + b"\x1b[?69h\x1b[3;5s\x1b[2;3r"
            )
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["a界 x界 z", "b 2v3 q", "c1   4r"])
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)
            self.assertEqual(terminal.last_update_rows(), (1, 2))

    def test_partial_scroll_to_right_margin_repairs_left_wide_boundary(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"1234567", wide + b"ABCDE")
                + b"\x1b[?69h\x1b[2;7s"
            )
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["1 ABCDE", "       "])
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_partial_scroll_from_left_margin_repairs_right_wide_boundary(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"1234567", b"ABCDE" + wide)
                + b"\x1b[?69h\x1b[1;6s"
            )
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["ABCDE 7", "       "])
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_invalid_zero_height_scroll_region_is_harmless(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(ROWS)
            terminal.write(b"\x1b[2;2r")
            self.assertEqual(terminal.snapshot().lines, ["abcd", "efgh", "ijkl", "mnop"])
            self.assertEqual(terminal.last_update_rows(), ())

    def test_partial_scroll_preserves_complete_wide_and_repairs_cut_one(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"1234567", wide + b"A" + wide + b"B")
                + b"\x1b[?69h\x1b[2;6s\x1b[1;2r"
            )
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "1 A界 B7")
            self.assertTrue(snapshot.cell(3, 0).double_width)
            self.assertTrue(snapshot.cell(4, 0).double_width_continuation)
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_partial_scroll_down_keeps_complete_wide_at_rectangle_edge(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"aBC" + wide + b"z", b"1234567")
                + b"\x1b[?69h\x1b[2;5s"
            )
            terminal.write(b"\x1b[T")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["a    z ", "1BC界 67"])
            self.assertTrue(snapshot.cell(3, 1).double_width)
            self.assertTrue(snapshot.cell(4, 1).double_width_continuation)
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_partial_scroll_up_keeps_complete_wide_at_rectangle_edge(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"1234567", b"aBC" + wide + b"z")
                + b"\x1b[?69h\x1b[2;5s"
            )
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["1BC界 67", "a    z "])
            self.assertTrue(snapshot.cell(3, 0).double_width)
            self.assertTrue(snapshot.cell(4, 0).double_width_continuation)
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_full_width_scroll_down_preserves_moved_soft_wrap_metadata(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\x1b[2;4r")
            terminal.write(b"\x1b[T")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "    ", "efgh", "ijkl", "qrst"])
            self.assertEqual([snapshot.cell(3, row).wrapped for row in range(5)], [True, False, True, True, False])
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_full_width_scroll_down_two_preserves_source_soft_wrap(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\x1b[2;4r")
            terminal.write(b"\x1b[2T")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "    ", "    ", "efgh", "qrst"])
            self.assertEqual([snapshot.cell(3, row).wrapped for row in range(5)], [True, False, False, True, False])
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_full_width_scroll_up_preserves_moved_soft_wrap_metadata(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\x1b[2;4r")
            terminal.write(b"\x1b[S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "ijkl", "mnop", "    ", "qrst"])
            self.assertEqual([snapshot.cell(3, row).wrapped for row in range(5)], [True, True, True, False, False])
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_full_width_scroll_up_two_preserves_source_soft_wrap(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\x1b[2;4r")
            terminal.write(b"\x1b[2S")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "mnop", "    ", "    ", "qrst"])
            self.assertEqual([snapshot.cell(3, row).wrapped for row in range(5)], [True, True, False, False, False])
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_partial_width_scroll_preserves_each_rows_soft_wrap_metadata(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"abcdefghijklmnopqrst"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r"
            )
            terminal.write(b"\x1b[T")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "e   ", "ifgh", "mjkl", "qrst"])
            self.assertEqual([snapshot.cell(3, row).wrapped for row in range(5)], [True, True, True, True, False])
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3))

    def test_partial_width_scroll_down_two_preserves_destination_row_endings(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"abcdefghijklmnopqrst"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[2T"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "e   ", "i   ", "mfgh", "qrst"])
            self.assertEqual(
                [snapshot.cell(3, row).wrapped for row in range(5)],
                [True, True, True, True, False],
            )

    def test_partial_width_scroll_down_repairs_a_dwc_skip_destination(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=5,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                b"abcdefghijk" + wide + b"opqrst"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[T"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "e   ", "ifgh", " jk ", "qrst"])
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_partial_width_scroll_up_one_preserves_destination_row_endings(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"abcdefghijklmnopqrst"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[S"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "ejkl", "inop", "m   ", "qrst"])
            self.assertEqual(
                [snapshot.cell(3, row).wrapped for row in range(5)],
                [True, True, True, True, False],
            )

    def test_partial_width_scroll_up_repairs_both_dwc_skip_boundaries(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=5,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                b"abc" + wide + b"ghijklmno" + wide + b"st"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[S"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abc ", " jkl", "ino ", "m   ", "界 st"])
            self.assertFalse(snapshot.cell(0, 1).double_width)
            self.assertFalse(snapshot.cell(0, 3).double_width)
            self.assertTrue(snapshot.cell(0, 4).double_width)
            self.assertTrue(snapshot.cell(1, 4).double_width_continuation)

    def test_partial_width_scroll_up_two_preserves_destination_row_endings(self):
        with Shitty(columns=4, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"abcdefghijklmnopqrst"
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[2S"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "enop", "i   ", "m   ", "qrst"])
            self.assertEqual(
                [snapshot.cell(3, row).wrapped for row in range(5)],
                [True, True, True, True, False],
            )

    def test_public_resize_restores_a_frame_at_smaller_and_larger_geometry(self):
        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"\x1b[?1049h" + ROWS + b"\x1b[3;2H")
            terminal.resize(3, 3)
            smaller = terminal.snapshot()
            self.assertEqual(smaller.lines, ["abc", "efg", "ijk"])
            self.assertEqual((smaller.cursor_x, smaller.cursor_y), (1, 2))

        with Shitty(columns=4, rows=4, save_lines=4) as terminal:
            terminal.write(b"\x1b[?1049h" + ROWS + b"\x1b[3;2H")
            terminal.resize(5, 5)
            larger = terminal.snapshot()
            self.assertEqual(larger.lines, ["abcd ", "efgh ", "ijkl ", "mnop ", "     "])
            self.assertEqual((larger.cursor_x, larger.cursor_y), (1, 2))

    def test_deccara_can_apply_foreground_and_background_independently(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(put_rows(*(b"xxxx" for _ in range(4))))
            terminal.write(b"\x1b[2*x\x1b[2;2;3;3;38;5;1;48;5;2$r")
            snapshot = terminal.snapshot()
            for row in range(4):
                for column in range(4):
                    cell = snapshot.cell(column, row)
                    targeted = 1 <= row <= 2 and 1 <= column <= 2
                    self.assertEqual(cell.foreground, (170, 0, 0) if targeted else (255, 255, 255))
                    self.assertEqual(cell.background, (0, 170, 0) if targeted else (0, 0, 0))

            terminal.write(b"\x1b[1;1;4;4;48;5;2$r")
            snapshot = terminal.snapshot()
            self.assertTrue(all(cell.background == (0, 170, 0) for cell in snapshot.cells))
            self.assertEqual(snapshot.cell(1, 1).foreground, (170, 0, 0))

            terminal.write(b"\x1b[1;1;4;4;38;5;7$r")
            snapshot = terminal.snapshot()
            self.assertTrue(all(cell.foreground == (170, 170, 170) for cell in snapshot.cells))
            self.assertTrue(all(cell.background == (0, 170, 0) for cell in snapshot.cells))

    def test_resize_restores_wrapped_line_buffer_content_and_cursor(self):
        with Shitty(columns=8, rows=8, save_lines=8) as terminal:
            terminal.write(b"test\r\nhello world\x1b[3;1H")
            terminal.resize(2, 2)
            small = terminal.snapshot()
            self.assertEqual(small.lines, ["rl", "d "])
            self.assertEqual((small.cursor_x, small.cursor_y), (0, 0))
            terminal.resize(8, 8)
            restored = terminal.snapshot()
            self.assertEqual(restored.lines[:3], ["test    ", "hello wo", "rld     "])
            self.assertEqual((restored.cursor_x, restored.cursor_y), (0, 2))

    def test_bounded_wide_reflow_keeps_cursor_on_surviving_glyph(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=2,
            save_lines=2,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"ABCDEFGH\r\nIJK" + wide + b"NOP")
            terminal.write(b"\x1b[1;1H")
            terminal.resize(4, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["EFGH", "IJK ", "界 NO", "P   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))
            self.assertTrue(snapshot.cell(0, 2).double_width)
            self.assertTrue(snapshot.cell(1, 2).double_width_continuation)

    def test_stream_write_from_mid_row_spans_the_same_linear_run(self):
        with Shitty(columns=8, rows=8, save_lines=0) as terminal:
            terminal.write(b"\x1b[3;4H" + b"x" * 20)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[2:5], ["   xxxxx", "xxxxxxxx", "xxxxxxx "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 4))

    def test_ris_resets_both_scroll_regions_to_the_page(self):
        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;3s\x1b[2;3r\x1bc")
            terminal.write(ROWS + b"\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["efgh", "ijkl", "mnop", "    "])

    def test_scroll_region_uses_columns_only_while_declrmm_is_enabled(self):
        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[2;3r\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["abcd", "ejkh", "i  l", "mnop"])

        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(ROWS + b"\x1b[?69h\x1b[2;3s\x1b[?69l\x1b[2;3r\x1b[S")
            self.assertEqual(terminal.snapshot().lines, ["abcd", "ijkl", "    ", "mnop"])

    def test_ech_on_a_wide_continuation_erases_the_complete_glyph(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide + b"\x1b[1;3H\x1b[X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "a   ")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_carriage_return_uses_the_active_left_margin(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[1;3H\r")
            self.assertEqual(terminal.snapshot().cursor_x, 0)
            terminal.write(b"\x1b[2;3s\x1b[1;3H\r")
            self.assertEqual(terminal.snapshot().cursor_x, 0)
            terminal.write(b"\x1b[?69h\x1b[2;3s\x1b[1;3H\r")
            self.assertEqual(terminal.snapshot().cursor_x, 1)

    def _assert_ris_clears_page_and_history(self, terminal):
        terminal.write(b"\x1bc")
        snapshot = terminal.snapshot()
        self.assertTrue(all(line.isspace() for line in snapshot.lines))
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
        self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_ris_with_bounded_history_leaves_no_saved_rows(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD\x1bD")
            self._assert_ris_clears_page_and_history(terminal)

    def test_ris_ignores_a_cursor_below_the_last_nonempty_row(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(put_rows(b"0123", b"abcd", b"efgh") + b"\x1b[4;3H")
            self._assert_ris_clears_page_and_history(terminal)

    def test_ris_ignores_a_cursor_at_the_end_of_content(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(put_rows(b"0123", b"abcd", b"efgh") + b"\x1b[3;3H")
            self._assert_ris_clears_page_and_history(terminal)

    def test_ris_ignores_a_cursor_within_existing_content(self):
        with Shitty(columns=4, rows=4, save_lines=1) as terminal:
            terminal.write(put_rows(b"0123", b"abcd", b"efgh") + b"\x1b[2;3H")
            self._assert_ris_clears_page_and_history(terminal)

    def test_ris_discards_unbounded_available_scrollback(self):
        with Shitty(columns=4, rows=4, save_lines=32) as terminal:
            terminal.write(ROWS + b"\x1b[4;1H\x1bD\x1bD\x1bD")
            self.assertGreater(terminal.scrollback_state()[0], 0)
            self._assert_ris_clears_page_and_history(terminal)

    def test_ris_on_an_empty_screen_is_idempotent(self):
        with Shitty(columns=4, rows=2, save_lines=1) as terminal:
            self._assert_ris_clears_page_and_history(terminal)

    def test_standard_scroll_controls_move_a_wrapped_cursor_line_to_the_top(self):
        with Shitty(columns=4, rows=7, save_lines=0) as terminal:
            terminal.write(b"abcdefg\r\nhijklmnopq\r\nrstuvwx")
            terminal.write(b"\x1b[?69h\x1b[3;4s\x1b[2;3r\x1b[5;2H")
            terminal.write(b"\x1b[?69l\x1b[r\x1b[2S\x1b[3;2H")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["hijk", "lmno", "pq  ", "rstu", "vwx ", "    ", "    "],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))

    def test_empty_output_is_a_complete_noop(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(put_rows(b"ab", b"cd") + b"\x1b[2;2H")
            before = terminal.snapshot()
            terminal.write(b"")
            after = terminal.snapshot()
            self.assertEqual(after.lines, before.lines)
            self.assertEqual((after.cursor_x, after.cursor_y), (before.cursor_x, before.cursor_y))

    def test_bottom_wrap_scrolls_the_completed_row_into_history(self):
        with Shitty(columns=3, rows=2, save_lines=2) as terminal:
            terminal.write(put_rows(b"abc", b"d") + b"\x1b[2;2Hefgh")
            self.assertEqual(terminal.snapshot().lines, ["def", "gh "])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (2, 1))
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().lines[0], "abc")

    def test_horizontal_margin_wrap_scrolls_only_its_columns(self):
        with Shitty(columns=3, rows=2, save_lines=2) as terminal:
            terminal.write(
                put_rows(b"abc", b"d")
                + b"\x1b[?69h\x1b[2;3s\x1b[2;2Hefgh"
            )
            self.assertEqual(terminal.snapshot().lines, ["aef", "dgh"])
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_one_row_top_region_wraps_into_history(self):
        with Shitty(columns=3, rows=1, save_lines=4) as terminal:
            terminal.write(b"abcefgh")
            self.assertEqual(terminal.snapshot().lines, ["h  "])
            self.assertEqual(terminal.scrollback_state()[0], 2)
            terminal.wheel_up(2)
            history = terminal.snapshot()
            self.assertEqual(history.lines, ["abc"])
            self.assertTrue(history.cell(2, 0).wrapped)

    def test_alternate_screen_wrap_has_no_scrollback_backing(self):
        with Shitty(columns=3, rows=1, save_lines=4) as terminal:
            terminal.write(b"\x1b[?1049habcefgh")
            self.assertEqual(terminal.snapshot().lines, ["h  "])
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_one_row_rectangular_region_wraps_without_history(self):
        with Shitty(columns=3, rows=1, save_lines=4) as terminal:
            terminal.write(b"abc\x1b[?69h\x1b[2;3s\x1b[1;2Hefgh")
            self.assertEqual(terminal.snapshot().lines, ["agh"])
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_long_wrap_keeps_every_logical_row_with_large_history(self):
        with Shitty(columns=2, rows=2, save_lines=16) as terminal:
            terminal.write(put_rows(b"ab") + b"\x1b[2;1Hcdefghijklmn")
            self.assertEqual(terminal.snapshot().lines, ["kl", "mn"])
            self.assertEqual(
                terminal.all_text(),
                ("ab", "cd", "ef", "gh", "ij", "kl", "mn"),
            )
            self.assertEqual(terminal.scrollback_state()[0], 5)
            terminal.wheel_up(5)
            history = terminal.snapshot()
            self.assertFalse(history.cell(1, 0).wrapped)
            self.assertTrue(history.cell(1, 1).wrapped)

    def test_wide_glyph_advances_by_two_cells_before_wrapping(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=3,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(wide + b"bcd")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["界 b", "cd "])
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_wide_glyph_that_does_not_fit_wraps_as_a_complete_cell(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=3,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"ab" + wide + b"d")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ab ", "界 d"])
            self.assertFalse(snapshot.cell(2, 0).double_width)
            self.assertFalse(snapshot.cell(2, 0).double_width_continuation)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_wide_glyph_wraps_at_a_horizontal_margin_without_an_orphan(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"\x1b[?69h\x1b[1;3s\x1b[1;1Hab" + wide + b"d")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["ab  ", "界 d "])
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_default_wraparound_defers_until_the_following_character(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[1;1Ha\x1b[1;2Hbcd")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ab", "cd"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_horizontal_margin_wrap_uses_its_left_edge_on_the_next_row(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"a\x1b[?69h\x1b[1;2s\x1b[1;2Hbcde")
            self.assertEqual(terminal.snapshot().lines, ["cd  ", "e   "])
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_insert_mode_shifts_plain_text_to_the_right(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcdgh", b"zy") + b"\x1b[1;5H\x1b[4hef")
            self.assertEqual(terminal.snapshot().lines, ["abcdefgh", "zy      "])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (6, 0))

    def test_insert_mode_drops_a_wide_glyph_cut_by_the_right_edge(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=8,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abcdg" + wide + b"\x1b[1;5H\x1b[4hef")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "abcdefg ")
            self.assertFalse(any(snapshot.cell(column, 0).double_width for column in range(8)))
            self.assertFalse(any(snapshot.cell(column, 0).double_width_continuation for column in range(8)))

    def test_insert_mode_replaces_a_wide_wrap_spacer_with_normal_text(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=8,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abcdfgh" + wide + b"\x1b[1;5H\x1b[4he")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["abcdefgh", "界       "])
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_long_insert_mode_write_wraps_and_keeps_the_shifted_tail(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcdtuvw", b"xyz")
                + b"\x1b[1;5H\x1b[4hefghijklm"
            )
            self.assertEqual(terminal.snapshot().lines, ["abcdefgh", "ijklmxyz"])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (5, 1))

    def test_long_insert_without_wraparound_keeps_only_the_last_margin_cell(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcdtuvw", b"xyz")
                + b"\x1b[1;5H\x1b[4h\x1b[?7lefghijklm"
            )
            self.assertEqual(terminal.snapshot().lines, ["abcdefgm", "xyz     "])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (7, 0))

    def test_insert_mode_shifts_only_inside_horizontal_margins(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcde", b"xyz")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;3H\x1b[4hm"
            )
            self.assertEqual(terminal.snapshot().lines, ["abmce", "xyz  "])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (3, 0))

    def test_insert_mode_wraps_from_right_to_left_horizontal_margin(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcde", b"xyz")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;3H\x1b[4hmno"
            )
            self.assertEqual(terminal.snapshot().lines, ["abmne", "xoyz "])
            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (2, 1))

    def test_insert_at_a_horizontal_margin_erases_a_wide_glyph_cut_by_the_shift(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=6,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"abc" + wide + b"e", b"xyz")
                + b"\x1b[?69h\x1b[2;5s\x1b[1;3H\x1b[4hm"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abmc e", "xyz   "])
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_overwrite_of_a_wide_head_erases_its_continuation(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=6,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(put_rows(b"abc" + wide + b"e", b"xyz") + b"\x1b[1;3Hmn")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abmn e", "xyz   "])
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_autowrap_is_deferred_after_writing_the_right_margin(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"abc\x1b[1;4Hd")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"e")
            self.assertEqual(terminal.model_snapshot().lines, ["abcd", "e   "])

    def test_disabled_autowrap_replaces_the_right_margin_without_advancing(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"abc\x1b[?7l\x1b[1;4Hde")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abce", "    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))

    def test_overwriting_a_pre_wrap_spacer_keeps_an_ordinary_soft_wrap(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abc" + wide + b"\x1b[1;4Hd")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "界   "])
            self.assertTrue(snapshot.cell(2, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_overwritten_pre_wrap_spacer_then_wrap_replaces_the_wide_row_head(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abc" + wide + b"\x1b[1;4Hdef")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcd", "ef  "])
            self.assertTrue(snapshot.cell(3, 0).wrapped)
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_split_combining_mark_attaches_to_the_preceding_narrow_cell(self):
        with Shitty(columns=3, rows=2, save_lines=0) as terminal:
            terminal.write(b"a")
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("a"), 0x301))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_leading_combining_mark_never_attaches_forward(self):
        with Shitty(columns=3, rows=2, save_lines=0) as terminal:
            terminal.write("\u0301a".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            base_cells = [cell for cell in snapshot.cells if cell.char == "a"]
            self.assertEqual(len(base_cells), 1)
            self.assertEqual(base_cells[0].grapheme, ())

    def test_combining_mark_attaches_to_a_pending_wrap_cell(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"ab")
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(1, 0).grapheme, (ord("b"), 0x301))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_hard_line_break_prevents_combining_with_the_previous_row(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"ab\r\n")
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(1, 0).grapheme, ())
            self.assertFalse(snapshot.cell(1, 0).wrapped)

    def test_combining_mark_attaches_to_a_wide_glyph_after_pre_wrap(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=2,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide)
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertTrue(snapshot.cell(0, 0).wrapped)
            self.assertEqual(snapshot.cell(0, 1).grapheme, (ord("界"), 0x301))
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_combining_mark_at_a_pending_horizontal_margin_uses_its_right_edge_base(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"AxxD", b"EyyH")
                + b"\x1b[?69h\x1b[2;3s\x1b[1;2Hbc"
            )
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(2, 0).grapheme, (ord("c"), 0x301))
            terminal.write(b"d")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["AbcD", "EdyH"])
            self.assertTrue(snapshot.cell(2, 0).wrapped)

    def test_combining_mark_skips_a_wide_continuation(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=3,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(wide)
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("界"), 0x301))
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_combining_mark_attaches_to_a_wide_right_margin_cell(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=3,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide)
            terminal.write("\u0301".encode("utf-8"))
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(1, 0).grapheme, (ord("界"), 0x301))
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_dch_deletes_one_cell_and_shifts_the_tail_left(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd", b"efg") + b"\x1b[1;2H\x1b[P")
            self.assertEqual(terminal.model_snapshot().lines, ["acd ", "efg "])

    def test_dch_clamps_an_oversized_count_at_the_right_edge(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd", b"efg") + b"\x1b[1;2H\x1b[100P")
            self.assertEqual(terminal.model_snapshot().lines, ["a   ", "efg "])

    def test_zero_dch_parameter_follows_the_terminal_consensus_of_one(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd", b"efg") + b"\x1b[1;2H\x1b[0P")
            self.assertEqual(terminal.model_snapshot().lines, ["acd ", "efg "])

    def test_dch_at_a_wide_head_repairs_the_cut_glyph(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide + b"d\x1b[1;2H\x1b[P")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "a d  ")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_dch_at_a_wide_continuation_repairs_the_cut_glyph(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide + b"d\x1b[1;3H\x1b[P")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "a d  ")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_dch_removes_a_shifted_pre_wrap_spacer_and_hardens_the_row(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abc" + wide + b"ef\x1b[1;1H\x1b[P")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["bc  ", "界 ef"])
            self.assertFalse(snapshot.cell(3, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_dch_inside_horizontal_margins_shifts_only_to_the_right_margin(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcde")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;3H\x1b[P"
            )
            self.assertEqual(terminal.model_snapshot().lines[0], "abd e")

    def test_dch_large_count_clears_only_to_the_horizontal_right_margin(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcde")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;3H\x1b[100P"
            )
            self.assertEqual(terminal.model_snapshot().lines[0], "ab  e")

    def test_dch_at_wide_tail_inside_horizontal_margins_repairs_the_glyph(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"a" + wide + b"cd")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;3H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "a c d")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_dch_repairs_wide_glyph_crossing_horizontal_right_margin(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"ab" + wide + b"e")
                + b"\x1b[?69h\x1b[1;3s\x1b[1;1H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "b   e")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_dch_repairs_wide_glyph_crossing_horizontal_left_margin(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=7,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"ab" + wide + b"efg")
                + b"\x1b[?69h\x1b[4;5s\x1b[1;4H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "ab e fg")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_dch_partial_horizontal_region_preserves_wide_pre_wrap(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=4,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                b"abc" + wide + b"ef"
                + b"\x1b[?69h\x1b[1;3s\x1b[1;1H\x1b[P"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["bc  ", "界 ef"])
            self.assertTrue(snapshot.cell(1, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_dch_outside_horizontal_margins_is_a_noop(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcd", b"efgh")
                + b"\x1b[?69h\x1b[1;2s\x1b[1;4H\x1b[P"
            )
            self.assertEqual(terminal.model_snapshot().lines, ["abcd", "efgh"])

    def test_ich_inserts_one_blank_and_shifts_tail_right(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd") + b"\x1b[1;2H\x1b[@")
            self.assertEqual(terminal.model_snapshot().lines[0], "a bc")

    def test_ich_large_count_clears_to_right_edge(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd") + b"\x1b[1;2H\x1b[100@")
            self.assertEqual(terminal.model_snapshot().lines[0], "a   ")

    def test_insert_mode_inserts_non_blank_graphics(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd") + b"\x1b[1;2H\x1b[4hxxx")
            self.assertEqual(terminal.model_snapshot().lines[0], "axxx")

    def test_zero_ich_parameter_follows_the_terminal_consensus_of_one(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd") + b"\x1b[1;2H\x1b[0@")
            self.assertEqual(terminal.model_snapshot().lines[0], "a bc")

    def test_ich_at_wide_continuation_repairs_both_halves(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"a" + wide + b"de\x1b[1;3H\x1b[@")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "a   d")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_ich_one_cell_keeps_soft_wrap_after_removing_wide_pre_wrap_spacer(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abcd" + wide + b"fgh\x1b[1;3H\x1b[@")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["ab cd", "界 fgh"])
            self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_ich_overflow_keeps_consensus_soft_wrap_after_dropping_pre_wrap_spacer(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"abcd" + wide + b"fgh\x1b[1;3H\x1b[2@")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["ab  c", "界 fgh"])
            self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_ich_overflow_repairs_wide_cell_and_keeps_consensus_soft_wrap(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(b"ab" + wide + wide + b"fgh\x1b[1;3H\x1b[2@")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["ab   ", "界 fgh"])
            self.assertTrue(snapshot.cell(4, 0).wrapped)
            self.assertFalse(snapshot.cell(2, 0).double_width)
            self.assertFalse(snapshot.cell(3, 0).double_width_continuation)

    def test_ich_inside_horizontal_margins_shifts_only_to_right_margin(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcdef")
                + b"\x1b[?69h\x1b[2;5s\x1b[1;3H\x1b[@"
            )
            self.assertEqual(terminal.model_snapshot().lines[0], "ab cdf")

    def test_ich_large_count_clears_only_to_horizontal_right_margin(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcdef")
                + b"\x1b[?69h\x1b[2;5s\x1b[1;3H\x1b[100@"
            )
            self.assertEqual(terminal.model_snapshot().lines[0], "ab   f")

    def test_ich_repairs_wide_glyph_crossing_horizontal_right_margin(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=6,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(b"abc" + wide + b"f")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;2H\x1b[@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "a bc f")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_ich_repairs_wide_glyph_crossing_horizontal_left_margin(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=6,
            rows=2,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                put_rows(wide + b"cdef")
                + b"\x1b[?69h\x1b[2;4s\x1b[1;2H\x1b[@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "   cef")
            self.assertFalse(any(cell.double_width for cell in snapshot.cells))
            self.assertFalse(any(cell.double_width_continuation for cell in snapshot.cells))

    def test_ich_partial_horizontal_region_preserves_wide_pre_wrap(self):
        wide = "界".encode("utf-8")
        with Shitty(
            columns=5,
            rows=3,
            save_lines=0,
            extra_arguments=("-unicodeWidths", "17"),
        ) as terminal:
            terminal.write(
                b"ab" + wide + wide + b"fgh"
                + b"\x1b[?69h\x1b[1;2s\x1b[1;1H\x1b[@"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], [" a界  ", "界 fgh"])
            self.assertTrue(snapshot.cell(3, 0).wrapped)
            self.assertTrue(snapshot.cell(2, 0).double_width)
            self.assertTrue(snapshot.cell(3, 0).double_width_continuation)

    def test_ich_outside_horizontal_margins_is_a_noop(self):
        with Shitty(columns=6, rows=2, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"abcdef")
                + b"\x1b[?69h\x1b[1;2s\x1b[1;4H\x1b[@"
            )
            self.assertEqual(terminal.model_snapshot().lines[0], "abcdef")

    def test_large_cuf_clamps_at_the_page_right_margin(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[1;2H\x1b[99C")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))

    def test_bottom_region_autowrap_keeps_every_moved_soft_break(self):
        with Shitty(columns=8, rows=8, save_lines=0) as terminal:
            terminal.write(b"\x1b[1;4r0123456789abcdefghijklmnopqrstuvwxyz")
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                [
                    "89abcdef",
                    "ghijklmn",
                    "opqrstuv",
                    "wxyz    ",
                    "        ",
                    "        ",
                    "        ",
                    "        ",
                ],
            )
            self.assertEqual(
                [snapshot.cell(7, row).wrapped for row in range(8)],
                [True, True, True, False, False, False, False, False],
            )

    @staticmethod
    def _select(terminal, start, end):
        terminal.select_start(*start)
        terminal.select_update(*end)
        return terminal.select_finish()

    def test_row_major_range_starts_at_the_first_cell(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghijKLMNOPQRST")
            self.assertEqual(self._select(terminal, (0, 0), (5, 0)), b"01234")

    def test_row_major_range_spans_a_soft_line_boundary(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghijKLMNOPQRST")
            self.assertEqual(self._select(terminal, (8, 0), (3, 1)), b"89abc")

    def test_row_major_range_can_start_on_a_subsequent_row(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghijKLMNOPQRST")
            self.assertEqual(self._select(terminal, (8, 1), (3, 2)), b"ijKLM")

    def test_row_major_range_applies_a_positive_view_row_offset(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(b"".join(bytes([ord("0") + row]) * 10 for row in range(10)))
            self.assertEqual(self._select(terminal, (8, 6), (3, 7)), b"66777")

    def test_row_major_range_maps_a_negative_history_offset_without_clipping(self):
        with Shitty(columns=10, rows=3, save_lines=10) as terminal:
            terminal.write(b"0123456789abcdefghijKLMNOPQRSTuvwxyz")
            terminal.wheel_up()
            self.assertEqual(self._select(terminal, (8, 0), (3, 1)), b"89abc")

    def test_row_major_range_clips_a_partially_negative_start(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghij")
            self.assertEqual(self._select(terminal, (-2, -1), (3, 0)), b"012")

    def test_row_major_range_fully_above_the_view_is_empty(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(b"0123456789abcdefghij")
            self.assertEqual(self._select(terminal, (-5, -2), (-1, -1)), b"")

    def test_one_column_history_retains_an_empty_logical_line(self):
        with Shitty(columns=1, rows=2, save_lines=10) as terminal:
            terminal.write(b"\r\n" * 6)
            self.assertEqual(terminal.scrollback_state()[0], 5)
            terminal.wheel_up(10)
            self.assertEqual(self._select(terminal, (0, 0), (1, 0)), b"")

    def test_height_growth_consumes_the_newest_regular_history_line(self):
        with Shitty(columns=8, rows=1, save_lines=10) as terminal:
            terminal.write(b"hello\r\nworld\r\n")
            self.assertEqual(terminal.scrollback_state()[0], 2)
            terminal.resize(8, 2)
            self.assertEqual(terminal.model_snapshot().lines, ["world   ", "        "])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up(10)
            self.assertEqual(terminal.model_snapshot().lines, ["hello   ", "world   "])

    def test_height_growth_consumes_a_complete_wrapped_history_line(self):
        with Shitty(columns=8, rows=1, save_lines=10) as terminal:
            terminal.write(b"hello\r\nabcdefghijklmnopqrst\r\n")
            self.assertEqual(terminal.scrollback_state()[0], 4)
            terminal.resize(8, 4)
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["abcdefgh", "ijklmnop", "qrst    ", "        "],
            )
            self.assertEqual(
                [snapshot.cell(7, row).wrapped for row in range(4)],
                [True, True, False, False],
            )
            self.assertEqual(terminal.scrollback_state()[0], 1)

    def test_height_growth_consumes_an_empty_newest_history_line(self):
        with Shitty(columns=8, rows=1, save_lines=10) as terminal:
            terminal.write(b"hello\r\n\r\n")
            self.assertEqual(terminal.scrollback_state()[0], 2)
            terminal.resize(8, 2)
            self.assertEqual(terminal.model_snapshot().lines, ["        ", "        "])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up(10)
            self.assertEqual(terminal.model_snapshot().lines, ["hello   ", "        "])

    def test_height_growth_consumes_a_history_line_larger_than_a_storage_block(self):
        payload = (b"0123456789" * 90) + b"xyz"
        physical_rows = (len(payload) + 79) // 80
        with Shitty(columns=80, rows=1, save_lines=32) as terminal:
            terminal.write(b"hello\r\n" + payload + b"\r\n")
            self.assertEqual(terminal.scrollback_state()[0], physical_rows + 1)
            terminal.resize(80, physical_rows + 1)
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                "".join(snapshot.lines[:-1]).rstrip(),
                payload.decode("ascii"),
            )
            self.assertEqual(terminal.scrollback_state()[0], 1)

    def test_height_growth_with_empty_history_only_adds_blank_rows(self):
        with Shitty(columns=8, rows=1, save_lines=10) as terminal:
            self.assertEqual(terminal.scrollback_state()[0], 0)
            terminal.resize(8, 4)
            self.assertEqual(terminal.model_snapshot().lines, ["        "] * 4)
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_full_screen_scroll_clears_with_the_current_background(self):
        with Shitty(columns=6, rows=4, save_lines=4) as terminal:
            terminal.write(put_rows(b"abcdef", b"ghijkl", b"mnopqr", b"stuvwx"))
            terminal.write(b"\x1b[48;2;255;165;0m\x1b[4;1H\x1bD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["ghijkl", "mnopqr", "stuvwx", "      "])
            self.assertTrue(
                all(snapshot.cell(column, 3).background == (255, 165, 0) for column in range(6))
            )

    def test_rectangular_scroll_clears_with_the_current_background(self):
        with Shitty(columns=6, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcdef", b"ghijkl", b"mnopqr", b"stuvwx"))
            terminal.write(
                b"\x1b[48;2;255;165;0m"
                b"\x1b[?69h\x1b[2;5s\x1b[2;4r\x1b[S"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcdef", "gnopql", "mtuvwr", "s    x"])
            for column in range(6):
                expected = (255, 165, 0) if 1 <= column <= 4 else (0, 0, 0)
                self.assertEqual(snapshot.cell(column, 3).background, expected)


if __name__ == "__main__":
    unittest.main()

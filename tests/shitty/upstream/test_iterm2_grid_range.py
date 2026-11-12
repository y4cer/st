# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 32 iTerm2 grid-range cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "test_emptyOuter_returnsEmpty",
    "test_invalidOuter_returnsEmpty",
    "test_outerWithNoExclusions_returnsOuter",
    "test_emptyExclusionInList_isIgnored",
    "test_exclusionInMiddle_splitsInTwo",
    "test_exclusionAtStart_clipsLeading",
    "test_exclusionAtEnd_clipsTrailing",
    "test_exclusionCoversWhole_returnsEmpty",
    "test_exclusionLargerThanOuter_returnsEmpty",
    "test_exclusionEntirelyBeforeOuter_isNoOp",
    "test_exclusionEntirelyAfterOuter_isNoOp",
    "test_exclusionAdjacentBeforeOuter_isNoOp",
    "test_exclusionAdjacentAfterOuter_isNoOp",
    "test_exclusionStraddlesStart_clipsLeft",
    "test_exclusionStraddlesEnd_clipsRight",
    "test_twoDisjointExclusionsInMiddle_threePieces",
    "test_unsortedInput_sortedInternally",
    "test_adjacentExclusionsNoGap_producesTwoOuterPieces",
    "test_overlappingExclusions_treatedAsUnion",
    "test_nestedExclusion_outerWins",
    "test_nestedExclusionReversedOrder",
    "test_duplicateExclusions_sameAsOne",
    "test_threeOverlappingExclusionsCovering_returnsEmpty",
    "test_multiRowOuter_exclusionOnMiddleRow",
    "test_multiRowOuter_exclusionSpansRowBoundary",
    "test_multiRowOuter_twoExclusionsOneOnEachRow",
    "test_cascadingOverlaps_noDuplicates",
    "test_exclusionMatchingOuterStart_noEmptyLeadingPiece",
    "test_exclusionMatchingOuterEnd_noEmptyTrailingPiece",
    "test_exclusionExactlyMatchingOuter_returnsEmpty",
    "test_multipleExclusionsMatchingOuterExactly_returnsEmpty",
    "test_mixedValidAndInvalidExclusions_filtersInvalid",
)

SINGLE_ROW = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def osc133(action, options=b""):
    suffix = b";" + options if options else b""
    return b"\x1b]133;" + action + suffix + b"\x1b\\"


def cup(position):
    column, row = position
    return f"\x1b[{row + 1};{column + 1}H".encode("ascii")


def install_command_ranges(terminal, outer, exclusions):
    """Install the exact source ranges through positioned OSC 133 marks."""
    terminal.write(cup(outer[0]) + osc133(b"P", b"k=i") + osc133(b"B"))
    for start, end in exclusions:
        terminal.write(
            cup(start)
            + osc133(b"P", b"k=s")
            + cup(end)
            + osc133(b"B")
        )
    terminal.write(cup(outer[1]) + osc133(b"C"))


def current_line_action(terminal, column, row):
    """Exercise Shitty's nearest public selection action.

    Shitty has no select-current-command action yet.  Cycling the existing
    action reaches whole-line selection and deliberately exposes that gap:
    prompt and right-prompt cells are still returned with the input.
    """
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)
    terminal.select_extend(column, row, cycle=True)
    return terminal.select_finish()


class ITerm2GridRangeTest(unittest.TestCase):
    def test_upstream_inventory_has_all_32_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 32)
        self.assertEqual(len(set(PORTED_CASES)), 32)

    @unittest.expectedFailure
    def test_empty_current_command_range_selects_nothing(self):
        with Shitty(columns=20, rows=1, save_lines=0) as terminal:
            terminal.write(osc133(b"P", b"k=i") + b"$ " + osc133(b"B"))
            self.assertEqual(current_line_action(terminal, 0, 0), b"")

    @unittest.expectedFailure
    def test_missing_current_command_range_selects_nothing(self):
        with Shitty(columns=24, rows=1, save_lines=0) as terminal:
            terminal.write(b"not a semantic command")
            self.assertEqual(current_line_action(terminal, 4, 0), b"")

    @unittest.expectedFailure
    def test_current_command_without_exclusions_selects_the_whole_outer_range(self):
        with Shitty(columns=24, rows=2, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P", b"k=i")
                + b"$ "
                + osc133(b"B")
                + b"echo one\r\n"
                + osc133(b"P", b"k=s")
                + b"> "
                + osc133(b"B")
                + b"echo two"
            )
            self.assertEqual(
                current_line_action(terminal, 4, 0),
                b"echo one\necho two",
            )

    @unittest.expectedFailure
    def test_empty_right_prompt_exclusion_does_not_remove_input(self):
        with Shitty(columns=20, rows=1, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P", b"k=i")
                + b"$ "
                + osc133(b"B")
                + b"left"
                + osc133(b"P", b"k=r")
                + osc133(b"B")
                + b"right"
            )
            self.assertEqual(current_line_action(terminal, 4, 0), b"leftright")

    @unittest.expectedFailure
    def test_middle_right_prompt_exclusion_splits_and_rejoins_same_row_input(self):
        with Shitty(columns=20, rows=1, save_lines=0) as terminal:
            terminal.write(
                osc133(b"P", b"k=i")
                + b"$ "
                + osc133(b"B")
                + b"left"
                + osc133(b"P", b"k=r")
                + b"RP"
                + osc133(b"B")
                + b"right"
            )
            self.assertEqual(current_line_action(terminal, 4, 0), b"leftright")

    @unittest.expectedFailure
    def test_exclusion_at_start_clips_leading_input(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((2, 0), (10, 0)),
                [((2, 0), (5, 0))],
            )
            self.assertEqual(current_line_action(terminal, 6, 0), SINGLE_ROW[5:10])

    @unittest.expectedFailure
    def test_exclusion_at_end_clips_trailing_input(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [((7, 0), (10, 0))],
            )
            self.assertEqual(current_line_action(terminal, 3, 0), SINGLE_ROW[:7])

    @unittest.expectedFailure
    def test_exclusion_covering_the_whole_input_selects_nothing(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((2, 0), (8, 0)),
                [((2, 0), (8, 0))],
            )
            self.assertEqual(current_line_action(terminal, 4, 0), b"")

    @unittest.expectedFailure
    def test_exclusion_larger_than_the_input_selects_nothing(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((2, 0), (8, 0)),
                [((0, 0), (100, 0))],
            )
            self.assertEqual(current_line_action(terminal, 4, 0), b"")

    @unittest.expectedFailure
    def test_exclusion_entirely_before_input_is_a_no_op(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((10, 0), (20, 0)),
                [((0, 0), (5, 0))],
            )
            self.assertEqual(current_line_action(terminal, 12, 0), SINGLE_ROW[10:20])

    @unittest.expectedFailure
    def test_exclusion_entirely_after_input_is_a_no_op(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [((50, 0), (60, 0))],
            )
            self.assertEqual(current_line_action(terminal, 4, 0), SINGLE_ROW[:10])

    @unittest.expectedFailure
    def test_exclusion_adjacent_before_input_is_a_no_op(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((5, 0), (10, 0)),
                [((0, 0), (5, 0))],
            )
            self.assertEqual(current_line_action(terminal, 7, 0), SINGLE_ROW[5:10])

    @unittest.expectedFailure
    def test_exclusion_adjacent_after_input_is_a_no_op(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [((10, 0), (15, 0))],
            )
            self.assertEqual(current_line_action(terminal, 4, 0), SINGLE_ROW[:10])

    @unittest.expectedFailure
    def test_exclusion_straddling_start_clips_left(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((5, 0), (15, 0)),
                [((0, 0), (8, 0))],
            )
            self.assertEqual(current_line_action(terminal, 10, 0), SINGLE_ROW[8:15])

    @unittest.expectedFailure
    def test_exclusion_straddling_end_clips_right(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((5, 0), (15, 0)),
                [((12, 0), (25, 0))],
            )
            self.assertEqual(current_line_action(terminal, 8, 0), SINGLE_ROW[5:12])

    @unittest.expectedFailure
    def test_two_disjoint_exclusions_produce_three_connected_pieces(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [((4, 0), (6, 0)), ((12, 0), (14, 0))],
            )
            expected = SINGLE_ROW[:4] + SINGLE_ROW[6:12] + SINGLE_ROW[14:20]
            self.assertEqual(current_line_action(terminal, 2, 0), expected)

    @unittest.expectedFailure
    def test_unsorted_exclusions_are_sorted_before_clipping(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [((12, 0), (14, 0)), ((4, 0), (6, 0))],
            )
            expected = SINGLE_ROW[:4] + SINGLE_ROW[6:12] + SINGLE_ROW[14:20]
            self.assertEqual(current_line_action(terminal, 2, 0), expected)

    @unittest.expectedFailure
    def test_adjacent_exclusions_do_not_insert_an_empty_piece(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (15, 0)),
                [((3, 0), (5, 0)), ((5, 0), (10, 0))],
            )
            expected = SINGLE_ROW[:3] + SINGLE_ROW[10:15]
            self.assertEqual(current_line_action(terminal, 1, 0), expected)

    @unittest.expectedFailure
    def test_overlapping_exclusions_are_treated_as_their_union(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [((3, 0), (8, 0)), ((5, 0), (12, 0))],
            )
            expected = SINGLE_ROW[:3] + SINGLE_ROW[12:20]
            self.assertEqual(current_line_action(terminal, 1, 0), expected)

    @unittest.expectedFailure
    def test_nested_exclusion_is_absorbed_by_outer_exclusion(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [((3, 0), (15, 0)), ((6, 0), (10, 0))],
            )
            expected = SINGLE_ROW[:3] + SINGLE_ROW[15:20]
            self.assertEqual(current_line_action(terminal, 1, 0), expected)

    @unittest.expectedFailure
    def test_nested_exclusion_reversed_order_has_the_same_result(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [((6, 0), (10, 0)), ((3, 0), (15, 0))],
            )
            expected = SINGLE_ROW[:3] + SINGLE_ROW[15:20]
            self.assertEqual(current_line_action(terminal, 1, 0), expected)

    @unittest.expectedFailure
    def test_duplicate_exclusions_are_equivalent_to_one(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            exclusion = ((5, 0), (10, 0))
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [exclusion, exclusion, exclusion],
            )
            expected = SINGLE_ROW[:5] + SINGLE_ROW[10:20]
            self.assertEqual(current_line_action(terminal, 2, 0), expected)

    @unittest.expectedFailure
    def test_three_overlapping_exclusions_cover_the_whole_input(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [
                    ((0, 0), (8, 0)),
                    ((5, 0), (15, 0)),
                    ((12, 0), (20, 0)),
                ],
            )
            self.assertEqual(current_line_action(terminal, 2, 0), b"")

    @unittest.expectedFailure
    def test_middle_row_exclusion_leaves_two_disconnected_pieces(self):
        with Shitty(columns=20, rows=4, save_lines=0) as terminal:
            terminal.write(b"aaaaaaaaaa\r\nbbbbbbbbbb\r\ncccccccccc")
            install_command_ranges(
                terminal,
                ((0, 0), (0, 3)),
                [((0, 1), (0, 2))],
            )
            self.assertEqual(
                current_line_action(terminal, 2, 0),
                b"aaaaaaaaaa\ncccccccccc",
            )

    @unittest.expectedFailure
    def test_exclusion_spanning_a_row_boundary_clips_both_rows(self):
        with Shitty(columns=20, rows=4, save_lines=0) as terminal:
            terminal.write(b"abcdefghij\r\n0123456789\r\nKLMNOPQRST")
            install_command_ranges(
                terminal,
                ((0, 0), (0, 3)),
                [((5, 0), (5, 1))],
            )
            self.assertEqual(
                current_line_action(terminal, 2, 0),
                b"abcde\n56789\nKLMNOPQRST",
            )

    @unittest.expectedFailure
    def test_two_exclusions_on_different_rows_leave_three_pieces(self):
        with Shitty(columns=20, rows=4, save_lines=0) as terminal:
            terminal.write(b"abcdefghij\r\n0123456789\r\nKLMNOPQRST")
            install_command_ranges(
                terminal,
                ((0, 0), (0, 3)),
                [((8, 0), (10, 0)), ((0, 1), (2, 1))],
            )
            self.assertEqual(
                current_line_action(terminal, 2, 0),
                b"abcdefgh\n23456789\nKLMNOPQRST",
            )

    @unittest.expectedFailure
    def test_cascading_overlaps_do_not_duplicate_pieces(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (40, 0)),
                [
                    ((3, 0), (12, 0)),
                    ((10, 0), (20, 0)),
                    ((18, 0), (30, 0)),
                ],
            )
            expected = SINGLE_ROW[:3] + SINGLE_ROW[30:40]
            self.assertEqual(current_line_action(terminal, 1, 0), expected)

    @unittest.expectedFailure
    def test_exclusion_matching_start_does_not_emit_empty_leading_piece(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((5, 0), (15, 0)),
                [((5, 0), (10, 0))],
            )
            self.assertEqual(current_line_action(terminal, 12, 0), SINGLE_ROW[10:15])

    @unittest.expectedFailure
    def test_exclusion_matching_end_does_not_emit_empty_trailing_piece(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [((5, 0), (10, 0))],
            )
            self.assertEqual(current_line_action(terminal, 2, 0), SINGLE_ROW[:5])

    @unittest.expectedFailure
    def test_exclusion_exactly_matching_input_selects_nothing(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [((0, 0), (10, 0))],
            )
            self.assertEqual(current_line_action(terminal, 2, 0), b"")

    @unittest.expectedFailure
    def test_duplicate_exclusions_matching_input_select_nothing(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            exclusion = ((0, 0), (10, 0))
            install_command_ranges(
                terminal,
                ((0, 0), (10, 0)),
                [exclusion, exclusion, exclusion],
            )
            self.assertEqual(current_line_action(terminal, 2, 0), b"")

    @unittest.expectedFailure
    def test_empty_exclusions_are_filtered_around_valid_exclusion(self):
        with Shitty(columns=128, rows=1, save_lines=0) as terminal:
            terminal.write(SINGLE_ROW)
            install_command_ranges(
                terminal,
                ((0, 0), (20, 0)),
                [
                    ((7, 0), (7, 0)),
                    ((8, 0), (12, 0)),
                    ((15, 0), (15, 0)),
                ],
            )
            expected = SINGLE_ROW[:8] + SINGLE_ROW[12:20]
            self.assertEqual(current_line_action(terminal, 2, 0), expected)


if __name__ == "__main__":
    unittest.main()

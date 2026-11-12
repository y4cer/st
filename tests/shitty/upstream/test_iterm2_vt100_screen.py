# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 65 iTerm2 VT100Screen cases."""

import random
import unittest

from harness import Shitty


PORTED_CASES = (
    "testResizeNotes",
    "testSwitchingScreenBuffersRefreshesChangedKeyReportingFlags",
    "testSwitchingScreenBuffersDoesNotRefreshUnchangedKeyReportingFlags",
    "testScreenCharArrayForLineContentIdentityMatchesSeparateCalls",
    "testResizeNoteInPrimaryWhileInAltAndSomeHistory",
    "testResizeNoteInPrimaryWhileInAltAndPushingSomePrimaryIncludingWholeNoteIntoHistory",
    "testResizeNoteInPrimaryWhileInAltAndPushingSomePrimaryIncludingPartOfNoteIntoHistory",
    "testResizeNoteInAlternateThatGetsTruncatedByShrinkage",
    "testResizeWithNoteFirstLine",
    "testResizeWithNoteFirstLinePlusFirstCharacterOfSecondLine",
    "testResizeWithNoteFirstTwoCharactersOfSecondLine",
    "testResizeWithNoteSecondLine",
    "testResizeWithNoteLastFourCharactersOfSecondLine",
    "testResizeWithNoteSecondCharacterOfSecondLineToSecondCharacterOfThirdLine",
    "testResizeWithNoteSecondAndThirdLines",
    "testResizeWithNoteSecondThroughFourthLines",
    "testResizeWithNoteSecondThroughFifthLines",
    "testResizeWithNoteSecondCharacterOfSecondLineThroughFirstCharacterOfFifthLine",
    "testResizeWithNoteThirdLineThroughFifthLine",
    "testResizeWithNoteThirdLineThroughMiddleOfFifthLine",
    "testResizeWithNoteFifthLine",
    "testResizeWithNoteAllLines",
    "testResizeWithBlanksBeforeAnnotation",
    "testMarkDeallocWithUnfulfilledReturnCodePromise",
    "testResizeScreenMarkPropertiesInPrimaryWhileInAlt",
    "testResizeWithOutOfBoundsCommandRangeStartX",
    "testResizeScreenMarkInSavedIntervalTreeWithDroppedLines",
    "testResizeScreenMarkPropertiesGrowingWidth",
    "testCommandMarkAtReturnsNilWhenLineIsOutOfBounds",
    "testCommandMarkAtReturnsNilWhenNoMarkOnLine",
    "testCommandMarkAtReturnsNilWhenMarkHasNoCommand",
    "testNoteResizeRegression1",
    "testNoteResizeNoEncodeDecode",
    "testNoteResizeNoEncodeDecodeLine1",
    "testNoteResizeRegression2",
    "testNoteResizeRegression3",
    "testNoteResizeRegression4",
    "testNoteResizeRegression5",
    "testGang_basic",
    "testGang_random",
    "testGang_insertMode",
    "testGang_wraparoundModeOff",
    "testGang_ansiMode",
    "testGang_altBuffer",
    "testGang_commandStartCoord",
    "testGang_lineDrawingMode",
    "testGang_loggingEnabled",
    "testGang_publishing",
    "testGang_expectations",
    "testGang_printBuffer",
    "testGang_multipleConditions",
    "testGang_expectationConsumedByMatch",
    "testGang_expectationExpiredByDeadline",
    "testGang_postTriggerActions",
    "testDropFirstBlock",
    "testEraseLineAfterCursorPreservesSoftEOLWhenPreviousLineIsFull",
    "testEraseLineAfterCursorRemovesSoftEOLWhenPreviousLineIsNotFull",
    "testEraseInDisplayAfterCursorPreservesSoftEOLWhenPreviousLineIsFull",
    "testProgressPauseWithoutPercentageKeepsCurrentPercentage",
    "testProgressPauseWithoutPercentageKeepsErrorPercentage",
    "testProgressPauseWithoutPercentageAndNothingShowingUsesMinimum",
    "testProgressPauseWithoutPercentageFromZeroUsesMinimum",
    "testProgressPauseWithInvalidPercentageIsIgnored",
    "testProgressPauseWithExplicitPercentage",
    "testProgressOtherStatesAreUnchanged",
)


class ITerm2VT100ScreenTest(unittest.TestCase):
    def test_upstream_inventory_has_all_65_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 65)
        self.assertEqual(len(set(PORTED_CASES)), 65)

    def test_primary_semantic_range_survives_alt_screen_resize_reflow(self):
        with Shitty(columns=5, rows=4, save_lines=10) as terminal:
            terminal.write(
                b"abcde"
                b"\x1b]133;P\x07fgh\x1b]133;D\x07"
                b"\r\nijkl\r\n"
            )
            before = terminal.model_snapshot()
            self.assertEqual(before.lines, ["abcde", "fgh  ", "ijkl ", "     "])
            self.assertEqual(
                [before.cell(column, 1).semantic for column in range(5)],
                [1, 1, 1, 0, 0],
            )

            terminal.write(b"\x1b[?1049h")
            terminal.resize(4, 4)
            terminal.write(b"\x1b[?1049l")

            after = terminal.model_snapshot()
            self.assertEqual(after.lines, ["abcd", "efgh", "ijkl", "    "])
            self.assertEqual(
                [after.cell(column, 1).semantic for column in range(4)],
                [0, 1, 1, 1],
            )

    def test_screen_switch_restores_each_kitty_keyboard_stack(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1u\x1b[?1049h\x1b[>2u")

            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.state()[3], 1)
            terminal.write(b"\x1b[?u")
            self.assertEqual(terminal.read_input(), b"\x1b[?1u")

            terminal.write(b"\x1b[?1049h")
            self.assertEqual(terminal.state()[3], 2)
            terminal.write(b"\x1b[?u")
            self.assertEqual(terminal.read_input(), b"\x1b[?2u")

    def test_screen_switch_with_equal_flags_keeps_the_public_report(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?1049h\x1b[?1049l")
            self.assertEqual(terminal.state()[3], 0)

            terminal.write(b"\x1b[=1;1u")
            self.assertEqual(terminal.state()[3], 1)
            terminal.write(b"\x1b[?1049h\x1b[?1049l\x1b[?u")
            self.assertEqual(terminal.state()[3], 1)
            self.assertEqual(terminal.read_input(), b"\x1b[?1u")

    def test_repeated_line_reads_match_across_the_history_boundary(self):
        with Shitty(columns=5, rows=4, save_lines=10) as terminal:
            terminal.write(b"abcdefgh\r\nijkl\r\nhello world")
            first = terminal.model_snapshot()
            second = terminal.model_snapshot()
            self.assertEqual(first.lines, second.lines)
            self.assertEqual(
                [first.cell(column, row) for row in range(4) for column in range(5)],
                [second.cell(column, row) for row in range(4) for column in range(5)],
            )

            terminal.wheel_up(20)
            history_first = terminal.model_snapshot()
            history_second = terminal.model_snapshot()
            self.assertEqual(history_first.lines, ["abcde", "fgh  ", "ijkl ", "hello"])
            self.assertEqual(history_first.lines, history_second.lines)
            self.assertEqual(
                [history_first.cell(column, row) for row in range(4) for column in range(5)],
                [history_second.cell(column, row) for row in range(4) for column in range(5)],
            )

    @staticmethod
    def _visible_semantic_chars(terminal):
        snapshot = terminal.model_snapshot()
        return "".join(
            snapshot.cell(column, row).char
            for row in range(snapshot.rows)
            for column in range(snapshot.columns)
            if snapshot.cell(column, row).semantic
        )

    def _assert_history_semantic_resize(self, start, end, width, visible_after):
        payload = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        marked = payload[start:end].decode("ascii")
        with Shitty(columns=5, rows=4, save_lines=20) as terminal:
            terminal.write(
                payload[:start]
                + b"\x1b]133;P\x07"
                + payload[start:end]
                + b"\x1b]133;D\x07"
                + payload[end:]
            )
            self.assertEqual(self._visible_semantic_chars(terminal), marked)

            terminal.write(b"\x1b[?1049h")
            terminal.resize(width, 4)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(self._visible_semantic_chars(terminal), visible_after)

            seen = set(self._visible_semantic_chars(terminal))
            for _ in range(terminal.scrollback_state()[0]):
                terminal.wheel_up(1)
                seen.update(self._visible_semantic_chars(terminal))
            self.assertEqual(seen, set(marked))

    def test_primary_semantic_range_survives_inactive_resize_with_history(self):
        self._assert_history_semantic_resize(24, 29, 4, "YZ012")

    def test_primary_semantic_range_can_move_wholly_into_history(self):
        self._assert_history_semantic_resize(20, 24, 3, "")

    def test_primary_semantic_range_can_split_across_history_and_screen(self):
        self._assert_history_semantic_resize(22, 27, 3, "YZ0")

    def test_alternate_semantic_range_is_clipped_by_nonreflowing_shrink(self):
        with Shitty(columns=5, rows=4, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[?1049hABCDE"
                b"\x1b]133;P\x07FGHIJKLMNOPQRST\x1b]133;D\x07"
            )
            terminal.resize(3, 4)
            self.assertEqual(terminal.model_snapshot().lines, ["ABC", "FGH", "KLM", "PQR"])
            self.assertEqual(self._visible_semantic_chars(terminal), "FGHKLMPQR")

    def _assert_semantic_range_reflow_round_trip(self, start, end):
        payload = b"ABCDEFGHIJKLMNOPQRSTUVWXY"
        marked = payload[start:end].decode("ascii")
        with Shitty(columns=5, rows=10, save_lines=10) as terminal:
            terminal.write(payload)
            row, column = divmod(start, 5)
            terminal.write(
                f"\x1b[{row + 1};{column + 1}H".encode()
                + b"\x1b]133;P\x07"
                + payload[start:end]
                + b"\x1b]133;D\x07"
            )
            self.assertEqual(self._visible_semantic_chars(terminal), marked)

            terminal.write(b"\x1b[?1049h")
            terminal.resize(3, 10)
            terminal.resize(5, 10)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.model_snapshot().lines[:5], [
                "ABCDE",
                "FGHIJ",
                "KLMNO",
                "PQRST",
                "UVWXY",
            ])
            self.assertEqual(self._visible_semantic_chars(terminal), marked)

    def test_semantic_round_trip_first_line(self):
        self._assert_semantic_range_reflow_round_trip(0, 5)

    def test_semantic_round_trip_first_line_and_second_line_prefix(self):
        self._assert_semantic_range_reflow_round_trip(0, 7)

    def test_semantic_round_trip_second_line_prefix(self):
        self._assert_semantic_range_reflow_round_trip(5, 8)

    def test_semantic_round_trip_second_line(self):
        self._assert_semantic_range_reflow_round_trip(5, 10)

    def test_semantic_round_trip_second_line_suffix(self):
        self._assert_semantic_range_reflow_round_trip(7, 10)

    def test_semantic_round_trip_crosses_second_and_third_lines(self):
        self._assert_semantic_range_reflow_round_trip(7, 12)

    def test_semantic_round_trip_second_and_third_lines(self):
        self._assert_semantic_range_reflow_round_trip(5, 15)

    def test_semantic_round_trip_second_through_fourth_lines(self):
        self._assert_semantic_range_reflow_round_trip(5, 20)

    def test_semantic_round_trip_second_through_fifth_lines(self):
        self._assert_semantic_range_reflow_round_trip(5, 25)

    def test_semantic_round_trip_second_line_suffix_through_fifth_prefix(self):
        self._assert_semantic_range_reflow_round_trip(7, 22)

    def test_semantic_round_trip_fourth_and_fifth_lines(self):
        self._assert_semantic_range_reflow_round_trip(15, 25)

    def test_semantic_round_trip_fourth_line_through_fifth_prefix(self):
        self._assert_semantic_range_reflow_round_trip(15, 23)

    def test_semantic_round_trip_fifth_line(self):
        self._assert_semantic_range_reflow_round_trip(20, 25)

    def test_semantic_round_trip_all_lines(self):
        self._assert_semantic_range_reflow_round_trip(0, 25)

    @staticmethod
    def _semantic_chars(terminal, value):
        snapshot = terminal.model_snapshot()
        return "".join(
            snapshot.cell(column, row).char
            for row in range(snapshot.rows)
            for column in range(snapshot.columns)
            if snapshot.cell(column, row).semantic == value
        )

    def test_blank_lines_before_a_semantic_range_do_not_move_it_on_shrink(self):
        with Shitty(columns=14, rows=8, save_lines=20) as terminal:
            terminal.write(
                b"one\r\ntwo\r\nthree\r\n\r\n"
                b"\x1b]133;P\x07XXXXXXXXXX\x1b]133;D\x07"
            )
            before = terminal.model_snapshot()
            self.assertEqual(
                [
                    (column, row)
                    for row in range(before.rows)
                    for column in range(before.columns)
                    if before.cell(column, row).semantic == 1
                ],
                [(column, 4) for column in range(10)],
            )

            terminal.resize(13, 8)
            after = terminal.model_snapshot()
            self.assertEqual(self._semantic_chars(terminal, 1), "XXXXXXXXXX")
            self.assertEqual(
                [
                    (column, row)
                    for row in range(after.rows)
                    for column in range(after.columns)
                    if after.cell(column, row).semantic == 1
                ],
                [(column, 4) for column in range(10)],
            )

    def test_teardown_accepts_an_unfinished_semantic_command(self):
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\still-running"
            )
            self.assertEqual(self._semantic_chars(terminal, 1), "$ ")
            self.assertEqual(self._semantic_chars(terminal, 2), "still-running")

        with Shitty(columns=4, rows=2) as fresh:
            fresh.write(b"ok")
            self.assertEqual(fresh.model_snapshot().lines[0], "ok  ")

    def test_inactive_primary_keeps_prompt_command_and_output_ranges(self):
        with Shitty(columns=10, rows=14, save_lines=20) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\prompt$ "
                b"\x1b]133;B\x1b\\command--with-long-arguments\r\n"
                b"\x1b]133;C\x1b\\output-one\r\noutput-two"
                b"\x1b]133;D;0\x1b\\"
            )
            expected = tuple(self._semantic_chars(terminal, value) for value in (1, 2, 3))

            terminal.write(b"\x1b[?1049h")
            terminal.resize(8, 14)
            terminal.write(b"\x1b[?1049l")

            self.assertEqual(
                tuple(self._semantic_chars(terminal, value) for value in (1, 2, 3)),
                expected,
            )

    def test_semantic_start_at_pending_wrap_is_safe_during_resize(self):
        with Shitty(columns=5, rows=6, save_lines=10) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\abcde"
                b"\x1b]133;B\x1b\\fgh"
                b"\x1b]133;C\x1b\\out"
            )
            self.assertEqual(self._semantic_chars(terminal, 1), "abcde")
            self.assertEqual(self._semantic_chars(terminal, 2), "fgh")

            terminal.resize(4, 6)
            self.assertEqual(self._semantic_chars(terminal, 1), "abcde")
            self.assertEqual(self._semantic_chars(terminal, 2), "fgh")
            self.assertEqual(self._semantic_chars(terminal, 3), "out")

    def test_saved_primary_semantics_survive_reflow_after_old_lines_drop(self):
        with Shitty(columns=20, rows=5, save_lines=10) as terminal:
            terminal.write(b"".join(
                f"old-{index:02d}\r\n".encode() for index in range(18)
            ))
            terminal.write(
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\long-command-name\r\n"
                b"\x1b]133;C\x1b\\TAIL-OUTPUT"
            )
            terminal.write(b"\x1b[?1049h")
            terminal.resize(10, 5)
            terminal.write(b"\x1b[?1049l")

            self.assertEqual(self._semantic_chars(terminal, 1), "$ ")
            self.assertEqual(self._semantic_chars(terminal, 2), "long-command-name")
            self.assertEqual(self._semantic_chars(terminal, 3), "TAIL-OUTPUT")
            self.assertLessEqual(terminal.scrollback_state()[0], 10)

    def test_inactive_primary_semantic_ranges_remain_valid_when_width_grows(self):
        with Shitty(columns=5, rows=8, save_lines=20) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\cmd\r\n"
                b"\x1b]133;C\x1b\\out1\r\nout2"
            )
            expected = tuple(self._semantic_chars(terminal, value) for value in (1, 2, 3))
            terminal.write(b"\x1b[?1049h")
            terminal.resize(10, 8)
            terminal.write(b"\x1b[?1049l")

            self.assertEqual(
                tuple(self._semantic_chars(terminal, value) for value in (1, 2, 3)),
                expected,
            )

    def test_prompt_lookup_declines_outside_the_public_row_domain(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\prompt\x1b]133;B\x1b\\")
            self.assertEqual(terminal.row_semantic(0), 1)
            self.assertTrue(terminal.cursor_at_prompt())
            self.assertEqual(terminal.row_semantic(-1), 0)
            self.assertEqual(terminal.row_semantic(4), 0)
            self.assertEqual(terminal.row_semantic(999), 0)

    def test_plain_line_has_no_command_mark_consumer(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"https://example.com\r\nnext line")
            terminal.write(b"\x1b[1;1H")
            self.assertEqual(terminal.row_semantic(0), 0)
            self.assertFalse(terminal.cursor_at_prompt())
            self.assertEqual(self._semantic_chars(terminal, 2), "")

    def test_prompt_without_a_command_is_visible_but_has_no_command_range(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\prompt\x1b]133;B\x1b\\")
            self.assertTrue(terminal.cursor_at_prompt())
            self.assertEqual(self._semantic_chars(terminal, 1), "prompt")
            self.assertEqual(self._semantic_chars(terminal, 2), "")
            self.assertEqual(self._semantic_chars(terminal, 3), "")

    def _assert_blank_prompt_resize(self, row, round_trip):
        with Shitty(columns=8, rows=15, save_lines=20) as terminal:
            terminal.write(
                f"\x1b[{row + 1};1H".encode()
                + b"\x1b]133;A\x1b\\\x1b]133;B\x1b\\"
            )
            self.assertEqual(terminal.row_semantic(row), 1)
            self.assertEqual(self._semantic_chars(terminal, 1), "")

            terminal.resize(7, 15)
            self.assertEqual(terminal.row_semantic(row), 1)
            if round_trip:
                terminal.resize(8, 15)
                self.assertEqual(terminal.row_semantic(row), 1)

    def test_blank_first_row_semantics_survive_resize_round_trip(self):
        self._assert_blank_prompt_resize(0, True)

    def test_blank_first_row_semantics_survive_direct_shrink(self):
        self._assert_blank_prompt_resize(0, False)

    def test_blank_second_row_semantics_survive_direct_shrink(self):
        self._assert_blank_prompt_resize(1, False)

    def test_blank_second_row_semantics_survive_resize_round_trip(self):
        self._assert_blank_prompt_resize(1, True)

    def test_blank_third_row_semantics_survive_resize_round_trip(self):
        self._assert_blank_prompt_resize(2, True)

    def test_multiline_semantic_range_survives_resize_round_trip(self):
        marked = b"ABCDEFGHIJKLMNOPQRST"
        with Shitty(columns=8, rows=12, save_lines=20) as terminal:
            terminal.write(b"\x1b[5;3H\x1b]133;P\x07" + marked + b"\x1b]133;D\x07")
            self.assertEqual(self._semantic_chars(terminal, 1), marked.decode())
            terminal.resize(7, 12)
            terminal.resize(8, 12)
            self.assertEqual(self._semantic_chars(terminal, 1), marked.decode())

    def test_blank_late_row_semantics_survive_resize_round_trip(self):
        self._assert_blank_prompt_resize(12, True)

    def test_mixed_ascii_batch_matches_separate_public_writes(self):
        initial = (
            b"Now is the time for all good men to come to the aid of their party.\r\n"
            b"\r\nTwas brillig and the slithy toves did gyre and gimbal in the wabe.\r\n"
        )
        tokens = (
            b"One for the money\r\ntwo for the show\r\n",
            b"Three to get ready\r\nFour let's",
            b" go",
        )
        with (
            Shitty(columns=10, rows=4, save_lines=100) as batched,
            Shitty(columns=10, rows=4, save_lines=100) as separate,
        ):
            batched.write(initial)
            separate.write(initial)
            batched.write(b"".join(tokens))
            separate.write_chunks(*tokens)
            self.assertEqual(batched.model_digest(), separate.model_digest())
            self.assertEqual(batched.all_text(), separate.all_text())
            self.assertEqual(batched.cursor_pending_wrap(), separate.cursor_pending_wrap())

    def test_seeded_mixed_ascii_batches_match_separate_public_writes(self):
        rng = random.Random(0)
        with (
            Shitty(columns=10, rows=4, save_lines=100) as batched,
            Shitty(columns=10, rows=4, save_lines=100) as separate,
        ):
            for iteration in range(100):
                batched.write(b"\x1bc")
                separate.write(b"\x1bc")
                initial = b"".join(
                    bytes([65 + index]) * rng.randrange(0, 40) + b"\r\n"
                    for index in range(rng.randrange(0, 8))
                )
                tokens = []
                letter = ord("a")
                for _ in range(rng.randrange(1, 8)):
                    token = bytearray()
                    line_count = rng.randrange(0, 8)
                    for line in range(line_count):
                        token.extend(bytes([letter]) * rng.randrange(0, 40))
                        letter = ord("a") + (letter - ord("a") + 1) % 26
                        if line + 1 < line_count or rng.randrange(2):
                            token.extend(b"\r\n")
                    tokens.append(bytes(token))

                batched.write(initial + b"".join(tokens))
                separate.write(initial)
                separate.write_chunks(*(token for token in tokens if token))
                with self.subTest(iteration=iteration):
                    self.assertEqual(batched.model_digest(), separate.model_digest())
                    self.assertEqual(
                        batched.cursor_pending_wrap(), separate.cursor_pending_wrap()
                    )

    def test_mixed_ascii_batch_matches_separate_writes_in_insert_mode(self):
        with (
            Shitty(columns=10, rows=4, save_lines=20) as batched,
            Shitty(columns=10, rows=4, save_lines=20) as separate,
        ):
            initial = b"abcdefghij\x1b[1;1H"
            first = b"\x1b[4hhello\r\nworld\r\n"
            second = b"\x1b[4lback\r\n"
            batched.write(initial + first + second)
            separate.write(initial)
            separate.write_chunks(b"\x1b[4h", b"hello", b"\r\n", b"world", b"\r\n")
            separate.write_chunks(b"\x1b[4l", b"back", b"\r\n")
            self.assertEqual(batched.model_digest(), separate.model_digest())
            self.assertEqual(batched.all_text(), separate.all_text())

    def test_mixed_ascii_batch_matches_separate_writes_with_autowrap_off(self):
        with (
            Shitty(columns=10, rows=4, save_lines=20) as batched,
            Shitty(columns=10, rows=4, save_lines=20) as separate,
        ):
            initial = b"abcdefghij\x1b[1;1H"
            first = b"\x1b[?7lhello-world\r\nsecond-line\r\n"
            second = b"\x1b[?7hback-to-wrap-around"
            batched.write(initial + first + second)
            separate.write(initial)
            separate.write_chunks(
                b"\x1b[?7l", b"hello-world", b"\r\n", b"second-line", b"\r\n"
            )
            separate.write_chunks(b"\x1b[?7h", b"back-to-wrap-around")
            self.assertEqual(batched.model_digest(), separate.model_digest())
            self.assertEqual(batched.all_text(), separate.all_text())

    def _assert_same_public_terminal(self, left, right):
        self.assertEqual(left.model_digest(), right.model_digest())
        self.assertEqual(left.all_text(), right.all_text())
        self.assertEqual(left.cursor_pending_wrap(), right.cursor_pending_wrap())

    def _assert_stream_transition(
        self,
        setup,
        first_tokens,
        restore,
        second_tokens,
        *,
        initial=b"",
        first_check=None,
        final_check=None,
    ):
        with (
            Shitty(columns=10, rows=4, save_lines=100) as batched,
            Shitty(columns=10, rows=4, save_lines=100) as separate,
        ):
            batched.write(initial + setup + b"".join(first_tokens))
            if initial:
                separate.write(initial)
            if setup:
                separate.write(setup)
            separate.write_chunks(*first_tokens)
            self._assert_same_public_terminal(batched, separate)
            if first_check is not None:
                first_check(batched)
                first_check(separate)

            batched.write(restore + b"".join(second_tokens))
            if restore:
                separate.write(restore)
            separate.write_chunks(*second_tokens)
            self._assert_same_public_terminal(batched, separate)
            if final_check is not None:
                final_check(batched)
                final_check(separate)

    def test_vt52_stream_matches_separate_writes_before_returning_to_ansi(self):
        self._assert_stream_transition(
            b"\x1b[?2l",
            (b"hello\r\n", b"world\r\n"),
            b"\x1b<",
            (b"back", b"\r\n"),
            first_check=lambda terminal: self.assertTrue(
                any("world" in line for line in terminal.model_snapshot().lines)
            ),
            final_check=lambda terminal: self.assertIn(
                "back      ", terminal.model_snapshot().lines
            ),
        )

    def test_alternate_buffer_stream_matches_separate_writes(self):
        self._assert_stream_transition(
            b"\x1b[?1049h",
            (b"hello\r\n", b"world\r\n"),
            b"\x1b[?1049l",
            (b"back", b"\r\n"),
            first_check=lambda terminal: self.assertEqual(
                terminal.conformance_state()["screen"], "Alternate"
            ),
            final_check=lambda terminal: self.assertEqual(
                terminal.conformance_state()["screen"], "Primary"
            ),
        )

    def test_command_start_semantics_survive_mixed_stream_batching(self):
        def check_command(terminal):
            self.assertEqual(self._semantic_chars(terminal, 2), "helloworld")

        self._assert_stream_transition(
            b"\x1b]133;A\x1b\\prompt>\x1b]133;B\x1b\\",
            (b"hello\r\n", b"world\r\n"),
            b"\x1b]133;D;0\x1b\\",
            (b"back", b"\r\n"),
            first_check=check_command,
            final_check=lambda terminal: self.assertIn(
                "back", "".join(terminal.all_text())
            ),
        )

    def test_line_drawing_stream_returns_to_normal_text(self):
        def check_graphics(terminal):
            self.assertEqual(terminal.model_snapshot().lines[0], "┘┐┌└┼     ")

        self._assert_stream_transition(
            b"\x1b(0",
            (b"jkl", b"mn\r\n"),
            b"\x1b(B",
            (b"back", b"\r\n"),
            first_check=check_graphics,
            final_check=lambda terminal: self.assertEqual(
                terminal.model_snapshot().lines[1], "back      "
            ),
        )

    def test_parser_observation_does_not_change_mixed_stream_result(self):
        tokens = (b"hello", b"\r\n", b"world", b"\r\n", b"back")
        with (
            Shitty(columns=10, rows=4, save_lines=20) as reference,
            Shitty(columns=10, rows=4, save_lines=20) as observed,
        ):
            reference.write(b"".join(tokens))
            observed.parser_trace_on()
            observed.write_chunks(*tokens)
            trace = observed.parser_trace()

            self._assert_same_public_terminal(reference, observed)
            self.assertTrue(trace)
            self.assertTrue(any(event == "text" for event, _ in trace))
            self.assertTrue(any(event == "control" for event, _ in trace))

    def test_published_intermediate_snapshots_preserve_stream_result(self):
        tokens = (b"hello", b"\r\n", b"world", b"\r\n", b"back")
        with (
            Shitty(columns=10, rows=4, save_lines=20) as reference,
            Shitty(columns=10, rows=4, save_lines=20) as published,
        ):
            reference.write(b"".join(tokens))
            snapshots = []
            for token in tokens:
                published.write(token)
                snapshots.append(published.model_snapshot())

            self._assert_same_public_terminal(reference, published)
            self.assertEqual(snapshots[0].lines[0], "hello     ")
            self.assertEqual(snapshots[-1].lines, reference.model_snapshot().lines)

    def test_pending_status_expectation_does_not_change_stream_processing(self):
        tokens = (b"hello", b"\x1b[6n", b"\r\nworld\r\n")
        with (
            Shitty(columns=10, rows=4, save_lines=20) as batched,
            Shitty(columns=10, rows=4, save_lines=20) as separate,
        ):
            batched.write(b"".join(tokens))
            separate.write_chunks(*tokens)
            batched.write(b"back\r\n")
            separate.write_chunks(b"back", b"\r\n")

            self._assert_same_public_terminal(batched, separate)
            self.assertEqual(batched.read_input(), separate.read_input())

    @unittest.expectedFailure
    def test_media_copy_controller_redirects_then_restores_screen_output(self):
        with Shitty(columns=10, rows=4, save_lines=20) as terminal:
            terminal.write(b"\x1b[5ihello\r\nworld\r\n")
            self.assertNotIn("hello", "".join(terminal.all_text()))
            terminal.write(b"\x1b[4iback\r\n")
            self.assertIn("back", "".join(terminal.all_text()))

    def test_multiple_public_conditions_preserve_mixed_stream_result(self):
        def check_conditions(terminal):
            self.assertTrue(terminal.conformance_state()["IRM"])
            self.assertEqual(self._semantic_chars(terminal, 2), "helloworld")

        self._assert_stream_transition(
            b"\x1b[4h\x1b]133;A\x1b\\prompt>\x1b]133;B\x1b\\",
            (b"hello\r\n", b"world\r\n"),
            b"\x1b[4l\x1b]133;D;0\x1b\\",
            (b"back", b"\r\n"),
            first_check=check_conditions,
            final_check=lambda terminal: self.assertFalse(
                terminal.conformance_state()["IRM"]
            ),
        )

    def test_consumed_status_reply_allows_following_stream(self):
        with Shitty(columns=10, rows=4, save_lines=20) as terminal:
            terminal.write(b"hello\x1b[6n\r\n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;6R")
            terminal.write_chunks(b"world", b"\r\n")
            self.assertIn("hello", "".join(terminal.all_text()))
            self.assertIn("world", "".join(terminal.all_text()))

    def test_expired_synchronized_update_allows_following_stream(self):
        with Shitty(columns=10, rows=4, save_lines=20) as terminal:
            before = terminal.snapshot().refresh_count
            terminal.write_chunks(b"\x1b[?2026h", b"hello", b"\r\n")
            self.assertEqual(terminal.snapshot().refresh_count, before)

            terminal.sync_timeout()
            released = terminal.snapshot()
            self.assertGreater(released.refresh_count, before)
            terminal.write_chunks(b"world", b"\r\n")
            self.assertIn("hello", "".join(terminal.all_text()))
            self.assertIn("world", "".join(terminal.all_text()))

    def test_semantic_post_action_drain_allows_following_stream(self):
        with Shitty(columns=10, rows=5, save_lines=20) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\prompt>"
                b"\x1b]133;B\x1b\\command\r\n"
                b"\x1b]133;D;0\x1b\\"
            )
            terminal.write_chunks(b"after\r\n", b"verify\r\n")

            self.assertEqual(self._semantic_chars(terminal, 1), "prompt>")
            self.assertEqual(self._semantic_chars(terminal, 2), "command")
            self.assertIn("after", "".join(terminal.all_text()))
            self.assertIn("verify", "".join(terminal.all_text()))

    def test_bounded_history_drops_whole_oldest_blocks_and_keeps_newest_tail(self):
        with Shitty(columns=8, rows=8, save_lines=6) as terminal:
            terminal.write(
                b"".join(
                    bytes([letter]) * 10 + b"\r\n"
                    for letter in range(ord("a"), ord("k"))
                )
            )
            self.assertEqual(
                terminal.all_text(),
                (
                    "dd",
                    "eeeeeeee",
                    "ee",
                    "ffffffff",
                    "ff",
                    "gggggggg",
                    "gg",
                    "hhhhhhhh",
                    "hh",
                    "iiiiiiii",
                    "ii",
                    "jjjjjjjj",
                    "jj",
                    "",
                ),
            )
            self.assertEqual(terminal.scrollback_state(), (6, 14, 8, 6))

            terminal.write(
                b"".join(
                    bytes([letter]) * 10 + b"\r\n"
                    for letter in range(ord("k"), ord("p"))
                )
            )
            self.assertEqual(
                terminal.all_text(),
                (
                    "ii",
                    "jjjjjjjj",
                    "jj",
                    "kkkkkkkk",
                    "kk",
                    "llllllll",
                    "ll",
                    "mmmmmmmm",
                    "mm",
                    "nnnnnnnn",
                    "nn",
                    "oooooooo",
                    "oo",
                    "",
                ),
            )

    def test_el_after_cursor_preserves_a_full_previous_soft_wrap(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"abcdefgh\r\x1b[K")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcde", "     ", "     ", "     "])
            self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_el_after_cursor_hardens_an_incomplete_previous_line(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"abcdefgh\x1b[1;5H\x1b[K")
            shortened = terminal.model_snapshot()
            self.assertEqual(shortened.lines[:2], ["abcd ", "fgh  "])
            self.assertFalse(shortened.cell(4, 0).wrapped)

            terminal.write(b"\x1b[2;1H\x1b[K")
            final = terminal.model_snapshot()
            self.assertEqual(final.lines[:2], ["abcd ", "     "])
            self.assertFalse(final.cell(4, 0).wrapped)

    def test_ed_after_cursor_preserves_a_full_previous_soft_wrap(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(b"abcdefgh\r\x1b[J")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["abcde", "     ", "     ", "     "])
            self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_progress_pause_without_percentage_keeps_current_percentage(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;1;60\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 60"])
            terminal.write(b"\x1b]9;4;4\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 4 60"])

    def test_progress_pause_without_percentage_keeps_error_percentage(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;2;25\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 2 25"])
            terminal.write(b"\x1b]9;4;4\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 4 25"])

    def test_progress_pause_without_percentage_starts_at_zero(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;4\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 4 0"])

    def test_progress_pause_without_percentage_keeps_explicit_zero(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;1;0\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 0"])
            terminal.write(b"\x1b]9;4;4\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 4 0"])

    def test_progress_pause_with_invalid_percentage_is_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;1;60\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 60"])

            terminal.write(b"\x1b]9;4;4;101\x07")
            self.assertEqual(terminal.read_actions(), [])
            terminal.write(b"\x1b]9;4;4;-1\x07")
            self.assertEqual(terminal.read_actions(), [])

    def test_progress_pause_with_explicit_percentage_uses_every_boundary(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;1;60\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 60"])

            for percent in (30, 0, 100):
                terminal.write(f"\x1b]9;4;4;{percent}\x07".encode())
                self.assertEqual(
                    terminal.read_actions(),
                    [f"PROGRESS 4 {percent}"],
                )

    def test_progress_other_states_follow_consensus_missing_value_rules(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]9;4;1;40\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 40"])

            terminal.write(b"\x1b]9;4;1;101\x07")
            self.assertEqual(terminal.read_actions(), [])
            terminal.write(b"\x1b]9;4;1\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 1 0"])

            terminal.write(b"\x1b]9;4;2\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 2 0"])
            terminal.write(b"\x1b]9;4;3\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 3 0"])
            terminal.write(b"\x1b]9;4;0\x07")
            self.assertEqual(terminal.read_actions(), ["PROGRESS 0 0"])


if __name__ == "__main__":
    unittest.main()

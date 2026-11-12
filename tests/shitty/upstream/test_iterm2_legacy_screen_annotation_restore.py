# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Fifth public batch from iTerm2's legacy VT100ScreenTest."""

import unittest

from harness import Shitty, put_rows


PORTED_CASES = (
    (
        "testResizeWithNoteFirstLinePlusFirstCharacterOfSecondLine",
        "test_restore_note_first_line_plus_first_character_of_second",
    ),
    (
        "testResizeWithNoteFirstTwoCharactersOfSecondLine",
        "test_restore_note_first_two_characters_of_second_line",
    ),
    ("testResizeWithNoteSecondLine", "test_restore_note_second_line"),
    (
        "testResizeWithNoteLastFourCharactersOfSecondLine",
        "test_restore_note_last_four_characters_of_second_line",
    ),
    (
        "testResizeWithNoteSecondCharacterOfSecondLineToSecondCharacterOfThirdLine",
        "test_restore_note_second_character_of_second_to_second_of_third",
    ),
    (
        "testResizeWithNoteSecondAndThirdLines",
        "test_restore_note_second_and_third_lines",
    ),
    (
        "testResizeWithNoteSecondThroughFourthLines",
        "test_restore_note_second_through_fourth_lines",
    ),
    (
        "testResizeWithNoteSecondThroughFifthLines",
        "test_restore_note_second_through_fifth_lines",
    ),
    (
        "testResizeWithNoteSecondCharacterOfSecondLineThroughFirstCharacterOfFifthLine",
        "test_restore_note_second_character_of_second_through_first_of_fifth",
    ),
    (
        "testResizeWithNoteThirdLineThroughFifthLine",
        "test_restore_note_third_through_fifth_lines",
    ),
    (
        "testResizeWithNoteThirdLineThroughMiddleOfFifthLine",
        "test_restore_note_third_through_middle_of_fifth",
    ),
    ("testResizeWithNoteFifthLine", "test_restore_note_fifth_line"),
    ("testResizeWithNoteAllLines", "test_restore_note_all_lines"),
    (
        "testResizeWithBlanksBeforeAnnotation",
        "test_resize_keeps_range_metadata_after_preceding_blank_line",
    ),
    ("testNoteResizeRegression1", "test_restore_blank_note_on_first_line"),
    ("testNoteResizeRegression2", "test_restore_blank_note_on_second_line"),
    ("testNoteResizeRegression3", "test_restore_blank_note_on_third_line"),
    (
        "testNoteResizeRegression4",
        "test_restore_multiline_note_across_width_round_trip",
    ),
    ("testNoteResizeRegression5", "test_restore_blank_note_on_twelfth_line"),
    (
        "testEmptyLineRestoresBackgroundColor",
        "test_empty_history_line_restores_background_color",
    ),
)

URI = b"https://example.test/iterm2-restored-note"
RESTORE_ROWS = (b"", b"abcde", b"fgh", b"", b"ijkl", b"", b"", b"", b"")


def osc8(uri=URI):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def close_osc8():
    return osc8(b"")


def cup(column, row):
    return f"\x1b[{row + 1};{column + 1}H".encode()


def linear_offset(point, width):
    return point[1] * width + point[0]


def mark_range(terminal, width, rows, start, end):
    """Attach public cell metadata to the half-open row-major range."""
    first = linear_offset(start, width)
    last = linear_offset(end, width)
    for offset in range(first, last):
        row, column = divmod(offset, width)
        value = rows[row][column : column + 1] if column < len(rows[row]) else b" "
        terminal.write(cup(column, row) + osc8() + value + close_osc8())


def assert_marked_range(test, terminal, width, height, start, end):
    first = linear_offset(start, width)
    last = linear_offset(end, width)
    for row in range(height):
        for column in range(width):
            expected = first <= row * width + column < last
            test.assertEqual(
                bool(terminal.hyperlink(column, row)),
                expected,
                (column, row),
            )


def save_annotation_state(terminal):
    """Use a real host-state serializer when Shitty gains one."""
    operation = getattr(terminal, "save_annotation_state", None)
    if operation is None:
        raise AssertionError(
            "iTerm2 serializes arbitrary PTYAnnotation objects, including "
            "ranges over untouched empty cells; Shitty has no corresponding "
            "host session-state operation"
        )
    return operation()


def restore_annotation_state(terminal, state):
    operation = getattr(terminal, "restore_annotation_state", None)
    if operation is None:
        raise AssertionError(
            "Shitty has no host session-state operation that restores "
            "serialized arbitrary annotations"
        )
    operation(state)


class ITerm2LegacyScreenAnnotationRestoreTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def assert_note_state_round_trip(self, start, end):
        with Shitty(columns=5, rows=9, save_lines=20) as terminal:
            # Preserve the source's visible rows and one real soft wrap.
            terminal.write(put_rows(b"", b"abcdefgh", b"", b"", b"ijkl"))
            mark_range(terminal, 5, RESTORE_ROWS, start, end)
            assert_marked_range(self, terminal, 5, 9, start, end)
            state = save_annotation_state(terminal)

        with Shitty(columns=3, rows=4, save_lines=20) as restored:
            restore_annotation_state(restored, state)
            snapshot = restored.model_snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (5, 9))
            assert_marked_range(self, restored, 5, 9, start, end)

    @unittest.expectedFailure
    def test_restore_note_first_line_plus_first_character_of_second(self):
        self.assert_note_state_round_trip((0, 0), (2, 1))

    @unittest.expectedFailure
    def test_restore_note_first_two_characters_of_second_line(self):
        self.assert_note_state_round_trip((0, 1), (3, 1))

    @unittest.expectedFailure
    def test_restore_note_second_line(self):
        self.assert_note_state_round_trip((0, 1), (5, 1))

    @unittest.expectedFailure
    def test_restore_note_last_four_characters_of_second_line(self):
        self.assert_note_state_round_trip((2, 1), (5, 1))

    @unittest.expectedFailure
    def test_restore_note_second_character_of_second_to_second_of_third(self):
        self.assert_note_state_round_trip((2, 1), (2, 2))

    @unittest.expectedFailure
    def test_restore_note_second_and_third_lines(self):
        self.assert_note_state_round_trip((0, 1), (5, 2))

    @unittest.expectedFailure
    def test_restore_note_second_through_fourth_lines(self):
        self.assert_note_state_round_trip((0, 1), (5, 3))

    @unittest.expectedFailure
    def test_restore_note_second_through_fifth_lines(self):
        self.assert_note_state_round_trip((0, 1), (5, 4))

    @unittest.expectedFailure
    def test_restore_note_second_character_of_second_through_first_of_fifth(self):
        self.assert_note_state_round_trip((2, 1), (2, 4))

    @unittest.expectedFailure
    def test_restore_note_third_through_fifth_lines(self):
        self.assert_note_state_round_trip((0, 3), (5, 4))

    @unittest.expectedFailure
    def test_restore_note_third_through_middle_of_fifth(self):
        self.assert_note_state_round_trip((0, 3), (3, 4))

    @unittest.expectedFailure
    def test_restore_note_fifth_line(self):
        self.assert_note_state_round_trip((0, 4), (5, 4))

    @unittest.expectedFailure
    def test_restore_note_all_lines(self):
        self.assert_note_state_round_trip((0, 0), (5, 4))

    def test_resize_keeps_range_metadata_after_preceding_blank_line(self):
        lines = (
            b"Last login: Mon Dec  9 23:22:07 on ttys011",
            b"You have mail.",
            b"Georges-iMac:/Users/gnachman% echo;echo xxxxxxxxxx",
            b"",
            osc8() + b"xxxxxxxxxx" + close_osc8(),
            b"Georges-iMac:/Users/gnachman%",
        )
        with Shitty(columns=142, rows=8, save_lines=1000) as terminal:
            terminal.write(put_rows(*lines))
            terminal.resize(141, 8)
            for column in range(10):
                self.assertEqual(terminal.hyperlink(column, 4), URI.decode())
            self.assertEqual(terminal.hyperlink(10, 4), "")
            self.assertEqual(terminal.hyperlink(0, 3), "")

    def assert_note_resize_regression(self, initial, intermediate):
        rows = [b""] * 25
        rows[3] = (
            b"Georges-iMac:/Users/gnachman% "
            + b"x" * 73
        )
        with Shitty(columns=80, rows=25, save_lines=1000) as terminal:
            terminal.write(put_rows(*rows[:4]))
            mark_range(terminal, 80, rows, *initial)
            assert_marked_range(self, terminal, 80, 25, *initial)
            state = save_annotation_state(terminal)

        with Shitty(columns=80, rows=25, save_lines=1000) as restored:
            restore_annotation_state(restored, state)
            restored.resize(77, 25)
            assert_marked_range(self, restored, 77, 25, *intermediate)
            restored.resize(80, 25)
            assert_marked_range(self, restored, 80, 25, *initial)

    @unittest.expectedFailure
    def test_restore_blank_note_on_first_line(self):
        self.assert_note_resize_regression(
            ((0, 0), (80, 0)),
            ((0, 0), (77, 0)),
        )

    @unittest.expectedFailure
    def test_restore_blank_note_on_second_line(self):
        self.assert_note_resize_regression(
            ((0, 1), (80, 1)),
            ((0, 1), (77, 1)),
        )

    @unittest.expectedFailure
    def test_restore_blank_note_on_third_line(self):
        self.assert_note_resize_regression(
            ((0, 2), (80, 2)),
            ((0, 2), (77, 2)),
        )

    @unittest.expectedFailure
    def test_restore_multiline_note_across_width_round_trip(self):
        self.assert_note_resize_regression(
            ((20, 4), (80, 6)),
            ((23, 4), (77, 6)),
        )

    @unittest.expectedFailure
    def test_restore_blank_note_on_twelfth_line(self):
        self.assert_note_resize_regression(
            ((0, 12), (80, 12)),
            ((0, 12), (77, 12)),
        )

    def test_empty_history_line_restores_background_color(self):
        with Shitty(columns=3, rows=1, save_lines=3) as terminal:
            terminal.write(b"\x1b[45m\x1b[2K\r\n")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.write(b"\x1b[49m")
            terminal.resize(3, 2)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["   ", "   "])
            for cell in snapshot.cells:
                self.assertEqual(cell.background_index, 5)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Second public batch from iTerm2's legacy VT100ScreenTest."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("testAPIsUsedByTailFind", "test_tail_find_resumes_after_buffer_growth"),
    ("testCursorXY", "test_cursor_coordinates_are_one_based_on_the_wire"),
    ("testScreenCharArrayForLine", "test_wide_wrap_topology_survives_history"),
    ("testNumberOfScrollbackLines", "test_bounded_scrollback_line_count"),
    ("testScrollbackOverflow", "test_zero_capacity_evicts_each_oldest_row"),
    ("testAbsoluteLineNumberOfCursor", "test_cursor_origin_tracks_history_eviction_and_clear"),
    ("testFind_ForwardWithWrapFromFirstChar", "test_find_forward_across_soft_wrap"),
    ("testFind_Backward", "test_find_backward_across_soft_wrap"),
    ("testFind_FromLastChar", "test_find_backward_from_last_character"),
    ("testFind_FromNullAfterLastChar", "test_find_backward_from_null_after_last_character"),
    ("testFind_FromMiddleOfScreen", "test_find_backward_from_middle_of_screen"),
    ("testFind_FromSecondCharBackward", "test_find_backward_honors_start_boundary"),
    ("testFind_WrongCase", "test_find_case_sensitive_rejects_wrong_case"),
    ("testFind_IgnoringCase", "test_find_case_insensitive_accepts_wrong_case"),
    ("testFind_Regex", "test_find_case_sensitive_regex"),
    ("testFind_RegexIgnoringCase", "test_find_case_insensitive_regex"),
    ("testFind_Offset0", "test_find_forward_offset_zero"),
    ("testFind_Offset1", "test_find_forward_offset_one"),
    ("testFind_BackwardOffset0", "test_find_backward_offset_zero"),
    ("testFind_BackwardOffset1", "test_find_backward_offset_one"),
)


def write_lines(terminal, *lines):
    for line in lines:
        terminal.write(line.encode("utf-8") + b"\r\n")


def find_text(terminal, query, **options):
    """Call the real host-search operation once Shitty provides one."""
    operation = getattr(terminal, "find_text", None)
    if operation is None:
        raise AssertionError(
            "terminal-buffer search is supported by the implementation "
            "consensus but Shitty has no host search operation"
        )
    return operation(query, **options)


class ITerm2LegacyScreenSearchTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_cursor_coordinates_are_one_based_on_the_wire(self):
        with Shitty(columns=5, rows=5) as terminal:
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[3;2H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))

    def test_wide_wrap_topology_survives_history(self):
        with Shitty(columns=6, rows=2, save_lines=8) as terminal:
            terminal.write("abcde界".encode("utf-8"))
            before = terminal.model_snapshot()
            self.assertEqual(before.lines, ["abcde ", "界     "])
            self.assertEqual(before.cell(0, 0).char, "a")
            self.assertTrue(before.cell(4, 0).wrapped)
            self.assertFalse(before.cell(5, 0).drawn)
            self.assertTrue(before.cell(0, 1).double_width)
            self.assertTrue(before.cell(1, 1).double_width_continuation)

            terminal.write(b"\r\njkl")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.wheel_up(8)
            restored = terminal.model_snapshot()
            self.assertEqual(restored.lines, ["abcde ", "界     "])
            self.assertTrue(restored.cell(4, 0).wrapped)
            self.assertFalse(restored.cell(5, 0).drawn)
            self.assertTrue(restored.cell(0, 1).double_width)
            self.assertTrue(restored.cell(1, 1).double_width_continuation)

    def test_bounded_scrollback_line_count(self):
        with Shitty(columns=5, rows=4, save_lines=2) as terminal:
            terminal.write(b"abcdefgh\r\nijkl\r\n")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            terminal.write(b"\n")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            terminal.write(b"\n")
            self.assertEqual(terminal.scrollback_state()[0], 2)
            terminal.write(b"\n")
            self.assertEqual(terminal.scrollback_state()[0], 2)
            self.assertEqual(
                terminal.all_text(),
                ("fgh", "ijkl", "", "", "", ""),
            )

    def test_zero_capacity_evicts_each_oldest_row(self):
        with Shitty(columns=5, rows=4, save_lines=0) as terminal:
            terminal.write(b"abcdefgh\r\nijkl\r\n")
            self.assertEqual(
                terminal.all_text(),
                ("abcde", "fgh", "ijkl", ""),
            )

            terminal.write(b"\n")
            self.assertEqual(terminal.all_text(), ("fgh", "ijkl", "", ""))
            terminal.write(b"\n")
            self.assertEqual(terminal.all_text(), ("ijkl", "", "", ""))

            acknowledged = terminal.model_digest()
            self.assertEqual(terminal.model_digest(), acknowledged)
            terminal.write(b"\n")
            self.assertEqual(terminal.all_text(), ("", "", "", ""))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_cursor_origin_tracks_history_eviction_and_clear(self):
        with Shitty(columns=5, rows=4, save_lines=1) as terminal:
            terminal.write(b"abcdefgh\r\nijkl\r\n")
            initial = terminal.model_snapshot()
            self.assertEqual((initial.cursor_x, initial.cursor_y), (0, 3))

            terminal.write(b"\n")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                terminal.all_text(),
                ("abcde", "fgh", "ijkl", "", ""),
            )
            terminal.write(b"\n")
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                terminal.all_text(),
                ("fgh", "ijkl", "", "", ""),
            )

            visible = terminal.model_snapshot()
            terminal.write(b"\x1b[3J")
            cleared = terminal.model_snapshot()
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.all_text(), ("ijkl", "", "", ""))
            self.assertEqual(cleared.lines, visible.lines)
            self.assertEqual(
                (cleared.cursor_x, cleared.cursor_y),
                (visible.cursor_x, visible.cursor_y),
            )

    def make_search_fixture(self):
        terminal = Shitty(columns=4, rows=5, save_lines=20)
        terminal.write(b"abcdefgc\r\nde\r\nfgx" + "界z".encode("utf-8"))
        self.assertEqual(
            terminal.all_text(),
            ("abcd", "efgc", "de", "fgx", "界z"),
        )
        terminal.resize(4, 2)
        self.assertEqual(terminal.scrollback_state()[0], 3)
        self.assertEqual(terminal.model_snapshot().lines, ["fgx ", "界 z "])
        return terminal

    def assert_search(
        self,
        query,
        *,
        start,
        backwards=False,
        offset=0,
        case_sensitive=True,
        regex=False,
        expected=(),
    ):
        terminal = self.make_search_fixture()
        try:
            result = find_text(
                terminal,
                query,
                start=start,
                backwards=backwards,
                offset=offset,
                case_sensitive=case_sensitive,
                regex=regex,
            )
            actual = tuple(zip(result["starts"], result["ends"]))
            self.assertEqual(actual, expected)
        finally:
            terminal.close()

    @unittest.expectedFailure
    def test_tail_find_resumes_after_buffer_growth(self):
        with Shitty(columns=5, rows=2, save_lines=8) as terminal:
            write_lines(terminal, "abcdefgh", "ijkl", "mnopqrstuvwxyz", "012")
            self.assertEqual(
                terminal.all_text(),
                ("abcde", "fgh", "ijkl", "mnopq", "rstuv", "wxyz", "012", ""),
            )
            initial = find_text(
                terminal,
                "wxyz",
                start=(0, 0),
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(initial["starts"], initial["ends"])),
                (((0, 5), (3, 5)),),
            )
            resume = initial["resume"]

            write_lines(terminal, "0123", "wxyz")
            continued = find_text(
                terminal,
                "wxyz",
                resume=resume,
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(continued["starts"], continued["ends"])),
                (((0, 8), (3, 8)),),
            )
            backward = find_text(
                terminal,
                "mnop",
                start="end",
                backwards=True,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(backward["starts"], backward["ends"])),
                (((0, 3), (3, 3)),),
            )

            resume = backward["resume"]
            empty_tail = find_text(
                terminal,
                "rst",
                resume=resume,
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(empty_tail["starts"], ())
            write_lines(terminal, "rst")
            tail = find_text(
                terminal,
                "rst",
                resume=resume,
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(tail["starts"], tail["ends"])),
                (((0, 9), (2, 9)),),
            )

    @unittest.expectedFailure
    def test_find_forward_across_soft_wrap(self):
        self.assert_search(
            "cde", start=(0, 0), expected=(((2, 0), (0, 1)),)
        )

    @unittest.expectedFailure
    def test_find_backward_across_soft_wrap(self):
        self.assert_search(
            "cde",
            start=(2, 4),
            backwards=True,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_backward_from_last_character(self):
        self.assert_search(
            "cde",
            start=(2, 4),
            backwards=True,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_backward_from_null_after_last_character(self):
        self.assert_search(
            "cde",
            start=(3, 4),
            backwards=True,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_backward_from_middle_of_screen(self):
        self.assert_search(
            "cde",
            start=(3, 2),
            backwards=True,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_backward_honors_start_boundary(self):
        self.assert_search("cde", start=(1, 0), backwards=True, expected=())

    @unittest.expectedFailure
    def test_find_case_sensitive_rejects_wrong_case(self):
        self.assert_search("CDE", start=(0, 0), case_sensitive=True, expected=())

    @unittest.expectedFailure
    def test_find_case_insensitive_accepts_wrong_case(self):
        self.assert_search(
            "CDE",
            start=(0, 0),
            case_sensitive=False,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_case_sensitive_regex(self):
        self.assert_search(
            "c.e",
            start=(0, 0),
            regex=True,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_case_insensitive_regex(self):
        self.assert_search(
            "C.E",
            start=(0, 0),
            regex=True,
            case_sensitive=False,
            expected=(((2, 0), (0, 1)),),
        )

    @unittest.expectedFailure
    def test_find_forward_offset_zero(self):
        self.assert_search(
            "de",
            start=(3, 0),
            offset=0,
            expected=(((3, 0), (0, 1)), ((0, 2), (1, 2))),
        )

    @unittest.expectedFailure
    def test_find_forward_offset_one(self):
        self.assert_search(
            "de",
            start=(3, 0),
            offset=1,
            expected=(((0, 2), (1, 2)),),
        )

    @unittest.expectedFailure
    def test_find_backward_offset_zero(self):
        self.assert_search(
            "de",
            start=(0, 2),
            backwards=True,
            offset=0,
            expected=(((0, 2), (1, 2)), ((3, 0), (0, 1))),
        )

    @unittest.expectedFailure
    def test_find_backward_offset_one(self):
        self.assert_search(
            "de",
            start=(0, 2),
            backwards=True,
            offset=1,
            expected=(((3, 0), (0, 1)),),
        )


if __name__ == "__main__":
    unittest.main()

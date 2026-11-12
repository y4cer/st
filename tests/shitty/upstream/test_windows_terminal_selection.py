# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import re
import unittest
from pathlib import Path

from harness import Shitty


UPSTREAM = (
    Path(__file__).parent
    / "windows_terminal"
    / "upstream"
    / "SelectionTest.cpp"
)

UPSTREAM_METHODS = (
    "SelectUnit",
    "SelectArea",
    "OverflowTests",
    "SelectFromOutofBounds",
    "SelectToOutOfBounds",
    "SelectBoxArea",
    "SelectAreaAfterScroll",
    "SelectWideGlyph_Trailing",
    "SelectWideGlyph_Leading",
    "SelectWideGlyphsInBoxSelection",
    "DoubleClick_GeneralCase",
    "DoubleClick_Delimiter",
    "DoubleClick_DelimiterClass",
    "DoubleClickDrag_Right",
    "DoubleClickDrag_Left",
    "TripleClick_GeneralCase",
    "TripleClick_WrappedLine",
    "TripleClickDrag_Horizontal",
    "TripleClickDrag_Vertical",
    "ShiftClick",
    "Pivot",
)


def put_at(column, row, text):
    return f"\x1b[{row + 1};{column + 1}H".encode() + text


def select_word(terminal, column, row):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)


def select_line(terminal, column, row):
    select_word(terminal, column, row)
    terminal.select_extend(column, row, cycle=True)


def assert_selection(test, terminal, expected, rectangular=False):
    state = terminal.selection_state()
    test.assertEqual(state["snapped"], expected)
    test.assertEqual(state["snapped_rectangular"], rectangular)


class WindowsTerminalSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = UPSTREAM.read_text()
        methods = tuple(re.findall(r"TEST_METHOD\(([^)]+)\)", source))
        if methods != UPSTREAM_METHODS:
            raise AssertionError(
                f"upstream selection method manifest changed: {methods!r}"
            )

    def test_select_unit(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.select_start(5, 10)
            assert_selection(self, terminal, (5, 10, 5, 10))

    def test_select_area(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.select_start(5, 10)
            terminal.select_update(15, 20)
            assert_selection(self, terminal, (5, 10, 15, 20))

    def test_overflow_tests(self):
        for save_lines in (0, 32767):
            with self.subTest(save_lines=save_lines):
                with Shitty(
                    columns=10,
                    rows=10,
                    save_lines=save_lines,
                ) as terminal:
                    terminal.select_start(32767, 32767)
                    assert_selection(self, terminal, (10, 9, 10, 9))

                with Shitty(
                    columns=10,
                    rows=10,
                    save_lines=save_lines,
                ) as terminal:
                    select_word(terminal, 32767, 32767)
                    assert_selection(self, terminal, (0, 9, 10, 9))

                with Shitty(
                    columns=10,
                    rows=10,
                    save_lines=save_lines,
                ) as terminal:
                    select_line(terminal, 32767, 32767)
                    assert_selection(self, terminal, (0, 9, 10, 9))

    def test_select_from_out_of_bounds(self):
        cases = (
            ((20, 5), (10, 5, 10, 5)),
            ((-20, 5), (0, 5, 0, 5)),
            ((5, -20), (5, 0, 5, 0)),
            ((5, 20), (5, 9, 5, 9)),
        )
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            for point, expected in cases:
                with self.subTest(point=point):
                    terminal.select_start(*point)
                    assert_selection(self, terminal, expected)

    def test_select_to_out_of_bounds(self):
        cases = (
            ((20, 5), (5, 5, 10, 5)),
            ((-20, 5), (0, 5, 5, 5)),
            ((5, -20), (5, 0, 5, 5)),
            ((5, 20), (5, 5, 5, 9)),
        )
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            for point, expected in cases:
                with self.subTest(point=point):
                    terminal.select_start(5, 5)
                    terminal.select_update(*point)
                    assert_selection(self, terminal, expected)

    @unittest.expectedFailure
    def test_select_box_area(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.select_start(5, 10)
            terminal.select_rectangular()
            terminal.select_update(15, 20)
            assert_selection(
                self,
                terminal,
                (5, 10, 15, 20),
                rectangular=True,
            )
            self.assertEqual(
                terminal.select_finish(),
                b"\n".join([b" " * 10] * 11),
            )

    def test_select_area_after_scroll(self):
        lines = [
            f"line-{index:03}-abcdefghijklmnop".encode()
            for index in range(45)
        ]
        with Shitty(
            columns=120,
            rows=30,
            save_lines=100,
        ) as terminal:
            terminal.write(b"\r\n".join(lines))
            self.assertEqual(terminal.scrollback_state()[0], 15)

            terminal.select_start(5, 10)
            terminal.select_update(15, 20)
            assert_selection(self, terminal, (5, 10, 15, 20))
            expected = (
                lines[25][5:]
                + b"\n"
                + b"\n".join(lines[26:35])
                + b"\n"
                + lines[35][:15]
            )
            self.assertEqual(terminal.select_finish(), expected)

            terminal.page_up()
            terminal.select_start(5, 10)
            terminal.select_update(15, 20)
            assert_selection(self, terminal, (5, 10, 15, 20))
            expected = (
                lines[10][5:]
                + b"\n"
                + b"\n".join(lines[11:20])
                + b"\n"
                + lines[20][:15]
            )
            self.assertEqual(terminal.select_finish(), expected)

    def test_select_wide_glyph_trailing(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(put_at(4, 10, "🌯".encode()))
            terminal.select_start(5, 10)
            assert_selection(self, terminal, (4, 10, 6, 10))

    def test_select_wide_glyph_leading(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(put_at(4, 10, "🌯".encode()))
            terminal.select_start(4, 10)
            assert_selection(self, terminal, (4, 10, 4, 10))

    def test_select_wide_glyphs_in_box_selection(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(
                put_at(4, 10, "🌯".encode())
                + put_at(7, 11, "🌯".encode())
            )
            terminal.select_start(5, 8)
            terminal.select_rectangular()
            terminal.select_update(8, 12)
            assert_selection(
                self,
                terminal,
                (5, 8, 8, 12),
                rectangular=True,
            )
            # Windows validates the five renderer spans here: rows 10 and 11
            # expand independently around the wide glyphs. Shitty performs
            # the equivalent expansion in the renderer; its reference-path
            # unit test covers the resulting whole-glyph highlight.

    def test_double_click_general_case(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(put_at(4, 10, b"doubleClickMe"))
            select_word(terminal, 5, 10)
            assert_selection(self, terminal, (4, 10, 17, 10))

    def test_double_click_delimiter(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            select_word(terminal, 5, 10)
            assert_selection(self, terminal, (0, 10, 100, 10))

    def test_double_click_delimiter_class(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(put_at(4, 10, b"C:\\Terminal>"))
            select_word(terminal, 15, 10)
            assert_selection(self, terminal, (15, 10, 16, 10))

    def test_double_click_drag_right(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(
                put_at(4, 10, b"doubleClickMe dragThroughHere")
            )
            select_word(terminal, 5, 10)
            terminal.select_update(21, 10)
            assert_selection(self, terminal, (4, 10, 33, 10))

    def test_double_click_drag_left(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(
                put_at(4, 10, b"doubleClickMe dragThroughHere")
            )
            select_word(terminal, 21, 10)
            terminal.select_update(5, 10)
            assert_selection(self, terminal, (4, 10, 33, 10))

    def test_triple_click_general_case(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            select_line(terminal, 5, 10)
            assert_selection(self, terminal, (0, 10, 100, 10))

    def test_triple_click_wrapped_line(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            terminal.write(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            select_line(terminal, 3, 1)
            assert_selection(self, terminal, (0, 0, 10, 2))
            self.assertEqual(
                terminal.select_finish(),
                b"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            )

    def test_triple_click_drag_horizontal(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            select_line(terminal, 5, 10)
            terminal.select_update(7, 10)
            assert_selection(self, terminal, (0, 10, 100, 10))

    def test_triple_click_drag_vertical(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            select_line(terminal, 5, 10)
            terminal.select_update(5, 11)
            assert_selection(self, terminal, (0, 10, 100, 11))

    def test_shift_click(self):
        text = b"doubleClickMe dragThroughHere anotherWord"
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.write(put_at(4, 10, text))
            select_word(terminal, 5, 10)
            assert_selection(self, terminal, (4, 10, 17, 10))

            # Foot and Kitty preserve the original word-wise mode when an
            # existing word selection is extended. Windows Terminal can
            # explicitly replace the mode on every Shift+click; the generic
            # desktop input contract does not carry that Windows-only enum.
            terminal.select_extend(21, 10)
            assert_selection(self, terminal, (4, 10, 33, 10))

            terminal.select_update(35, 10)
            assert_selection(self, terminal, (4, 10, 45, 10))
            terminal.select_update(21, 10)
            assert_selection(self, terminal, (4, 10, 33, 10))
            terminal.select_update(25, 10)
            assert_selection(self, terminal, (4, 10, 33, 10))

            terminal.select_start(4, 10)
            terminal.select_extend(22, 10)
            assert_selection(self, terminal, (4, 10, 22, 10))

            select_line(terminal, 21, 10)
            terminal.select_extend(35, 10)
            assert_selection(self, terminal, (0, 10, 100, 10))

    def test_pivot(self):
        with Shitty(columns=100, rows=100, save_lines=0) as terminal:
            terminal.select_start(10, 10)
            terminal.select_update(21, 10)
            assert_selection(self, terminal, (10, 10, 21, 10))

            terminal.select_update(5, 10)
            assert_selection(self, terminal, (5, 10, 10, 10))
            terminal.select_update(20, 10)
            assert_selection(self, terminal, (10, 10, 20, 10))

            terminal.select_extend(5, 10)
            assert_selection(self, terminal, (5, 10, 10, 10))
            terminal.select_extend(21, 10)
            assert_selection(self, terminal, (10, 10, 21, 10))


if __name__ == "__main__":
    unittest.main()

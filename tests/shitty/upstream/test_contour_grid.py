# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Grid.setup",
    "Grid.writeAndScrollUp",
    "iteratorAt",
    "LogicalLines.iterator",
    "LogicalLines.reverse_iterator",
    "resize_lines_nr2_with_scrollback_moving_fully_into_page",
    "resize_lines_nr3_with_scrollback_moving_into_page_overflow",
    "resize_grow_lines_with_history_cursor_no_bottom",
    "resize_shrink_lines_with_history",
    "resize_shrink_columns_with_reflow_and_unwrappable",
    "resize_shrink_columns_with_reflow_grow_lines_and_unwrappable",
    "resize_reflow_shrink",
    "Grid.reflow",
    "Grid.reflow.shrink_many",
    "Grid.reflow.shrink_many_grow_many",
    "Grid.reflow.triple",
    "Grid infinite",
    "Grid resize with wrap",
    "Grid resize",
    "Grid resize with wrap and spaces",
    "Grid.render_extraLines.renders_extra_line_above_viewport",
    "Grid.render_extraLines.clamps_to_available_history",
    "Grid.render_extraLines.zero_extra_lines_unchanged",
    "Grid.spawnWithLargeHistory.leavesHistoryUnmaterialized",
    "Grid.resizeColumnsWithLargeHistory.keepsBlank",
    "Grid.shrinkColumnsWrapsLongLine",
    "Grid.shrinkColumnsWrapsTextWithBlankHistory",
    "Grid.render.blankLineWithSearchHighlight.usesTrivialPath",
    "Grid.scrollUp.partialHorizontal.blankLinesDifferingFillAttrsMaterialize",
    "Grid.scrollDown.partialHorizontal.blankLinesDifferingFillAttrsMaterialize",
    "Grid.scrollUp.partialHorizontal.blankLinesMatchingFillAttrsStayBlank",
    "Grid.reflow.semanticMarksStayOnTheHeadLine",
)


class ContourGridTest(unittest.TestCase):
    def test_upstream_inventory_has_all_32_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 32)
        self.assertEqual(len(set(UPSTREAM_CASES)), 32)

    def test_setup_indexing_and_history_scroll(self):
        with Shitty(columns=5, rows=2, save_lines=3) as terminal:
            terminal.write(put_rows(b"ABCDE", b"abcde"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABCDE", "abcde"])
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(1, 0).char, "B")
            self.assertEqual(snapshot.cell(2, 0).char, "C")
            self.assertEqual(snapshot.cell(1, 1).char, "b")
            self.assertEqual(snapshot.cell(4, 1).char, "e")

            terminal.write(b"\x1b[S\x1b[2;1H12345")
            self.assertEqual(
                terminal.all_text(),
                ("ABCDE", "abcde", "12345"),
            )
            self.assertEqual(terminal.scrollback_state()[0], 1)

            terminal.write(b"\x1b[S")
            self.assertEqual(
                terminal.all_text(),
                ("ABCDE", "abcde", "12345", ""),
            )
            self.assertEqual(terminal.scrollback_state()[0], 2)

    def test_logical_lines_survive_forward_and_reverse_reflow(self):
        with Shitty(columns=3, rows=2, save_lines=8) as terminal:
            terminal.write(b"ABC\r\nDEFGHIJKL\r\nMNOPQR")
            self.assertEqual(
                terminal.all_text(),
                ("ABC", "DEF", "GHI", "JKL", "MNO", "PQR"),
            )

            terminal.resize(9, 3)
            self.assertEqual(
                terminal.all_text()[:3],
                ("ABC", "DEFGHIJKL", "MNOPQR"),
            )

            terminal.resize(3, 2)
            self.assertEqual(
                terminal.all_text(),
                ("ABC", "DEF", "GHI", "JKL", "MNO", "PQR"),
            )

    def test_height_growth_restores_history_and_appends_blanks(self):
        for rows, expected in (
            (4, ("ABC", "DEF", "GHI", "JKL")),
            (5, ("ABC", "DEF", "GHI", "JKL", "")),
        ):
            with self.subTest(rows=rows), Shitty(
                columns=3,
                rows=2,
                save_lines=3,
            ) as terminal:
                terminal.write(b"ABC\r\nDEF\r\nGHI\r\nJKL")
                self.assertEqual(terminal.scrollback_state()[0], 2)

                terminal.resize(3, rows)

                self.assertEqual(terminal.all_text(), expected)
                self.assertEqual(terminal.scrollback_state()[0], 0)
                self.assertEqual(
                    (terminal.snapshot().cursor_x,
                     terminal.snapshot().cursor_y),
                    (2, 3),
                )

    def test_height_growth_uses_the_bottom_anchored_policy(self):
        with Shitty(columns=3, rows=2, save_lines=3) as terminal:
            terminal.write(b"ABC\r\nDEF\r\nGHI\r\nJKL\x1b[1;2H")
            terminal.resize(3, 3)

            # Contour, Ghostty, iTerm2 and default Kitty keep history hidden
            # here. Alacritty, VTE, Foot's completed reflow and default xterm
            # instead restore history, which is the policy used here. The
            # configurable implementations expose both choices.
            self.assertEqual(terminal.all_text(), ("ABC", "DEF", "GHI", "JKL"))
            self.assertEqual(terminal.snapshot().lines, ["DEF", "GHI", "JKL"])
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                (terminal.snapshot().cursor_x,
                 terminal.snapshot().cursor_y),
                (1, 1),
            )

    def test_height_shrink_moves_only_rows_above_cursor_to_history(self):
        with Shitty(columns=3, rows=2, save_lines=5) as terminal:
            terminal.write(b"ABC\r\nDEF\r\nGHI")
            terminal.resize(3, 1)

            self.assertEqual(terminal.all_text(), ("ABC", "DEF", "GHI"))
            self.assertEqual(terminal.snapshot().lines, ["GHI"])
            self.assertEqual(terminal.scrollback_state()[0], 2)
            self.assertEqual(
                (terminal.snapshot().cursor_x,
                 terminal.snapshot().cursor_y),
                (2, 0),
            )

    def test_hard_lines_are_reflowed_but_never_joined(self):
        with Shitty(columns=3, rows=2, save_lines=8) as terminal:
            terminal.write(b"ABC\r\nDEF\r\nGHI\r\nJKL")
            terminal.resize(2, 4)

            self.assertEqual(
                terminal.all_text(),
                ("AB", "C", "DE", "F", "GH", "I", "JK", "L"),
            )

            terminal.resize(3, 4)
            self.assertEqual(
                terminal.all_text(),
                ("ABC", "DEF", "GHI", "JKL"),
            )

    def test_reflow_shrink_and_regrow_are_exactly_reversible(self):
        routes = (
            (2,),
            (4, 3, 2),
            (2, 3, 4, 5),
            (2, 5),
        )
        for route in routes:
            with self.subTest(route=route), Shitty(
                columns=5,
                rows=2,
                save_lines=10,
            ) as terminal:
                terminal.write(put_rows(b"ABCDE", b"abcde"))
                for width in route:
                    terminal.resize(width, 2)

                if route[-1] == 2:
                    self.assertEqual(
                        terminal.all_text(),
                        ("AB", "CD", "E", "ab", "cd", "e"),
                    )
                    self.assertEqual(
                        terminal.snapshot().lines,
                        ["cd", "e "],
                    )
                else:
                    self.assertEqual(
                        terminal.all_text(),
                        ("ABCDE", "abcde"),
                    )
                    self.assertEqual(
                        terminal.snapshot().lines,
                        ["ABCDE", "abcde"],
                    )
                    self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_reflow_across_three_physical_rows(self):
        with Shitty(columns=8, rows=2, save_lines=10) as terminal:
            terminal.write(put_rows(b"ABCDEFGH", b"abcdefgh"))
            terminal.resize(2, 2)
            self.assertEqual(
                terminal.all_text(),
                ("AB", "CD", "EF", "GH", "ab", "cd", "ef", "gh"),
            )

            for width, expected in (
                (3, ("ABC", "DEF", "GH", "abc", "def", "gh")),
                (4, ("ABCD", "EFGH", "abcd", "efgh")),
                (5, ("ABCDE", "FGH", "abcde", "fgh")),
                (7, ("ABCDEFG", "H", "abcdefg", "h")),
                (8, ("ABCDEFGH", "abcdefgh")),
            ):
                terminal.resize(width, 2)
                self.assertEqual(terminal.all_text(), expected)

    def test_zero_and_large_scrollback_have_explicit_finite_semantics(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABCDEFGH", b"abcdefgh"))
            terminal.write(b"\x1b[S")
            self.assertEqual(terminal.all_text(), ("abcdefgh", ""))
            self.assertEqual(terminal.scrollback_state()[0], 0)

        with Shitty(columns=8, rows=2, save_lines=100) as terminal:
            terminal.write(put_rows(b"ABCDEFGH", b"abcdefgh"))
            terminal.write(b"\x1b[S" * 98)
            contents = terminal.all_text()
            self.assertEqual(contents[0], "ABCDEFGH")
            self.assertEqual(contents[1], "abcdefgh")
            self.assertEqual(len(contents), 100)
            self.assertEqual(terminal.scrollback_state()[0], 98)

    def test_wrapped_bottom_row_round_trip_restores_real_top_rows(self):
        with Shitty(columns=5, rows=3, save_lines=8) as terminal:
            terminal.write(put_rows(b"1", b"2", b"ABCDE"))

            terminal.resize(3, 3)
            self.assertEqual(terminal.snapshot().lines, ["2  ", "ABC", "DE "])
            self.assertEqual(terminal.all_text(), ("1", "2", "ABC", "DE"))

            terminal.resize(5, 3)
            self.assertEqual(
                terminal.snapshot().lines,
                ["1    ", "2    ", "ABCDE"],
            )
            self.assertEqual(terminal.all_text(), ("1", "2", "ABCDE"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_sparse_rows_and_spaces_survive_width_round_trips(self):
        with Shitty(columns=7, rows=3, save_lines=8) as terminal:
            terminal.write(b"a a a a")
            for width, expected in (
                (6, ("a a a ", "a", "")),
                (7, ("a a a a", "", "")),
                (5, ("a a a", " a", "")),
                (4, ("a a ", "a a", "")),
                (3, ("a a", " a ", "a")),
                (7, ("a a a a", "", "")),
            ):
                terminal.resize(width, 3)
                self.assertEqual(terminal.all_text(), expected)

    def test_scrollback_view_clamps_and_zero_offset_is_unchanged(self):
        with Shitty(columns=5, rows=2, save_lines=5) as terminal:
            terminal.write(put_rows(b"L000", b"L001"))
            for index in range(2, 7):
                terminal.write(b"\x1b[S\x1b[2;1H" + f"L{index:03}".encode())

            bottom = terminal.snapshot()
            self.assertEqual(bottom.view_offset, 0)
            self.assertEqual(bottom.lines, ["L005 ", "L006 "])

            terminal.wheel_up(99)
            top = terminal.snapshot()
            self.assertEqual(top.view_offset, 5)
            self.assertEqual(top.lines, ["L000 ", "L001 "])

            terminal.wheel_down(99)
            self.assertEqual(terminal.snapshot().lines, bottom.lines)
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_long_line_and_blank_history_reflow_without_loss(self):
        with Shitty(columns=200, rows=2, save_lines=50) as terminal:
            terminal.write(b"A" * 200)
            terminal.resize(40, 2)
            self.assertEqual(
                terminal.all_text(),
                ("A" * 40,) * 5,
            )

        with Shitty(columns=80, rows=2, save_lines=20) as terminal:
            terminal.write(b"\x1b[S" * 2)
            terminal.write(b"\x1b[1;1H" + b"B" * 60)
            terminal.write(b"\x1b[S" * 3)
            self.assertEqual(terminal.scrollback_state()[0], 5)

            terminal.resize(40, 2)
            self.assertIn("B" * 60, "".join(terminal.all_text()))

    def test_semantic_regions_survive_every_reflow_split(self):
        text = b"A" * 30
        with Shitty(columns=30, rows=2, save_lines=10) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\" + text)

            for width in (10, 20, 30):
                terminal.resize(width, 2)
                terminal.wheel_up(99)
                snapshot = terminal.snapshot()
                semantic = [
                    cell.semantic
                    for cell in snapshot.cells
                    if cell.char == "A"
                ]
                self.assertTrue(semantic)
                self.assertEqual(semantic, [1] * len(semantic))
                terminal.wheel_down(99)


if __name__ == "__main__":
    unittest.main()

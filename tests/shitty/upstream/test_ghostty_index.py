# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class GhosttyIndexTest(unittest.TestCase):
    def test_reverse_index_moves_and_scrolls_at_the_top(self):
        with Shitty(columns=2, rows=5) as terminal:
            terminal.write(b"A\r\nB\r\nC\x1bMD\r\n\r\n")
            self.assertEqual(
                terminal.snapshot().lines,
                ["A ", "BD", "C ", "  ", "  "],
            )

        with Shitty(columns=2, rows=5) as terminal:
            terminal.write(
                b"A\r\nB\r\n\r\n"
                b"\x1b[1;1H\x1bMD\r\n"
                b"\x1b[1;1H\x1bME"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["E ", "D ", "A ", "B ", "  "],
            )

    def test_reverse_index_obeys_vertical_region(self):
        cases = (
            (
                b"\x1b[2;5r\x1b[2;1H\x1bMX",
                ["A    ", "X    ", "B    ", "C    ", "D    "],
                (1, 2, 3, 4),
            ),
            (
                b"\x1b[2;3r\x1b[2;1H\x1bM",
                ["A    ", "     ", "B    ", "D    ", "E    "],
                (1, 2),
            ),
            (
                b"\x1b[2;3r\x1b[1;1H\x1bM",
                ["A    ", "B    ", "C    ", "D    ", "E    "],
                (),
            ),
        )
        for operation, expected, damage in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(put_rows(b"A", b"B", b"C", b"D", b"E"))
                terminal.write(operation)
                self.assertEqual(terminal.snapshot().lines, expected)
                self.assertEqual(terminal.last_update_rows(), damage)

    def test_reverse_index_at_screen_top_and_above_it(self):
        cases = (
            (
                b"\x1b[1;1H\x1bMX",
                ["X    ", "A    ", "B    ", "C    ", "     "],
                (0, 1, 2, 3, 4),
            ),
            (
                b"\x1b[2;1H\x1bMX",
                ["X    ", "B    ", "C    ", "     ", "     "],
                (0,),
            ),
        )
        for operation, expected, damage in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(put_rows(b"A", b"B", b"C"))
                terminal.write(operation)
                self.assertEqual(terminal.snapshot().lines, expected)
                self.assertEqual(terminal.last_update_rows(), damage)

    def test_reverse_index_obeys_horizontal_region(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"ABC", b"DEF", b"GHI"))
            terminal.write(
                b"\x1b[?69h\x1b[2;3s"
                b"\x1b[1;2H\x1bM"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["A    ", "DBC  ", "GEF  ", " HI  ", "     "],
            )
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2, 3, 4))

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"ABC", b"DEF", b"GHI"))
            terminal.write(
                b"\x1b[?69h\x1b[2;3s"
                b"\x1b[1;1H\x1bM"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["ABC  ", "DEF  ", "GHI  ", "     ", "     "],
            )
            self.assertEqual(terminal.last_update_rows(), ())

    def test_index_moves_or_scrolls_only_at_the_relevant_boundary(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1bD")
            self.assertEqual(terminal.last_update_rows(), ())
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))
            terminal.write(b"X")
            self.assertEqual(
                terminal.snapshot().lines,
                ["     ", "X    ", "     ", "     ", "     "],
            )

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1b[5;1HA\x1b[D")
            terminal.write(b"\x1bD")
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2, 3, 4))
            terminal.write(b"X")
            self.assertEqual(
                terminal.snapshot().lines,
                ["     ", "     ", "     ", "A    ", "X    "],
            )

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1b[1;2r\x1b[5;1HA")
            terminal.write(b"\x1bD")
            terminal.write(b"X")
            self.assertEqual(
                terminal.snapshot().lines,
                ["     ", "     ", "     ", "     ", "AX   "],
            )
            self.assertEqual(terminal.last_update_rows(), (4,))

    def test_index_moves_hyperlink_with_its_cell(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[5;1H"
                b"\x1b]8;;https://example.test\x1b\\"
                b"A"
                b"\x1b]8;;\x1b\\"
                b"\x1b[5;1H\x1bD"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[3:], ["A    ", "     "])
            self.assertNotEqual(snapshot.cell(0, 3).hyperlink, 0)
            self.assertEqual(
                terminal.hyperlink(0, 3),
                "https://example.test",
            )
            self.assertEqual(snapshot.cell(0, 4).hyperlink, 0)
            self.assertEqual(terminal.hyperlink(0, 4), "")

    def test_index_region_moves_and_releases_hyperlinks(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[2;3r\x1b[2;1H"
                b"\x1b]8;;https://example.test\x1b\\"
                b"A"
                b"\x1b]8;;\x1b\\"
                b"\x1bD\rB\x1bD\rC"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["     ", "B    ", "C    ", "     ", "     "],
            )
            for row in (1, 2):
                self.assertEqual(snapshot.cell(0, row).hyperlink, 0)
                self.assertEqual(terminal.hyperlink(0, row), "")

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[1;2r"
                b"A\x1bD\r"
                b"\x1b]8;;https://example.test\x1b\\"
                b"B"
                b"\x1b]8;;\x1b\\"
                b"\x1bD\rC"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["B    ", "C    "])
            self.assertEqual(
                terminal.hyperlink(0, 0),
                "https://example.test",
            )
            self.assertEqual(terminal.hyperlink(0, 1), "")

    def test_index_blank_row_uses_current_erase_colors(self):
        cases = (
            (
                b"\x1b[5;1HA\x1b[48;2;255;0;0m\x1bD",
                4,
                ["     ", "     ", "     ", "A    ", "     "],
            ),
            (
                b"\x1b[1;3r\x1b[4;1HB\x1b[3;1HA"
                b"\x1b[48;2;255;0;0m\x1bD",
                2,
                ["     ", "A    ", "     ", "B    ", "     "],
            ),
            (
                put_rows(b"1", b"2", b"3", b"4", b"5")
                + b"\x1b[2;4r\x1b[4;1H"
                b"\x1b[48;2;255;0;0m\x1bD",
                3,
                ["1    ", "3    ", "4    ", "     ", "5    "],
            ),
        )
        for operation, blank_row, expected in cases:
            with self.subTest(blank_row=blank_row), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(operation)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, expected)
                for column in range(snapshot.columns):
                    cell = snapshot.cell(column, blank_row)
                    self.assertEqual(cell.background, (255, 0, 0))
                    self.assertFalse(cell.bold)
                    self.assertFalse(cell.italic)
                    self.assertFalse(cell.underline)

    def test_index_top_region_creates_primary_history_only(self):
        with Shitty(columns=5, rows=5, save_lines=5) as terminal:
            terminal.write(
                put_rows(b"1", b"2", b"3", b"X")
                + b"\x1b[1;3r\x1b[3;1H\x1bDY\x1b[r"
            )
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(
                snapshot.lines,
                ["1    ", "2    ", "3    ", "Y    ", "X    "],
            )

        with Shitty(columns=5, rows=5, save_lines=5) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                + put_rows(b"1", b"2", b"3", b"4", b"5")
                + b"\x1b[1;4r\x1b[4;1H\x1bDX"
            )
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["2    ", "3    ", "4    ", "X    ", "5    "],
            )

    def test_index_obeys_both_margin_pairs(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(put_rows(b"AAAAAA", b"AAAAAA", b"AAAAAA"))
            terminal.write(
                b"\x1b[1;3r\x1b[?69h\x1b[1;3s"
                b"\x1b[3;1H\x1bD"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                [
                    "AAAAAA    ",
                    "AAAAAA    ",
                    "   AAA    ",
                    "          ",
                    "          ",
                ],
            )
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))

        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[1;3r\x1b[?69h\x1b[3;5s")
            terminal.write(b"\x1b[3;3HA\x1b[3;1H\x1bDX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 2).char, "A")
            self.assertEqual(snapshot.cell(0, 2).char, "X")
            self.assertEqual(terminal.last_update_rows(), (2,))


if __name__ == "__main__":
    unittest.main()

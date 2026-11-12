# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class GhosttyDeleteLinesTest(unittest.TestCase):
    def test_delete_line_shifts_rows_and_reports_exact_damage(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"ABC", b"DEF", b"GHI"))
            terminal.write(b"\x1b[2;2H\x1b[M")
            self.assertEqual(
                terminal.snapshot().lines,
                ["ABC  ", "GHI  ", "     ", "     ", "     "],
            )
            self.assertEqual(terminal.last_update_rows(), (1, 2, 3, 4))

    def test_delete_line_blank_rows_use_current_erase_colors(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(put_rows(b"ABC", b"DEF", b"GHI"))
            terminal.write(
                b"\x1b[2;2H"
                b"\x1b[1;3;4;38;2;1;2;3;48;2;255;0;0m"
                b"\x1b[M"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["ABC  ", "GHI  ", "     ", "     ", "     "],
            )
            for column in range(snapshot.columns):
                cell = snapshot.cell(column, 4)
                self.assertEqual(cell.foreground, (1, 2, 3))
                self.assertEqual(cell.background, (255, 0, 0))
                self.assertFalse(cell.bold)
                self.assertFalse(cell.italic)
                self.assertFalse(cell.underline)

    def test_delete_line_moves_dense_hyperlinks_without_aliasing(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(put_rows(b"0", b"1", b"2", b"4"))
            terminal.write(b"\x1b[4;1H")
            for index in range(10):
                terminal.write(
                    (
                        f"\x1b]8;;https://example.test/{index}\x1b\\"
                        f"{chr(ord('A') + index)}"
                        "\x1b]8;;\x1b\\"
                    ).encode()
                )
            terminal.write(b"\x1b[5;1H4")
            terminal.write(b"\x1b[1;1H\x1b[M")

            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["1         ", "2         ", "ABCDEFGHIJ", "4         ",
                 "          "],
            )
            identities = set()
            for column in range(10):
                cell = snapshot.cell(column, 2)
                self.assertNotEqual(cell.hyperlink, 0)
                identities.add(cell.hyperlink)
                self.assertEqual(
                    terminal.hyperlink(column, 2),
                    f"https://example.test/{column}",
                )
            self.assertEqual(len(identities), 10)

    def test_delete_line_obeys_vertical_region_and_clamps_count(self):
        cases = (
            (
                b"\x1b[1;3r\x1b[1;1H\x1b[M",
                ["B    ", "C    ", "     ", "D    ", "     "],
                (0, 1, 2),
            ),
            (
                b"\x1b[1;3r\x1b[1;1H\x1b[99M",
                ["     ", "     ", "     ", "D    ", "     "],
                (0, 1, 2),
            ),
            (
                b"\x1b[1;3r\x1b[4;1H\x1b[M",
                ["A    ", "B    ", "C    ", "D    ", "     "],
                (),
            ),
        )
        for operation, expected, damage in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(put_rows(b"A", b"B", b"C", b"D"))
                terminal.write(operation)
                self.assertEqual(terminal.snapshot().lines, expected)
                self.assertEqual(terminal.last_update_rows(), damage)

    def test_delete_line_resets_pending_wrap_and_row_wrap(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"ABCDE")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[M")
            self.assertFalse(terminal.cursor_pending_wrap())
            terminal.write(b"B")
            self.assertEqual(
                terminal.snapshot().lines,
                ["B    ", "     ", "     ", "     ", "     "],
            )

        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"1\r\nABCDEF")
            terminal.write(b"\x1b[1;2r\x1b[1;1H\x1b[MX")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["XBC", "   ", "DEF"])
            for row in range(snapshot.rows):
                self.assertFalse(snapshot.cell(2, row).wrapped)

    def test_delete_line_obeys_horizontal_region(self):
        cases = (
            (
                b"\x1b[2;2H\x1b[M",
                ["ABC123    ", "DHI756    ", "G   89    "],
            ),
            (
                b"\x1b[1;2H\x1b[M",
                ["AEF423    ", "DHI756    ", "G   89    "],
            ),
            (
                b"\x1b[2;2H\x1b[99M",
                ["ABC123    ", "D   56    ", "G   89    "],
            ),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=10,
                rows=3,
            ) as terminal:
                terminal.write(put_rows(b"ABC123", b"DEF456", b"GHI789"))
                terminal.write(
                    b"\x1b[?69h\x1b[2;4s" + operation
                )
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_delete_line_repairs_wide_cells_at_both_margin_edges(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                put_rows(
                    b"AAAAA",
                    "😀B😀".encode(),
                )
            )
            terminal.write(
                b"\x1b[?69h\x1b[2;4s"
                b"\x1b[1;2H\x1b[M"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["A B A", "     "])
            for column in range(snapshot.columns):
                cell = snapshot.cell(column, 0)
                self.assertFalse(cell.double_width)
                self.assertFalse(cell.double_width_continuation)

    def test_delete_line_repairs_wide_wrap_spacer(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write("AAAAABBBB😀CCC".encode())
            terminal.write(b"\x1b[1;1H\x1b[M")
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["BBBB ", "😀 CCC", "     "],
            )
            for row in range(snapshot.rows):
                self.assertFalse(snapshot.cell(4, row).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(
                snapshot.cell(1, 1).double_width_continuation
            )

    def test_delete_line_partial_wide_wrap_preserves_row_wrap(self):
        cases = (
            (
                b"\x1b[3;5s\x1b[1;3H\x1b[M",
                ["AABB ", "BBCCC", "😀    "],
                (True, True, False),
            ),
            (
                b"\x1b[1;4s\x1b[1;1H\x1b[M",
                ["BBBBA", "😀 CC ", "    C"],
                (True, True, False),
            ),
            (
                b"\x1b[3;4s\x1b[1;3H\x1b[M",
                ["AABBA", "BBCC ", "😀   C"],
                (True, True, False),
            ),
            (
                b"\x1b[2;4s\x1b[1;2H\x1b[M",
                ["ABBBA", "B CC ", "    C"],
                (True, True, False),
            ),
        )
        for operation, expected, wrapped in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write("AAAAABBBB😀CCC".encode())
                terminal.write(b"\x1b[?69h" + operation)
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines, expected)
                self.assertEqual(
                    tuple(
                        any(
                            snapshot.cell(column, row).wrapped
                            for column in range(snapshot.columns)
                        )
                        for row in range(3)
                    ),
                    wrapped,
                )


if __name__ == "__main__":
    unittest.main()

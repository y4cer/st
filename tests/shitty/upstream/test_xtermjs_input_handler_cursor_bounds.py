# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 81 through 100."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "horizontal position relative (HPR)",
    "vertical position absolute (VPA)",
    "vertical position relative (VPR)",
    "addressable-range clamp: CUF",
    "addressable-range clamp: CUB",
    "addressable-range clamp: CUD",
    "addressable-range clamp: CUU",
    "addressable-range clamp: CNL",
    "addressable-range clamp: CPL",
    "addressable-range clamp: CHA",
    "addressable-range clamp: CUP",
    "addressable-range clamp: HPA",
    "addressable-range clamp: HPR",
    "addressable-range clamp: VPA",
    "addressable-range clamp: VPR",
    "addressable-range clamp: DCH",
    "DCH deletes the final cell after pending wrap",
    "addressable-range clamp: ECH",
    "ECH erases the final cell after pending wrap",
    "addressable-range clamp: ICH",
)


def cursor(terminal):
    snapshot = terminal.snapshot()
    return snapshot.cursor_x, snapshot.cursor_y


class XtermJsInputHandlerCursorBoundsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_horizontal_position_relative_defaults_clamps_and_preserves_row(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[a", (1, 0)),
                (b"\x1b[1a", (2, 0)),
                (b"\x1b[4a", (6, 0)),
                (b"\x1b[100a", (9, 0)),
                (b"\x1b[5;9H\x1b[a", (9, 4)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_vertical_position_absolute_defaults_clamps_and_preserves_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[d", (0, 0)),
                (b"\x1b[1d", (0, 0)),
                (b"\x1b[2d", (0, 1)),
                (b"\x1b[5d", (0, 4)),
                (b"\x1b[100d", (0, 9)),
                (b"\x1b[5;9H\x1b[d", (8, 0)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_vertical_position_relative_defaults_clamps_and_preserves_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            for sequence, expected in (
                (b"\x1b[e", (0, 1)),
                (b"\x1b[1e", (0, 2)),
                (b"\x1b[4e", (0, 6)),
                (b"\x1b[100e", (0, 9)),
                (b"\x1b[5;9H\x1b[e", (8, 5)),
            ):
                terminal.write(sequence)
                self.assertEqual(cursor(terminal), expected)

    def test_cuf_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[C")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[C")
            self.assertEqual(cursor(terminal), (1, 0))

    def test_cub_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[D")
            self.assertEqual(cursor(terminal), (8, 9))
            terminal.write(b"\x1b[H\x1b[D")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_cud_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[B")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[B")
            self.assertEqual(cursor(terminal), (0, 1))

    def test_cuu_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[A")
            self.assertEqual(cursor(terminal), (9, 8))
            terminal.write(b"\x1b[H\x1b[A")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_cnl_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[E")
            self.assertEqual(cursor(terminal), (0, 9))
            terminal.write(b"\x1b[H\x1b[E")
            self.assertEqual(cursor(terminal), (0, 1))

    def test_cpl_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[F")
            self.assertEqual(cursor(terminal), (0, 8))
            terminal.write(b"\x1b[H\x1b[F")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_cha_sets_column_and_preserves_each_boundary_row(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[5G")
            self.assertEqual(cursor(terminal), (4, 9))
            terminal.write(b"\x1b[H\x1b[5G")
            self.assertEqual(cursor(terminal), (4, 0))

    def test_cup_sets_the_same_address_from_each_boundary(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[5;5H")
            self.assertEqual(cursor(terminal), (4, 4))
            terminal.write(b"\x1b[H\x1b[5;5H")
            self.assertEqual(cursor(terminal), (4, 4))

    def test_hpa_sets_column_and_preserves_each_boundary_row(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[5`")
            self.assertEqual(cursor(terminal), (4, 9))
            terminal.write(b"\x1b[H\x1b[5`")
            self.assertEqual(cursor(terminal), (4, 0))

    def test_hpr_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[a")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[a")
            self.assertEqual(cursor(terminal), (1, 0))

    def test_vpa_sets_row_and_preserves_each_boundary_column(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[5d")
            self.assertEqual(cursor(terminal), (9, 4))
            terminal.write(b"\x1b[H\x1b[5d")
            self.assertEqual(cursor(terminal), (0, 4))

    def test_vpr_stays_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[e")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[e")
            self.assertEqual(cursor(terminal), (0, 1))

    def test_dch_keeps_cursor_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[P")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[P")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_dch_deletes_the_final_cell_after_pending_wrap(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"0123456789\x1b[P")
            self.assertEqual(terminal.snapshot().lines[0], "012345678 ")

    def test_ech_keeps_cursor_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[X")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[X")
            self.assertEqual(cursor(terminal), (0, 0))

    def test_ech_erases_the_final_cell_after_pending_wrap(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"0123456789\x1b[X")
            self.assertEqual(terminal.snapshot().lines[0], "012345678 ")

    def test_ich_keeps_cursor_inside_both_public_page_boundaries(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"\x1b[10;10H\x1b[@")
            self.assertEqual(cursor(terminal), (9, 9))
            terminal.write(b"\x1b[H\x1b[@")
            self.assertEqual(cursor(terminal), (0, 0))


if __name__ == "__main__":
    unittest.main()

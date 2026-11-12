# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList resize (no reflow) less rows trims blank lines cursor in blank line",
    "PageList resize (no reflow) less rows trims blank lines erases pages",
    "PageList resize (no reflow) more rows extends blank lines",
    "PageList resize (no reflow) more rows contains viewport",
    "PageList resize (no reflow) less cols",
    "PageList resize (no reflow) less cols pin in trimmed cols",
    "PageList resize (no reflow) less cols clears graphemes",
    "PageList resize (no reflow) more cols",
    "PageList resize (no reflow) more cols with spacer head",
    "PageList resize (no reflow) grow cols fast path with spacer head",
    "PageList resize (no reflow) more cols forces less rows per page",
    "PageList resize (no reflow) less cols then more cols",
    "PageList resize (no reflow) less rows and cols",
    "PageList resize less rows and cols cursor at bottom",
    "PageList resize less rows and cols cursor near top pushed to scrollback",
    "PageList resize (no reflow) more rows and less cols",
    "PageList resize more rows and cols doesn't fit in single std page",
    "PageList resize (no reflow) empty screen",
    "PageList resize (no reflow) more cols forces smaller cap",
    "PageList resize (no reflow) more rows adds blank rows if cursor at bottom",
)


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def nonempty_visible_lines(terminal):
    lines = list(visible_lines(terminal))
    while lines and not lines[-1]:
        lines.pop()
    return tuple(lines)


class GhosttyPageListResizeNoReflowTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_blank_tail_cursor_clamps_to_the_last_surviving_blank_row(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[?1049hA"
                b"\x1b[2;1H\x1b[41m\x1b[2K"
                b"\x1b[3;1H\x1b[2K"
                b"\x1b[4;1H\x1b[2K"
                b"\x1b[5;1H\x1b[2K\x1b[0m"
                b"\x1b[4;1H"
            )

            terminal.resize(10, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("A", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_shrinking_a_large_blank_screen_discards_unused_backing_rows(self):
        with Shitty(columns=100, rows=5, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049hA")
            terminal.resize(100, 300)

            terminal.resize(100, 5)

            self.assertEqual(visible_lines(terminal), ("A", "", "", "", ""))
            self.assertEqual(terminal.scrollback_state(), (0, 5, 5, 0))

    def test_height_growth_extends_background_only_tail_with_blank_rows(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[?1049hA"
                b"\x1b[2;1H\x1b[41m\x1b[2K"
                b"\x1b[3;1H\x1b[2K\x1b[0m\x1b[1;2H"
            )

            terminal.resize(10, 7)

            self.assertEqual(visible_lines(terminal), ("A", "", "", "", "", "", ""))
            self.assertEqual(terminal.snapshot().cursor_y, 0)

    def test_height_growth_contains_a_previously_parked_viewport(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(numbered_lines(0, 5))
            terminal.wheel_up(1)
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.resize(5, 7)

            self.assertEqual(nonempty_visible_lines(terminal), tuple(f"{value:03}" for value in range(6)))
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_no_reflow_width_shrink_truncates_each_hard_row(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(b"ABCDEFGHIJ", b"KLMNOPQRST", b"UVWXYZ1234"))

            terminal.resize(5, 3)

            self.assertEqual(visible_lines(terminal), ("ABCDE", "KLMNO", "UVWXY"))

    def test_width_shrink_clamps_the_cursor_out_of_trimmed_columns(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h\x1b[3;9H")

            terminal.resize(5, 3)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 2))

    def test_width_shrink_releases_a_grapheme_in_trimmed_columns(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h\x1b[1;9H" + "a\N{COMBINING ACUTE ACCENT}".encode())

            terminal.resize(5, 3)
            snapshot = terminal.model_snapshot()

            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertTrue(all(ord("a") not in cell.grapheme for cell in snapshot.cells))

    def test_no_reflow_width_growth_preserves_hard_row_positions(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(b"ABCDE", b"FGHIJ", b"KLMNO"))

            terminal.resize(10, 3)

            self.assertEqual(visible_lines(terminal), ("ABCDE", "FGHIJ", "KLMNO"))

    def test_width_growth_repairs_a_wide_spacer_at_the_old_right_edge(self):
        with Shitty(columns=2, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + "x😀".encode())

            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertFalse(snapshot.cell(1, 0).double_width)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)
            self.assertTrue(snapshot.cell(0, 1).double_width)

    def test_shrink_grow_fast_path_leaves_no_stale_wide_spacer(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h")
            terminal.resize(5, 3)
            terminal.write("xxxx😀".encode())

            terminal.resize(10, 3)
            snapshot = terminal.snapshot()

            self.assertFalse(snapshot.cell(4, 0).double_width)
            self.assertFalse(snapshot.cell(4, 0).double_width_continuation)
            self.assertTrue(snapshot.cell(0, 1).double_width)

    def test_very_wide_no_reflow_resize_preserves_every_tall_row(self):
        with Shitty(columns=5, rows=150, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + numbered_lines(0, 149))

            terminal.resize(600, 150)

            self.assertEqual(nonempty_visible_lines(terminal), tuple(f"{value:03}" for value in range(150)))

    def test_no_reflow_shrink_then_growth_does_not_restore_truncated_cells(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049hABCDE")
            terminal.resize(2, 3)

            terminal.resize(5, 3)

            self.assertEqual(visible_lines(terminal), ("AB", "", ""))

    def test_combined_no_reflow_shrink_updates_both_dimensions(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + numbered_lines(0, 9))

            terminal.resize(5, 7)
            snapshot = terminal.snapshot()

            # No blank tail to trim, so the excess comes off the top and
            # the cursor keeps its bottom content - exactly the rows the
            # ghostty pagelist keeps in its active area (upstream pushes
            # them to scrollback; the alternate screen discards them).
            self.assertEqual((snapshot.columns, snapshot.rows), (5, 7))
            self.assertEqual(visible_lines(terminal), tuple(f"{value:03}" for value in range(3, 10)))

    def test_combined_reflow_shrink_keeps_a_bottom_cursor_on_bottom_content(self):
        with Shitty(columns=80, rows=24, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 23))

            terminal.resize(79, 20)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 19))
            self.assertEqual(snapshot.lines[19].rstrip(), "023")

    def test_combined_shrink_keeps_a_near_top_anchor_in_scrollback(self):
        with Shitty(columns=80, rows=24, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 23))
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)

            terminal.resize(79, 20)
            terminal.wheel_up(100)

            self.assertEqual(visible_lines(terminal)[0], "000")
            self.assertEqual(terminal.select_finish(), b"000")

    def test_more_rows_and_fewer_columns_preserve_no_reflow_hard_lines(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                + put_rows(*[f"{value}abcdefgh".encode() for value in range(10)])
            )

            terminal.resize(5, 20)

            self.assertEqual(nonempty_visible_lines(terminal), tuple(f"{value}abcd" for value in range(10)))

    def test_large_two_axis_growth_preserves_geometry_and_existing_content(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(b"origin")

            terminal.resize(600, 600)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (600, 600))
            self.assertEqual(snapshot.lines[0][:6], "origin")
            self.assertEqual(len(snapshot.cells), 360_000)

    def test_no_reflow_empty_screen_resize_stays_entirely_blank(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h")

            terminal.resize(10, 10)

            self.assertEqual(visible_lines(terminal), ("",) * 10)
            self.assertEqual(terminal.scrollback_state(), (0, 10, 10, 0))

    def test_wider_rows_with_smaller_internal_capacity_keep_all_row_heads(self):
        with Shitty(columns=100, rows=150, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(*([b"A"] * 150)))

            terminal.resize(500, 150)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (500, 150))
            self.assertTrue(all(snapshot.cell(0, row).char == "A" for row in range(150)))

    def test_height_growth_at_a_nonfinal_cursor_adds_blank_rows_after_content(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(numbered_lines(0, 4))
            terminal.write(b"\x1b[2;1H")

            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), tuple(f"{value:03}" for value in range(5)))
            self.assertEqual(snapshot.lines[snapshot.cursor_y].rstrip(), "003")
            self.assertEqual(visible_lines(terminal)[5:], ("",) * 5)


if __name__ == "__main__":
    unittest.main()

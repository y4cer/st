# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: resize more cols with reflow that fits full width",
    "Screen: resize more cols with reflow that ends in newline",
    "Screen: resize more cols with reflow that forces more wrapping",
    "Screen: resize more cols with reflow that unwraps multiple times",
    "Screen: resize more cols with populated scrollback",
    "Screen: resize more cols bounded scrollback keeps viewport valid",
    "Screen: resize more cols with reflow",
    "Screen: resize errors preserve state",
    "Screen: resize cursor references when node survives",
    "Screen: resize cursor references when node is replaced",
    "Screen: resize more rows and cols with wrapping",
    "Screen: resize less rows no scrollback",
    "Screen: resize less rows moving cursor",
    "Screen: resize less rows with empty scrollback",
    "Screen: resize less rows with populated scrollback",
    "Screen: resize less rows with full scrollback",
    "Screen: resize less cols no reflow",
    "Screen: resize less cols with reflow but row space",
    "Screen: resize less cols with reflow with trimmed rows",
    "Screen: resize less cols with reflow with trimmed rows and scrollback",
)


def osc8(uri=b"", params=b""):
    return b"\x1b]8;" + params + b";" + uri + b"\x1b\\"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def nonempty_visible_lines(terminal):
    lines = list(visible_lines(terminal))
    while lines and not lines[-1]:
        lines.pop()
    return tuple(lines)


class GhosttyScreenResizeReflowTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_growth_reflows_a_full_width_soft_wrap(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABCD2EFGH\r\n3IJKL\x1b[2;1H")
            terminal.resize(10, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1ABCD2EFGH", "3IJKL", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))

    def test_growth_reflows_wrapped_text_ending_at_a_hard_break(self):
        with Shitty(columns=6, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABCD2EFGH\r\n3IJKL\x1b[3;1H")
            terminal.resize(10, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1ABCD2EFGH", "3IJKL", ""))
            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "3")

    def test_growth_can_rewrap_to_a_different_number_of_rows(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABCD2EFGH\r\n3IJKL\x1b[2;1H")
            terminal.resize(7, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1ABCD2E", "FGH", "3IJKL"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))

    def test_growth_unwraps_multiple_rows_and_tracks_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABCD2EFGH3IJKL\x1b[3;1H")
            terminal.resize(15, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("1ABCD2EFGH3IJKL",))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (10, 0))

    def test_growth_reflows_active_text_with_populated_scrollback(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD5EFGH"
                b"\x1b[3;1H"
            )
            terminal.resize(10, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.all_text(),
                ("1ABCD", "2EFGH", "3IJKL", "4ABCD5EFGH"),
            )
            self.assertEqual(
                visible_lines(terminal),
                ("2EFGH", "3IJKL", "4ABCD5EFGH"),
            )
            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "5")

    def test_bounded_scrollback_view_remains_valid_after_mass_unwrap(self):
        with Shitty(columns=2, rows=10, save_lines=30) as terminal:
            terminal.write(b"\r\n".join(b"AAAA" for _ in range(20)))
            terminal.wheel_up(2)
            before = terminal.scrollback_state()
            terminal.resize(4, 10)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (4, 10))
            self.assertEqual(len(snapshot.cells), 40)
            self.assertLess(terminal.scrollback_state()[0], before[0])
            self.assertLessEqual(snapshot.view_offset, terminal.scrollback_state()[0])
            self.assertTrue(all(line.rstrip() == "AAAA" for line in snapshot.lines))

    def test_growth_reflows_multiple_hard_lines_and_tracks_cursor(self):
        with Shitty(columns=2, rows=3, save_lines=5) as terminal:
            terminal.write(b"1ABC\r\n2DEF\r\n3ABC\r\n4DEF\x1b[3;1H")
            terminal.resize(7, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.all_text(),
                ("1ABC", "2DEF", "3ABC", "4DEF"),
            )
            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "E")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))

    def test_rejected_resize_preserves_rich_terminal_state(self):
        uri = b"https://example.test/resize"
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            terminal.write(
                b"\x1b]133;P\x1b\\> "
                b"\x1b]133;B\x1b\\"
                b"\x1b[1m" + osc8(uri, b"id=resize") + b"echo"
                b"\x1b7"
            )
            before_model = terminal.model_digest()
            before_frame = terminal.model_snapshot()

            with self.assertRaises(RuntimeError):
                terminal.resize(0, 4)

            self.assertEqual(terminal.model_digest(), before_model)
            self.assertEqual(terminal.model_snapshot(), before_frame)
            terminal.write(b"X")
            cell = terminal.snapshot().cell(6, 0)
            self.assertTrue(cell.bold)
            self.assertEqual(terminal.hyperlink(6, 0), uri.decode())

    def test_copy_resize_preserves_current_style_and_hyperlink(self):
        uri = b"https://example.test/copy-resize"
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(b"\x1b[1m" + osc8(uri) + b"abc")
            terminal.resize(5, 4)
            terminal.write(b"X")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "abcX")
            self.assertTrue(snapshot.cell(3, 0).bold)
            self.assertEqual(terminal.hyperlink(3, 0), uri.decode())

    def test_reflow_resize_preserves_current_style_and_hyperlink(self):
        uri = b"https://example.test/reflow-resize"
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(b"\x1b[1m" + osc8(uri) + b"abc")
            terminal.resize(10, 3)
            terminal.write(b"X")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "abcX")
            self.assertTrue(snapshot.cell(3, 0).bold)
            self.assertEqual(terminal.hyperlink(3, 0), uri.decode())

    # Ghostty keeps a pending-wrap cursor on the last printed cell after the
    # line grows. The other reflowing implementations resolve it to the
    # insertion position after that cell.
    @unittest.expectedFailure
    def test_growth_in_both_dimensions_undoes_soft_wraps(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"1A2B\r\n3C4D")
            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("1A2B", "3C4D"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))

    def test_growth_resolves_pending_wrap_to_the_next_insertion_column(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"1A2B\r\n3C4D")
            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("1A2B", "3C4D"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))

    # Cursor-relative and bottom-gravity implementations split evenly for a
    # height shrink with the cursor above the discarded rows. ECMA-48 has no
    # window-resize or scrollback rule.
    @unittest.expectedFailure
    def test_height_shrink_without_scrollback_keeps_bottom_content(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.write(b"\x1b[1;1H")
            terminal.resize(5, 1)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("3IJKL",))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_height_shrink_without_scrollback_keeps_cursor_content(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.write(b"\x1b[1;1H")
            terminal.resize(5, 1)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1ABCD",))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_height_shrink_moves_bottom_cursor_with_its_content(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.write(b"\x1b[3;2H")
            terminal.resize(5, 1)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("3IJKL",))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "I")

    def test_height_shrink_with_empty_scrollback_retains_clipped_rows(self):
        with Shitty(columns=5, rows=3, save_lines=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.resize(5, 1)

            self.assertEqual(visible_lines(terminal), ("3IJKL",))
            self.assertEqual(terminal.all_text(), ("1ABCD", "2EFGH", "3IJKL"))

    def test_height_shrink_with_history_retains_all_rows(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.resize(5, 1)

            self.assertEqual(visible_lines(terminal), ("5EFGH",))
            self.assertEqual(
                terminal.all_text(),
                ("1ABCD", "2EFGH", "3IJKL", "4ABCD", "5EFGH"),
            )

    def test_height_shrink_at_capacity_keeps_cursor_bottom_anchored(self):
        with Shitty(columns=5, rows=3, save_lines=4) as terminal:
            terminal.write(
                b"00000\r\n1ABCD\r\n2EFGH\r\n"
                b"3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.resize(5, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("4ABCD", "5EFGH"))
            self.assertEqual(
                terminal.all_text(),
                ("00000", "1ABCD", "2EFGH", "3IJKL", "4ABCD", "5EFGH"),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))

    def test_width_shrink_keeps_short_hard_rows_and_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1AB", b"2EF", b"3IJ"))
            terminal.write(b"\x1b[1;1H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1AB", "2EF", "3IJ"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_width_shrink_reflows_into_available_rows(self):
        with Shitty(columns=5, rows=3, save_lines=1) as terminal:
            terminal.write(b"1ABCD\x1b[1;5H")
            terminal.resize(3, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1AB", "CD", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "D")

    def test_width_shrink_without_history_keeps_newest_physical_rows(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"3IJKL", b"4ABCD", b"5EFGH"))
            terminal.resize(3, 3)

            self.assertEqual(visible_lines(terminal), ("CD", "5EF", "GH"))
            self.assertEqual(terminal.all_text(), ("CD", "5EF", "GH"))

    def test_width_shrink_with_history_retains_all_reflowed_rows(self):
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(put_rows(b"3IJKL", b"4ABCD", b"5EFGH"))
            terminal.resize(3, 3)

            self.assertEqual(visible_lines(terminal), ("CD", "5EF", "GH"))
            self.assertEqual(
                terminal.all_text(),
                ("3IJ", "KL", "4AB", "CD", "5EF", "GH"),
            )

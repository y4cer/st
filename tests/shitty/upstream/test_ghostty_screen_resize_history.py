# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: clear above cursor",
    "Screen: clear above cursor with history",
    "Screen: resize (no reflow) more rows",
    "Screen: resize (no reflow) less rows",
    "Screen: resize (no reflow) less rows trims blank lines",
    "Screen: resize (no reflow) more rows trims blank lines",
    "Screen: resize (no reflow) more cols",
    "Screen: resize (no reflow) less cols",
    "Screen: resize (no reflow) more rows with scrollback cursor end",
    "Screen: resize (no reflow) less rows with scrollback",
    "Screen: resize (no reflow) less rows with empty trailing",
    "Screen: resize (no reflow) more rows with soft wrapping",
    "Screen: resize more rows no scrollback",
    "Screen: resize more rows with empty scrollback",
    "Screen: resize more rows with populated scrollback",
    "Screen: resize more cols no reflow",
    "Screen: resize more cols perfect split",
    "Screen: resize (no reflow) more cols with scrollback scrolled up",
    "Screen: resize (no reflow) less cols with scrollback scrolled up",
    "Screen: resize more cols no reflow preserves semantic prompt",
)


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def nonempty_visible_lines(terminal):
    lines = list(visible_lines(terminal))
    while lines and not lines[-1]:
        lines.pop()
    return tuple(lines)


def write_numbered_lines(terminal, last):
    terminal.write(b"\r\n".join(str(value).encode() for value in range(1, last + 1)))


class GhosttyScreenResizeHistoryTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_clear_rows_above_cursor_preserves_current_row_and_cursor(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(b"4ABCD", b"5EFGH", b"6IJKL"))
            terminal.write(b"\x1b7\x1b[1;1H\x1b[2K\x1b[2;1H\x1b[2K\x1b8")
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("", "", "6IJKL"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 2))

    def test_clear_rows_above_cursor_does_not_touch_history(self):
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n"
                b"4ABCD\r\n5EFGH\r\n6IJKL"
            )
            terminal.write(b"\x1b7\x1b[1;1H\x1b[2K\x1b[2;1H\x1b[2K\x1b8")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("", "", "6IJKL"))
            self.assertEqual(
                terminal.all_text(),
                ("1ABCD", "2EFGH", "3IJKL", "", "", "6IJKL"),
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 2))

    def test_no_reflow_height_growth_preserves_hard_rows(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.resize(10, 10)

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL"),
            )

    def test_no_reflow_height_shrink_keeps_rows_nearest_cursor(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.resize(10, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2EFGH", "3IJKL"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 1))

    def test_no_reflow_shrink_trims_background_only_trailing_rows(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[?1049h1ABCD"
                b"\x1b[2;1H\x1b[41m\x1b[2K"
                b"\x1b[3;1H\x1b[2K\x1b[0m\x1b[1;6H"
            )
            before = terminal.snapshot()
            terminal.resize(6, 2)
            after = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("1ABCD",))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_no_reflow_growth_keeps_background_only_rows_empty(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"1ABCD"
                b"\x1b[2;1H\x1b[41m\x1b[2K"
                b"\x1b[3;1H\x1b[2K\x1b[0m\x1b[1;6H"
            )
            before = terminal.snapshot()
            terminal.resize(10, 7)
            after = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("1ABCD",))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_no_reflow_width_growth_preserves_hard_rows(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.resize(20, 3)

            self.assertEqual(
                visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL"),
            )

    def test_no_reflow_width_shrink_truncates_hard_rows(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.resize(4, 3)

            self.assertEqual(visible_lines(terminal), ("1ABC", "2EFG", "3IJK"))

    def test_no_reflow_height_growth_recovers_history_at_cursor_end(self):
        with Shitty(columns=7, rows=3, save_lines=2) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.resize(7, 10)

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL", "4ABCD", "5EFGH"),
            )

    def test_no_reflow_height_shrink_moves_rows_to_history(self):
        with Shitty(columns=7, rows=3, save_lines=2) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.resize(7, 2)

            self.assertEqual(visible_lines(terminal), ("4ABCD", "5EFGH"))

    def test_no_reflow_shrink_ignores_empty_trailing_storage(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            write_numbered_lines(terminal, 8)
            terminal.write(b"\x1b[2J\x1b[H")
            terminal.write(b"A\r\nB")
            before = terminal.snapshot()
            terminal.resize(5, 2)
            after = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("A", "B"))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_no_reflow_height_growth_preserves_soft_wrap_flags(self):
        with Shitty(columns=2, rows=3, save_lines=3) as terminal:
            terminal.write(b"1A2B\r\n3C4E\r\n5F6G")
            terminal.resize(2, 10)
            snapshot = terminal.model_snapshot()

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1A", "2B", "3C", "4E", "5F", "6G"),
            )
            self.assertEqual(
                tuple(snapshot.cell(1, row).wrapped for row in range(6)),
                (True, False, True, False, True, False),
            )

    def test_height_growth_without_scrollback_does_not_move_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            before = terminal.snapshot()
            terminal.resize(5, 10)
            after = terminal.snapshot()

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL"),
            )
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_height_growth_with_empty_scrollback_does_not_move_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            before = terminal.snapshot()
            terminal.resize(5, 10)
            after = terminal.snapshot()

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL"),
            )
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    # There is no consensus for history gravity when the cursor is not at the
    # bottom. Ghostty, Contour, iTerm2 and default Kitty keep history hidden;
    # Alacritty, default xterm, VTE and Foot pull it into the enlarged page.
    # ECMA-48 specifies neither host-side resizing nor scrollback.
    @unittest.expectedFailure
    def test_height_growth_with_history_keeps_cursor_on_its_line(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.write(b"\x1b[2;1H")
            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "4")
            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("3IJKL", "4ABCD", "5EFGH"),
            )

    def test_height_growth_with_history_pulls_retained_rows_into_view(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH"
            )
            terminal.write(b"\x1b[2;1H")
            terminal.resize(5, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(snapshot.cursor_x, snapshot.cursor_y).char, "4")
            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD", "2EFGH", "3IJKL", "4ABCD", "5EFGH"),
            )

    def test_width_growth_keeps_hard_rows_and_cursor(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[?1049h" + put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            before = terminal.snapshot()
            terminal.resize(10, 3)
            after = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_width_growth_joins_a_perfect_soft_wrap_split(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABCD2EFGH3IJKL")
            terminal.resize(10, 3)

            self.assertEqual(
                nonempty_visible_lines(terminal),
                ("1ABCD2EFGH", "3IJKL"),
            )

    def test_scrolled_view_survives_width_growth(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            write_numbered_lines(terminal, 8)
            terminal.wheel_up(4)
            before = terminal.snapshot()
            terminal.resize(8, 3)
            after = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2", "3", "4"))
            self.assertEqual(terminal.all_text(), tuple(map(str, range(1, 9))))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_scrolled_view_survives_width_shrink(self):
        with Shitty(columns=5, rows=3, save_lines=5) as terminal:
            write_numbered_lines(terminal, 8)
            terminal.wheel_up(4)
            before = terminal.snapshot()
            terminal.resize(4, 3)
            after = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2", "3", "4"))
            self.assertEqual(terminal.all_text(), tuple(map(str, range(1, 9))))
            self.assertEqual(
                (after.cursor_x, after.cursor_y),
                (before.cursor_x, before.cursor_y),
            )

    def test_no_reflow_width_growth_preserves_semantic_prompt_row(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(
                osc133(b"C") + b"1ABCD\r\n"
                + osc133(b"P") + b"2EFGH"
                + osc133(b"C") + b"\r\n3IJKL"
            )
            terminal.resize(10, 3)

            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(3)),
                (0, 1, 0),
            )

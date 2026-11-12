# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: scrollback doesn't move viewport if not at bottom",
    "Screen: scrolling moves selection",
    "Screen: cursorScrollRegionUp simple",
    "Screen: cursorScrollRegionUp renews page generation",
    "Screen: cursorScrollRegionUp moves selection",
    "Screen: cursorScrollRegionUp region spans pages",
    "Screen: cursorScrollRegionUp region spans pages with background SGR",
    "Screen: cursorScrollRegionUp with styled erased row",
    "Screen: scrolling moves viewport",
    "Screen: scrolling when viewport is pruned",
    "Screen: scroll and clear full screen",
    "Screen: scroll and clear partial screen",
    "Screen: scroll and clear empty screen",
    "Screen: scroll and clear ignore blank lines",
    "Screen: scroll above same page",
    "Screen: scroll above same page but cursor on previous page",
    "Screen: scroll above same page but cursor on previous page last row",
    "Screen: scroll above creates new page",
    "Screen: scroll above with cursor on non-final row",
    "Screen: scroll above no scrollback bottom of page",
)


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def feed_numbered_lines(terminal, first, last):
    terminal.write(b"\r\n".join(str(value).encode() for value in range(first, last + 1)))


def prepare_rotated_grid(terminal, history_rows, *rows):
    if history_rows:
        terminal.write((b"history\r\n" * history_rows) + b"tail")
        terminal.write(b"\x1b[2J")
    terminal.write(put_rows(*rows))


def scroll_above(terminal, bottom=2):
    terminal.write(f"\x1b[1;{bottom}r\x1b[{bottom};1H\n\x1b[r".encode())


class GhosttyScreenScrollRegionHistoryTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_output_does_not_move_a_viewport_parked_in_history(self):
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            feed_numbered_lines(terminal, 1, 5)
            terminal.wheel_up()
            before = terminal.snapshot()

            terminal.write(b"\r\n6\r\n7")
            after = terminal.snapshot()

            self.assertEqual(after.lines, before.lines)
            self.assertGreater(after.view_offset, before.view_offset)

    def test_full_screen_scroll_moves_and_eventually_drops_selection(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 1)
            terminal.select_update(5, 1)

            terminal.write(b"\x1b[3;1H\n")
            self.assertEqual(terminal.snapshot().selection[1::2], (0, 0))
            self.assertEqual(terminal.select_finish(), b"2EFGH")

            terminal.write(b"\x1b[3;1H\n")
            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))

    def test_scroll_region_up_leaves_cursor_on_new_blank_row(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL", b"4MNOP", b"5QRST"))
            terminal.write(b"\x1b[1;3r\x1b[3;2H\n")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2EFGH", "3IJKL", "", "4MNOP", "5QRST"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))

    def test_repeated_region_scroll_renews_the_erased_storage(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL", b"4MNOP", b"5QRST"))
            terminal.write(b"\x1b[1;3r\x1b[3;1H\nX\x1b[3;1H\nY\x1b[r")

            self.assertEqual(visible_lines(terminal), ("3IJKL", "X", "Y", "4MNOP", "5QRST"))

    def test_region_scroll_moves_selection_with_the_selected_row(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL", b"4MNOP", b"5QRST"))
            terminal.select_start(0, 1)
            terminal.select_update(5, 1)
            terminal.write(b"\x1b[1;3r\x1b[3;1H\n\x1b[r")

            self.assertEqual(terminal.snapshot().selection[1::2], (0, 0))
            self.assertEqual(terminal.select_finish(), b"2EFGH")
            self.assertEqual(visible_lines(terminal), ("2EFGH", "3IJKL", "", "4MNOP", "5QRST"))

    def test_region_scroll_after_large_history_preserves_cursor_style(self):
        with Shitty(columns=10, rows=5, save_lines=160) as terminal:
            prepare_rotated_grid(terminal, 80, b"1A", b"2B", b"3C", b"4D", b"5E")
            terminal.write(b"\x1b[2;4r\x1b[4;1H\x1b[1m\nX\x1b[r")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1A", "3C", "4D", "X", "5E"))
            self.assertTrue(snapshot.cell(0, 3).bold)

    def test_region_scroll_uses_current_background_for_the_blank_row(self):
        with Shitty(columns=10, rows=5, save_lines=160) as terminal:
            prepare_rotated_grid(terminal, 81, b"1A", b"2B", b"3C", b"4D", b"5E")
            terminal.write(b"\x1b[2;4r\x1b[4;1H\x1b[48;2;155;0;0m\n\x1b[r")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("1A", "3C", "4D", "", "5E"))
            for column in range(snapshot.columns):
                self.assertEqual(snapshot.cell(column, 3).background, (155, 0, 0))

    def test_region_scroll_releases_style_from_the_erased_row(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[1;1H\x1b[1m1ABCD\x1b[0m"
                b"\x1b[2;1H2EFGH\x1b[3;1H3IJKL"
            )
            terminal.write(b"\x1b[1;3r\x1b[3;1H\n\x1b[r")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2EFGH", "3IJKL", ""))
            self.assertFalse(snapshot.cell(0, 0).bold)
            self.assertFalse(terminal.pen_state().bold)

    def test_scrolling_back_two_rows_selects_the_expected_history_window(self):
        with Shitty(columns=10, rows=3, save_lines=6) as terminal:
            feed_numbered_lines(terminal, 1, 6)
            terminal.wheel_up(2)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2", "3", "4"))
            self.assertEqual(snapshot.view_offset, 2)

    def test_pruning_a_parked_viewport_returns_it_to_retained_content(self):
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            feed_numbered_lines(terminal, 1, 6)
            terminal.wheel_up(2)
            feed_numbered_lines(terminal, 7, 40)
            snapshot = terminal.snapshot()

            retained = terminal.all_text()
            history_rows = terminal.scrollback_state()[0]

            self.assertEqual(snapshot.view_offset, history_rows)
            self.assertEqual(visible_lines(terminal), retained[:3])

    @unittest.expectedFailure
    def test_scroll_complete_moves_a_full_screen_into_history(self):
        with Shitty(columns=10, rows=3, save_lines=6) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.write(b"\x1b[22J")

            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual(terminal.all_text(), ("1ABCD", "2EFGH", "3IJKL"))

    @unittest.expectedFailure
    def test_scroll_complete_moves_a_partial_screen_into_history(self):
        with Shitty(columns=10, rows=3, save_lines=6) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH"))
            terminal.write(b"\x1b[22J")

            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual(terminal.all_text(), ("1ABCD", "2EFGH"))

    def test_scroll_complete_on_an_empty_screen_is_a_noop(self):
        with Shitty(columns=10, rows=3, save_lines=6) as terminal:
            before = terminal.snapshot()
            terminal.write(b"\x1b[22J")
            after = terminal.snapshot()

            self.assertEqual(after.lines, before.lines)
            self.assertEqual(after.view_offset, before.view_offset)

    @unittest.expectedFailure
    def test_successive_scroll_complete_ignores_trailing_blank_rows(self):
        with Shitty(columns=10, rows=3, save_lines=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH") + b"\x1b[22J")
            terminal.write(put_rows(b"3ABCD") + b"\x1b[22J")
            terminal.write(b"\x1b[HX")

            self.assertEqual(terminal.all_text(), ("1ABCD", "2EFGH", "3ABCD", "X"))

    def test_scroll_above_inserts_a_background_colored_row(self):
        with Shitty(columns=10, rows=3, save_lines=10) as terminal:
            terminal.write(b"\x1b[48;2;155;0;0m" + put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            scroll_above(terminal)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2EFGH", "", "3IJKL"))
            self.assertEqual(snapshot.cell(0, 1).background, (155, 0, 0))

    def test_scroll_above_after_storage_rotation_preserves_following_rows(self):
        with Shitty(columns=10, rows=5, save_lines=180) as terminal:
            prepare_rotated_grid(terminal, 63, b"1A", b"2B", b"3C", b"4D", b"5E")
            terminal.write(b"\x1b[48;2;155;0;0m")
            scroll_above(terminal)

            self.assertEqual(visible_lines(terminal), ("2B", "", "3C", "4D", "5E"))

    def test_scroll_above_at_a_rotated_page_tail_preserves_following_rows(self):
        with Shitty(columns=10, rows=5, save_lines=180) as terminal:
            prepare_rotated_grid(terminal, 64, b"1A", b"2B", b"3C", b"4D", b"5E")
            terminal.write(b"\x1b[48;2;155;0;0m")
            scroll_above(terminal)

            self.assertEqual(visible_lines(terminal), ("2B", "", "3C", "4D", "5E"))

    def test_scroll_above_at_fresh_storage_preserves_the_bottom_row(self):
        with Shitty(columns=10, rows=3, save_lines=180) as terminal:
            prepare_rotated_grid(terminal, 127, b"1ABCD", b"2EFGH", b"3IJKL")
            terminal.write(b"\x1b[48;2;155;0;0m")
            scroll_above(terminal)

            self.assertEqual(visible_lines(terminal), ("2EFGH", "", "3IJKL"))

    def test_scroll_above_with_cursor_before_final_row_preserves_tail(self):
        with Shitty(columns=10, rows=4, save_lines=180) as terminal:
            prepare_rotated_grid(terminal, 96, b"1AB", b"2BC", b"3DE", b"4FG")
            terminal.write(b"\x1b[48;2;155;0;0m")
            scroll_above(terminal)

            self.assertEqual(visible_lines(terminal), ("2BC", "", "3DE", "4FG"))

    def test_scroll_above_without_history_preserves_the_bottom_row(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"\x1b[48;2;155;0;0m" + put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            scroll_above(terminal)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("2EFGH", "", "3IJKL"))
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.cell(0, 1).background, (155, 0, 0))


if __name__ == "__main__":
    unittest.main()

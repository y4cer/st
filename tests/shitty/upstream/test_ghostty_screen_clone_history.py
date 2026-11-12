# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen: scroll above hyperlink-dense row to fresh page",
    "Screen: scroll above hyperlink-dense row to existing page",
    "Screen: clone",
    "Screen: clone partial",
    "Screen: clone partial cursor out of bounds",
    "Screen: clone contains full selection",
    "Screen: clone contains none of selection",
    "Screen: clone contains selection start cutoff",
    "Screen: clone contains selection end cutoff",
    "Screen: clone contains selection end cutoff reversed",
    "Screen: clone contains subset of selection",
    "Screen: clone clamps clipped selections to mixed-width pages",
    "Screen: clone contains subset of rectangle selection",
    "Screen: clone basic",
    "Screen: clone empty viewport",
    "Screen: clone one line viewport",
    "Screen: clone empty active",
    "Screen: clone one line active with extra space",
    "Screen: clear history with no history",
    "Screen: clear history",
)


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def rotate_storage(terminal, count):
    terminal.write((b"history\r\n" * count) + b"tail\x1b[2J")


def write_linked_row(terminal, row, prefix):
    payload = [f"\x1b[{row};1H".encode()]
    uris = []
    for column in range(10):
        uri = f"https://example.test/{prefix}/{column}".encode()
        uris.append(uri.decode())
        payload.extend((osc8(uri), b"A", osc8()))
    terminal.write(b"".join(payload))
    return tuple(uris)


def assert_linked_row(test, terminal, row, uris):
    snapshot = terminal.snapshot()
    for column, uri in enumerate(uris):
        test.assertEqual(snapshot.cell(column, row).char, "A")
        test.assertEqual(terminal.hyperlink(column, row), uri)


class GhosttyScreenCloneHistoryTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_dense_hyperlink_row_survives_scroll_into_fresh_storage(self):
        with Shitty(columns=10, rows=5, save_lines=180) as terminal:
            rotate_storage(terminal, 127)
            uris = write_linked_row(terminal, 5, "fresh")
            terminal.write(b"\x1b[1;2r\x1b[2;1H\n\x1b[r")

            assert_linked_row(self, terminal, 4, uris)
            self.assertEqual(terminal.hyperlink_count(), 10)

    def test_dense_hyperlink_row_survives_scroll_into_existing_storage(self):
        with Shitty(columns=10, rows=5, save_lines=180) as terminal:
            rotate_storage(terminal, 128)
            uris = write_linked_row(terminal, 5, "existing")
            terminal.write(
                b"\x1b[1;2r\x1b[2;1H\n"
                b"\x1b[1;3r\x1b[3;1H\n\x1b[r"
            )

            assert_linked_row(self, terminal, 4, uris)
            self.assertEqual(terminal.hyperlink_count(), 10)

    def test_serialized_screen_copy_is_independent_of_later_output(self):
        with Shitty(columns=10, rows=3, save_lines=10) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH"))
            copied = terminal.model_snapshot()

            terminal.write(b"\x1b[3;1H34567")
            current = terminal.model_snapshot()

            self.assertEqual(copied.lines, ["1ABCD     ", "2EFGH     ", "          "])
            self.assertEqual((copied.cursor_x, copied.cursor_y), (5, 1))
            self.assertNotEqual(current.lines, copied.lines)

    def test_partial_screen_copy_exposes_only_the_requested_row(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH"))
            terminal.select_start(0, 1)
            terminal.select_update(5, 1)

            self.assertEqual(terminal.select_finish(), b"2EFGH")
            self.assertEqual(terminal.snapshot().selection, (0, 1, 5, 1))

    def test_screen_without_source_cursor_starts_with_a_safe_cursor(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[2;6H")
            copied = terminal.model_snapshot()
            terminal.write(b"\x1bc")
            reset = terminal.model_snapshot()

            self.assertEqual((copied.cursor_x, copied.cursor_y), (5, 1))
            self.assertEqual((reset.cursor_x, reset.cursor_y), (0, 0))
            self.assertEqual(reset.lines, ["          ", "          ", "          "])

    def test_full_screen_copy_keeps_a_complete_selection(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 1)
            terminal.select_update(5, 1)

            self.assertEqual(terminal.snapshot().selection, (0, 1, 5, 1))
            self.assertEqual(terminal.select_finish(), b"2EFGH")

    def test_screen_copy_without_selected_rows_has_no_selection(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 0)
            terminal.select_update(5, 0)
            terminal.write(b"\x1b[?1049h")

            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.select_finish(), b"1ABCD")

    def test_selection_start_is_clamped_to_the_copied_top_row(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 0)
            terminal.select_update(5, 1)
            terminal.write(b"\x1b[3;1H\n")

            self.assertEqual(terminal.snapshot().selection, (0, 0, 5, 0))
            self.assertEqual(terminal.select_finish(), b"2EFGH")

    def test_selection_end_is_clamped_to_the_last_available_cell(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 1)
            terminal.select_update(20, 20)

            self.assertEqual(terminal.snapshot().selection, (0, 1, 5, 2))
            self.assertEqual(terminal.select_finish(), b"2EFGH\n3IJKL")

    def test_reversed_selection_end_is_clamped_identically(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(20, 20)
            terminal.select_update(0, 1)

            self.assertEqual(terminal.snapshot().selection, (0, 1, 5, 2))
            self.assertEqual(terminal.select_finish(), b"2EFGH\n3IJKL")

    def test_copy_contained_by_a_selection_clamps_both_ends(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL", b"4ABCD"))
            terminal.select_start(-20, -20)
            terminal.select_update(20, 20)

            self.assertEqual(terminal.snapshot().selection, (0, 0, 5, 3))
            self.assertEqual(
                terminal.select_finish(),
                b"1ABCD\n2EFGH\n3IJKL\n4ABCD",
            )

    def test_selection_columns_clamp_after_width_changes(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"ABCD", b"EFGH", b"IJKL"))
            terminal.resize(2, 3)
            terminal.select_start(1, 0)
            terminal.select_update(3, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.selection, (1, 0, 2, 2))
            self.assertLessEqual(snapshot.selection[0], snapshot.columns)
            self.assertLessEqual(snapshot.selection[2], snapshot.columns)

    def test_rectangle_selection_keeps_columns_when_rows_are_clamped(self):
        with Shitty(columns=5, rows=4) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL", b"4ABCD"))
            terminal.select_start(1, -20)
            terminal.select_rectangular()
            terminal.select_update(4, 20)
            snapshot = terminal.snapshot()

            self.assertTrue(snapshot.rectangular_selection)
            self.assertEqual(snapshot.selection, (1, 0, 4, 3))
            self.assertEqual(terminal.select_finish(), b"ABC\nEFG\nIJK\nABC")

    def test_two_partial_ranges_copy_one_or_two_rows(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.select_start(0, 1)
            terminal.select_update(5, 1)
            self.assertEqual(terminal.select_finish(), b"2EFGH")

            terminal.select_start(0, 1)
            terminal.select_update(5, 2)
            self.assertEqual(terminal.select_finish(), b"2EFGH\n3IJKL")

    def test_empty_viewport_copy_is_empty(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_one_line_viewport_copy_keeps_the_line(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABC")

            self.assertEqual(visible_lines(terminal), ("1ABC", "", ""))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_empty_active_copy_contains_only_default_cells(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            snapshot = terminal.model_snapshot()

            self.assertTrue(all(cell.char == " " for cell in snapshot.cells))
            self.assertTrue(all(not cell.drawn for cell in snapshot.cells))

    def test_one_line_active_copy_keeps_only_blank_padding(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(b"1ABC")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "1ABC      ")
            self.assertEqual(visible_lines(terminal), ("1ABC", "", ""))

    def test_clear_history_without_history_preserves_the_active_screen(self):
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            terminal.write(put_rows(b"4ABCD", b"5EFGH", b"6IJKL"))
            before = terminal.snapshot()
            terminal.write(b"\x1b[3J")
            after = terminal.snapshot()

            self.assertEqual(after.lines, before.lines)
            self.assertEqual(after.view_offset, 0)
            self.assertEqual(terminal.all_text(), ("4ABCD", "5EFGH", "6IJKL"))

    def test_clear_history_discards_scrollback_and_returns_to_live_screen(self):
        with Shitty(columns=10, rows=3, save_lines=3) as terminal:
            terminal.write(b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4ABCD\r\n5EFGH\r\n6IJKL")
            terminal.wheel_up(3)
            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))

            terminal.write(b"\x1b[3J")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(visible_lines(terminal), ("4ABCD", "5EFGH", "6IJKL"))
            self.assertEqual(terminal.all_text(), ("4ABCD", "5EFGH", "6IJKL"))


if __name__ == "__main__":
    unittest.main()

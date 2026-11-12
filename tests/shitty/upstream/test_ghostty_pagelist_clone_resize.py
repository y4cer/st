# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList eraseRowBounded full rows single page",
    "PageList eraseRowBounded full rows two pages",
    "PageList eraseRow hyperlink-dense row crosses page boundary",
    "PageList eraseRowBounded hyperlink-dense row crosses page boundary",
    "PageList clone",
    "PageList clone partial trimmed right",
    "PageList clone partial trimmed left",
    "PageList clone partial trimmed left reclaims styles",
    "PageList clone partial trimmed both",
    "PageList clone less than active",
    "PageList clone remap tracked pin",
    "PageList clone remap tracked pin not in cloned area",
    "PageList clone full dirty",
    "PageList resize (no reflow) more rows",
    "PageList resize (no reflow) more rows with history",
    "PageList resize (no reflow) less rows",
    "PageList resize (no reflow) one rows",
    "PageList resize (no reflow) less rows cursor on bottom",
    "PageList resize (no reflow) less rows cursor in scrollback",
    "PageList resize (no reflow) less rows trims blank lines",
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


def select_rows(terminal, first, last, width=3):
    terminal.select_start(0, first)
    terminal.select_update(width, last)
    return terminal.select_finish().decode().splitlines()


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def dense_link_row(row, count=10):
    payload = bytearray(f"\x1b[{row + 1};1H".encode())
    for index in range(count):
        uri = f"https://example.test/{index}".encode()
        payload.extend(osc8(uri) + b"X" + osc8())
    return bytes(payload)


class GhosttyPageListCloneResizeTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_full_bounded_erase_clamps_to_the_remaining_region_rows(self):
        with Shitty(columns=4, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*[bytes([ord("A") + row]) for row in range(10)]))

            terminal.write(b"\x1b[6;10r\x1b[99S\x1b[r")

            self.assertEqual(
                visible_lines(terminal),
                ("A", "B", "C", "D", "E", "", "", "", "", ""),
            )
            self.assertEqual(terminal.last_update_rows(), (5, 6, 7, 8, 9))

    def test_bounded_erase_crosses_large_storage_boundaries_once(self):
        with Shitty(columns=4, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))

            terminal.write(b"\x1b[100;250r\x1b[4S\x1b[r")
            lines = visible_lines(terminal)

            self.assertEqual(lines[98], "098")
            self.assertEqual(lines[99], "103")
            self.assertEqual(lines[245:250], ("249", "", "", "", ""))
            self.assertEqual(lines[250], "250")

    def test_full_row_erase_moves_every_dense_hyperlink_with_its_cell(self):
        with Shitty(columns=12, rows=300, save_lines=0) as terminal:
            terminal.write(dense_link_row(150))

            terminal.write(b"\x1b[H\x1b[M")

            self.assertEqual(visible_lines(terminal)[149], "X" * 10)
            self.assertEqual(
                tuple(terminal.hyperlink(column, 149) for column in range(10)),
                tuple(f"https://example.test/{index}" for index in range(10)),
            )

    def test_bounded_cross_storage_erase_keeps_dense_links_and_outside_rows(self):
        with Shitty(columns=12, rows=300, save_lines=0) as terminal:
            terminal.write(dense_link_row(150) + b"\x1b[152;1HOUTSIDE")

            terminal.write(b"\x1b[1;151r\x1b[S\x1b[r")

            self.assertEqual(visible_lines(terminal)[149], "X" * 10)
            self.assertEqual(visible_lines(terminal)[151], "OUTSIDE")
            self.assertEqual(
                tuple(terminal.hyperlink(column, 149) for column in range(10)),
                tuple(f"https://example.test/{index}" for index in range(10)),
            )

    def test_public_model_snapshot_is_an_independent_full_copy(self):
        with Shitty(columns=6, rows=3, save_lines=3) as terminal:
            terminal.write(numbered_lines(0, 4))
            cloned = terminal.model_snapshot()

            terminal.write(b"\r\n005")

            self.assertEqual(tuple(line.rstrip() for line in cloned.lines), ("002", "003", "004"))
            self.assertEqual(visible_lines(terminal), ("003", "004", "005"))

    def test_bounded_copy_can_trim_only_the_right_side(self):
        with Shitty(columns=4, rows=50, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 49))

            self.assertEqual(select_rows(terminal, 0, 39), [f"{value:03}" for value in range(40)])

    def test_bounded_copy_can_trim_only_the_left_side(self):
        with Shitty(columns=4, rows=50, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 49))

            self.assertEqual(select_rows(terminal, 10, 49), [f"{value:03}" for value in range(10, 50)])

    def test_pruning_styled_left_rows_does_not_leak_style_to_retained_rows(self):
        with Shitty(columns=4, rows=3, save_lines=4) as terminal:
            payload = bytearray()
            for value in range(10):
                payload.extend(b"\x1b[1m" + f"{value:03}".encode() + b"\x1b[0m\r\n")
            payload.extend(numbered_lines(10, 19))
            terminal.write(bytes(payload))
            terminal.wheel_up(100)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.all_text(), tuple(f"{value:03}" for value in range(13, 20)))
            self.assertFalse(snapshot.cell(0, 0).bold)

    def test_bounded_copy_can_trim_both_sides(self):
        with Shitty(columns=4, rows=50, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 49))

            self.assertEqual(select_rows(terminal, 10, 35), [f"{value:03}" for value in range(10, 36)])

    def test_copy_shorter_than_active_keeps_the_public_screen_height(self):
        with Shitty(columns=4, rows=24, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 23))

            copied = select_rows(terminal, 5, 23)

            self.assertEqual(copied, [f"{value:03}" for value in range(5, 24)])
            self.assertEqual(terminal.snapshot().rows, 24)

    def test_snapshot_remaps_a_live_selection_to_the_same_cells(self):
        with Shitty(columns=4, rows=10, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.select_start(0, 6)
            terminal.select_update(3, 6)
            cloned = terminal.model_snapshot()

            self.assertEqual(cloned.selection, (0, 6, 3, 6))
            self.assertEqual(cloned.lines[6].rstrip(), "006")
            self.assertEqual(terminal.select_finish(), b"006")

    def test_resize_drops_a_selection_outside_the_retained_area(self):
        with Shitty(columns=4, rows=10, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.select_start(0, 3)
            terminal.select_update(3, 3)

            terminal.resize(4, 5)

            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

    def test_snapshot_copy_does_not_consume_dirty_row_publication(self):
        with Shitty(columns=4, rows=24, save_lines=0) as terminal:
            terminal.write(put_rows(b"A", *([b""] * 11), b"M", *([b""] * 10), b"X"))
            before = terminal.last_update_rows()

            cloned = terminal.model_snapshot()

            self.assertEqual(before, (0, 12, 23))
            self.assertEqual(terminal.last_update_rows(), before)
            self.assertEqual((cloned.lines[0][0], cloned.lines[12][0], cloned.lines[23][0]), ("A", "M", "X"))

    def test_no_reflow_height_growth_keeps_existing_rows_and_cursor(self):
        with Shitty(columns=6, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"000", b"001", b"002"))
            before = terminal.snapshot()

            terminal.resize(6, 10)
            after = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), ("000", "001", "002"))
            self.assertEqual((after.cursor_x, after.cursor_y), (before.cursor_x, before.cursor_y))

    def test_no_reflow_height_growth_pulls_history_above_a_bottom_cursor(self):
        with Shitty(columns=6, rows=3, save_lines=5) as terminal:
            terminal.write(numbered_lines(0, 4))

            terminal.resize(6, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(nonempty_visible_lines(terminal), tuple(f"{value:03}" for value in range(5)))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 4))

    def test_no_reflow_height_shrink_keeps_the_rows_nearest_the_cursor(self):
        with Shitty(columns=6, rows=10, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 9))

            terminal.resize(6, 5)

            self.assertEqual(visible_lines(terminal), tuple(f"{value:03}" for value in range(5, 10)))

    def test_no_reflow_height_can_shrink_to_one_row(self):
        with Shitty(columns=6, rows=10, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 9))

            terminal.resize(6, 1)

            self.assertEqual(visible_lines(terminal), ("009",))

    def test_bottom_cursor_remains_on_its_cell_after_height_shrink(self):
        with Shitty(columns=6, rows=10, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 9))

            terminal.resize(6, 5)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 4))
            self.assertEqual(snapshot.cell(0, snapshot.cursor_y).char, "0")
            self.assertEqual(snapshot.lines[snapshot.cursor_y].rstrip(), "009")

    def test_selection_anchor_can_move_from_active_screen_into_scrollback(self):
        with Shitty(columns=6, rows=10, save_lines=10) as terminal:
            terminal.write(numbered_lines(0, 9))
            terminal.select_start(0, 2)
            terminal.select_update(3, 2)

            terminal.resize(6, 5)
            terminal.wheel_up(100)

            self.assertEqual(visible_lines(terminal)[:3], ("000", "001", "002"))
            self.assertEqual(terminal.select_finish(), b"002")

    def test_no_reflow_shrink_trims_background_only_trailing_rows(self):
        with Shitty(columns=10, rows=5, save_lines=0) as terminal:
            terminal.write(
                b"A"
                b"\x1b[2;1H\x1b[41m\x1b[2K"
                b"\x1b[3;1H\x1b[2K"
                b"\x1b[4;1H\x1b[2K"
                b"\x1b[5;1H\x1b[2K\x1b[0m\x1b[1;2H"
            )

            terminal.resize(10, 2)

            self.assertEqual(visible_lines(terminal), ("A", ""))
            self.assertEqual(terminal.scrollback_state(), (0, 2, 2, 0))


if __name__ == "__main__":
    unittest.main()

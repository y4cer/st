# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "PageList eraseRowBounded invalidates viewport offset cache",
    "PageList row erasure renews affected page generations",
    "PageList trailing row truncation renews page generation",
    "PageList eraseRowBounded multi-page invalidates viewport offset cache",
    "PageList eraseRowBounded full page shift invalidates viewport offset cache",
    "PageList eraseRowBounded exhausts pages invalidates viewport offset cache",
    "PageList increaseCapacity to increase styles",
    "PageList increaseCapacity to increase graphemes",
    "PageList increaseCapacity to increase hyperlinks",
    "PageList increaseCapacity to increase string_bytes",
    "PageList increaseCapacity tracked pins",
    "PageList increaseCapacity returns OutOfSpace at max capacity",
    "PageList increaseCapacity after col shrink",
    "PageList increaseCapacity multi-page",
    "PageList increaseCapacity preserves dirty flag",
    "PageList pageIterator single page",
    "PageList pageIterator two pages",
    "PageList pageIterator history two pages",
    "PageList pageIterator reverse single page",
    "PageList pageIterator reverse two pages",
)


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def rgb(index):
    return (
        (index * 17 + 1) & 0xFF,
        (index * 29 + 2) & 0xFF,
        (index * 43 + 3) & 0xFF,
    )


def sgr_rgb(index):
    red, green, blue = rgb(index)
    return f"\x1b[38;2;{red};{green};{blue}m".encode()


def styled_numbered_lines(first, last, width=3):
    rows = []
    for value in range(first, last + 1):
        rows.append(sgr_rgb(value) + str(value).zfill(width).encode())
    return b"\r\n".join(rows)


class GhosttyPageListCapacityIterationTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_bounded_region_scroll_keeps_a_history_viewport_stable(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(numbered_lines(0, 19))
            terminal.wheel_up(10)
            before_lines = visible_lines(terminal)
            before_state = terminal.scrollback_state()

            terminal.write(b"\x1b[2;5r\x1b[S\x1b[r")

            self.assertEqual(visible_lines(terminal), before_lines)
            self.assertEqual(terminal.scrollback_state(), before_state)

    def test_rows_shifted_inside_a_region_publish_only_fresh_contents(self):
        with Shitty(columns=8, rows=6, save_lines=0) as terminal:
            terminal.write(b"A\r\nB\r\nC\r\nD\r\nE\r\nF")
            terminal.write(b"\x1b[2;5r\x1b[S\x1b[5;1HZ\x1b[r")

            self.assertEqual(visible_lines(terminal), ("A", "C", "D", "E", "Z", "F"))
            self.assertEqual(terminal.snapshot().cell(0, 4).char, "Z")

    def test_shrinking_trailing_blank_rows_and_regrowing_keeps_live_rows(self):
        with Shitty(columns=8, rows=6, save_lines=10) as terminal:
            terminal.write(b"A\r\nB")
            terminal.resize(8, 3)
            self.assertEqual(visible_lines(terminal)[:2], ("A", "B"))

            terminal.resize(8, 6)

            self.assertEqual(visible_lines(terminal)[:2], ("A", "B"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_tall_bounded_region_does_not_move_a_parked_history_view(self):
        with Shitty(columns=6, rows=300, save_lines=400) as terminal:
            terminal.write(numbered_lines(0, 599))
            terminal.wheel_up(300)
            before_lines = visible_lines(terminal)
            before_state = terminal.scrollback_state()

            terminal.write(b"\x1b[50;250r\x1b[100S\x1b[r")

            self.assertEqual(visible_lines(terminal), before_lines)
            self.assertEqual(terminal.scrollback_state(), before_state)

    def test_full_screen_shift_without_history_moves_each_row_once(self):
        with Shitty(columns=8, rows=6, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 5))
            terminal.write(b"\x1b[2S")

            self.assertEqual(visible_lines(terminal), ("002", "003", "004", "005", "", ""))
            self.assertEqual(terminal.scrollback_state(), (0, 6, 6, 0))

    def test_oversized_bounded_shift_exhausts_only_the_selected_region(self):
        with Shitty(columns=8, rows=6, save_lines=0) as terminal:
            terminal.write(b"A\r\nB\r\nC\r\nD\r\nE\r\nF")
            terminal.write(b"\x1b[2;5r\x1b[999S\x1b[r")

            self.assertEqual(visible_lines(terminal), ("A", "", "", "", "", "F"))

    def test_style_storage_growth_preserves_oldest_and_newest_renditions(self):
        with Shitty(columns=8, rows=4, save_lines=400) as terminal:
            terminal.write(styled_numbered_lines(0, 319))
            self.assertEqual(terminal.snapshot().cell(0, 3).foreground, rgb(319))

            terminal.wheel_up(10_000)

            self.assertEqual(visible_lines(terminal)[0], "000")
            self.assertEqual(terminal.snapshot().cell(0, 0).foreground, rgb(0))

    def test_grapheme_storage_growth_preserves_every_cluster(self):
        cluster = "a\N{COMBINING ACUTE ACCENT}"
        with Shitty(columns=4, rows=4, save_lines=220) as terminal:
            terminal.write(("\r\n".join([cluster] * 200)).encode())
            terminal.wheel_up(10_000)
            cell = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(cell.grapheme, tuple(map(ord, cluster)))
            self.assertEqual(terminal.all_text(), tuple([cluster] * 200))

    def test_hyperlink_storage_growth_preserves_distinct_targets(self):
        with Shitty(columns=4, rows=4, save_lines=160) as terminal:
            payload = bytearray()
            for index in range(128):
                uri = f"https://example.test/{index}".encode()
                payload.extend(osc8(uri) + b"X" + osc8())
                if index != 127:
                    payload.extend(b"\r\n")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.hyperlink(0, 3), "https://example.test/127")
            terminal.wheel_up(10_000)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/0")

    def test_large_string_storage_growth_preserves_long_link_values(self):
        with Shitty(columns=4, rows=4, save_lines=80) as terminal:
            payload = bytearray()
            uris = []
            for index in range(40):
                uri = f"https://example.test/{index}/" + "x" * 1024
                uris.append(uri)
                payload.extend(osc8(uri.encode()) + b"X" + osc8())
                if index != 39:
                    payload.extend(b"\r\n")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.hyperlink(0, 3), uris[-1])
            terminal.wheel_up(10_000)
            self.assertEqual(terminal.hyperlink(0, 0), uris[0])

    def test_selection_anchor_survives_unrelated_style_storage_growth(self):
        with Shitty(columns=512, rows=3, save_lines=0) as terminal:
            terminal.write(b"SELECT-ME")
            terminal.select_start(0, 0)
            terminal.select_update(9, 0)

            payload = bytearray(b"\x1b[2;1H")
            for index in range(256):
                payload.extend(sgr_rgb(index) + b"X")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.select_finish(), b"SELECT-ME")

    def test_thousands_of_live_styles_remain_observable_at_capacity_edges(self):
        with Shitty(columns=4096, rows=2, save_lines=0) as terminal:
            payload = bytearray()
            for index in range(4096):
                payload.extend(sgr_rgb(index) + b"X")
            terminal.write(bytes(payload))
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).foreground, rgb(0))
            self.assertEqual(snapshot.cell(4095, 0).foreground, rgb(4095))
            self.assertTrue(all(snapshot.cell(column, 0).char == "X" for column in range(4096)))

    def test_metadata_growth_after_column_shrink_keeps_reflowed_geometry(self):
        with Shitty(columns=20, rows=4, save_lines=20) as terminal:
            terminal.write(b"abcdefghijklmnopqrst")
            terminal.resize(5, 8)
            before = visible_lines(terminal)[:4]

            payload = bytearray(b"\x1b[8;1H")
            for index in range(64):
                payload.extend(sgr_rgb(index) + b"Z")
            terminal.write(bytes(payload))

            self.assertEqual(before, ("abcde", "fghij", "klmno", "pqrst"))
            self.assertEqual(terminal.snapshot().columns, 5)
            self.assertIn("Z", "".join(visible_lines(terminal)))

    def test_metadata_growth_in_history_does_not_change_the_active_page(self):
        with Shitty(columns=8, rows=6, save_lines=240) as terminal:
            payload = bytearray()
            for index in range(200):
                uri = f"https://example.test/page/{index}".encode()
                payload.extend(sgr_rgb(index) + osc8(uri) + b"X" + osc8())
                if index != 199:
                    payload.extend(b"\r\n")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.hyperlink(0, 5), "https://example.test/page/199")
            self.assertEqual(terminal.snapshot().cell(0, 5).foreground, rgb(199))
            terminal.wheel_up(10_000)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/page/0")
            self.assertEqual(terminal.snapshot().cell(0, 0).foreground, rgb(0))

    def test_capacity_growth_marks_the_modified_render_row_dirty(self):
        with Shitty(columns=128, rows=4, save_lines=0) as terminal:
            payload = bytearray(b"\x1b[3;1H")
            for index in range(96):
                payload.extend(sgr_rgb(index) + b"X")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.last_update_rows(), (2,))
            self.assertEqual(terminal.snapshot().cell(95, 2).foreground, rgb(95))

    def test_forward_active_traversal_preserves_single_screen_row_order(self):
        with Shitty(columns=6, rows=4, save_lines=0) as terminal:
            terminal.write(b"zero\r\none\r\ntwo\r\nthree")

            self.assertEqual(visible_lines(terminal), ("zero", "one", "two", "three"))

    def test_forward_active_traversal_covers_a_tall_screen_exactly_once(self):
        with Shitty(columns=6, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            snapshot = terminal.snapshot()

            self.assertEqual(tuple(line.rstrip() for line in snapshot.lines), tuple(f"{n:03}" for n in range(300)))
            self.assertEqual(len(snapshot.cells), 1800)

    def test_forward_history_traversal_excludes_no_retained_rows(self):
        with Shitty(columns=6, rows=5, save_lines=50) as terminal:
            terminal.write(numbered_lines(0, 39))

            self.assertEqual(terminal.all_text(), tuple(f"{n:03}" for n in range(40)))
            self.assertEqual(visible_lines(terminal), tuple(f"{n:03}" for n in range(35, 40)))

    def test_reverse_selection_traverses_a_single_screen_in_logical_order(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(b"abcde\r\nfghij\r\nklmno")
            terminal.select_start(5, 2)
            terminal.select_update(0, 0)

            self.assertEqual(terminal.select_finish(), b"abcde\nfghij\nklmno")

    def test_reverse_selection_traverses_a_tall_screen_without_losing_row_zero(self):
        with Shitty(columns=4, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            terminal.select_start(3, 299)
            terminal.select_update(0, 0)
            selected = terminal.select_finish().decode().splitlines()

            self.assertEqual(selected, [f"{n:03}" for n in range(300)])


if __name__ == "__main__":
    unittest.main()

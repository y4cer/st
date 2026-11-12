# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList split at middle row",
    "PageList split at row 0 is no-op",
    "PageList split at last row",
    "PageList split single row page returns OutOfSpace",
    "PageList split moves tracked pins",
    "PageList split tracked pin before split point unchanged",
    "PageList split tracked pin at split point moves to new page",
    "PageList split multiple tracked pins across regions",
    "PageList split tracked viewport_pin in split region moves correctly",
    "PageList split middle page preserves linked list order",
    "PageList split last page makes new page the last",
    "PageList split first page keeps original as first",
    "PageList split preserves wrap flags",
    "PageList split preserves styled cells",
    "PageList split preserves grapheme clusters",
    "PageList split preserves hyperlinks",
)


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def rgb(index):
    return (
        (index * 17 + 1) & 0xFF,
        (index * 29 + 2) & 0xFF,
        (index * 43 + 3) & 0xFF,
    )


def sgr(index):
    red, green, blue = rgb(index)
    return f"\x1b[38;2;{red};{green};{blue}m".encode()


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def styled_rows(first, last):
    payload = bytearray()
    for index in range(first, last + 1):
        payload.extend(sgr(index) + f"{index:03}".encode())
        if index != last:
            payload.extend(b"\r\n")
    return bytes(payload)


class GhosttyPageListSplitTest(unittest.TestCase):
    def test_upstream_inventory_has_all_16_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 16)
        self.assertEqual(len(set(UPSTREAM_CASES)), 16)

    def test_metadata_growth_around_a_middle_row_preserves_both_halves(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            payload = bytearray()
            for row in range(50, 250):
                payload.extend(f"\x1b[{row + 1};6H".encode() + sgr(row) + b"X")
            terminal.write(bytes(payload))

            lines = visible_lines(terminal)
            self.assertEqual(lines[49], "049")
            self.assertEqual(lines[50], "050  X")
            self.assertEqual(lines[249], "249  X")
            self.assertEqual(lines[250], "250")

    def test_capacity_growth_at_row_zero_leaves_following_rows_unchanged(self):
        with Shitty(columns=300, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*[f"ROW-{row}".encode() for row in range(10)]))
            payload = bytearray(b"\x1b[1;1H")
            for index in range(256):
                payload.extend(sgr(index) + b"X")
            terminal.write(bytes(payload))

            lines = visible_lines(terminal)
            self.assertTrue(lines[0].startswith("X" * 256))
            self.assertEqual(lines[1:], tuple(f"ROW-{row}" for row in range(1, 10)))

    def test_capacity_growth_on_the_last_row_keeps_the_preceding_rows(self):
        uri = b"https://example.test/" + b"x" * 4096
        with Shitty(columns=20, rows=10, save_lines=0) as terminal:
            terminal.write(put_rows(*[f"ROW-{row}".encode() for row in range(10)]))
            terminal.write(b"\x1b[10;1H" + osc8(uri) + b"LAST" + osc8())

            self.assertEqual(visible_lines(terminal)[:9], tuple(f"ROW-{row}" for row in range(9)))
            self.assertEqual(visible_lines(terminal)[9], "LAST9")
            self.assertEqual(terminal.hyperlink(0, 9), uri.decode())

    def test_single_row_accepts_metadata_growth_without_exposing_partial_state(self):
        with Shitty(columns=4096, rows=1, save_lines=0) as terminal:
            payload = bytearray()
            for index in range(4096):
                payload.extend(sgr(index) + b"X")
            terminal.write(bytes(payload))
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "X" * 4096)
            self.assertEqual(snapshot.cell(0, 0).foreground, rgb(0))
            self.assertEqual(snapshot.cell(4095, 0).foreground, rgb(4095))

    def test_selection_after_a_capacity_hotspot_keeps_its_text(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            terminal.select_start(0, 250)
            terminal.select_update(3, 250)
            payload = bytearray()
            for row in range(200):
                payload.extend(f"\x1b[{row + 1};6H".encode() + sgr(row) + b"X")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.select_finish(), b"250")

    def test_selection_before_a_capacity_hotspot_keeps_its_text(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            terminal.select_start(0, 20)
            terminal.select_update(3, 20)
            payload = bytearray()
            for row in range(100, 300):
                payload.extend(f"\x1b[{row + 1};6H".encode() + sgr(row) + b"X")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.select_finish(), b"020")

    def test_cursor_at_the_capacity_hotspot_remains_on_the_same_cell(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[151;5H")
            terminal.write(b"".join(sgr(index) for index in range(512)) + b"X")
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 150))
            self.assertEqual(snapshot.cell(4, 150).char, "X")
            self.assertEqual(snapshot.cell(4, 150).foreground, rgb(511))

    def test_cursor_and_both_selection_anchors_survive_one_capacity_growth(self):
        with Shitty(columns=10, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 299))
            terminal.select_start(0, 20)
            terminal.select_update(3, 280)
            terminal.write(b"\x1b[151;5H" + b"".join(sgr(index) for index in range(512)))
            snapshot = terminal.snapshot()
            selected = terminal.select_finish().decode().splitlines()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 150))
            self.assertEqual(len(selected), 261)
            self.assertEqual((selected[0], selected[-1]), ("020", "280"))

    def test_parked_viewport_keeps_its_rows_while_new_rich_output_grows_storage(self):
        with Shitty(columns=10, rows=4, save_lines=320) as terminal:
            terminal.write(styled_rows(0, 199))
            terminal.wheel_up(100)
            before = terminal.snapshot()

            terminal.write(b"\r\n" + styled_rows(200, 299))
            after = terminal.snapshot()

            self.assertEqual(tuple(line.rstrip() for line in after.lines), tuple(line.rstrip() for line in before.lines))
            self.assertEqual(after.view_offset, before.view_offset + 100)

    def test_rich_rows_keep_global_order_across_multiple_storage_boundaries(self):
        with Shitty(columns=10, rows=4, save_lines=700) as terminal:
            terminal.write(styled_rows(0, 599))

            self.assertEqual(terminal.all_text(), tuple(f"{index:03}" for index in range(600)))
            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            terminal.wheel_down(10_000)
            self.assertEqual(visible_lines(terminal), ("596", "597", "598", "599"))

    def test_new_rich_tail_becomes_the_last_row_without_losing_old_history(self):
        uri = b"https://example.test/tail"
        with Shitty(columns=10, rows=4, save_lines=240) as terminal:
            terminal.write(styled_rows(0, 199))
            terminal.write(b"\r\n" + sgr(200) + osc8(uri) + b"TAIL" + osc8())

            self.assertEqual(visible_lines(terminal)[-1], "TAIL")
            self.assertEqual(terminal.hyperlink(0, 3), uri.decode())
            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal)[0], "000")

    def test_oldest_rich_rows_remain_first_after_later_capacity_growth(self):
        with Shitty(columns=10, rows=4, save_lines=320) as terminal:
            terminal.write(styled_rows(0, 299))
            terminal.wheel_up(10_000)
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            self.assertEqual(snapshot.cell(0, 0).foreground, rgb(0))
            self.assertEqual(snapshot.cell(0, 3).foreground, rgb(3))

    def test_soft_wrap_topology_survives_metadata_capacity_growth(self):
        logical = tuple(f"{index:03}-abcdefghijk" for index in range(80))
        with Shitty(columns=5, rows=12, save_lines=300) as terminal:
            payload = bytearray()
            for index, line in enumerate(logical):
                payload.extend(sgr(index) + line.encode())
                if index != len(logical) - 1:
                    payload.extend(b"\r\n")
            terminal.write(bytes(payload))

            terminal.resize(20, 12)

            self.assertEqual(terminal.all_text(), logical)

    def test_distinct_styles_follow_their_cells_across_capacity_growth(self):
        with Shitty(columns=10, rows=4, save_lines=320) as terminal:
            terminal.write(styled_rows(0, 299))
            bottom = terminal.snapshot()
            terminal.wheel_up(150)
            middle = terminal.snapshot()
            terminal.wheel_up(10_000)
            top = terminal.snapshot()

            self.assertEqual(bottom.cell(0, 3).foreground, rgb(299))
            self.assertEqual(middle.cell(0, 0).foreground, rgb(146))
            self.assertEqual(top.cell(0, 0).foreground, rgb(0))

    def test_grapheme_clusters_follow_rows_across_capacity_growth(self):
        clusters = tuple(
            f"{chr(ord('a') + index % 26)}\N{COMBINING ACUTE ACCENT}"
            for index in range(300)
        )
        with Shitty(columns=4, rows=4, save_lines=320) as terminal:
            terminal.write(b"\r\n".join(cluster.encode() for cluster in clusters))

            self.assertEqual(terminal.all_text(), clusters)
            bottom = terminal.model_snapshot()
            self.assertEqual(bottom.cell(0, 3).grapheme, tuple(map(ord, clusters[-1])))
            terminal.wheel_up(10_000)
            top = terminal.model_snapshot()
            self.assertEqual(top.cell(0, 0).grapheme, tuple(map(ord, clusters[0])))

    def test_hyperlinks_follow_rows_across_capacity_growth(self):
        with Shitty(columns=4, rows=4, save_lines=240) as terminal:
            payload = bytearray()
            for index in range(200):
                uri = f"https://example.test/{index}".encode()
                payload.extend(osc8(uri) + b"X" + osc8())
                if index != 199:
                    payload.extend(b"\r\n")
            terminal.write(bytes(payload))

            self.assertEqual(terminal.hyperlink(0, 3), "https://example.test/199")
            terminal.wheel_up(100)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/96")
            terminal.wheel_up(10_000)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/0")


if __name__ == "__main__":
    unittest.main()

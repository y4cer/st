# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList resize reflow more cols no wrapped rows",
    "PageList resize reflow more cols wrapped rows",
    "PageList resize reflow invalidates viewport offset cache",
    "PageList resize reflow more cols creates multiple pages",
    "PageList resize reflow more cols wrap across page boundary",
    "PageList resize reflow more cols wrap across page boundary cursor in second page",
    "PageList resize reflow less cols wrap across page boundary cursor in second page",
    "PageList resize reflow more cols cursor in wrapped row",
    "PageList resize reflow more cols cursor in not wrapped row",
    "PageList resize reflow more cols cursor in wrapped row that isn't unwrapped",
    "PageList resize reflow more cols no reflow preserves semantic prompt",
    "PageList resize reflow exceeds hyperlink memory forcing capacity increase",
    "PageList resize reflow hyperlink dupe string alloc chunk rounding",
    "PageList resize reflow exceeds grapheme memory forcing capacity increase",
    "PageList resize reflow exceeds style memory forcing capacity increase",
    "PageList resize reflow more cols unwrap wide spacer head",
    "PageList resize reflow more cols unwrap wide spacer head across two rows",
    "PageList resize reflow more cols unwrap still requires wide spacer head",
    "PageList resize reflow less cols no reflow preserves semantic prompt",
    "PageList resize reflow less cols no reflow preserves semantic prompt on first line",
)


PROMPT = 1


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def nonempty_visible_lines(terminal):
    return tuple(line for line in visible_lines(terminal) if line)


def osc8(uri=b"", identifier=None):
    parameters = b"" if identifier is None else b"id=" + identifier
    return b"\x1b]8;" + parameters + b";" + uri + b"\x1b\\"


def osc133(action):
    return b"\x1b]133;" + action + b"\x1b\\"


def rgb(index):
    return (
        (index * 17 + 1) & 0xFF,
        (index * 29 + 2) & 0xFF,
        (index * 43 + 3) & 0xFF,
    )


def sgr_foreground(index):
    red, green, blue = rgb(index)
    return f"\x1b[38;2;{red};{green};{blue}m".encode()


def sgr_background(index):
    red, green, blue = rgb(index)
    return f"\x1b[48;2;{red};{green};{blue}m".encode()


class GhosttyPageListReflowCapacityTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_width_growth_keeps_independent_hard_rows_independent(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"AAAAA", b"BBBBB", b"CCCCC"))

            terminal.resize(10, 3)

            self.assertEqual(visible_lines(terminal), ("AAAAA", "BBBBB", "CCCCC"))

    def test_width_growth_unwraps_each_soft_line_without_joining_hard_lines(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"AAAA\r\nBBBB")

            terminal.resize(4, 4)

            self.assertEqual(visible_lines(terminal), ("AAAA", "BBBB", "", ""))

    def test_reflow_recomputes_a_parked_viewport_offset_from_its_anchor(self):
        logical_lines = [f"{value:02}{value:02}".encode() for value in range(12)]
        with Shitty(columns=2, rows=4, save_lines=20) as terminal:
            terminal.write(b"\r\n".join(logical_lines))
            terminal.wheel_up(10)
            before = terminal.snapshot()
            self.assertEqual(before.view_offset, 10)
            self.assertEqual(tuple(line.rstrip() for line in before.lines), ("05", "05", "06", "06"))

            terminal.resize(4, 4)
            after = terminal.snapshot()

            self.assertEqual(after.view_offset, 3)
            self.assertEqual(tuple(line.rstrip() for line in after.lines), ("0505", "0606", "0707", "0808"))

    def test_large_width_growth_preserves_all_logical_lines_across_storage_pages(self):
        lines = [f"{value:03}XYZ".encode() for value in range(150)]
        with Shitty(columns=5, rows=300, save_lines=0) as terminal:
            terminal.write(b"\r\n".join(lines))

            terminal.resize(600, 300)

            self.assertEqual(nonempty_visible_lines(terminal), tuple(line.decode() for line in lines))

    def test_width_growth_joins_a_soft_line_deep_inside_a_large_screen(self):
        with Shitty(columns=2, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[150;1H0101")

            terminal.resize(4, 300)

            self.assertEqual(visible_lines(terminal)[149], "0101")
            self.assertEqual(visible_lines(terminal)[150], "")

    def test_cursor_in_a_deep_continuation_row_tracks_the_same_cell_when_unwrapped(self):
        with Shitty(columns=2, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[150;1H0101\x1b[151;2H")

            terminal.resize(4, 300)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 149))
            self.assertEqual(snapshot.cell(3, 149).char, "1")

    def test_cursor_tracks_the_same_deep_cell_when_reflow_adds_a_row(self):
        with Shitty(columns=5, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[150;1H0123401234\x1b[151;3H")

            terminal.resize(4, 300)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 150))
            self.assertEqual(snapshot.cell(3, 150).char, "2")

    def test_cursor_in_a_wrapped_row_moves_to_its_unwrapped_column(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"0101\x1b[2;2H")

            terminal.resize(4, 4)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (3, 0))

    def test_cursor_in_the_first_soft_row_keeps_its_original_column(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"0101\x1b[1;2H")

            terminal.resize(4, 4)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (1, 0))

    def test_cursor_in_a_continuation_that_stays_wrapped_moves_to_the_new_row(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"010101\x1b[3;2H")

            terminal.resize(4, 4)

            self.assertEqual((terminal.snapshot().cursor_x, terminal.snapshot().cursor_y), (1, 1))

    def test_width_growth_preserves_a_prompt_marker_on_an_unwrapped_blank_row(self):
        with Shitty(columns=2, rows=4, save_lines=0) as terminal:
            terminal.write(b"\x1b[2;1H" + osc133(b"P"))
            self.assertEqual(terminal.row_semantic(1), PROMPT)

            terminal.resize(4, 4)

            self.assertEqual(terminal.row_semantic(1), PROMPT)

    def test_many_long_hyperlinks_survive_capacity_growth_during_unwrap(self):
        logical_lines = []
        uris = []
        for index in range(64):
            first = f"https://example.test/{index}/a/".encode() + b"a" * 1024
            second = f"https://example.test/{index}/b/".encode() + b"b" * 1024
            uris.append((first.decode(), second.decode()))
            logical_lines.append(
                b"Z" + osc8(first) + b"X" + osc8() + osc8(second) + b"Y" + osc8()
            )

        with Shitty(columns=2, rows=4, save_lines=140) as terminal:
            terminal.write(b"\r\n".join(logical_lines))

            terminal.resize(4, 4)

            self.assertEqual(terminal.all_text(), tuple(["ZXY"] * 64))
            self.assertEqual(terminal.hyperlink_count(), 128)
            terminal.wheel_up(10_000)
            self.assertEqual(terminal.hyperlink(1, 0), uris[0][0])
            self.assertEqual(terminal.hyperlink(2, 0), uris[0][1])
            terminal.wheel_down(10_000)
            self.assertEqual(terminal.hyperlink(1, 3), uris[-1][0])
            self.assertEqual(terminal.hyperlink(2, 3), uris[-1][1])

    def test_explicit_id_hyperlink_survives_string_chunk_rounding_during_unwrap(self):
        first_uri = b"a" * 64
        second_uri = b"b" * 33
        second_id = b"i" * 31
        with Shitty(columns=2, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"x"
                + osc8(first_uri) + b"A" + osc8()
                + osc8(second_uri, second_id) + b"B" + osc8()
            )

            terminal.resize(3, 3)

            self.assertEqual(visible_lines(terminal)[0], "xAB")
            self.assertEqual(terminal.hyperlink(1, 0), first_uri.decode())
            self.assertEqual(terminal.hyperlink(2, 0), second_uri.decode())
            self.assertEqual(terminal.hyperlink_count(), 2)

    def test_maximal_combining_clusters_survive_grapheme_capacity_growth(self):
        cluster = "X" + "\N{COMBINING ACUTE ACCENT}" * 15
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write((cluster * 8).encode())

            terminal.resize(5, 3)
            snapshot = terminal.model_snapshot()
            clusters = [cell.grapheme for cell in snapshot.cells if cell.drawn]

            self.assertEqual(clusters, [tuple(map(ord, cluster))] * 8)

    def test_unique_styles_survive_capacity_growth_when_two_rows_unwrap(self):
        payload = bytearray()
        for index in range(64):
            payload.extend(sgr_background(index) + b"X")
        for index in range(64, 128):
            payload.extend(sgr_foreground(index) + b"X")

        with Shitty(columns=64, rows=3, save_lines=0) as terminal:
            terminal.write(bytes(payload))

            terminal.resize(128, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "X" * 128)
            self.assertEqual(
                tuple(snapshot.cell(column, 0).background for column in range(64)),
                tuple(rgb(index) for index in range(64)),
            )
            self.assertEqual(
                tuple(snapshot.cell(column, 0).foreground for column in range(64, 128)),
                tuple(rgb(index) for index in range(64, 128)),
            )

    def test_width_growth_removes_a_wide_spacer_that_is_no_longer_needed(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write("x😀".encode())

            terminal.resize(4, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "x😀")
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)

    def test_width_growth_moves_a_wide_spacer_after_unwrapping_two_rows(self):
        with Shitty(columns=2, rows=3, save_lines=0) as terminal:
            terminal.write("xxx😀".encode())

            terminal.resize(4, 3)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "xxx ")
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)
            self.assertFalse(snapshot.cell(3, 0).double_width)
            self.assertFalse(snapshot.cell(3, 0).double_width_continuation)

    def test_width_growth_keeps_a_wide_spacer_when_the_glyph_still_does_not_fit(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write("xx😀".encode())

            terminal.resize(3, 2)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "xx ")
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)
            self.assertFalse(snapshot.cell(2, 0).double_width)
            self.assertFalse(snapshot.cell(2, 0).double_width_continuation)

    def test_width_shrink_copies_a_prompt_marker_to_every_new_soft_row(self):
        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(b"\x1b[2;1H" + osc133(b"P") + b"ABCD")

            terminal.resize(2, 4)
            snapshot = terminal.snapshot()

            self.assertEqual(tuple(line.rstrip() for line in snapshot.lines[1:3]), ("AB", "CD"))
            self.assertEqual(tuple(snapshot.cell(column, 1).semantic for column in range(2)), (PROMPT, PROMPT))
            self.assertEqual(tuple(snapshot.cell(column, 2).semantic for column in range(2)), (PROMPT, PROMPT))

    def test_width_shrink_preserves_a_blank_prompt_marker_on_the_first_row(self):
        with Shitty(columns=4, rows=4, save_lines=0) as terminal:
            terminal.write(osc133(b"P"))
            self.assertEqual(terminal.row_semantic(0), PROMPT)

            terminal.resize(2, 4)

            self.assertEqual(terminal.row_semantic(0), PROMPT)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Screen forwards optional scrollback limits",
    "Screen read and write",
    "Screen read and write newline",
    "Screen read and write scrollback",
    "Screen read and write no scrollback small",
    "Screen read and write no scrollback large",
    "Screen clearRows active one line",
    "Screen clearRows active multi line",
    "Screen clearRows active styled line",
    "Screen clearRows protected",
    "Screen eraseRows history",
    "Screen eraseRows history with more lines",
    "Screen: cursorDown across pages preserves style",
    "Screen: cursorUp across pages preserves style",
    "Screen: cursorAbsolute across pages preserves style",
    "Screen: cursorAbsolute to page with insufficient capacity",
    "Screen: scrolling",
    "Screen: scrolling with a single-row screen no scrollback",
    "Screen: scrolling with a single-row screen with scrollback",
    "Screen: scrolling across pages preserves style",
)


def numbered_rows(count):
    return b"\r\n".join(str(index).encode() for index in range(count))


class GhosttyScreenTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_screen_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_optional_scrollback_line_limit_is_forwarded_exactly(self):
        with Shitty(columns=80, rows=24, save_lines=123) as terminal:
            terminal.write(numbered_rows(160))
            self.assertEqual(terminal.scrollback_state()[0], 123)
            contents = terminal.all_text()
            self.assertEqual(len(contents), 147)
            self.assertEqual(contents[0], "13")
            self.assertEqual(contents[-1], "159")

    def test_read_and_write(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"hello, world")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0].rstrip(), "hello, world")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (12, 0))

    def test_read_and_write_newline(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"hello\r\nworld")
            snapshot = terminal.snapshot()
            self.assertEqual(
                [line.rstrip() for line in snapshot.lines[:2]],
                ["hello", "world"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 1))

    def test_read_and_write_scrollback(self):
        with Shitty(columns=80, rows=2, save_lines=8) as terminal:
            terminal.write(b"hello\r\nworld\r\ntest")
            self.assertEqual(terminal.all_text(), ("hello", "world", "test"))
            self.assertEqual(
                [line.rstrip() for line in terminal.snapshot().lines],
                ["world", "test"],
            )

    def test_read_and_write_no_scrollback_small(self):
        with Shitty(columns=80, rows=2, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\ntest")
            self.assertEqual(terminal.all_text(), ("world", "test"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_read_and_write_no_scrollback_large(self):
        with Shitty(columns=80, rows=2, save_lines=0) as terminal:
            terminal.write(numbered_rows(1001))
            self.assertEqual(terminal.all_text(), ("999", "1000"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_clear_active_one_line(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"hello, world")
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.snapshot().lines, [" " * 20] * 4)
            self.assertIn(0, terminal.last_update_rows())

    def test_clear_active_multiple_lines(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"hello\r\nworld")
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.snapshot().lines, [" " * 20] * 4)
            damaged = terminal.last_update_rows()
            self.assertIn(0, damaged)
            self.assertIn(1, damaged)

    def test_clear_active_releases_styled_contents_observably(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"\x1b[1mhello world\x1b[22m\x1b[2JX")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], " " * 11 + "X" + " " * 8)
            self.assertFalse(snapshot.cell(11, 0).bold)
            for row in range(snapshot.rows):
                for column in range(snapshot.columns):
                    self.assertFalse(snapshot.cell(column, row).bold)

    def test_selective_clear_preserves_only_decsca_cells(self):
        with Shitty(columns=40, rows=2) as terminal:
            terminal.write(
                b"UNPROTECTED"
                b"\x1b[1\"qPROTECTED\x1b[0\"q"
                b"UNPROTECTED\r\n"
                b"\x1b[1\"qPROTECTED\x1b[0\"q"
                b"UNPROTECTED"
                b"\x1b[1\"qPROTECTED\x1b[0\"q"
                b"\x1b[?2J"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                [line.rstrip() for line in snapshot.lines],
                ["           PROTECTED", "PROTECTED           PROTECTED"],
            )
            for column in range(11, 20):
                self.assertTrue(snapshot.cell(column, 0).protected)
            for column in (*range(0, 9), *range(20, 29)):
                self.assertTrue(snapshot.cell(column, 1).protected)

    def test_erase_history_keeps_the_active_rows(self):
        with Shitty(columns=5, rows=5, save_lines=10) as terminal:
            terminal.write(b"1\r\n2\r\n3\r\n4\r\n5\r\n6")
            self.assertEqual(terminal.all_text(), ("1", "2", "3", "4", "5", "6"))
            active = terminal.snapshot().lines
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.snapshot().lines, active)
            self.assertEqual(terminal.all_text(), ("2", "3", "4", "5", "6"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_erase_larger_history_keeps_the_active_rows(self):
        with Shitty(columns=5, rows=5, save_lines=10) as terminal:
            terminal.write(b"A\r\nB\r\nC\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6")
            self.assertEqual(
                terminal.all_text(),
                ("A", "B", "C", "1", "2", "3", "4", "5", "6"),
            )
            active = terminal.snapshot().lines
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.snapshot().lines, active)
            self.assertEqual(terminal.all_text(), ("2", "3", "4", "5", "6"))
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_cursor_down_after_long_scrollback_preserves_style(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            terminal.write(numbered_rows(300))
            terminal.write(b"\x1b[1;1H\x1b[1m\x1b[BD")
            cell = terminal.model_snapshot().cell(0, 1)
            self.assertEqual(cell.char, "D")
            self.assertTrue(cell.bold)

    def test_cursor_up_after_long_scrollback_preserves_style(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            terminal.write(numbered_rows(300))
            terminal.write(b"\x1b[3;1H\x1b[1m\x1b[AU")
            cell = terminal.model_snapshot().cell(0, 1)
            self.assertEqual(cell.char, "U")
            self.assertTrue(cell.bold)

    def test_cursor_absolute_after_long_scrollback_preserves_style(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            terminal.write(numbered_rows(300))
            terminal.write(b"\x1b[3;1H\x1b[1m\x1b[1;1HA")
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "A")
            self.assertTrue(cell.bold)

    def test_cursor_absolute_preserves_style_after_many_distinct_styles(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            stream = bytearray()
            for value in range(260):
                stream.extend(
                    f"\x1b[38;2;{value % 256};{(value * 3) % 256};"
                    f"{(value * 7) % 256}mX\r\n".encode()
                )
            stream.extend(b"\x1b[1m\x1b[1;1HZ")
            terminal.write(bytes(stream))
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.char, "Z")
            self.assertTrue(cell.bold)
            self.assertEqual(cell.foreground, (3, 9, 21))

    def test_scrolling_uses_current_background_for_the_new_row(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[48;2;155;0;0m"
                b"1ABCD\r\n2EFGH\r\n3IJKL"
            )
            terminal.write(b"\x1bD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                [line.rstrip() for line in snapshot.lines],
                ["2EFGH", "3IJKL", ""],
            )
            for column in range(snapshot.columns):
                self.assertEqual(snapshot.cell(column, 2).background, (155, 0, 0))
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))

    def test_scrolling_single_row_without_scrollback_blanks_it(self):
        with Shitty(columns=10, rows=1, save_lines=0) as terminal:
            terminal.write(b"1ABCD\x1bD")
            self.assertEqual(terminal.snapshot().lines, [" " * 10])
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.last_update_rows(), (0,))

    def test_scrolling_single_row_with_scrollback_retains_the_row(self):
        with Shitty(columns=10, rows=1, save_lines=2) as terminal:
            terminal.write(b"1ABCD\x1bD")
            self.assertEqual(terminal.snapshot().lines, [" " * 10])
            self.assertEqual(terminal.all_text(), ("1ABCD", ""))
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines, ["1ABCD     "])

    def test_scrolling_across_storage_boundaries_preserves_style(self):
        with Shitty(columns=10, rows=3, save_lines=400) as terminal:
            terminal.write(b"\x1b[1m" + numbered_rows(300) + b"\r\nZ")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 2).char, "Z")
            self.assertTrue(snapshot.cell(0, 2).bold)
            self.assertTrue(terminal.pen_state().bold)


if __name__ == "__main__":
    unittest.main()

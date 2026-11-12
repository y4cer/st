# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Page html trailing blank lines",
    "Page html ascii characters unchanged",
    "Page html mixed ascii and unicode",
    "Page VT with palette option emits RGB",
    "Page html with palette option emits RGB",
    "Page VT style reset properly closes styles",
    "Page codepoint_map single replacement",
    "Page codepoint_map conflicting replacement prefers last",
    "Page codepoint_map replace with string",
    "Page codepoint_map range replacement",
    "Page codepoint_map multiple ranges",
    "Page codepoint_map unicode replacement",
    "Page codepoint_map with styled formats",
    "Page codepoint_map empty map",
    "Page VT background color on trailing blank cells",
    "Page HTML with hyperlinks",
    "Page HTML with multiple hyperlinks",
    "Page HTML with hyperlink escaping",
    "Page HTML with styled hyperlink",
    "Page HTML hyperlink closes style before anchor",
    "Page HTML hyperlink point map maps closing to previous cell",
)


def select(terminal, start, end):
    terminal.select_start(*start)
    terminal.select_update(*end)
    return terminal.select_finish()


class GhosttyFormatterHtmlCodepointTest(unittest.TestCase):
    def test_upstream_inventory_has_21_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 21)
        self.assertEqual(len(set(UPSTREAM_CASES)), 21)

    def test_html_source_trims_trailing_blank_rows_from_plain_copy(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello\r\nworld\r\n\r\n")

            self.assertEqual(select(terminal, (0, 0), (80, 23)), b"hello\nworld")
            self.assertEqual(terminal.snapshot().cursor_y, 3)

    def test_html_ascii_source_is_unchanged_in_plain_copy(self):
        text = b"hello world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)

            self.assertEqual(select(terminal, (0, 0), (len(text), 0)), text)

    def test_html_mixed_ascii_and_unicode_source_keeps_codepoints(self):
        text = "test ╰─❯ ok"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text.encode())
            snapshot = terminal.snapshot()

            self.assertEqual(select(terminal, (0, 0), (len(text), 0)), text.encode())
            self.assertEqual(
                tuple(snapshot.cell(column, 0).char for column in range(5, 8)),
                tuple("╰─❯"),
            )

    def test_vt_palette_source_resolves_an_index_to_its_current_rgb(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b]4;1;rgb:ab/cd/ef\x1b\\\x1b[31mred")
            snapshot = terminal.model_snapshot()

            for column in range(3):
                cell = snapshot.cell(column, 0)
                self.assertEqual(cell.foreground_index, 1)
                self.assertEqual(cell.foreground, (0xAB, 0xCD, 0xEF))

    def test_html_palette_source_is_observable_as_index_and_rgb(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b]4;1;rgb:ab/cd/ef\x1b\\\x1b[31mred\x1b]4;1;?\x1b\\")
            cell = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(cell.foreground_index, 1)
            self.assertEqual(cell.foreground, (0xAB, 0xCD, 0xEF))
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]4;1;rgb:abab/cdcd/efef\x1b\\",
            )

    def test_vt_style_reset_limits_bold_to_the_preceding_run(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[1mbold\x1b[0mnormal")
            snapshot = terminal.snapshot()

            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(4)))
            self.assertTrue(
                all(not snapshot.cell(column, 0).bold for column in range(4, 10))
            )

    def test_codepoint_map_single_replacement_source_keeps_both_cells(self):
        text = b"hello world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(4, 0).char, "o")
            self.assertEqual(snapshot.cell(7, 0).char, "o")
            self.assertEqual(select(terminal, (0, 0), (len(text), 0)), text)

    def test_codepoint_map_conflict_source_remains_the_original_codepoint(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")

            self.assertEqual(terminal.snapshot().cell(4, 0).char, "o")
            self.assertEqual(select(terminal, (0, 0), (5, 0)), b"hello")

    def test_codepoint_map_string_source_keeps_one_addressable_cell(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"hello")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cursor_x, 5)
            self.assertEqual(snapshot.cell(4, 0).char, "o")
            self.assertEqual(snapshot.cell(5, 0).char, " ")

    def test_codepoint_map_range_source_preserves_each_ascii_cell(self):
        text = b"abcdefg"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)
            snapshot = terminal.snapshot()

            self.assertEqual(
                tuple(snapshot.cell(column, 0).char for column in range(len(text))),
                tuple(text.decode()),
            )

    def test_codepoint_map_multiple_range_source_preserves_the_separator(self):
        text = b"hello world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(5, 0).char, " ")
            self.assertEqual(snapshot.lines[0][: len(text)], text.decode())

    def test_codepoint_map_unicode_source_keeps_wide_cell_coordinates(self):
        text = "hello ⚡ world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text.encode())
            snapshot = terminal.model_snapshot()

            self.assertEqual(snapshot.cell(6, 0).char, "⚡")
            self.assertTrue(snapshot.cell(6, 0).double_width)
            self.assertTrue(snapshot.cell(7, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(8, 0).char, " ")
            self.assertEqual(select(terminal, (0, 0), (14, 0)), text.encode())

    def test_codepoint_map_styled_source_keeps_style_on_every_source_cell(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[31mred text\x1b[0m")
            snapshot = terminal.model_snapshot()

            self.assertEqual(select(terminal, (0, 0), (8, 0)), b"red text")
            for column in range(8):
                self.assertEqual(snapshot.cell(column, 0).foreground_index, 1)

    def test_empty_codepoint_map_source_is_plain_text(self):
        text = b"hello world"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(text)
            snapshot = terminal.model_snapshot()

            self.assertEqual(select(terminal, (0, 0), (len(text), 0)), text)
            self.assertTrue(all(snapshot.cell(column, 0).drawn for column in range(len(text))))

    def test_vt_trailing_blank_cells_retain_their_background(self):
        with Shitty(columns=20, rows=5, save_lines=0) as terminal:
            terminal.write(b"CPU:\x1b[41m\x1b[K\x1b[0m\r\nline2")
            snapshot = terminal.model_snapshot()

            self.assertEqual(snapshot.lines[0][:4], "CPU:")
            for column in range(4, 20):
                self.assertEqual(snapshot.cell(column, 0).background_index, 1)

    def test_html_hyperlink_source_scopes_one_link_run(self):
        uri = "https://example.com"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"link text\x1b]8;;\x1b\\ normal"
            )

            for column in range(9):
                self.assertEqual(terminal.hyperlink(column, 0), uri)
            self.assertEqual(terminal.hyperlink(9, 0), "")

    def test_html_multiple_hyperlink_sources_remain_distinct(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://first.com\x1b\\first\x1b]8;;\x1b\\ "
                b"\x1b]8;;https://second.com\x1b\\second\x1b]8;;\x1b\\"
            )

            self.assertEqual(terminal.hyperlink(0, 0), "https://first.com")
            self.assertEqual(terminal.hyperlink(4, 0), "https://first.com")
            self.assertEqual(terminal.hyperlink(5, 0), "")
            self.assertEqual(terminal.hyperlink(6, 0), "https://second.com")
            self.assertEqual(terminal.hyperlink(11, 0), "https://second.com")

    def test_html_hyperlink_escape_source_retains_the_literal_uri(self):
        uri = "https://example.com?a=1&b=2"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com?a=1&b=2\x1b\\"
                b"link\x1b]8;;\x1b\\"
            )

            self.assertEqual(terminal.hyperlink(0, 0), uri)
            self.assertEqual(terminal.hyperlink(3, 0), uri)

    def test_html_styled_hyperlink_source_keeps_both_attributes(self):
        uri = "https://example.com"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"\x1b[1mbold link\x1b[0m\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()

            for column in range(9):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertEqual(terminal.hyperlink(column, 0), uri)

    def test_html_hyperlink_survives_style_close_until_osc8_close(self):
        uri = "https://example.com"
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"\x1b[1mbold\x1b[0m plain"
            )
            snapshot = terminal.snapshot()

            for column in range(10):
                self.assertEqual(terminal.hyperlink(column, 0), uri)
            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(4)))
            self.assertTrue(
                all(not snapshot.cell(column, 0).bold for column in range(4, 10))
            )

    def test_html_hyperlink_close_places_following_cells_outside_the_link(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"link\x1b]8;;\x1b\\ normal"
            )

            for column in range(4):
                self.assertEqual(terminal.hyperlink(column, 0), "https://example.com")
            for column in range(4, 11):
                self.assertEqual(terminal.hyperlink(column, 0), "")


if __name__ == "__main__":
    unittest.main()

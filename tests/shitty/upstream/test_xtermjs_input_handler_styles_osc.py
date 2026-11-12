# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 141 through 160."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "SGR 4:2 and resets toggle double underline",
    "SGR 4:3 and resets toggle curly underline",
    "SGR 4:4 and resets toggle dotted underline",
    "SGR 4:5 and resets toggle dashed underline",
    "plain SGR 4 replaces an extended underline style",
    "underline color defaults to the foreground",
    "SGR 58 sets indexed and RGB underline colors",
    "underline colors persist on cells independently",
    "DECSTR resets IRM",
    "DECSTR resets cursor visibility",
    "DECSTR resets vertical margins",
    "DECSTR resets text attributes",
    "DECSTR resets DECSC data",
    "DECSTR resets DECOM",
    "OSC 4 queries palette colors",
    "OSC 4 sets palette colors",
    "OSC 4 skips invalid values without losing valid siblings",
    "OSC 8 accepts an id parameter",
    "OSC 8 preserves semicolons in the URI",
    "OSC 104 restores palette colors",
)


def query_palette(terminal, *indices):
    payload = b";".join(f"{index};?".encode() for index in indices)
    terminal.write(b"\x1b]4;" + payload + b"\x1b\\")
    return terminal.read_input()


class XtermJsInputHandlerStylesOscTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def assert_extended_underline_toggle(self, style):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                f"\x1b[4:{style}mA\x1b[4:0mB".encode()
                + f"\x1b[4:{style}mC\x1b[24mD".encode()
            )
            self.assertEqual(
                [terminal.snapshot().cell(column, 0).underline_style
                 for column in range(4)],
                [style, 0, style, 0],
            )

    def test_sgr_colon_double_and_resets(self):
        self.assert_extended_underline_toggle(2)

    def test_sgr_colon_curly_and_resets(self):
        self.assert_extended_underline_toggle(3)

    def test_sgr_colon_dotted_and_resets(self):
        self.assert_extended_underline_toggle(4)

    def test_sgr_colon_dashed_and_resets(self):
        self.assert_extended_underline_toggle(5)

    def test_plain_sgr_four_replaces_extended_underline_style(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[4:5mA\x1b[4mB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).underline_style, 5)
            self.assertEqual(snapshot.cell(1, 0).underline_style, 1)

    def test_underline_color_defaults_to_current_foreground(self):
        with Shitty(columns=8, rows=2) as terminal:
            for payload in (
                b"",
                b"\x1b[30m",
                b"\x1b[38;510m",
                b"\x1b[38;2;1;2;3m",
            ):
                terminal.write(payload + b"\x1b[4mX")
            snapshot = terminal.snapshot()
            for column in range(4):
                cell = snapshot.cell(column, 0)
                self.assertEqual(cell.underline_color, cell.foreground)

    @unittest.expectedFailure
    def test_sgr_58_sets_indexed_and_rgb_underline_colors(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[4m\x1b[58;5;123mA"
                b"\x1b[58;2::1:2:3mB"
            )
            snapshot = terminal.model_snapshot()
            indexed = snapshot.cell(0, 0)
            direct = snapshot.cell(1, 0)
            self.assertEqual(indexed.underline_index, 123)
            self.assertEqual(direct.underline_index, -1)
            self.assertEqual(direct.underline_color, (1, 2, 3))

    @unittest.expectedFailure
    def test_underline_colors_persist_on_cells_independently(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[4m\x1b[58;5;123mAB"
                b"\x1b[4:0mC"
                b"\x1b[4m\x1b[58;2::1:2:3mD"
                b"\x1b[24m"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).underline_index, 123)
            self.assertEqual(snapshot.cell(1, 0).underline_index, 123)
            self.assertEqual(
                snapshot.cell(2, 0).underline_color,
                snapshot.cell(2, 0).foreground,
            )
            self.assertEqual(snapshot.cell(3, 0).underline_color, (1, 2, 3))

    def test_decstr_resets_insert_mode(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[4h\x1b[!p\x1b[4$p")
            self.assertEqual(terminal.read_input(), b"\x1b[4;2$y")

    def test_decstr_resets_cursor_visibility(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?25l\x1b[!p\x1b[?25$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?25;1$y")

    def test_decstr_resets_vertical_margins(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[!p\x1bP$qr\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r1;5r\x1b\\")

    def test_decstr_resets_text_attributes(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[1;2;32;43mA\x1b[!pB")
            snapshot = terminal.snapshot()
            before = snapshot.cell(0, 0)
            after = snapshot.cell(1, 0)
            self.assertTrue(before.bold)
            self.assertTrue(before.faint)
            self.assertNotEqual(before.foreground, after.foreground)
            self.assertNotEqual(before.background, after.background)
            self.assertFalse(after.bold)
            self.assertFalse(after.faint)

    def test_decstr_resets_decsc_data(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"\x1b[2;5H\x1b7"
                b"\x1b[!p"
                b"\x1b[5;10H\x1b8X"
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_decstr_resets_origin_mode(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?6h\x1b[!p\x1b[?6$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?6;2$y")

    def test_osc4_queries_single_and_multiple_palette_colors(self):
        with Shitty(columns=10, rows=5) as terminal:
            zero = query_palette(terminal, 0)
            one_twenty_three = query_palette(terminal, 123)
            self.assertEqual(
                query_palette(terminal, 0, 123),
                zero + one_twenty_three,
            )

    def test_osc4_sets_single_and_multiple_palette_colors(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b]4;0;rgb:01/02/03\x1b\\")
            self.assertEqual(
                query_palette(terminal, 0),
                b"\x1b]4;0;rgb:0101/0202/0303\x1b\\",
            )
            terminal.write(b"\x1b]4;123;#aabbcc\x1b\\")
            self.assertEqual(
                query_palette(terminal, 123),
                b"\x1b]4;123;rgb:aaaa/bbbb/cccc\x1b\\",
            )
            terminal.write(
                b"\x1b]4;0;rgb:aa/bb/cc;123;#001122\x1b\\"
            )
            self.assertEqual(
                query_palette(terminal, 0, 123),
                b"\x1b]4;0;rgb:aaaa/bbbb/cccc\x1b\\"
                b"\x1b]4;123;rgb:0000/1111/2222\x1b\\",
            )

    @unittest.expectedFailure
    def test_osc4_invalid_value_does_not_block_valid_siblings(self):
        with Shitty(columns=10, rows=5) as terminal:
            original_45 = query_palette(terminal, 45)
            terminal.write(
                b"\x1b]4;0;rgb:aa/bb/cc;45;rgb:1/22/333;"
                b"123;#001122\x1b\\"
            )
            reply = query_palette(terminal, 0, 45, 123)
            self.assertIn(b"\x1b]4;0;rgb:aaaa/bbbb/cccc\x1b\\", reply)
            self.assertIn(original_45, reply)
            self.assertIn(b"\x1b]4;123;rgb:0000/1111/2222\x1b\\", reply)

    def test_osc8_accepts_id_and_closes_the_link(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"\x1b]8;id=100;http://localhost:3000\x1b\\A"
                b"\x1b]8;;\x1b\\B"
            )
            snapshot = terminal.snapshot()
            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(terminal.hyperlink(0, 0), "http://localhost:3000")
            self.assertEqual(snapshot.cell(1, 0).hyperlink, 0)

    def test_osc8_preserves_semicolons_in_the_uri(self):
        uri = "http://localhost:3000;abc=def"
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b]8;;" + uri.encode() + b"\x1b\\A")
            self.assertEqual(terminal.hyperlink(0, 0), uri)

    def test_osc104_restores_single_multiple_and_all_palette_colors(self):
        with Shitty(columns=10, rows=5) as terminal:
            original = query_palette(terminal, 0, 43)

            terminal.write(
                b"\x1b]4;0;#010203;43;#040506\x1b\\"
                b"\x1b]104;0\x1b\\\x1b]104;43\x1b\\"
            )
            self.assertEqual(query_palette(terminal, 0, 43), original)

            terminal.write(
                b"\x1b]4;0;#010203;43;#040506\x1b\\"
                b"\x1b]104;0;43\x1b\\"
            )
            self.assertEqual(query_palette(terminal, 0, 43), original)

            terminal.write(
                b"\x1b]4;0;#010203;43;#040506\x1b\\"
                b"\x1b]104\x1b\\"
            )
            self.assertEqual(query_palette(terminal, 0, 43), original)


if __name__ == "__main__":
    unittest.main()

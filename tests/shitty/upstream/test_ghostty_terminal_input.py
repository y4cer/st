# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class GhosttyTerminalInputTest(unittest.TestCase):
    def test_cursor_position_saturates_overflowing_origin_offsets(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(
                b"\x1b[3;8r"
                b"\x1b[?69h"
                b"\x1b[4;9s"
                b"\x1b[?6h"
                b"\x1b[999999999999;999999999999H"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (8, 7))

    def test_plain_input_and_basic_wraparound(self):
        with Shitty(columns=40, rows=40) as terminal:
            terminal.write_chunks(*[bytes((byte,)) for byte in b"hello"])
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))
            self.assertEqual(snapshot.lines[0].rstrip(), "hello")

        with Shitty(columns=5, rows=40) as terminal:
            terminal.write_chunks(
                *[bytes((byte,)) for byte in b"helloworldabc12"]
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 2))
            self.assertEqual(snapshot.lines[:3], ["hello", "world", "abc12"])
            self.assertTrue(snapshot.cell(4, 0).wrapped)
            self.assertTrue(snapshot.cell(4, 1).wrapped)

    def test_soft_wrap_preserves_prompt_semantics(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\")
            self.assertEqual(terminal.last_update(), (0, 0))
            terminal.write(b"hello")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["hel", "lo "])
            self.assertTrue(snapshot.cell(2, 0).wrapped)
            self.assertEqual(
                [
                    snapshot.cell(column, row).semantic
                    for row, width in ((0, 3), (1, 2))
                    for column in range(width)
                ],
                [1] * 5,
            )

    def test_input_forces_scroll(self):
        with Shitty(columns=1, rows=5) as terminal:
            terminal.write_chunks(*[bytes((byte,)) for byte in b"abcdef"])
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 4))
            self.assertEqual(snapshot.lines, ["b", "c", "d", "e", "f"])

    def test_every_cell_can_have_a_unique_direct_background(self):
        output = bytearray()
        for row in range(30):
            for column in range(30):
                output.extend(
                    f"\x1b[{row + 1};{column + 1}H"
                    f"\x1b[48;2;{column};{row};0mX".encode()
                )

        with Shitty(columns=30, rows=30) as terminal:
            terminal.write(bytes(output))
            snapshot = terminal.snapshot()
            for row in range(30):
                for column in range(30):
                    cell = snapshot.cell(column, row)
                    self.assertEqual(cell.char, "X")
                    self.assertEqual(cell.background, (column, row, 0))

    def test_glitch_text_grows_grapheme_storage_without_corruption(self):
        marks = "".join(chr(codepoint) for codepoint in range(0x300, 0x370))
        glitch = "".join(character + marks for character in "Ghostty")

        with Shitty(columns=30, rows=30) as terminal:
            terminal.write((glitch * 32).encode())
            snapshot = terminal.model_snapshot()
            self.assertTrue(any(cell.grapheme for cell in snapshot.cells))
            terminal.write(b"OK")
            self.assertIn("OK", "".join(terminal.snapshot().lines))

    def test_zero_width_character_without_base_is_ignored(self):
        with Shitty(columns=80, rows=80) as terminal:
            before = terminal.model_digest()
            terminal.write("\u200d".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertFalse(snapshot.cell(0, 0).drawn)
            self.assertEqual(terminal.model_digest(), before)

    def test_zero_width_character_extends_pending_wrap_cell(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write("xå\u0332".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(
                snapshot.cell(1, 0).grapheme,
                (ord("å"), 0x0332),
            )
            self.assertEqual(snapshot.lines[0], "xå")

    def test_single_very_long_line_does_not_corrupt_screen(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"x" * 1000)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["xxxxx"] * 5)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 4))

    def test_wide_character_and_right_edge_wrap(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(b"123456789" + "😀".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["123456789 ", "😀         "])
            self.assertTrue(snapshot.cell(8, 0).wrapped)
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

    def test_wide_character_without_autowrap_is_not_truncated(self):
        for prefix in (b"AAAA", b"AAAAA"):
            with self.subTest(prefix=prefix), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"\x1b[?7l" + prefix)
                before = terminal.model_digest()
                terminal.write("🚨".encode())
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[0], prefix.decode().ljust(5))
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
                self.assertFalse(snapshot.cell(4, 0).double_width)
                self.assertFalse(
                    snapshot.cell(4, 0).double_width_continuation
                )
                self.assertEqual(terminal.model_digest(), before)
                self.assertEqual(terminal.last_update(), (0, 0))

    def test_right_margin_wrap_and_damage_are_row_precise(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"123456789"
                b"\x1b[?69h\x1b[3;5s"
                b"\x1b[1;5H"
            )
            terminal.write(b"X")
            self.assertEqual(terminal.last_update_rows(), (0,))
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(b"Y")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:2], ["1234X6789 ", "  Y       "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))
            self.assertEqual(terminal.last_update_rows(), (0, 1))
            self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_wide_character_wraps_wholly_inside_horizontal_margins(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;5s\x1b[1;5H")
            terminal.write("😀".encode())
            snapshot = terminal.model_snapshot()
            self.assertFalse(snapshot.cell(4, 0).drawn)
            self.assertFalse(snapshot.cell(4, 0).wrapped)
            self.assertTrue(snapshot.cell(2, 1).double_width)
            self.assertTrue(
                snapshot.cell(3, 1).double_width_continuation
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))
            self.assertEqual(terminal.last_update_rows(), (0, 1))

    def test_wide_character_in_single_column_terminal(self):
        with Shitty(columns=1, rows=2) as terminal:
            terminal.write("😀".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" ", "😀"])
            self.assertFalse(snapshot.cell(1 - 1, 1).double_width)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_narrow_character_replaces_both_halves_of_wide_character(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("😀".encode())
            terminal.write(b"\x1b[H")
            terminal.write(b"A")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(1, 0).drawn)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)

    def test_overwriting_wide_cell_does_not_corrupt_previous_row_tail(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(("中" * 10).encode())
            terminal.write(b"\x1b[2;1H")
            terminal.write(b"A")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 1).char, "A")
            self.assertFalse(snapshot.cell(0, 1).double_width)
            self.assertEqual(snapshot.cell(8, 0).char, "中")
            self.assertTrue(snapshot.cell(8, 0).double_width)
            self.assertTrue(snapshot.cell(9, 0).double_width_continuation)

    def test_overwriting_wide_continuation_clears_leading_half(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write("橋".encode())
            terminal.write(b"\x1b[1;2H")
            terminal.write(b"X")
            snapshot = terminal.model_snapshot()
            self.assertFalse(snapshot.cell(0, 0).drawn)
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertEqual(snapshot.cell(1, 0).char, "X")
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.lines[0], " X   ")

    def test_replacing_wide_character_clears_attributes_on_both_halves(self):
        for attribute in (b"\x1b[1m", b"\x1b[48;2;255;0;0m"):
            with self.subTest(attribute=attribute):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(attribute + "😀".encode())
                    terminal.write(b"\x1b[H\x1b[0mA")
                    snapshot = terminal.model_snapshot()
                    self.assertEqual(snapshot.cell(0, 0).char, "A")
                    self.assertFalse(snapshot.cell(0, 0).bold)
                    self.assertEqual(snapshot.cell(0, 0).background, (0, 0, 0))
                    self.assertFalse(snapshot.cell(1, 0).drawn)
                    self.assertFalse(snapshot.cell(1, 0).bold)
                    self.assertEqual(snapshot.cell(1, 0).background, (0, 0, 0))


if __name__ == "__main__":
    unittest.main()

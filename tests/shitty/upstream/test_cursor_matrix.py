# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class CursorCommandMatrixTest(unittest.TestCase):
    def assert_cursor(self, terminal, column, row):
        snapshot = terminal.snapshot()
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (column, row))

    def test_horizontal_relative_commands_move_exact_counts(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[4;6H\x1b[3D")
            self.assert_cursor(terminal, 2, 3)
            terminal.write(b"\x1b[2C")
            self.assert_cursor(terminal, 4, 3)
            terminal.write(b"\x1b[2a")
            self.assert_cursor(terminal, 6, 3)

    def test_vertical_relative_commands_move_exact_counts(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[4;6H\x1b[2A")
            self.assert_cursor(terminal, 5, 1)
            terminal.write(b"\x1b[3B")
            self.assert_cursor(terminal, 5, 4)
            terminal.write(b"\x1b[1e")
            self.assert_cursor(terminal, 5, 5)

    def test_next_and_previous_line_home_the_cursor(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[3;7H\x1b[2E")
            self.assert_cursor(terminal, 0, 4)
            terminal.write(b"\x1b[3F")
            self.assert_cursor(terminal, 0, 1)

    def test_horizontal_absolute_aliases_address_the_same_column(self):
        for final in (b"G", b"`"):
            with self.subTest(final=final):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(b"\x1b[4;8H\x1b[3" + final)
                    self.assert_cursor(terminal, 2, 3)

    def test_vertical_absolute_addresses_requested_row(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[2;8H\x1b[5d")
            self.assert_cursor(terminal, 7, 4)

    def test_cup_and_hvp_are_equivalent(self):
        for final in (b"H", b"f"):
            with self.subTest(final=final):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(b"\x1b[5;7" + final)
                    self.assert_cursor(terminal, 6, 4)

    def test_default_tab_stops_for_forward_and_backward_tabulation(self):
        with Shitty(columns=25, rows=2) as terminal:
            terminal.write(b"\x1b[3I")
            self.assert_cursor(terminal, 24, 0)
            terminal.write(b"\x1b[2Z")
            self.assert_cursor(terminal, 8, 0)
            terminal.write(b"\x1b[9Z")
            self.assert_cursor(terminal, 0, 0)

    def test_custom_tab_stops_are_used_by_cht_and_cbt(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(
                b"\x1b[3g"
                b"\x1b[4G\x1bH"
                b"\x1b[10G\x1bH"
                b"\x1b[1G\x1b[2I"
            )
            self.assert_cursor(terminal, 9, 0)
            terminal.write(b"\x1b[2Z")
            self.assert_cursor(terminal, 0, 0)

    def test_cbt_ignores_horizontal_margins_without_origin_mode(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[5;15s"
                b"\x1b[2;9H\x1b[2Z"
            )
            self.assert_cursor(terminal, 0, 1)

    def test_cbt_stops_at_left_margin_in_origin_mode(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[5;15s\x1b[?6h"
                b"\x1b[2;5H\x1b[9Z"
            )
            self.assert_cursor(terminal, 4, 1)

    def test_tab_without_a_following_stop_preserves_pending_wrap(self):
        for setup in (b"", b"\x1b[3g\x1b[4G\x1bH\x1b[1G"):
            for tab in (b"\t", b"\x1b[I", b"\x1b[2I"):
                with self.subTest(setup=setup, tab=tab):
                    with Shitty(columns=8, rows=2) as terminal:
                        terminal.write(setup + b"12345678" + tab + b"X")
                        self.assertEqual(
                            terminal.snapshot().lines,
                            ["12345678", "X       "],
                        )

    def test_zero_and_omitted_counts_match_one_for_every_relative_command(self):
        commands = b"ABCDEFIZae"
        for final in commands:
            states = []
            for parameter in (b"", b"0", b"1"):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(b"\x1b[4;6H\x1b[" + parameter + bytes((final,)))
                    snapshot = terminal.snapshot()
                    states.append((snapshot.cursor_x, snapshot.cursor_y))
            with self.subTest(final=bytes((final,))):
                self.assertEqual(states[0], states[1])
                self.assertEqual(states[0], states[2])

    def test_huge_relative_counts_clip_without_wrapping_integer_types(self):
        cases = {
            b"A": (2, 0),
            b"B": (2, 5),
            b"C": (9, 2),
            b"D": (0, 2),
            b"E": (0, 5),
            b"F": (0, 0),
            b"I": (9, 2),
            b"Z": (0, 2),
            b"a": (9, 2),
            b"e": (2, 5),
        }
        for final, expected in cases.items():
            with self.subTest(final=final):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(
                        b"\x1b[3;3H\x1b[999999999999999999999" + final
                    )
                    self.assert_cursor(terminal, *expected)

    def test_huge_absolute_coordinates_clip_to_page_edges(self):
        sequences = (b"\x1b[999999999G", b"\x1b[999999999`")
        for sequence in sequences:
            with self.subTest(sequence=sequence):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(sequence)
                    self.assert_cursor(terminal, 9, 0)

        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[999999999d")
            self.assert_cursor(terminal, 0, 5)
            terminal.write(b"\x1b[999999999;999999999H")
            self.assert_cursor(terminal, 9, 5)

    def test_relative_vertical_motion_stays_in_margins_when_inside(self):
        with Shitty(columns=10, rows=7) as terminal:
            terminal.write(b"\x1b[3;6r\x1b[4;5H\x1b[99A")
            self.assert_cursor(terminal, 4, 2)
            terminal.write(b"\x1b[99B")
            self.assert_cursor(terminal, 4, 5)

    def test_relative_vertical_motion_obeys_directional_margin_barriers(self):
        with Shitty(columns=10, rows=7) as terminal:
            terminal.write(b"\x1b[3;6r\x1b[1;5H\x1b[99B")
            self.assert_cursor(terminal, 4, 5)
            terminal.write(b"\x1b[7;5H\x1b[99A")
            self.assert_cursor(terminal, 4, 2)

            terminal.write(b"\x1b[1;5H\x1b[99A")
            self.assert_cursor(terminal, 4, 0)
            terminal.write(b"\x1b[7;5H\x1b[99B")
            self.assert_cursor(terminal, 4, 6)

    def test_relative_horizontal_motion_stays_in_margins_when_inside(self):
        with Shitty(columns=12, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;9s\x1b[2;6H\x1b[99C")
            self.assert_cursor(terminal, 8, 1)
            terminal.write(b"\x1b[99D")
            self.assert_cursor(terminal, 2, 1)

    def test_relative_horizontal_motion_uses_page_edges_outside_margins(self):
        with Shitty(columns=12, rows=4) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;9s\x1b[2;11H\x1b[99D")
            self.assert_cursor(terminal, 0, 1)
            terminal.write(b"\x1b[99C")
            self.assert_cursor(terminal, 11, 1)

    def test_origin_mode_cup_is_relative_to_both_margin_pairs(self):
        with Shitty(columns=12, rows=7) as terminal:
            terminal.write(
                b"\x1b[2;6r\x1b[?69h\x1b[3;10s\x1b[?6h"
                b"\x1b[2;4H"
            )
            self.assert_cursor(terminal, 5, 2)

    def test_clipped_motion_clears_pending_autowrap(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[1;5HX\x1b[CY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "    Y")
            self.assertEqual(snapshot.lines[1], "     ")

    def test_movement_to_wide_continuation_clears_whole_glyph_on_write(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write("界".encode() + b"\x1b[1;2HX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:2], " X")
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)


if __name__ == "__main__":
    unittest.main()

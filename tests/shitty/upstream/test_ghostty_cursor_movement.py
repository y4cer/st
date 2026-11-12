# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class GhosttyCursorMovementTest(unittest.TestCase):
    def test_cursor_up_clamps_to_screen_or_margin_from_its_side(self):
        cases = (
            (
                b"\x1b[3;1HA\x1b[10AX",
                [" X   ", "     ", "A    ", "     ", "     "],
            ),
            (
                b"\x1b[2;4r\x1b[3;1HA\x1b[10AX",
                ["     ", " X   ", "A    ", "     ", "     "],
            ),
            (
                b"\x1b[3;5r\x1b[3;1HA\x1b[2;1H\x1b[10AX",
                ["X    ", "     ", "A    ", "     ", "     "],
            ),
        )
        for stream, expected in cases:
            with self.subTest(stream=stream), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(stream)
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_cursor_down_clamps_to_screen_or_margin_from_its_side(self):
        cases = (
            (
                b"A\x1b[10BX",
                ["A    ", "     ", "     ", "     ", " X   "],
            ),
            (
                b"\x1b[1;3rA\x1b[10BX",
                ["A    ", "     ", " X   ", "     ", "     "],
            ),
            (
                b"\x1b[1;3rA\x1b[4;1H\x1b[10BX",
                ["A    ", "     ", "     ", "     ", "X    "],
            ),
        )
        for stream, expected in cases:
            with self.subTest(stream=stream), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(stream)
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_every_relative_cursor_motion_cancels_pending_wrap(self):
        cases = (
            (b"\x1b[A", "ABCDX", (4, 0)),
            (b"\x1b[B", "ABCDE", (4, 1)),
            (b"\x1b[C", "ABCDX", (4, 0)),
            (b"\x1b[D", "ABCXE", (4, 0)),
            (b"\x1b[3D", "AXCDE", (2, 0)),
        )
        for movement, first_line, cursor in cases:
            with self.subTest(movement=movement), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(b"ABCDE")
                self.assertTrue(terminal.cursor_pending_wrap())
                terminal.write(movement)
                self.assertFalse(terminal.cursor_pending_wrap())
                terminal.write(b"X")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], first_line)
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    cursor,
                )

    def test_reverse_wrap_requires_a_soft_wrapped_predecessor(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[?7;45h"
                b"ABCDE1\x1b[2DX"
            )
            self.assertEqual(
                terminal.snapshot().lines[:2],
                ["ABCDX", "1    "],
            )
            self.assertTrue(terminal.cursor_pending_wrap())

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[?7;45h"
                b"ABCDE\r\n1\x1b[2DX"
            )
            self.assertEqual(
                terminal.snapshot().lines[:2],
                ["ABCDE", "X    "],
            )

    def test_reverse_wrap_modes_still_require_autowrap(self):
        for mode in (b"45", b"1045"):
            with self.subTest(mode=mode), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    b"\x1b[?7l\x1b[?" + mode + b"h"
                    b"\x1b[2;1H\x1b[2DX"
                )
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[1], "X    ")
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (1, 1),
                )

    def test_reverse_wrap_modes_cancel_pending_wrap_before_moving(self):
        for mode in (b"45", b"1045"):
            with self.subTest(mode=mode), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(
                    b"\x1b[?7;" + mode + b"h"
                    b"ABCDE\x1b[D"
                )
                self.assertFalse(terminal.cursor_pending_wrap())
                terminal.write(b"X")
                self.assertEqual(
                    terminal.snapshot().lines[0],
                    "ABCDX",
                )

    def test_extended_reverse_wrap_crosses_hard_rows_and_wraps_screen(self):
        cases = (
            (
                b"\x1b[?7;1045h"
                b"ABCDE\r\n1\x1b[2DX",
                ["ABCDX", "1    ", "     "],
            ),
            (
                b"\x1b[?7;1045h"
                b"ABCDE\r\n1\x1b[7DX",
                ["ABCDE", "1    ", "    X"],
            ),
            (
                b"\x1b[?7;45;1045h"
                b"ABCDE\r\n1\x1b[7DX",
                ["ABCDE", "1    ", "    X"],
            ),
        )
        for stream, expected in cases:
            with self.subTest(stream=stream), Shitty(
                columns=5,
                rows=3,
            ) as terminal:
                terminal.write(stream)
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_extended_reverse_wrap_skips_saturated_complete_cycles(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1b[?7;1045h"
                b"\x1b[4294967295D"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y),
                (0, 0),
            )

    def test_reverse_wrap_never_crosses_above_the_screen(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[?7;1045h"
                b"\x1b[3;5r\x1b[2;1H\x1b[1000D"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y),
                (0, 0),
            )

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"\x1b[?7;45h"
                b"\x1b[3;5r\x1b[1;2H\x1b[1000D"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y),
                (0, 0),
            )

    def test_cursor_right_clamps_to_active_or_physical_right_edge(self):
        cases = (
            (
                b"\x1b[100C",
                (4, 0),
            ),
            (
                b"\x1b[?69h\x1b[1;3s\x1b[100C",
                (2, 0),
            ),
            (
                b"\x1b[?69h\x1b[1;3s\x1b[1;4H\x1b[100C",
                (4, 0),
            ),
        )
        for stream, expected in cases:
            with self.subTest(stream=stream), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(stream)
                snapshot = terminal.snapshot()
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    expected,
                )

    def test_scroll_up_top_region_without_history_discards_the_row(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"E")
                + b"\x1b[1;3r\x1b[S\x1b[r"
            )
            terminal.wheel_up()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["B    ", "C    ", "     ", "D    ", "E    "],
            )


if __name__ == "__main__":
    unittest.main()

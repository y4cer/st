# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def assert_wide_cells_are_complete(test, snapshot):
    for column in range(snapshot.columns):
        cell = snapshot.cell(column, 0)
        if cell.double_width:
            test.assertLess(column + 1, snapshot.columns)
            test.assertTrue(
                snapshot.cell(
                    column + 1,
                    0,
                ).double_width_continuation
            )
        if cell.double_width_continuation:
            test.assertGreater(column, 0)
            test.assertTrue(snapshot.cell(column - 1, 0).double_width)


class GhosttyEraseLineTest(unittest.TestCase):
    def test_protection_modes_apply_to_subsequently_written_cells(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(
                b"A"
                b"\x1bVB\x1bW"
                b"C"
                b"\x1b[1\"qD\x1b[0\"q"
                b"E"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "ABCDE ")
            self.assertEqual(
                tuple(snapshot.cell(column, 0).protected for column in range(5)),
                (False, True, False, True, False),
            )

    def test_right_left_and_complete_erase_have_exact_damage(self):
        cases = (
            (b"\x1b[1;3H\x1b[K", "AB   "),
            (b"\x1b[1;3H\x1b[1K", "   DE"),
            (b"\x1b[1;3H\x1b[2K", "     "),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"ABCDE" + operation)
                self.assertEqual(terminal.snapshot().lines[0], expected)
                self.assertEqual(terminal.last_update_rows(), (0,))

    def test_erase_resets_pending_wrap_and_soft_wrap(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABCDE")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[K")
            self.assertFalse(terminal.cursor_pending_wrap())
            terminal.write(b"B")
            self.assertEqual(terminal.snapshot().lines[0], "ABCDB")

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"ABCDE123")
            self.assertTrue(
                any(
                    terminal.model_snapshot().cell(column, 0).wrapped
                    for column in range(5)
                )
            )
            terminal.write(b"\x1b[1;1H\x1b[KX")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["X    ", "123  "])
            self.assertFalse(
                any(snapshot.cell(column, 0).wrapped for column in range(5))
            )

    def test_each_erase_direction_uses_the_current_background(self):
        cases = (
            (b"\x1b[K", range(2, 5)),
            (b"\x1b[1K", range(0, 3)),
            (b"\x1b[2K", range(0, 5)),
        )
        for operation, erased in cases:
            with self.subTest(operation=operation), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(
                    b"ABCDE"
                    b"\x1b[1;3H"
                    b"\x1b[1;4:3;7;48;2;255;0;0m"
                    + operation
                )
                snapshot = terminal.model_snapshot()
                for column in erased:
                    cell = snapshot.cell(column, 0)
                    self.assertEqual(cell.background, (255, 0, 0))
                    self.assertFalse(
                        cell.bold
                        or cell.underline
                        or cell.inverse
                    )

    def test_right_and_left_erase_remove_both_halves_of_a_wide_glyph(self):
        cases = (
            (b"\x1b[1;4H\x1b[K", "AB        "),
            (b"\x1b[1;3H\x1b[1K", "    DE    "),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=10,
                rows=2,
            ) as terminal:
                terminal.write(
                    b"AB" + "橋".encode() + b"DE" + operation
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                assert_wide_cells_are_complete(self, snapshot)

    def test_regular_el_respects_only_iso_protection(self):
        operations = (
            (b"\x1b[1;1H\x1b[K", "ABC  "),
            (b"\x1b[1;2H\x1b[1K", "ABC  "),
            (b"\x1b[1;2H\x1b[2K", "ABC  "),
        )
        for operation, expected in operations:
            with self.subTest(protection="ISO", operation=operation), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"\x1bVABC\x1bW" + operation)
                self.assertEqual(terminal.snapshot().lines[0], expected)

        dec_cases = (
            (b"\x1b[1;1H\x1b[K", "     "),
            (b"\x1b[1;2H\x1b[1K", "  C  "),
            (b"\x1b[1;2H\x1b[2K", "     "),
        )
        for operation, expected in dec_cases:
            with self.subTest(protection="DEC", operation=operation), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"\x1b[1\"qABC\x1b[0\"q" + operation)
                self.assertEqual(terminal.snapshot().lines[0], expected)

    def test_toggling_dec_protection_does_not_destroy_iso_protection(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1bVABC\x1bW"
                b"\x1b[1\"q\x1b[0\"q"
                b"\x1b[1;1H\x1b[2K"
            )
            self.assertEqual(terminal.snapshot().lines[0], "ABC  ")

    def test_selective_el_respects_dec_protection_in_every_direction(self):
        cases = (
            (b"\x1b[1;4H\x1b[?K", "123  X    "),
            (b"\x1b[1;8H\x1b[?1K", "     X  9 "),
            (b"\x1b[1;8H\x1b[?2K", "     X    "),
        )
        for operation, expected in cases:
            with self.subTest(operation=operation), Shitty(
                columns=10,
                rows=2,
            ) as terminal:
                terminal.write(
                    b"123456789"
                    b"\x1b[1;6H\x1b[1\"qX\x1b[0\"q"
                    + operation
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                self.assertTrue(snapshot.cell(5, 0).protected)

    def test_selective_el_does_not_treat_iso_protection_as_decsca(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1bVABC\x1bW\x1b[1;1H\x1b[?2K")
            self.assertEqual(terminal.snapshot().lines[0], "     ")


if __name__ == "__main__":
    unittest.main()

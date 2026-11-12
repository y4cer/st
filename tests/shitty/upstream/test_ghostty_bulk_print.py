# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import random
import unittest

from harness import Shitty


PRINT_ALPHABET = (
    ord("a"),
    ord("b"),
    ord("Z"),
    ord("0"),
    ord(" "),
    0xE9,
    0xFF,
    0x301,
    0x4E00,
    0x4E01,
    0x1F600,
    0x200D,
    0xFE0F,
    ord("x"),
    ord("y"),
    0x1F9D1,
    0x308,
    0xAD,
    0x3042,
    0xAC00,
    ord("q"),
    ord("r"),
    ord("s"),
    ord("t"),
    ord("u"),
    ord("v"),
    ord("w"),
    ord("1"),
    ord("2"),
    0x1F1E6,
    0x1F1E7,
    0x1100,
    0x1161,
    0x11A8,
    0x200C,
    0x430,
    0x3B1,
)


class GhosttyBulkPrintTest(unittest.TestCase):
    def test_clear_current_and_all_tab_stops_do_not_damage_cells(self):
        with Shitty(columns=30, rows=2) as terminal:
            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().cursor_x, 8)
            terminal.write(b"\x1b[g")
            self.assertEqual(terminal.last_update(), (0, 0))
            terminal.write(b"\x1b[1;1H\t")
            self.assertEqual(terminal.snapshot().cursor_x, 16)

        with Shitty(columns=30, rows=2) as terminal:
            terminal.write(b"\x1b[3g")
            self.assertEqual(terminal.last_update(), (0, 0))
            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().cursor_x, 29)

    def test_repeat_uses_the_previous_character_and_wraps_normally(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"A\x1b[b")
            self.assertEqual(terminal.snapshot().lines[0], "AA   ")
            self.assertEqual(terminal.last_update_rows(), (0,))

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"    A\x1b[b")
            self.assertEqual(
                terminal.snapshot().lines,
                ["    A", "A    "],
            )

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[b")
            self.assertEqual(terminal.snapshot().lines[0], "     ")
            self.assertEqual(terminal.last_update(), (0, 0))

    def test_bulk_ascii_updates_cursor_previous_character_and_scroll(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"hello\x1b[2b")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "hellooo   ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 0))

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"abcdefghijkl")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["fghij", "kl   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))
            self.assertFalse(terminal.cursor_pending_wrap())

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"abcde")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_bulk_feed_matches_scalar_feed_differentially(self):
        rng = random.Random(0xC0FFEE)
        for columns, rows, operations in (
            (80, 24, 500),
            (10, 4, 500),
            (5, 2, 500),
            (2, 2, 200),
        ):
            with self.subTest(columns=columns, rows=rows), Shitty(
                columns=columns,
                rows=rows,
            ) as scalar, Shitty(columns=columns, rows=rows) as bulk:
                for operation_index in range(operations):
                    operation = rng.randrange(21)
                    if operation <= 9:
                        count = rng.randint(1, 64)
                        encoded = [
                            chr(rng.choice(PRINT_ALPHABET)).encode()
                            for _ in range(count)
                        ]
                        scalar.feed_chunks(*encoded)
                        chunks = []
                        offset = 0
                        while offset < count:
                            size = rng.randint(1, count - offset)
                            chunks.append(
                                b"".join(encoded[offset : offset + size])
                            )
                            offset += size
                        bulk.feed_chunks(*chunks)
                    elif operation == 10:
                        scalar.write(b"\r\n")
                        bulk.write(b"\r\n")
                    elif operation == 11:
                        row = rng.randint(1, rows)
                        column = rng.randint(1, columns)
                        sequence = f"\x1b[{row};{column}H".encode()
                        scalar.write(sequence)
                        bulk.write(sequence)
                    elif operation == 12:
                        attribute = rng.randrange(4)
                        if attribute == 0:
                            sequence = b"\x1b[0m"
                        elif attribute == 1:
                            sequence = b"\x1b[1m"
                        elif attribute == 2:
                            sequence = (
                                f"\x1b[38;2;{rng.randrange(256)};"
                                f"{rng.randrange(256)};"
                                f"{rng.randrange(256)}m"
                            ).encode()
                        else:
                            sequence = b"\x1b[31m"
                        scalar.write(sequence)
                        bulk.write(sequence)
                    elif operation in (13, 14, 15):
                        enabled = rng.randrange(2)
                        mode = (4, 7, 2027)[operation - 13]
                        private = b"?" if operation != 13 else b""
                        sequence = (
                            b"\x1b["
                            + private
                            + str(mode).encode()
                            + (b"h" if enabled else b"l")
                        )
                        scalar.write(sequence)
                        bulk.write(sequence)
                    elif operation == 16:
                        left = rng.randint(1, max(1, columns // 2))
                        right = rng.randint(left + 1, columns)
                        sequence = (
                            b"\x1b[?69h\x1b["
                            + str(left).encode()
                            + b";"
                            + str(right).encode()
                            + b"s"
                        )
                        scalar.write(sequence)
                        bulk.write(sequence)
                    elif operation == 17:
                        scalar.write(b"\x1b[?69l")
                        bulk.write(b"\x1b[?69l")
                    elif operation == 18:
                        sequence = (
                            b"\x1b]8;;https://example.test/differential"
                            b"\x1b\\"
                        )
                        scalar.write(sequence)
                        bulk.write(sequence)
                    elif operation == 19:
                        scalar.write(b"\x1b]8;;\x1b\\")
                        bulk.write(b"\x1b]8;;\x1b\\")
                    else:
                        sequence = b"\x1b(0" if rng.randrange(2) else b"\x1b(B"
                        scalar.write(sequence)
                        bulk.write(sequence)

                    with self.subTest(
                        columns=columns,
                        rows=rows,
                        operation=operation_index,
                    ):
                        self.assertEqual(
                            scalar.model_digest(),
                            bulk.model_digest(),
                        )
                        self.assertEqual(
                            scalar.cursor_pending_wrap(),
                            bulk.cursor_pending_wrap(),
                        )

                scalar.write(b"Z")
                bulk.write(b"Z")
                self.assertEqual(scalar.model_digest(), bulk.model_digest())
                self.assertEqual(scalar.pen_state(), bulk.pen_state())
                self.assertEqual(scalar.charset_state(), bulk.charset_state())
                self.assertEqual(
                    scalar.conformance_state(),
                    bulk.conformance_state(),
                )


if __name__ == "__main__":
    unittest.main()

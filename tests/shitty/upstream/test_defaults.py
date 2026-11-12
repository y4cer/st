# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


def observable(snapshot):
    return (
        snapshot.cursor_x,
        snapshot.cursor_y,
        snapshot.lines,
        snapshot.cells,
    )


class DefaultParameterMatrixTest(unittest.TestCase):
    def assert_variants_equal(self, prelude, *sequences, columns=12, rows=6):
        states = []
        for sequence in sequences:
            with Shitty(columns=columns, rows=rows) as terminal:
                terminal.write(prelude + sequence)
                states.append(observable(terminal.snapshot()))
        for state in states[1:]:
            self.assertEqual(state, states[0])

    def test_omitted_zero_and_one_mean_one_for_count_operations(self):
        operations = "ABCDEFGILMPSTXZ@`abde"
        for final in operations:
            with self.subTest(final=final):
                prelude = put_rows(b"abcdefghijk", b"second", b"third")
                prelude += b"\x1b[3;5H"
                self.assert_variants_equal(
                    prelude,
                    f"\x1b[{final}".encode(),
                    f"\x1b[0{final}".encode(),
                    f"\x1b[1{final}".encode(),
                )

    def test_cursor_position_defaults_each_coordinate_to_one(self):
        for final in "Hf":
            with self.subTest(final=final):
                self.assert_variants_equal(
                    b"\x1b[4;7H",
                    f"\x1b[{final}".encode(),
                    f"\x1b[0;0{final}".encode(),
                    f"\x1b[1;1{final}".encode(),
                )

    def test_erase_and_selective_erase_default_to_zero(self):
        prelude = put_rows(b"abcdefgh", b"ijklmnop", b"qrstuvwx")
        prelude += b"\x1b[2;4H"
        for final in ("J", "K"):
            with self.subTest(final=final):
                self.assert_variants_equal(
                    prelude,
                    f"\x1b[{final}".encode(),
                    f"\x1b[0{final}".encode(),
                    columns=8,
                    rows=3,
                )
        for final in ("J", "K"):
            with self.subTest(final="?" + final):
                self.assert_variants_equal(
                    prelude,
                    f"\x1b[?{final}".encode(),
                    f"\x1b[?0{final}".encode(),
                    columns=8,
                    rows=3,
                )

    def test_margin_defaults_expand_to_screen_edges(self):
        self.assert_variants_equal(
            b"",
            b"\x1b[r\x1b[?6hX",
            b"\x1b[0;0r\x1b[?6hX",
            b"\x1b[1;6r\x1b[?6hX",
        )
        self.assert_variants_equal(
            b"\x1b[?69h",
            b"\x1b[s\x1b[?6hX",
            b"\x1b[0;0s\x1b[?6hX",
            b"\x1b[1;12s\x1b[?6hX",
        )

    def test_rectangle_coordinates_use_documented_edge_defaults(self):
        prelude = put_rows(b"abcdefgh", b"ijklmnop", b"qrstuvwx")
        self.assert_variants_equal(
            prelude,
            b"\x1b[;;;$z",
            b"\x1b[0;0;0;0$z",
            b"\x1b[1;1;3;8$z",
            columns=8,
            rows=3,
        )

        for final in (b"z", b"{"):
            with self.subTest(final=final):
                self.assert_variants_equal(
                    prelude,
                    b"\x1b[$" + final,
                    b"\x1b[;;;$" + final,
                    b"\x1b[1;1;3;8$" + final,
                    columns=8,
                    rows=3,
                )

        self.assert_variants_equal(
            prelude,
            b"\x1b[37$x",
            b"\x1b[37;;;;$x",
            b"\x1b[37;1;1;3;8$x",
            columns=8,
            rows=3,
        )

        self.assert_variants_equal(
            prelude,
            b"\x1b[2;2;3;3;1$v",
            b"\x1b[2;2;3;3;1;1;1;1$v",
            columns=8,
            rows=3,
        )


if __name__ == "__main__":
    unittest.main()

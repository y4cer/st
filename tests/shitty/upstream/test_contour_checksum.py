# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ContourRectangularAreaChecksumTest(unittest.TestCase):
    def checksum(self, columns, rows, content=b"", flags=0):
        with Shitty(columns=columns, rows=rows) as terminal:
            if flags:
                terminal.write(f"\x1b[{flags}#y".encode())
            terminal.write(content)
            terminal.write(
                f"\x1b[99;1;1;1;{rows};{columns}*y".encode()
            )
            response = terminal.read_input()
            self.assertTrue(response.startswith(b"\x1bP99!~"))
            self.assertTrue(response.endswith(b"\x1b\\"))
            return int(response[6:-2], 16)

    def attributed(self, sgr):
        return self.checksum(1, 1, f"\x1b[{sgr}ma".encode())

    def test_default_is_the_negated_sum(self):
        self.assertEqual(self.checksum(1, 1, b"a"), 0xFF9F)
        self.assertEqual(self.checksum(2, 1, b"ab"), 0xFF3D)
        self.assertEqual(
            self.checksum(2, 2, b"ab\x1b[2;1Hcd"),
            0xFE76,
        )

    def test_written_space_is_not_an_empty_cell(self):
        self.assertEqual(self.checksum(1, 1, b" "), 0xFFE0)
        self.assertEqual(self.checksum(1, 1), 0)
        self.assertEqual(self.checksum(3, 1), 0)
        self.assertEqual(self.checksum(3, 1, b"ab"), 0xFF3D)

    def test_fill_rectangle_counts_like_written_text(self):
        # DECFRA fills must checksum like the same characters written
        # normally: xterm counts them, and a space put down by a fill is
        # still a written space.
        self.assertEqual(
            self.checksum(2, 1, b"\x1b[97;1;1;1;2$x"),
            self.checksum(2, 1, b"aa"),
        )
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[32;1;1;1;1$x"),
            self.checksum(1, 1, b" "),
        )

    def test_video_attributes_fold_into_the_cell_value(self):
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1\"qa"),
            0xFF9B,
        )
        self.assertEqual(self.attributed("8"), 0xFF97)
        self.assertEqual(self.attributed("4"), 0xFF8F)
        self.assertEqual(self.attributed("7"), 0xFF7F)
        self.assertEqual(self.attributed("5"), 0xFF5F)
        self.assertEqual(self.attributed("1"), 0xFF1F)
        self.assertEqual(self.attributed("6"), 0xFF5F)
        self.assertEqual(self.attributed("5;6"), 0xFF5F)
        self.assertEqual(self.attributed("3"), 0xFF9F)
        self.assertEqual(self.attributed("9"), 0xFF9F)
        self.assertEqual(self.attributed("51"), 0xFF9F)
        self.assertEqual(self.attributed("1;4;7"), 0xFEEF)

    def test_codepoints_are_mapped_into_the_dec_charset(self):
        self.assertEqual(
            self.checksum(1, 1, "\u00e9".encode()),
            0xFF97,
        )
        self.assertEqual(
            self.checksum(1, 1, "\u2592".encode()),
            0xFFE5,
        )
        self.assertEqual(
            self.checksum(2, 1, "a\u00a0".encode()),
            0xFF7F,
        )

    def test_positive_reports_the_plain_sum(self):
        self.assertEqual(self.checksum(1, 1, b"a", 1), 0x0061)
        self.assertEqual(self.checksum(2, 1, b"ab", 1), 0x00C3)
        self.assertEqual(self.checksum(1, 1, b" ", 1), 0x0020)
        self.assertEqual(
            self.checksum(1, 1, "\u00e9".encode(), 1),
            0x0069,
        )
        self.assertEqual(
            self.checksum(1, 1, "\u2592".encode(), 1),
            0x001B,
        )
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1ma", 1),
            0x00E1,
        )

    def test_no_attributes_leaves_video_attributes_out(self):
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1ma", 2),
            0xFF9F,
        )
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1\"qa", 2),
            0xFF9F,
        )

    def test_include_undrawn_counts_only_the_first_blank(self):
        self.assertEqual(self.checksum(1, 1, flags=8), 0xFFE0)
        self.assertEqual(self.checksum(2, 1, flags=8), 0xFFE0)
        self.assertEqual(self.checksum(3, 1, flags=8), 0xFFE0)
        self.assertEqual(self.checksum(2, 2, flags=8), 0xFFE0)
        self.assertEqual(
            self.checksum(1, 2, b"\x1b[2;1Ha", 8),
            0xFF7F,
        )

    def test_keep_blanks_counts_every_cell(self):
        self.assertEqual(self.checksum(2, 1, flags=4), 0xFFC0)
        self.assertEqual(self.checksum(3, 1, flags=4), 0xFFA0)
        self.assertEqual(self.checksum(2, 2, flags=4), 0xFF80)
        self.assertEqual(self.checksum(3, 1, b"ab", 4), 0xFF1D)

    def test_raw_codepoint_reports_the_codepoint_verbatim(self):
        self.assertEqual(
            self.checksum(1, 1, "\u00e9".encode(), 16),
            0xFF17,
        )
        self.assertEqual(
            self.checksum(1, 1, "\u2592".encode(), 16),
            0xDA6E,
        )
        self.assertEqual(self.checksum(2, 1, flags=16), 0)
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1ma", 16),
            0xFF1F,
        )

    def test_flags_compose(self):
        self.assertEqual(self.checksum(1, 1, flags=10), 0xFFE0)
        self.assertEqual(self.checksum(1, 1, b"a", 10), 0xFF9F)
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1\"qa", 10),
            0xFF9F,
        )
        self.assertEqual(
            self.checksum(1, 1, b"\x1b[1ma", 3),
            0x0061,
        )

    def test_combining_marks(self):
        # Cluster continuation codepoints count in the trimmed and the
        # keep-blanks sums alike: for a fully written region the two
        # views must agree.
        combining = "e\u0301".encode()
        expected = (-(0x65 + 0x0301)) & 0xFFFF
        self.assertEqual(self.checksum(1, 1, combining), expected)
        self.assertEqual(self.checksum(1, 1, combining, 4), expected)
        self.assertEqual(
            self.checksum(1, 1, combining, 20),
            (-0x65) & 0xFFFF,
        )


if __name__ == "__main__":
    unittest.main()

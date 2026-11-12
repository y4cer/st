# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from font_fixture import NERD_FONT
from harness import Shitty


def render(text, columns, rows, fontsize=17):
    with Shitty(
        columns=columns,
        rows=rows,
        extra_arguments=("-fontsize", str(fontsize)),
    ) as terminal:
        terminal.write(
            b"\x1b[?25l\x1b[48;5;16m\x1b[38;2;255;0;0m" + text.encode()
        )
        cell = terminal.load_font(NERD_FONT)
        border = terminal.options()["border"]
        width, height, pixels = terminal.render_image(NERD_FONT)
    return cell["px"], cell["py"], border, width, pixels


def red(pixels, width, border, x, y):
    offset = ((border + y) * width + border + x) * 3
    return pixels[offset] / 255


class BlockElementTest(unittest.TestCase):
    # Issue 60: fonts rasterize the block elements with fractional ink,
    # leaving background seams at cell boundaries. The renderer draws
    # U+2580-259F itself now, on exact cell pixels, even when the font
    # covers them - JetBrainsMono does, which is what this file loads.
    def test_full_blocks_leave_no_seams(self):
        cw, ch, border, width, pixels = render(
            "\x1b[1;1H██\x1b[2;1H██", columns=4, rows=2
        )
        # The reporter's metric: the ink lost where four blocks meet.
        row = (1 - red(pixels, width, border, cw // 2, ch - 1)) + (
            1 - red(pixels, width, border, cw // 2, ch)
        )
        column = (1 - red(pixels, width, border, cw - 1, ch // 2)) + (
            1 - red(pixels, width, border, cw, ch // 2)
        )
        self.assertEqual(row, 0.0, "ink lost at the row boundary")
        self.assertEqual(column, 0.0, "ink lost at the column boundary")

    def test_half_blocks_split_the_cell_exactly(self):
        cw, ch, border, width, pixels = render("▀", columns=2, rows=1)
        boundary = ch * 4 // 8
        for y in range(ch):
            expected = 1.0 if y < boundary else 0.0
            self.assertEqual(
                red(pixels, width, border, cw // 2, y),
                expected,
                f"upper half block at row {y}",
            )

    def test_stacked_halves_meet_without_a_seam(self):
        cw, ch, border, width, pixels = render(
            "\x1b[1;1H▄\x1b[2;1H▀", columns=2, rows=2
        )
        # The lower half of row one and the upper half of row two form
        # one solid band across the cell boundary.
        for y in range(ch * 4 // 8, ch + ch * 4 // 8):
            self.assertEqual(
                red(pixels, width, border, cw // 2, y),
                1.0,
                f"seam at row {y}",
            )

    def test_left_and_right_eighths_are_complementary(self):
        cw, ch, border, width, pixels = render("▉▕", columns=3, rows=1)
        split = cw * 7 // 8
        for x in range(cw):
            self.assertEqual(
                red(pixels, width, border, x, ch // 2),
                1.0 if x < split else 0.0,
                f"left seven eighths at column {x}",
            )
        for x in range(cw):
            self.assertEqual(
                red(pixels, width, border, cw + x, ch // 2),
                1.0 if x >= split else 0.0,
                f"right eighth at column {x}",
            )

    def test_quadrants_fill_their_corners(self):
        cw, ch, border, width, pixels = render("▖", columns=2, rows=1)
        for x, y, expected in (
            (cw // 4, ch // 4, 0.0),
            (3 * cw // 4, ch // 4, 0.0),
            (cw // 4, 3 * ch // 4, 1.0),
            (3 * cw // 4, 3 * ch // 4, 0.0),
        ):
            self.assertEqual(
                red(pixels, width, border, x, y),
                expected,
                f"quadrant lower left at ({x}, {y})",
            )

    def test_shades_cover_their_fractions(self):
        for glyph, expected in (("░", 4 / 16), ("▒", 8 / 16), ("▓", 12 / 16)):
            with self.subTest(glyph=glyph):
                cw, ch, border, width, pixels = render(glyph, columns=2, rows=1)
                inked = sum(
                    red(pixels, width, border, x, y)
                    for y in range(ch)
                    for x in range(cw)
                )
                self.assertAlmostEqual(
                    inked / (cw * ch), expected, delta=0.06
                )

    def test_box_drawing_joins_across_cells(self):
        # Box drawing bypasses the font now too: the vertical line runs
        # through both rows without a break at the cell boundary.
        cw, ch, border, width, pixels = render(
            "\x1b[1;1H│\x1b[2;1H│", columns=2, rows=2
        )
        profile = [red(pixels, width, border, x, 0) for x in range(cw)]
        self.assertGreater(sum(profile), 0.0)
        for y in range(1, 2 * ch):
            self.assertEqual(
                [red(pixels, width, border, x, y) for x in range(cw)],
                profile,
                f"vertical line changes at row {y}",
            )

    def test_box_drawing_stem_matches_the_primary_font_pipe(self):
        cw, ch, border, width, pixels = render(
            "|│", columns=2, rows=1, fontsize=32
        )
        pipe_rows = [
            sum(red(pixels, width, border, x, y) for x in range(cw))
            for y in range(ch)
        ]
        pipe_rows = sorted(value for value in pipe_rows if value > 0.05)
        self.assertTrue(pipe_rows)
        pipe_stem = pipe_rows[len(pipe_rows) // 2]

        synthesized_rows = [
            sum(red(pixels, width, border, cw + x, y) for x in range(cw))
            for y in range(ch)
        ]
        self.assertTrue(all(value > 0.05 for value in synthesized_rows))
        synthesized_stem = sum(synthesized_rows) / len(synthesized_rows)
        self.assertAlmostEqual(synthesized_stem, pipe_stem, delta=0.35)


if __name__ == "__main__":
    unittest.main()

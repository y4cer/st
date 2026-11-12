# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""A non-scalable bitmap strike through the FreeType backend: the
strike's own ascender places the baseline, and the monochrome glyphs
land in the cell bit for bit."""

import unittest

from font_fixture import FONT_ROOT
from harness import Shitty


BITMAP_FONT = FONT_ROOT / "fixture-8x8.bdf"
SPLEEN = FONT_ROOT / "spleen-8x16.bdf"
COZETTE = FONT_ROOT / "cozette.bdf"
BORDER = 2

# (font, requested size, cell width, cell height, strike baseline)
REAL_FONTS = (
    (SPLEEN, 16, 8, 16, 12),
    (COZETTE, 13, 6, 13, 10),
)

GLYPH_A = (0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x00)
GLYPH_B = (0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0x00)


def cell_bits(pixels, width, column):
    # A lit pixel is whatever differs from the corner background; the
    # mono strike leaves no antialiasing in between.
    background = pixels[:3]
    rows = []
    for y in range(8):
        value = 0
        for x in range(8):
            offset = 3 * ((BORDER + y) * width + BORDER + column * 8 + x)
            value = (value << 1) | int(pixels[offset : offset + 3] != background)
        rows.append(value)
    return tuple(rows)


class BitmapFontRenderTest(unittest.TestCase):
    def render(self, size):
        with Shitty(
            columns=2,
            rows=1,
            extra_arguments=("-fontsize", str(size)),
        ) as terminal:
            terminal.write(b"\x1b[?25lAB")
            metrics = terminal.load_font(str(BITMAP_FONT))
            width, height, pixels = terminal.render_image(str(BITMAP_FONT))
            return metrics, width, height, pixels

    def test_matching_size_draws_the_strike_bit_for_bit(self):
        metrics, width, height, pixels = self.render(8)
        self.assertEqual((metrics["px"], metrics["py"]), (8, 8))
        self.assertEqual((width, height), (2 * BORDER + 16, 2 * BORDER + 8))
        self.assertEqual(cell_bits(pixels, width, 0), GLYPH_A)
        self.assertEqual(cell_bits(pixels, width, 1), GLYPH_B)

    def test_repeated_glyph_hits_the_strike_cache_bit_for_bit(self):
        # The second A comes out of the glyph cache; a hit must be
        # indistinguishable from the fresh rasterization.
        with Shitty(
            columns=3,
            rows=1,
            extra_arguments=("-fontsize", "8"),
        ) as terminal:
            terminal.write(b"\x1b[?25lABA")
            terminal.load_font(str(BITMAP_FONT))
            width, height, pixels = terminal.render_image(str(BITMAP_FONT))
        self.assertEqual(cell_bits(pixels, width, 0), GLYPH_A)
        self.assertEqual(cell_bits(pixels, width, 1), GLYPH_B)
        self.assertEqual(cell_bits(pixels, width, 2), GLYPH_A)

    def test_mismatched_size_still_uses_the_only_strike(self):
        metrics, width, height, pixels = self.render(16)
        # A bitmap-only face has nothing to scale: the lone 8-pixel
        # strike serves whatever size was asked.
        self.assertEqual((metrics["px"], metrics["py"]), (8, 8))
        self.assertEqual(cell_bits(pixels, width, 0), GLYPH_A)


class RealBitmapFontTest(unittest.TestCase):
    # Two shipped bitmap families end to end: strike metrics become the
    # cell, the strike ascender places the baseline (descenders reach
    # below it - the exact signature of the baseline regression), and
    # box drawing spans the whole cell.
    def render(self, font, size, text):
        with Shitty(
            columns=4,
            rows=1,
            extra_arguments=("-fontsize", str(size)),
        ) as terminal:
            terminal.write(b"\x1b[?25l" + text.encode())
            metrics = terminal.load_font(str(font))
            width, height, pixels = terminal.render_image(str(font))
            return metrics, width, pixels

    def inked_rows(self, pixels, width, column, cell_width, cell_height):
        background = pixels[:3]
        rows = set()
        for y in range(cell_height):
            for x in range(cell_width):
                offset = 3 * ((BORDER + y) * width + BORDER + column * cell_width + x)
                if pixels[offset : offset + 3] != background:
                    rows.add(y)
                    break
        return rows

    def test_strike_metrics_shape_the_cell(self):
        for font, size, cell_width, cell_height, _ in REAL_FONTS:
            with self.subTest(font=font.name):
                metrics, _, _ = self.render(font, size, " ")
                self.assertEqual(metrics["px"], cell_width)
                self.assertEqual(metrics["py"], cell_height)

    def test_descenders_hang_below_the_strike_baseline(self):
        for font, size, cell_width, cell_height, baseline in REAL_FONTS:
            with self.subTest(font=font.name):
                _, width, pixels = self.render(font, size, "Ag_")
                capital = self.inked_rows(pixels, width, 0, cell_width, cell_height)
                descender = self.inked_rows(pixels, width, 1, cell_width, cell_height)
                underscore = self.inked_rows(pixels, width, 2, cell_width, cell_height)
                self.assertTrue(capital, "no ink in the capital")
                self.assertTrue(all(row < baseline for row in capital), capital)
                self.assertTrue(any(row >= baseline for row in descender), descender)
                self.assertTrue(underscore, "no ink in the underscore")
                self.assertTrue(all(row >= baseline for row in underscore), underscore)

    def test_box_drawing_spans_the_whole_cell_at_the_font_stem_width(self):
        for font, size, cell_width, cell_height, _ in REAL_FONTS:
            with self.subTest(font=font.name):
                _, width, pixels = self.render(font, size, "|─│")
                background = pixels[:3]

                def lit(column, x, y):
                    offset = 3 * ((BORDER + y) * width + BORDER + column * cell_width + x)
                    return pixels[offset : offset + 3] != background

                pipe_width = max(
                    sum(lit(0, x, y) for x in range(cell_width))
                    for y in range(cell_height)
                )
                full_rows = [
                    y for y in range(cell_height)
                    if all(lit(1, x, y) for x in range(cell_width))
                ]
                full_columns = [
                    x for x in range(cell_width)
                    if all(lit(2, x, y) for y in range(cell_height))
                ]
                self.assertEqual(len(full_rows), pipe_width, full_rows)
                self.assertEqual(len(full_columns), pipe_width, full_columns)


if __name__ == "__main__":
    unittest.main()

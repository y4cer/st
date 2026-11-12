# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""The straight dentistry brackets and the media-control symbols are
synthesized: most monospace fonts lack them (the embedded fallback
included), and a TUI status line built from them turned into notdef
boxes."""

import unittest

from font_fixture import FONT_ROOT
from harness import Shitty


BITMAP_FONT = FONT_ROOT / "fixture-8x8.bdf"
BORDER = 2
CELL = 8


class SynthesizedSymbolTest(unittest.TestCase):
    def render(self, text):
        with Shitty(
            columns=len(text),
            rows=1,
            extra_arguments=("-fontsize", "8"),
        ) as terminal:
            terminal.write(b"\x1b[?25l" + text.encode())
            terminal.load_font(str(BITMAP_FONT))
            width, height, pixels = terminal.render_image(str(BITMAP_FONT))
            return width, pixels

    def ink(self, pixels, width, column, x, y):
        offset = 3 * ((BORDER + y) * width + BORDER + column * CELL + x)
        background = pixels[:3]
        return max(
            abs(pixels[offset + i] - background[i]) for i in range(3)
        )

    def test_media_symbols_have_their_shapes(self):
        width, pixels = self.render("⏵⏺⏹⏸")
        # The right-pointing triangle: full at the base, gone past the
        # apex and above the upper slope.
        self.assertGreaterEqual(self.ink(pixels, width, 0, 2, 4), 100)
        self.assertLess(self.ink(pixels, width, 0, 7, 4), 100)
        self.assertLess(self.ink(pixels, width, 0, 2, 0), 100)
        # The record circle: solid center, empty corners.
        self.assertGreaterEqual(self.ink(pixels, width, 1, 4, 4), 100)
        for x, y in ((0, 0), (7, 0), (0, 7), (7, 7)):
            self.assertLess(self.ink(pixels, width, 1, x, y), 100)
        # The stop square: solid center and diagonal shoulder.
        self.assertGreaterEqual(self.ink(pixels, width, 2, 4, 4), 100)
        self.assertGreaterEqual(self.ink(pixels, width, 2, 2, 2), 100)
        # The pause bars with a dimmer gap between them.
        bar = self.ink(pixels, width, 3, 2, 4)
        gap = self.ink(pixels, width, 3, 4, 4)
        self.assertGreaterEqual(bar, 100)
        self.assertGreater(bar, gap)

    def test_dentistry_brackets_hug_the_cell_edges(self):
        width, pixels = self.render("⎿⏋")
        # Vertical and bottom right: the left column and the bottom row.
        self.assertGreaterEqual(self.ink(pixels, width, 0, 0, 0), 100)
        self.assertGreaterEqual(self.ink(pixels, width, 0, 0, 4), 100)
        self.assertGreaterEqual(self.ink(pixels, width, 0, 4, 7), 100)
        self.assertGreaterEqual(self.ink(pixels, width, 0, 7, 7), 100)
        self.assertLess(self.ink(pixels, width, 0, 7, 0), 100)
        self.assertLess(self.ink(pixels, width, 0, 4, 4), 100)
        # Vertical and top left: the right column and the top row.
        self.assertGreaterEqual(self.ink(pixels, width, 1, 7, 7), 100)
        self.assertGreaterEqual(self.ink(pixels, width, 1, 0, 0), 100)
        self.assertLess(self.ink(pixels, width, 1, 0, 7), 100)


if __name__ == "__main__":
    unittest.main()

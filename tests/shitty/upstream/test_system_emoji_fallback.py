# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Issue 85: an emoji absent from the configured family must cascade
to the system color face on macOS instead of the primary's notdef
box."""

import os
import sys
import unittest

from font_fixture import NERD_FONT
from harness import Shitty


APPLE_COLOR_EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"


@unittest.skipUnless(sys.platform == "darwin", "the Core Text cascade is macOS-only")
@unittest.skipUnless(os.access(APPLE_COLOR_EMOJI, os.R_OK), "no system emoji face in this sandbox")
class SystemEmojiFallbackTest(unittest.TestCase):
    def test_globe_cascades_to_the_system_color_face(self):
        with Shitty(
            columns=4,
            rows=1,
            extra_arguments=("-fontsize", "22"),
        ) as terminal:
            terminal.write("\x1b[?25l🌐".encode())
            metrics = terminal.load_font(str(NERD_FONT))
            border = terminal.options()["border"]
            width, height, pixels = terminal.render_image(str(NERD_FONT))

        chromatic = {
            pixels[offset : offset + 3]
            for offset in range(0, len(pixels), 3)
            if max(pixels[offset : offset + 3]) != min(pixels[offset : offset + 3])
        }
        self.assertGreater(len(chromatic), 4, "the globe rendered without color")

        colored_rows = []
        for row in range(border, border + metrics["py"]):
            for column in range(border, width - border):
                offset = 3 * (row * width + column)
                pixel = pixels[offset : offset + 3]
                if max(pixel) != min(pixel):
                    colored_rows.append(row)
                    break
        self.assertTrue(colored_rows, "the globe rendered no colored ink")
        top_margin = min(colored_rows) - border
        bottom_margin = border + metrics["py"] - 1 - max(colored_rows)
        self.assertLessEqual(
            abs(top_margin - bottom_margin),
            2,
            f"the globe is not vertically centered ({top_margin}, {bottom_margin})",
        )


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import hashlib
import unittest

from font_fixture import COLOR_EMOJI_FONT
from harness import Shitty


class ColorFontRenderTest(unittest.TestCase):
    def test_color_zwj_grapheme_renders_to_image(self):
        with Shitty(
            columns=2,
            rows=1,
            extra_arguments=("-fontsize", "32"),
        ) as terminal:
            terminal.write(b"\x1b[?25l" + "👩‍💻".encode())
            width, height, pixels = terminal.render_image(COLOR_EMOJI_FONT)

        self.assertEqual((width, height), (84, 42))
        self.assertEqual(
            hashlib.sha256(pixels).hexdigest(),
            "9a0ea45ef565bc6fca3da680d205b275bc2a8d3d97bce5c7088c9733df514337",
        )
        chromatic_colors = {
            pixels[offset : offset + 3]
            for offset in range(0, len(pixels), 3)
            if max(pixels[offset : offset + 3])
            != min(pixels[offset : offset + 3])
        }
        self.assertGreater(len(chromatic_colors), 16)


if __name__ == "__main__":
    unittest.main()

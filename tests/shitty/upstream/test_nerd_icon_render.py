# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from font_fixture import NERD_FONT
from harness import Shitty


# Wide Nerd Font pictograms behind width-one codepoints, the eza --icons
# staple: the NixOS snowflake, the Python logo, and the C symbol from the
# issue-32 listing.
ICONS = tuple(chr(code) for code in (0xF313, 0xE606, 0xE61E, 0xE60B))


def ink_margins(pixels, width, cell_width, height, cell):
    """Horizontal ink margins of one cell in an RGB row-major image."""
    left = None
    right = None
    for column in range(cell * cell_width, (cell + 1) * cell_width):
        for row in range(height):
            offset = (row * width + column) * 3
            if max(pixels[offset : offset + 3]) > 8:
                inside = column - cell * cell_width
                left = inside if left is None else min(left, inside)
                right = inside if right is None else max(right, inside)
                break
    if left is None:
        return None
    return left, cell_width - 1 - right


class NerdIconRenderTest(unittest.TestCase):
    def test_icon_with_trailing_blank_spreads_over_two_cells(self):
        # The kitty/ghostty consensus from issue 32: a pictogram followed
        # by a blank cell captures it and renders at natural size across
        # both cells, unclipped and unscaled.
        for icon in ICONS:
            with self.subTest(icon=hex(ord(icon))):
                with Shitty(
                    columns=4,
                    rows=1,
                    extra_arguments=("-fontsize", "32"),
                ) as terminal:
                    terminal.write(b"\x1b[?25l " + icon.encode() + b"  ")
                    width, height, pixels = terminal.render_image(NERD_FONT)

                cell_width = width // 4
                first = ink_margins(pixels, width, cell_width, height, 1)
                self.assertIsNotNone(first, "icon rendered no ink")
                left, cell_edge = first
                # Anchored in its own cell with clearance on the left, and
                # flowing into the captured blank without a gap.
                self.assertGreaterEqual(left, 1, f"ink flush left ({first})")
                self.assertEqual(cell_edge, 0, "ink stops short of the captured cell")
                second = ink_margins(pixels, width, cell_width, height, 2)
                self.assertIsNotNone(second, "no ink in the captured blank cell")
                spill_start, right = second
                self.assertEqual(spill_start, 0, "ink is discontinuous at the cell seam")
                self.assertGreaterEqual(right, 1, f"ink clipped at the far edge ({second})")
                # The neighbouring cells stay clean: two cells, no more.
                for neighbour in (0, 3):
                    self.assertIsNone(
                        ink_margins(pixels, width, cell_width, height, neighbour),
                        f"ink leaked into cell {neighbour}",
                    )
                # Substantial ink, not an antialiasing sliver.
                ink = (cell_width - left) + (cell_width - right)
                self.assertGreaterEqual(ink, cell_width, "icon shrank away")

    def test_icon_against_text_scales_to_fit_its_cell(self):
        # No blank to capture: the pictogram re-renders at a smaller size
        # until its ink fits the one cell it owns.
        for icon in ICONS:
            with self.subTest(icon=hex(ord(icon))):
                with Shitty(
                    columns=4,
                    rows=1,
                    extra_arguments=("-fontsize", "32"),
                ) as terminal:
                    terminal.write(b"\x1b[?25l " + icon.encode() + b"__")
                    width, height, pixels = terminal.render_image(NERD_FONT)

                cell_width = width // 4
                margins = ink_margins(pixels, width, cell_width, height, 1)
                self.assertIsNotNone(margins, "icon rendered no ink")
                left, right = margins
                self.assertGreaterEqual(left, 1, f"ink flush left ({margins})")
                self.assertGreaterEqual(right, 1, f"ink clipped right ({margins})")
                self.assertGreaterEqual(
                    cell_width - left - right, cell_width // 2, "icon shrank away"
                )
                self.assertIsNone(
                    ink_margins(pixels, width, cell_width, height, 0),
                    "ink leaked into cell 0",
                )


if __name__ == "__main__":
    unittest.main()

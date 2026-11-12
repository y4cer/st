# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class RenderContractTest(unittest.TestCase):
    def test_gpu_cell_flags_match_compute_shader_abi(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.gpu_attribute_masks(),
                (1 << 16, 1 << 17),
            )

    def test_blink_and_reverse_screen_reach_renderer(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1 q\x1b[5mX\x1b[?5h")
            state = terminal.render_state()
            self.assertTrue(state.screen_reverse)
            self.assertTrue(state.blink_visible)
            self.assertTrue(state.cursor_blink)

            terminal.blink_tick()
            self.assertFalse(terminal.render_state().blink_visible)

    def test_palette_and_selection_colors_reach_renderer(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;5;1mX"
                b"\x1b]4;1;#010203\x1b\\"
                b"\x1b]17;#0a0b0c\x1b\\"
                b"\x1b]19;#0d0e0f\x1b\\"
            )
            self.assertEqual(
                terminal.snapshot().cell(0, 0).foreground,
                (1, 2, 3),
            )
            state = terminal.render_state()
            self.assertEqual(state.selection_mask, 3)
            self.assertEqual(state.selection_background, (10, 11, 12))
            self.assertEqual(state.selection_foreground, (13, 14, 15))

            terminal.write(b"\x1b]117\x1b\\")
            self.assertEqual(terminal.render_state().selection_mask, 1)
            terminal.write(b"\x1b]119\x1b\\")
            self.assertEqual(terminal.render_state().selection_mask, 0)

    def test_grapheme_payload_reaches_renderer(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("e\N{COMBINING ACUTE ACCENT}".encode())
            state = terminal.render_state()
            self.assertEqual(state.grapheme_cells, 1)
            self.assertEqual(state.grapheme_codepoints, 2)


if __name__ == "__main__":
    unittest.main()

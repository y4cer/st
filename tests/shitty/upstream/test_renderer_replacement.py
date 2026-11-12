# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, TEST_PLATFORM


RELEASE = 0
PRESS = 1
KEY_EQUAL = 61
KEY_MINUS = 45
MOD_SHIFT = 1
MOD_CONTROL = 2
MOD_SUPER = 8

# The default bindings differ per platform: Cmd chords on macOS (which
# deliver no text event), Ctrl chords with their typed text on Linux.
if TEST_PLATFORM == "cocoa":
    FONT_INC = (KEY_EQUAL, None, MOD_SUPER)
    FONT_DEC = (KEY_MINUS, None, MOD_SUPER)
else:
    FONT_INC = (KEY_EQUAL, "+", MOD_CONTROL | MOD_SHIFT)
    FONT_DEC = (KEY_MINUS, "-", MOD_CONTROL)


class RendererReplacementTest(unittest.TestCase):
    @staticmethod
    def shortcut(terminal, key, text, modifiers):
        terminal.frontend_key_event(key, PRESS, modifiers=modifiers)
        if text is not None:
            terminal.frontend_text_event(text, modifiers=modifiers)
        terminal.frontend_key_event(key, RELEASE, modifiers=modifiers)

    def test_failed_font_replacement_preserves_visible_generation(self):
        with Shitty(
            columns=20,
            rows=4,
            glyph_px=8,
            glyph_py=16,
            extra_arguments=("-fontsize", "16"),
        ) as terminal:
            self.shortcut(terminal, *FONT_INC)
            self.shortcut(terminal, *FONT_DEC)
            terminal.write(b"before")
            before_state = terminal.font_state()
            before_frame = terminal.snapshot()

            terminal.fail_next_font_change()
            self.shortcut(terminal, FONT_INC[0], None, FONT_INC[2])

            self.assertEqual(terminal.font_state(), before_state)
            self.assertEqual(terminal.snapshot(), before_frame)
            terminal.write(b"+usable")
            self.assertIn("before+usable", terminal.snapshot().lines[0])

            self.shortcut(terminal, *FONT_INC)
            after_state = terminal.font_state()
            self.assertEqual(after_state[0], 17)
            self.assertNotEqual(after_state[1:5], before_state[1:5])

    def test_failed_output_resize_preserves_previous_frame(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"previous")
            previous = terminal.snapshot()

            terminal.fail_next_present()
            terminal.resize(5, 3)
            self.assertEqual(terminal.snapshot(), previous)

            terminal.write(b"+usable")
            resized = terminal.snapshot()
            self.assertEqual((resized.columns, resized.rows), (5, 3))
            self.assertGreater(resized.refresh_count, previous.refresh_count)

            state = terminal.font_state()
            before_unchanged = terminal.snapshot()
            terminal.resize_pixels(state[3], state[4])
            self.assertEqual(terminal.snapshot(), before_unchanged)
            terminal.write(b"+")
            self.assertGreater(
                terminal.snapshot().refresh_count,
                before_unchanged.refresh_count,
            )


if __name__ == "__main__":
    unittest.main()

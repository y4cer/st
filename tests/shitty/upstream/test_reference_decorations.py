# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Cell decorations the reference renderer paints itself: double
underlines, overlines, strikes, wrap marks and the hollow cursor."""

import unittest

from font_fixture import NERD_FONT
from harness import Shitty


def render(text, columns=None, extra_arguments=()):
    arguments = ("-fontsize", "16", *extra_arguments)
    with Shitty(columns=columns or len(text), rows=2, extra_arguments=arguments) as terminal:
        terminal.write(text.encode())
        terminal.load_font(str(NERD_FONT))
        width, height, pixels = terminal.render_image(str(NERD_FONT))
        return width, height, bytes(pixels)


def ink(image):
    width, height, pixels = image
    background = pixels[:3]
    return sum(
        max(abs(pixels[offset + at] - background[at]) for at in range(3))
        for offset in range(0, len(pixels), 3)
    )


class ReferenceDecorationTest(unittest.TestCase):
    def test_double_underline_overline_and_strike_add_ink(self):
        plain = render("\x1b[?25lab", columns=2)
        for sgr in (b"21", b"53", b"9"):
            with self.subTest(sgr=sgr):
                decorated = render("\x1b[?25l\x1b[" + sgr.decode() + "mab", columns=2)
                self.assertEqual(plain[:2], decorated[:2])
                self.assertGreater(ink(decorated), ink(plain))

    def test_wrap_marks_and_the_hollow_cursor_are_drawn(self):
        wrapped = render("\x1b[?25labcd", columns=2)
        marked = render("\x1b[?25labcd", columns=2, extra_arguments=("-showWraps",))
        self.assertGreater(ink(marked), ink(wrapped))
        with Shitty(columns=2, rows=2, extra_arguments=("-fontsize", "16")) as terminal:
            terminal.write(b"\x1b[?25h\x1b[2 qa")
            terminal.load_font(str(NERD_FONT))
            focused = bytes(terminal.render_image(str(NERD_FONT))[2])
            terminal.focus(False)
            unfocused = bytes(terminal.render_image(str(NERD_FONT))[2])
        self.assertNotEqual(focused, unfocused)


if __name__ == "__main__":
    unittest.main()

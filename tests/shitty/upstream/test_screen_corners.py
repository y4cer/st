# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Screen paths off the straight and narrow: counted scrolls inside a
margin box, a wide character sliced by the margin, hyperlink hover in
scrollback, and reflow across resizes."""

import unittest

from harness import Shitty, put_rows


PRESS = 1
CONTROL = 2
LEFT_CONTROL = 341


def fill_letters(terminal, rows):
    terminal.write(put_rows(*(
        (chr(ord("A") + row) * 10).encode()
        for row in range(rows)
    )))


class ScreenCornerTest(unittest.TestCase):
    def test_counted_scrolls_move_only_the_margin_box(self):
        with Shitty(columns=10, rows=6) as terminal:
            fill_letters(terminal, 6)
            terminal.write(b"\x1b[?69h\x1b[3;8s\x1b[2;5r\x1b[2;3H\x1b[2S")
            snapshot = terminal.snapshot()
            # The box shifted up by two; everything around it stayed.
            self.assertEqual(snapshot.lines[1], "BBDDDDDDBB")
            self.assertEqual(snapshot.lines[2], "CCEEEEEECC")
            self.assertEqual(snapshot.lines[3], "DD      DD")
            self.assertEqual(snapshot.lines[4], "EE      EE")
            self.assertEqual(snapshot.lines[0], "AAAAAAAAAA")
            self.assertEqual(snapshot.lines[5], "FFFFFFFFFF")

            terminal.write(b"\x1b[3T")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[4], "EEDDDDDDEE")
            self.assertEqual(snapshot.lines[1], "BB      BB")
            self.assertEqual(snapshot.lines[2], "CC      CC")
            self.assertEqual(snapshot.lines[3], "DD      DD")

    def test_margin_scroll_repairs_a_sliced_wide_character(self):
        with Shitty(columns=10, rows=4) as terminal:
            # The wide cell sits on columns 2-3; the left margin starts
            # at 3, so a scroll inside the box slices its continuation.
            terminal.write("\x1b[1;2H你".encode())
            self.assertTrue(terminal.snapshot().cell(1, 0).double_width)
            terminal.write(b"\x1b[?69h\x1b[3;8s\x1b[1;3r\x1b[1;3H\x1b[S")
            cell = terminal.snapshot().cell(1, 0)
            self.assertFalse(cell.double_width)
            self.assertEqual(cell.char, " ")

    def test_hyperlink_hover_resolves_in_scrollback(self):
        with Shitty(columns=16, rows=4, save_lines=50) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test\x1b\\LINK\x1b]8;;\x1b\\"
            )
            terminal.write(b"\r\n" * 8)
            target = None
            for _ in range(4):
                terminal.page_up()
                snapshot = terminal.snapshot()
                for row, line in enumerate(snapshot.lines):
                    if line.startswith("LINK"):
                        target = row
                        break
                if target is not None:
                    break
            self.assertIsNotNone(target, snapshot.lines)
            # The link lights up under a Control-held pointer.
            terminal.pointer(2 + 1, 2 + target)
            terminal.frontend_key_event(LEFT_CONTROL, PRESS, modifiers=CONTROL)
            state = terminal.desktop_state()
            self.assertNotEqual(state["hovered_hyperlink"], 0)

            # Off the link the hover clears.
            terminal.pointer(2 + 9, 2 + target, modifiers=CONTROL)
            state = terminal.desktop_state()
            self.assertEqual(state["hovered_hyperlink"], 0)

    def test_fullscreen_roundtrip_keeps_the_screen(self):
        # Issue 83's shape: content at the top, the window grows to
        # fullscreen, transient animation sizes shrink the grid on the
        # way back, and the shell repaints its prompt at the smallest
        # one. Everything above must survive the round trip.
        with Shitty(columns=20, rows=10, save_lines=50) as terminal:
            terminal.write(b"Welcome to fish\r\nType help\r\n\r\n~ prompt ")
            terminal.resize(20, 24)
            terminal.resize(20, 2)
            terminal.write(b"\r\x1b[K~ prompt again ")
            terminal.resize(20, 10)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0].rstrip(), "Welcome to fish")
            self.assertEqual(snapshot.lines[1].rstrip(), "Type help")
            self.assertEqual(snapshot.lines[3].rstrip(), "~ prompt again")

    def test_reflow_rewraps_and_rejoins_across_resizes(self):
        with Shitty(columns=12, rows=4, save_lines=50) as terminal:
            terminal.write(b"ABCDEFGHIJKLMNOPQR")
            terminal.resize(6, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0].rstrip(), "ABCDEF")
            self.assertEqual(snapshot.lines[1].rstrip(), "GHIJKL")
            self.assertEqual(snapshot.lines[2].rstrip(), "MNOPQR")

            terminal.resize(12, 4)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0].rstrip(), "ABCDEFGHIJKL")
            self.assertEqual(snapshot.lines[1].rstrip(), "MNOPQR")


if __name__ == "__main__":
    unittest.main()

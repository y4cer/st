# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def numbered_lines(count):
    return b"\r\n".join(str(line).encode() for line in range(1, count + 1))


class SelectionAutoscrollTest(unittest.TestCase):
    def test_top_edge_scrolls_to_history_limit_and_extends_selection(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=4, y=5)
            terminal.pointer(x=2, y=2)

            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.selection_autoscroll_tick()
            first = terminal.snapshot()
            self.assertEqual(first.view_offset, 1)
            self.assertEqual(first.selection, (0, 0, 2, 4))

            for expected_offset in range(2, 7):
                terminal.selection_autoscroll_tick()
                self.assertEqual(
                    terminal.snapshot().view_offset, expected_offset
                )

            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 6)
            self.assertEqual(
                terminal.button(0, False, x=2, y=2),
                numbered_lines(10).replace(b"\r", b""),
            )

    def test_bottom_edge_scrolls_to_live_screen_and_extends_selection(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.wheel_up(3)
            terminal.button(0, True, x=2, y=2)
            terminal.pointer(x=4, y=5)

            for expected_offset in (2, 1, 0):
                terminal.selection_autoscroll_tick()
                self.assertEqual(
                    terminal.snapshot().view_offset, expected_offset
                )

            terminal.selection_autoscroll_tick()
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.selection, (0, -3, 2, 3))
            self.assertEqual(
                terminal.button(0, False, x=4, y=5),
                numbered_lines(10)[9:].replace(b"\r", b""),
            )

    def test_application_mouse_protocol_does_not_autoscroll(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.wheel_up(3)
            terminal.write(b"\x1b[?1000h\x1b[?1006h")
            terminal.button(0, True, x=2, y=2)
            terminal.pointer(x=4, y=5)

            terminal.selection_autoscroll_tick()

            self.assertEqual(terminal.snapshot().view_offset, 3)
            terminal.button(0, False, x=4, y=5)

    def test_shift_override_autoscrolls_local_selection(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.wheel_up(3)
            terminal.write(b"\x1b[?1000h\x1b[?1006h")
            terminal.button(0, True, x=2, y=2, modifiers=1)
            terminal.pointer(x=4, y=5, modifiers=1)

            terminal.selection_autoscroll_tick()

            self.assertEqual(terminal.snapshot().view_offset, 2)
            self.assertEqual(terminal.read_input(), b"")
            terminal.button(0, False, x=4, y=5, modifiers=1)

    def test_alternate_drag_does_not_autoscroll_primary_after_return(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.wheel_up(3)
            terminal.select_start(0, 0)
            terminal.select_update(2, 1)
            self.assertNotEqual(terminal.select_finish(), b"")
            primary = terminal.snapshot()

            terminal.write(b"\x1b[?1049h")
            terminal.button(0, True, x=4, y=5)
            terminal.pointer(x=2, y=2)
            terminal.write(b"\x1b[?1049l")
            terminal.selection_autoscroll_tick()

            current = terminal.snapshot()
            self.assertEqual(current.view_offset, primary.view_offset)
            self.assertEqual(current.selection, primary.selection)
            self.assertEqual(terminal.read_input(), b"")

    def test_primary_drag_does_not_survive_alternate_round_trip(self):
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=4, y=5)
            terminal.pointer(x=2, y=2)
            primary = terminal.snapshot()

            terminal.write(b"\x1b[?1049h\x1b[?1049l")
            terminal.selection_autoscroll_tick()

            current = terminal.snapshot()
            self.assertEqual(current.view_offset, primary.view_offset)
            self.assertEqual(current.selection, primary.selection)
            self.assertEqual(terminal.read_input(), b"")

    def test_autoscroll_stops_when_drag_is_no_longer_active_at_edge(self):
        for event in ("away", "release", "leave", "focus-loss"):
            with self.subTest(event=event):
                with Shitty(columns=8, rows=4, save_lines=20) as terminal:
                    terminal.write(numbered_lines(10))
                    terminal.button(0, True, x=4, y=5)
                    terminal.pointer(x=2, y=2)

                    if event == "away":
                        terminal.pointer(x=2, y=3)
                    elif event == "release":
                        terminal.button(0, False, x=2, y=2)
                    elif event == "leave":
                        terminal.pointer_presence(False)
                    else:
                        terminal.focus(False)

                    terminal.selection_autoscroll_tick()

                    self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_returning_inside_stops_the_armed_autoscroll(self):
        # The drag comes back inside the content area: the pending tick
        # finds no scroll direction any more, stops the autoscroll, and
        # the view stays where the earlier ticks put it.
        with Shitty(columns=8, rows=4, save_lines=20) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=4, y=5)
            terminal.pointer(x=2, y=2)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.pointer(x=4, y=3)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 1)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 1)


    def test_autoscroll_stops_when_there_is_no_history_to_reveal(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(numbered_lines(6))
            terminal.button(0, True, x=4, y=5)
            terminal.pointer(2, 2)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)


if __name__ == "__main__":
    unittest.main()

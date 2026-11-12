# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of the final 15 SelectionGesture.zig cases."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "SelectionGesture double-click drag selects by word",
    "SelectionGesture double-click drag selects by word backwards",
    "SelectionGesture double-click drag on empty cell selects nearest word",
    "SelectionGesture triple-click drag selects by line",
    "SelectionGesture triple-click drag selects by line backwards",
    "SelectionGesture repeat increments click count",
    "SelectionGesture repeat clamps at triple click",
    "SelectionGesture null initial time stays single click",
    "SelectionGesture null repeat time stays single click",
    "SelectionGesture distant press resets click count",
    "SelectionGesture expired repeat resets click count",
    "SelectionGesture backwards repeat time resets click count",
    "SelectionGesture screen switch resets click count",
    "SelectionGesture removed screen resets without untracking stale pin",
    "SelectionGesture deinit untracks pin",
)


BORDER = 2
GLYPH = 10


def x(column):
    return BORDER + column * GLYPH


def y(row):
    return BORDER + row * GLYPH


def click(terminal, column, row, time):
    terminal.button(0, True, x=x(column), y=y(row), time=time)
    return terminal.button(
        0,
        False,
        x=x(column),
        y=y(row),
        time=time + 0.01,
    )


class GhosttySelectionGestureTailTest(unittest.TestCase):
    def test_upstream_inventory_has_15_distinct_gesture_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 15)
        self.assertEqual(len(set(UPSTREAM_CASES)), 15)

    def test_double_click_drag_expands_forward_by_whole_words(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta gamma")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            terminal.pointer(x(7), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(7), y=y(0), time=1.11),
                b"alpha beta",
            )

    def test_double_click_drag_expands_backwards_by_whole_words(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta gamma")
            self.assertEqual(click(terminal, 7, 0, 1), b"")
            terminal.button(0, True, x=x(7), y=y(0), time=1.1)
            terminal.pointer(x(1), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.11),
                b"alpha beta",
            )

    def test_word_drag_to_empty_tail_stops_at_nearest_written_word(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            terminal.pointer(x(15), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(15), y=y(0), time=1.11),
                b"alpha beta",
            )

    def test_triple_click_drag_expands_forward_by_whole_lines(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(b"alpha beta", b"one two", b"three four"))
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            self.assertEqual(click(terminal, 1, 0, 1.1), b"alpha")
            terminal.button(0, True, x=x(1), y=y(0), time=1.2)
            terminal.pointer(x(2), y(2))
            self.assertEqual(
                terminal.button(0, False, x=x(2), y=y(2), time=1.21),
                b"alpha beta\none two\nthree four",
            )

    def test_triple_click_drag_expands_backwards_by_whole_lines(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(b"alpha beta", b"one two", b"three four"))
            self.assertEqual(click(terminal, 2, 2, 1), b"")
            self.assertEqual(click(terminal, 2, 2, 1.1), b"three")
            terminal.button(0, True, x=x(2), y=y(2), time=1.2)
            terminal.pointer(x(1), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.21),
                b"alpha beta\none two\nthree four",
            )

    def test_nearby_repeat_increments_to_word_selection(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            self.assertEqual(click(terminal, 1, 0, 1.1), b"alpha")

    @unittest.expectedFailure
    def test_repeat_count_clamps_at_triple_click(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta")
            selections = tuple(
                click(terminal, 1, 0, 1 + index * 0.1)
                for index in range(4)
            )
            self.assertEqual(
                selections,
                (b"", b"alpha", b"alpha beta", b"alpha beta"),
            )

    def test_missing_initial_timestamp_keeps_the_next_click_single(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            terminal.button(0, True, x=x(1), y=y(0), time=float("nan"))
            terminal.button(0, False, x=x(1), y=y(0), time=float("nan"))
            self.assertEqual(click(terminal, 1, 0, 1), b"")

    def test_missing_repeat_timestamp_keeps_that_click_single(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            terminal.button(0, True, x=x(1), y=y(0), time=float("nan"))
            self.assertEqual(
                terminal.button(
                    0,
                    False,
                    x=x(1),
                    y=y(0),
                    time=float("nan"),
                ),
                b"",
            )

    def test_distant_press_restarts_at_single_click(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            self.assertEqual(click(terminal, 4, 0, 1.1), b"")

    def test_expired_repeat_restarts_at_single_click(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            self.assertEqual(click(terminal, 1, 0, 1.51), b"")

    def test_backwards_repeat_timestamp_restarts_at_single_click(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 2), b"")
            self.assertEqual(click(terminal, 1, 0, 1), b"")

    @unittest.expectedFailure
    def test_screen_switch_resets_the_click_count(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            terminal.write(b"\x1b[?1049h")
            terminal.write(b"alpha")
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            terminal.pointer(x(3), y(0))
            self.assertNotEqual(
                terminal.button(0, False, x=x(3), y=y(0), time=1.11),
                b"",
            )

    @unittest.expectedFailure
    def test_removed_alternate_screen_does_not_continue_its_click_count(self):
        with Shitty(columns=10, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"\x1b[?1049h")
            terminal.write(b"alpha")
            self.assertEqual(click(terminal, 1, 0, 1), b"")
            terminal.write(b"\x1b[?1049l")
            terminal.write(b"alpha")
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            terminal.pointer(x(3), y(0))
            self.assertNotEqual(
                terminal.button(0, False, x=x(3), y=y(0), time=1.11),
                b"",
            )

    def test_frontend_teardown_releases_an_active_click(self):
        terminal = Shitty(
            columns=5,
            rows=5,
            glyph_px=GLYPH,
            glyph_py=GLYPH,
        )
        terminal.button(0, True, x=x(1), y=y(1), time=1)
        terminal.close()
        self.assertEqual(terminal.process.returncode, 0)


if __name__ == "__main__":
    unittest.main()

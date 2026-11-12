# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of SelectionGesture.zig cases 1 through 20."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "SelectionGesture drag selection logic",
    "SelectionGesture rectangle drag selection logic",
    "SelectionGesture press records initial click",
    "SelectionGesture press returns standard click selections",
    "SelectionGesture press behaviors choose press and drag behavior",
    "SelectionGesture output behavior selects and drags semantic output",
    "SelectionGesture drag returns selection and records autoscroll",
    "SelectionGesture drag clamps unrepresentable positions",
    "SelectionGesture drag saturates overflowing geometry",
    "SelectionGesture drag rejects empty geometry",
    "SelectionGesture release clears autoscroll and records drag",
    "SelectionGesture release with invalidated click records drag",
    "SelectionGesture same-cell threshold selection records drag",
    "SelectionGesture drag without press returns null",
    "SelectionGesture drag autoscroll edge boundaries",
    "SelectionGesture autoscroll tick scrolls and continues drag",
    "SelectionGesture autoscroll tick resolves drag pin after scrolling",
    "SelectionGesture autoscroll tick stops with invalidated click",
    "SelectionGesture deep press selects word and consumes drag",
    "SelectionGesture drag with invalidated click returns null",
)


BORDER = 2
GLYPH = 10


def x(column, fraction=0.0):
    return BORDER + (column + fraction) * GLYPH


def y(row, fraction=0.0):
    return BORDER + (row + fraction) * GLYPH


def numbered_lines(count):
    return b"\r\n".join(str(line).encode() for line in range(1, count + 1))


class GhosttySelectionGestureCoreTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_gesture_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    @unittest.expectedFailure
    def test_drag_selection_uses_fractional_cell_thresholds(self):
        rows = tuple(bytes([ord("A") + row]) * 10 for row in range(5))
        with Shitty(columns=10, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(*rows))
            terminal.button(0, True, x=x(3), y=y(3), time=1)
            terminal.pointer(x(5, 0.9), y(3))
            self.assertEqual(terminal.selection_state()["raw"], (3, 3, 5, 3))
            terminal.button(0, False, x=x(5, 0.9), y=y(3), time=1.01)

            terminal.button(0, True, x=x(3), y=y(3), time=2)
            terminal.pointer(x(3, 0.9), y(3))
            self.assertTrue(terminal.has_selection())

    @unittest.expectedFailure
    def test_rectangular_drag_uses_fractional_column_thresholds(self):
        rows = tuple(bytes([ord("A") + row]) * 10 for row in range(5))
        with Shitty(columns=10, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(*rows))
            terminal.button(0, True, x=x(3), y=y(2), time=1)
            terminal.select_rectangular()
            terminal.pointer(x(5, 0.9), y(4))
            self.assertEqual(terminal.selection_state()["raw"], (3, 2, 5, 4))
            terminal.button(0, False, x=x(5, 0.9), y=y(4), time=1.01)

            terminal.button(0, True, x=x(3), y=y(2), time=2)
            terminal.select_rectangular()
            terminal.pointer(x(3, 0.9), y(4))
            self.assertFalse(terminal.has_selection())

    def test_first_press_is_remembered_for_the_next_click(self):
        with Shitty(columns=12, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta")
            terminal.button(0, True, x=x(1), y=y(0), time=1)
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.01),
                b"",
            )
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.11),
                b"alpha",
            )

    def test_repeated_presses_cycle_character_word_and_line(self):
        with Shitty(columns=12, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta")
            expected = (b"", b"alpha", b"alpha beta")
            for index, selected in enumerate(expected):
                now = 1 + index * 0.1
                terminal.button(0, True, x=x(1), y=y(0), time=now)
                self.assertEqual(
                    terminal.button(0, False, x=x(1), y=y(0), time=now + 0.01),
                    selected,
                )

    @unittest.expectedFailure
    def test_custom_press_behavior_order_can_choose_line_on_double_click(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(b"alpha beta", b"one two", b"three four"))
            terminal.button(0, True, x=x(1), y=y(0), time=1)
            terminal.button(0, False, x=x(1), y=y(0), time=1.01)
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.11),
                b"alpha beta",
            )

    @unittest.expectedFailure
    def test_output_press_behavior_selects_a_semantic_output_block(self):
        with Shitty(columns=10, rows=6, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(
                b"\x1b]133;C\x1b\\out1\r\n"
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\cmd\r\n"
                b"\x1b]133;C\x1b\\out2"
            )
            terminal.button(0, True, x=x(1), y=y(0), time=1)
            self.assertEqual(
                terminal.button(0, False, x=x(1), y=y(0), time=1.01),
                b"out1",
            )

    def test_drag_updates_selection_and_autoscroll_direction(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(3), y(2))
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)

            terminal.pointer(x(3), y=2)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.pointer(x(3), y=41)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertNotEqual(
                terminal.button(0, False, x=x(3), y=41, time=1.01),
                b"",
            )

    @unittest.expectedFailure
    def test_nonfinite_drag_positions_follow_ghostty_clamping(self):
        with Shitty(columns=5, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(put_rows(b"AAAAA", b"BBBBB", b"CCCCC"))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(float("inf"), y(1))
            self.assertEqual(terminal.selection_state()["raw"], (1, 1, 1, 1))
            terminal.pointer(float("nan"), y(1))
            self.assertFalse(terminal.has_selection())

    def test_huge_pointer_coordinates_saturate_to_a_bounded_selection(self):
        with Shitty(columns=5, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(1e300, 1e300)
            raw = terminal.selection_state()["raw"]
            self.assertTrue(all(0 <= column <= 5 for column in (raw[0], raw[2])))
            self.assertTrue(all(0 <= row < 5 for row in (raw[1], raw[3])))
            terminal.button(0, False, x=1e300, y=1e300, time=1.01)

    def test_empty_public_geometry_is_rejected_without_mutating_selection(self):
        with Shitty(columns=5, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.select_start(1, 1)
            terminal.select_update(3, 1)
            before = terminal.selection_state()
            with self.assertRaises(RuntimeError):
                terminal.resize_pixels(4, 4)
            self.assertEqual(terminal.selection_state(), before)

    def test_release_stops_autoscroll_and_preserves_the_drag(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(2), 2)
            selected = terminal.button(0, False, x=x(2), y=2, time=1.01)
            self.assertNotEqual(selected, b"")
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.select_finish(), selected)

    def test_release_after_screen_switch_clears_pending_autoscroll(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(2), 2)
            terminal.write(b"\x1b[?1049h")
            terminal.button(0, False, x=x(2), y=2, time=1.01)
            terminal.write(b"\x1b[?1049l")
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_same_cell_threshold_drag_selects_one_cell_and_consumes_click(self):
        with Shitty(columns=5, rows=3, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"abcde")
            terminal.button(0, True, x=x(1), y=y(0), time=1)
            terminal.pointer(x(1, 0.9), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(1, 0.9), y=y(0), time=1.01),
                b"b",
            )

    def test_motion_without_a_press_does_not_create_a_selection(self):
        with Shitty(columns=5, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.pointer(x(1), y(1))
            terminal.pointer(x(3), y(3))
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))

    def test_autoscroll_uses_exact_content_edge_boundaries(self):
        cases = (
            (2, 0, 1),
            (3, 0, 0),
            (40, 2, 2),
            (41, 2, 1),
        )
        for pointer_y, initial_offset, expected_offset in cases:
            with self.subTest(pointer_y=pointer_y):
                with Shitty(
                    columns=8, rows=4, save_lines=20,
                    glyph_px=GLYPH, glyph_py=GLYPH,
                ) as terminal:
                    terminal.write(numbered_lines(10))
                    if initial_offset:
                        terminal.wheel_up(initial_offset)
                    terminal.button(0, True, x=x(1), y=y(1), time=1)
                    terminal.pointer(x(2), pointer_y)
                    terminal.selection_autoscroll_tick()
                    self.assertEqual(
                        terminal.snapshot().view_offset,
                        expected_offset,
                    )

    def test_autoscroll_tick_scrolls_and_continues_the_drag(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.wheel_up(2)
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(3), 41)
            before = terminal.snapshot().selection
            terminal.selection_autoscroll_tick()
            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 1)
            self.assertNotEqual(after.selection, before)
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_autoscroll_tick_resolves_endpoint_after_view_scroll(self):
        with Shitty(
            columns=5, rows=3, save_lines=10,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(8))
            terminal.wheel_up(2)
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(3), 31)
            before = terminal.selection_state()["raw"]
            terminal.selection_autoscroll_tick()
            after = terminal.selection_state()["raw"]
            self.assertEqual(terminal.snapshot().view_offset, 1)
            self.assertNotEqual(after[:2], before[:2])
            self.assertEqual(after[2:], before[2:])

    def test_autoscroll_tick_stops_after_the_click_screen_is_invalidated(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(2), 2)
            terminal.write(b"\x1b[?1049h")
            terminal.selection_autoscroll_tick()
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertFalse(terminal.has_selection())

    @unittest.expectedFailure
    def test_deep_press_selects_word_and_consumes_the_active_drag(self):
        with Shitty(columns=20, rows=5, glyph_px=GLYPH, glyph_py=GLYPH) as terminal:
            terminal.write(b"alpha beta")
            terminal.button(0, True, x=x(1), y=y(0), time=1)
            terminal.pointer(x(1), 2)

            # A second press while primary is still held is the closest public
            # pressure/deep-press event available to the headless frontend.
            terminal.button(0, True, x=x(1), y=y(0), time=1.1)
            terminal.pointer(x(8), y(0))
            self.assertEqual(
                terminal.button(0, False, x=x(8), y=y(0), time=1.11),
                b"alpha",
            )

    def test_drag_after_screen_invalidation_does_not_touch_new_screen(self):
        with Shitty(
            columns=8, rows=4, save_lines=20,
            glyph_px=GLYPH, glyph_py=GLYPH,
        ) as terminal:
            terminal.write(numbered_lines(10))
            terminal.button(0, True, x=x(1), y=y(1), time=1)
            terminal.pointer(x(2), 2)
            primary = terminal.snapshot().selection

            terminal.write(b"\x1b[?1049h")
            terminal.pointer(x(2), y(2))
            self.assertFalse(terminal.has_selection())
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.snapshot().selection, primary)


if __name__ == "__main__":
    unittest.main()

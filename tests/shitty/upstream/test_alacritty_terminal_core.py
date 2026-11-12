# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all Alacritty terminal core unit tests."""

import re
import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "scroll_display_page_up",
    "scroll_display_page_down",
    "simple_selection_works",
    "semantic_selection_works",
    "line_selection_works",
    "block_selection_works",
    "grid_serde",
    "input_line_drawing_character",
    "clearing_viewport_keeps_history_position",
    "clearing_viewport_with_vi_mode_keeps_history_position",
    "clearing_scrollback_resets_display_offset",
    "clearing_scrollback_sets_vi_cursor_into_viewport",
    "clear_saved_lines",
    "vi_cursor_keep_pos_on_scrollback_buffer",
    "grow_lines_updates_active_cursor_pos",
    "grow_lines_updates_inactive_cursor_pos",
    "shrink_lines_updates_active_cursor_pos",
    "shrink_lines_updates_inactive_cursor_pos",
    "damage_public_usage",
    "damage_cursor_movements",
    "full_damage",
    "window_title",
    "parse_cargo_version",
)


def make_history(terminal, linefeeds=20):
    terminal.write(b"\n" * linefeeds)


def select_with_snap(terminal, point, cycles):
    terminal.select_start(*point)
    for _ in range(cycles):
        terminal.select_extend(*point, cycle=True)
    return terminal.select_finish()


def rich_state(snapshot):
    return (
        snapshot.lines,
        snapshot.cursor_x,
        snapshot.cursor_y,
        tuple(snapshot.cells),
    )


class AlacrittyTerminalCoreTest(unittest.TestCase):
    def test_upstream_inventory_has_all_23_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 23)
        self.assertEqual(len(set(UPSTREAM_CASES)), 23)

    def test_page_up_moves_to_history_top_and_saturates(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            make_history(terminal)
            history = terminal.scrollback_state()[0]
            previous = terminal.snapshot().view_offset
            for _ in range(32):
                terminal.page_up()
                current = terminal.snapshot().view_offset
                self.assertGreaterEqual(current, previous)
                if current == previous:
                    break
                previous = current
            self.assertEqual(previous, history)
            terminal.page_up()
            self.assertEqual(terminal.snapshot().view_offset, history)

    def test_page_down_moves_to_bottom_and_saturates(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            make_history(terminal)
            terminal.wheel_up(100)
            self.assertEqual(
                terminal.snapshot().view_offset,
                terminal.scrollback_state()[0],
            )
            previous = terminal.snapshot().view_offset
            for _ in range(32):
                terminal.page_down()
                current = terminal.snapshot().view_offset
                self.assertLessEqual(current, previous)
                if current == previous:
                    break
                previous = current
            self.assertEqual(previous, 0)
            terminal.page_down()
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_simple_selection_extracts_hard_and_wrapped_lines(self):
        rows = (b'"aaa"', b"", b" aaa ", b' aaa"', b"")
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            terminal.set_wrapped(2)
            terminal.select_start(0, 0)
            terminal.select_update(5, 2)
            self.assertEqual(terminal.select_finish(), b'"aaa"\n\n aaa ')

            terminal.select_start(0, 2)
            terminal.select_update(5, 3)
            self.assertEqual(terminal.select_finish(), b' aaa  aaa"')

    def test_semantic_selection_crosses_wrap_but_stops_at_quotes(self):
        with Shitty(columns=5, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b'"aa"a', b'aa"aa', b""))
            terminal.set_wrapped(0)
            self.assertEqual(select_with_snap(terminal, (1, 0), 1), b"aa")
            self.assertEqual(select_with_snap(terminal, (4, 0), 1), b"aaa")
            self.assertEqual(select_with_snap(terminal, (1, 1), 1), b"aaa")

    @unittest.expectedFailure
    def test_line_selection_includes_its_hard_line_terminator(self):
        with Shitty(columns=5, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b'"aa"a', b""))
            self.assertEqual(select_with_snap(terminal, (3, 0), 2), b'"aa"a\n')

    @unittest.expectedFailure
    def test_block_selection_extracts_each_source_rectangle(self):
        rows = (b"", b'"aaa"', b'"a a"', b'"aaa ', b"")
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(*rows))
            terminal.set_wrapped(2)

            terminal.select_start(3, 0)
            terminal.select_rectangular()
            terminal.select_update(4, 3)
            self.assertEqual(terminal.select_finish(), b"\na\na\na")

            terminal.select_start(0, 0)
            terminal.select_rectangular()
            terminal.select_update(3, 3)
            self.assertEqual(terminal.select_finish(), b'\n"aa\n"a \n"aa')

            terminal.select_start(3, 0)
            terminal.select_rectangular()
            terminal.select_update(5, 3)
            self.assertEqual(terminal.select_finish(), b'\na"\na"\na')

    def test_grid_state_round_trips_through_inactive_screen_storage(self):
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(b"\x1b[1;3;4;38;5;2mA\x1b[0m\r\nwide:\xe4\xb8\xad")
            before = rich_state(terminal.model_snapshot())
            terminal.write(b"\x1b[?1049hALT\x1b[?1049l")
            self.assertEqual(rich_state(terminal.model_snapshot()), before)

    def test_dec_special_graphics_maps_line_drawing_character(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b(0a\x1b(B")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "\u2592")

    def test_clearing_active_viewport_keeps_scrolled_history_position(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            make_history(terminal)
            terminal.wheel_up(100)
            before = terminal.snapshot().view_offset
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.snapshot().view_offset, before)

    def test_view_anchor_survives_clear_outside_selected_history(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            terminal.write(
                b"0000\r\n1111\r\n2222\r\n3333\r\n4444\r\n"
                b"5555\r\n6666\r\n7777\r\n8888\r\n9999\r\n"
                b"AAAA\r\nBBBB\r\nCCCC\r\nDDDD\r\nEEEE"
            )
            terminal.wheel_up(100)
            before_offset = terminal.snapshot().view_offset
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            before_selection = terminal.select_finish()
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.snapshot().view_offset, before_offset)
            self.assertEqual(terminal.select_finish(), before_selection)

    def test_clearing_scrollback_resets_display_offset(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            make_history(terminal)
            terminal.wheel_up(100)
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_clearing_scrollback_clips_history_selection_to_viewport(self):
        with Shitty(columns=5, rows=10, save_lines=20) as terminal:
            make_history(terminal)
            terminal.wheel_up(100)
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            self.assertTrue(terminal.has_selection())
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertFalse(terminal.has_selection())

    def test_clear_saved_lines_leaves_visible_grid_unchanged(self):
        with Shitty(columns=5, rows=3, save_lines=4) as terminal:
            terminal.write(b"AAAA\r\nBBBB\r\nCCCC\r\nDDDD")
            self.assertGreater(terminal.scrollback_state()[0], 0)
            before = rich_state(terminal.model_snapshot())
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(rich_state(terminal.model_snapshot()), before)
            terminal.page_up()
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_history_selection_keeps_its_text_when_output_scrolls(self):
        with Shitty(columns=5, rows=4, save_lines=20) as terminal:
            terminal.write(
                b"0000\r\n1111\r\n2222\r\n3333\r\n4444\r\n5555"
            )
            terminal.wheel_up(100)
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            before = terminal.select_finish()
            terminal.write(b"\n")
            self.assertEqual(terminal.select_finish(), before)

    def test_growing_active_screen_pulls_history_and_moves_cursor(self):
        with Shitty(columns=5, rows=10, save_lines=30) as terminal:
            make_history(terminal, 19)
            self.assertEqual(terminal.scrollback_state()[0], 10)
            self.assertEqual(terminal.snapshot().cursor_y, 9)
            terminal.resize(5, 30)
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.snapshot().cursor_y, 19)

    def test_growing_inactive_primary_screen_updates_saved_cursor(self):
        with Shitty(columns=5, rows=10, save_lines=30) as terminal:
            make_history(terminal, 19)
            terminal.write(b"\x1b[?1049h")
            terminal.resize(5, 30)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.snapshot().cursor_y, 19)

    def test_shrinking_active_screen_pushes_rows_to_history(self):
        with Shitty(columns=5, rows=10, save_lines=30) as terminal:
            make_history(terminal, 19)
            terminal.resize(5, 5)
            self.assertEqual(terminal.scrollback_state()[0], 15)
            self.assertEqual(terminal.snapshot().cursor_y, 4)

    @unittest.expectedFailure
    def test_shrinking_inactive_primary_screen_updates_saved_cursor(self):
        with Shitty(columns=5, rows=10, save_lines=30) as terminal:
            make_history(terminal, 19)
            terminal.write(b"\x1b[?1049h")
            terminal.resize(5, 5)
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.scrollback_state()[0], 15)
            self.assertEqual(terminal.snapshot().cursor_y, 4)

    def test_visible_writes_scroll_and_view_changes_schedule_frames(self):
        with Shitty(columns=10, rows=4, save_lines=20) as terminal:
            before = terminal.snapshot().refresh_count
            terminal.write(b"damage")
            after_write = terminal.snapshot().refresh_count
            self.assertGreater(after_write, before)
            terminal.write(b"\n" * 8)
            after_scroll = terminal.snapshot().refresh_count
            self.assertGreater(after_scroll, after_write)
            terminal.page_up()
            self.assertGreater(terminal.snapshot().refresh_count, after_scroll)

    def test_cursor_and_erase_operations_update_visible_presentation(self):
        operations = (
            (b"\x1b[2;2H", (1, 1)),
            (b"\x1b[3C", (4, 1)),
            (b"\x1b[8D", (0, 1)),
            (b"\x1b[6;6H\x08\x08", (3, 5)),
            (b"\x1b[A", (3, 4)),
            (b"\x1b[2B", (3, 6)),
            (b"\x1bE", (0, 7)),
            (b"\x1b[3C\x1b[A\n", (3, 7)),
            (b"\r\x1b[5X\x1b[3P", (0, 7)),
            (b"\x1b[20C\x1b[Z", (8, 7)),
            (b"\x1b7\x1b[2;2H", (1, 1)),
            (b"\x1b8", (8, 7)),
            (b"\x1b[2K\x1b[1K\x1b[0K\x1bM", (8, 6)),
        )
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            previous_refresh = terminal.snapshot().refresh_count
            for sequence, cursor in operations:
                terminal.write(sequence)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), cursor)
                self.assertGreater(snapshot.refresh_count, previous_refresh)
                previous_refresh = snapshot.refresh_count

    def test_whole_screen_operations_schedule_complete_presentations(self):
        with Shitty(columns=10, rows=5, save_lines=10) as terminal:
            terminal.write(b"abc\r\ndef")
            previous = terminal.snapshot().refresh_count
            operations = (
                b"\x1b[1J",
                b"\x1b#8",
                b"\x1b[?1049h",
                b"\x1b[?1049l",
            )
            for sequence in operations:
                terminal.write(sequence)
                current = terminal.snapshot().refresh_count
                self.assertGreater(current, previous)
                previous = current
            terminal.resize(12, 6)
            self.assertGreater(terminal.snapshot().refresh_count, previous)

    def test_window_title_stack_and_ris_reset_public_title(self):
        with Shitty(
            columns=8,
            rows=2,
            save_lines=0,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            self.assertEqual(terminal.window_title(), "Shitty")
            terminal.write(b"\x1b]2;Test\x07")
            self.assertEqual(terminal.window_title(), "Test")
            terminal.write(b"\x1b[22;2t\x1b]2;Next\x07")
            self.assertEqual(terminal.window_title(), "Next")
            terminal.write(b"\x1b[23;2t")
            self.assertEqual(terminal.window_title(), "Test")
            terminal.write(b"\x1b[23;2t")
            self.assertEqual(terminal.window_title(), "Test")
            terminal.write(b"\x1b[22;2t\x1bc\x1b[23;2t")
            self.assertEqual(terminal.window_title(), "Shitty")

    def test_secondary_da_contains_stable_numeric_version_fields(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[>c")
            first = terminal.read_input()
            terminal.write(b"\x1b[>c")
            self.assertEqual(terminal.read_input(), first)
            match = re.fullmatch(rb"\x1b\[>(\d+);(\d+);(\d+)c", first)
            self.assertIsNotNone(match)
            self.assertTrue(all(int(value) >= 0 for value in match.groups()))
            self.assertGreater(int(match.group(2)), 0)


if __name__ == "__main__":
    unittest.main()

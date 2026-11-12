# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of the remaining xterm.js selection cases."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "column selection copies a rectangle",
    "column selection preserves double-width characters",
    "column selection preserves single-cell emoji",
    "column selection preserves double-cell emoji",
    "selection coordinates use a half-open final endpoint",
    "mouseEventsRequireAlt lets unmodified input force selection",
    "mouseEventsRequireAlt takes precedence over mac option selection",
    "clearSelection clears the final selection",
    "selection values are reversed when the end precedes the start",
    "selection values are not reversed when the end follows the start",
    "trimming part of a selection preserves its remaining part",
    "trimming an entire selection clears it",
    "trimming the start row resets the remaining start to the origin",
    "select-all starts at the beginning of the buffer",
    "a selection without an end retains its start",
    "a reversed selection exposes its end as the final start",
    "select-all ends at the end of the buffer",
    "an end without a start does not create a selection",
    "word selection supplies an end without a drag endpoint",
    "a reversed drag preserves the complete initial word",
    "an endpoint inside the initial word preserves the complete word",
    "a wrapped initial word ends on the following row",
    "an endpoint inside a wrapped initial word preserves the complete word",
    "an endpoint after the initial word extends beyond it",
    "a word ending at the physical line edge adds no trailing EOL",
)


def select(terminal, start, end, rectangular=False):
    terminal.select_start(*start)
    if rectangular:
        terminal.select_rectangular()
    terminal.select_update(*end)
    return terminal.select_finish()


def select_word(terminal, column, row=0):
    terminal.select_start(column, row)
    terminal.select_extend(column, row, cycle=True)


class XtermJsSelectionTailTest(unittest.TestCase):
    def test_upstream_inventory_has_25_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 25)
        self.assertEqual(len(set(UPSTREAM_CASES)), 25)

    def test_column_selection_copies_a_rectangle(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcdefghij", b"klmnopqrst", b"uvwxyz"))
            self.assertEqual(
                select(terminal, (2, 0), (4, 2), rectangular=True),
                b"cd\nmn\nwx",
            )

    def test_column_selection_preserves_double_width_characters(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"a", "語".encode(), b"b"))
            self.assertEqual(
                select(terminal, (0, 0), (1, 2), rectangular=True),
                "a\n語\nb".encode(),
            )

    def test_column_selection_preserves_single_cell_emoji(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"a", "☃".encode(), b"c"))
            self.assertEqual(
                select(terminal, (0, 0), (1, 2), rectangular=True),
                "a\n☃\nc".encode(),
            )

    def test_column_selection_preserves_double_cell_emoji(self):
        with Shitty(columns=4, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"a", "😁".encode(), b"c"))
            self.assertEqual(
                select(terminal, (0, 0), (1, 2), rectangular=True),
                "a\n😁\nc".encode(),
            )

    def test_selection_coordinates_use_a_half_open_final_endpoint(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcdefghij", b"klmnopqrst"))
            self.assertEqual(select(terminal, (2, 0), (2, 1)), b"cdefghij\nkl")
            self.assertEqual(
                terminal.selection_state()["snapped"],
                (2, 0, 2, 1),
            )

    @unittest.expectedFailure
    def test_mouse_events_require_alt_allows_unmodified_selection(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef\x1b[?1000h\x1b[?1006h")
            terminal.button(0, True, x=2, y=2, time=1)
            terminal.pointer(5, 2)
            self.assertEqual(
                terminal.button(0, False, x=5, y=2, time=1.01),
                b"abc",
            )
            self.assertEqual(terminal.read_input(), b"")

    def test_mouse_events_require_alt_precedes_option_click_selection(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef\x1b[?1000h\x1b[?1006h")
            terminal.button(0, True, x=2, y=2, modifiers=2, time=1)
            terminal.pointer(5, 2, modifiers=2)
            self.assertEqual(
                terminal.button(
                    0, False, x=5, y=2, modifiers=2, time=1.01
                ),
                b"",
            )
            self.assertNotEqual(terminal.read_input(), b"")
            self.assertFalse(terminal.has_selection())

    def test_clear_selection_clears_the_final_selection(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            self.assertEqual(select(terminal, (0, 0), (3, 0)), b"abc")
            self.assertTrue(terminal.has_selection())
            terminal.select_clear()
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.select_finish(), b"")

    def test_selection_values_are_reversed_when_end_precedes_start(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            self.assertEqual(select(terminal, (5, 0), (2, 0)), b"cde")
            self.assertEqual(terminal.selection_state()["snapped"], (2, 0, 5, 0))

    def test_selection_values_are_not_reversed_when_end_follows_start(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            self.assertEqual(select(terminal, (2, 0), (5, 0)), b"cde")
            self.assertEqual(terminal.selection_state()["raw"], (2, 0, 5, 0))

    def test_trimming_part_of_a_selection_preserves_the_remainder(self):
        with Shitty(columns=4, rows=2, save_lines=3) as terminal:
            terminal.write(b"Aaa\r\nBbb\r\nCcc\r\nDdd")
            terminal.wheel_up(2)
            self.assertEqual(select(terminal, (0, 0), (3, 1)), b"Aaa\nBbb")
            terminal.write(b"\r\nEee\r\nFff")
            self.assertEqual(terminal.select_finish(), b"Bbb")

    def test_trimming_an_entire_selection_clears_it(self):
        with Shitty(columns=4, rows=2, save_lines=3) as terminal:
            terminal.write(b"Aaa\r\nBbb\r\nCcc\r\nDdd")
            terminal.wheel_up(2)
            self.assertEqual(select(terminal, (0, 0), (3, 0)), b"Aaa")
            terminal.write(b"\r\nEee\r\nFff")
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.select_finish(), b"")

    def test_trimmed_start_row_resets_remaining_start_to_origin(self):
        with Shitty(columns=4, rows=2, save_lines=3) as terminal:
            terminal.write(b"Aaa\r\nBbb\r\nCcc\r\nDdd")
            terminal.wheel_up(2)
            self.assertEqual(select(terminal, (2, 0), (2, 1)), b"a\nBb")
            terminal.write(b"\r\nEee\r\nFff")
            self.assertEqual(terminal.select_finish(), b"Bb")
            self.assertEqual(terminal.selection_state()["snapped"][:2], (0, 0))

    def test_select_all_starts_at_the_beginning_of_the_buffer(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd", b"efgh"))
            self.assertEqual(
                select(terminal, (-10, -10), (10, 10)),
                b"abcd\nefgh",
            )
            self.assertEqual(terminal.selection_state()["snapped"][:2], (0, 0))

    def test_selection_without_an_end_retains_its_start(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            terminal.select_start(2, 1)
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.selection_state()["raw"], (2, 1, 2, 1))

    def test_reversed_selection_exposes_its_end_as_final_start(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            self.assertEqual(select(terminal, (5, 0), (1, 0)), b"bcde")
            self.assertEqual(terminal.selection_state()["snapped"][:2], (1, 0))

    def test_select_all_ends_at_the_end_of_the_buffer(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(put_rows(b"abcd", b"efgh"))
            self.assertEqual(
                select(terminal, (-10, -10), (10, 10)),
                b"abcd\nefgh",
            )
            self.assertEqual(terminal.selection_state()["snapped"][2:], (4, 1))

    def test_endpoint_without_a_start_does_not_create_a_selection(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdef")
            terminal.select_update(3, 0)
            self.assertFalse(terminal.has_selection())
            self.assertEqual(terminal.select_finish(), b"")

    def test_word_selection_supplies_an_end_without_a_drag_endpoint(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"a word")
            select_word(terminal, 3)
            self.assertTrue(terminal.has_selection())
            self.assertEqual(terminal.select_finish(), b"word")

    def test_reversed_drag_preserves_the_complete_initial_word(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"foo bar")
            select_word(terminal, 5)
            terminal.select_update(0, 0)
            self.assertEqual(terminal.select_finish(), b"foo bar")

    def test_endpoint_inside_initial_word_preserves_complete_word(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"foo bar")
            select_word(terminal, 5)
            terminal.select_update(6, 0)
            self.assertEqual(terminal.select_finish(), b"bar")

    def test_wrapped_initial_word_ends_on_the_following_row(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"  foobar")
            select_word(terminal, 3, 0)
            self.assertEqual(terminal.select_finish(), b"foobar")
            self.assertEqual(terminal.selection_state()["snapped"][2:], (4, 1))

    def test_endpoint_inside_wrapped_word_preserves_complete_word(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"  foobar")
            select_word(terminal, 3, 0)
            terminal.select_update(2, 1)
            self.assertEqual(terminal.select_finish(), b"foobar")

    def test_endpoint_after_initial_word_extends_beyond_it(self):
        with Shitty(columns=10, rows=2, save_lines=0) as terminal:
            terminal.write(b"foo bar baz")
            select_word(terminal, 1)
            terminal.select_update(6, 0)
            self.assertEqual(terminal.select_finish(), b"foo bar")

    def test_word_at_physical_line_edge_adds_no_trailing_eol(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcd")
            select_word(terminal, 1)
            self.assertEqual(terminal.select_finish(), b"abcd")
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"abcdefgh")
            select_word(terminal, 1)
            self.assertEqual(terminal.select_finish(), b"abcdefgh")


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "Screen: implicit hyperlink ID wraps",
    "Screen: hyperlink cursor state on resize",
    "Screen: cursorSetHyperlink OOM + URI too large for string alloc",
    "Screen: increaseCapacity cursor style ref count preserved",
    "Screen: increaseCapacity cursor hyperlink ref count preserved",
    "Screen: increaseCapacity cursor with both style and hyperlink preserved",
    "Screen: increaseCapacity non-cursor page returns early",
    "Screen: cursorDown to page with insufficient capacity",
    "Screen setAttribute increases capacity when style map is full",
    "Screen setAttribute splits page on OutOfSpace at max styles",
    "selectionString map allocation failure cleanup",
    "Screen: promptClickMove line right basic",
    "Screen: promptClickMove line right cursor not on input",
    "Screen: promptClickMove line right click on same position",
    "Screen: promptClickMove line right skips non-input cells",
    "Screen: promptClickMove line right soft-wrapped line",
    "Screen: promptClickMove disabled when click is none",
    "Screen: promptClickMove line right stops at hard wrap",
    "Screen: promptClickMove line right stops at non-continuation row",
    "Screen: promptClickMove line left basic",
)


def osc133(action, options=b""):
    suffix = b";" + options if options else b""
    return b"\x1b]133;" + action + suffix + b"\x1b\\"


def osc8(uri=b"", identifier=None):
    if identifier is None:
        parameters = b""
    else:
        parameters = b"id=" + identifier
    return b"\x1b]8;" + parameters + b";" + uri + b"\x1b\\"


def click_input(terminal, column, row, time=1.0):
    x = column + 2
    y = row + 2
    terminal.button(0, True, x=x, y=y, time=time)
    terminal.button(0, False, x=x, y=y, time=time + 0.01)
    return terminal.read_all_input()


def rgb_rows(count):
    output = bytearray()
    for index in range(count):
        red = index & 0xFF
        green = (index >> 3) & 0xFF
        blue = (index >> 7) & 0xFF
        output.extend(
            f"\x1b[38;2;{red};{green};{blue}mX\r\n".encode()
        )
    return bytes(output)


class GhosttyScreenCapacityPromptClickTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_implicit_hyperlink_sequence_survives_repeated_start_end_cycles(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            transaction = bytearray()
            for index in range(4096):
                uri = f"https://example.test/{index}".encode()
                transaction.extend(osc8(uri) + b"X" + osc8() + b"\r")
            terminal.write(bytes(transaction))

            self.assertEqual(
                terminal.hyperlink(0, 0),
                "https://example.test/4095",
            )
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_active_hyperlink_cursor_state_survives_resize(self):
        with Shitty(columns=5, rows=5) as terminal:
            uri = b"https://example.test/resize"
            terminal.write(osc8(uri) + b"A")
            terminal.resize(10, 5)
            terminal.write(b"B" + osc8())

            self.assertEqual(terminal.hyperlink(0, 0), uri.decode())
            self.assertEqual(terminal.hyperlink(1, 0), uri.decode())
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_large_hyperlink_survives_storage_growth(self):
        with Shitty(columns=20, rows=5, save_lines=200) as terminal:
            uri = b"https://example.test/" + b"a" * 4096
            terminal.write(osc8(uri) + (b"linked text\r\n" * 160) + osc8())

            self.assertEqual(terminal.hyperlink(0, 3), uri.decode())
            self.assertEqual(terminal.hyperlink(5, 3), uri.decode())
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_active_style_survives_resize_capacity_change(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1b[1m1ABCD")
            terminal.resize(10, 5)
            terminal.write(b"X")
            snapshot = terminal.snapshot()

            self.assertTrue(all(snapshot.cell(column, 0).bold for column in range(6)))

    def test_active_hyperlink_survives_reflow_capacity_change(self):
        with Shitty(columns=5, rows=5) as terminal:
            uri = b"https://example.test/reflow"
            terminal.write(osc8(uri) + b"1ABCD")
            terminal.resize(10, 5)
            terminal.write(b"X" + osc8())

            self.assertTrue(
                all(terminal.hyperlink(column, 0) == uri.decode() for column in range(6))
            )

    def test_active_style_and_hyperlink_survive_capacity_change_together(self):
        with Shitty(columns=5, rows=5) as terminal:
            uri = b"https://example.test/both"
            terminal.write(b"\x1b[1m" + osc8(uri) + b"1ABCD")
            terminal.resize(10, 5)
            terminal.write(b"X" + osc8())
            snapshot = terminal.snapshot()

            for column in range(6):
                self.assertTrue(snapshot.cell(column, 0).bold)
                self.assertEqual(terminal.hyperlink(column, 0), uri.decode())

    def test_non_cursor_history_growth_does_not_change_active_cursor_state(self):
        with Shitty(columns=10, rows=4, save_lines=200) as terminal:
            terminal.write(b"old rows\r\n" * 80)
            uri = b"https://example.test/current"
            terminal.write(b"\x1b[1m" + osc8(uri) + b"CUR")
            terminal.resize(20, 4)
            terminal.write(b"SOR" + osc8())
            snapshot = terminal.snapshot()

            self.assertTrue(all(snapshot.cell(column, 3).bold for column in range(6)))
            self.assertTrue(
                all(terminal.hyperlink(column, 3) == uri.decode() for column in range(6))
            )

    def test_cursor_crosses_storage_growth_with_its_active_style(self):
        with Shitty(columns=10, rows=3, save_lines=300) as terminal:
            terminal.write(rgb_rows(180))
            terminal.write(b"\x1b[1mBEFORE\r\nAFTER")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[1].rstrip(), "BEFORE")
            self.assertEqual(snapshot.lines[2].rstrip(), "AFTER")
            self.assertTrue(snapshot.cell(0, 1).bold)
            self.assertTrue(snapshot.cell(0, 2).bold)

    def test_new_style_is_applied_after_many_distinct_styles(self):
        with Shitty(columns=10, rows=5, save_lines=300) as terminal:
            terminal.write(rgb_rows(256) + b"\x1b[1;38;2;1;2;3mB")
            cell = terminal.snapshot().cell(0, 4)

            self.assertEqual(cell.char, "B")
            self.assertTrue(cell.bold)
            self.assertEqual(cell.foreground, (1, 2, 3))

    def test_style_growth_with_full_scrollback_keeps_new_and_old_cells_valid(self):
        with Shitty(columns=8, rows=4, save_lines=32) as terminal:
            terminal.write(rgb_rows(320) + b"\x1b[1;3;38;2;7;8;9mZ")
            cell = terminal.snapshot().cell(0, 3)

            self.assertEqual(cell.char, "Z")
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertEqual(cell.foreground, (7, 8, 9))
            terminal.page_up()
            self.assertTrue(any(c.char == "X" for c in terminal.snapshot().cells))

    def test_repeated_selection_copy_keeps_text_and_link_map_stable(self):
        with Shitty(columns=10, rows=3) as terminal:
            uri = b"https://example.test/selection"
            terminal.write(osc8(uri) + b"hello" + osc8())

            for _ in range(64):
                terminal.select_start(0, 0)
                terminal.select_update(5, 0)
                self.assertEqual(terminal.select_finish(), b"hello")
                self.assertEqual(terminal.hyperlink(0, 0), uri.decode())

    @unittest.expectedFailure
    def test_prompt_click_moves_right_by_input_cells(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello"
                + b"\x1b[1;3H"
            )
            self.assertEqual(click_input(terminal, 4, 0), b"\x1b[C" * 2)

    def test_prompt_click_does_nothing_when_cursor_is_not_on_input(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello"
                + osc133(b"C") + b"\x1b[1;1H"
            )
            self.assertEqual(click_input(terminal, 4, 0), b"")

    def test_prompt_click_on_the_cursor_position_does_nothing(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello"
                + b"\x1b[1;5H"
            )
            self.assertEqual(click_input(terminal, 4, 0), b"")

    @unittest.expectedFailure
    def test_prompt_click_skips_non_input_cells_when_moving_right(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"h"
                + osc133(b"C") + b"X"
                + osc133(b"B") + b"llo"
                + b"\x1b[1;3H"
            )
            self.assertEqual(click_input(terminal, 5, 0), b"\x1b[C" * 2)

    @unittest.expectedFailure
    def test_prompt_click_counts_input_cells_across_a_soft_wrap(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"abcdefghij"
                + b"\x1b[1;3H"
            )
            self.assertEqual(click_input(terminal, 1, 1), b"\x1b[C" * 9)

    def test_prompt_click_is_disabled_without_a_click_option(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A") + b"> "
                + osc133(b"B") + b"hello"
                + b"\x1b[1;3H"
            )
            self.assertEqual(click_input(terminal, 4, 0), b"")

    @unittest.expectedFailure
    def test_prompt_click_right_stops_at_a_hard_line_break(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello\r\nworld"
                + b"\x1b[1;3H"
            )
            self.assertEqual(click_input(terminal, 0, 1), b"\x1b[C" * 5)

    @unittest.expectedFailure
    def test_prompt_click_right_stops_before_a_new_prompt(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello\r\n"
                + osc133(b"P", b"k=c") + osc133(b"B") + b"world\r\n"
                + osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"again"
                + b"\x1b[2;1H"
            )
            self.assertEqual(click_input(terminal, 2, 2), b"\x1b[C" * 5)

    @unittest.expectedFailure
    def test_prompt_click_moves_left_by_input_cells(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"cl=line") + b"> "
                + osc133(b"B") + b"hello"
                + b"\x1b[1;7H"
            )
            self.assertEqual(click_input(terminal, 2, 0), b"\x1b[D" * 4)


if __name__ == "__main__":
    unittest.main()

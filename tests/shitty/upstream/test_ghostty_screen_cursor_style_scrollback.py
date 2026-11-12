# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "Screen cursorCopy x/y",
    "Screen cursorCopy style deref",
    "Screen cursorCopy style deref new page",
    "Screen cursorCopy style copy",
    "Screen cursorCopy hyperlink deref",
    "Screen write regrows compacted page capacity",
    "Screen cursorCopy hyperlink deref new page",
    "Screen cursorCopy hyperlink copy",
    "Screen cursorCopy hyperlink copy disabled",
    "Screen style basics",
    "Screen style reset to default",
    "Screen style reset with unset",
    "Screen clearCells empty range",
    "Screen clearRows uses stored page width",
    "Screen eraseRows active partial",
    "Screen: cursorCellEndOfPrev across mixed-width pages",
    "Screen: scroll down from 0",
    "Screen: scrollback various cases",
    "Screen: scrollback with multi-row delta",
    "Screen: scrollback empty",
)


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


class GhosttyScreenCursorStyleScrollbackTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_mode_47_copies_cursor_position_to_alternate_screen(self):
        with Shitty(columns=10, rows=10, save_lines=0) as terminal:
            terminal.write(b"\x1b[4;3H\x1b[?47hHello")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[3].rstrip(), "  Hello")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 3))

    def test_cursor_copy_releases_an_obsolete_active_style(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"\x1b[?1049h\x1b[1mA"
                b"\x1b[?1049l\x1b[?47hX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.char, "X")
            self.assertFalse(cell.bold)

    def test_cursor_style_release_survives_rotated_alternate_storage(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                + b"old\r\n" * 80
                + b"\x1b[1mA"
                + b"\x1b[?1049l\x1b[?47hX"
            )
            cell = terminal.snapshot().cell(0, 0)

            self.assertEqual(cell.char, "X")
            self.assertFalse(cell.bold)

    def test_mode_47_copies_the_active_rendition(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[1;3m\x1b[?47hX")
            cell = terminal.snapshot().cell(0, 0)

            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)

    @unittest.expectedFailure
    def test_ghostty_cursor_copy_releases_an_obsolete_active_hyperlink(self):
        with Shitty(columns=10, rows=5) as terminal:
            uri = b"https://example.test/old"
            terminal.write(
                b"\x1b[?1049h" + osc8(uri) + b"A"
                b"\x1b[?1049l\x1b[?47hX"
            )

            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            self.assertEqual(terminal.hyperlink(0, 0), "")

    def test_active_hyperlink_persists_across_alternate_screen_switches(self):
        with Shitty(columns=10, rows=5) as terminal:
            uri = b"https://example.test/persistent"
            terminal.write(
                b"\x1b[?1049h" + osc8(uri) + b"A"
                b"\x1b[?1049l\x1b[?47hX"
            )

            self.assertEqual(terminal.hyperlink(0, 0), uri.decode())

    def test_first_write_populates_style_grapheme_and_hyperlink_storage(self):
        with Shitty(columns=10, rows=3) as terminal:
            uri = b"https://example.test/first"
            terminal.write(
                b"\x1b[1m" + osc8(uri) + "a\u0301".encode() + osc8()
            )
            cell = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(cell.char, "a")
            self.assertEqual(cell.grapheme, (ord("a"), 0x301))
            self.assertTrue(cell.bold)
            self.assertEqual(terminal.hyperlink(0, 0), uri.decode())

    @unittest.expectedFailure
    def test_ghostty_hyperlink_release_survives_rotated_alternate_storage(self):
        with Shitty(columns=10, rows=3) as terminal:
            uri = b"https://example.test/rotated"
            terminal.write(
                b"\x1b[?1049h"
                + b"old\r\n" * 80
                + osc8(uri) + b"A"
                + b"\x1b[?1049l\x1b[?47hX"
            )

            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            self.assertEqual(terminal.hyperlink(0, 0), "")

    def test_active_hyperlink_persists_after_rotated_alternate_storage(self):
        with Shitty(columns=10, rows=3) as terminal:
            uri = b"https://example.test/rotated-persistent"
            terminal.write(
                b"\x1b[?1049h"
                + b"old\r\n" * 80
                + osc8(uri) + b"A"
                + b"\x1b[?1049l\x1b[?47hX"
            )

            self.assertEqual(terminal.hyperlink(0, 0), uri.decode())

    def test_active_hyperlink_is_retained_across_cursor_movement(self):
        with Shitty(columns=10, rows=5) as terminal:
            uri = b"https://example.test/moved"
            terminal.write(osc8(uri) + b"\x1b[3;4HX" + osc8())

            self.assertEqual(terminal.hyperlink(3, 2), uri.decode())
            self.assertEqual(terminal.snapshot().cell(3, 2).char, "X")

    @unittest.expectedFailure
    def test_ghostty_alternate_screen_cursor_copy_does_not_copy_hyperlink(self):
        with Shitty(columns=10, rows=5) as terminal:
            uri = b"https://example.test/primary"
            terminal.write(osc8(uri) + b"A\x1b[?47hX")

            self.assertEqual(terminal.snapshot().cell(1, 0).char, "X")
            self.assertEqual(terminal.hyperlink(1, 0), "")

    def test_alternate_screen_switch_preserves_active_hyperlink(self):
        with Shitty(columns=10, rows=5) as terminal:
            uri = b"https://example.test/primary-persistent"
            terminal.write(osc8(uri) + b"A\x1b[?47hX")

            self.assertEqual(terminal.hyperlink(1, 0), uri.decode())

    def test_successive_sgr_attributes_update_the_current_style(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1mA\x1b[3mB")
            snapshot = terminal.snapshot()

            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(snapshot.cell(0, 0).italic)
            self.assertTrue(snapshot.cell(1, 0).bold)
            self.assertTrue(snapshot.cell(1, 0).italic)

    def test_selective_intensity_reset_returns_to_default_style(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1mA\x1b[22mB")
            snapshot = terminal.snapshot()

            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(snapshot.cell(1, 0).bold)
            self.assertFalse(terminal.pen_state().bold)

    def test_sgr_zero_unsets_the_current_style(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1;3;4mA\x1b[0mB")
            snapshot = terminal.snapshot()
            reset = snapshot.cell(1, 0)

            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(reset.bold)
            self.assertFalse(reset.italic)
            self.assertFalse(reset.underline)

    def test_invalid_empty_rectangle_erase_is_a_noop(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"ABCDE\x1b[2;2;1;1$z")

            self.assertEqual(terminal.snapshot().lines[0], "ABCDE")

    def test_clear_after_width_growth_clears_old_and_new_columns(self):
        with Shitty(columns=2, rows=1, save_lines=0) as terminal:
            terminal.write(b"AB")
            terminal.resize(4, 1)
            terminal.write(b"\x1b[2J")

            self.assertEqual(terminal.snapshot().lines, ["    "])

    def test_scroll_up_erases_only_the_requested_active_rows(self):
        with Shitty(columns=5, rows=5, save_lines=0) as terminal:
            terminal.write(put_rows(b"1", b"2", b"3"))
            terminal.write(b"\x1b[2S")

            self.assertEqual(visible_lines(terminal), ("3", "", "", "", ""))

    def test_reverse_wrap_finds_the_previous_row_after_width_changes(self):
        with Shitty(columns=4, rows=3, save_lines=4) as terminal:
            terminal.write(b"ABCDE")
            terminal.resize(2, 3)
            terminal.resize(4, 3)
            terminal.write(b"\x1b[?45h\x1b[2;1H\bX")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0], "ABCX")
            self.assertEqual(snapshot.lines[1].rstrip(), "E")

    def test_page_down_at_history_bottom_is_a_noop(self):
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            before = terminal.snapshot()
            terminal.page_down()
            after = terminal.snapshot()

            self.assertEqual(after.lines, before.lines)
            self.assertEqual(after.view_offset, 0)

    def test_scrollback_navigation_clamps_and_live_clear_stays_live(self):
        with Shitty(columns=10, rows=3, save_lines=4) as terminal:
            terminal.write(b"1ABCD\r\n2EFGH\r\n3IJKL\r\n4MNOP")
            self.assertEqual(visible_lines(terminal), ("2EFGH", "3IJKL", "4MNOP"))

            for _ in range(8):
                terminal.page_up()
            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))

            terminal.write(b"\x1b[2J")
            self.assertEqual(visible_lines(terminal)[0], "1ABCD")
            terminal.page_down()
            terminal.page_down()
            self.assertEqual(visible_lines(terminal), ("", "", ""))

    def test_multi_row_scrollback_delta_clamps_to_live_screen(self):
        with Shitty(columns=10, rows=3, save_lines=6) as terminal:
            terminal.write(
                b"1ABCD\r\n2EFGH\r\n3IJKL\r\n"
                b"4ABCD\r\n5EFGH\r\n6IJKL"
            )
            for _ in range(8):
                terminal.page_up()
            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))

            terminal.wheel_down(8)
            self.assertEqual(visible_lines(terminal), ("4ABCD", "5EFGH", "6IJKL"))
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_scrollback_forward_on_empty_history_is_a_noop(self):
        with Shitty(columns=10, rows=3, save_lines=50) as terminal:
            terminal.write(put_rows(b"1ABCD", b"2EFGH", b"3IJKL"))
            terminal.wheel_down(4)

            self.assertEqual(visible_lines(terminal), ("1ABCD", "2EFGH", "3IJKL"))
            self.assertEqual(terminal.snapshot().view_offset, 0)


if __name__ == "__main__":
    unittest.main()

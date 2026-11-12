# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 121 through 140."""

import re
import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "XTVERSION reports for CSI > q",
    "XTVERSION reports for CSI > 0 q",
    "XTVERSION ignores CSI > 1 q",
    "print repairs wide cells",
    "EL repairs wide cells",
    "ICH repairs wide cells",
    "DCH repairs wide cells",
    "ECH repairs wide cells",
    "default reverse-wrap cannot erase the pending-wrap cell",
    "default reverse-wrap cannot enter the preceding line",
    "reverse-wrap erases the pending-wrap cell",
    "reverse-wrap enters a soft-wrapped preceding line",
    "reverse-wrap removes the crossed soft-wrap marker",
    "reverse-wrap stops at a hard newline",
    "reverse-wrap repairs wide cells",
    "SGR 0 resets every rendition without an OSC 8 URL",
    "SGR 0 preserves the active OSC 8 URL",
    "SGR 4 and 24 toggle single underline",
    "SGR 21 and 24 toggle double underline",
    "SGR 4:1, 4:0 and 24 toggle single underline",
)


YEN = "￥".encode()
TTY_BS = b"\x08 \x08"


def trimmed_lines(terminal, count=None):
    snapshot = terminal.model_snapshot()
    row_count = snapshot.rows if count is None else min(count, snapshot.rows)
    lines = []
    for row in range(row_count):
        line = []
        for column in range(snapshot.columns):
            cell = snapshot.cell(column, row)
            if cell.double_width_continuation:
                continue
            line.append(
                "".join(chr(codepoint) for codepoint in cell.grapheme)
                if cell.grapheme else cell.char
            )
        lines.append("".join(line).rstrip())
    return lines


def assert_wide_cells_valid(test, terminal):
    snapshot = terminal.model_snapshot()
    for row in range(snapshot.rows):
        for column in range(snapshot.columns):
            cell = snapshot.cell(column, row)
            if cell.double_width:
                test.assertLess(column + 1, snapshot.columns)
                test.assertTrue(
                    snapshot.cell(column + 1, row).double_width_continuation
                )
            if cell.double_width_continuation:
                test.assertGreater(column, 0)
                test.assertTrue(snapshot.cell(column - 1, row).double_width)


def rendition(cell):
    return (
        cell.bold,
        cell.italic,
        cell.underline_style,
        cell.faint,
        cell.blink,
        cell.conceal,
        cell.strike,
        cell.overline,
        cell.inverse,
        cell.foreground,
        cell.background,
        cell.underline_color,
        cell.foreground_index,
        cell.background_index,
        cell.underline_index,
    )


class XtermJsInputHandlerWideTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def assert_xtversion(self, request):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(request)
            self.assertRegex(
                terminal.read_input(),
                re.compile(rb"^\x1bP>\|Shitty \d{4}\.\d{2}\.\d{2}\x1b\\$"),
            )

    def test_xtversion_reports_for_omitted_parameter(self):
        self.assert_xtversion(b"\x1b[>q")

    def test_xtversion_reports_for_zero_parameter(self):
        self.assert_xtversion(b"\x1b[>0q")

    def test_xtversion_ignores_nonzero_parameter(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[>1q")
            self.assertEqual(terminal.read_input(), b"")

    def wide_terminal(self):
        terminal = Shitty(columns=10, rows=5, save_lines=1)
        terminal.__enter__()
        terminal.write(YEN * 20)
        return terminal

    def test_print_repairs_every_touched_wide_cell(self):
        terminal = self.wide_terminal()
        try:
            cases = (
                (b"\x1b[H#", ["# ￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[1;6H######", ["# ￥ #####", "# ￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"#", ["# ￥ #####", "##￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"#", ["# ￥ #####", "### ￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[3;9H#", ["# ￥ #####", "### ￥￥￥", "￥￥￥￥#", "￥￥￥￥￥", ""]),
                (b"#", ["# ￥ #####", "### ￥￥￥", "￥￥￥￥##", "￥￥￥￥￥", ""]),
                (b"#", ["# ￥ #####", "### ￥￥￥", "￥￥￥￥##", "# ￥￥￥￥", ""]),
                (b"\x1b[4;10H#", ["# ￥ #####", "### ￥￥￥", "￥￥￥￥##", "# ￥￥￥ #", ""]),
            )
            for payload, expected in cases:
                terminal.write(payload)
                self.assertEqual(trimmed_lines(terminal), expected)
                assert_wide_cells_valid(self, terminal)
        finally:
            terminal.__exit__(None, None, None)

    def test_el_repairs_wide_cells_at_each_boundary(self):
        terminal = self.wide_terminal()
        try:
            for payload, expected in (
                (b"\x1b[1;6H\x1b[K#", ["￥￥ #", "￥￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[2;5H\x1b[1K", ["￥￥ #", "      ￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[3;6H\x1b[1K", ["￥￥ #", "      ￥￥", "      ￥￥", "￥￥￥￥￥", ""]),
            ):
                terminal.write(payload)
                self.assertEqual(trimmed_lines(terminal), expected)
                assert_wide_cells_valid(self, terminal)
        finally:
            terminal.__exit__(None, None, None)

    def test_ich_repairs_wide_cells_at_each_boundary(self):
        terminal = self.wide_terminal()
        try:
            for payload, expected in (
                (b"\x1b[1;6H\x1b[@", ["￥￥   ￥", "￥￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[2;4H\x1b[2@", ["￥￥   ￥", "￥    ￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[3;4H\x1b[3@", ["￥￥   ￥", "￥    ￥￥", "￥     ￥", "￥￥￥￥￥", ""]),
                (b"\x1b[4;4H\x1b[4@", ["￥￥   ￥", "￥    ￥￥", "￥     ￥", "￥      ￥", ""]),
            ):
                terminal.write(payload)
                self.assertEqual(trimmed_lines(terminal), expected)
                assert_wide_cells_valid(self, terminal)
        finally:
            terminal.__exit__(None, None, None)

    def test_dch_repairs_wide_cells_at_each_boundary(self):
        terminal = self.wide_terminal()
        try:
            for payload, expected in (
                (b"\x1b[1;6H\x1b[P", ["￥￥ ￥￥", "￥￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[2;6H\x1b[2P", ["￥￥ ￥￥", "￥￥  ￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[3;6H\x1b[3P", ["￥￥ ￥￥", "￥￥  ￥", "￥￥ ￥", "￥￥￥￥￥", ""]),
            ):
                terminal.write(payload)
                self.assertEqual(trimmed_lines(terminal), expected)
                assert_wide_cells_valid(self, terminal)
        finally:
            terminal.__exit__(None, None, None)

    def test_ech_repairs_wide_cells_at_each_boundary(self):
        terminal = self.wide_terminal()
        try:
            for payload, expected in (
                (b"\x1b[1;6H\x1b[X", ["￥￥  ￥￥", "￥￥￥￥￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[2;6H\x1b[2X", ["￥￥  ￥￥", "￥￥    ￥", "￥￥￥￥￥", "￥￥￥￥￥", ""]),
                (b"\x1b[3;6H\x1b[3X", ["￥￥  ￥￥", "￥￥    ￥", "￥￥    ￥", "￥￥￥￥￥", ""]),
            ):
                terminal.write(payload)
                self.assertEqual(trimmed_lines(terminal), expected)
                assert_wide_cells_valid(self, terminal)
        finally:
            terminal.__exit__(None, None, None)

    def test_default_reverse_wrap_cannot_erase_pending_wrap_cell(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"12345" + TTY_BS)
            self.assertEqual(terminal.model_snapshot().lines[0], "123 5")
            terminal.write(TTY_BS * 10)
            self.assertEqual(terminal.model_snapshot().lines[0], "    5")

    def test_default_reverse_wrap_cannot_enter_previous_line(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"12345" * 2 + TTY_BS)
            self.assertEqual(terminal.model_snapshot().lines[:2], ["12345", "123 5"])
            terminal.write(TTY_BS * 10)
            self.assertEqual(terminal.model_snapshot().lines[:2], ["12345", "    5"])

    def test_reverse_wrap_erases_pending_wrap_cell(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[?45h12345" + TTY_BS)
            self.assertEqual(terminal.model_snapshot().lines[0], "1234 ")
            terminal.write(TTY_BS * 7)
            self.assertEqual(terminal.model_snapshot().lines[0], "     ")

    def test_reverse_wrap_enters_soft_wrapped_previous_line(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[?45h" + b"12345" * 2 + TTY_BS)
            self.assertEqual(terminal.model_snapshot().lines[:2], ["12345", "1234 "])
            terminal.write(TTY_BS * 7)
            self.assertEqual(terminal.model_snapshot().lines[:2], ["12   ", "     "])

    def test_reverse_wrap_removes_crossed_soft_wrap_marker(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[?45h" + b"12345" * 2)
            self.assertTrue(terminal.model_snapshot().cell(4, 0).wrapped)
            terminal.write(TTY_BS * 7)
            self.assertFalse(terminal.model_snapshot().cell(4, 0).wrapped)

    def test_reverse_wrap_stops_at_hard_newline(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[?45h12345\r\n" + b"12345" * 2 + TTY_BS * 50)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[:3], ["12345", "     ", "     "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_reverse_wrap_repairs_wide_cells(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(b"\x1b[?45h" + YEN * 3)
            self.assertEqual(trimmed_lines(terminal, 2), ["￥￥", "￥"])
            expected = (
                (["￥￥", ""], 1),
                (["￥￥", ""], 0),
                (["￥", ""], 3),
                (["￥", ""], 2),
                (["", ""], 1),
                (["", ""], 0),
            )
            for lines, cursor_x in expected:
                terminal.write(TTY_BS)
                snapshot = terminal.model_snapshot()
                self.assertEqual(trimmed_lines(terminal, 2), lines)
                self.assertEqual(snapshot.cursor_x, cursor_x)
                assert_wide_cells_valid(self, terminal)

    def test_sgr_zero_resets_all_rendition_without_url(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"A\x1b[30;40;4m\x1b[mB")
            snapshot = terminal.model_snapshot()
            self.assertEqual(rendition(snapshot.cell(1, 0)), rendition(snapshot.cell(0, 0)))
            self.assertEqual(snapshot.cell(1, 0).hyperlink, 0)

    def test_sgr_zero_preserves_active_osc8_url(self):
        url = "https://example.com"
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"A\x1b[30;40;4m\x1b]8;;" + url.encode() + b"\x1b\\\x1b[mB")
            snapshot = terminal.model_snapshot()
            self.assertEqual(rendition(snapshot.cell(1, 0)), rendition(snapshot.cell(0, 0)))
            self.assertNotEqual(snapshot.cell(1, 0).hyperlink, 0)
            self.assertEqual(terminal.hyperlink(1, 0), url)

    def test_sgr_four_and_twenty_four_toggle_single_underline(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[4mA\x1b[24mB")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).underline_style, 1)
            self.assertEqual(snapshot.cell(1, 0).underline_style, 0)

    def test_sgr_twenty_one_and_twenty_four_toggle_double_underline(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[21mA\x1b[24mB")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).underline_style, 2)
            self.assertEqual(snapshot.cell(1, 0).underline_style, 0)

    def test_sgr_colon_single_and_resets_toggle_single_underline(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[4:1mA\x1b[4:0mB\x1b[4:1mC\x1b[24mD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                [snapshot.cell(column, 0).underline_style for column in range(4)],
                [1, 0, 1, 0],
            )


if __name__ == "__main__":
    unittest.main()

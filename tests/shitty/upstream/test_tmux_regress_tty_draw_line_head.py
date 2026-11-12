# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""First terminal-visible cases from current tmux tty-draw-line regress."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/tty-draw-line.sh:long-line", "test_long_line_content"),
    ("regress/tty-draw-line.sh:short-redraw", "test_short_redraw_content"),
    (
        "regress/tty-draw-line.sh:short-redraw-stale-tail",
        "test_short_redraw_clears_stale_tail",
    ),
    ("regress/tty-draw-line.sh:styled-tab-line", "test_styled_tab_line"),
    (
        "regress/tty-draw-line.sh:combining-wide-flag-line",
        "test_combining_wide_flag_line",
    ),
    ("regress/tty-draw-line.sh:same-run-spaces", "test_same_run_spaces"),
    (
        "regress/tty-draw-line.sh:styled-attributes",
        "test_styled_attributes",
    ),
    (
        "regress/tty-draw-line.sh:wide-right-edge",
        "test_wide_right_edge_content",
    ),
    (
        "regress/tty-draw-line.sh:wide-clipped-right-edge",
        "test_wide_clipped_right_edge_content",
    ),
    (
        "regress/tty-draw-line.sh:wide-clipping-stale-cell",
        "test_wide_clipping_leaves_no_stale_cell",
    ),
)


MIXED_STREAM = (
    "\x1b[31;44;1mRED\x1b[0m\tTAIL\r\n"
    "u:e\u0301:\u754c:\U0001f1fa\U0001f1f8:Z\r\n"
    "AAA      BBB"
).encode()


class TmuxRegressTtyDrawLineHeadTest(unittest.TestCase):
    def _mixed_snapshot(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(MIXED_STREAM)
            return terminal.model_snapshot()

    def test_upstream_inventory_has_10_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 10)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 10)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 10)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_long_line_content(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(b"abcdefghijklmnopqrst")
            self.assertEqual(
                terminal.snapshot().lines[0],
                "abcdefghijklmnopqrst",
            )

    def test_short_redraw_content(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\r\x1b[KXYZ")
            self.assertEqual(terminal.snapshot().lines[0].rstrip(), "XYZ")

    def test_short_redraw_clears_stale_tail(self):
        with Shitty(columns=20, rows=6) as terminal:
            terminal.write(b"abcdefghijklmnopqrst\r\x1b[KXYZ")
            cells = terminal.model_snapshot().cells[:20]
            self.assertTrue(all(not cell.drawn for cell in cells[3:]))

    def test_styled_tab_line(self):
        snapshot = self._mixed_snapshot()
        self.assertEqual(snapshot.lines[0].rstrip(), "RED     TAIL")

    def test_combining_wide_flag_line(self):
        snapshot = self._mixed_snapshot()
        self.assertEqual(snapshot.cell(2, 1).grapheme, (ord("e"), 0x0301))
        self.assertTrue(snapshot.cell(4, 1).double_width)
        self.assertEqual(
            snapshot.cell(7, 1).grapheme,
            (0x1F1FA, 0x1F1F8),
        )

    def test_same_run_spaces(self):
        snapshot = self._mixed_snapshot()
        self.assertEqual(snapshot.lines[2].rstrip(), "AAA      BBB")

    def test_styled_attributes(self):
        snapshot = self._mixed_snapshot()
        for column in range(3):
            cell = snapshot.cell(column, 0)
            self.assertTrue(cell.bold)
            self.assertEqual(cell.foreground_index, 1)
            self.assertEqual(cell.background_index, 4)

    def test_wide_right_edge_content(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write("12345678\u754cZ".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "12345678\u754c ")
            self.assertTrue(snapshot.cell(8, 0).double_width)
            self.assertTrue(snapshot.cell(9, 0).double_width_continuation)

    def test_wide_clipped_right_edge_content(self):
        with Shitty(columns=9, rows=3) as terminal:
            terminal.write("12345678\u754cZ".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "12345678 ")
            self.assertEqual(snapshot.cell(0, 1).char, "\u754c")

    def test_wide_clipping_leaves_no_stale_cell(self):
        with Shitty(columns=9, rows=3) as terminal:
            terminal.write("12345678\u754cZ".encode())
            snapshot = terminal.model_snapshot()
            self.assertFalse(snapshot.cell(8, 0).drawn)
            self.assertEqual(snapshot.cell(2, 1).char, "Z")


if __name__ == "__main__":
    unittest.main()

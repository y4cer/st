# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Remaining terminal-visible cases from current tmux tty-draw-line."""

import unittest

from harness import Shitty


PORTED_CASES = (
    (
        "regress/tty-draw-line.sh:repeated-wide-right-edge",
        "test_repeated_wide_right_edge",
    ),
    ("regress/tty-draw-line.sh:tab-initial-line", "test_tab_initial_line"),
    ("regress/tty-draw-line.sh:tab-redraw-line", "test_tab_redraw_line"),
    (
        "regress/tty-draw-line.sh:tab-redraw-stale-cell",
        "test_tab_redraw_clears_stale_cell",
    ),
    ("regress/tty-draw-line.sh:tab-clip-left", "test_tab_clip_left"),
    ("regress/tty-draw-line.sh:tab-clip-middle", "test_tab_clip_middle"),
    ("regress/tty-draw-line.sh:tab-clip-right", "test_tab_clip_right"),
    ("regress/tty-draw-line.sh:tab-clip-after", "test_tab_clip_after"),
    (
        "regress/tty-draw-line.sh:wide-horizontal-clip-four",
        "test_wide_horizontal_clip_four",
    ),
    (
        "regress/tty-draw-line.sh:wide-horizontal-clip-five",
        "test_wide_horizontal_clip_five",
    ),
    ("regress/tty-draw-line.sh:wrapped-first-row", "test_wrapped_first_row"),
    ("regress/tty-draw-line.sh:wrapped-second-row", "test_wrapped_second_row"),
    (
        "regress/tty-draw-line.sh:selected-spaces-content",
        "test_selected_spaces_content",
    ),
    (
        "regress/tty-draw-line.sh:selected-spaces-attributes",
        "test_selected_spaces_attributes",
    ),
    (
        "regress/tty-draw-line.sh:selected-short-first-row",
        "test_selected_short_first_row",
    ),
    (
        "regress/tty-draw-line.sh:selected-short-second-row",
        "test_selected_short_second_row",
    ),
    (
        "regress/tty-draw-line.sh:selected-short-attributes",
        "test_selected_short_attributes",
    ),
    ("regress/tty-draw-line.sh:acs-redraw", "test_acs_redraw"),
    (
        "regress/tty-draw-line.sh:long-same-style-run",
        "test_long_same_style_run",
    ),
    (
        "regress/tty-draw-line.sh:combining-overflow-completes",
        "test_combining_overflow_completes",
    ),
    (
        "regress/tty-draw-line.sh:combining-overflow-content",
        "test_combining_overflow_content",
    ),
)


def visible_row(snapshot, row):
    begin = row * snapshot.columns
    cells = snapshot.cells[begin:begin + snapshot.columns]
    return "".join(
        cell.char for cell in cells if not cell.double_width_continuation
    ).rstrip()


class TmuxRegressTtyDrawLineTailTest(unittest.TestCase):
    def _tab_redraw_snapshot(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"123456789Z\r123456789\x1b[X\t")
            return terminal.model_snapshot()

    def _short_line_snapshot(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                b"abcdefghijklmnopqrst\r\x1b[KXYZ\r\nnext"
            )
            return terminal.model_snapshot()

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_repeated_wide_right_edge(self):
        with Shitty(columns=9, rows=3) as terminal:
            terminal.write(("\u754c" * 5).encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(visible_row(snapshot, 0), "\u754c" * 4)
            self.assertFalse(snapshot.cell(8, 0).drawn)

    def test_tab_initial_line(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"123456789Z")
            self.assertEqual(terminal.snapshot().lines[0], "123456789Z")

    def test_tab_redraw_line(self):
        snapshot = self._tab_redraw_snapshot()
        self.assertEqual(snapshot.lines[0].rstrip(), "123456789")

    def test_tab_redraw_clears_stale_cell(self):
        snapshot = self._tab_redraw_snapshot()
        self.assertFalse(snapshot.cell(9, 0).drawn)

    def test_tab_clip_left(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"ab\t")
            self.assertEqual(terminal.snapshot().lines[0], "ab  ")

    def test_tab_clip_middle(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().lines[0], "    ")

    def test_tab_clip_right(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"\x1b[3g\x1b[3G\x1bH\r\tcd")
            self.assertEqual(terminal.snapshot().lines[0], "  cd")

    def test_tab_clip_after(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"cdef")
            self.assertEqual(terminal.snapshot().lines[0], "cdef")

    def test_wide_horizontal_clip_four(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write("ef\u754cGHIJKLMNOPQRSTUV".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                visible_row(snapshot, 0),
                "ef\u754cGHIJKLMNOPQRSTUV",
            )
            self.assertTrue(snapshot.cell(2, 0).double_width)

    def test_wide_horizontal_clip_five(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write("f\u754cGHIJKLMNOPQRSTUVW".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                visible_row(snapshot, 0),
                "f\u754cGHIJKLMNOPQRSTUVW",
            )
            self.assertTrue(snapshot.cell(1, 0).double_width)

    def test_wrapped_first_row(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"wrap-ABCDEFGHIJKLMNOZ")
            self.assertEqual(
                terminal.snapshot().lines[0],
                "wrap-ABCDEFGHIJKLMNO",
            )

    def test_wrapped_second_row(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"wrap-ABCDEFGHIJKLMNOZ")
            self.assertEqual(terminal.snapshot().lines[1].rstrip(), "Z")

    def test_selected_spaces_content(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(b"AA    BB")
            terminal.select_start(2, 0)
            terminal.select_update(5, 0)
            self.assertEqual(terminal.select_finish(), b"   ")

    def test_selected_spaces_attributes(self):
        with Shitty(
            columns=20,
            rows=4,
            glyph_px=4,
            glyph_py=8,
        ) as terminal:
            terminal.write(
                b"\x1b]17;#00aa00\x1b\\\x1b[?25lAA    BB"
            )
            terminal.select_start(2, 0)
            terminal.select_update(5, 0)
            self.assertEqual(terminal.presented_pixel(13, 6), (0, 170, 0))

    def test_selected_short_first_row(self):
        snapshot = self._short_line_snapshot()
        self.assertEqual(snapshot.lines[0].rstrip(), "XYZ")

    def test_selected_short_second_row(self):
        snapshot = self._short_line_snapshot()
        self.assertEqual(snapshot.lines[1].rstrip(), "next")

    def test_selected_short_attributes(self):
        with Shitty(
            columns=20,
            rows=4,
            glyph_px=4,
            glyph_py=8,
        ) as terminal:
            terminal.write(
                b"\x1b]17;#00aa00\x1b\\\x1b[?25l"
                b"abcdefghijklmnopqrst\r\x1b[KXYZ\r\nnext"
            )
            terminal.select_start(0, 0)
            terminal.select_update(0, 1)
            self.assertEqual(terminal.presented_pixel(73, 6), (0, 170, 0))

    def test_acs_redraw(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b(0x\x1b(B")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "\u2502")

    def test_long_same_style_run(self):
        with Shitty(columns=1100, rows=2) as terminal:
            terminal.write(b"a" * 1100)
            self.assertEqual(len(terminal.snapshot().lines[0].rstrip()), 1100)

    def test_combining_overflow_completes(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(("u" + "\u0325" * 16).encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 1)
            self.assertFalse(any(cell.drawn for cell in snapshot.cells[1:20]))

    def test_combining_overflow_content(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(("u" + "\u0325" * 16).encode())
            grapheme = terminal.model_snapshot().cell(0, 0).grapheme
            self.assertEqual(grapheme, (ord("u"),) + (0x0325,) * 16)


if __name__ == "__main__":
    unittest.main()

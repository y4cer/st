# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class PreeditTest(unittest.TestCase):
    def test_preview_overlays_the_cursor_row(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ab")
            terminal.preedit("ni", 0, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:4], "abni")
            self.assertTrue(snapshot.cell(2, 0).inverse)
            self.assertTrue(snapshot.cell(3, 0).inverse)
            terminal.preedit("")
            self.assertEqual(terminal.snapshot().lines[0][:4], "ab  ")

    def test_preview_outside_cursor_range_is_underlined(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.preedit("abc", -1, -1)
            snapshot = terminal.snapshot()
            self.assertTrue(snapshot.cell(0, 0).underline)
            self.assertFalse(snapshot.cell(0, 0).inverse)

    def test_preview_hides_the_regular_cursor_and_anchors_it(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ab")
            terminal.preedit("xy", 2, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_style, 0)
            self.assertEqual(snapshot.cursor_x, 4)
            self.assertEqual(snapshot.cursor_y, 0)

    def test_preview_never_reaches_the_model_or_the_pty(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ab")
            terminal.preedit("XYZ", -1, -1)
            self.assertEqual(terminal.all_text()[0], "ab")
            self.assertEqual(terminal.read_input(), b"")

    def test_wide_preview_shifts_left_at_the_right_edge(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"\x1b[1;5H")
            terminal.preedit("漢字", -1, -1)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 0).char, "漢")
            self.assertEqual(snapshot.cell(4, 0).char, "字")

    def test_oversized_preview_keeps_the_tail_visible(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.preedit("abcdef", -1, -1)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "cdef")

    def test_a_combining_mark_extends_the_preview_cell(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ab")
            terminal.preedit("e\u0301", -1, -1)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:4], "abe ")
            state = terminal.render_state()
            self.assertEqual(state.grapheme_cells, 1)
            self.assertEqual(state.grapheme_codepoints, 2)

    def test_a_variation_selector_widens_the_preview_cluster(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.preedit("\u2764\ufe0f", -1, -1)
            snapshot = terminal.snapshot()
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(terminal.render_state().grapheme_codepoints, 2)

    def test_a_joined_emoji_keeps_one_preview_cluster(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.preedit("\U0001f469\u200d\U0001f4bb", -1, -1)
            snapshot = terminal.snapshot()
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertEqual(snapshot.cell(2, 0).char, " ")
            self.assertEqual(terminal.render_state().grapheme_codepoints, 3)

    def test_a_lone_joiner_leaves_no_preview(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ab")
            terminal.preedit("\u200d", -1, -1)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:3], "ab ")
            self.assertEqual(snapshot.cursor_style, 1)

    def test_the_cursor_anchor_counts_cluster_cells(self):
        with Shitty(columns=10, rows=3) as terminal:
            # Three bytes in: past "e" and its combining acute, which
            # share one cell.
            terminal.preedit("e\u0301x", 3, 3)
            self.assertEqual(terminal.snapshot().cursor_x, 1)

    def test_the_preview_clusters_like_printed_text(self):
        def observe(terminal):
            snapshot = terminal.snapshot()
            state = terminal.render_state()
            return (
                snapshot.lines[0],
                [
                    (cell.char, cell.double_width, cell.double_width_continuation)
                    for cell in snapshot.cells[: snapshot.columns]
                ],
                state.grapheme_cells,
                state.grapheme_codepoints,
            )

        for text in (
            "e\u0301",
            "\u2764\ufe0f",
            "\U0001f469\u200d\U0001f4bb",
            "\u1100\u1161",
            "ab\u0301",
        ):
            with self.subTest(text=text):
                with Shitty(columns=10, rows=3) as terminal:
                    terminal.preedit(text, -1, -1)
                    preview = observe(terminal)
                with Shitty(columns=10, rows=3) as terminal:
                    terminal.write(text.encode())
                    printed = observe(terminal)
                self.assertEqual(preview, printed)

    def test_a_preview_cluster_outlives_a_grapheme_collection(self):
        # The preview references the shared extras store like any other
        # cell: a collection that did not walk it would leave the cluster
        # bound to whatever took the slot.
        with Shitty(columns=10, rows=3, save_lines=0) as terminal:
            terminal.preedit("e\u0301\u0302\u0303", -1, -1)
            self.assertEqual(terminal.render_state().grapheme_codepoints, 4)
            for _ in range(40):
                terminal.write(b"\x1b[H" + "a\u0301b\u0301c\u0301d\u0301e\u0301".encode())
                terminal.snapshot()
            terminal.write(b"\x1b[2J\x1b[H")
            terminal.snapshot()
            state = terminal.render_state()
            self.assertEqual(state.grapheme_cells, 1)
            self.assertEqual(state.grapheme_codepoints, 4)


if __name__ == "__main__":
    unittest.main()

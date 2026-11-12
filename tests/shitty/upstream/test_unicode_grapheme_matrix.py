# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest
from pathlib import Path

from harness import Shitty


ROOT = Path(__file__).resolve().parents[1]
GRAPHEME_BREAK_TEST = (
    ROOT / "ext" / "unicode" / "GraphemeBreakTest-17.0.0.txt"
)


def official_vectors():
    for line_number, line in enumerate(
        GRAPHEME_BREAK_TEST.read_text().splitlines(), 1
    ):
        vector = line.split("#", 1)[0].strip()
        if vector:
            yield line_number, vector


def parse_vector(vector):
    fields = vector.split()
    codepoints = tuple(int(value, 16) for value in fields[1::2])
    boundaries = tuple(value == "÷" for value in fields[0::2][:-1])
    return codepoints, boundaries


class UnicodeGraphemeMatrixTest(unittest.TestCase):
    def test_unicode_17_official_grapheme_break_vectors(self):
        with Shitty(columns=8, rows=2) as terminal:
            for line_number, vector in official_vectors():
                with self.subTest(line=line_number, vector=vector):
                    codepoints, expected = parse_vector(vector)
                    self.assertEqual(
                        terminal.grapheme_breaks(*codepoints), expected
                    )

    def test_prepend_spacing_mark_and_indic_linker_are_wide_clusters(self):
        samples = ("\u06ddA", "कः", "क्ष")
        for sample in samples:
            with self.subTest(sample=sample):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write((sample + "X").encode())
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.cursor_x, 3)
                    self.assertTrue(snapshot.cell(0, 0).double_width)
                    self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
                    terminal.select_start(0, 0)
                    terminal.select_update(2, 0)
                    self.assertEqual(terminal.select_finish(), sample.encode())

    def test_ascii_run_preserves_prepend_across_input_chunks(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write("\u06dd".encode())
            terminal.write(b"ASCII")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 6)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            terminal.select_start(0, 0)
            terminal.select_update(2, 0)
            self.assertEqual(terminal.select_finish(), "\u06ddA".encode())

    def test_regional_indicators_pair_by_parity(self):
        flags = "🇦🇧🇨🇩"
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write((flags + "X").encode())
            self.assertEqual(terminal.snapshot().cursor_x, 5)
            terminal.select_start(0, 0)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), "🇦🇧".encode())

    def test_keycap_cluster_remains_atomic(self):
        sample, width = "#️⃣", 2
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write((sample + "X").encode())
            self.assertEqual(terminal.snapshot().cursor_x, width + 1)
            terminal.select_start(0, 0)
            terminal.select_update(width, 0)
            self.assertEqual(terminal.select_finish(), sample.encode())

    def test_orphan_extenders_do_not_advance_and_yield_to_text(self):
        # A cluster of extenders with no base holds its cell without
        # moving the cursor, and the next printable character replaces
        # it - the tmux and xterm.js reading of a leading combining mark.
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write("\u0308\u0300".encode())
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cursor_x, 1)
            self.assertEqual(snapshot.lines[0][0], "X")

    def test_cluster_at_right_edge_wraps_as_one_unit(self):
        cluster = "क्ष"
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(("ab" + cluster + "X").encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ab ")
            self.assertEqual(snapshot.lines[1], "क X")
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)
            terminal.select_start(0, 1)
            terminal.select_update(2, 1)
            self.assertEqual(terminal.select_finish(), cluster.encode())

    def test_variation_width_changes_at_right_edge(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write("ab#️X".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ab ")
            self.assertEqual(snapshot.lines[1], "# X")
            self.assertTrue(snapshot.cell(0, 1).double_width)

        with Shitty(columns=3, rows=2) as terminal:
            terminal.write("a⌚︎X".encode())
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "a⌚X")
            self.assertFalse(snapshot.cell(1, 0).double_width)


if __name__ == "__main__":
    unittest.main()

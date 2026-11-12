# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class SelectionEditingTest(unittest.TestCase):
    def test_erase_overlapping_linear_selection_clears_it(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcdefgh")
            terminal.select_start(2, 0)
            terminal.select_update(6, 0)
            terminal.write(b"\x1b[1;4H\x1b[2X")
            self.assertEqual(terminal.snapshot().selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

    def test_disjoint_erase_keeps_linear_selection(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcdefgh")
            terminal.select_start(1, 0)
            terminal.select_update(3, 0)
            terminal.write(b"\x1b[1;6H\x1b[2X")
            self.assertEqual(terminal.select_finish(), b"bc")

    def test_insert_or_delete_before_selection_invalidates_moved_text(self):
        for edit in (b"\x1b[@", b"\x1b[P"):
            with self.subTest(edit=edit):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(b"abcdefgh")
                    terminal.select_start(3, 0)
                    terminal.select_update(6, 0)
                    terminal.write(b"\x1b[1;2H" + edit)
                    self.assertEqual(terminal.select_finish(), b"")

    def test_edit_after_selection_keeps_unchanged_text(self):
        for edit in (b"\x1b[@", b"\x1b[P", b"\x1b[2X"):
            with self.subTest(edit=edit):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(b"abcdefgh")
                    terminal.select_start(0, 0)
                    terminal.select_update(2, 0)
                    terminal.write(b"\x1b[1;6H" + edit)
                    self.assertEqual(terminal.select_finish(), b"ab")

    def test_rectangular_selection_ignores_edits_outside_its_columns(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(put_rows(b"abcdefgh", b"ijklmnop", b"qrstuvwx"))
            terminal.select_start(1, 0)
            terminal.select_rectangular()
            terminal.select_update(4, 2)
            terminal.write(b"\x1b[2;6H\x1b[2X")
            self.assertEqual(terminal.select_finish(), b"bcd\njkl\nrst")

    def test_rectangular_selection_is_cleared_by_overlapping_edit(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(put_rows(b"abcdefgh", b"ijklmnop", b"qrstuvwx"))
            terminal.select_start(1, 0)
            terminal.select_rectangular()
            terminal.select_update(4, 2)
            terminal.write(b"\x1b[2;3H\x1b[X")
            self.assertEqual(terminal.select_finish(), b"")

    def test_rectangular_selection_cleared_by_row_rotation(self):
        # IL/DL rotate whole rows under the selection; the invalidation
        # must span the full row width, not a zero-width strip.
        for edit in (b"\x1b[L", b"\x1b[M"):
            with self.subTest(edit=edit):
                with Shitty(columns=8, rows=3) as terminal:
                    terminal.write(put_rows(b"abcdefgh", b"ijklmnop", b"qrstuvwx"))
                    terminal.select_start(1, 1)
                    terminal.select_rectangular()
                    terminal.select_update(4, 2)
                    terminal.write(b"\x1b[1;1H" + edit)
                    self.assertEqual(terminal.select_finish(), b"")

    def test_alignment_pattern_clears_selection(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"abcdefgh")
            terminal.select_start(1, 0)
            terminal.select_update(4, 0)
            terminal.write(b"\x1b#8")
            self.assertEqual(terminal.select_finish(), b"")

    def test_copy_rectangle_does_not_transplant_wrap_state(self):
        with Shitty(columns=4, rows=4) as terminal:
            terminal.write(b"aaaabbbb")
            terminal.write(b"\x1b[3;1Hcccc\x1b[4;1Hdddd")
            # DECCRA rows 1-2 → rows 3-4: the copied cells must not carry
            # the source rows' soft-wrap join into the target rows.
            terminal.write(b"\x1b[1;1;2;4;1;3;1;1;1$v")
            terminal.select_start(0, 2)
            terminal.select_update(4, 3)
            self.assertEqual(terminal.select_finish(), b"aaaa\nbbbb")

    def test_noop_selective_erase_keeps_protected_selection(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1\"qABC\x1b[0\"q")
            terminal.select_start(0, 0)
            terminal.select_update(3, 0)
            terminal.write(b"\x1b[1;1H\x1b[?2K")
            self.assertEqual(terminal.select_finish(), b"ABC")


    ROWS = (
        b"abcdefghij", b"klmnopqrst", b"uvwxyz0123",
        b"4567890ABC", b"DEFGHIJKLM", b"NOPQRSTUVW",
    )

    def test_edits_touching_a_held_selection_drop_it(self):
        # Every cell mutator invalidates an overlapping selection; edits
        # elsewhere keep it, and scrolls carry it along.
        cleared = (-1, -1, -1, -1)
        cases = {
            "double height": (b"\x1b[2;1H\x1b#6", cleared),
            "double height elsewhere": (b"\x1b[5;1H\x1b#6", (1, 1, 4, 2)),
            "wrap flag": (b"\x1b[2;10HZZ", cleared),
            "ascii run": (b"\x1b[2;2HXYZ", cleared),
            "ascii run elsewhere": (b"\x1b[5;2HXYZ", (1, 1, 4, 2)),
            "single cell": ("\x1b[2;2Hé".encode(), cleared),
            "wide cell": ("\x1b[2;2H日".encode(), cleared),
            "insert mode": (b"\x1b[4h\x1b[2;2HXY\x1b[4l", cleared),
            "DECFRA": (b"\x1b[65;2;2;3;5$x", cleared),
            "DECCRA": (b"\x1b[1;1;1;3;1;2;2;1$v", cleared),
            "DECCARA": (b"\x1b[2;2;3;5;1$r", cleared),
            "DECSERA": (b"\x1b[2;2;3;5${", cleared),
            "ECH": (b"\x1b[2;2H\x1b[3X", cleared),
            "EL": (b"\x1b[2;2H\x1b[K", cleared),
            "EL whole row": (b"\x1b[2;1H\x1b[2K", cleared),
            "ED": (b"\x1b[3;1H\x1b[J", cleared),
            "DECSEL": (b"\x1b[2;2H\x1b[?K", cleared),
            "DECSED": (b"\x1b[2;1H\x1b[?J", cleared),
            "ICH": (b"\x1b[2;2H\x1b[2@", cleared),
            "DCH": (b"\x1b[2;2H\x1b[2P", cleared),
            "IL": (b"\x1b[1;1H\x1b[L", cleared),
            "DL": (b"\x1b[1;1H\x1b[M", cleared),
            "IL below": (b"\x1b[5;1H\x1b[L", (1, 1, 4, 2)),
            "SU": (b"\x1b[S", (1, 0, 4, 1)),
            "SD": (b"\x1b[T", (1, 2, 4, 3)),
            "region around": (b"\x1b[1;4r\x1b[S", (1, 0, 4, 1)),
            "region straddled": (b"\x1b[2;4r\x1b[S", cleared),
            "region below": (b"\x1b[4;6r\x1b[S", (1, 1, 4, 2)),
            "margin index": (b"\x1b[?69h\x1b[2;7s\x1b[1;4r\x1b[4;3H\n", cleared),
            "margin SU": (b"\x1b[?69h\x1b[2;7s\x1b[1;4r\x1b[S", cleared),
            "margin SD": (b"\x1b[?69h\x1b[2;7s\x1b[1;4r\x1b[T", cleared),
            "margin IL": (b"\x1b[?69h\x1b[2;7s\x1b[2;3H\x1b[L", cleared),
            "REP with link": (
                b"\x1b[2;2H\x1b]8;;http://x.test/\x1b\\a\x1b[3b\x1b]8;;\x1b\\",
                cleared,
            ),
            "wide overwrite tail": ("\x1b[2;2H日本\x1b[2;3HQ".encode(), cleared),
            "wide overwrite head": ("\x1b[2;2H日本\x1b[2;2HQ".encode(), cleared),
            "line feed at bottom": (b"\x1b[6;1H\n", (1, 0, 4, 1)),
        }
        for name, (sequence, expected) in cases.items():
            with self.subTest(edit=name):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(put_rows(*self.ROWS))
                    terminal.select_start(1, 1)
                    terminal.select_update(4, 2)
                    terminal.write(sequence)
                    self.assertEqual(terminal.snapshot().selection, expected)
        for name in ("DECFRA", "double height", "ICH"):
            with self.subTest(edit=name, rectangular=True):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(put_rows(*self.ROWS))
                    terminal.select_start(1, 1)
                    terminal.select_rectangular()
                    terminal.select_update(4, 2)
                    terminal.write(cases[name][0])
                    self.assertEqual(terminal.snapshot().selection, cleared)
        with self.subTest(edit="SU", rectangular=True):
            with Shitty(columns=10, rows=6) as terminal:
                terminal.write(put_rows(*self.ROWS))
                terminal.select_start(1, 1)
                terminal.select_rectangular()
                terminal.select_update(4, 2)
                terminal.write(b"\x1b[S")
                self.assertEqual(terminal.snapshot().selection, (1, 0, 4, 1))

    def test_alternate_screen_resize_moves_or_drops_the_selection(self):
        cleared = (-1, -1, -1, -1)
        cases = (
            ((1, 1, 4, 2), (10, 4), cleared),
            ((1, 4, 4, 5), (10, 4), (1, 2, 4, 3)),
            ((1, 1, 4, 5), (10, 4), cleared),
            ((1, 1, 4, 2), (12, 8), (1, 1, 4, 2)),
        )
        for selection, geometry, expected in cases:
            with self.subTest(selection=selection, geometry=geometry):
                with Shitty(columns=10, rows=6) as terminal:
                    terminal.write(b"\x1b[?1049h" + put_rows(*self.ROWS))
                    terminal.select_start(selection[0], selection[1])
                    terminal.select_update(selection[2], selection[3])
                    terminal.resize(*geometry)
                    self.assertEqual(terminal.snapshot().selection, expected)

    def test_reflow_carries_the_selection_through_history(self):
        with Shitty(columns=10, rows=6, save_lines=10) as terminal:
            terminal.write(b"x" * 25 + b"\r\n" + put_rows(*self.ROWS))
            terminal.select_start(2, 0)
            terminal.select_update(4, 1)
            terminal.resize(6, 6)
            self.assertEqual(terminal.snapshot().selection, (2, -6, 4, -4))
            terminal.resize(30, 6)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.selection, (2, 0, 4, 1))
            self.assertEqual(snapshot.lines[0].rstrip(), "abcdefghij")


if __name__ == "__main__":
    unittest.main()

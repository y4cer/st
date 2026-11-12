# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Cursor/editing streams from current tmux regress tests."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/input-cursor.sh:cursor", "test_cursor_relative_and_absolute"),
    ("regress/input-cursor.sh:saverc", "test_dec_save_restore_cursor"),
    ("regress/input-cursor.sh:hvp", "test_vertical_horizontal_position"),
    ("regress/input-cursor.sh:cursorlines", "test_cursor_line_movements"),
    ("regress/input-cursor.sh:tabs", "test_default_horizontal_tab"),
    ("regress/input-cursor.sh:tabclear", "test_set_and_clear_all_tab_stops"),
    ("regress/input-cursor.sh:cbt", "test_cursor_backward_tab"),
    ("regress/input-edit.sh:dch", "test_delete_characters"),
    ("regress/input-edit.sh:ich", "test_insert_characters"),
    ("regress/input-edit.sh:erase", "test_erase_to_end_of_line"),
    ("regress/input-edit.sh:el1", "test_erase_from_start_of_line"),
    ("regress/input-edit.sh:ech", "test_erase_characters"),
    ("regress/input-edit.sh:irm", "test_insert_replacement_mode"),
    ("regress/input-scroll.sh:wrap", "test_delayed_autowrap"),
)


class TmuxRegressCursorEditTest(unittest.TestCase):
    def _run_stream(
        self,
        columns,
        rows,
        payload,
        expected_lines,
        *,
        cursor=None,
    ):
        # tmux's start_pane emits these printf strings through a normal PTY;
        # its ONLCR output processing turns each source LF into CR LF before
        # the terminal parser sees it.
        with Shitty(columns=columns, rows=rows) as terminal:
            terminal.write(payload.replace(b"\n", b"\r\n"))
            snapshot = terminal.snapshot()
            expected = [line.ljust(columns) for line in expected_lines]
            expected.extend([" " * columns] * (rows - len(expected)))
            self.assertEqual(snapshot.lines, expected)
            if cursor is not None:
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y), cursor
                )
            return snapshot

    def test_upstream_inventory_has_14_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 14)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 14)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 14)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_cursor_relative_and_absolute(self):
        self._run_stream(
            10,
            3,
            b"ABCDE\r\x1b[2Cxy\x1b[1D!\x1b[4GZ\n",
            ["ABxZE"],
            cursor=(0, 1),
        )

    def test_dec_save_restore_cursor(self):
        self._run_stream(
            10,
            3,
            b"abc\x1b7\x1b[2;5HXY\x1b8Z\n",
            ["abcZ", "    XY"],
            cursor=(0, 1),
        )

    def test_vertical_horizontal_position(self):
        self._run_stream(
            10,
            4,
            b"A\x1b[3dB\x1b[5GC\x1b[2;2fD\n",
            ["A", " D", " B  C"],
            cursor=(0, 2),
        )

    def test_cursor_line_movements(self):
        self._run_stream(
            8,
            4,
            b"A\x1b[2BB\x1b[1FC\x1b[1AD\n",
            ["AD", "C", " B"],
            cursor=(0, 1),
        )

    def test_default_horizontal_tab(self):
        self._run_stream(
            12,
            3,
            b"a\tb\n",
            ["a       b"],
            cursor=(0, 1),
        )

    def test_set_and_clear_all_tab_stops(self):
        self._run_stream(
            12,
            3,
            b"\x1bH\ta\x1b[3g\r\tb\n",
            ["        a  b"],
            cursor=(0, 1),
        )

    def test_cursor_backward_tab(self):
        self._run_stream(
            16,
            3,
            b"0123456789\r\x1b[10C\x1b[Zx\n",
            ["01234567x9"],
            cursor=(0, 1),
        )

    def test_delete_characters(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[3C\x1b[2PXY\n",
            ["abcXY"],
        )

    def test_insert_characters(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[3C\x1b[2@XY\n",
            ["abcXYdef"],
        )

    def test_erase_to_end_of_line(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[3C\x1b[KZ\n",
            ["abcZ"],
        )

    def test_erase_from_start_of_line(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[3C\x1b[1KZ\n",
            ["   Zef"],
        )

    def test_erase_characters(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[3C\x1b[2XX\n",
            ["abcX f"],
        )

    def test_insert_replacement_mode(self):
        self._run_stream(
            10,
            3,
            b"abcdef\r\x1b[4h\x1b[3CXY\x1b[4lZ\n",
            ["abcXYZef"],
        )

    def test_delayed_autowrap(self):
        snapshot = self._run_stream(
            5,
            3,
            b"abcdeF",
            ["abcde", "F"],
            cursor=(1, 1),
        )
        self.assertTrue(snapshot.cell(4, 0).wrapped)
        self.assertFalse(snapshot.cell(0, 1).wrapped)


if __name__ == "__main__":
    unittest.main()

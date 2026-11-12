# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class SelectionWrappedLinesTest(unittest.TestCase):
    def test_soft_wrapped_rows_copy_as_one_logical_line(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"abcdefghij")
            terminal.select_start(1, 0)
            terminal.select_update(1, 2)
            self.assertEqual(terminal.select_finish(), b"bcdefghi")

    def test_hard_line_break_is_preserved_between_selected_rows(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"abc\r\ndef")
            terminal.select_start(1, 0)
            terminal.select_update(2, 1)
            self.assertEqual(terminal.select_finish(), b"bc\nde")

    def test_wide_character_pre_wrap_does_not_copy_placeholder_space(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write("abc界d".encode())
            terminal.select_start(0, 0)
            terminal.select_update(3, 1)
            self.assertEqual(terminal.select_finish(), "abc界d".encode())

    def test_reverse_drag_across_wrapped_rows_has_same_text(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"abcdefghij")
            terminal.select_start(1, 2)
            terminal.select_update(1, 0)
            self.assertEqual(terminal.select_finish(), b"bcdefghi")

    def test_wrapped_selection_crosses_history_and_live_screen(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(b"abcdefghijkl")
            terminal.page_up()
            terminal.select_start(0, 0)
            terminal.select_update(4, 1)
            self.assertEqual(terminal.select_finish(), b"abcdefgh")


if __name__ == "__main__":
    unittest.main()

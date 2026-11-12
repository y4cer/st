# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


PROMPT = 1
PROMPT_CONTINUATION = 2

CLICK_NONE = 0
CLICK_ABSOLUTE = 1
CLICK_RELATIVE = 2
CLICK_LINE = 3
CLICK_MULTIPLE = 4
CLICK_CONSERVATIVE_VERTICAL = 5


def osc133(action, options=b""):
    return b"\x1b]133;" + action + (b";" + options if options else b"") + b"\x1b\\"


class GhosttySemanticPromptTest(unittest.TestCase):
    def test_semantic_prompt(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"A") + b"hello"
                + osc133(b"I") + b"\r\nworld"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(4, 0).semantic, 1)
            self.assertEqual(terminal.row_semantic(0), PROMPT)
            self.assertEqual(snapshot.cell(4, 1).semantic, 0)
            self.assertEqual(terminal.row_semantic(1), 0)

    def test_semantic_prompt_continuations(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"A") + b"hello\r\n"
                + osc133(b"P", b"k=c") + b"world"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(4, 0).semantic, 1)
            self.assertEqual(terminal.row_semantic(0), PROMPT)
            self.assertEqual(snapshot.cell(4, 1).semantic, 1)
            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )

    def test_index_in_prompt_mode_marks_continuation(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"P") + b"hello\r\nX")
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.row_semantic(0), PROMPT)
            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )
            self.assertEqual(snapshot.cell(0, 1).semantic, 1)

    def test_index_in_input_mode_marks_continuation(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"P") + b"$ "
                + osc133(b"B") + b"echo \\\r\nX"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )
            self.assertEqual(snapshot.cell(0, 1).semantic, 2)

    def test_index_in_output_mode_does_not_mark_prompt(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"P") + b"$ "
                + osc133(b"B") + b"ls"
                + osc133(b"C") + b"\r\nX"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.row_semantic(1), 0)
            self.assertEqual(snapshot.cell(0, 1).semantic, 3)

    def test_output_at_column_zero_clears_prompt_mark(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"P") + b"$ echo \\\r\n"
                + osc133(b"C")
            )

            self.assertEqual(terminal.row_semantic(1), 0)

    def test_output_after_prompt_text_preserves_prompt_mark(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"P") + b"$ \r\n"
                + osc133(b"P", b"k=c") + b"> "
                + osc133(b"C")
            )

            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )

    def test_multiple_prompt_newlines_mark_every_row(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"P") + b"line1\r\nline2\r\nline3"
            )

            self.assertEqual(terminal.row_semantic(0), PROMPT)
            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )
            self.assertEqual(
                terminal.row_semantic(2),
                PROMPT_CONTINUATION,
            )

    def test_empty_prompt_row_keeps_continuation_when_scrolling(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc133(b"P") + b"l1\r\nl2\r\nl3\r\n\r\nl5")
            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )
            self.assertEqual(
                terminal.row_semantic(2),
                PROMPT_CONTINUATION,
            )

    def test_click_events_absolute(self):
        with Shitty(columns=10, rows=5) as terminal:
            self.assertEqual(terminal.semantic_click(), CLICK_NONE)
            terminal.write(osc133(b"A", b"click_events=1"))
            self.assertEqual(terminal.semantic_click(), CLICK_ABSOLUTE)

    def test_click_events_relative(self):
        with Shitty(columns=10, rows=5) as terminal:
            self.assertEqual(terminal.semantic_click(), CLICK_NONE)
            terminal.write(osc133(b"A", b"click_events=2"))
            self.assertEqual(terminal.semantic_click(), CLICK_RELATIVE)

    def test_disabled_click_events_leave_click_none(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"A", b"click_events=0"))
            self.assertEqual(terminal.semantic_click(), CLICK_NONE)

    def test_cl_multiple(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"A", b"cl=m"))
            self.assertEqual(terminal.semantic_click(), CLICK_MULTIPLE)

    def test_cl_line(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"A", b"cl=line"))
            self.assertEqual(terminal.semantic_click(), CLICK_LINE)

    def test_click_events_take_priority_over_cl(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"click_events=1;cl=m")
            )
            self.assertEqual(terminal.semantic_click(), CLICK_ABSOLUTE)

    def test_disabled_click_events_fall_back_to_cl(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                osc133(b"A", b"click_events=0;cl=v")
            )
            self.assertEqual(
                terminal.semantic_click(),
                CLICK_CONSERVATIVE_VERTICAL,
            )

    def test_no_click_options_leave_click_none(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(osc133(b"A", b"aid=123"))
            self.assertEqual(terminal.semantic_click(), CLICK_NONE)

    def test_cursor_is_at_prompt(self):
        with Shitty(columns=10, rows=3) as terminal:
            self.assertFalse(terminal.cursor_at_prompt())
            terminal.write(osc133(b"P"))
            self.assertTrue(terminal.cursor_at_prompt())
            terminal.write(b"$ " + osc133(b"B"))
            self.assertTrue(terminal.cursor_at_prompt())
            terminal.write(b"ls" + osc133(b"C"))
            self.assertTrue(terminal.cursor_at_prompt())
            terminal.write(b"\n")
            self.assertFalse(terminal.cursor_at_prompt())
            terminal.write(b"\n" + osc133(b"P"))
            self.assertTrue(terminal.cursor_at_prompt())

    def test_cursor_is_never_at_prompt_on_alternate_screen(self):
        with Shitty(columns=3, rows=2) as terminal:
            self.assertFalse(terminal.cursor_at_prompt())
            terminal.write(osc133(b"P"))
            self.assertTrue(terminal.cursor_at_prompt())
            terminal.write(b"\x1b[?1049h")
            self.assertFalse(terminal.cursor_at_prompt())
            terminal.write(osc133(b"P"))
            self.assertFalse(terminal.cursor_at_prompt())

    def test_explicit_prompt_start_does_not_move_cursor(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"Hello" + osc133(b"P") + b"X")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:6], "HelloX")
            self.assertEqual(snapshot.cell(5, 0).semantic, 1)
            self.assertEqual(terminal.row_semantic(0), PROMPT)

    def test_new_command_has_fresh_line_semantics(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"Hello" + osc133(b"N") + b"X")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:5], "Hello")
            self.assertEqual(snapshot.lines[1][0], "X")
            self.assertEqual(snapshot.cell(0, 1).semantic, 1)
            self.assertEqual(terminal.row_semantic(1), PROMPT)

    def test_new_command_at_column_zero_stays_on_row(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(osc133(b"N") + b"X")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][0], "X")
            self.assertEqual(snapshot.cursor_y, 0)
            self.assertEqual(terminal.row_semantic(0), PROMPT)

    def test_prompt_row_metadata_survives_reflow(self):
        with Shitty(columns=12, rows=4, save_lines=8) as terminal:
            terminal.write(
                osc133(b"P") + b"0123456789abcdef"
                + osc133(b"P", b"k=c") + b"> "
            )
            terminal.resize(8, 4)

            self.assertEqual(terminal.row_semantic(0), PROMPT)
            self.assertEqual(
                terminal.row_semantic(1),
                PROMPT_CONTINUATION,
            )
            self.assertEqual(
                terminal.row_semantic(2),
                PROMPT_CONTINUATION,
            )


if __name__ == "__main__":
    unittest.main()

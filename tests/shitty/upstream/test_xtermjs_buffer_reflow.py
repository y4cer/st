# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all xterm.js BufferReflow cases."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "small line with wide characters reflows to valid cell boundaries",
    "large line with wide characters reflows at every smaller width",
    "mixed narrow and wide characters reflow at valid boundaries",
    "an existing soft-wrapped line reflows at valid boundaries",
    "a line ending in null space ignores that space during reflow",
    "growth skips the wrapped block containing the cursor when configured",
    "growth reflows a wrapped block when the cursor is outside it",
)


def visible_text(terminal):
    snapshot = terminal.snapshot()
    result = []
    for row in range(snapshot.rows):
        text = "".join(
            snapshot.cell(column, row).char
            for column in range(snapshot.columns)
            if not snapshot.cell(column, row).double_width_continuation
        ).rstrip()
        result.append(text)
    while result and not result[-1]:
        result.pop()
    return tuple(result)


def reflow_text(text, old_columns, new_columns):
    with Shitty(columns=old_columns, rows=12, save_lines=0) as terminal:
        terminal.write(text.encode() + b"\r\n")
        terminal.resize(new_columns, 12)
        return visible_text(terminal)


class XtermJsBufferReflowTest(unittest.TestCase):
    def test_upstream_inventory_has_7_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 7)
        self.assertEqual(len(set(UPSTREAM_CASES)), 7)

    def test_small_line_with_wide_characters(self):
        self.assertEqual(reflow_text("汉语", 4, 3), ("汉", "语"))
        self.assertEqual(reflow_text("汉语", 4, 2), ("汉", "语"))

    def test_large_line_with_wide_characters(self):
        text = "汉语汉语汉语"
        expected = {
            11: ("汉语汉语汉", "语"),
            10: ("汉语汉语汉", "语"),
            9: ("汉语汉语", "汉语"),
            8: ("汉语汉语", "汉语"),
            7: ("汉语汉", "语汉语"),
            6: ("汉语汉", "语汉语"),
            5: ("汉语", "汉语", "汉语"),
            4: ("汉语", "汉语", "汉语"),
            3: ("汉", "语", "汉", "语", "汉", "语"),
            2: ("汉", "语", "汉", "语", "汉", "语"),
        }
        for columns, lines in expected.items():
            with self.subTest(columns=columns):
                self.assertEqual(reflow_text(text, 12, columns), lines)

    def test_mixed_narrow_and_wide_characters(self):
        expected = {
            5: ("a汉语", "b"),
            4: ("a汉", "语b"),
            3: ("a汉", "语b"),
            2: ("a", "汉", "语", "b"),
        }
        for columns, lines in expected.items():
            with self.subTest(columns=columns):
                self.assertEqual(reflow_text("a汉语b", 6, columns), lines)

    def test_existing_soft_wrapped_line(self):
        expected = {
            5: ("a汉语", "ba汉", "语b"),
            4: ("a汉", "语ba", "汉语", "b"),
            3: ("a汉", "语b", "a汉", "语b"),
            2: ("a", "汉", "语", "ba", "汉", "语", "b"),
        }
        for columns, lines in expected.items():
            with self.subTest(columns=columns):
                self.assertEqual(
                    reflow_text("a汉语ba汉语b", 6, columns),
                    lines,
                )

    def test_line_ending_in_null_space(self):
        self.assertEqual(reflow_text("汉语", 5, 3), ("汉", "语"))
        self.assertEqual(reflow_text("汉语", 5, 2), ("汉", "语"))

    @unittest.expectedFailure
    def test_growth_skips_wrapped_cursor_block_when_configured(self):
        with Shitty(columns=1, rows=7, save_lines=0) as terminal:
            terminal.write(b"abcde")
            terminal.resize(5, 7)
            self.assertEqual(visible_text(terminal), ("a", "b", "c", "d", "e"))

    def test_growth_reflows_wrapped_block_when_cursor_is_outside_it(self):
        with Shitty(columns=1, rows=7, save_lines=0) as terminal:
            terminal.write(b"abcde\r\n\r\n")
            terminal.resize(5, 7)
            self.assertEqual(visible_text(terminal), ("abcde",))


if __name__ == "__main__":
    unittest.main()

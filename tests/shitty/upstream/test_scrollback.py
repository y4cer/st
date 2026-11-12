# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


class ScrollbackTest(unittest.TestCase):
    def test_control_reports_absolute_scrollback_geometry(self):
        with Shitty(columns=4, rows=2, save_lines=5) as terminal:
            self.assertEqual(terminal.scrollback_state(), (0, 2, 2, 0))
            terminal.write(b"zero\r\none\r\ntwo\r\ntri")
            self.assertEqual(terminal.scrollback_state(), (2, 4, 2, 2))
            terminal.wheel_up(2)
            self.assertEqual(terminal.scrollback_state(), (2, 4, 2, 0))

    def test_wheel_unit_moves_exactly_one_line(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
                + b"\x1b[S\x1b[3;1HE"
                + b"\x1b[S\x1b[3;1HF"
            )

            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().view_offset, 1)
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().view_offset, 2)
            terminal.wheel_down()
            self.assertEqual(terminal.snapshot().view_offset, 1)

    def test_new_output_preserves_scrolled_view(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            terminal.page_up()

            before = terminal.snapshot()
            self.assertEqual(before.view_offset, 1)
            self.assertEqual(before.lines, ["one     ", "two     ", "three   "])

            terminal.write(b"\r\nfive")

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 2)
            self.assertEqual(after.lines, ["one     ", "two     ", "three   "])

    def test_modifier_only_keys_do_not_exit_scrollback(self):
        modifiers = (
            (340, 1),
            (341, 2),
            (342, 4),
            (343, 8),
            (344, 1),
            (345, 2),
            (346, 4),
            (347, 8),
        )
        for key, mask in modifiers:
            with self.subTest(key=key):
                with Shitty(columns=8, rows=3, save_lines=8) as terminal:
                    terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
                    terminal.page_up()

                    terminal.frontend_key_event(key, 1, modifiers=mask)
                    terminal.frontend_key_event(key, 0)

                    self.assertEqual(terminal.snapshot().view_offset, 1)
                    self.assertEqual(terminal.read_input(), b"")

        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour")
            terminal.page_up()

            terminal.frontend_text_event("x")

            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.read_input(), b"x")

        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\x1b[>2u")
            terminal.page_up()

            terminal.frontend_key_event(340, 1, modifiers=1)
            terminal.frontend_key_event(340, 0)

            self.assertEqual(terminal.snapshot().view_offset, 1)
            self.assertEqual(terminal.read_input(), b"")

        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\r\nfour\x1b[>10u")
            terminal.page_up()

            terminal.frontend_key_event(340, 1, modifiers=1)

            self.assertEqual(terminal.snapshot().view_offset, 1)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[57441;2u",
            )

    def test_alternate_screen_does_not_keep_scrollback(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                b"one\r\ntwo\r\nthree\r\nfour"
            )
            terminal.page_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["two     ", "three   ", "four    "],
            )

            terminal.write(b"\r\nfive")

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 0)
            self.assertEqual(
                after.lines,
                ["three   ", "four    ", "five    "],
            )

    def test_partial_region_scroll_does_not_create_blank_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                b"screen1\r\nscreen2\r\nscreen3"
                b"\x1b[3;6r\x1b[3;1H\x1b[5S\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)

    def test_top_anchored_region_saves_evicted_row(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"STATUS", b"PROMPT")
                + b"\x1b[1;4r\x1b[S\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(
                snapshot.lines,
                ["A       ", "B       ", "C       ",
                 "D       ", "        ", "STATUS  "],
            )

    def test_top_anchored_region_saves_multiple_rows_in_order(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[1;4r\x1b[2S\x1b[r"
            )
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(
                snapshot.lines,
                ["A       ", "B       ", "C       ",
                 "D       ", "        ", "        "],
            )

    def test_linefeed_at_region_bottom_saves_evicted_row(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[1;4r\x1b[4;1H\n\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines[0], "A       ")

    def test_index_at_region_bottom_saves_evicted_row(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[1;4r\x1b[4;1H\x1bD\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines[0], "A       ")

    def test_scroll_count_is_clamped_and_saves_entire_region(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"FIXED")
                + b"\x1b[1;3r\x1b[99S\x1b[r"
            )
            terminal.wheel_up(3)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 3)
            self.assertEqual(
                snapshot.lines,
                ["A       ", "B       ", "C       ", "        "],
            )

    def test_middle_region_scrolls_only_region_without_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[2;5r\x1b[2S\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["A       ", "D       ", "E       ",
                 "        ", "        ", "F       "],
            )

    def test_middle_region_does_not_modify_existing_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"H1", b"H2", b"A", b"B", b"C", b"D")
                + b"\x1b[2S"
                + put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[2;5r\x1b[2S\x1b[r"
            )
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(
                snapshot.lines,
                ["H1      ", "H2      ", "A       ",
                 "D       ", "E       ", "        "],
            )

    def test_full_reverse_scroll_does_not_consume_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"H1", b"H2", b"A", b"B", b"C", b"D")
                + b"\x1b[2S"
                + put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[2T"
            )
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(
                snapshot.lines,
                ["H1      ", "H2      ", "        ",
                 "        ", "A       ", "B       "],
            )

    def test_top_anchored_reverse_scroll_does_not_consume_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"H1", b"H2", b"A", b"B", b"C", b"D")
                + b"\x1b[2S"
                + put_rows(b"A", b"B", b"C", b"D", b"E", b"F")
                + b"\x1b[1;4r\x1b[T\x1b[r"
            )
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(
                snapshot.lines,
                ["H1      ", "H2      ", "        ",
                 "A       ", "B       ", "C       "],
            )

    def test_scrollback_capacity_drops_only_oldest_rows(self):
        with Shitty(columns=8, rows=3, save_lines=3) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
                + b"\x1b[S\x1b[3;1HE"
                + b"\x1b[S\x1b[3;1HF"
                + b"\x1b[S\x1b[3;1HG"
                + b"\x1b[S\x1b[3;1HH"
                + b"\x1b[S\x1b[3;1HI"
            )
            terminal.wheel_up(5)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 3)
            self.assertEqual(snapshot.lines, ["D       ", "E       ", "F       "])

    def test_output_at_capacity_advances_past_evicted_history(self):
        with Shitty(columns=8, rows=3, save_lines=3) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
                + b"\x1b[S\x1b[3;1HE"
                + b"\x1b[S\x1b[3;1HF"
                + b"\x1b[S\x1b[3;1HG"
                + b"\x1b[S\x1b[3;1HH"
            )
            terminal.wheel_up(5)
            self.assertEqual(
                terminal.snapshot().lines,
                ["C       ", "D       ", "E       "],
            )

            terminal.write(b"\x1b[S\x1b[3;1HI")

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 3)
            self.assertEqual(snapshot.lines, ["D       ", "E       ", "F       "])

    def test_write_while_scrolled_changes_only_live_screen(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
                + b"\x1b[S\x1b[3;1HE"
            )
            terminal.wheel_up(2)
            before = terminal.snapshot()

            terminal.write(b"\x1b[2;1HX")

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 2)
            self.assertEqual(after.lines, before.lines)
            terminal.wheel_down(2)
            self.assertEqual(
                terminal.snapshot().lines,
                ["C       ", "X       ", "E       "],
            )

    def test_changing_margins_does_not_change_screen_or_history(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"H", b"A", b"B", b"C")
                + b"\x1b[S"
            )
            terminal.wheel_up()
            before = terminal.snapshot()

            terminal.write(b"\x1b[2;3r\x1b[r")

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, before.view_offset)
            self.assertEqual(after.lines, before.lines)

    def test_zero_capacity_never_exposes_scrollback(self):
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.lines, ["B       ", "C       ", "D       "])

    def test_clear_history_while_scrolled_returns_to_live_screen(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"A", b"B", b"C")
                + b"\x1b[S\x1b[3;1HD"
            )
            terminal.wheel_up()
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.write(b"\x1b[3J")

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.lines, ["B       ", "C       ", "D       "])

    def test_top_anchored_scroll_preserves_cell_attributes(self):
        # Asserts bold-brightened palette indices; default off (issue 59).
        with Shitty(
            columns=8, rows=4, save_lines=8, extra_arguments=("-boldColors",)
        ) as terminal:
            terminal.write(
                b"\x1b[1;1H\x1b]8;;https://example.com\x1b\\"
                b"\x1b[1;31mX\x1b[0m\x1b]8;;\x1b\\"
                b"\x1b[2;1HB\x1b[3;1HC\x1b[4;1HD"
                + b"\x1b[S"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            cell = snapshot.cell(0, 0)
            self.assertTrue(cell.bold)
            self.assertEqual(cell.foreground, (255, 85, 85))
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.com")

    def test_alternate_top_anchored_region_does_not_create_scrollback(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            terminal.write(
                b"\x1b[?1049h"
                + put_rows(b"A", b"B", b"C", b"D")
                + b"\x1b[1;3r\x1b[S\x1b[r"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["B       ", "C       ", "        ", "D       "],
            )

    def test_primary_history_survives_alternate_screen_scrolling(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                put_rows(b"P1", b"P2", b"P3")
                + b"\x1b[S\x1b[3;1HP4"
                + b"\x1b[?1049h"
                + put_rows(b"A1", b"A2", b"A3")
                + b"\x1b[S\x1b[3;1HA4"
                + b"\x1b[?1049l"
            )
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 1)
            self.assertEqual(snapshot.lines, ["P1      ", "P2      ", "P3      "])

    def test_shrink_moves_clipped_top_rows_to_scrollback(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D"))
            terminal.resize(8, 2)
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(snapshot.lines, ["A       ", "B       "])

    def test_grow_restores_newest_rows_from_scrollback(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            terminal.write(put_rows(b"A", b"B", b"C", b"D"))
            terminal.resize(8, 2)
            terminal.resize(8, 4)
            terminal.wheel_up()

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(
                snapshot.lines,
                ["A       ", "B       ", "C       ", "D       "],
            )

    def test_codex_top_anchored_redraw_builds_real_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                put_rows(b"T1", b"T2", b"T3", b"T4", b"UI1", b"UI2")
                + b"\x1b[?2026h"
                + b"\x1b[1;4r\x1b[2S"
                + b"\x1b[3;6r\x1b[3;1H\x1bM\x1bM"
                + b"\x1b[r\x1b[?2026l"
            )
            terminal.wheel_up(2)

            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.view_offset, 2)
            self.assertEqual(snapshot.lines[:2], ["T1      ", "T2      "])

    def test_scroll_sequence_matches_slow_reference_model(self):
        rows = 4
        capacity = 4
        screen = ["A", "B", "C", "D"]
        history = []
        operations = [
            ("up", 0, 4, 1, ["E"]),
            ("up", 0, 3, 1, ["F"]),
            ("up", 1, 4, 2, ["G", "H"]),
            ("down", 0, 4, 1, ["I"]),
            ("up", 0, 4, 2, ["J", "K"]),
            ("down", 0, 3, 2, ["L", "M"]),
            ("up", 2, 4, 1, ["N"]),
            ("up", 0, 4, 3, ["O", "P", "Q"]),
        ]

        with Shitty(columns=4, rows=rows, save_lines=capacity) as terminal:
            terminal.write(put_rows(*(value.encode() for value in screen)))

            for direction, top, bottom, count, fill in operations:
                actual = min(count, bottom - top)
                for _ in range(actual):
                    if direction == "up":
                        outgoing = screen[top]
                        screen[top : bottom - 1] = screen[top + 1 : bottom]
                        screen[bottom - 1] = ""
                        if top == 0:
                            history.append(outgoing)
                            history = history[-capacity:]
                    else:
                        screen[top + 1 : bottom] = screen[top : bottom - 1]
                        screen[top] = ""

                if direction == "up":
                    fill_rows = range(bottom - actual, bottom)
                    command = "S"
                else:
                    fill_rows = range(top, top + actual)
                    command = "T"

                output = (
                    f"\x1b[{top + 1};{bottom}r"
                    f"\x1b[{count}{command}\x1b[r"
                ).encode()
                for row, value in zip(fill_rows, fill):
                    screen[row] = value
                    output += f"\x1b[{row + 1};1H{value}".encode()
                terminal.write(output)

                live = terminal.snapshot()
                self.assertEqual(
                    live.lines,
                    [value.ljust(4) for value in screen],
                )

                terminal.wheel_up(len(history))
                viewed = terminal.snapshot()
                self.assertEqual(viewed.view_offset, len(history))
                expected = (history + screen)[:rows]
                self.assertEqual(
                    viewed.lines,
                    [value.ljust(4) for value in expected],
                )
                terminal.wheel_down(len(history))

    def test_codex_partial_reverse_index_preserves_real_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                b"line1\r\nline2\r\nline3\r\nline4\r\n"
                b"line5\r\nline6\r\nline7\r\nline8\r\n"
                b"line9\r\nline10\r\nline11\r\nline12"
            )
            terminal.wheel_up(6)
            before = terminal.snapshot()
            self.assertEqual(before.view_offset, 6)
            self.assertEqual(
                before.lines,
                ["line1   ", "line2   ", "line3   ",
                 "line4   ", "line5   ", "line6   "],
            )
            terminal.wheel_down(6)

            terminal.write(
                b"\x1b[?2026h"
                b"\x1b[3;6r\x1b[3;1H"
                + b"\x1bM" * 8
                + b"\x1b[r"
                b"\x1b[?2026l"
            )
            terminal.wheel_up(6)

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 6)
            self.assertEqual(after.lines, before.lines)

    def test_codex_full_screen_reverse_index_preserves_real_history(self):
        with Shitty(columns=8, rows=6, save_lines=20) as terminal:
            terminal.write(
                b"line1\r\nline2\r\nline3\r\nline4\r\n"
                b"line5\r\nline6\r\nline7\r\nline8\r\n"
                b"line9\r\nline10\r\nline11\r\nline12"
            )
            terminal.wheel_up(6)
            before = terminal.snapshot()
            terminal.wheel_down(6)

            terminal.write(
                b"\x1b[?2026h"
                b"\x1b[1;6r\x1b[1;1H"
                + b"\x1bM" * 8
                + b"\x1b[r"
                b"\x1b[?2026l"
            )
            terminal.wheel_up(6)

            after = terminal.snapshot()
            self.assertEqual(after.view_offset, 6)
            self.assertEqual(after.lines, before.lines)


if __name__ == "__main__":
    unittest.main()

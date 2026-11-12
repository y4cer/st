# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Editing, scrolling, history and SGR streams from tmux regress."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/input-edit.sh:ed", "test_erase_display_after_cursor"),
    ("regress/input-edit.sh:ed1", "test_erase_display_before_cursor"),
    ("regress/input-edit.sh:ed2", "test_erase_complete_display"),
    ("regress/input-edit.sh:il", "test_insert_line"),
    ("regress/input-edit.sh:dl", "test_delete_line"),
    ("regress/input-edit.sh:rep", "test_repeat_previous_character"),
    ("regress/input-edit.sh:decaln", "test_screen_alignment_pattern"),
    ("regress/input-scroll.sh:wraplast", "test_wrap_after_absolute_last_column"),
    ("regress/input-scroll.sh:nowrap", "test_disabled_autowrap_overwrites_last_column"),
    ("regress/input-scroll.sh:origin", "test_origin_mode_addresses_inside_scroll_region"),
    ("regress/input-scroll.sh:scrollup", "test_linefeed_scrolls_vertical_region_up"),
    ("regress/input-scroll.sh:scrolldown", "test_scroll_down_inside_vertical_region"),
    ("regress/input-scroll.sh:ri", "test_reverse_index_inside_vertical_region"),
    ("regress/input-scroll.sh:nel", "test_next_line_moves_to_first_column"),
    ("regress/input-scroll.sh:history-limit", "test_finite_history_keeps_page_and_tail"),
    ("regress/input-scroll.sh:clear-history", "test_clear_history_keeps_live_page"),
    ("regress/input-sgr.sh:sgr-basic", "test_basic_renditions_and_resets"),
    ("regress/input-sgr.sh:sgr-colour", "test_palette_rgb_and_default_colours"),
    ("regress/input-sgr.sh:sgr-underline", "test_all_underline_styles"),
    ("regress/input-sgr.sh:sgr-uscolour", "test_underline_palette_rgb_and_reset"),
    ("regress/input-sgr.sh:sgr-reset", "test_bright_colours_and_default_resets"),
)


class TmuxRegressEditScrollSgrTest(unittest.TestCase):
    def _run_stream(
        self,
        columns,
        rows,
        payload,
        expected_lines,
        *,
        cursor=None,
        save_lines=3,
    ):
        with Shitty(
            columns=columns, rows=rows, save_lines=save_lines
        ) as terminal:
            # These source printf strings pass through a normal PTY, so
            # ONLCR turns source LF into CR LF before the parser sees it.
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

    def _sgr_snapshot(self, payload, expected_text):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(payload.replace(b"\n", b"\r\n"))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], expected_text.ljust(20))
            return snapshot

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_erase_display_after_cursor(self):
        self._run_stream(
            10,
            3,
            b"one\ntwo\x1b[2;2H\x1b[JX\n",
            ["one", "tX"],
        )

    def test_erase_display_before_cursor(self):
        self._run_stream(
            10,
            3,
            b"one\ntwo\x1b[2;2H\x1b[1JX\n",
            ["", " Xo"],
        )

    def test_erase_complete_display(self):
        self._run_stream(
            10,
            3,
            b"one\ntwo\x1b[2JZ\n",
            ["", "   Z"],
        )

    def test_insert_line(self):
        self._run_stream(
            8,
            4,
            b"111\n222\n333\x1b[2;1H\x1b[LAAA\n",
            ["111", "AAA", "222", "333"],
        )

    def test_delete_line(self):
        self._run_stream(
            8,
            4,
            b"111\n222\n333\x1b[2;1H\x1b[MZZZ\n",
            ["111", "ZZZ"],
        )

    def test_repeat_previous_character(self):
        self._run_stream(
            10,
            3,
            b"A\x1b[4bB\n",
            ["AAAAAB"],
        )

    def test_screen_alignment_pattern(self):
        self._run_stream(
            6,
            3,
            b"\x1b#8",
            ["EEEEEE", "EEEEEE", "EEEEEE"],
            cursor=(0, 0),
        )

    def test_wrap_after_absolute_last_column(self):
        snapshot = self._run_stream(
            5,
            3,
            b"abcd\x1b[5GZQ",
            ["abcdZ", "Q"],
            cursor=(1, 1),
        )
        self.assertTrue(snapshot.cell(4, 0).wrapped)

    def test_disabled_autowrap_overwrites_last_column(self):
        snapshot = self._run_stream(
            5,
            3,
            b"\x1b[?7labcdeF",
            ["abcdF"],
            cursor=(4, 0),
        )
        self.assertFalse(snapshot.cell(4, 0).wrapped)

    def test_origin_mode_addresses_inside_scroll_region(self):
        self._run_stream(
            6,
            4,
            b"111111\n222222\n333333\n444444"
            b"\x1b[2;3r\x1b[?6h\x1b[1;1HAA\x1b[?6l\x1b[r",
            ["111111", "AA2222", "333333", "444444"],
        )

    def test_linefeed_scrolls_vertical_region_up(self):
        self._run_stream(
            5,
            4,
            b"11111\n22222\n33333\n44444"
            b"\x1b[2;3r\x1b[3;1HAAAAA\nBBBBB\x1b[r",
            ["11111", "AAAAA", "BBBBB", "44444"],
        )

    def test_scroll_down_inside_vertical_region(self):
        self._run_stream(
            5,
            4,
            b"11111\n22222\n33333\n44444"
            b"\x1b[2;3r\x1b[2;1H\x1b[TZZZZZ\x1b[r",
            ["11111", "ZZZZZ", "22222", "44444"],
        )

    def test_reverse_index_inside_vertical_region(self):
        self._run_stream(
            5,
            4,
            b"11111\n22222\n33333\n44444"
            b"\x1b[2;3r\x1b[2;1H\x1bMZZZZZ\x1b[r",
            ["11111", "ZZZZZ", "22222", "44444"],
        )

    def test_next_line_moves_to_first_column(self):
        self._run_stream(
            5,
            3,
            b"AA\x1bEBC\n",
            ["AA", "BC"],
            cursor=(0, 2),
        )

    def test_finite_history_keeps_page_and_tail(self):
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(b"01\r\n02\r\n03\r\n04\r\n05\r\n06")
            self.assertEqual(
                terminal.all_text(),
                ("01", "02", "03", "04", "05", "06"),
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["04   ", "05   ", "06   "],
            )

    def test_clear_history_keeps_live_page(self):
        with Shitty(columns=5, rows=3, save_lines=3) as terminal:
            terminal.write(b"01\r\n02\r\n03\r\n04\r\n05\r\n06")
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.all_text(), ("04", "05", "06"))
            self.assertEqual(
                terminal.snapshot().lines,
                ["04   ", "05   ", "06   "],
            )

    def test_basic_renditions_and_resets(self):
        snapshot = self._sgr_snapshot(
            b"\x1b[1;2;3;4;5;7;8;9mA"
            b"\x1b[22;23;24;25;27;28;29mB\n",
            "AB",
        )
        active = snapshot.cell(0, 0)
        self.assertTrue(active.bold)
        self.assertTrue(active.faint)
        self.assertTrue(active.italic)
        self.assertTrue(active.underline)
        self.assertEqual(active.underline_style, 1)
        self.assertTrue(active.blink)
        self.assertTrue(active.inverse)
        self.assertTrue(active.conceal)
        self.assertTrue(active.strike)
        reset = snapshot.cell(1, 0)
        for name in (
            "bold",
            "faint",
            "italic",
            "underline",
            "blink",
            "inverse",
            "conceal",
            "strike",
        ):
            self.assertFalse(getattr(reset, name), name)

    def test_palette_rgb_and_default_colours(self):
        snapshot = self._sgr_snapshot(
            b"\x1b[31;42mA"
            b"\x1b[38;5;196;48;5;22mB"
            b"\x1b[38;2;1;2;3;48;2;4;5;6mC"
            b"\x1b[39;49mD\n",
            "ABCD",
        )
        self.assertEqual(
            (snapshot.cell(0, 0).foreground, snapshot.cell(0, 0).background),
            ((170, 0, 0), (0, 170, 0)),
        )
        self.assertEqual(
            (snapshot.cell(1, 0).foreground, snapshot.cell(1, 0).background),
            ((255, 0, 0), (0, 95, 0)),
        )
        self.assertEqual(
            (snapshot.cell(2, 0).foreground, snapshot.cell(2, 0).background),
            ((1, 2, 3), (4, 5, 6)),
        )
        self.assertEqual(
            (snapshot.cell(3, 0).foreground, snapshot.cell(3, 0).background),
            ((255, 255, 255), (0, 0, 0)),
        )

    def test_all_underline_styles(self):
        snapshot = self._sgr_snapshot(
            b"\x1b[4:1mA\x1b[4:2mB\x1b[4:3mC"
            b"\x1b[4:4mD\x1b[4:5mE\x1b[4:0mF\n",
            "ABCDEF",
        )
        self.assertEqual(
            [snapshot.cell(column, 0).underline_style for column in range(6)],
            [1, 2, 3, 4, 5, 0],
        )
        self.assertEqual(
            [snapshot.cell(column, 0).underline for column in range(6)],
            [True, True, True, True, True, False],
        )

    def test_underline_palette_rgb_and_reset(self):
        snapshot = self._sgr_snapshot(
            b"\x1b[58;5;45;4mA"
            b"\x1b[58:2::10:20:30mB"
            b"\x1b[59mC\n",
            "ABC",
        )
        self.assertEqual(snapshot.cell(0, 0).underline_color, (0, 215, 255))
        self.assertEqual(snapshot.cell(1, 0).underline_color, (10, 20, 30))
        self.assertEqual(snapshot.cell(2, 0).underline_color, (255, 255, 255))
        for column in range(3):
            self.assertTrue(snapshot.cell(column, 0).underline)

    def test_bright_colours_and_default_resets(self):
        snapshot = self._sgr_snapshot(
            b"\x1b[90;100mA\x1b[0mB"
            b"\x1b[91;101mC\x1b[39;49mD\n",
            "ABCD",
        )
        self.assertEqual(
            (snapshot.cell(0, 0).foreground, snapshot.cell(0, 0).background),
            ((85, 85, 85), (85, 85, 85)),
        )
        self.assertEqual(
            (snapshot.cell(1, 0).foreground, snapshot.cell(1, 0).background),
            ((255, 255, 255), (0, 0, 0)),
        )
        self.assertEqual(
            (snapshot.cell(2, 0).foreground, snapshot.cell(2, 0).background),
            ((255, 85, 85), (255, 85, 85)),
        )
        self.assertEqual(
            (snapshot.cell(3, 0).foreground, snapshot.cell(3, 0).background),
            ((255, 255, 255), (0, 0, 0)),
        )


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Third public batch from iTerm2's legacy VT100ScreenTest."""

import unittest

from harness import Shitty, put_rows


PORTED_CASES = (
    ("testFind_MatchingDWC", "test_find_matches_wide_character"),
    ("testFind_MatchOverDwcSkip", "test_find_crosses_wide_wrap_skip"),
    ("testFind_MultipleBlocks", "test_find_crosses_storage_blocks_and_eviction"),
    ("testScrollingInAltScreen", "test_alternate_scrolling_policy_and_selection"),
    ("testAllDirty", "test_full_redraw_is_distinct_from_cell_damage"),
    ("testSetCharDirtyAtCursor", "test_cursor_writes_publish_exact_rows"),
    ("testIsDirtyAt", "test_row_damage_tracks_write_and_full_erase"),
    ("testSaveToDvr", "test_terminal_recording_replays_saved_frames"),
    ("testContentsChangedNotification", "test_content_change_publishes_one_refresh"),
    ("testPrinting", "test_media_copy_obeys_printer_policy"),
    ("testBackspace", "test_backspace_margins_soft_wrap_and_wide_skip"),
    ("testTabStops", "test_tab_stops_text_margins_and_backtab"),
    ("testMoveCursor", "test_cup_clamps_to_page_or_origin_margins"),
    ("testSaveAndRestoreCursorAndCharset", "test_decsc_decrc_restore_position_and_charsets"),
    ("testSetTopBottomScrollRegion", "test_vertical_region_scroll_and_origin_home"),
    ("testEraseInDisplay", "test_ed_directions_cursor_and_history_policy"),
    ("testEraseLine", "test_el_directions_and_clamped_cursor"),
    ("testIndex", "test_ind_and_ri_with_full_and_rectangular_regions"),
    ("testResetPreservingPrompt", "test_reset_preserving_prompt_contract"),
    ("testSetWidth", "test_window_width_request_respects_host_policy"),
)


def write_lines(terminal, *lines):
    for line in lines:
        terminal.write(line.encode("utf-8") + b"\r\n")


def find_text(terminal, query, **options):
    """Call the real host-search operation once Shitty provides one."""
    operation = getattr(terminal, "find_text", None)
    if operation is None:
        raise AssertionError(
            "terminal-buffer search is supported by the implementation "
            "consensus but Shitty has no host search operation"
        )
    return operation(query, **options)


def tab_destinations(terminal):
    terminal.write(b"\r")
    result = []
    previous = terminal.model_snapshot().cursor_x
    while True:
        terminal.write(b"\t")
        current = terminal.model_snapshot().cursor_x
        if current == previous:
            return result
        result.append(current)
        previous = current


class ITerm2LegacyScreenControlsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def make_wide_search_fixture(self):
        terminal = Shitty(columns=4, rows=5, save_lines=20)
        terminal.write(
            b"abcdefgc\r\nde\r\nfgx" + "界z".encode("utf-8")
        )
        self.assertEqual(
            terminal.all_text(),
            ("abcd", "efgc", "de", "fgx", "界z"),
        )
        snapshot = terminal.model_snapshot()
        self.assertTrue(snapshot.cell(2, 3).wrapped)
        self.assertTrue(snapshot.cell(0, 4).double_width)
        self.assertTrue(snapshot.cell(1, 4).double_width_continuation)
        return terminal

    @unittest.expectedFailure
    def test_find_matches_wide_character(self):
        terminal = self.make_wide_search_fixture()
        try:
            result = find_text(
                terminal,
                "界z",
                start=(0, 0),
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(result["starts"], result["ends"])),
                (((0, 4), (2, 4)),),
            )
        finally:
            terminal.close()

    @unittest.expectedFailure
    def test_find_crosses_wide_wrap_skip(self):
        terminal = self.make_wide_search_fixture()
        try:
            result = find_text(
                terminal,
                "x界z",
                start=(0, 0),
                backwards=False,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(result["starts"], result["ends"])),
                (((2, 3), (2, 4)),),
            )
        finally:
            terminal.close()

    @unittest.expectedFailure
    def test_find_crosses_storage_blocks_and_eviction(self):
        lines = (
            "abcdefghij",
            "spam",
            "bacon",
            "eggs",
            "spam",
            "0123def456789",
            "hello def world",
        )
        with Shitty(columns=5, rows=2, save_lines=32) as terminal:
            write_lines(terminal, *lines)
            result = find_text(
                terminal,
                "def",
                start="end",
                backwards=True,
                case_sensitive=True,
            )
            self.assertEqual(
                tuple(zip(result["starts"], result["ends"])),
                (
                    ((1, 10), (3, 10)),
                    ((4, 6), (1, 7)),
                    ((3, 0), (0, 1)),
                ),
            )

        with Shitty(columns=5, rows=2, save_lines=11) as terminal:
            write_lines(terminal, *lines)
            result = find_text(
                terminal,
                "spam",
                start="end",
                backwards=True,
                case_sensitive=True,
            )
            resume = result["resume"]
            write_lines(terminal, "FOO")
            continued = find_text(
                terminal,
                "spam",
                resume=resume,
                backwards=True,
                case_sensitive=True,
            )
            matches = tuple(zip(result["starts"], result["ends"]))
            matches += tuple(zip(continued["starts"], continued["ends"]))
            self.assertEqual(matches, (((0, 5), (3, 5)),))

    @unittest.expectedFailure
    def test_alternate_scrolling_policy_and_selection(self):
        with Shitty(columns=2, rows=3, save_lines=3) as terminal:
            terminal.write(b"primary")
            terminal.write(
                b"\x1b[?1049h" + put_rows(b"A", b"B", b"C")
            )
            terminal.select_start(1, 1)
            terminal.select_extend(1, 2)
            self.assertTrue(terminal.has_selection())

            terminal.write(b"\x1b[3;1H\x1bD")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["B ", "C ", "  "],
            )
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))
            self.assertEqual(
                terminal.selection_state()["raw"],
                (1, 0, 1, 1),
            )

            operation = getattr(terminal, "set_alt_scrollback", None)
            if operation is None:
                raise AssertionError(
                    "iTerm2's opt-in alternate-screen scrollback policy "
                    "has no Shitty host configuration"
                )
            operation(True)
            terminal.write(b"\x1b[3;1H\x1bD")
            self.assertGreater(terminal.scrollback_state()[0], 0)

    def test_full_redraw_is_distinct_from_cell_damage(self):
        with Shitty(columns=2, rows=3) as terminal:
            terminal.write(b"\n")
            moved = terminal.model_snapshot()
            self.assertEqual(terminal.last_update_rows(), ())

            terminal.present()
            redrawn = terminal.model_snapshot()
            self.assertEqual(terminal.last_update_rows(), ())
            self.assertEqual(redrawn.cells, moved.cells)
            self.assertEqual(redrawn.refresh_count, moved.refresh_count + 1)

    def test_cursor_writes_publish_exact_rows(self):
        with Shitty(columns=2, rows=3) as terminal:
            terminal.write(b"\x1b[1;1HX")
            self.assertEqual(terminal.last_update_rows(), (0,))

            terminal.write(b"\x1b[2;2HY")
            self.assertEqual(terminal.last_update_rows(), (1,))

            terminal.write(b"\x1b[2;2HA")
            self.assertEqual(terminal.last_update_rows(), (1,))
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"B")
            self.assertEqual(terminal.last_update_rows(), (1, 2))
            self.assertEqual(terminal.model_snapshot().lines[2], "B ")

    def test_row_damage_tracks_write_and_full_erase(self):
        with Shitty(columns=2, rows=3) as terminal:
            self.assertEqual(terminal.last_update_rows(), ())
            terminal.write(b"x")
            self.assertEqual(terminal.last_update_rows(), (0,))
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.last_update_rows(), (0, 1, 2))

    @unittest.expectedFailure
    def test_terminal_recording_replays_saved_frames(self):
        with Shitty(columns=20, rows=3) as terminal:
            write_lines(terminal, "Line 1", "Line 2")
            self.assertEqual(
                terminal.model_snapshot().lines[:2],
                ["Line 1              ", "Line 2              "],
            )

            record = getattr(terminal, "record_frame", None)
            replay = getattr(terminal, "replay_frames", None)
            if record is None or replay is None:
                raise AssertionError(
                    "iTerm2's DVR record/replay component has no Shitty "
                    "host operation"
                )
            record()
            write_lines(terminal, "Line 3")
            record()
            frames = replay()
            self.assertEqual(frames[0].lines[0].rstrip(), "Line 1")
            self.assertEqual(frames[1].lines[0].rstrip(), "Line 2")

    def test_content_change_publishes_one_refresh(self):
        with Shitty(columns=20, rows=3) as terminal:
            before = terminal.model_snapshot()
            acknowledged = terminal.model_snapshot()
            self.assertEqual(acknowledged.refresh_count, before.refresh_count)

            terminal.write(b"x")
            changed = terminal.model_snapshot()
            self.assertEqual(changed.refresh_count, before.refresh_count + 1)
            self.assertEqual(terminal.last_update_rows(), (0,))
            self.assertEqual(changed.cell(0, 0).char, "x")

    @unittest.expectedFailure
    def test_media_copy_obeys_printer_policy(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[5itest\r\n\x1b[4i")
            self.assertNotIn("test", "".join(terminal.all_text()))

            output = getattr(terminal, "printer_output", None)
            if output is None:
                raise AssertionError(
                    "Media Copy printer-controller output is not exposed "
                    "by Shitty's host"
                )
            self.assertEqual(output(), b"test\n")

            policy = getattr(terminal, "set_printing_allowed", None)
            if policy is None:
                raise AssertionError("printing allow/deny policy is absent")
            policy(False)
            terminal.write(b"\x1b[5ifallback\x1b[4i")
            self.assertIn("fallback", "".join(terminal.all_text()))

    @unittest.expectedFailure
    def test_backspace_margins_soft_wrap_and_wide_skip(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"Hello\x08")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?45h12345678901234567890Hello"
                b"\x1b[2;1H\x08"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (19, 0))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?45h\x1b[2;1H\x08")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?45h\x1b[?69h\x1b[3;10s"
                b"\x1b[2;3H\x08"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?45h1234567890123456789"
                + "Ｗ".encode("utf-8")
                + b"\x1b[2;1H\x08"
            )
            snapshot = terminal.model_snapshot()
            self.assertTrue(snapshot.cell(18, 0).wrapped)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (19, 0))

    def test_tab_stops_text_margins_and_backtab(self):
        with Shitty(columns=20, rows=3) as terminal:
            self.assertEqual(tab_destinations(terminal), [8, 16, 19])
            terminal.write(b"\x1b[1;10H\x1bH")
            self.assertEqual(tab_destinations(terminal), [8, 9, 16, 19])
            terminal.write(b"\x1b[1;9H\x1b[g")
            self.assertEqual(tab_destinations(terminal), [9, 16, 19])

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?69h\x1b[1;8s\x1b[1;1H\t")
            self.assertEqual(terminal.model_snapshot().cursor_x, 7)

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"0123456789\x1b[1;1H\t")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0][:10], "0123456789")
            self.assertEqual(snapshot.cursor_x, 8)

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\t")
            self.assertEqual(terminal.all_text()[0], "")
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[1;3Hx\x1b[1;1H\t")
            self.assertEqual(terminal.all_text()[0], "  x")
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\t\t\t\t")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (19, 0))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[2;1H\t\t\x1b[Z")
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)
            terminal.write(b"\x1b[Z")
            self.assertEqual(terminal.model_snapshot().cursor_x, 0)
            terminal.write(b"\x1b[Z")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[11;20s\x1b[1;11H\x1b[Z"
            )
            self.assertEqual(terminal.model_snapshot().cursor_x, 8)

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[11;20s\x1b[?6h"
                b"\x1b[1;1H\x1b[Z"
            )
            self.assertEqual(terminal.model_snapshot().cursor_x, 10)

    def test_cup_clamps_to_page_or_origin_margins(self):
        with Shitty(columns=20, rows=20) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[6;16s\x1b[6;16r\x1b[1;1H"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[100;100H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (19, 19))

            terminal.write(b"\x1b[?6h\x1b[1;1H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 5))

            terminal.write(b"\x1b[100;100H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (15, 15))

    def test_decsc_decrc_restore_position_and_charsets(self):
        with Shitty(columns=20, rows=20) as terminal:
            defaults = terminal.charset_state()
            terminal.write(b"\x1b[5;4H\x1b)0\x1b+0")
            saved_charsets = terminal.charset_state()
            self.assertNotEqual(saved_charsets, defaults)
            terminal.write(b"\x1b7\x1b[H\x1b)B\x1b+B")
            self.assertEqual(terminal.charset_state(), defaults)
            terminal.write(b"\x1b8")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 4))
            self.assertEqual(terminal.charset_state(), saved_charsets)

        with Shitty(columns=20, rows=20) as terminal:
            defaults = terminal.charset_state()
            terminal.write(b"\x1b[5;5H\x1b8")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(terminal.charset_state(), defaults)

    def test_vertical_region_scroll_and_origin_home(self):
        with Shitty(columns=20, rows=20) as terminal:
            terminal.write(b"\x1b[6;16r")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            terminal.write(b"\x1b[16;5HHello\n")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[14][4:9], "Hello")
            self.assertEqual(snapshot.lines[15], " " * 20)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 15))

        with Shitty(columns=20, rows=20) as terminal:
            terminal.write(b"\x1b[?6h\x1b[6;16r")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 5))
            terminal.write(b"\x1b[2;2H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 6))

        with Shitty(columns=20, rows=20) as terminal:
            terminal.write(
                b"\x1b[?6h\x1b[?69h\x1b[6;16s\x1b[6;16r"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 5))
            terminal.write(b"\x1b[2;2H")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 6))

    def make_erase_fixture(self, *, save_lines=20):
        terminal = Shitty(columns=10, rows=4, save_lines=save_lines)
        terminal.write(
            put_rows(b"abcdefghij", b"klmnopqrst", b"0123456789")
            + b"\x1b[2;5H"
        )
        self.assertEqual(
            terminal.model_snapshot().lines,
            ["abcdefghij", "klmnopqrst", "0123456789", " " * 10],
        )
        return terminal

    def test_ed_directions_cursor_and_history_policy(self):
        terminal = self.make_erase_fixture()
        try:
            terminal.write(b"\x1b[2J")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" " * 10] * 4)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))
            self.assertEqual(terminal.scrollback_state()[0], 0)
        finally:
            terminal.close()

        terminal = self.make_erase_fixture()
        try:
            terminal.write(b"\x1b[1J")
            self.assertEqual(
                terminal.model_snapshot().lines,
                [" " * 10, " " * 5 + "pqrst", "0123456789", " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture()
        try:
            terminal.write(b"\x1b[2;99H\x1b[1J")
            self.assertEqual(
                terminal.model_snapshot().lines,
                [" " * 10, " " * 10, "0123456789", " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture()
        try:
            terminal.write(b"\x1b[J")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["abcdefghij", "klmn" + " " * 6, " " * 10, " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture()
        try:
            before = terminal.model_digest()
            terminal.write(b"\x1b[9J")
            self.assertEqual(terminal.model_digest(), before)
        finally:
            terminal.close()

    def test_el_directions_and_clamped_cursor(self):
        terminal = self.make_erase_fixture(save_lines=0)
        try:
            terminal.write(b"\x1b[2K")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["abcdefghij", " " * 10, "0123456789", " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture(save_lines=0)
        try:
            terminal.write(b"\x1b[1K")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["abcdefghij", " " * 5 + "pqrst", "0123456789", " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture(save_lines=0)
        try:
            terminal.write(b"\x1b[2;99H\x1b[1K")
            self.assertEqual(terminal.model_snapshot().lines[1], " " * 10)
        finally:
            terminal.close()

        terminal = self.make_erase_fixture(save_lines=0)
        try:
            terminal.write(b"\x1b[K")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["abcdefghij", "klmn" + " " * 6, "0123456789", " " * 10],
            )
        finally:
            terminal.close()

        terminal = self.make_erase_fixture(save_lines=0)
        try:
            before = terminal.model_digest()
            terminal.write(b"\x1b[9K")
            self.assertEqual(terminal.model_digest(), before)
        finally:
            terminal.close()

    def test_ind_and_ri_with_full_and_rectangular_regions(self):
        page = put_rows(b"abcdefghij", b"klmnopqrst", b"0123456789")

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(page)
            terminal.write(b"\x1b[3;1H\x1bD\x1bD")
            self.assertEqual(
                terminal.model_snapshot().lines,
                ["klmnopqrst", "0123456789", " " * 10, " " * 10],
            )

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(page)
            terminal.write(
                b"\x1b[2;3r\x1b[?69h\x1b[3;6s"
                b"\x1b[2;3H\x1bD\x1bD"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["abcdefghij", "kl2345qrst", "01" + " " * 4 + "6789", " " * 10],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(page)
            terminal.write(b"\x1b[2;1H\x1bM\x1bM")
            self.assertEqual(
                terminal.model_snapshot().lines,
                [" " * 10, "abcdefghij", "klmnopqrst", "0123456789"],
            )

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(page)
            terminal.write(
                b"\x1b[2;3r\x1b[?69h\x1b[3;6s"
                b"\x1b[3;3H\x1bM\x1bM"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                snapshot.lines,
                ["abcdefghij", "kl" + " " * 4 + "qrst", "01mnop6789", " " * 10],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

    @unittest.expectedFailure
    def test_reset_preserving_prompt_contract(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(
                b"abcdefghijklm\x1b[2;4H"
                b"\x1bH\x1b(0\x1b[?25l"
            )
            self.assertEqual(
                terminal.model_snapshot().lines[:2],
                ["abcdefghij", "klm       "],
            )
            operation = getattr(terminal, "reset_preserving_prompt", None)
            if operation is None:
                raise AssertionError(
                    "iTerm2's reset-preserving-prompt host operation is "
                    "not implemented by Shitty"
                )
            operation(preserve=True, modify_content=True)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["klm       "] + [" " * 10] * 3)
            self.assertEqual(
                tuple(i for i, stop in enumerate(terminal.tab_stops()) if stop),
                (0, 8),
            )
            self.assertEqual(terminal.charset_state(), (0, 0, 0, 0))
            self.assertEqual(terminal.cursor_state()[0], 1)

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"abcdefghijklm\x1b[2;4H")
            operation = terminal.reset_preserving_prompt
            operation(preserve=False, modify_content=True)
            self.assertEqual(terminal.model_snapshot().lines, [" " * 10] * 4)

    @unittest.expectedFailure
    def test_window_width_request_respects_host_policy(self):
        with Shitty(
            columns=10,
            rows=4,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(b"\x1b[8;4;6t")
            self.assertEqual(terminal.winsize(), (6, 4))
            self.assertEqual(terminal.read_actions(), ["WINDOW 8 4 6"])

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[8;4;6t")
            self.assertEqual(terminal.winsize(), (10, 4))
            self.assertEqual(terminal.read_actions(), [])

        with Shitty(
            columns=10,
            rows=4,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(fullscreen=True)
            terminal.write(b"\x1b[8;4;6t")
            self.assertEqual(terminal.winsize(), (10, 4))
            self.assertEqual(terminal.read_actions(), [])


if __name__ == "__main__":
    unittest.main()

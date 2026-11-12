# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import re
import unittest
from pathlib import Path

from harness import Shitty


UPSTREAM = (
    Path(__file__).parent
    / "windows_terminal"
    / "upstream"
    / "TerminalBufferTests.cpp"
)

UPSTREAM_METHODS = (
    "TestSimpleBufferWriting",
    "TestWrappingCharByChar",
    "TestWrappingALongString",
    "DontSnapToOutputTest",
    "TestResetClearTabStops",
    "TestAddTabStop",
    "TestClearTabStop",
    "TestGetForwardTab",
    "TestGetReverseTab",
    "TestURLPatternDetection",
)

TEST_100_CHARS = bytes(range(33, 127)) + bytes(range(33, 39))
TAB_STOPS = (3, 5, 6, 10, 15, 17)
CONTROL = 2


def stops(terminal):
    return tuple(
        column
        for column, present in enumerate(terminal.tab_stops())
        if column != 0 and present
    )


def move_to_column(column):
    return f"\x1b[{column + 1}G".encode()


def set_tab_stops(terminal, columns, replace=True):
    if replace:
        terminal.write(b"\x1b[3g")
    for column in columns:
        terminal.write(move_to_column(column) + b"\x1bH")


class WindowsTerminalBufferTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = UPSTREAM.read_text()
        methods = tuple(re.findall(r"TEST_METHOD\(([^)]+)\)", source))
        if methods != UPSTREAM_METHODS:
            raise AssertionError(
                f"upstream terminal buffer method manifest changed: {methods!r}"
            )

    def assert_wrapped_text(self, terminal):
        snapshot = terminal.snapshot()
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (20, 1))
        self.assertTrue(snapshot.cell(79, 0).wrapped)
        self.assertFalse(snapshot.cell(79, 1).wrapped)
        actual = (
            snapshot.lines[0].encode()
            + snapshot.lines[1][:20].encode()
        )
        self.assertEqual(actual, TEST_100_CHARS)

    def test_simple_buffer_writing(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            self.assertEqual(terminal.scrollback_state(), (0, 32, 32, 0))
            terminal.write(b"Hello World")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0][:11], "Hello World")
            self.assertEqual(terminal.scrollback_state(), (0, 32, 32, 0))

    def test_wrapping_char_by_char(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            for byte in TEST_100_CHARS:
                terminal.write(bytes((byte,)))
            self.assert_wrapped_text(terminal)

    def test_wrapping_a_long_string(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            terminal.write(TEST_100_CHARS)
            self.assert_wrapped_text(terminal)

    def test_dont_snap_to_output(self):
        with Shitty(columns=80, rows=32, save_lines=100) as probe:
            probe.write(b"x\n" * 1000)
            maximum_history = probe.scrollback_state()[0]

        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            self.assertEqual(terminal.scrollback_state(), (0, 32, 32, 0))

            terminal.write(b"x\n" * 39)
            self.assertEqual(terminal.snapshot().view_offset, 0)
            self.assertEqual(terminal.scrollback_state()[0], 8)

            terminal.wheel_up()
            anchored = terminal.snapshot().lines
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.write(b"x\n" * 8)
            self.assertEqual(terminal.snapshot().view_offset, 9)
            self.assertEqual(terminal.snapshot().lines, anchored)

            while terminal.scrollback_state()[0] < maximum_history:
                terminal.write(b"x\n")

            history = terminal.scrollback_state()[0]
            self.assertEqual(history, maximum_history)
            self.assertEqual(terminal.snapshot().view_offset, history - 7)
            self.assertEqual(terminal.snapshot().lines, anchored)

            terminal.write(b"x\n" * 3)
            self.assertEqual(terminal.snapshot().view_offset, history - 4)

            terminal.write(b"x\n" * 8)
            self.assertEqual(terminal.snapshot().view_offset, history)

    def test_reset_clear_tab_stops(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            expected = tuple(range(8, 80, 8))
            self.assertEqual(stops(terminal), expected)
            terminal.write(b"\x1b[3g")
            self.assertEqual(stops(terminal), ())
            terminal.write(b"\x1bc")
            self.assertEqual(stops(terminal), expected)

    def test_add_tab_stop(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            terminal.write(b"\x1b[3g")
            self.assertEqual(stops(terminal), ())

            for column, expected in (
                (12, (12,)),
                (4, (4, 12)),
                (30, (4, 12, 30)),
                (24, (4, 12, 24, 30)),
                (24, (4, 12, 24, 30)),
            ):
                terminal.write(move_to_column(column) + b"\x1bH")
                self.assertEqual(stops(terminal), expected)

    def test_clear_tab_stop(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            terminal.write(b"\x1b[3g")
            terminal.write(move_to_column(0) + b"\x1b[0g")
            self.assertEqual(stops(terminal), ())

            terminal.write(move_to_column(0) + b"\x1bH\x1b[0g")
            self.assertEqual(stops(terminal), ())

            terminal.write(move_to_column(1) + b"\x1bH")
            for column in (2, 0):
                terminal.write(move_to_column(column) + b"\x1b[0g")
                self.assertEqual(stops(terminal), (1,))
            terminal.write(b"\x1b[3g")

            for removed, expected in (
                (3, (5, 6, 10, 15, 17)),
                (5, (3, 6, 10, 15, 17)),
                (17, (3, 5, 6, 10, 15)),
                (0, TAB_STOPS),
            ):
                set_tab_stops(terminal, TAB_STOPS, replace=True)
                terminal.write(move_to_column(removed) + b"\x1b[0g")
                self.assertEqual(stops(terminal), expected)

    def test_get_forward_tab(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            set_tab_stops(terminal, TAB_STOPS)
            for column, expected in ((0, 3), (6, 10), (30, 79), (79, 79)):
                terminal.write(move_to_column(column) + b"\x1b[I")
                self.assertEqual(terminal.snapshot().cursor_x, expected)

    def test_get_reverse_tab(self):
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            set_tab_stops(terminal, TAB_STOPS)
            for column, expected in ((1, 0), (6, 5), (30, 17)):
                terminal.write(move_to_column(column) + b"\x1b[Z")
                self.assertEqual(terminal.snapshot().cursor_x, expected)

    def test_url_pattern_detection(self):
        before = b"<Before>"
        url = b"https://www.contoso.com"
        after = b"<After>"
        long_url = (
            b"https://www.contoso.com/this-is-a-very-long-path/"
            b"that-will-wrap-across-multiple-rows-in-the-terminal-buffer"
        )
        with Shitty(columns=80, rows=32, save_lines=100) as terminal:
            terminal.write(before + url + after)
            start = len(before)
            end = start + len(url) - 1
            self.assertEqual(terminal.hyperlink(start - 1, 0), "")
            self.assertEqual(terminal.hyperlink(start, 0), url.decode())
            self.assertEqual(terminal.hyperlink(end, 0), url.decode())
            self.assertEqual(terminal.hyperlink(end + 1, 0), "")

            terminal.write(b"\r\n\r\nWRAP>" + long_url)
            self.assertEqual(terminal.hyperlink(5, 2), long_url.decode())
            self.assertEqual(terminal.hyperlink(0, 3), long_url.decode())
            self.assertEqual(terminal.hyperlink(4, 2), "")

            terminal.write(b"filler\r\n" * 40)
            scroll_url = b"https://www.example.com/scrolled"
            terminal.write(scroll_url)
            snapshot = terminal.snapshot()
            self.assertEqual(
                terminal.hyperlink(0, snapshot.cursor_y),
                scroll_url.decode(),
            )

            viewport_url = b"https://www.example.com/viewport"
            terminal.write(b"\r\n" + viewport_url)
            snapshot = terminal.snapshot()
            self.assertEqual(
                terminal.hyperlink(0, snapshot.cursor_y),
                viewport_url.decode(),
            )
            terminal.pointer(
                2,
                2 + snapshot.cursor_y,
                modifiers=CONTROL,
            )
            state = terminal.desktop_state()
            begin = snapshot.cursor_y * snapshot.columns
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (begin, begin + len(viewport_url)),
            )

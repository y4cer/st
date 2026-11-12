# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import itertools
import re
from pathlib import Path
import unittest

from harness import Shitty as HostShitty, put_rows

def Shitty(**kwargs):
    # The ported conhost expectations assume bold brightens the palette
    # (FOREGROUND_INTENSITY); the terminal default is off now (issue 59).
    extra = kwargs.pop("extra_arguments", ())
    return HostShitty(extra_arguments=("-boldColors", *extra), **kwargs)



UPSTREAM = (
    Path(__file__).parent
    / "windows_terminal"
    / "upstream"
    / "ScreenBufferTests.cpp"
)

PORTED_METHODS = {
    "SingleAlternateBufferCreationTest",
    "MultipleAlternateBufferCreationTest",
    "MultipleAlternateBuffersFromMainCreationTest",
    "AlternateBufferCursorInheritanceTest",
    "TestReverseLineFeed",
    "TestResetClearTabStops",
    "TestAddTabStop",
    "TestClearTabStop",
    "TestGetForwardTab",
    "TestGetReverseTab",
    "TestAltBufferTabStops",
    "EraseAllTests",
    "InactiveControlCharactersTest",
    "VtResize",
    "VtResizeComprehensive",
    "VtResizeDECCOLM",
    "VtResizePreservingAttributes",
    "VtSoftResetCursorPosition",
    "VtSoftResetAltBufferCursorState",
    "VtScrollMarginsNewlineColor",
    "VtNewlinePastViewport",
    "VtNewlinePastEndOfBuffer",
    "VtNewlineOutsideMargins",
    "VtSetColorTable",
    "VtRestoreColorTableReport",
    "ResizeTraditionalDoesNotDoubleFreeAttrRows",
    "ResizeCursorUnchanged",
    "ResizeAltBuffer",
    "ResizeAltBufferGetScreenBufferInfo",
    "VtEraseAllPersistCursor",
    "VtEraseAllPersistCursorFillColor",
    "GetWordBoundary",
    "TestAltBufferCursorState",
    "TestAltBufferVtDispatching",
    "TestAltBufferRIS",
    "SetDefaultsIndividuallyBothDefault",
    "SetDefaultsTogether",
    "ReverseResetWithDefaultBackground",
    "BackspaceDefaultAttrs",
    "BackspaceDefaultAttrsWriteCharsLegacy",
    "BackspaceDefaultAttrsInPrompt",
    "SetGlobalColorTable",
    "SetColorTableThreeDigits",
    "SetDefaultForegroundColor",
    "SetDefaultBackgroundColor",
    "AssignColorAliases",
    "DeleteCharsNearEndOfLine",
    "DeleteCharsNearEndOfLineSimpleFirstCase",
    "DeleteCharsNearEndOfLineSimpleSecondCase",
    "DontResetColorsAboveVirtualBottom",
    "ScrollOperations",
    "InsertReplaceMode",
    "InsertChars",
    "DeleteChars",
    "HorizontalScrollOperations",
    "ScrollingWideCharsHorizontally",
    "EraseScrollbackTests",
    "EraseTests",
    "ProtectedAttributeTests",
    "ScrollUpInMargins",
    "ScrollDownInMargins",
    "InsertLinesInMargins",
    "DeleteLinesInMargins",
    "ReverseLineFeedInMargins",
    "LineFeedEscapeSequences",
    "ScrollLines256Colors",
    "SetLineFeedMode",
    "SetScreenMode",
    "SetOriginMode",
    "SetAutoWrapMode",
    "HardResetBuffer",
    "ClearAlternateBuffer",
    "TestExtendedTextAttributes",
    "TestExtendedTextAttributesWithColors",
    "CursorUpDownAcrossMargins",
    "CursorUpDownOutsideMargins",
    "CursorUpDownExactlyAtMargins",
    "CursorLeftRightAcrossMargins",
    "CursorLeftRightOutsideMargins",
    "CursorLeftRightExactlyAtMargins",
    "CursorNextPreviousLine",
    "CursorPositionRelative",
    "CursorSaveRestore",
    "ScreenAlignmentPattern",
    "TestCursorIsOn",
    "TestAddHyperlink",
    "TestAddHyperlinkCustomId",
    "TestAddHyperlinkCustomIdDifferentUri",
    "TestReflowEndOfLineColor",
    "TestReflowSmallerLongLineWithColor",
    "TestReflowBiggerLongLineWithColor",
    "RectangularAreaOperations",
    "CopyDoubleWidthRectangularArea",
    "DelayedWrapReset",
    "MultilineWrap",
}

CLASSIFIED_METHODS = {
    "GetWordBoundaryTrimZerosOn",
    "GetWordBoundaryTrimZerosOff",
    "RestoreDownAltBufferWithTerminalScrolling",
    "SnapCursorWithTerminalScrolling",
    "UpdateVirtualBottomWhenCursorMovesBelowIt",
    "UpdateVirtualBottomWithSetConsoleCursorPosition",
    "UpdateVirtualBottomAfterInternalSetViewportSize",
    "UpdateVirtualBottomAfterResizeWithReflow",
    "DontShrinkVirtualBottomDuringResizeWithReflowAtTop",
    "DontChangeVirtualBottomWithOffscreenLinefeed",
    "DontChangeVirtualBottomAfterResizeWindow",
    "DontChangeVirtualBottomWithMakeCursorVisible",
    "RetainHorizontalOffsetWhenMovingToBottom",
    "TestDeferredMainBufferResize",
    "EraseColorMode",
    "SimpleMarkCommand",
    "SimpleWrappedCommand",
    "SimplePromptRegions",
}


def upstream_methods():
    source = UPSTREAM.read_text()
    return set(re.findall(r"TEST_METHOD\((\w+)\);", source))


def tab_columns(terminal, columns):
    return tuple(
        column
        for column, present in enumerate(terminal.tab_stops(columns))
        if present
    )


def replace_tab_stops(terminal, columns):
    terminal.write(b"\x1b[3g")
    for column in columns:
        terminal.write(f"\x1b[{column + 1}G\x1bH".encode())


def window_terminal(columns=10, rows=4, **kwargs):
    return Shitty(
        columns=columns,
        rows=rows,
        extra_arguments=("-allowWindowOps", "true"),
        **kwargs,
    )


def palette_color(terminal, index):
    terminal.write(f"\x1b]4;{index};?\x1b\\".encode())
    reply = terminal.read_input()
    match = re.fullmatch(
        rb"\x1b\]4;" + str(index).encode()
        + rb";rgb:([0-9a-f]{4})/([0-9a-f]{4})/([0-9a-f]{4})\x1b\\",
        reply,
    )
    if match is None:
        raise AssertionError(f"invalid palette reply: {reply!r}")
    return tuple(int(component[:2], 16) for component in match.groups())


def select_word(terminal, column, row=0):
    x = column + 2
    y = row + 2
    terminal.button(0, True, x=x, y=y, time=1.0)
    terminal.button(0, False, x=x, y=y, time=1.01)
    terminal.button(0, True, x=x, y=y, time=1.1)
    return terminal.button(0, False, x=x, y=y, time=1.11)


class WindowsTerminalScreenBufferInitialTest(unittest.TestCase):
    def test_upstream_inventory_has_all_113_methods(self):
        methods = upstream_methods()
        self.assertEqual(len(methods), 113)
        self.assertLessEqual(PORTED_METHODS, methods)
        self.assertLessEqual(CLASSIFIED_METHODS, methods)
        self.assertFalse(PORTED_METHODS & CLASSIFIED_METHODS)

    def test_single_alternate_buffer_creation(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"main\x1b[?1049h")
            alternate = terminal.snapshot()
            self.assertEqual(alternate.lines, [" " * 10] * 4)

            terminal.write(b"alternate\x1b[?1049l")
            primary = terminal.snapshot()
            self.assertEqual(primary.lines[0], "main      ")
            self.assertEqual((primary.cursor_x, primary.cursor_y), (4, 0))

    def test_multiple_alternate_buffer_creation(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(
                b"main\x1b[?47hfirst\x1b[?47h-second\x1b[?47l"
            )
            primary = terminal.snapshot()
            self.assertEqual(primary.lines[0], "main      ")

            terminal.write(b"\x1b[?47h")
            alternate = terminal.snapshot()
            self.assertEqual(alternate.lines[0], "    first-")
            self.assertEqual(alternate.lines[1], "second    ")

    def test_multiple_alternate_buffers_from_main_creation(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(
                b"main"
                b"\x1b[?1047hfirst"
                b"\x1b[?1047l"
                b"\x1b[?1047hsecond"
                b"\x1b[?1047l"
            )
            self.assertEqual(terminal.snapshot().lines[0], "main      ")

            terminal.write(b"\x1b[?1047h")
            self.assertEqual(terminal.snapshot().lines, [" " * 10] * 4)

    def test_alternate_buffer_cursor_inheritance(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"\x1b[3;4H\x1b[?25l\x1b[5 q"
                b"\x1b[?1049h"
            )
            alternate = terminal.snapshot()
            self.assertEqual((alternate.cursor_x, alternate.cursor_y), (3, 2))
            self.assertEqual(alternate.cursor_style, 0)

            terminal.write(
                b"\x1b[2;6H\x1b[?25h\x1b[3 q"
                b"\x1b[?1049l"
            )
            primary = terminal.snapshot()
            self.assertEqual((primary.cursor_x, primary.cursor_y), (3, 2))
            self.assertNotEqual(primary.cursor_style, 0)

    def test_reverse_line_feed(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"foo\nfoo\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 0))

        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"123456789\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))
            self.assertEqual(snapshot.lines[0], " " * 10)
            self.assertEqual(snapshot.lines[1], "123456789 ")

    def test_reset_clear_tab_stops(self):
        expected = (0, *range(8, 80, 8))
        with Shitty(columns=80, rows=2) as terminal:
            self.assertEqual(tab_columns(terminal, 80), expected)

            terminal.write(b"\x1b[3g")
            self.assertEqual(tab_columns(terminal, 80), ())

            terminal.write(b"\x1bc")
            self.assertEqual(tab_columns(terminal, 80), expected)

            terminal.write(b"\x1b[3g\x1b[?5W")
            self.assertEqual(tab_columns(terminal, 80), expected)

            terminal.write(b"\x1b[3g\x1b[?W")
            self.assertEqual(tab_columns(terminal, 80), expected)

    def test_add_tab_stop(self):
        with Shitty(columns=40, rows=2) as terminal:
            terminal.write(b"\x1b[3g")
            expected = []
            for column in (12, 4, 30, 24, 24):
                terminal.write(f"\x1b[{column + 1}G\x1bH".encode())
                if column not in expected:
                    expected.append(column)
                    expected.sort()
                self.assertEqual(tab_columns(terminal, 40), tuple(expected))

    def test_clear_tab_stop(self):
        with Shitty(columns=40, rows=2) as terminal:
            terminal.write(b"\x1b[3g\x1b[g")
            self.assertEqual(tab_columns(terminal, 40), ())

            terminal.write(b"\x1b[H\x1b[g")
            self.assertEqual(tab_columns(terminal, 40), ())

            replace_tab_stops(terminal, (1,))
            terminal.write(b"\x1b[3G\x1b[g\x1b[1G\x1b[g")
            self.assertEqual(tab_columns(terminal, 40), (1,))

            for removed in (3, 5, 17, 0):
                expected = [3, 5, 6, 10, 15, 17]
                replace_tab_stops(terminal, expected)
                terminal.write(f"\x1b[{removed + 1}G\x1b[g".encode())
                if removed in expected:
                    expected.remove(removed)
                self.assertEqual(tab_columns(terminal, 40), tuple(expected))

    def test_get_forward_tab(self):
        with Shitty(columns=40, rows=2) as terminal:
            replace_tab_stops(terminal, (3, 5, 6, 10, 15, 17))
            for start, expected in ((0, 3), (6, 10), (30, 39), (39, 39)):
                terminal.write(f"\x1b[{start + 1}G\x1b[I".encode())
                self.assertEqual(terminal.snapshot().cursor_x, expected)

    def test_get_reverse_tab(self):
        with Shitty(columns=40, rows=2) as terminal:
            replace_tab_stops(terminal, (3, 5, 6, 10, 15, 17))
            for start, expected in ((1, 0), (6, 5), (30, 17)):
                terminal.write(f"\x1b[{start + 1}G\x1b[Z".encode())
                self.assertEqual(terminal.snapshot().cursor_x, expected)

    def test_alternate_buffer_tab_stops(self):
        with Shitty(columns=40, rows=2) as terminal:
            replace_tab_stops(terminal, (3, 5, 6, 10, 15, 17))
            terminal.write(b"\x1b[?47h")
            self.assertEqual(
                tab_columns(terminal, 40), (3, 5, 6, 10, 15, 17)
            )

            replace_tab_stops(terminal, (4, 8, 12, 16))
            terminal.write(b"\x1b[?47l")
            self.assertEqual(tab_columns(terminal, 40), (4, 8, 12, 16))

    def test_erase_all_uses_terminal_not_win32_viewport_semantics(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"foo\r\nbar\x1b[2J")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, [" " * 10] * 4)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))

    def test_inactive_control_characters(self):
        controls = (
            0, 1, 2, 3, 4, 5, 6, 7,
            14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
            28, 29, 30, 31,
        )
        for ordinal in controls:
            with self.subTest(ordinal=ordinal), Shitty(
                columns=10, rows=3
            ) as terminal:
                control = bytes((ordinal,))
                terminal.write(control)
                self.assertEqual(
                    (terminal.snapshot().cursor_x,
                     terminal.snapshot().cursor_y),
                    (0, 0),
                )

                terminal.write(control * 8)
                self.assertEqual(
                    (terminal.snapshot().cursor_x,
                     terminal.snapshot().cursor_y),
                    (0, 0),
                )

                terminal.write(control + b"foo\r\n")
                terminal.write(
                    control + b"foo" + control + b"bar" + control
                )
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 1))


class WindowsTerminalScreenBufferResizeAndColorTest(unittest.TestCase):
    def test_vt_resize(self):
        with window_terminal(glyph_px=8, glyph_py=16) as terminal:
            for rows, columns in ((30, 80), (40, 80), (40, 90), (12, 12)):
                terminal.write(f"\x1b[8;{rows};{columns}t".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.columns, snapshot.rows), (columns, rows))

            terminal.write(b"\x1b[8;0;0t")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (239, 67))

    def test_vt_resize_comprehensive(self):
        for delta_columns in (-10, -1, 0, 1, 10):
            for delta_rows in (-10, -1, 0, 1, 10):
                with self.subTest(
                    delta_columns=delta_columns,
                    delta_rows=delta_rows,
                ), window_terminal(columns=80, rows=24) as terminal:
                    columns = 80 + delta_columns
                    rows = 24 + delta_rows
                    terminal.write(f"\x1b[8;{rows};{columns}t".encode())
                    snapshot = terminal.snapshot()
                    self.assertEqual(
                        (snapshot.columns, snapshot.rows),
                        (columns, rows),
                    )

    def test_vt_resize_deccolm(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"\x1b[5;15r\x1b[10;40HABCDEF\x1b[?3h")
            unchanged = terminal.snapshot()
            self.assertEqual((unchanged.columns, unchanged.rows), (80, 24))
            self.assertEqual(
                (unchanged.cursor_x, unchanged.cursor_y),
                (45, 9),
            )

            terminal.write(b"\x1b[?40h\x1b[?3h")
            wide = terminal.snapshot()
            self.assertEqual((wide.columns, wide.rows), (132, 24))
            self.assertEqual((wide.cursor_x, wide.cursor_y), (0, 0))
            terminal.write(b"\x1b[9999B")
            self.assertEqual(terminal.snapshot().cursor_y, 23)

            terminal.write(
                b"\x1b[5;15r\x1b[10;40HABCDEF\x1b[?40l\x1b[?3l"
            )
            disallowed = terminal.snapshot()
            self.assertEqual((disallowed.columns, disallowed.rows), (132, 24))
            self.assertEqual(
                (disallowed.cursor_x, disallowed.cursor_y),
                (45, 9),
            )

            terminal.write(b"\x1b[?40h\x1b[?3l")
            narrow = terminal.snapshot()
            self.assertEqual((narrow.columns, narrow.rows), (80, 24))
            self.assertEqual((narrow.cursor_x, narrow.cursor_y), (0, 0))
            terminal.write(b"\x1b[9999B")
            self.assertEqual(terminal.snapshot().cursor_y, 23)

    def test_vt_resize_preserving_attributes(self):
        attributes = (
            b"\x1b[3;4:3;9;"
            b"38;2;12;34;56;48;2;78;90;12;58;2;188;20;24m"
        )
        for resize in ("host", "deccolm"):
            with self.subTest(resize=resize), Shitty(
                columns=80,
                rows=24,
            ) as terminal:
                terminal.write(attributes)
                before = terminal.pen_state()
                if resize == "host":
                    terminal.resize(132, 24)
                    terminal.resize(80, 24)
                else:
                    terminal.write(b"\x1b[?40h\x1b[?3h\x1b[?3l")
                self.assertEqual(terminal.pen_state(), before)

    def test_vt_soft_reset_cursor_position(self):
        with Shitty(columns=20, rows=12) as terminal:
            terminal.write(b"\x1b[2;2H\x1b[!p")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

            terminal.write(b"\x1b[2;10r")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[2;2H\x1b[!p")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

            terminal.write(b"\x1b[?6h\x1b[5;10r\x1b[2;2H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 5))

            terminal.write(b"\x1b[!p\x1b[5;10r\x1b[2;2H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_vt_soft_reset_alt_buffer_cursor_state(self):
        with Shitty(columns=12, rows=6) as terminal:
            terminal.write(
                b"\x1b[4;7H"
                b"\x1b[?1049h\x1b[!p\x1b[?1049l"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 3))

    def test_vt_scroll_margins_newline_color(self):
        with Shitty(columns=12, rows=10) as terminal:
            terminal.write(
                b"\x1b]10;#ffff00\x1b\\"
                b"\x1b]11;#ff00ff\x1b\\"
                b"\x1b[2J\x1b[m\x1b[2;5r"
            )
            for _ in range(10):
                terminal.write(b"X\n")
                snapshot = terminal.snapshot()
                for cell in snapshot.cells:
                    self.assertEqual(cell.foreground, (255, 255, 0))
                    self.assertEqual(cell.background, (255, 0, 255))

    def assert_bottom_row_uses_erase_colors(self, terminal):
        snapshot = terminal.snapshot()
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))
        for column in range(snapshot.columns):
            cell = snapshot.cell(column, 3)
            self.assertEqual(cell.foreground, (12, 34, 56))
            self.assertEqual(cell.background, (78, 90, 12))
            self.assertFalse(cell.italic)
            self.assertFalse(cell.underline)
            self.assertFalse(cell.inverse)
            self.assertFalse(cell.strike)

    def test_vt_newline_past_viewport(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"\x1b[2J\x1b[4;1H"
                b"\x1b[3;4:3;7;9;"
                b"38;2;12;34;56;48;2;78;90;12m\n"
            )
            self.assert_bottom_row_uses_erase_colors(terminal)

    def test_vt_newline_past_end_of_buffer(self):
        with Shitty(columns=8, rows=4, save_lines=4) as terminal:
            terminal.write(
                b"\x1b[2J"
                + b"\n" * 16
                + b"\x1b[3;4:3;7;9;"
                b"38;2;12;34;56;48;2;78;90;12m\n"
            )
            self.assert_bottom_row_uses_erase_colors(terminal)

    def test_vt_newline_outside_margins(self):
        with Shitty(columns=8, rows=8) as terminal:
            terminal.write(b"\x1b[8;1H\n")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 7))

            terminal.write(b"\x1b[1;5r\x1b[8;1H\n")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 7))

    def test_vt_set_color_table(self):
        valid = (
            (0, b"rgb:1/1/1", (0x11, 0x11, 0x11), b"\x07"),
            (1, b"rgb:1/23/1", (0x11, 0x23, 0x11), b"\x07"),
            (2, b"rgb:1/23/12", (0x11, 0x23, 0x12), b"\x07"),
            (3, b"rgb:12/23/12", (0x12, 0x23, 0x12), b"\x07"),
            (4, b"rgb:ff/a1/1b", (0xFF, 0xA1, 0x1B), b"\x07"),
            (5, b"rgb:ff/a1/1b", (0xFF, 0xA1, 0x1B), b"\x1b\\"),
        )
        invalid = (
            b"rgb:/1/1",
            b"rgb:1/1/1/1",
            b"rgb:1//1",
            b"rgb://",
            b"rgb:1/11/",
            b"cmyk:1/1/1",
            b"1/1/1",
        )
        with Shitty(columns=4, rows=2) as terminal:
            for index, color, expected, terminator in valid:
                terminal.write(
                    b"\x1b]4;" + str(index).encode() + b";"
                    + color + terminator
                )
                self.assertEqual(palette_color(terminal, index), expected)

            terminal.write(b"\x1b]4;5;rgb:09/09/09\x1b\\")
            for color in invalid:
                terminal.write(b"\x1b]4;5;" + color + b"\x1b\\")
                self.assertEqual(palette_color(terminal, 5), (9, 9, 9))
            terminal.write(b"\x1b]4;5;rgbi:1/1/1\x1b\\")
            self.assertEqual(palette_color(terminal, 5), (255, 255, 255))
            terminal.write(b"\x1b]4;;rgb:1/1/1\x1b\\")
            self.assertEqual(palette_color(terminal, 5), (255, 255, 255))

    def test_vt_restore_color_table_report(self):
        hls = (
            (0, 0, 0, 0, (0, 0, 0)),
            (1, 0, 49, 59, (51, 51, 199)),
            (2, 120, 46, 71, (201, 34, 34)),
            (3, 240, 49, 59, (51, 199, 51)),
            (4, 60, 49, 59, (199, 51, 199)),
            (5, 300, 49, 59, (51, 199, 199)),
            (6, 180, 49, 59, (199, 199, 51)),
            (7, 0, 46, 0, (117, 117, 117)),
            (8, 0, 26, 0, (66, 66, 66)),
            (9, 0, 46, 28, (84, 84, 150)),
            (10, 120, 42, 38, (148, 66, 66)),
            (11, 240, 46, 28, (84, 150, 84)),
            (12, 60, 46, 28, (150, 84, 150)),
            (13, 300, 46, 28, (84, 150, 150)),
            (14, 180, 46, 28, (150, 150, 84)),
            (15, 0, 79, 0, (201, 201, 201)),
        )
        rgb = (
            (0, 0, 0, 0, (0, 0, 0)),
            (1, 20, 20, 78, (51, 51, 199)),
            (2, 79, 13, 13, (201, 33, 33)),
            (3, 20, 78, 20, (51, 199, 51)),
            (4, 78, 20, 78, (199, 51, 199)),
            (5, 20, 78, 78, (51, 199, 199)),
            (6, 78, 78, 20, (199, 199, 51)),
            (7, 46, 46, 46, (117, 117, 117)),
            (8, 26, 26, 26, (66, 66, 66)),
            (9, 33, 33, 59, (84, 84, 150)),
            (10, 58, 26, 26, (148, 66, 66)),
            (11, 33, 59, 33, (84, 150, 84)),
            (12, 59, 33, 59, (150, 84, 150)),
            (13, 33, 59, 59, (84, 150, 150)),
            (14, 59, 59, 33, (150, 150, 84)),
            (15, 79, 79, 79, (201, 201, 201)),
        )
        with Shitty(columns=4, rows=2) as terminal:
            original = tuple(
                palette_color(terminal, index) for index in range(16)
            )
            for color_space, cases in ((1, hls), (2, rgb)):
                for index, first, second, third, expected in cases:
                    terminal.write(
                        f"\x1bP2$p{index};{color_space};"
                        f"{first};{second};{third}\x1b\\".encode()
                    )
                    self.assertEqual(palette_color(terminal, index), expected)

            terminal.write(
                b"\x1bP2$p"
                b"0;1;120;50;100/2;1;240;50;100/4;1;360;50;100"
                b"\x1b\\"
                b"\x1bP2$p"
                b"1;2;100;0;0/3;2;0;100;0/5;2;0;0;100"
                b"\x1b\\"
            )
            for index, expected in enumerate(
                (
                    (255, 0, 0),
                    (255, 0, 0),
                    (0, 255, 0),
                    (0, 255, 0),
                    (0, 0, 255),
                    (0, 0, 255),
                )
            ):
                self.assertEqual(palette_color(terminal, index), expected)

            omitted_and_clamped = (
                (6, b"1;;50;100", (0, 0, 255)),
                (7, b"1;120;;100", (0, 0, 0)),
                (8, b"1;120;50", (128, 128, 128)),
                (6, b"2;;50;100", (0, 128, 255)),
                (7, b"2;50;;100", (128, 0, 255)),
                (8, b"2;50;100", (128, 255, 0)),
                (9, b"1;480;50;100", (255, 0, 0)),
                (10, b"1;240;150;100", (255, 255, 255)),
                (11, b"1;0;50;120", (0, 0, 255)),
                (12, b"2;150;0;0", (255, 0, 0)),
                (13, b"2;0;150;0", (0, 255, 0)),
                (14, b"2;0;0;150", (0, 0, 255)),
            )
            for index, definition, expected in omitted_and_clamped:
                terminal.write(
                    b"\x1bP2$p" + str(index).encode() + b";"
                    + definition + b"\x1b\\"
                )
                self.assertEqual(palette_color(terminal, index), expected)

            terminal.write(b"\x1bc")
            self.assertEqual(
                tuple(
                    palette_color(terminal, index)
                    for index in range(16)
                ),
                original,
            )


class WindowsTerminalScreenBufferResizeEraseAndAltTest(unittest.TestCase):
    def test_resize_traditional_does_not_double_free_attr_rows(self):
        with Shitty(columns=12, rows=6, save_lines=0) as terminal:
            terminal.write(b"\x1b[31;44mone\r\ntwo\r\nthree")
            terminal.resize(12, 5)
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.columns, snapshot.rows), (12, 5))
            self.assertIn("three", "".join(snapshot.lines))

    def test_resize_cursor_unchanged(self):
        for alternate in (False, True):
            with self.subTest(alternate=alternate), Shitty(
                columns=80,
                rows=24,
            ) as terminal:
                terminal.write(b"\x1b[5 q")
                if alternate:
                    terminal.write(b"\x1b[?1049h")
                expected_style = terminal.snapshot().cursor_style
                self.assertNotEqual(expected_style, 0)
                for delta_columns in (-10, -1, 0, 1, 10):
                    for delta_rows in (-10, -1, 0, 1, 10):
                        terminal.resize(
                            80 + delta_columns,
                            24 + delta_rows,
                        )
                        self.assertEqual(
                            terminal.snapshot().cursor_style,
                            expected_style,
                        )
                if alternate:
                    terminal.write(b"\x1b[?1049l")
                    self.assertEqual(
                        terminal.snapshot().cursor_style,
                        expected_style,
                    )

    def test_resize_alt_buffer(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"primary\x1b[?1049h\x1b[Halt")
            terminal.resize(12, 6)
            alternate = terminal.snapshot()
            self.assertEqual(
                (alternate.columns, alternate.rows),
                (12, 6),
            )
            self.assertEqual(alternate.lines[0], "alt" + " " * 9)

            terminal.write(b"\x1b[?1049l")
            primary = terminal.snapshot()
            self.assertEqual((primary.columns, primary.rows), (12, 6))
            self.assertEqual(primary.lines[0], "primary" + " " * 5)

    def test_resize_alt_buffer_get_screen_buffer_info(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"\x1b[?1049h")
            for delta_columns in (-10, -1, 1, 10):
                for delta_rows in (-10, -1, 1, 10):
                    columns = 80 + delta_columns
                    rows = 24 + delta_rows
                    terminal.resize(columns, rows)
                    snapshot = terminal.snapshot()
                    self.assertEqual(
                        (snapshot.columns, snapshot.rows),
                        (columns, rows),
                    )
                    self.assertEqual(terminal.winsize(), (columns, rows))

    def test_vt_erase_all_persist_cursor(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[2;2H\x1b[2J")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(snapshot.lines, [" " * 10] * 4)

    def test_vt_erase_all_persist_cursor_fill_color(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[31;104mtext\x1b[2J")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            for cell in snapshot.cells:
                self.assertEqual(cell.char, " ")
                self.assertEqual(cell.foreground, (170, 0, 0))
                self.assertEqual(cell.background, (85, 85, 255))

    def test_get_word_boundary(self):
        text = b"This is some test text for word boundaries."
        cases = (
            (0, b"This"),
            (1, b"This"),
            (3, b"This"),
            (13, b"test"),
            (15, b"test"),
            (16, b"test"),
            (32, b"boundaries"),
            (39, b"boundaries"),
            (41, b"boundaries"),
            (12, b" "),
        )
        for column, expected in cases:
            with self.subTest(column=column), Shitty(
                columns=len(text),
                rows=2,
            ) as terminal:
                terminal.write(text)
                self.assertEqual(select_word(terminal, column), expected)

    def test_alt_buffer_vt_dispatching(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(
                b"P"
                b"\x1b[?1049h"
                b"\x1b[5;6H\x1b[48;2;255;0;255mX"
            )
            alternate = terminal.snapshot()
            self.assertEqual((alternate.cursor_x, alternate.cursor_y), (6, 4))
            self.assertEqual(alternate.cell(5, 4).char, "X")
            self.assertEqual(alternate.cell(5, 4).background, (255, 0, 255))

            terminal.write(b"\x1b[?1049l")
            primary = terminal.snapshot()
            self.assertEqual((primary.cursor_x, primary.cursor_y), (1, 0))
            self.assertEqual(primary.lines[0], "P" + " " * 9)

    def test_alt_buffer_ris(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"primary\x1b[?1049halt\x1bc")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.lines, [" " * 10] * 4)

            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.snapshot().lines, [" " * 10] * 4)


class WindowsTerminalScreenBufferDefaultColorTest(unittest.TestCase):
    def test_set_defaults_individually_both_default(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;#ffff00\x1b\\"
                b"\x1b]11;#ff00ff\x1b\\"
                b"\x1b[mX"
                b"\x1b[92;44mX"
                b"\x1b[39mX"
                b"\x1b[49mX"
                b"\x1b[92;44mX"
                b"\x1b[49mX"
            )
            cells = terminal.snapshot().cells[:6]
            self.assertEqual(
                [(cell.foreground, cell.background) for cell in cells],
                [
                    ((255, 255, 0), (255, 0, 255)),
                    ((85, 255, 85), (0, 0, 170)),
                    ((255, 255, 0), (0, 0, 170)),
                    ((255, 255, 0), (255, 0, 255)),
                    ((85, 255, 85), (0, 0, 170)),
                    ((85, 255, 85), (255, 0, 255)),
                ],
            )
            self.assertEqual(
                [
                    (cell.foreground_index, cell.background_index)
                    for cell in terminal.model_snapshot().cells[:6]
                ],
                [(-2, -2), (10, 4), (-2, 4), (-2, -2), (10, 4), (10, -2)],
            )

    def test_set_defaults_together(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;#ffff00\x1b\\"
                b"\x1b]11;#ff00ff\x1b\\"
                b"\x1b[mX\x1b[48;5;250mX\x1b[39;49mX"
            )
            cells = terminal.snapshot().cells[:3]
            self.assertEqual(
                [(cell.foreground, cell.background) for cell in cells],
                [
                    ((255, 255, 0), (255, 0, 255)),
                    ((255, 255, 0), (188, 188, 188)),
                    ((255, 255, 0), (255, 0, 255)),
                ],
            )
            self.assertEqual(
                terminal.model_snapshot().cell(1, 0).background_index,
                250,
            )

    def test_reverse_reset_with_default_background(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(
                b"\x1b]11;#ff00ff\x1b\\"
                b"X\x1b[7mX\x1b[27mX"
            )
            cells = terminal.snapshot().cells[:3]
            self.assertEqual(
                [cell.inverse for cell in cells],
                [False, True, False],
            )
            for cell in cells:
                self.assertEqual(cell.background, (255, 0, 255))

    def test_backspace_default_attrs(self):
        for chunked in (False, True):
            with self.subTest(chunked=chunked), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(b"\x1b]11;#ff00ff\x1b\\\x1b[m")
                if chunked:
                    terminal.write_chunks(b"X", b"X", b"\x08")
                else:
                    terminal.write(b"XX\x08")
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
                for cell in snapshot.cells[:2]:
                    self.assertEqual(cell.char, "X")
                    self.assertEqual(cell.background, (255, 0, 255))
                    self.assertEqual(cell.background_index, -2)

    def test_backspace_default_attrs_in_prompt(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(
                b"\x1b]11;#ff00ff\x1b\\"
                b"\x1b[m\x1b[2J"
                b"XXX\x1b[2D\x1b[P"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(snapshot.lines[0], "XX" + " " * 8)
            for cell in snapshot.cells:
                self.assertEqual(cell.background, (255, 0, 255))
                self.assertEqual(cell.background_index, -2)

    def test_set_global_color_table(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[41mX\x1b[?1049h\x1b[H\x1b[41mX")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).background,
                (170, 0, 0),
            )
            terminal.write(b"\x1b]4;1;rgb:11/22/33\x07X")
            alternate = terminal.snapshot()
            self.assertEqual(
                [alternate.cell(column, 0).background for column in (0, 1)],
                [(0x11, 0x22, 0x33)] * 2,
            )

            terminal.write(b"\x1b[?1049lX")
            primary = terminal.snapshot()
            self.assertEqual(
                [primary.cell(column, 0).background for column in (0, 1)],
                [(0x11, 0x22, 0x33)] * 2,
            )

    def test_set_color_table_three_digits(self):
        with Shitty(columns=5, rows=2) as terminal:
            original = palette_color(terminal, 123)
            terminal.write(
                b"\x1b[48;5;123mX"
                b"\x1b]4;123;rgb:11/22/33\x07X"
            )
            snapshot = terminal.snapshot()
            self.assertNotEqual(original, (0x11, 0x22, 0x33))
            self.assertEqual(
                [snapshot.cell(column, 0).background for column in (0, 1)],
                [(0x11, 0x22, 0x33)] * 2,
            )

    def test_set_default_foreground_color(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b]10;rgb:33/66/99\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).foreground,
                (0x33, 0x66, 0x99),
            )
            terminal.write(b"\x1b]10;rgb:ff/ff/ff\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(1, 0).foreground,
                (255, 255, 255),
            )
            terminal.write(b"\x1b]10;99/66/33\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(2, 0).foreground,
                (255, 255, 255),
            )

    def test_set_default_background_color(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b]11;rgb:33/66/99\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).background,
                (0x33, 0x66, 0x99),
            )
            terminal.write(b"\x1b]11;rgb:ff/ff/ff\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(1, 0).background,
                (255, 255, 255),
            )
            terminal.write(b"\x1b]11;99/66/33\x1b\\X")
            self.assertEqual(
                terminal.snapshot().cell(2, 0).background,
                (255, 255, 255),
            )

    def test_assign_color_aliases(self):
        with Shitty(columns=6, rows=2) as terminal:
            foreground = palette_color(terminal, 23)
            background = palette_color(terminal, 45)
            terminal.write(b"A\x1b[0;12;34,|B")
            unchanged = terminal.snapshot()
            self.assertEqual(
                unchanged.cell(0, 0).foreground,
                unchanged.cell(1, 0).foreground,
            )
            self.assertEqual(
                unchanged.cell(0, 0).background,
                unchanged.cell(1, 0).background,
            )

            terminal.write(b"\x1b[1;23;45,|C")
            assigned = terminal.snapshot().cell(2, 0)
            self.assertEqual(assigned.foreground, foreground)
            self.assertEqual(assigned.background, background)

            terminal.write(b"\x1bcD")
            reset = terminal.snapshot().cell(0, 0)
            self.assertEqual(reset.foreground, (255, 255, 255))
            self.assertEqual(reset.background, (0, 0, 0))


class WindowsTerminalScreenBufferEditingTest(unittest.TestCase):
    def assert_erase_cells(self, snapshot, row, begin, end):
        for column in range(begin, end):
            cell = snapshot.cell(column, row)
            self.assertEqual(cell.char, " ")
            self.assertEqual(
                (cell.foreground, cell.background),
                ((12, 34, 56), (78, 90, 12)),
            )
            self.assertFalse(cell.strike)
            self.assertFalse(cell.inverse)
            self.assertEqual(cell.underline_style, 0)

    @staticmethod
    def editing_row(terminal, row=10):
        terminal.write(
            b"\x1b[31;44m"
            + f"\x1b[{row + 1};1H".encode()
            + b"Q" * 40
            + f"\x1b[{row + 1};11H".encode()
            + b"ABCDEFGHIJKLMNOPQRST"
        )

    @staticmethod
    def set_editing_margins(terminal, vertical):
        terminal.write(
            b"\x1b[?69h\x1b[11;30s"
            + (b"\x1b[15;20r" if vertical else b"\x1b[r")
        )

    @staticmethod
    def set_erase_attributes(terminal):
        terminal.write(
            b"\x1b[38;2;12;34;56;48;2;78;90;12;9;7;4:3m"
        )

    def test_delete_chars_near_end_of_line(self):
        distances = (1, 2, 3, 5, 8, 13, 21, 34)
        counts = (1, 2, 3, 5, 8, 13, 21, 34)
        width = 80
        for distance in distances:
            for count in counts:
                with self.subTest(distance=distance, count=count), Shitty(
                    columns=width,
                    rows=2,
                ) as terminal:
                    column = width - distance
                    terminal.write(
                        b"X" * width
                        + f"\x1b[1;{column + 1}H\x1b[{count}P".encode()
                    )
                    snapshot = terminal.snapshot()
                    erased = min(distance, count)
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (column, 0),
                    )
                    self.assertEqual(
                        snapshot.lines[0],
                        "X" * (width - erased) + " " * erased,
                    )

    def test_delete_chars_near_end_of_line_simple_first_case(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"ABCDEFG\x1b[1;4H\x1b[3P")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))
            self.assertEqual(snapshot.lines[0], "ABCG    ")

    def test_delete_chars_near_end_of_line_simple_second_case(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"ABCDEFG\x1b[1;3H\x1b[4P")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertEqual(snapshot.lines[0], "ABG     ")

    def test_scrollback_write_does_not_reset_history_colors(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                b"\x1b[31;44mX\x1b[mX"
                b"\r\nL1\r\nL2\r\nL3"
            )
            terminal.wheel_up(1)
            before = terminal.snapshot()
            self.assertEqual(before.view_offset, 1)
            self.assertEqual(before.lines[0], "XX      ")
            self.assertEqual(
                (before.cell(0, 0).foreground,
                 before.cell(0, 0).background),
                ((170, 0, 0), (0, 0, 170)),
            )
            self.assertEqual(
                (before.cell(1, 0).foreground,
                 before.cell(1, 0).background),
                ((255, 255, 255), (0, 0, 0)),
            )

            terminal.write(b"X")
            after = terminal.snapshot()
            self.assertEqual(after.cells, before.cells)

            terminal.wheel_down(1)
            live = terminal.snapshot()
            self.assertEqual(live.lines[-1], "L3X     ")

    def test_scroll_operations(self):
        operations = (
            ("SU", b"S", "up", False),
            ("SD", b"T", "down", False),
            ("IL", b"L", "down", True),
            ("DL", b"M", "up", True),
            ("RI", b"", "down", False),
        )
        initial = [chr(ord("A") + row) for row in range(10)]
        top = 1
        bottom = 9
        cursor_row = 4
        for name, final, direction, from_cursor in operations:
            for count in (1, 2, 5):
                with self.subTest(operation=name, count=count), Shitty(
                    columns=8,
                    rows=10,
                    save_lines=0,
                ) as terminal:
                    row = top if name == "RI" else cursor_row
                    sequence = (
                        b"\x1bM" * count
                        if name == "RI"
                        else b"\x1b[" + str(count).encode() + final
                    )
                    terminal.write(
                        put_rows(*(value.encode() for value in initial))
                        + b"\x1b[2;9r"
                        + f"\x1b[{row + 1};5H".encode()
                        + b"\x1b[38;2;12;34;56;48;2;78;90;12;9;7;4:3m"
                        + sequence
                    )

                    scroll_top = cursor_row if from_cursor else top
                    expected = initial.copy()
                    region = expected[scroll_top:bottom]
                    if direction == "up":
                        region = region[count:] + [""] * count
                        revealed = range(bottom - count, bottom)
                    else:
                        region = [""] * count + region[:-count]
                        revealed = range(scroll_top, scroll_top + count)
                    expected[scroll_top:bottom] = region

                    snapshot = terminal.snapshot()
                    self.assertEqual(
                        snapshot.lines,
                        [value.ljust(8) for value in expected],
                    )
                    expected_column = 0 if from_cursor else 4
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (expected_column, row),
                    )
                    for revealed_row in revealed:
                        for column in range(8):
                            cell = snapshot.cell(column, revealed_row)
                            self.assertEqual(cell.char, " ")
                            self.assertEqual(
                                (cell.foreground, cell.background),
                                ((12, 34, 56), (78, 90, 12)),
                            )
                            self.assertFalse(cell.strike)
                            self.assertFalse(cell.inverse)
                            self.assertEqual(cell.underline_style, 0)

    def test_insert_replace_mode(self):
        expected = {
            True: "ABCDEFGHIJ12345KLMNOPQRST" + "*" * 15,
            False: "ABCDEFGHIJ12345PQRST" + "*" * 20,
        }
        for insert in (True, False):
            with self.subTest(insert=insert), Shitty(
                columns=40,
                rows=12,
            ) as terminal:
                terminal.write(
                    b"\x1b[31;44m\x1b[6;1H"
                    b"ABCDEFGHIJKLMNOPQRST" + b"*" * 20
                    + b"\x1b[7;1H" + b"Z" * 40
                )
                self.set_erase_attributes(terminal)
                terminal.write(
                    b"\x1b[6;11H"
                    + (b"\x1b[4h" if insert else b"\x1b[4l")
                    + b"12345"
                )
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[5], expected[insert])
                self.assertEqual(snapshot.lines[6], "Z" * 40)
                for column in range(10, 15):
                    cell = snapshot.cell(column, 5)
                    self.assertEqual(
                        (cell.foreground, cell.background),
                        ((12, 34, 56), (78, 90, 12)),
                    )
                    self.assertTrue(cell.strike)
                    self.assertTrue(cell.inverse)
                    self.assertEqual(cell.underline_style, 3)

    def test_insert_chars(self):
        base = "Q" * 10 + "ABCDEFGHIJKLMNOPQRST" + "Q" * 10
        cases = (
            ("middle", 20, 5),
            ("right", None, 5),
            ("all", None, 100),
        )
        for vertical in (False, True):
            for name, fixed_column, count in cases:
                if name == "middle":
                    column = fixed_column
                elif name == "right":
                    column = 29
                else:
                    column = 10

                with self.subTest(
                    vertical=vertical,
                    case=name,
                ), Shitty(columns=40, rows=25) as terminal:
                    self.editing_row(terminal)
                    self.set_editing_margins(terminal, vertical)
                    self.set_erase_attributes(terminal)
                    terminal.write(
                        f"\x1b[11;{column + 1}H\x1b[{count}@".encode()
                    )
                    snapshot = terminal.snapshot()

                    if name == "middle":
                        expected = (
                            "Q" * 10 + "ABCDEFGHIJ" + " " * 5
                            + "KLMNO" + "Q" * 10
                        )
                        erased = (20, 25)
                    elif name == "right":
                        expected = base[:column] + " " + base[column + 1:]
                        erased = (column, column + 1)
                    else:
                        expected = "Q" * 10 + " " * 20 + "Q" * 10
                        erased = (10, 30)

                    self.assertEqual(snapshot.lines[10], expected)
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (column, 10),
                    )
                    self.assert_erase_cells(
                        snapshot,
                        10,
                        erased[0],
                        erased[1],
                    )

    def test_delete_chars(self):
        base = "Q" * 10 + "ABCDEFGHIJKLMNOPQRST" + "Q" * 10
        cases = (
            ("middle", 20, 5),
            ("right", None, 5),
            ("all", None, 100),
        )
        for vertical in (False, True):
            for name, fixed_column, count in cases:
                if name == "middle":
                    column = fixed_column
                elif name == "right":
                    column = 29
                else:
                    column = 10

                with self.subTest(
                    vertical=vertical,
                    case=name,
                ), Shitty(columns=40, rows=25) as terminal:
                    self.editing_row(terminal)
                    self.set_editing_margins(terminal, vertical)
                    self.set_erase_attributes(terminal)
                    terminal.write(
                        f"\x1b[11;{column + 1}H\x1b[{count}P".encode()
                    )
                    snapshot = terminal.snapshot()

                    if name == "middle":
                        expected = (
                            "Q" * 10 + "ABCDEFGHIJ" + "PQRST"
                            + " " * 5 + "Q" * 10
                        )
                        erased = (25, 30)
                    elif name == "right":
                        expected = base[:column] + " " + base[column + 1:]
                        erased = (column, column + 1)
                    else:
                        expected = "Q" * 10 + " " * 20 + "Q" * 10
                        erased = (10, 30)

                    self.assertEqual(snapshot.lines[10], expected)
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (column, 10),
                    )
                    self.assert_erase_cells(
                        snapshot,
                        10,
                        erased[0],
                        erased[1],
                    )

    def test_horizontal_scroll_operations(self):
        initial = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn"
        cases = (
            (
                "DECIC",
                20,
                b"\x1b[4'}",
                20,
                "ABCDEFGHIJKLMNOPQRST    UVWXYZefghijklmn",
                (20, 24),
            ),
            (
                "DECDC",
                20,
                b"\x1b[4'~",
                20,
                "ABCDEFGHIJKLMNOPQRSTYZabcd    efghijklmn",
                (26, 30),
            ),
            (
                "DECFI",
                27,
                b"\x1b9" * 4,
                29,
                "ABCDEFGHIJMNOPQRSTUVWXYZabcd  efghijklmn",
                (28, 30),
            ),
            (
                "DECBI",
                12,
                b"\x1b6" * 4,
                10,
                "ABCDEFGHIJ  KLMNOPQRSTUVWXYZabefghijklmn",
                (10, 12),
            ),
        )
        rows = tuple(value.encode() for value in [initial] * 25)
        for name, column, sequence, expected_column, expected, erased in cases:
            with self.subTest(operation=name), Shitty(
                columns=40,
                rows=25,
            ) as terminal:
                terminal.write(b"\x1b[31;44m" + put_rows(*rows))
                terminal.write(
                    b"\x1b[?69h\x1b[11;30s\x1b[15;20r"
                )
                self.set_erase_attributes(terminal)
                terminal.write(
                    f"\x1b[18;{column + 1}H".encode() + sequence
                )
                snapshot = terminal.snapshot()
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (expected_column, 17),
                )
                self.assertEqual(snapshot.lines[:14], [initial] * 14)
                self.assertEqual(snapshot.lines[20:], [initial] * 5)
                self.assertEqual(snapshot.lines[14:20], [expected] * 6)
                for row in range(14, 20):
                    self.assert_erase_cells(
                        snapshot,
                        row,
                        erased[0],
                        erased[1],
                    )

    def test_scrolling_wide_chars_horizontally(self):
        content = "こんにちは World"
        encoded = content.encode()
        with Shitty(columns=30, rows=2) as terminal:
            terminal.write(b"\x1b[31;44m" + encoded + b"\x1b[H\x1b[@")
            inserted = terminal.model_snapshot()
            self.assertEqual(
                inserted.lines[0],
                " " + "".join(char + " " for char in "こんにちは")
                + " World" + " " * 13,
            )
            for column in (1, 3, 5, 7, 9):
                self.assertTrue(inserted.cell(column, 0).double_width)
                self.assertTrue(
                    inserted.cell(column + 1, 0).double_width_continuation
                )

            terminal.write(b"\x1b[P")
            deleted = terminal.model_snapshot()
            self.assertEqual(
                deleted.lines[0],
                "".join(char + " " for char in "こんにちは")
                + " World" + " " * 14,
            )
            for column in (0, 2, 4, 6, 8):
                self.assertTrue(deleted.cell(column, 0).double_width)
                self.assertTrue(
                    deleted.cell(column + 1, 0).double_width_continuation
                )

            terminal.write(b"\x1b[1;1;1;;;1;2$v")
            copied = terminal.model_snapshot()
            self.assertEqual(
                copied.lines[0],
                " " + "".join(char + " " for char in "こんにちは")
                + " World" + " " * 13,
            )
            for column in (1, 3, 5, 7, 9):
                self.assertTrue(copied.cell(column, 0).double_width)
                self.assertTrue(
                    copied.cell(column + 1, 0).double_width_continuation
                )


class WindowsTerminalScreenBufferMarginScrollingTest(unittest.TestCase):
    INITIAL = (
        "AAAAAAAA",
        "55555555",
        "66666666",
        "77777777",
        "        ",
        "BBBBBBBB",
    )

    def setup_scrolling_region(self, terminal):
        terminal.write(
            put_rows(*(row.encode() for row in self.INITIAL))
            + b"\x1b[2;5r\x1b[5;1H"
        )
        snapshot = terminal.snapshot()
        self.assertEqual(snapshot.lines, list(self.INITIAL))
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 4))

    def run_scrolling_case(
        self,
        sequence,
        expected,
        cursor,
        horizontal=False,
        clear_vertical=False,
        vertical=None,
        position=None,
    ):
        with Shitty(columns=8, rows=6, save_lines=0) as terminal:
            self.setup_scrolling_region(terminal)
            if clear_vertical:
                terminal.write(b"\x1b[r")
            if vertical is not None:
                terminal.write(
                    f"\x1b[{vertical[0]};{vertical[1]}r".encode()
                )
            if horizontal:
                terminal.write(b"\x1b[?69h\x1b[3;6s")
            if position is not None:
                terminal.write(
                    f"\x1b[{position[1] + 1};{position[0] + 1}H".encode()
                )
            terminal.write(sequence)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, list(expected))
            if cursor is not None:
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    cursor,
                )

    def test_scroll_up_in_margins(self):
        self.run_scrolling_case(
            b"\x1b[S",
            (
                "AAAAAAAA",
                "66666666",
                "77777777",
                "        ",
                "        ",
                "BBBBBBBB",
            ),
            (0, 4),
        )
        self.run_scrolling_case(
            b"\x1b[S",
            (
                "AAAAAAAA",
                "55666655",
                "66777766",
                "77    77",
                "        ",
                "BBBBBBBB",
            ),
            None,
            horizontal=True,
        )

    def test_scroll_down_in_margins(self):
        self.run_scrolling_case(
            b"\x1b[T",
            (
                "AAAAAAAA",
                "        ",
                "55555555",
                "66666666",
                "77777777",
                "BBBBBBBB",
            ),
            (0, 4),
        )
        self.run_scrolling_case(
            b"\x1b[T",
            (
                "AAAAAAAA",
                "55    55",
                "66555566",
                "77666677",
                "  7777  ",
                "BBBBBBBB",
            ),
            None,
            horizontal=True,
        )

    def test_insert_lines_in_margins(self):
        self.run_scrolling_case(
            b"\x1b[2L",
            (
                "AAAAAAAA",
                "55555555",
                "        ",
                "        ",
                "66666666",
                "BBBBBBBB",
            ),
            (0, 2),
            position=(4, 2),
        )
        self.run_scrolling_case(
            b"\x1b[L",
            (
                "AAAAAAAA",
                "        ",
                "55555555",
                "66666666",
                "77777777",
                "        ",
            ),
            (0, 1),
            clear_vertical=True,
            position=(4, 1),
        )
        self.run_scrolling_case(
            b"\x1b[2L",
            (
                "AAAAAAAA",
                "55555555",
                "66    66",
                "77    77",
                "  6666  ",
                "BBBBBBBB",
            ),
            (2, 2),
            horizontal=True,
            position=(4, 2),
        )

    def test_delete_lines_in_margins(self):
        self.run_scrolling_case(
            b"\x1b[2M",
            (
                "AAAAAAAA",
                "55555555",
                "        ",
                "        ",
                "        ",
                "BBBBBBBB",
            ),
            (0, 2),
            position=(4, 2),
        )
        self.run_scrolling_case(
            b"\x1b[M",
            (
                "AAAAAAAA",
                "66666666",
                "77777777",
                "        ",
                "BBBBBBBB",
                "        ",
            ),
            (0, 1),
            clear_vertical=True,
            position=(4, 1),
        )
        self.run_scrolling_case(
            b"\x1b[2M",
            (
                "AAAAAAAA",
                "55555555",
                "66    66",
                "77    77",
                "        ",
                "BBBBBBBB",
            ),
            (2, 2),
            horizontal=True,
            position=(4, 2),
        )

    def test_reverse_line_feed_in_margins(self):
        self.run_scrolling_case(
            b"\x1bM",
            (
                "AAAAAAAA",
                "        ",
                "55555555",
                "66666666",
                "77777777",
                "BBBBBBBB",
            ),
            (4, 1),
            position=(4, 1),
        )
        self.run_scrolling_case(
            b"\x1bM",
            (
                "        ",
                "AAAAAAAA",
                "55555555",
                "66666666",
                "77777777",
                "BBBBBBBB",
            ),
            (4, 0),
            vertical=(1, 5),
            position=(4, 0),
        )
        self.run_scrolling_case(
            b"\x1bM",
            (
                "AAAAAAAA",
                "55    55",
                "66555566",
                "77666677",
                "  7777  ",
                "BBBBBBBB",
            ),
            (4, 1),
            horizontal=True,
            position=(4, 1),
        )


class WindowsTerminalScreenBufferModesTest(unittest.TestCase):
    def test_line_feed_escape_sequences(self):
        for name, sequence, expected_x in (
            ("IND", b"\x1bD", 4),
            ("NEL", b"\x1bE", 0),
        ):
            with self.subTest(control=name, location="top"), Shitty(
                columns=8,
                rows=6,
                save_lines=0,
            ) as terminal:
                terminal.write(b"\x1b[1;5H" + sequence)
                snapshot = terminal.snapshot()
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (expected_x, 1),
                )

            with self.subTest(control=name, location="bottom"), Shitty(
                columns=8,
                rows=6,
                save_lines=0,
            ) as terminal:
                terminal.write(
                    put_rows(*(bytes((digit,)) * 8 for digit in b"012345"))
                    + b"\x1b[6;5H"
                    + sequence
                )
                snapshot = terminal.snapshot()
                self.assertEqual(
                    snapshot.lines,
                    [
                        "1" * 8,
                        "2" * 8,
                        "3" * 8,
                        "4" * 8,
                        "5" * 8,
                        " " * 8,
                    ],
                )
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (expected_x, 5),
                )

            with self.subTest(
                control=name,
                location="vertical-margin",
            ), Shitty(columns=8, rows=6, save_lines=0) as terminal:
                terminal.write(
                    put_rows(
                        b"A" * 8,
                        b"1" * 8,
                        b"2" * 8,
                        b"3" * 8,
                        b"Q" * 8,
                        b"B" * 8,
                    )
                    + b"\x1b[2;5r\x1b[5;5H"
                    + sequence
                )
                snapshot = terminal.snapshot()
                self.assertEqual(
                    snapshot.lines,
                    [
                        "A" * 8,
                        "2" * 8,
                        "3" * 8,
                        "Q" * 8,
                        " " * 8,
                        "B" * 8,
                    ],
                )
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (expected_x, 4),
                )

            with self.subTest(
                control=name,
                location="rectangular-margin",
            ), Shitty(columns=8, rows=6, save_lines=0) as terminal:
                terminal.write(
                    put_rows(
                        b"A" * 8,
                        b"1" * 8,
                        b"2" * 8,
                        b"Q" * 8,
                        b"R" * 8,
                        b"B" * 8,
                    )
                    + b"\x1b[2;5r\x1b[?69h\x1b[3;6s"
                    + b"\x1b[5;6H"
                    + sequence
                )
                snapshot = terminal.snapshot()
                self.assertEqual(
                    snapshot.lines,
                    [
                        "A" * 8,
                        "11222211",
                        "22QQQQ22",
                        "QQRRRRQQ",
                        "RR    RR",
                        "B" * 8,
                    ],
                )
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (2 if name == "NEL" else 5, 4),
                )

    def test_scroll_lines_256_colors(self):
        colors = (
            ("ansi", b"\x1b[42m", 2, (0, 170, 0)),
            ("indexed", b"\x1b[48;5;20m", 20, (0, 0, 215)),
            ("rgb", b"\x1b[48;2;1;2;3m", -1, (1, 2, 3)),
        )
        operations = (
            ("IL", b"\x1b[10L"),
            ("DL", b"\x1b[10M"),
            ("RI", b"\x1bM" * 10),
        )
        for color_name, sgr, index, rgb in colors:
            for operation_name, operation in operations:
                with self.subTest(
                    color=color_name,
                    operation=operation_name,
                ), Shitty(columns=8, rows=4, save_lines=0) as terminal:
                    terminal.write(
                        b"\x1b[1;3r" + sgr + b"\x1b[H"
                        + operation + b"foo"
                    )
                    snapshot = terminal.model_snapshot()
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (3, 0),
                    )
                    self.assertEqual(
                        snapshot.lines[:3],
                        ["foo     "] + [" " * 8] * 2,
                    )
                    for column, row in (
                        (0, 0),
                        (1, 0),
                        (2, 0),
                        (3, 0),
                        (0, 1),
                        (0, 2),
                    ):
                        cell = snapshot.cell(column, row)
                        self.assertEqual(cell.background_index, index)
                        self.assertEqual(cell.background, rgb)

    def test_set_line_feed_mode(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[20h\x1b[1;5H\nX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[1][0], "X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            terminal.key("RETURN")
            self.assertEqual(terminal.read_input(), b"\r\n")

            terminal.write(b"\x1b[20l\x1b[1;5H\nX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[1][4], "X")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 1))
            terminal.key("RETURN")
            self.assertEqual(terminal.read_input(), b"\r")

    def test_set_screen_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertFalse(terminal.render_state().screen_reverse)
            terminal.write(b"\x1b[38;2;12;34;56;48;2;78;90;12mX")
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.foreground, (12, 34, 56))
            self.assertEqual(cell.background, (78, 90, 12))

            terminal.write(b"\x1b[?5h")
            self.assertTrue(terminal.render_state().screen_reverse)
            cell = terminal.model_snapshot().cell(0, 0)
            self.assertEqual(cell.foreground, (12, 34, 56))
            self.assertEqual(cell.background, (78, 90, 12))

            terminal.write(b"\x1b[?5l")
            self.assertFalse(terminal.render_state().screen_reverse)

    def test_set_origin_mode(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[13;41H\x1b[6;20r")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            terminal.write(b"\x1b[?69h\x1b[13;41H\x1b[31;50s")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            for position, expected in (
                (b"\x1b[13;41H", (40, 12)),
                (b"\x1b[23;61H", (60, 22)),
            ):
                terminal.write(position)
                snapshot = terminal.snapshot()
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    expected,
                )

            terminal.write(b"\x1b[13;41H\x1b[?6h")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (30, 5),
            )
            terminal.write(b"\x1b[13;41H\x1b[6;20r")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (30, 5),
            )
            terminal.write(b"\x1b[13;41H\x1b[31;50s")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (30, 5),
            )
            terminal.write(b"\x1b[8;11H")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (40, 12),
            )
            terminal.write(b"\x1b[100;100H")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (49, 19),
            )

            terminal.write(b"\x1b[?6l")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            terminal.write(b"\x1b[13;41H\x1b[6;20r")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            terminal.write(b"\x1b[13;41H\x1b[31;50s")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            terminal.write(b"\x1b[23;61H")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (60, 22),
            )

            terminal.write(b"\x1b[r\x1b[s\x1b[13;41H\x1b[?6h")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 0),
            )
            terminal.write(b"\x1b[13;41H")
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (40, 12),
            )

    def test_set_auto_wrap_mode(self):
        with Shitty(columns=8, rows=6) as terminal:
            terminal.write(b"\x1b[1;6Habcdef")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0][5:], "abc")
            self.assertEqual(snapshot.lines[1][:3], "def")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))

            terminal.write(b"\x1b[?7l\x1b[3;6Habcdef")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[2][5:], "abf")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 2))

            terminal.write(b"\x1b[3;6H" + "a😄b".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[2][5:], "a b")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 2))

            terminal.write(b"\x1b[3;6H" + "ab😄c".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[2][5:], "abc")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (7, 2))

            terminal.write(b"\x1b[?7h\x1b[5;6Habcdef")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[4][5:], "abc")
            self.assertEqual(snapshot.lines[5][:3], "def")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 5))

    def test_hard_reset_buffer(self):
        with Shitty(columns=8, rows=4, save_lines=8) as terminal:
            default_pen = terminal.pen_state()
            terminal.write(b"Hello!\r\n")
            self.assertNotEqual(terminal.snapshot().lines, [" " * 8] * 4)
            terminal.write(b"\x1bc")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" " * 8] * 4)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1b[41m" + b"Hello!\r\n" * 12)
            self.assertGreater(terminal.scrollback_state()[0], 0)
            self.assertNotEqual(terminal.pen_state(), default_pen)
            terminal.write(b"\x1bc")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, [" " * 8] * 4)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.pen_state(), default_pen)


class WindowsTerminalScreenBufferExtendedAttributesTest(unittest.TestCase):
    ATTRIBUTE_NAMES = (
        "bold",
        "faint",
        "italic",
        "underline",
        "double_underline",
        "blink",
        "conceal",
        "strike",
    )

    def attribute_setup(self, values):
        (
            bold,
            faint,
            italic,
            underline,
            double_underline,
            blink,
            conceal,
            strike,
        ) = values
        sequence = bytearray()
        expected = {
            "bold": bold,
            "faint": faint,
            "italic": italic,
            "underline_style": 1 if underline else (
                2 if double_underline else 0
            ),
            "blink": blink,
            "conceal": conceal,
            "strike": strike,
        }
        for enabled, sgr in (
            (bold, 1),
            (faint, 2),
            (italic, 3),
            (underline, 4),
            (double_underline and not underline, 21),
            (blink, 5),
            (conceal, 8),
            (strike, 9),
        ):
            if enabled:
                sequence.extend(f"\x1b[{sgr}m".encode())
        return bytes(sequence), expected

    def attribute_resets(self, values, expected):
        (
            bold,
            faint,
            italic,
            underline,
            double_underline,
            blink,
            conceal,
            strike,
        ) = values
        if bold or faint:
            expected["bold"] = False
            expected["faint"] = False
            yield b"\x1b[22m"
        if italic:
            expected["italic"] = False
            yield b"\x1b[23m"
        if underline or double_underline:
            expected["underline_style"] = 0
            yield b"\x1b[24m"
        if blink:
            expected["blink"] = False
            yield b"\x1b[25m"
        if conceal:
            expected["conceal"] = False
            yield b"\x1b[28m"
        if strike:
            expected["strike"] = False
            yield b"\x1b[29m"

    def assert_attributes(self, cell, expected):
        self.assertEqual(cell.char, "X")
        self.assertEqual(cell.bold, expected["bold"])
        self.assertEqual(cell.faint, expected["faint"])
        self.assertEqual(cell.italic, expected["italic"])
        self.assertEqual(
            cell.underline_style,
            expected["underline_style"],
        )
        self.assertEqual(cell.blink, expected["blink"])
        self.assertEqual(cell.conceal, expected["conceal"])
        self.assertEqual(cell.strike, expected["strike"])

    def assert_colors(self, cell, foreground, background, expected):
        if foreground[0] == "ansi" and expected["bold"]:
            expected_foreground = (10, (85, 255, 85))
        else:
            expected_foreground = (foreground[2], foreground[3])
        self.assertEqual(
            (cell.foreground_index, cell.foreground),
            expected_foreground,
        )
        self.assertEqual(
            (cell.background_index, cell.background),
            (background[2], background[3]),
        )

    def write_and_read_cell(self, terminal, sequence):
        terminal.write(b"\x1b[H" + sequence + b"X")
        return terminal.model_snapshot().cell(0, 0)

    def test_clear_alternate_buffer(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"foo\r\nfoo")
            primary = terminal.snapshot()
            self.assertEqual(primary.lines[:2], ["foo     ", "foo     "])
            self.assertEqual((primary.cursor_x, primary.cursor_y), (3, 1))

            terminal.write(b"\x1b[?1049h\x1b[Hfoo\r\nfoo")
            alternate = terminal.snapshot()
            self.assertEqual(
                alternate.lines[:2],
                ["foo     ", "foo     "],
            )
            terminal.write(b"\x1b[2J\x1b[H")
            alternate = terminal.snapshot()
            self.assertEqual(alternate.lines, [" " * 8] * 4)
            self.assertEqual(
                (alternate.cursor_x, alternate.cursor_y),
                (0, 0),
            )

            terminal.write(b"\x1b[?1049l")
            restored = terminal.snapshot()
            self.assertEqual(restored.lines, primary.lines)
            self.assertEqual(
                (restored.cursor_x, restored.cursor_y),
                (3, 1),
            )

    def test_extended_text_attributes(self):
        with Shitty(columns=2, rows=1, save_lines=0) as terminal:
            for values in itertools.product((False, True), repeat=8):
                with self.subTest(**dict(zip(self.ATTRIBUTE_NAMES, values))):
                    setup, expected = self.attribute_setup(values)
                    cell = self.write_and_read_cell(
                        terminal,
                        b"\x1b[0m" + setup,
                    )
                    self.assert_attributes(cell, expected)
                    for reset in self.attribute_resets(values, expected):
                        cell = self.write_and_read_cell(terminal, reset)
                        self.assert_attributes(cell, expected)

    def test_extended_text_attributes_with_colors(self):
        with Shitty(columns=2, rows=1, save_lines=0) as terminal:
            default = terminal.model_snapshot().cell(0, 0)
            foregrounds = (
                ("default", b"\x1b[39m", -2, default.foreground),
                ("ansi", b"\x1b[32m", 2, (0, 170, 0)),
                ("indexed", b"\x1b[38;5;20m", 20, (0, 0, 215)),
                ("rgb", b"\x1b[38;2;1;2;3m", -1, (1, 2, 3)),
            )
            backgrounds = (
                ("default", b"\x1b[49m", -2, default.background),
                ("ansi", b"\x1b[42m", 2, (0, 170, 0)),
                ("indexed", b"\x1b[48;5;20m", 20, (0, 0, 215)),
                ("rgb", b"\x1b[48;2;1;2;3m", -1, (1, 2, 3)),
            )
            for values in itertools.product((False, True), repeat=8):
                setup, initial_expected = self.attribute_setup(values)
                for foreground in foregrounds:
                    for background in backgrounds:
                        with self.subTest(
                            attributes=values,
                            foreground=foreground[0],
                            background=background[0],
                        ):
                            expected = initial_expected.copy()
                            cell = self.write_and_read_cell(
                                terminal,
                                b"\x1b[0m" + setup
                                + foreground[1] + background[1],
                            )
                            self.assert_attributes(cell, expected)
                            self.assert_colors(
                                cell,
                                foreground,
                                background,
                                expected,
                            )
                            for reset in self.attribute_resets(
                                values,
                                expected,
                            ):
                                cell = self.write_and_read_cell(
                                    terminal,
                                    reset,
                                )
                                self.assert_attributes(cell, expected)
                                self.assert_colors(
                                    cell,
                                    foreground,
                                    background,
                                    expected,
                                )


class WindowsTerminalScreenBufferEraseTest(unittest.TestCase):
    def test_erase_scrollback(self):
        with Shitty(columns=8, rows=3, save_lines=8) as terminal:
            terminal.write(
                b"\x1b[31;44mold\r\n"
                b"\x1b[32;41mone\r\n"
                b"two\r\nthree"
            )
            live_before = terminal.model_snapshot()
            terminal.wheel_up(1)
            self.assertEqual(terminal.snapshot().view_offset, 1)

            terminal.write(b"\x1b[32;41m\x1b[3J")

            live_after = terminal.model_snapshot()
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(live_after.view_offset, 0)
            self.assertEqual(
                (live_after.cursor_x, live_after.cursor_y),
                (live_before.cursor_x, live_before.cursor_y),
            )
            self.assertEqual(live_after.cells, live_before.cells)

    def test_erase_matrix(self):
        columns = 8
        rows = 4
        cursor_x = 4
        cursor_y = 2
        for erase_type in (0, 1, 2):
            for display in (False, True):
                for selective in (False, True):
                    with self.subTest(
                        erase_type=erase_type,
                        display=display,
                        selective=selective,
                    ), Shitty(columns=columns, rows=rows) as terminal:
                        terminal.write(b"\x1b[34;42m")
                        for row in range(rows):
                            terminal.write(
                                f"\x1b[{row + 1};1H".encode()
                                + (
                                    b"\x1b[1\"qZZ\x1b[0\"q"
                                    if selective
                                    else b"ZZ"
                                )
                                + b"Z" * (columns - 2)
                            )
                        terminal.write(
                            b"\x1b[38;2;12;34;56;48;2;78;90;12"
                            b";9;7;4:3m"
                            + f"\x1b[{cursor_y + 1};{cursor_x + 1}H".encode()
                            + b"\x1b["
                            + (b"?" if selective else b"")
                            + str(erase_type).encode()
                            + (b"J" if display else b"K")
                        )
                        snapshot = terminal.model_snapshot()

                        erased = set()
                        if display:
                            if erase_type == 0:
                                erased.update(
                                    (row, column)
                                    for row in range(cursor_y + 1, rows)
                                    for column in range(columns)
                                )
                                erased.update(
                                    (cursor_y, column)
                                    for column in range(cursor_x, columns)
                                )
                            elif erase_type == 1:
                                erased.update(
                                    (row, column)
                                    for row in range(cursor_y)
                                    for column in range(columns)
                                )
                                erased.update(
                                    (cursor_y, column)
                                    for column in range(cursor_x + 1)
                                )
                            else:
                                erased.update(
                                    (row, column)
                                    for row in range(rows)
                                    for column in range(columns)
                                )
                        elif erase_type == 0:
                            erased.update(
                                (cursor_y, column)
                                for column in range(cursor_x, columns)
                            )
                        elif erase_type == 1:
                            erased.update(
                                (cursor_y, column)
                                for column in range(cursor_x + 1)
                            )
                        else:
                            erased.update(
                                (cursor_y, column)
                                for column in range(columns)
                            )

                        for row in range(rows):
                            for column in range(columns):
                                cell = snapshot.cell(column, row)
                                protected = selective and column < 2
                                should_erase = (
                                    (row, column) in erased
                                    and not protected
                                )
                                self.assertEqual(
                                    cell.char,
                                    " " if should_erase else "Z",
                                )
                                self.assertEqual(cell.protected, protected)
                                if should_erase:
                                    self.assertEqual(
                                        (
                                            cell.foreground,
                                            cell.background,
                                        ),
                                        ((12, 34, 56), (78, 90, 12)),
                                    )
                                    self.assertFalse(cell.strike)
                                    self.assertFalse(cell.inverse)
                                    self.assertEqual(cell.underline_style, 0)
                                else:
                                    self.assertEqual(
                                        (
                                            cell.foreground,
                                            cell.background,
                                        ),
                                        ((0, 0, 170), (0, 170, 0)),
                                    )

    def test_protected_attribute(self):
        cases = (
            (b"\x1b[\"q", False),
            (b"\x1b[0\"q", False),
            (b"\x1b[1\"q", True),
            (b"\x1b[2\"q", False),
            (b"\x1b[2;1\"q", False),
            (b"\x1b[1;2\"q", True),
        )
        with Shitty(columns=8, rows=len(cases)) as terminal:
            for row, (sequence, expected) in enumerate(cases):
                terminal.write(
                    f"\x1b[{row + 1};1H".encode()
                    + b"\x1b[1\"q"
                    + sequence
                    + b"ZZZZZ"
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(
                    [
                        snapshot.cell(column, row).protected
                        for column in range(5)
                    ],
                    [expected] * 5,
                )


class WindowsTerminalScreenBufferCursorTest(unittest.TestCase):
    def assert_cursor(self, terminal, column, row):
        snapshot = terminal.snapshot()
        self.assertEqual(
            (snapshot.cursor_x, snapshot.cursor_y),
            (column, row),
        )

    def test_cursor_up_down_across_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[6;19r\x1b[24H\x1b[99A")
            self.assert_cursor(terminal, 0, 5)
            terminal.write(b"X\x1b[1H\x1b[99B")
            self.assert_cursor(terminal, 0, 18)
            terminal.write(b"Y")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[5][0], "X")
            self.assertEqual(snapshot.lines[18][0], "Y")

    def test_cursor_up_down_outside_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[6;19r\x1b[24H\x1b[A")
            self.assert_cursor(terminal, 0, 22)
            terminal.write(b"X\x1b[1H\x1b[B")
            self.assert_cursor(terminal, 0, 1)
            terminal.write(b"Y")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[22][0], "X")
            self.assertEqual(snapshot.lines[1][0], "Y")

    def test_cursor_up_down_exactly_at_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[6;19r\x1b[19;1H\x1b[B")
            self.assert_cursor(terminal, 0, 18)
            terminal.write(b"1\x1b[A")
            self.assert_cursor(terminal, 1, 17)
            terminal.write(b"2\x1b[6;1H\x1b[A")
            self.assert_cursor(terminal, 0, 5)
            terminal.write(b"3\x1b[B")
            self.assert_cursor(terminal, 1, 6)
            terminal.write(b"4")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[18][0], "1")
            self.assertEqual(snapshot.lines[17][1], "2")
            self.assertEqual(snapshot.lines[5][0], "3")
            self.assertEqual(snapshot.lines[6][1], "4")

    def test_cursor_left_right_across_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[31;50s"
                b"\x1b[12;40H\x1b[99C"
            )
            self.assert_cursor(terminal, 49, 11)
            terminal.write(b"X\x1b[12;40H\x1b[99D")
            self.assert_cursor(terminal, 30, 11)
            terminal.write(b"Y")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[11][49], "X")
            self.assertEqual(snapshot.lines[11][30], "Y")

    def test_cursor_left_right_outside_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[31;50s"
                b"\x1b[12;1H\x1b[C"
            )
            self.assert_cursor(terminal, 1, 11)
            terminal.write(b"Y\x1b[12;80H\x1b[D")
            self.assert_cursor(terminal, 78, 11)
            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[11][1], "Y")
            self.assertEqual(snapshot.lines[11][78], "X")

    def test_cursor_left_right_exactly_at_margins(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[31;50s"
                b"\x1b[12;50H\x1b[C"
            )
            self.assert_cursor(terminal, 49, 11)
            terminal.write(b"1\x1b[D")
            self.assert_cursor(terminal, 48, 11)
            terminal.write(b"2\x1b[12;31H\x1b[D")
            self.assert_cursor(terminal, 30, 11)
            terminal.write(b"3\x1b[C")
            self.assert_cursor(terminal, 32, 11)
            terminal.write(b"4")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[11][49], "1")
            self.assertEqual(snapshot.lines[11][48], "2")
            self.assertEqual(snapshot.lines[11][30], "3")
            self.assertEqual(snapshot.lines[11][32], "4")

    def test_cursor_next_previous_line(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[11;21H\x1b[5E")
            self.assert_cursor(terminal, 0, 15)
            terminal.write(b"\x1b[11;21H\x1b[5F")
            self.assert_cursor(terminal, 0, 5)

            terminal.write(b"\x1b[?69h\x1b[11;30s\x1b[9;13r")
            for position, sequence, expected in (
                (b"\x1b[11;21H", b"\x1b[5E", (10, 12)),
                (b"\x1b[11;21H", b"\x1b[5F", (10, 8)),
                (b"\x1b[14;21H", b"\x1b[5E", (10, 18)),
                (b"\x1b[8;21H", b"\x1b[5F", (10, 2)),
            ):
                terminal.write(position + sequence)
                self.assert_cursor(terminal, *expected)

    def test_cursor_position_relative(self):
        with Shitty(columns=80, rows=25) as terminal:
            for sequence, expected in (
                (b"\x1b[11;21H\x1b[5a", (25, 10)),
                (b"\x1b[11;21H\x1b[5e", (20, 15)),
            ):
                terminal.write(sequence)
                self.assert_cursor(terminal, *expected)

            terminal.write(b"\x1b[?69h\x1b[19;23s\x1b[9;13r")
            for sequence, expected in (
                (b"\x1b[11;21H\x1b[5a", (25, 10)),
                (b"\x1b[11;21H\x1b[5e", (20, 15)),
                (b"\x1b[11;21H\x1b[9999a", (79, 10)),
                (b"\x1b[11;21H\x1b[9999e", (20, 24)),
            ):
                terminal.write(sequence)
                self.assert_cursor(terminal, *expected)

    def test_cursor_save_restore(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(
                b"\x1b[11;21H"
                b"\x1b[38;2;12;34;56;48;2;78;90;12m"
                b"\x1b(0"
            )
            saved_pen = terminal.pen_state()
            saved_charset = terminal.charset_state()
            terminal.write(b"\x1b7\x1b[H\x1b[0m\x1b(B\x1b8")
            self.assert_cursor(terminal, 20, 10)
            self.assertEqual(terminal.pen_state(), saved_pen)
            self.assertEqual(terminal.charset_state(), saved_charset)
            terminal.write(b"lwkmvj")
            self.assertEqual(terminal.snapshot().lines[10][20:26], "┌┬┐└┴┘")

            terminal.write(b"\x1b[H\x1b[0m\x1b(B\x1b8")
            self.assert_cursor(terminal, 20, 10)
            self.assertEqual(terminal.pen_state(), saved_pen)
            self.assertEqual(terminal.charset_state(), saved_charset)

            terminal.write(b"\x1b[25;80HX\x1b7")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\x1b[H\x1b8")
            self.assert_cursor(terminal, 79, 24)
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(
                b"\x1b[!p"
                b"\x1b[11;21H\x1b[31;44m\x1b(0"
                b"\x1b8"
            )
            self.assert_cursor(terminal, 0, 0)
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertEqual(terminal.charset_state(), (0, 0, 0, 0))

            terminal.write(
                b"\x1b[?69h\x1b[10;20r\x1b[31;50s\x1b[?6h"
            )
            self.assert_cursor(terminal, 30, 9)
            terminal.write(b"\x1b7\x1b[?6l")
            self.assert_cursor(terminal, 0, 0)
            terminal.write(b"\x1b8\x1b[H")
            self.assert_cursor(terminal, 30, 9)

            terminal.write(
                b"\x1b[r\x1b[s\x1b[?6h\x1b[6;6H\x1b7"
                b"\x1b[15;25r\x1b[31;50s\x1b8"
            )
            self.assert_cursor(terminal, 35, 19)

            terminal.write(
                b"\x1b[r\x1b[s\x1b[?6h\x1b[16;16H\x1b7"
                b"\x1b[1;10r\x1b[1;10s\x1b8"
            )
            self.assert_cursor(terminal, 9, 9)

    def test_screen_alignment_pattern(self):
        with Shitty(columns=12, rows=8) as terminal:
            terminal.write(
                b"\x1b[34;42m"
                + put_rows(*(b"Z" * 12 for _ in range(8)))
                + b"\x1b[38;2;12;34;56;48;2;78;90;12;7;4m"
                + b"\x1b[?69h\x1b[3;10s\x1b[3;6r"
                + b"\x1b[5;6H\x1b#8"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["E" * 12] * 8)
            self.assert_cursor(terminal, 0, 0)
            for cell in snapshot.cells:
                self.assertEqual(
                    (cell.foreground, cell.background),
                    ((255, 255, 255), (0, 0, 0)),
                )
                self.assertFalse(cell.inverse)
                self.assertEqual(cell.underline_style, 0)

            terminal.write(b"\x1b[3;3H\x1b[99A\x1b[99D")
            self.assert_cursor(terminal, 0, 0)
            terminal.write(b"\x1b[6;10H\x1b[99B\x1b[99C")
            self.assert_cursor(terminal, 11, 7)

    def test_cursor_is_on(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"Hello World")
            self.assertEqual(terminal.cursor_state()[:2], (1, 0))
            terminal.write(b"\x1b[?12l")
            self.assertEqual(terminal.cursor_state()[:2], (1, 0))
            terminal.write(b"\x1b[?12h")
            self.assertEqual(terminal.cursor_state()[:2], (1, 1))
            terminal.write(b"\x1b[?25l")
            self.assertEqual(terminal.cursor_state()[:2], (0, 1))
            terminal.write(b"\x1b[?25h")
            self.assertEqual(terminal.cursor_state()[:2], (1, 1))
            terminal.write(b"\x1b[?12;25l")
            self.assertEqual(terminal.cursor_state()[:2], (0, 0))


class WindowsTerminalScreenBufferHyperlinkTest(unittest.TestCase):
    def test_add_hyperlink(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;test.url\x1b\\"
                b"Hello World"
                b"\x1b]8;;\x1b\\!"
            )
            snapshot = terminal.snapshot()
            links = [snapshot.cell(column, 0).hyperlink for column in range(12)]
            self.assertNotEqual(links[0], 0)
            self.assertEqual(links[:11], [links[0]] * 11)
            self.assertEqual(links[11], 0)
            self.assertEqual(terminal.hyperlink(0, 0), "test.url")

    def test_add_hyperlink_custom_id(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;id=myId;test.url\x1b\\A"
                b"\x1b]8;id=myId;test.url\x1b\\B"
                b"\x1b]8;;\x1b\\C"
            )
            snapshot = terminal.snapshot()
            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(
                snapshot.cell(0, 0).hyperlink,
                snapshot.cell(1, 0).hyperlink,
            )
            self.assertEqual(snapshot.cell(2, 0).hyperlink, 0)
            self.assertEqual(terminal.hyperlink(1, 0), "test.url")
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_add_hyperlink_custom_id_different_uri(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;id=myId;test.url\x1b\\A"
                b"\x1b]8;id=myId;other.url\x1b\\B"
                b"\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()
            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertNotEqual(
                snapshot.cell(0, 0).hyperlink,
                snapshot.cell(1, 0).hyperlink,
            )
            self.assertEqual(terminal.hyperlink(0, 0), "test.url")
            self.assertEqual(terminal.hyperlink(1, 0), "other.url")
            self.assertEqual(terminal.hyperlink_count(), 2)


class WindowsTerminalScreenBufferFinalTest(unittest.TestCase):
    def assert_background_run(
        self,
        snapshot,
        row,
        begin,
        end,
        background,
        char=None,
    ):
        for column in range(begin, end):
            cell = snapshot.cell(column, row)
            if char is not None:
                self.assertEqual(cell.char, char)
            self.assertEqual(cell.background, background)

    def test_reflow_end_of_line_color(self):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                with self.subTest(dx=dx, dy=dy):
                    with Shitty(
                        columns=80,
                        rows=25,
                        save_lines=0,
                    ) as terminal:
                        terminal.write(
                            b"\x1b[H\x1b[41mAAAAA"
                            b"\x1b[42m\r\nBBBBB\r\n"
                            b"\x1b[44m CCC \r\n"
                            b"\x1b[43m\xf0\x9f\x99\x83\r\n"
                            b"\x1b[K\x1b[2;6H"
                        )
                        terminal.resize(80 + dx, 25 + dy)
                        snapshot = terminal.model_snapshot()
                        width = snapshot.columns
                        self.assert_background_run(
                            snapshot, 0, 0, 5, (170, 0, 0), "A"
                        )
                        self.assert_background_run(
                            snapshot, 0, 5, width, (0, 0, 0), " "
                        )
                        self.assert_background_run(
                            snapshot, 1, 0, 5, (0, 170, 0), "B"
                        )
                        self.assert_background_run(
                            snapshot, 1, 5, width, (0, 0, 0), " "
                        )
                        self.assert_background_run(
                            snapshot, 2, 0, 5, (0, 0, 170)
                        )
                        self.assertEqual(snapshot.lines[2][:5], " CCC ")
                        self.assert_background_run(
                            snapshot, 2, 5, width, (0, 0, 0), " "
                        )
                        self.assert_background_run(
                            snapshot, 3, 0, 2, (170, 85, 0)
                        )
                        self.assertTrue(snapshot.cell(0, 3).double_width)
                        self.assertTrue(
                            snapshot.cell(1, 3).double_width_continuation
                        )
                        self.assert_background_run(
                            snapshot, 3, 2, width, (0, 0, 0), " "
                        )
                        retained = min(80, width)
                        self.assert_background_run(
                            snapshot, 4, 0, retained, (170, 85, 0), " "
                        )
                        self.assert_background_run(
                            snapshot, 4, retained, width, (0, 0, 0), " "
                        )

    def test_reflow_smaller_long_line_with_color(self):
        with Shitty(columns=80, rows=4, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[H\x1b[41m"
                + b"A" * 70
                + b"\x1b[42m BBB \r\n"
            )
            terminal.resize(65, 4)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "A" * 65)
            self.assertEqual(snapshot.lines[1][:10], "AAAAA BBB ")
            self.assert_background_run(
                snapshot, 0, 0, 65, (170, 0, 0)
            )
            self.assert_background_run(
                snapshot, 1, 0, 5, (170, 0, 0)
            )
            self.assert_background_run(
                snapshot, 1, 5, 10, (0, 170, 0)
            )
            self.assert_background_run(
                snapshot, 1, 10, 65, (0, 0, 0), " "
            )

    def test_reflow_bigger_long_line_with_color(self):
        with Shitty(columns=80, rows=4, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[H\x1b[41m"
                + b"A" * 85
                + b"\x1b[42m BBB \r\n"
            )
            terminal.resize(95, 4)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0][:90], "A" * 85 + " BBB ")
            self.assert_background_run(
                snapshot, 0, 0, 85, (170, 0, 0)
            )
            self.assert_background_run(
                snapshot, 0, 85, 90, (0, 170, 0)
            )
            self.assert_background_run(
                snapshot, 0, 90, 95, (0, 0, 0), " "
            )

    def test_delayed_wrap_reset(self):
        operations = (
            ("DECSTBM", b"\x1b[1;10r", (0, 0)),
            ("DECSLRM", b"\x1b[?69h\x1b[1;10s", (0, 0)),
            ("DECSWL", b"\x1b#5", (79, 5)),
            ("DECDWL", b"\x1b#6", (39, 5)),
            ("DECDHL top", b"\x1b#3", (39, 5)),
            ("DECDHL bottom", b"\x1b#4", (39, 5)),
            ("DECCOLM set", b"\x1b[?40h\x1b[?3h", (0, 0)),
            ("DECOM set", b"\x1b[?6h", (0, 0)),
            ("DECCOLM reset", b"\x1b[?40h\x1b[?3l", (0, 0)),
            ("DECOM reset", b"\x1b[?6l", (0, 0)),
            ("DECAWM reset", b"\x1b[?7l", (79, 5)),
            ("CUU", b"\x1b[A", (79, 4)),
            ("CUD", b"\x1b[B", (79, 6)),
            ("CUF", b"\x1b[C", (79, 5)),
            ("CUB", b"\x1b[D", (78, 5)),
            ("CUP", b"\x1b[3;7H", (6, 2)),
            ("HVP", b"\x1b[3;7f", (6, 2)),
            ("BS", b"\b", (78, 5)),
            ("LF", b"\n", (79, 6)),
            ("VT", b"\v", (79, 6)),
            ("FF", b"\f", (79, 6)),
            ("CR", b"\r", (0, 5)),
            ("IND", b"\x1bD", (79, 6)),
            ("RI", b"\x1bM", (79, 4)),
            ("NEL", b"\x1bE", (0, 6)),
            ("ECH", b"\x1b[X", (79, 5)),
            ("DCH", b"\x1b[P", (79, 5)),
            ("ICH", b"\x1b[@", (79, 5)),
            ("EL", b"\x1b[K", (79, 5)),
            ("DECSEL", b"\x1b[?K", (79, 5)),
            ("DL", b"\x1b[M", (0, 5)),
            ("IL", b"\x1b[L", (0, 5)),
            ("ED", b"\x1b[J", (79, 5)),
            ("ED all", b"\x1b[2J", (79, 5)),
            ("DECSED", b"\x1b[?J", (79, 5)),
        )
        for name, sequence, expected in operations:
            with self.subTest(operation=name):
                self.assert_delayed_wrap_reset(sequence, expected)

    def assert_delayed_wrap_reset(self, sequence, expected):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[6;80HX")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(sequence)
            self.assertFalse(terminal.cursor_pending_wrap())
            snapshot = terminal.snapshot()
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y),
                expected,
            )

    @unittest.expectedFailure
    def test_delayed_wrap_reset_ed_scrollback_windows_policy(self):
        self.assert_delayed_wrap_reset(b"\x1b[3J", (79, 5))

    def test_multiline_wrap(self):
        with Shitty(columns=12, rows=4, save_lines=8) as terminal:
            terminal.write(
                b"\x1b[4;1H"
                + b"1" + b" " * 11
                + b"2" + b" " * 11
                + b"3" + b" " * 11
                + b"4"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                [line[0] for line in snapshot.lines],
                ["1", "2", "3", "4"],
            )

    def test_rectangular_area_operations(self):
        operations = {
            "DECFRA": b"\x1b[42;3;27;6;54$x",
            "DECERA": b"\x1b[3;27;6;54$z",
            "DECSERA": b"\x1b[3;27;6;54${",
            "DECCARA": (
                b"\x1b[2*x"
                b"\x1b[3;27;6;54;7;4:4;58:2::55:23:28$r"
            ),
            "DECRARA": b"\x1b[2*x\x1b[3;27;6;54;1$t",
            "DECCRA": b"\x1b[11;27;14;54;1;3;27;1;4$v",
        }
        base = (
            b"\x1b[0;1;4:3;"
            b"38;2;0;0;255;48;2;0;255;0;58;2;255;0;0m"
        )
        active = b"\x1b[0;1;38;2;255;0;0;48;2;0;0;255m"
        copied = b"\x1b[0;38;2;0;255;0;48;2;255;0;0m"
        for name, sequence in operations.items():
            with self.subTest(operation=name):
                with Shitty(columns=60, rows=20, save_lines=0) as terminal:
                    terminal.write(
                        base
                        + put_rows(*(b"Z" * 60 for _ in range(20)))
                    )
                    if name == "DECCRA":
                        terminal.write(
                            copied
                            + b"".join(
                                f"\x1b[{row + 1};1H".encode() + b"*" * 60
                                for row in range(10, 14)
                            )
                        )
                    terminal.write(active + sequence)
                    if name == "DECCRA":
                        terminal.write(
                            base
                            + b"".join(
                                f"\x1b[{row + 1};1H".encode() + b"Z" * 60
                                for row in range(10, 14)
                            )
                        )
                    snapshot = terminal.model_snapshot()
                    for row in range(20):
                        for column in range(60):
                            cell = snapshot.cell(column, row)
                            targeted = 2 <= row < 6 and 26 <= column < 54
                            if not targeted:
                                self.assertEqual(cell.char, "Z")
                                self.assertEqual(cell.foreground, (0, 0, 255))
                                self.assertEqual(cell.background, (0, 255, 0))
                                self.assertTrue(cell.bold)
                                self.assertEqual(cell.underline_style, 3)
                                self.assertEqual(
                                    cell.underline_color,
                                    (255, 0, 0),
                                )
                                continue
                            if name == "DECFRA":
                                self.assertEqual(cell.char, "*")
                                self.assertEqual(
                                    cell.foreground, (255, 0, 0)
                                )
                                self.assertEqual(
                                    cell.background, (0, 0, 255)
                                )
                                self.assertTrue(cell.bold)
                                self.assertEqual(cell.underline_style, 0)
                            elif name in ("DECERA", "DECSERA"):
                                self.assertEqual(cell.char, " ")
                                self.assertEqual(
                                    cell.foreground, (255, 0, 0)
                                )
                                self.assertEqual(
                                    cell.background, (0, 0, 255)
                                )
                                self.assertFalse(cell.bold)
                                self.assertEqual(cell.underline_style, 0)
                            elif name == "DECCARA":
                                self.assertEqual(cell.char, "Z")
                                self.assertTrue(cell.inverse)
                                self.assertEqual(cell.underline_style, 4)
                                self.assertEqual(
                                    cell.underline_color,
                                    (55, 23, 28),
                                )
                            elif name == "DECRARA":
                                self.assertEqual(cell.char, "Z")
                                self.assertFalse(cell.bold)
                                self.assertEqual(cell.underline_style, 3)
                            else:
                                self.assertEqual(cell.char, "*")
                                self.assertEqual(
                                    cell.foreground, (0, 255, 0)
                                )
                                self.assertEqual(
                                    cell.background, (255, 0, 0)
                                )

    def test_copy_double_width_rectangular_area(self):
        with Shitty(columns=80, rows=6, save_lines=0) as terminal:
            terminal.write(
                b"\x1b[0;4;34;42m"
                + put_rows(*(b"Z" * 80 for _ in range(6)))
                + b"\x1b[0;1;32;41m"
                + put_rows(*(b"C" * 80 for _ in range(3)))
                + b"\x1b[2;1H\x1b#6"
                + b"\x1b[1;31;3;50;1;4;31;1$v"
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[3][30:50], "C" * 20)
            self.assertEqual(snapshot.lines[4][30:40], "C" * 10)
            self.assertEqual(snapshot.lines[5][30:50], "C" * 20)
            self.assertEqual(snapshot.cell(50, 3).char, "Z")
            self.assertEqual(snapshot.cell(40, 4).char, "Z")
            self.assertEqual(snapshot.cell(50, 5).char, "Z")

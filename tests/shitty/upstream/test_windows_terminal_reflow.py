# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import re
import unittest
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from harness import Shitty


UPSTREAM = (
    Path(__file__).parent
    / "windows_terminal"
    / "upstream"
    / "ReflowTests.cpp"
)
UPSTREAM_CASES = 15
UPSTREAM_BUFFERS = 42


@dataclass
class ReflowRow:
    text: str
    wrapped: bool


@dataclass
class ReflowBuffer:
    columns: int
    rows: int
    contents: list[ReflowRow]
    cursor: tuple[int, int]


@dataclass
class ReflowCase:
    name: str
    buffers: list[ReflowBuffer]


def parse_upstream():
    cases = []
    case = None
    buffer = None
    stage = None
    pair = re.compile(r"\{\s*(\d+),\s*(\d+)\s*\}")
    row = re.compile(r'\{\s*L"([^"]*)",\s*(true|false)\s*\}')

    for line in UPSTREAM.read_text().splitlines():
        if "TestCase{" in line:
            case = ReflowCase("", [])
            cases.append(case)
            buffer = None
            stage = "name"
            continue

        if case is None:
            continue
        if stage == "name":
            match = re.search(r'L"([^"]*)"', line)
            if match is not None:
                case.name = match.group(1)
                stage = None
            continue

        if "TestBuffer{" in line:
            buffer = ReflowBuffer(0, 0, [], (0, 0))
            case.buffers.append(buffer)
            stage = "size"
            continue

        if buffer is None:
            continue
        if stage == "size":
            match = pair.search(line)
            if match is not None:
                buffer.columns, buffer.rows = map(int, match.groups())
                stage = "rows"
            continue
        if stage == "rows":
            match = row.search(line)
            if match is not None:
                buffer.contents.append(
                    ReflowRow(match.group(1), match.group(2) == "true")
                )
                if len(buffer.contents) == buffer.rows:
                    stage = "cursor"
            continue
        if stage == "cursor":
            match = pair.search(line)
            if match is not None:
                buffer.cursor = tuple(map(int, match.groups()))
                buffer = None
                stage = None

    return cases


def move_to(column, row):
    return f"\x1b[{row + 1};{column + 1}H".encode()


def install_buffer(terminal, expected):
    for row, contents in enumerate(expected.contents):
        text = (
            contents.text
            if contents.wrapped
            else contents.text.rstrip(" ")
        )
        if text:
            terminal.write(move_to(0, row) + text.encode())
    for row, contents in enumerate(expected.contents):
        if contents.wrapped:
            terminal.set_wrapped(row)
    terminal.write(move_to(*expected.cursor))


def physical_cells(text):
    result = []
    for character in text:
        wide = unicodedata.east_asian_width(character) in ("W", "F")
        result.append((character, wide, False))
        if wide:
            result.append(("", False, True))
    return result


def adapted_buffer(columns, rows, contents, cursor):
    return ReflowBuffer(
        columns,
        rows,
        [ReflowRow(text, wrapped) for text, wrapped in contents],
        cursor,
    )


ADAPTED_EXPECTATIONS = {
    # Windows Terminal owns a buffer with rows below the viewport, so it can
    # keep this cursor visible while discarding newer rows. Shitty's screen has
    # scrollback only above the active area, so it retains newer materialized
    # output there when capacity allows; a cursor moved there is reset to the
    # active top-left, as Ghostty's Screen.cursorReload does.
    (5, 1): adapted_buffer(
        5,
        5,
        (
            ("L    ", False),
            ("MNOPQ", True),
            ("R    ", False),
            ("STUVW", True),
            ("X    ", False),
        ),
        (0, 0),
    ),
    (5, 2): adapted_buffer(
        6,
        5,
        (
            ("L     ", False),
            ("MNOPQR", False),
            ("STUVWX", False),
            ("      ", False),
            ("      ", False),
        ),
        (0, 0),
    ),
    (8, 1): adapted_buffer(
        5,
        5,
        (
            ("ABCDE", True),
            ("F    ", False),
            ("$    ", False),
            ("     ", False),
            ("     ", False),
        ),
        (4, 2),
    ),
    (9, 1): adapted_buffer(
        5,
        5,
        (
            ("ABCDE", True),
            ("F    ", False),
            ("$    ", False),
            ("BLAH ", False),
            ("BLAH ", False),
        ),
        (4, 2),
    ),
    (9, 2): adapted_buffer(
        6,
        5,
        (
            ("ABCDEF", False),
            ("$     ", False),
            ("BLAH  ", False),
            ("BLAH  ", False),
            ("      ", False),
        ),
        (5, 1),
    ),
    (11, 1): adapted_buffer(
        2,
        5,
        (
            ("  ", True),
            ("  ", True),
            ("  ", True),
            ("  ", True),
            ("  ", False),
        ),
        (0, 0),
    ),
    (12, 1): adapted_buffer(
        2,
        5,
        (
            ("  ", True),
            ("  ", True),
            ("  ", True),
            ("  ", True),
            (" Q", False),
        ),
        (0, 0),
    ),
    (13, 1): adapted_buffer(
        2,
        5,
        (
            ("  ", True),
            ("  ", True),
            ("  ", True),
            ("  ", True),
            (" Q", False),
        ),
        (0, 0),
    ),
}


class WindowsTerminalReflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = parse_upstream()
        buffers = sum(len(case.buffers) for case in cls.cases)
        if len(cls.cases) != UPSTREAM_CASES or buffers != UPSTREAM_BUFFERS:
            raise AssertionError(
                "upstream reflow manifest changed: "
                f"{len(cls.cases)} cases, {buffers} buffers"
            )
        for case in cls.cases:
            if not case.name or len(case.buffers) < 2:
                raise AssertionError(f"invalid upstream reflow case: {case!r}")
            for buffer in case.buffers:
                if len(buffer.contents) != buffer.rows:
                    raise AssertionError(
                        f"invalid upstream reflow buffer: {buffer!r}"
                    )

    def assert_buffer(self, terminal, expected):
        snapshot = terminal.snapshot()
        self.assertEqual(
            (snapshot.columns, snapshot.rows),
            (expected.columns, expected.rows),
        )
        self.assertEqual(
            (snapshot.cursor_x, snapshot.cursor_y),
            expected.cursor,
        )
        for row, expected_row in enumerate(expected.contents):
            with self.subTest(row=row):
                cells = physical_cells(expected_row.text)
                self.assertEqual(len(cells), expected.columns)
                actual = [
                    snapshot.cell(column, row)
                    for column in range(expected.columns)
                ]
                self.assertEqual(
                    any(cell.wrapped for cell in actual),
                    expected_row.wrapped,
                )
                for cell, (character, wide, continuation) in zip(
                    actual, cells
                ):
                    self.assertEqual(
                        cell.double_width_continuation,
                        continuation,
                    )
                    if continuation:
                        continue
                    self.assertEqual(cell.char, character)
                    self.assertEqual(cell.double_width, wide)

    def test_reflow_cases(self):
        for case_index, case in enumerate(self.cases):
            with self.subTest(case=case.name, index=case_index):
                initial = case.buffers[0]
                with Shitty(
                    columns=initial.columns,
                    rows=initial.rows,
                    save_lines=0,
                ) as terminal:
                    install_buffer(terminal, initial)
                    for buffer_index, upstream in enumerate(
                        case.buffers[1:], 1
                    ):
                        expected = ADAPTED_EXPECTATIONS.get(
                            (case_index, buffer_index),
                            upstream,
                        )
                        terminal.resize(
                            upstream.columns,
                            upstream.rows,
                        )
                        self.assert_buffer(terminal, expected)
                        if (case_index, buffer_index) in ((8, 1), (9, 1)):
                            self.assertTrue(terminal.cursor_pending_wrap())

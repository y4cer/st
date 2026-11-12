# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Final legacy Grid cases and the first iTerm2 Semantic History cases."""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from harness import Shitty
import test_iterm2_vt100_grid as public_grid


PORTED_CASES = (
    (
        "VT100GridTest.testGridRunFromRange_spanLines",
        "test_grid_range_spans_lines",
    ),
    (
        "VT100GridTest.testGridRunFromRange_startOnSubsequentLine",
        "test_grid_range_starts_on_subsequent_line",
    ),
    (
        "VT100GridTest.testGridRunFromRange_positiveRow",
        "test_grid_range_positive_view_row",
    ),
    (
        "VT100GridTest.testGridRunFromRange_negativeRowNoTruncation",
        "test_grid_range_negative_history_row_without_truncation",
    ),
    (
        "VT100GridTest.testGridRunFromRange_negativeRowTruncatedStart",
        "test_grid_range_negative_row_clips_start",
    ),
    (
        "VT100GridTest.testGridRunFromRange_negativeRowCompletelyTruncated",
        "test_grid_range_above_view_is_empty",
    ),
    (
        "VT100GridTest.testSingleColumnLineBuffer",
        "test_single_column_history_keeps_empty_logical_line",
    ),
    (
        "VT100GridTest.testRemoveLastLine_Regular",
        "test_height_growth_restores_newest_regular_history_line",
    ),
    (
        "VT100GridTest.testRemoveLastRawLine_Wrapped",
        "test_height_growth_restores_complete_wrapped_history_line",
    ),
    (
        "VT100GridTest.testRemoveLastRawLine_Empty",
        "test_height_growth_restores_empty_history_line",
    ),
    (
        "VT100GridTest.testRemoveLastRawLine_LargerThanBlockSize",
        "test_height_growth_restores_history_larger_than_storage_block",
    ),
    (
        "VT100GridTest.testRemoveLastRawLine_EmptyBuffer",
        "test_height_growth_with_empty_history_adds_blank_rows",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathFailsOnNil",
        "test_semantic_path_rejects_nil",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathFailsOnEmpty",
        "test_semantic_path_rejects_empty",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathFindsExistingFileAtAbsolutePath",
        "test_semantic_path_resolves_existing_absolute_path",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathFindsExistingFileAtRelativePath",
        "test_semantic_path_resolves_existing_relative_path",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathStripsDelimiters",
        "test_semantic_path_strips_balanced_delimiters",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathStripsTrailingPunctuation",
        "test_semantic_path_strips_trailing_punctuation",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsLineNumber",
        "test_semantic_path_extracts_line_number",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsLineNumberAndIgnoresColumn",
        "test_semantic_path_extracts_line_and_accepts_column_suffix",
    ),
)


@contextmanager
def semantic_path_fixture():
    with TemporaryDirectory(prefix="shitty-semantic-history-") as root_text:
        root = Path(root_text)
        absolute = root / "path" / "to" / "file"
        absolute.parent.mkdir(parents=True)
        absolute.write_text("fixture")

        working_directory = root / "working" / "directory"
        relative_target = working_directory / "path" / "to" / "file"
        relative_target.parent.mkdir(parents=True)
        relative_target.write_text("fixture")
        yield absolute, working_directory, relative_target


class ITerm2LegacyGridTailSemanticHeadTest(unittest.TestCase):
    _select = staticmethod(public_grid.ITerm2VT100GridTest._select)

    def _run_public_adapter(self, name):
        operation = getattr(public_grid.ITerm2VT100GridTest, name)
        operation(self)

    def _resolve_semantic_path(self, terminal, candidate, working_directory):
        operation = getattr(terminal, "resolve_semantic_path", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no host semantic-path resolver; terminal text and "
                "OSC 7 CWD are present, but path/line/column cannot be queried"
            )
        return operation(candidate, str(working_directory))

    def _terminal_with_candidate(self, candidate, working_directory):
        terminal = Shitty(columns=240, rows=2)
        terminal.osc7_cwd(("file://" + working_directory.as_posix()).encode())
        if candidate is not None:
            terminal.write(candidate.encode())
            self.assertEqual(terminal.all_text()[0], candidate)
        return terminal

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_grid_range_spans_lines(self):
        self._run_public_adapter("test_row_major_range_spans_a_soft_line_boundary")

    def test_grid_range_starts_on_subsequent_line(self):
        self._run_public_adapter("test_row_major_range_can_start_on_a_subsequent_row")

    def test_grid_range_positive_view_row(self):
        self._run_public_adapter("test_row_major_range_applies_a_positive_view_row_offset")

    def test_grid_range_negative_history_row_without_truncation(self):
        self._run_public_adapter(
            "test_row_major_range_maps_a_negative_history_offset_without_clipping"
        )

    def test_grid_range_negative_row_clips_start(self):
        self._run_public_adapter("test_row_major_range_clips_a_partially_negative_start")

    def test_grid_range_above_view_is_empty(self):
        self._run_public_adapter("test_row_major_range_fully_above_the_view_is_empty")

    def test_single_column_history_keeps_empty_logical_line(self):
        self._run_public_adapter("test_one_column_history_retains_an_empty_logical_line")

    def test_height_growth_restores_newest_regular_history_line(self):
        self._run_public_adapter("test_height_growth_consumes_the_newest_regular_history_line")

    def test_height_growth_restores_complete_wrapped_history_line(self):
        self._run_public_adapter("test_height_growth_consumes_a_complete_wrapped_history_line")

    def test_height_growth_restores_empty_history_line(self):
        self._run_public_adapter("test_height_growth_consumes_an_empty_newest_history_line")

    def test_height_growth_restores_history_larger_than_storage_block(self):
        self._run_public_adapter(
            "test_height_growth_consumes_a_history_line_larger_than_a_storage_block"
        )

    def test_height_growth_with_empty_history_adds_blank_rows(self):
        self._run_public_adapter("test_height_growth_with_empty_history_only_adds_blank_rows")

    @unittest.expectedFailure
    def test_semantic_path_rejects_nil(self):
        with semantic_path_fixture() as (_, cwd, _):
            with self._terminal_with_candidate(None, cwd) as terminal:
                self.assertIsNone(self._resolve_semantic_path(terminal, None, cwd))

    @unittest.expectedFailure
    def test_semantic_path_rejects_empty(self):
        with semantic_path_fixture() as (_, cwd, _):
            with self._terminal_with_candidate("", cwd) as terminal:
                self.assertIsNone(self._resolve_semantic_path(terminal, "", cwd))

    @unittest.expectedFailure
    def test_semantic_path_resolves_existing_absolute_path(self):
        with semantic_path_fixture() as (target, cwd, _):
            candidate = target.as_posix()
            with self._terminal_with_candidate(candidate, cwd) as terminal:
                result = self._resolve_semantic_path(terminal, candidate, cwd)
                self.assertEqual(result, (candidate, None, None))

    @unittest.expectedFailure
    def test_semantic_path_resolves_existing_relative_path(self):
        with semantic_path_fixture() as (_, cwd, target):
            candidate = "path/to/file"
            with self._terminal_with_candidate(candidate, cwd) as terminal:
                result = self._resolve_semantic_path(terminal, candidate, cwd)
                self.assertEqual(result, (target.as_posix(), None, None))

    @unittest.expectedFailure
    def test_semantic_path_strips_balanced_delimiters(self):
        with semantic_path_fixture() as (target, cwd, _):
            expected = (target.as_posix(), None, None)
            for delimiters in ("()", "<>", "[]", "{}", "''", '\"\"'):
                candidate = delimiters[0] + target.as_posix() + delimiters[1]
                with self.subTest(delimiters=delimiters):
                    with self._terminal_with_candidate(candidate, cwd) as terminal:
                        result = self._resolve_semantic_path(terminal, candidate, cwd)
                        self.assertEqual(result, expected)

    @unittest.expectedFailure
    def test_semantic_path_strips_trailing_punctuation(self):
        with semantic_path_fixture() as (target, cwd, _):
            expected = (target.as_posix(), None, None)
            for punctuation in (".", ")", ",", ":"):
                candidate = target.as_posix() + punctuation
                with self.subTest(punctuation=punctuation):
                    with self._terminal_with_candidate(candidate, cwd) as terminal:
                        result = self._resolve_semantic_path(terminal, candidate, cwd)
                        self.assertEqual(result, expected)

    @unittest.expectedFailure
    def test_semantic_path_extracts_line_number(self):
        with semantic_path_fixture() as (target, cwd, _):
            candidate = target.as_posix() + ":123"
            with self._terminal_with_candidate(candidate, cwd) as terminal:
                result = self._resolve_semantic_path(terminal, candidate, cwd)
                self.assertEqual(result, (target.as_posix(), 123, None))

    @unittest.expectedFailure
    def test_semantic_path_extracts_line_and_accepts_column_suffix(self):
        with semantic_path_fixture() as (target, cwd, _):
            candidate = target.as_posix() + ":123:456"
            with self._terminal_with_candidate(candidate, cwd) as terminal:
                path, line, _column = self._resolve_semantic_path(
                    terminal,
                    candidate,
                    cwd,
                )
                self.assertEqual(path, target.as_posix())
                self.assertEqual(line, 123)


if __name__ == "__main__":
    unittest.main()

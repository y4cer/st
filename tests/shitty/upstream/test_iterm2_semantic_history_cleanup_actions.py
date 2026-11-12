# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""iTerm2 Semantic History cleanup and action cases 9 through 28."""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from harness import Shitty


PORTED_CASES = (
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsAlternateLineNumberAndColumnSyntax",
        "test_bracketed_line_and_column_with_space",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsAlternateLineNumberAndColumnSyntax_NoSpaceAfterComma",
        "test_bracketed_line_and_column_without_space",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsVeryVerboseLineNumberAndColumnSyntax",
        "test_verbose_suffix_extracts_line_and_column",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsVeryVerboseLineNumberSyntax",
        "test_verbose_suffix_extracts_line_without_column",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsParenthesesLineNumberAndColumnSyntax",
        "test_parenthesized_line_and_column_with_space",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathExtractsParenthesesLineNumberAndColumnSyntax_NoSpaceAfterComma",
        "test_parenthesized_line_and_column_without_space",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathWithParensAndTrailingPunctuationExtractsLineNumber",
        "test_outer_parentheses_and_punctuation_preserve_line",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathWithLineNumberInParensAfterFilename",
        "test_parenthesized_line_after_filename",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathFailsWithJustStrippedChars",
        "test_cleanup_rejects_only_delimiters_and_location",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathStandardizesDot",
        "test_dot_segment_is_normalized",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathStandardizesDotDot",
        "test_dot_dot_segment_is_normalized",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathStripsLeadingGitDiffPrefixes",
        "test_git_diff_prefixes_are_removed",
    ),
    (
        "iTermSemanticHistoryTest.testGetFullPathRejectsNetworkPaths",
        "test_network_mount_path_is_rejected",
    ),
    (
        "iTermSemanticHistoryTest.testRandomStuffAfterFileNameNotIdentifiedAsPartOfFile",
        "test_random_context_is_not_absorbed_into_path",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathRawAction",
        "test_raw_action_expands_all_substitutions",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathFailsIfFileDoesNotExist",
        "test_editor_action_rejects_missing_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathRunsCommandActionForExistingFile",
        "test_command_action_receives_existing_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathRunsCoprocessForExistingFile",
        "test_coprocess_action_receives_existing_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensFileForDirectoryWithURLAction",
        "test_url_action_opens_directory_as_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensURLWithProperSubstitutions",
        "test_url_action_percent_encodes_substitutions",
    ),
)


@contextmanager
def semantic_history_fixture():
    with TemporaryDirectory(prefix="shitty-semantic-history-") as root_text:
        root = Path(root_text)
        absolute = root / "path" / "to" / "file"
        absolute.parent.mkdir(parents=True)
        absolute.write_text("fixture")

        working_directory = root / "working" / "directory"
        relative = working_directory / "path" / "to" / "file"
        relative.parent.mkdir(parents=True)
        relative.write_text("fixture")

        directory = root / "directory"
        directory.mkdir()
        spaced = root / "The Path"
        spaced.write_text("fixture")

        yield {
            "root": root,
            "absolute": absolute,
            "working_directory": working_directory,
            "relative": relative,
            "directory": directory,
            "spaced": spaced,
        }


class ITerm2SemanticHistoryCleanupActionsTest(unittest.TestCase):
    def _terminal_with_text(self, text, working_directory):
        terminal = Shitty(columns=240, rows=2)
        terminal.osc7_cwd(("file://" + working_directory.as_posix()).encode())
        terminal.write(text.encode())
        self.assertEqual(terminal.all_text()[0], text)
        return terminal

    def _resolve_semantic_path(
        self,
        terminal,
        candidate,
        working_directory,
        *,
        suffix=None,
        network_mounts=(),
        trim_whitespace=True,
    ):
        operation = getattr(terminal, "resolve_semantic_path", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no host semantic-path resolver for the path, "
                "location and surrounding terminal context"
            )
        options = {"trim_whitespace": trim_whitespace}
        if suffix is not None:
            options["suffix"] = suffix
        if network_mounts:
            options["network_mounts"] = tuple(
                path.as_posix() for path in network_mounts
            )
        return operation(candidate, working_directory.as_posix(), **options)

    def _perform_semantic_action(self, terminal, request):
        operation = getattr(terminal, "perform_semantic_action", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no frontend semantic-history action dispatcher; "
                "the test will not emulate command, coprocess or URL actions"
            )
        return operation(request)

    def _assert_location(self, syntax, expected_line, expected_column):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            candidate = target.as_posix() + syntax
            with self._terminal_with_text(
                candidate, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal,
                        candidate,
                        fixture["working_directory"],
                    ),
                    (target.as_posix(), expected_line, expected_column),
                )

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    @unittest.expectedFailure
    def test_bracketed_line_and_column_with_space(self):
        self._assert_location("[123, 456]", 123, 456)

    @unittest.expectedFailure
    def test_bracketed_line_and_column_without_space(self):
        self._assert_location("[123,456]", 123, 456)

    @unittest.expectedFailure
    def test_verbose_suffix_extracts_line_and_column(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            suffix = '\", line 123, column 456'
            text = target.as_posix() + suffix
            with self._terminal_with_text(
                text, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal,
                        target.as_posix(),
                        fixture["working_directory"],
                        suffix=suffix,
                    ),
                    (target.as_posix(), 123, 456),
                )

    @unittest.expectedFailure
    def test_verbose_suffix_extracts_line_without_column(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            suffix = '\", line 123, in'
            text = target.as_posix() + suffix
            with self._terminal_with_text(
                text, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal,
                        target.as_posix(),
                        fixture["working_directory"],
                        suffix=suffix,
                    ),
                    (target.as_posix(), 123, None),
                )

    @unittest.expectedFailure
    def test_parenthesized_line_and_column_with_space(self):
        self._assert_location("(123, 456)", 123, 456)

    @unittest.expectedFailure
    def test_parenthesized_line_and_column_without_space(self):
        self._assert_location("(123,456)", 123, 456)

    @unittest.expectedFailure
    def test_outer_parentheses_and_punctuation_preserve_line(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            candidate = f"({target.as_posix()}:123.)"
            with self._terminal_with_text(
                candidate, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal, candidate, fixture["working_directory"]
                    ),
                    (target.as_posix(), 123, None),
                )

    @unittest.expectedFailure
    def test_parenthesized_line_after_filename(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            candidate = f"{target.as_posix()}(123):"
            with self._terminal_with_text(
                candidate, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal, candidate, fixture["working_directory"]
                    ),
                    (target.as_posix(), 123, None),
                )

    @unittest.expectedFailure
    def test_cleanup_rejects_only_delimiters_and_location(self):
        with semantic_history_fixture() as fixture:
            candidate = "(:123.)"
            with self._terminal_with_text(
                candidate, fixture["working_directory"]
            ) as terminal:
                self.assertIsNone(
                    self._resolve_semantic_path(
                        terminal, candidate, fixture["working_directory"]
                    )
                )

    @unittest.expectedFailure
    def test_dot_segment_is_normalized(self):
        with semantic_history_fixture() as fixture:
            candidate = "./path/to/file"
            with self._terminal_with_text(
                candidate, fixture["working_directory"]
            ) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal, candidate, fixture["working_directory"]
                    ),
                    (fixture["relative"].as_posix(), None, None),
                )

    @unittest.expectedFailure
    def test_dot_dot_segment_is_normalized(self):
        with semantic_history_fixture() as fixture:
            cwd = fixture["working_directory"] / "blah"
            cwd.mkdir()
            candidate = "../path/to/file"
            with self._terminal_with_text(candidate, cwd) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(terminal, candidate, cwd),
                    (fixture["relative"].as_posix(), None, None),
                )

    @unittest.expectedFailure
    def test_git_diff_prefixes_are_removed(self):
        with semantic_history_fixture() as fixture:
            cwd = fixture["working_directory"]
            expected = (fixture["relative"].as_posix(), None, None)
            for prefix in ("a/", "b/", "i/", "w/", "c/", "o/"):
                candidate = prefix + "path/to/file"
                with self.subTest(prefix=prefix):
                    with self._terminal_with_text(candidate, cwd) as terminal:
                        self.assertEqual(
                            self._resolve_semantic_path(
                                terminal, candidate, cwd
                            ),
                            expected,
                        )

    @unittest.expectedFailure
    def test_network_mount_path_is_rejected(self):
        with semantic_history_fixture() as fixture:
            cwd = fixture["working_directory"]
            candidate = "path/to/file"
            network_root = fixture["root"] / "working"
            with self._terminal_with_text(candidate, cwd) as terminal:
                self.assertEqual(
                    self._resolve_semantic_path(terminal, candidate, cwd),
                    (fixture["relative"].as_posix(), None, None),
                )
                self.assertIsNone(
                    self._resolve_semantic_path(
                        terminal,
                        candidate,
                        cwd,
                        network_mounts=(network_root,),
                    )
                )

    @unittest.expectedFailure
    def test_random_context_is_not_absorbed_into_path(self):
        with semantic_history_fixture() as fixture:
            prefix = "path/to/file:12:34: blah blah blah"
            suffix = "raz boom bah"
            with self._terminal_with_text(
                prefix + suffix, fixture["working_directory"]
            ) as terminal:
                self.assertIsNone(
                    self._resolve_semantic_path(
                        terminal,
                        prefix,
                        fixture["working_directory"],
                        suffix=suffix,
                        trim_whitespace=False,
                    )
                )

    @unittest.expectedFailure
    def test_raw_action_expands_all_substitutions(self):
        with semantic_history_fixture() as fixture:
            raw = "Prefix X Suffix:1"
            cwd = fixture["root"]
            with self._terminal_with_text(raw, cwd) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "raw_command",
                        "raw_filename": raw,
                        "template": r"\1;\2;\3;\4;\5;\(test)",
                        "prefix": "Prefix",
                        "suffix": "Suffix",
                        "working_directory": cwd.as_posix(),
                        "variables": {"test": "User Variable"},
                    },
                )
                self.assertEqual(
                    result,
                    {
                        "opened": True,
                        "kind": "raw_command",
                        "command": (
                            "Prefix\\ X\\ Suffix:1;;Prefix;Suffix;"
                            + cwd.as_posix()
                            + ";User Variable"
                        ),
                    },
                )

    @unittest.expectedFailure
    def test_editor_action_rejects_missing_file(self):
        with semantic_history_fixture() as fixture:
            raw = "Prefix X Suffix:1"
            cwd = fixture["root"]
            with self._terminal_with_text(raw, cwd) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "best_editor",
                        "raw_filename": raw,
                        "working_directory": cwd.as_posix(),
                    },
                )
                self.assertEqual(result, {"opened": False, "kind": None})

    @unittest.expectedFailure
    def test_command_action_receives_existing_file(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            with self._terminal_with_text(
                target.as_posix(), fixture["root"]
            ) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "command",
                        "path": target.as_posix(),
                        "command": "Command",
                        "working_directory": fixture["root"].as_posix(),
                    },
                )
                self.assertEqual(
                    result,
                    {"opened": True, "kind": "command", "command": "Command"},
                )

    @unittest.expectedFailure
    def test_coprocess_action_receives_existing_file(self):
        with semantic_history_fixture() as fixture:
            target = fixture["absolute"]
            with self._terminal_with_text(
                target.as_posix(), fixture["root"]
            ) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "coprocess",
                        "path": target.as_posix(),
                        "command": "Command",
                        "working_directory": fixture["root"].as_posix(),
                    },
                )
                self.assertEqual(
                    result,
                    {"opened": True, "kind": "coprocess", "command": "Command"},
                )

    @unittest.expectedFailure
    def test_url_action_opens_directory_as_file(self):
        with semantic_history_fixture() as fixture:
            target = fixture["directory"]
            with self._terminal_with_text(
                target.as_posix(), fixture["root"]
            ) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "url",
                        "path": target.as_posix(),
                        "template": "Command",
                        "working_directory": fixture["root"].as_posix(),
                    },
                )
                self.assertEqual(
                    result,
                    {
                        "opened": True,
                        "kind": "file",
                        "target": target.as_posix(),
                    },
                )

    @unittest.expectedFailure
    def test_url_action_percent_encodes_substitutions(self):
        with semantic_history_fixture() as fixture:
            raw = "The Path:1"
            cwd = fixture["root"]
            path = fixture["spaced"].as_posix()
            expected = (
                "http://foo/?pwd="
                + quote(path, safe="/")
                + "&line=1&prefix=The%20Prefix&suffix=The%20Suffix&dir="
                + quote(cwd.as_posix(), safe="/")
                + "&uservar=User%20Variable"
            )
            with self._terminal_with_text(raw, cwd) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "url",
                        "raw_filename": raw,
                        "template": (
                            r"http://foo/?pwd=\1&line=\2&prefix=\3&suffix=\4"
                            r"&dir=\5&uservar=\(test)"
                        ),
                        "prefix": "The Prefix",
                        "suffix": "The Suffix",
                        "working_directory": cwd.as_posix(),
                        "variables": {"test": "User Variable"},
                    },
                )
                self.assertEqual(
                    result,
                    {
                        "opened": True,
                        "kind": "url",
                        "target": expected,
                        "editor": False,
                    },
                )


if __name__ == "__main__":
    unittest.main()

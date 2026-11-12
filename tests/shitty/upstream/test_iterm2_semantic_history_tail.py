# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Final iTerm2 Semantic History cases 49 through 54."""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from harness import Shitty


PORTED_CASES = (
    (
        "iTermSemanticHistoryTest.testPathOfExistingFile_IgnoresFilesOnNetworkVolumes",
        "test_finder_rejects_candidate_on_network_mount",
    ),
    (
        "iTermSemanticHistoryTest.testLeadingWhitespaceIgnoredWithoutTrimming",
        "test_finder_does_not_skip_leading_whitespace_without_trimming",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFile_EscapedCharacters",
        "test_finder_unescapes_spaces_around_clicked_cell",
    ),
    (
        "iTermSemanticHistoryTest.testColonTextAfterLineNumber",
        "test_finder_stops_after_line_before_colon_prose",
    ),
    (
        "iTermSemanticHistoryTest.testIssue7760",
        "test_raw_command_expands_path_and_working_directory_once",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFile_QuestionableSuffix",
        "test_disabled_upstream_questionable_suffix_expectation",
    ),
)


@contextmanager
def semantic_history_fixture():
    with TemporaryDirectory(prefix="shitty-semantic-tail-") as root_text:
        root = Path(root_text)
        working_directory = root / "directory"
        working_directory.mkdir()
        yield root, working_directory


class ITerm2SemanticHistoryTailTest(unittest.TestCase):
    def _terminal_with_context(self, text, working_directory, visible=()):
        terminal = Shitty(columns=320, rows=3)
        terminal.osc7_cwd(
            ("file://" + working_directory.as_posix()).encode()
        )
        terminal.write(text.encode())
        rendered = "\n".join(terminal.all_text())
        for piece in visible:
            self.assertIn(piece, rendered)
        return terminal

    def _find_semantic_path(
        self,
        terminal,
        *,
        prefix,
        suffix,
        working_directory,
        trim_whitespace,
        network_mounts=(),
    ):
        operation = getattr(terminal, "find_semantic_path", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no host path finder that combines terminal "
                "prefix and suffix around the clicked cell"
            )
        return operation(
            prefix=prefix,
            suffix=suffix,
            working_directory=working_directory.as_posix(),
            trim_whitespace=trim_whitespace,
            network_mounts=tuple(path.as_posix() for path in network_mounts),
        )

    def _resolve_semantic_path(
        self, terminal, candidate, working_directory
    ):
        operation = getattr(terminal, "resolve_semantic_path", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no host semantic-path resolver for the path "
                "and location selected from terminal text"
            )
        return operation(candidate, working_directory.as_posix())

    def _perform_semantic_action(self, terminal, request):
        operation = getattr(terminal, "perform_semantic_action", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no frontend semantic-history action dispatcher; "
                "the test will not emulate command execution"
            )
        return operation(request)

    def _create_file(self, working_directory, relative_name):
        target = working_directory / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture")
        return target

    def test_upstream_inventory_has_6_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 6)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 6)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 6)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    @unittest.expectedFailure
    def test_finder_rejects_candidate_on_network_mount(self):
        with semantic_history_fixture() as (_, cwd):
            relative = "five six seven eight"
            self._create_file(cwd, relative)
            prefix = "one two three four five six "
            suffix = "seven eight nine ten eleven"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(relative,)
            ) as terminal:
                self.assertIsNone(
                    self._find_semantic_path(
                        terminal,
                        prefix=prefix,
                        suffix=suffix,
                        working_directory=cwd,
                        trim_whitespace=False,
                        network_mounts=(cwd,),
                    )
                )

    @unittest.expectedFailure
    def test_finder_does_not_skip_leading_whitespace_without_trimming(self):
        with semantic_history_fixture() as (_, cwd):
            self._create_file(cwd, "test.txt")
            prefix = "     "
            suffix = "  test.txt"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=("test.txt",)
            ) as terminal:
                self.assertIsNone(
                    self._find_semantic_path(
                        terminal,
                        prefix=prefix,
                        suffix=suffix,
                        working_directory=cwd,
                        trim_whitespace=False,
                    )
                )

    @unittest.expectedFailure
    def test_finder_unescapes_spaces_around_clicked_cell(self):
        with semantic_history_fixture() as (_, cwd):
            relative = "five six seven eight"
            self._create_file(cwd, relative)
            prefix = "one two three four five\\ six\\ "
            suffix = "seven\\ eight nine ten eleven"
            with self._terminal_with_context(
                prefix + suffix,
                cwd,
                visible=("five\\ six\\ seven\\ eight",),
            ) as terminal:
                self.assertEqual(
                    self._find_semantic_path(
                        terminal,
                        prefix=prefix,
                        suffix=suffix,
                        working_directory=cwd,
                        trim_whitespace=False,
                    ),
                    {
                        "path": relative,
                        "prefix_chars": len("five\\ six\\ "),
                        "suffix_chars": len("seven\\ eight"),
                    },
                )

    @unittest.expectedFailure
    def test_finder_stops_after_line_before_colon_prose(self):
        with semantic_history_fixture() as (_, cwd):
            target = self._create_file(cwd, "file.rb")
            prefix = "file"
            suffix = ".rb:7:in `new`"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=("file.rb:7",)
            ) as terminal:
                found = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(found["path"], "file.rb:7")
                self.assertEqual(
                    self._resolve_semantic_path(
                        terminal, found["path"], cwd
                    ),
                    (target.as_posix(), 7, None),
                )

    @unittest.expectedFailure
    def test_raw_command_expands_path_and_working_directory_once(self):
        with semantic_history_fixture() as (_, cwd):
            target = self._create_file(
                cwd, "tmp/failure-sandbox_spec-246-screenshot.png"
            )
            prefix = (
                "Saving\\ screenshot\\ to\\ "
                + (cwd / "tmp" / "failure-").as_posix()
            )
            suffix = "sandbox_spec-246-screenshot.png\\"
            template = (
                '/bin/bash -l -c "cd \\5 && env /usr/local/bin/atom \\1:2"'
            )
            expected = (
                f'/bin/bash -l -c "cd {cwd.as_posix()} && env '
                f'/usr/local/bin/atom {target.as_posix()}:2"'
            )
            with self._terminal_with_context(
                target.as_posix(), cwd, visible=(target.name,)
            ) as terminal:
                result = self._perform_semantic_action(
                    terminal,
                    {
                        "action": "raw_command",
                        "path": target.as_posix(),
                        "raw_filename": target.as_posix(),
                        "template": template,
                        "prefix": prefix,
                        "suffix": suffix,
                        "working_directory": cwd.as_posix(),
                        "line": "",
                        "column": "",
                    },
                )
                self.assertEqual(
                    result,
                    {
                        "opened": True,
                        "kind": "raw_command",
                        "command": expected,
                    },
                )

    @unittest.expectedFailure
    def test_disabled_upstream_questionable_suffix_expectation(self):
        with semantic_history_fixture() as (_, cwd):
            relative = "five six seven eight"
            self._create_file(cwd, relative)
            prefix = "one two three four five six "
            suffix = "seven eight. nine ten eleven"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(relative + ".",)
            ) as terminal:
                self.assertEqual(
                    self._find_semantic_path(
                        terminal,
                        prefix=prefix,
                        suffix=suffix,
                        working_directory=cwd,
                        trim_whitespace=False,
                    ),
                    {
                        "path": relative,
                        "prefix_chars": len("five six "),
                        "suffix_chars": len("seven eight"),
                    },
                )


if __name__ == "__main__":
    unittest.main()

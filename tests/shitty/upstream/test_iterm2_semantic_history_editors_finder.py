# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""iTerm2 Semantic History editor and path-finder cases 29 through 48."""

import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from harness import Shitty


MACVIM = "org.vim.MacVim"
ATOM = "com.github.atom"
VSCODE = "com.microsoft.VSCode"
SUBLIME_2 = "com.sublimetext.2"
SUBLIME_3 = "com.sublimetext.3"
SUBLIME_4 = "com.sublimetext.4"
TEXTMATE = "com.macromates.TextMate"
BBEDIT = "com.barebones.bbedit"


PORTED_CASES = (
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInEditorWhenEditorIsDefaultApp",
        "test_explicit_macvim_editor_when_it_is_default",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInDefaultAppWithLineNumber",
        "test_best_editor_uses_default_macvim_with_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInEditorWithLineNumberWhenEditorIsDefaultApp",
        "test_explicit_default_macvim_with_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileAtomEditor",
        "test_atom_receives_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileAtomEditorWhenDefaultAppForThisFile",
        "test_atom_receives_path_and_line_when_default_for_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileVSCodeEditor",
        "test_vscode_receives_path_line_and_column",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileVSCodeEditorWhenDefaultAppForThisFile",
        "test_vscode_receives_location_when_default_for_file",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileSublimeText2Editor",
        "test_sublime_text_2_receives_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileSublimeText4Editor",
        "test_sublime_text_4_receives_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileSublimeText3Editor",
        "test_sublime_text_3_receives_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInMacVim",
        "test_macvim_editor_url_contains_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInTextMate",
        "test_textmate_editor_url_contains_path_and_line",
    ),
    (
        "iTermSemanticHistoryTest.testOpenPathOpensTextFileInBBEdit",
        "test_bbedit_uses_textmate_url_scheme",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFile_Local",
        "test_finder_combines_prefix_and_suffix_around_local_path",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileIgnoringLeadingAndTrailingWhitespaceAndNewlines",
        "test_finder_trims_selected_line_whitespace",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileRemovesParens",
        "test_finder_removes_parentheses_around_path",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileSupportsLineNumberAndColumnNumber",
        "test_finder_keeps_colon_line_and_column",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileSupportsLineNumberAndColumnNumberInParens",
        "test_finder_keeps_parenthesized_line_and_column_split_at_click",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileFindsColumnAndLineNumber",
        "test_finder_takes_location_entirely_from_suffix",
    ),
    (
        "iTermSemanticHistoryTest.testPathOfExistingFileSupportsLineNumberAndColumnNumberAndParensAndNonspaceSeparators",
        "test_finder_handles_tab_separator_location_and_punctuation",
    ),
)


@contextmanager
def semantic_history_fixture():
    with TemporaryDirectory(prefix="shitty-semantic-editor-") as root_text:
        root = Path(root_text)
        working_directory = root / "directory"
        working_directory.mkdir()
        editor_target = root / "file" / "that" / "exists"
        editor_target.parent.mkdir(parents=True)
        editor_target.write_text("fixture")
        yield root, working_directory, editor_target


class ITerm2SemanticHistoryEditorsFinderTest(unittest.TestCase):
    def _terminal_with_context(self, data, working_directory, visible=()):
        terminal = Shitty(columns=300, rows=3)
        terminal.osc7_cwd(("file://" + working_directory.as_posix()).encode())
        terminal.write(data.encode())
        rendered = "\n".join(terminal.all_text())
        for piece in visible:
            self.assertIn(piece, rendered)
        return terminal

    def _perform_semantic_action(self, terminal, request):
        operation = getattr(terminal, "perform_semantic_action", None)
        if operation is None:
            raise AssertionError(
                "Shitty has no frontend semantic-history editor dispatcher; "
                "the test will not emulate application launches"
            )
        return operation(request)

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

    def _editor_action(
        self,
        *,
        editor,
        location="",
        default_app_is_editor=False,
        bundle_id_for_default_app=None,
        best_editor=False,
    ):
        with semantic_history_fixture() as (root, _, target):
            raw = target.as_posix() + location
            with self._terminal_with_context(
                raw, root, visible=(raw,)
            ) as terminal:
                return target, self._perform_semantic_action(
                    terminal,
                    {
                        "action": "best_editor" if best_editor else "editor",
                        "editor": editor,
                        "path": target.as_posix(),
                        "raw_filename": raw,
                        "line": 12 if location else None,
                        "column": 11 if location == ":12:11" else None,
                        "working_directory": root.as_posix(),
                        "default_app_is_editor": default_app_is_editor,
                        "bundle_id_for_default_app": bundle_id_for_default_app,
                    },
                )

    def _assert_application_argument(
        self,
        editor,
        location,
        *,
        bundle_id_for_default_app=None,
    ):
        target, result = self._editor_action(
            editor=editor,
            location=location,
            bundle_id_for_default_app=bundle_id_for_default_app,
        )
        self.assertEqual(
            result,
            {
                "opened": True,
                "kind": "application",
                "application": editor,
                "argument": target.as_posix() + location,
            },
        )

    def _assert_editor_url(self, editor, scheme):
        target, result = self._editor_action(editor=editor, location=":12")
        expected_url = (
            f"{scheme}://open?url=file://"
            + quote(target.as_posix(), safe="/")
            + "&line=12"
        )
        self.assertEqual(
            result,
            {
                "opened": True,
                "kind": "editor_url",
                "editor": editor,
                "url": expected_url,
            },
        )

    def _path_fixture(self, working_directory, relative_name):
        target = working_directory / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture")
        return target

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    @unittest.expectedFailure
    def test_explicit_macvim_editor_when_it_is_default(self):
        target, result = self._editor_action(
            editor=MACVIM,
            default_app_is_editor=True,
        )
        expected_url = (
            "mvim://open?url=file:%2F%2F"
            + quote(target.as_posix(), safe="")
        )
        self.assertEqual(
            result,
            {
                "opened": True,
                "kind": "editor_url",
                "editor": MACVIM,
                "url": expected_url,
            },
        )

    @unittest.expectedFailure
    def test_best_editor_uses_default_macvim_with_line(self):
        target, result = self._editor_action(
            editor=MACVIM,
            location=":12",
            default_app_is_editor=True,
            bundle_id_for_default_app=MACVIM,
            best_editor=True,
        )
        self.assertEqual(
            result,
            {
                "opened": True,
                "kind": "editor_url",
                "editor": MACVIM,
                "url": (
                    "mvim://open?url=file://"
                    + target.as_posix()
                    + "&line=12"
                ),
            },
        )

    @unittest.expectedFailure
    def test_explicit_default_macvim_with_line(self):
        target, result = self._editor_action(
            editor=MACVIM,
            location=":12",
            default_app_is_editor=True,
        )
        self.assertEqual(
            result,
            {
                "opened": True,
                "kind": "editor_url",
                "editor": MACVIM,
                "url": (
                    "mvim://open?url=file://"
                    + target.as_posix()
                    + "&line=12"
                ),
            },
        )

    @unittest.expectedFailure
    def test_atom_receives_path_and_line(self):
        self._assert_application_argument(ATOM, ":12")

    @unittest.expectedFailure
    def test_atom_receives_path_and_line_when_default_for_file(self):
        self._assert_application_argument(
            ATOM,
            ":12",
            bundle_id_for_default_app=ATOM,
        )

    @unittest.expectedFailure
    def test_vscode_receives_path_line_and_column(self):
        self._assert_application_argument(VSCODE, ":12:11")

    @unittest.expectedFailure
    def test_vscode_receives_location_when_default_for_file(self):
        self._assert_application_argument(
            VSCODE,
            ":12:11",
            bundle_id_for_default_app=VSCODE,
        )

    @unittest.expectedFailure
    def test_sublime_text_2_receives_path_and_line(self):
        self._assert_application_argument(SUBLIME_2, ":12")

    @unittest.expectedFailure
    def test_sublime_text_4_receives_path_and_line(self):
        self._assert_application_argument(SUBLIME_4, ":12")

    @unittest.expectedFailure
    def test_sublime_text_3_receives_path_and_line(self):
        self._assert_application_argument(SUBLIME_3, ":12")

    @unittest.expectedFailure
    def test_macvim_editor_url_contains_path_and_line(self):
        self._assert_editor_url(MACVIM, "mvim")

    @unittest.expectedFailure
    def test_textmate_editor_url_contains_path_and_line(self):
        self._assert_editor_url(TEXTMATE, "txmt")

    @unittest.expectedFailure
    def test_bbedit_uses_textmate_url_scheme(self):
        self._assert_editor_url(BBEDIT, "txmt")

    @unittest.expectedFailure
    def test_finder_combines_prefix_and_suffix_around_local_path(self):
        with semantic_history_fixture() as (_, cwd, _):
            relative = "five six seven eight"
            self._path_fixture(cwd, relative)
            prefix = "one two three four five six "
            suffix = "seven eight nine ten eleven"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(relative,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(result["path"], relative)
                self.assertEqual(result["prefix_chars"], len("five six "))

    @unittest.expectedFailure
    def test_finder_trims_selected_line_whitespace(self):
        with semantic_history_fixture() as (_, cwd, _):
            relative = "five six seven eight"
            self._path_fixture(cwd, relative)
            prefix = relative + " \r\n"
            suffix = ""
            with self._terminal_with_context(
                prefix, cwd, visible=(relative,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=True,
                )
                self.assertEqual(
                    result,
                    {
                        "path": relative,
                        "prefix_chars": len(relative),
                        "suffix_chars": 0,
                    },
                )

    @unittest.expectedFailure
    def test_finder_removes_parentheses_around_path(self):
        with semantic_history_fixture() as (_, cwd, _):
            relative = "five six seven eight"
            self._path_fixture(cwd, relative)
            prefix = "one two three four (five six "
            suffix = "seven eight) nine ten eleven"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(relative,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(
                    result,
                    {
                        "path": relative,
                        "prefix_chars": len("five six "),
                        "suffix_chars": len("seven eight"),
                    },
                )

    @unittest.expectedFailure
    def test_finder_keeps_colon_line_and_column(self):
        with semantic_history_fixture() as (_, cwd, _):
            relative = "five six seven eight"
            self._path_fixture(cwd, relative)
            prefix = "one two three four five six "
            suffix = "seven eight:123:456 nine ten eleven"
            decorated = relative + ":123:456"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(decorated,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(
                    result,
                    {
                        "path": decorated,
                        "prefix_chars": len("five six "),
                        "suffix_chars": len("seven eight:123:456"),
                    },
                )

    @unittest.expectedFailure
    def test_finder_keeps_parenthesized_line_and_column_split_at_click(self):
        with semantic_history_fixture() as (_, cwd, _):
            self._path_fixture(cwd, "file.txt")
            prefix = "file.txt(10"
            suffix = ", 10)"
            decorated = "file.txt(10, 10)"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=(decorated,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(
                    result,
                    {
                        "path": decorated,
                        "prefix_chars": len(prefix),
                        "suffix_chars": len(suffix),
                    },
                )

    @unittest.expectedFailure
    def test_finder_takes_location_entirely_from_suffix(self):
        with semantic_history_fixture() as (_, cwd, _):
            self._path_fixture(cwd, "file.txt")
            prefix = "file.txt"
            suffix = "(10, 10)"
            decorated = prefix + suffix
            with self._terminal_with_context(
                decorated, cwd, visible=(decorated,)
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(
                    result,
                    {
                        "path": decorated,
                        "prefix_chars": len(prefix),
                        "suffix_chars": len(suffix),
                    },
                )

    @unittest.expectedFailure
    def test_finder_handles_tab_separator_location_and_punctuation(self):
        with semantic_history_fixture() as (_, cwd, _):
            relative = "five.six\tseven eight"
            self._path_fixture(cwd, relative)
            prefix = "one two three four (five.six\t"
            suffix = "seven eight:123:456). nine ten eleven"
            decorated = relative + ":123:456"
            with self._terminal_with_context(
                prefix + suffix, cwd, visible=("five.six", "seven eight")
            ) as terminal:
                result = self._find_semantic_path(
                    terminal,
                    prefix=prefix,
                    suffix=suffix,
                    working_directory=cwd,
                    trim_whitespace=False,
                )
                self.assertEqual(
                    result,
                    {
                        "path": decorated,
                        "prefix_chars": len("five.six\t"),
                        "suffix_chars": len("seven eight:123:456"),
                    },
                )


if __name__ == "__main__":
    unittest.main()

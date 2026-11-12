# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "ShellIntegration.OSC_133",
    "ShellIntegration.SETMARK",
    "SemanticBlockProtocol.LineFlags",
    "SemanticBlockProtocol.lastCommandBlockWithoutMode2034",
    "SemanticBlockProtocol.lastCommandBlockWithoutShellIntegration",
    "SemanticBlockProtocol.outputWithoutTrailingNewline",
    "SemanticBlockProtocol.outputThatFitsOnTheLineItStartedOn",
    "SemanticBlockProtocol.marksSurviveResize",
    "SemanticBlockProtocol.noCommandAtAllIsNoBlock",
    "SemanticBlockProtocol.TrackerMetadata",
    "SemanticBlockProtocol.DECRQM",
    "SemanticBlockProtocol.QueryDisabled",
    "SemanticBlockProtocol.QueryLastCommand",
    "SemanticBlockProtocol.QueryLastNCommands",
    "SemanticBlockProtocol.QueryInProgress",
    "SemanticBlockProtocol.NoCompletedCommands",
    "SemanticBlockProtocol.TokenOnEnable",
    "SemanticBlockProtocol.TokenInvalidatedOnDisable",
    "SemanticBlockProtocol.QueryWithoutToken",
    "SemanticBlockProtocol.QueryWithWrongToken",
    "SemanticBlockProtocol.TokenChangesOnReEnable",
    "ShellIntegration.OSC_133_B stamps PromptEnd on the logical head",
    "ShellIntegration.OSC_133_B on a multi-line prompt marks the line it ended on",
    "ShellIntegration.PromptEnd survives reflow",
    "ShellIntegration.LineFlags formatter names PromptEnd",
    "ShellIntegration.livePromptSpan reports a fresh prompt",
    "ShellIntegration.livePromptSpan spans a reflowed multi-line prompt",
    "ShellIntegration.livePromptSpan declines while a command is running",
    "ShellIntegration.livePromptSpan reports a prompt again once the command finished",
    "ShellIntegration.livePromptSpan reports no integration for a plain shell",
    "ShellIntegration.livePromptSpan is silent on the alternate screen",
)

EXTRACTION_UPSTREAM_CASES = (
    "SemanticBlockProtocol.lastCommandBlockWithoutMode2034",
    "SemanticBlockProtocol.lastCommandBlockWithoutShellIntegration",
    "SemanticBlockProtocol.outputWithoutTrailingNewline",
    "SemanticBlockProtocol.outputThatFitsOnTheLineItStartedOn",
    "SemanticBlockProtocol.marksSurviveResize",
    "SemanticBlockProtocol.noCommandAtAllIsNoBlock",
    "ShellIntegration.livePromptSpan reports a fresh prompt",
    "ShellIntegration.livePromptSpan spans a reflowed multi-line prompt",
    "ShellIntegration.livePromptSpan declines while a command is running",
    "ShellIntegration.livePromptSpan reports a prompt again once the command finished",
    "ShellIntegration.livePromptSpan reports no integration for a plain shell",
    "ShellIntegration.livePromptSpan is silent on the alternate screen",
)


def semantics(snapshot, row, begin, end):
    return [
        snapshot.cell(column, row).semantic
        for column in range(begin, end)
    ]


def semantic_text(snapshot, value):
    result = []
    for row in range(snapshot.rows):
        result.append("".join(
            snapshot.cell(column, row).char
            for column in range(snapshot.columns)
            if snapshot.cell(column, row).semantic == value
        ).rstrip())
    return tuple(line for line in result if line)


def write_prompt_and_run(terminal, prompt, output):
    terminal.write(
        b"\x1b]133;A\x1b\\" + prompt + b"\r\n"
        b"\x1b]133;C\x1b\\" + output
    )


def write_next_prompt(terminal, prompt=b"$ ", exit_code=0):
    terminal.write(
        f"\x1b]133;D;{exit_code}\x1b\\".encode()
        + b"\x1b[>M\x1b]133;A\x1b\\"
        + prompt
    )


class ContourShellIntegrationTest(unittest.TestCase):
    def test_upstream_inventory_has_all_31_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 31)
        self.assertEqual(len(set(UPSTREAM_CASES)), 31)

    def test_extraction_inventory_has_all_12_remaining_cases(self):
        self.assertEqual(len(EXTRACTION_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(EXTRACTION_UPSTREAM_CASES)), 12)
        self.assertTrue(set(EXTRACTION_UPSTREAM_CASES).issubset(UPSTREAM_CASES))

    def test_osc_133_metadata_and_transitions(self):
        with Shitty(columns=24, rows=3) as terminal:
            terminal.write(
                b"\x1b]133;A;click_events=1\x1b\\prompt"
                b"\x1b]133;B;future=value\x1b\\input"
                b"\x1b]133;C;cmdline_url=echo%20ok\x1b\\output"
                b"\x1b]133;D;123\x1b\\idle"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:21], "promptinputoutputidle")
            self.assertEqual(semantics(snapshot, 0, 0, 6), [1] * 6)
            self.assertEqual(semantics(snapshot, 0, 6, 11), [2] * 5)
            self.assertEqual(semantics(snapshot, 0, 11, 17), [3] * 6)
            self.assertEqual(semantics(snapshot, 0, 17, 21), [0] * 4)

    def test_setmark_marks_in_place_without_forcing_a_new_line(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"x\x1b[>My")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:2], "xy")
            self.assertEqual(semantics(snapshot, 0, 0, 2), [0, 1])

    def test_prompt_end_boundary_survives_forward_and_reverse_reflow(self):
        with Shitty(columns=20, rows=4, save_lines=8) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\0123456789abcdef> "
                b"\x1b]133;B\x1b\\command"
            )

            for columns in (10, 40, 7, 20):
                terminal.resize(columns, 4)
                snapshot = terminal.snapshot()
                cells = [
                    cell.semantic
                    for cell in snapshot.cells
                    if cell.drawn
                ]
                self.assertEqual(cells, [1] * 18 + [2] * 7)

    def test_scrolled_out_prompt_head_survives_the_input_transition(self):
        with Shitty(columns=4, rows=2, save_lines=10) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\abcdefgh\r\n")
            terminal.write(b"\r\n")

            self.assertEqual(terminal.scrollback_state(), (2, 4, 2, 2))
            self.assertEqual(terminal.row_semantic(-2), 1)
            self.assertEqual(terminal.row_semantic(-1), 2)

            terminal.write(b"\x1b]133;B\x1b\\")
            terminal.write(b"i")

            current = terminal.model_snapshot()
            self.assertEqual(current.cell(0, 1).semantic, 2)
            self.assertEqual(terminal.last_update_rows(), (1,))

            terminal.wheel_up(2)
            history = terminal.snapshot()
            self.assertEqual(history.lines, ["abcd", "efgh"])
            self.assertEqual(
                [cell.semantic for cell in history.cells],
                [1] * 8,
            )

    def test_multiline_prompt_keeps_prompt_and_input_regions_distinct(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\first\r\n> "
                b"\x1b]133;B\x1b\\ls"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(semantics(snapshot, 0, 0, 5), [1] * 5)
            self.assertEqual(semantics(snapshot, 1, 0, 2), [1] * 2)
            self.assertEqual(semantics(snapshot, 1, 2, 4), [2] * 2)

    def test_running_command_and_next_prompt_have_disjoint_regions(self):
        with Shitty(columns=20, rows=4) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\ls\r\n"
                b"\x1b]133;C\x1b\\file\r\n"
                b"\x1b]133;D;0\x1b\\"
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\x"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(semantics(snapshot, 0, 0, 2), [1, 1])
            self.assertEqual(semantics(snapshot, 0, 2, 4), [2, 2])
            self.assertEqual(semantics(snapshot, 1, 0, 4), [3] * 4)
            self.assertEqual(semantics(snapshot, 2, 0, 2), [1, 1])
            self.assertEqual(snapshot.cell(2, 2).semantic, 2)

    def test_plain_shell_has_no_semantic_regions(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"$ plain")
            snapshot = terminal.snapshot()
            self.assertEqual(semantics(snapshot, 0, 0, 7), [0] * 7)

    def test_alternate_screen_does_not_inherit_live_prompt_state(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ "
                b"\x1b]133;B\x1b\\"
                b"\x1b[?1049happ"
            )
            alternate = terminal.snapshot()
            self.assertEqual(semantics(alternate, 0, 0, 3), [0, 0, 0])

            terminal.write(b"\x1b[?1049lcmd")
            primary = terminal.snapshot()
            self.assertEqual(primary.lines[0][:5], "$ cmd")
            self.assertEqual(semantics(primary, 0, 0, 5), [1, 1, 2, 2, 2])

    def test_last_command_boundaries_exist_without_private_mode_2034(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ ls\r\n"
                b"\x1b]133;C\x1b\\file1\r\nfile2\r\n"
                b"\x1b]133;D;0\x1b\\"
                b"\x1b]133;A\x1b\\$ "
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.all_text()[:4], ("$ ls", "file1", "file2", "$ ")
            )
            self.assertEqual(semantic_text(snapshot, 1), ("$ ls", "$"))
            self.assertEqual(semantic_text(snapshot, 3), ("file1", "file2"))
            self.assertEqual(
                [terminal.row_semantic(row) for row in range(4)],
                [1, 0, 0, 1],
            )

    def test_plain_output_has_no_last_command_boundaries(self):
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"just some plain output\r\n")
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.all_text()[0], "just some plain output")
            self.assertEqual(semantic_text(snapshot, 1), ())
            self.assertEqual(semantic_text(snapshot, 3), ())
            self.assertFalse(terminal.cursor_at_prompt())

    def test_output_without_trailing_newline_ends_before_next_prompt(self):
        # OSC 133;A marks without moving, so the next prompt is painted
        # onto the row the output ended on - contour's own model, whose
        # command blocks split the shared physical row at the CommandEnd
        # marker: only the columns before the ;D belong to the command.
        with Shitty(columns=80, rows=25) as terminal:
            write_prompt_and_run(
                terminal, b"$ printf 'a\\nb\\nc'", b"a\r\nb\r\nc"
            )
            write_next_prompt(terminal)
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.all_text()[:5],
                ("$ printf 'a\\nb\\nc'", "a", "b", "c$ ", ""),
            )
            self.assertEqual(semantic_text(snapshot, 3), ("a", "b", "c"))
            self.assertEqual(semantic_text(snapshot, 1)[-1], "$")
            self.assertEqual(terminal.row_semantic(3), 1)

    def test_single_line_output_ends_before_next_prompt(self):
        # The same shared-row split for a command whose output fits on
        # the line it started on: the physical row reads "hello$ ", and
        # the semantic regions divide it into output and the new prompt.
        with Shitty(columns=80, rows=25) as terminal:
            write_prompt_and_run(terminal, b"$ printf hello", b"hello")
            write_next_prompt(terminal)
            snapshot = terminal.snapshot()

            self.assertEqual(
                terminal.all_text()[:3],
                ("$ printf hello", "hello$ ", ""),
            )
            self.assertEqual(semantic_text(snapshot, 3), ("hello",))
            self.assertEqual(terminal.row_semantic(1), 1)

    def test_command_boundaries_survive_widening_and_narrowing(self):
        for columns in (40, 6):
            with self.subTest(columns=columns), Shitty(
                columns=10, rows=10, save_lines=30
            ) as terminal:
                write_prompt_and_run(terminal, b"$ wrap", b"x" * 25)
                write_next_prompt(terminal)
                terminal.resize(columns, 10)
                snapshot = terminal.snapshot()

                self.assertEqual("".join(semantic_text(snapshot, 3)), "x" * 25)
                self.assertEqual("".join(semantic_text(snapshot, 1)), "$ wrap$")
                self.assertTrue(terminal.cursor_at_prompt())

    def test_prompt_without_a_preceding_command_has_no_output_region(self):
        with Shitty(columns=80, rows=25) as terminal:
            write_next_prompt(terminal)
            snapshot = terminal.snapshot()

            self.assertEqual(terminal.all_text()[0], "$ ")
            self.assertEqual(semantic_text(snapshot, 3), ())
            self.assertEqual(terminal.row_semantic(0), 1)
            self.assertTrue(terminal.cursor_at_prompt())

    def test_live_prompt_geometry_reports_a_fresh_prompt(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\$ \x1b]133;B\x1b\\")
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertEqual(terminal.row_semantic(0), 1)
            self.assertEqual(semantics(snapshot, 0, 0, 2), [1, 1])
            self.assertTrue(terminal.cursor_at_prompt())

    def test_live_prompt_geometry_spans_reflowed_physical_rows(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\line one of prompt\r\n"
                b"> \x1b]133;B\x1b\\"
            )
            self.assertEqual(
                [terminal.row_semantic(row) for row in range(2)], [1, 2]
            )

            terminal.resize(10, 10)
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))
            self.assertEqual(
                [terminal.row_semantic(row) for row in range(3)], [1, 2, 2]
            )
            self.assertEqual(
                terminal.all_text()[:3], ("line one o", "f prompt", "> ")
            )
            self.assertTrue(terminal.cursor_at_prompt())

    def test_live_prompt_geometry_declines_during_command_output(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ \x1b]133;B\x1b\\ls\r\n"
                b"\x1b]133;C\x1b\\a-file\r\n"
            )
            snapshot = terminal.snapshot()

            self.assertFalse(terminal.cursor_at_prompt())
            self.assertEqual(semantic_text(snapshot, 3), ("a-file",))

    def test_live_prompt_geometry_recovers_for_the_next_prompt(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\$ \x1b]133;B\x1b\\ls\r\n"
                b"\x1b]133;C\x1b\\a-file\r\n"
                b"\x1b]133;D;0\x1b\\"
                b"\x1b]133;A\x1b\\$ \x1b]133;B\x1b\\"
            )
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))
            self.assertEqual(terminal.row_semantic(2), 1)
            self.assertTrue(terminal.cursor_at_prompt())

    def test_live_prompt_geometry_is_absent_for_a_plain_shell(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"$ ")

            self.assertEqual(terminal.row_semantic(0), 0)
            self.assertFalse(terminal.cursor_at_prompt())

    def test_live_prompt_geometry_is_hidden_on_the_alternate_screen(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b]133;A\x1b\\$ \x1b]133;B\x1b\\")
            self.assertTrue(terminal.cursor_at_prompt())

            terminal.write(b"\x1b[?1049h")
            self.assertEqual(terminal.row_semantic(0), 0)
            self.assertFalse(terminal.cursor_at_prompt())

            terminal.write(b"\x1b[?1049l")
            self.assertEqual(terminal.row_semantic(0), 1)
            self.assertTrue(terminal.cursor_at_prompt())


    def test_click_modes_cover_the_vertical_variants(self):
        with Shitty(columns=10, rows=3) as terminal:
            observed = []
            for click in (b"w", b"v", b"m", b"line", b"zzz"):
                terminal.write(b"\x1b]133;A;cl=" + click + b"\x1b\\")
                observed.append(terminal.semantic_click())
            terminal.write(b"\x1b]133;A;click_events=1\x1b\\")
            observed.append(terminal.semantic_click())
            self.assertEqual(observed, [6, 5, 4, 3, 0, 1])


    def test_fresh_line_moves_off_a_started_line_only(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"abc\x1b]133;L\x1b\\d\x1b]133;L\x1b\\e")
            self.assertEqual(
                terminal.snapshot().lines, ["abc       ", "d         ", "e         "]
            )


if __name__ == "__main__":
    unittest.main()

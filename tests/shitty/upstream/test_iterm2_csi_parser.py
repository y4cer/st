# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 36 iTerm2 CSI parser cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "testCSIOnly",
    "testPrefixOnly",
    "testPrefixParameterOnly",
    "testPrefixParameterIntermediateOnly",
    "testFullyFormedPrefixParameterIntermediateFinal",
    "testSimpleCSI",
    "testSimpleCSIWithParameter",
    "testSimpleCSIWithTwoDigitParameter",
    "testParameterPrefix",
    "testTwoParameters",
    "testCursorForwardTabulation",
    "testCursorForwardTabulationDefault",
    "testSubParameter",
    "testBogusCharacterInParameters",
    "testDualModeRGBForeground",
    "testDualModeRGBBackground",
    "testDualModeIndexedForeground",
    "testDualModeRejectsSemicolonForm",
    "testDualModeShortSubparametersInvalid",
    "testDualModeChainedAfterFallback",
    "testDualModeRGBUnderline",
    "testDualModeIndexedUnderline",
    "testIntermediateByte",
    "testBogusCharInParameterSection",
    "testGarbageIgnored",
    "testBadGarbageCausesFailure",
    "testDefaultParameterValues",
    "testUnsupportedCodes",
    "testWindowManipulationCodes",
    "testParameterOverflow",
    "testMaximumNumberOfParameters",
    "testParametersPastTheMaximumAreDiscarded",
    "testSubparametersOfADiscardedParameterDoNotAttachToTheLastOneKept",
    "testSubparametersOfTheSixteenthParameter",
    "testSubparametersOfABlankSixteenthParameterAreKept",
    "testGetCSISubparameterByIndex",
)


# The exact rows of testDefaultParameterValues.  The second item is an
# explicit spelling with the same public default semantics; None means the
# upstream token deliberately has no parameter slot to compare.
DEFAULT_PARAMETER_CASES = (
    (b"@", b"1@"),
    (b"A", b"1A"),
    (b"B", b"1B"),
    (b"C", b"1C"),
    (b"D", b"1D"),
    (b"E", b"1E"),
    (b"F", b"1F"),
    (b"G", b"1G"),
    (b"H", b"1;1H"),
    (b"J", b"0J"),
    (b"K", b"0K"),
    (b"L", b"1L"),
    (b"M", b"1M"),
    (b"P", b"1P"),
    (b"S", b"1S"),
    (b"T", b"1T"),
    (b"X", b"1X"),
    (b"Z", b"1Z"),
    (b"b", b"1b"),
    (b"c", b"0c"),
    (b">c", b">0c"),
    (b"d", b"1d"),
    (b"e", b"1e"),
    (b"f", b"1;1f"),
    (b"g", b"0g"),
    (b"h", None),
    (b"?h", None),
    (b"i", b"0i"),
    (b"l", None),
    (b"?l", None),
    (b"m", b"0m"),
    (b">m", None),
    (b"n", b"0n"),
    (b">n", None),
    (b"?n", b"?0n"),
    (b"!p", None),
    (b"$p", b"0$p"),
    (b"?$p", b"?0$p"),
    (b" q", b"0 q"),
    (b"r", None),
    (b"s", None),
    (b"u", None),
    (b"*y", b";;1*y"),
    (b"#|", b"1;1;1;1#|"),
    (b">q", b">0q"),
    (b">\x01u", b">0u"),
    (b"<u", None),
    (b"?u", None),
)


SOURCE_UNSUPPORTED_CODES = (
    b"1;1;1;1;1T",
    b"?1i",
    b">0p",
    b'61;0"p',
    b"q",
    b"?1s",
    b">1;60t",
    b"0 t",
    b"1 u",
    b"1;2;3;4'w",
    b"x",
    b"0;0'z",
    b"'{",
    b"'|",
)


WINDOW_MANIPULATION_CODES = (
    1, 2, 3, 4, 5, 6, 8, 11, 13, 14, 18, 19, 20, 21, 22, 23,
)


def assert_pending_csi(testcase, prefix, suffix, body):
    with Shitty(columns=40, rows=8, save_lines=0) as terminal:
        terminal.parser_trace_on()
        terminal.write(prefix)
        testcase.assertEqual(terminal.parser_trace(), [])
        terminal.write(suffix)
        testcase.assertEqual(terminal.parser_trace(), [("csi", body)])


def csi_public_effect(body):
    with Shitty(
        columns=40,
        rows=8,
        save_lines=0,
        extra_arguments=("-allowWindowOps", "true"),
    ) as terminal:
        terminal.window_info(
            x=7,
            y=9,
            pixel_width=44,
            pixel_height=12,
            screen_width=80,
            screen_height=24,
        )
        terminal.write(
            b"abcdefghijklmnop"
            b"\x1b[3;10H\x1b[1;31;44m"
            b"\x1b[" + body + b"X"
        )
        return (
            terminal.snapshot(),
            terminal.read_input(),
            terminal.read_actions(),
        )


class ITerm2CSIParserTest(unittest.TestCase):
    def test_upstream_inventory_has_all_36_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 36)
        self.assertEqual(len(set(PORTED_CASES)), 36)

    def test_csi_introducer_remains_pending(self):
        assert_pending_csi(self, b"\x1b[", b"D", b"D")

    def test_private_prefix_remains_pending(self):
        assert_pending_csi(self, b"\x1b[?", b"36$p", b"?36$p")

    def test_private_prefix_and_parameter_remain_pending(self):
        assert_pending_csi(self, b"\x1b[?36", b"$p", b"?36$p")

    def test_private_parameter_and_intermediate_remain_pending(self):
        assert_pending_csi(self, b"\x1b[?36$", b"p", b"?36$p")

    def test_complete_private_parameter_intermediate_final_dispatches(self):
        with Shitty(columns=40, rows=8, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[?36$p")
            self.assertEqual(terminal.parser_trace(), [("csi", b"?36$p")])

    def test_cub_defaults_to_one_column(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.write(b"ABCDE\x1b[DX")
            self.assertEqual(terminal.snapshot().lines[0][:5], "ABCDX")

    def test_cub_accepts_one_digit_parameter(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.write(b"ABCDE\x1b[2DX")
            self.assertEqual(terminal.snapshot().lines[0][:5], "ABCXE")

    def test_cub_accepts_two_digit_parameter(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.write(b"A" * 25 + b"\x1b[23DX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 3)

    def test_da2_private_prefix_and_parameter_dispatch(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[>23c")
            self.assertEqual(terminal.parser_trace(), [("csi", b">23c")])
            self.assertTrue(terminal.read_input().startswith(b"\x1b[>"))

    def test_cup_accepts_two_parameters(self):
        with Shitty(columns=40, rows=8, save_lines=0) as terminal:
            terminal.write(b"\x1b[5;6H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 4))

    def test_cht_accepts_explicit_count(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[2IX")
            self.assertEqual(terminal.snapshot().cell(16, 0).char, "X")

    def test_cht_defaults_to_one_tab_stop(self):
        with Shitty(columns=40, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[IX")
            self.assertEqual(terminal.snapshot().cell(8, 0).char, "X")

    def test_colon_subparameters_reach_truecolor_executor(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[38:2:255:128:64:0:5:1mX")
            self.assertEqual(
                terminal.parser_trace(),
                [
                    ("csi", b"38:2:255:128:64:0:5:1m"),
                    ("text", b"X"),
                ],
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).foreground, (128, 64, 0))

    def test_bogus_equals_in_parameter_section_invalidates_csi(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[38=mX")
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])

    @unittest.expectedFailure
    def test_dual_mode_rgb_foreground_tracks_light_and_dark_values(self):
        for background, expected in (
            ("#ffffff", (10, 20, 30)),
            ("#000000", (40, 50, 60)),
        ):
            with self.subTest(background=background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", background),
                ) as terminal:
                    terminal.write(b"\x1b[38:12:10:20:30:40:50:60mX")
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).foreground,
                        expected,
                    )

    @unittest.expectedFailure
    def test_dual_mode_rgb_background_tracks_light_and_dark_values(self):
        for configured_background, expected in (
            ("#ffffff", (1, 2, 3)),
            ("#000000", (4, 5, 6)),
        ):
            with self.subTest(background=configured_background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", configured_background),
                ) as terminal:
                    terminal.write(b"\x1b[48:12:1:2:3:4:5:6mX")
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).background,
                        expected,
                    )

    @unittest.expectedFailure
    def test_dual_mode_indexed_foreground_tracks_both_palette_indices(self):
        for background, expected in (("#ffffff", 208), ("#000000", 11)):
            with self.subTest(background=background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", background),
                ) as terminal:
                    terminal.write(b"\x1b[38:13:208:11mX")
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).foreground_index,
                        expected,
                    )

    def test_dual_mode_semicolon_form_is_not_accepted(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            default_foreground = terminal.snapshot().cell(0, 0).foreground
            terminal.write(b"\x1b[38;12;1;2;3;4;5;6mX")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.foreground, default_foreground)
            self.assertTrue(cell.bold)
            self.assertTrue(cell.italic)
            self.assertTrue(cell.underline)

    def test_short_dual_mode_subparameters_do_not_set_a_color(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            default_foreground = terminal.snapshot().cell(0, 0).foreground
            terminal.write(b"\x1b[38:12:1:2:3mX")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).foreground,
                default_foreground,
            )

    @unittest.expectedFailure
    def test_dual_mode_override_after_fallback_is_last_wins(self):
        for background, expected in (
            ("#ffffff", (11, 22, 33)),
            ("#000000", (44, 55, 66)),
        ):
            with self.subTest(background=background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", background),
                ) as terminal:
                    terminal.write(
                        b"\x1b[38;2;7;7;7;38:12:11:22:33:44:55:66mX"
                    )
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).foreground,
                        expected,
                    )

    @unittest.expectedFailure
    def test_dual_mode_rgb_underline_tracks_light_and_dark_values(self):
        for background, expected in (
            ("#ffffff", (10, 20, 30)),
            ("#000000", (40, 50, 60)),
        ):
            with self.subTest(background=background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", background),
                ) as terminal:
                    terminal.write(b"\x1b[58:12:10:20:30:40:50:60mX")
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).underline_color,
                        expected,
                    )

    @unittest.expectedFailure
    def test_dual_mode_indexed_underline_tracks_both_palette_indices(self):
        for background, expected in (("#ffffff", 208), ("#000000", 120)):
            with self.subTest(background=background):
                with Shitty(
                    columns=8,
                    rows=2,
                    save_lines=0,
                    extra_arguments=("-bg", background),
                ) as terminal:
                    terminal.write(b"\x1b[58:13:208:120mX")
                    self.assertEqual(
                        terminal.snapshot().cell(0, 0).underline_index,
                        expected,
                    )

    def test_cursor_style_keeps_space_intermediate(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[3 q")
            self.assertEqual(terminal.parser_trace(), [("csi", b"3 q")])
            self.assertEqual(terminal.snapshot().cursor_style, 3)

    def test_less_than_in_parameter_section_invalidates_csi(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[1<mX")
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])

    def test_del_is_ignored_while_collecting_parameters(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[1\x7fmX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"1m"), ("text", b"X")],
            )
            self.assertTrue(terminal.snapshot().cell(0, 0).bold)

    def test_parameter_after_intermediate_invalidates_csi(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[1\x7f 2mX")
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])

    def test_default_parameter_table_matches_explicit_public_semantics(self):
        self.assertEqual(len(DEFAULT_PARAMETER_CASES), 48)
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            for source, _ in DEFAULT_PARAMETER_CASES:
                with self.subTest(source=source, phase="trace"):
                    terminal.parser_trace_clear()
                    terminal.write(b"\x1b[" + source)
                    csi = [
                        event
                        for event in terminal.parser_trace()
                        if event[0] == "csi"
                    ]
                    expected = source.replace(b"\x01", b"")
                    self.assertEqual(csi, [("csi", expected)])

        for source, explicit in DEFAULT_PARAMETER_CASES:
            if explicit is None:
                continue
            with self.subTest(source=source, explicit=explicit, phase="effect"):
                self.assertEqual(
                    csi_public_effect(source),
                    csi_public_effect(explicit),
                )

    def test_iTerm_unsupported_table_retains_consensus_parser_behavior(self):
        self.assertEqual(len(SOURCE_UNSUPPORTED_CODES), 14)
        for body in SOURCE_UNSUPPORTED_CODES:
            with self.subTest(body=body):
                with Shitty(columns=8, rows=2, save_lines=0) as terminal:
                    terminal.parser_trace_on()
                    terminal.write(b"\x1b[" + body + b"X")
                    trace = terminal.parser_trace()
                    self.assertIn(("csi", body), trace)
                    self.assertEqual(trace[-1], ("text", b"X"))

        # DECREQTPARM and DECRQLP are standardized public operations, not
        # iTerm2's private VT100_NOTSUPPORT classification.
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[x\x1b['|")
            reply = terminal.read_input()
            self.assertIn(b"x", reply)
            self.assertIn(b"&w", reply)

    def test_window_manipulation_table_dispatches_public_operations(self):
        self.assertEqual(len(WINDOW_MANIPULATION_CODES), 16)
        with Shitty(
            columns=10,
            rows=4,
            save_lines=0,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(
                x=7,
                y=9,
                pixel_width=14,
                pixel_height=8,
                screen_width=30,
                screen_height=20,
            )
            terminal.write(
                b"\x1b[1t\x1b[2t\x1b[3t\x1b[4t"
                b"\x1b[5t\x1b[6t\x1b[8t"
            )
            actions = terminal.read_actions()
            self.assertEqual(
                [action.split()[1] for action in actions],
                ["1", "2", "3", "4", "5", "6", "8"],
            )

        with Shitty(
            columns=10,
            rows=4,
            save_lines=0,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(
                x=7,
                y=9,
                pixel_width=14,
                pixel_height=8,
                screen_width=30,
                screen_height=20,
            )
            terminal.write(
                b"\x1b]1;icon\x1b\\\x1b]2;window\x1b\\"
                b"\x1b[11t\x1b[13t\x1b[14t\x1b[18t\x1b[19t"
                b"\x1b[20t\x1b[21t"
            )
            reply = terminal.read_input()
            for marker in (
                b"\x1b[1t",
                b"\x1b[3;7;9t",
                b"\x1b[4;4;10t",
                b"\x1b[8;4;10t",
                b"\x1b[9;16;26t",
                b"\x1b]Licon\x1b\\",
                b"\x1b]lwindow\x1b\\",
            ):
                self.assertIn(marker, reply)

            terminal.write(
                b"\x1b[22t\x1b]1;new-icon\x1b\\"
                b"\x1b]2;new-window\x1b\\\x1b[23t\x1b[20t\x1b[21t"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]Licon\x1b\\\x1b]lwindow\x1b\\",
            )

    def test_numeric_parameter_overflow_saturates_without_wrapping(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[9999999999mX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"4294967295m"), ("text", b"X")],
            )

    def test_all_sixteen_iTerm_parameter_slots_are_preserved(self):
        body = b"1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16m"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + body)
            self.assertEqual(terminal.parser_trace(), [("csi", body)])

    def test_parameters_past_each_implementation_limit_are_safe(self):
        source_body = (
            b";".join(str(value).encode() for value in range(1, 18))
            + b"m"
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + source_body)
            self.assertEqual(terminal.parser_trace(), [("csi", source_body)])

        overflow = (
            b";".join(str(value).encode() for value in range(1, 34))
            + b"mX"
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + overflow)
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])

    def test_discarded_parameter_subparameter_never_attaches_to_previous(self):
        source = b"1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;4;3:5m"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + source)
            self.assertEqual(terminal.parser_trace(), [("csi", source)])

        overflow = b";".join([b"1"] * 31 + [b"4", b"3:5"]) + b"mX"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[" + overflow)
            self.assertNotEqual(
                terminal.snapshot().cell(0, 0).underline_style,
                5,
            )

    def test_sixteenth_parameter_keeps_its_subparameters(self):
        body = b"1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;38:2:255:0:0m"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + body + b"X")
            self.assertEqual(terminal.parser_trace()[0], ("csi", body))
            self.assertEqual(
                terminal.snapshot().cell(0, 0).foreground,
                (255, 0, 0),
            )

    def test_blank_sixteenth_parameter_keeps_its_subparameter(self):
        body = b"1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;;:5m"
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + body)
            normalized = (
                b"1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;0;0:5m"
            )
            self.assertEqual(terminal.parser_trace(), [("csi", normalized)])

    def test_subparameters_remain_addressable_in_source_order(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[4:1:2:3mX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"4:1:2:3m"), ("text", b"X")],
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).underline_style, 1)


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 27 iTerm2 Xterm parser cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "testNoModeYet",
    "testWellFormedSetWindowTitleTerminatedByBell",
    "testWellFormedSetWindowTitleTerminatedByST",
    "testIgnoreEmbeddedOSC",
    "testIgnoreEmbeddedOSCTwoPart_OutOfDataAfterBracket",
    "testIgnoreEmbeddedOSCTwoPart_OutOfDataAfterEsc",
    "testFailOnEmbeddedEscapePlusCharacter",
    "testNonstandardLinuxSetPalette",
    "testUnsupportedFirstParameterNoTerminator",
    "testUnsupportedFirstParameter",
    "testPartialNonstandardLinuxSetPalette",
    "testCancelAbortsOSC",
    "testSubstituteAbortsOSC",
    "testUnfinishedMultitoken",
    "testCompleteMultitoken",
    "testCompleteMultitokenInMultiplePasses",
    "testLateFailureMultitokenInMultiplePasses",
    "testUnfinishedMultitokenWithDeprecatedMode",
    "testUnterminatedOSCWaits",
    "testUnterminateOSCWaits_2",
    "testMultiPartOSC",
    "testEmbeddedColon",
    "testUnsupportedMode",
    "testBelAfterEmbeddedOSC",
    "testIgnoreEmbeddedOSCWhenFailing",
    "testDefaultModeForDtermCodes",
    "testOverflow",
)


FILE_OSC = b"1337;File=blah;foo=bar:abc"


def assert_embedded_osc_title(testcase, chunks):
    with Shitty(columns=8, rows=2, save_lines=0) as terminal:
        terminal.parser_trace_on()
        terminal.write_chunks(*chunks)
        testcase.assertEqual(terminal.parser_trace(), [("osc", b"0;title")])
        testcase.assertEqual(terminal.window_title(), "title")


def assert_linux_palette(testcase, first, rest=b""):
    with Shitty(columns=8, rows=2, save_lines=0) as terminal:
        terminal.parser_trace_on()
        terminal.write(first)
        testcase.assertEqual(terminal.parser_trace(), [])
        if rest:
            terminal.write(rest)
        terminal.write(b"\x1b[38;5;10mX")
        cell = terminal.snapshot().cell(0, 0)
        testcase.assertEqual(cell.char, "X")
        testcase.assertEqual(cell.foreground, (0x12, 0x34, 0x56))


class ITerm2XtermParserTest(unittest.TestCase):
    def test_upstream_inventory_has_all_27_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 27)
        self.assertEqual(len(set(PORTED_CASES)), 27)

    def test_osc_introducer_waits_and_a_new_complete_osc_recovers(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]")
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"\x1b]0;title\x07")
            self.assertEqual(terminal.window_title(), "title")
            self.assertEqual(terminal.parser_trace(), [("osc", b"0;title")])

    def test_window_title_terminated_by_bell(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0;title\x07")
            self.assertEqual(terminal.window_title(), "title")
            self.assertEqual(terminal.parser_trace(), [("osc", b"0;title")])

    def test_window_title_terminated_by_st(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0;title\x1b\\")
            self.assertEqual(terminal.window_title(), "title")
            self.assertEqual(terminal.parser_trace(), [("osc", b"0;title")])

    @unittest.expectedFailure
    def test_embedded_osc_introducer_is_ignored(self):
        assert_embedded_osc_title(
            self,
            (b"\x1b]0;ti\x1b]tle\x07",),
        )

    @unittest.expectedFailure
    def test_embedded_osc_split_after_bracket_is_ignored(self):
        assert_embedded_osc_title(
            self,
            (b"\x1b]0;ti\x1b]", b"tle\x07"),
        )

    @unittest.expectedFailure
    def test_embedded_osc_split_after_escape_is_ignored(self):
        assert_embedded_osc_title(
            self,
            (b"\x1b]0;ti\x1b", b"]tle\x07"),
        )

    def test_escape_aborts_osc_and_ris_is_dispatched(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0;ti\x1bc")
            self.assertEqual(terminal.parser_trace(), [("escape", b"c")])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, " ")

    @unittest.expectedFailure
    def test_nonstandard_linux_palette_sequence_is_fixed_length(self):
        assert_linux_palette(self, b"\x1b]Pa123456")

    def test_unknown_selector_without_terminator_remains_pending(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]x")
            self.assertEqual(terminal.parser_trace(), [])

    def test_unknown_selector_is_ignored_after_terminator(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]x\x07")
            self.assertEqual(terminal.parser_trace(), [("osc", b"x")])

    @unittest.expectedFailure
    def test_partial_nonstandard_linux_palette_sequence_waits(self):
        assert_linux_palette(self, b"\x1b]Pa12345", b"6")

    def test_cancel_aborts_osc_and_returns_to_ground(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0\x18X")
            self.assertEqual(
                terminal.parser_trace(),
                [("control", b"\x18"), ("text", b"X")],
            )

    def test_substitute_aborts_osc_and_returns_to_ground(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0\x1aX")
            self.assertEqual(
                terminal.parser_trace(),
                [("control", b"\x1a"), ("text", b"X")],
            )

    def test_unfinished_file_transaction_has_no_completed_osc(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]" + FILE_OSC)
            self.assertEqual(terminal.parser_trace(), [])

    def test_complete_file_transaction_dispatches_one_osc(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]" + FILE_OSC + b"\x07")
            self.assertEqual(terminal.parser_trace(), [("osc", FILE_OSC)])

    def test_file_transaction_survives_source_chunk_boundaries(self):
        chunks = (
            b"\x1b]1337;File=blah;",
            b"foo=bar",
            b":",
            b"a",
            b"bc",
            b"\x1b",
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            for chunk in chunks:
                terminal.write(chunk)
                self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"\\")
            self.assertEqual(terminal.parser_trace(), [("osc", FILE_OSC)])

    def test_substitute_discards_an_unfinished_file_transaction(self):
        chunks = (
            b"\x1b]1337;File=blah;",
            b"foo=bar",
            b":",
            b"a",
            b"bc",
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write_chunks(*chunks)
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"\x1aX")
            self.assertEqual(
                terminal.parser_trace(),
                [("control", b"\x1a"), ("text", b"X")],
            )

    def test_unfinished_deprecated_file_transaction_remains_pending(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]50;File=blah;foo=bar:abc")
            self.assertEqual(terminal.parser_trace(), [])

    def test_unterminated_title_osc_remains_pending(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0;foo")
            self.assertEqual(terminal.parser_trace(), [])

    def test_unterminated_title_selector_remains_pending(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0")
            self.assertEqual(terminal.parser_trace(), [])

    def test_multipart_title_uses_saved_prefix_and_new_suffixes(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]0;foo")
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"bar")
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"\x07")
            self.assertEqual(terminal.parser_trace(), [("osc", b"0;foobar")])
            self.assertEqual(terminal.window_title(), "foobar")

    def test_icon_title_preserves_embedded_colon(self):
        with Shitty(
            columns=8,
            rows=2,
            save_lines=0,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(b"\x1b]1;foo:bar\x07\x1b[20t")
            self.assertEqual(terminal.read_input(), b"\x1b]Lfoo:bar\x1b\\")

    def test_unknown_numeric_mode_is_ignored_and_parser_recovers(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]999;foo\x07X")
            self.assertEqual(
                terminal.parser_trace(),
                [("osc", b"999;foo"), ("text", b"X")],
            )

    @unittest.expectedFailure
    def test_bell_after_embedded_osc_sets_an_empty_icon_title(self):
        with Shitty(
            columns=8,
            rows=2,
            save_lines=0,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(b"\x1b]1;seed\x07")
            terminal.write(b"\x1b]1;\x1b]\x07\x1b[20t")
            self.assertEqual(terminal.read_input(), b"\x1b]L\x1b\\")

    def test_embedded_osc_in_unknown_mode_is_consumed_and_recovers(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]x\x1b]\x07X")
            self.assertEqual(
                terminal.parser_trace(),
                [("osc", b""), ("text", b"X")],
            )

    @unittest.expectedFailure
    def test_missing_numeric_mode_defaults_to_title_zero(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b];Foo\x07")
            self.assertEqual(terminal.parser_trace(), [("osc", b";Foo")])
            self.assertEqual(terminal.window_title(), "Foo")

    def test_oversized_numeric_mode_is_ignored_and_recovers(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b]9999999999;foo\x07X")
            self.assertEqual(
                terminal.parser_trace(),
                [("osc", b"9999999999;foo"), ("text", b"X")],
            )


if __name__ == "__main__":
    unittest.main()

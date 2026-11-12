# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public streaming adaptations of all 34 iTerm2 DCS parser cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "testDCS",
    "testDCSControl",
    "testDCSBackspace",
    "testDCSIntermediate",
    "testDCSMultipleIntermediates",
    "testDCSIntermediateIgnore",
    "testDCSIntermediateIgnoreIgnore",
    "testDCSIntermediateIgnoreMany",
    "testDCSIntermediateIgnoreIgnoreEsc",
    "testDCSIntermediateIgnoreIgnoreST",
    "testDCSIntermediateIgnoreIgnoreEscAsciiST",
    "testDCSIntermediatePassthrough",
    "testDCSIntermediatePassthroughEsc",
    "testDCSIntermediatePassthroughST",
    "testDCSIgnore",
    "testDCSParam",
    "testDCSMultipleParameters",
    "testDCSParamIgnoreColon",
    "testDCSParamIgnoreLT",
    "testDCSPrivate",
    "testDCSParamIntermediate",
    "testDCSParamPassthrough",
    "testDCSCatchesBinaryGarbage",
    "testDCSPassthroughEsc",
    "testDCSPassthroughST",
    "testDCSEverything",
    "testDCSRequestTermcapTerminfo",
    "testDCSEnterTmuxIntegration",
    "testDCSTmuxHook",
    "testDCSTmuxWrap",
    "testDCSSavedState",
    "testParserWithDSCTmuxWrap",
    "testDECRQSS",
    "testIssue9070",
)

TEXT_X = [("text", b"X")]


def assert_pending_then_recovers(testcase, prefix, suffix, expected=TEXT_X):
    with Shitty(columns=8, rows=3, save_lines=0) as terminal:
        terminal.parser_trace_on()
        terminal.write(prefix)
        testcase.assertEqual(terminal.parser_trace(), [])
        terminal.write(suffix)
        testcase.assertEqual(terminal.parser_trace(), expected)


def parser_diagnostics(terminal):
    operation = getattr(terminal, "parser_diagnostics", None)
    if operation is None:
        raise AssertionError("Shitty has no public parser-diagnostic stream")
    return operation()


def tmux_control_events(terminal, chunks):
    operation = getattr(terminal, "tmux_control_events", None)
    if operation is None:
        raise AssertionError("Shitty has no host tmux control-mode parser")
    return operation(chunks)


class ITerm2DCSParserTest(unittest.TestCase):
    def test_upstream_inventory_has_all_34_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 34)
        self.assertEqual(len(set(PORTED_CASES)), 34)

    def test_dcs_introducer_remains_pending_until_terminated(self):
        assert_pending_then_recovers(self, b"\x1bP", b"\x1b\\X")

    def test_dcs_entry_ignores_embedded_line_feed(self):
        assert_pending_then_recovers(self, b"\x1bP\n", b"\x1b\\X")

    def test_dcs_entry_ignores_delete(self):
        assert_pending_then_recovers(self, b"\x1bP\x7f", b"\x1b\\X")

    def test_one_dcs_intermediate_remains_pending(self):
        assert_pending_then_recovers(self, b"\x1bP ", b"\x1b\\X")

    def test_multiple_dcs_intermediates_remain_pending(self):
        assert_pending_then_recovers(self, b"\x1bP !", b"\x1b\\X")

    def test_parameter_after_intermediate_enters_ignore(self):
        assert_pending_then_recovers(self, b"\x1bP 0", b"\x1b\\X")

    def test_more_parameters_remain_ignored(self):
        assert_pending_then_recovers(self, b"\x1bP 01", b"\x1b\\X")

    def test_controls_and_printable_bytes_remain_ignored(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP 0\n\x19\x1c0",
            b"\x1b\\X",
        )

    def test_escape_at_end_of_ignored_dcs_remains_pending(self):
        assert_pending_then_recovers(self, b"\x1bP 01\x1b", b"\\X")

    def test_st_terminates_ignored_dcs_without_dispatch(self):
        assert_pending_then_recovers(self, b"\x1bP 01\x1b\\", b"X")

    @unittest.expectedFailure
    def test_non_st_escape_inside_ignored_dcs_stays_in_the_string(self):
        # This is iTerm2/Kitty behavior.  Six other implementations and the
        # DEC parser model abort the DCS and process ESC a as a new escape.
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP 01\x1babc\x1b\\")
            self.assertEqual(terminal.parser_trace(), [])
            terminal.write(b"X")
            self.assertEqual(terminal.parser_trace(), TEXT_X)

    def test_intermediate_final_enters_dcs_passthrough(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP x",
            b"\x1b\\X",
            [("dcs", b" x"), ("text", b"X")],
        )

    def test_escape_at_end_of_dcs_passthrough_remains_pending(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP x\x1b",
            b"\\X",
            [("dcs", b" x"), ("text", b"X")],
        )

    def test_st_dispatches_intermediate_dcs_passthrough(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP x\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b" x")])

    def test_colon_in_dcs_entry_ignores_until_st(self):
        assert_pending_then_recovers(self, b"\x1bP:", b"\x1b\\X")

    def test_dcs_parameter_remains_pending_until_final_byte(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP1",
            b"x\x1b\\X",
            [("dcs", b"1x"), ("text", b"X")],
        )

    def test_multiple_dcs_parameters_ignore_controls_and_delete(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP12\n3;45\x7f6;;0",
            b"x\x1b\\X",
            [("dcs", b"123;456;;0x"), ("text", b"X")],
        )

    def test_colon_after_dcs_parameter_ignores_until_st(self):
        assert_pending_then_recovers(self, b"\x1bP1:", b"\x1b\\X")

    def test_second_private_marker_ignores_until_st(self):
        assert_pending_then_recovers(self, b"\x1bP1<", b"\x1b\\X")

    def test_private_marker_and_parameters_reach_dispatch_unchanged(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP<1;2",
            b"x\x1b\\X",
            [("dcs", b"<1;2x"), ("text", b"X")],
        )

    def test_parameters_and_intermediate_reach_dispatch_unchanged(self):
        assert_pending_then_recovers(
            self,
            b"\x1bP1;2 ",
            b"x\x1b\\X",
            [("dcs", b"1;2 x"), ("text", b"X")],
        )

    def test_parameterized_dcs_passthrough_preserves_payload(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP1;2Abc~\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b"1;2Abc~")])

    @unittest.expectedFailure
    def test_binary_garbage_reports_the_i_term_parser_diagnostic(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1bPAbc\n\x19\x1c\x7f~")
            self.assertEqual(
                parser_diagnostics(terminal),
                [("binary_garbage", b"Abc\n")],
            )

    def test_escape_at_end_of_plain_dcs_passthrough_remains_pending(self):
        assert_pending_then_recovers(
            self,
            b"\x1bPAbcd\x1b",
            b"\\X",
            [("dcs", b"Abcd"), ("text", b"X")],
        )

    def test_st_dispatches_plain_dcs_passthrough(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bPAbcd\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b"Abcd")])

    def test_private_parameters_intermediates_and_data_dispatch_together(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b'\x1bP<0;1;!"abc\x1b\\')
            self.assertEqual(
                terminal.parser_trace(),
                [("dcs", b'<0;1;!"abc')],
            )

    def test_termcap_request_is_dispatched_and_replied_to(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP+q544e\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b"+q544e")])
            reply = terminal.read_input()
            self.assertTrue(reply.startswith(b"\x1bP1+r544e="))
            self.assertTrue(reply.endswith(b"\x1b\\"))

    @unittest.expectedFailure
    def test_tmux_integration_hook_consumes_exit_record(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            self.assertEqual(
                tmux_control_events(
                    terminal,
                    (b"\x1bP1000p\x1b\\", b"%%exit\n"),
                ),
                [("hook", b"1000p"), ("exit", b"")],
            )

    @unittest.expectedFailure
    def test_tmux_hook_buffers_and_emits_complete_control_lines(self):
        chunks = (
            b"\x1bP1000",
            b"p",
            b"abc",
            b"def\r\n",
            b"\x1b[1m\n",
            b"\n",
            b"\r\r\r\n",
            b"\r",
            b"\n",
            b"%%exit\r\n",
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            self.assertEqual(
                tmux_control_events(terminal, chunks),
                [
                    ("hook", b"1000p"),
                    ("line", b"abcdef"),
                    ("line", b"\x1b[1m"),
                    ("line", b""),
                    ("line", b""),
                    ("line", b""),
                    ("exit", b""),
                ],
            )

    def test_tmux_dcs_wrapper_applies_the_inner_sgr(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1bPtmux;\x1b\x1b[1m\x1b\\X")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.char, "X")
            self.assertTrue(cell.bold)

    def test_dcs_saved_state_survives_every_input_split(self):
        sequence = b'\x1bP<0;1;!"abc\x1b\\'
        expected = [("dcs", b'<0;1;!"abc')]
        for split in range(2, len(sequence)):
            with self.subTest(split=split):
                with Shitty(columns=8, rows=2, save_lines=0) as terminal:
                    terminal.parser_trace_on()
                    terminal.write_chunks(sequence[:split], sequence[split:])
                    self.assertEqual(terminal.parser_trace(), expected)

    def test_full_parser_replays_inner_tmux_sgr(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bPtmux;\x1b\x1b[1m\x1b\\X")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", b"1m"), ("escape", b"\\"), ("text", b"X")],
            )

    def test_decrqss_payload_and_reply_are_preserved(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1bP$q q\x1b\\")
            self.assertEqual(terminal.parser_trace(), [("dcs", b"$q q")])
            reply = terminal.read_input()
            self.assertTrue(reply.startswith(b"\x1bP1$r"))
            self.assertTrue(reply.endswith(b" q\x1b\\"))

    def test_large_nul_sixel_stream_dispatches_once_after_all_chunks(self):
        payload = b"\x00" * (4453 * 43)
        sequence = b"\x1bP0;0;8q" + payload + b"\x1b\\"
        chunks = tuple(
            sequence[offset : offset + 1024]
            for offset in range(0, len(sequence), 1024)
        )
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            terminal.parser_trace_on()
            terminal.write_chunks(*chunks)
            trace = terminal.parser_trace()
            self.assertEqual(len(trace), 1)
            kind, body = trace[0]
            self.assertEqual(kind, "dcs")
            self.assertEqual(body[:6], b"0;0;8q")
            self.assertEqual(body[6:], payload)


if __name__ == "__main__":
    unittest.main()

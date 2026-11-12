# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 161 xterm.js EscapeSequenceParser cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "constructor",
    "initial states",
    "reset states",
    "state GROUND execute action",
    "state GROUND print action",
    "trans ANYWHERE --> GROUND with actions",
    "trans ANYWHERE --> ESCAPE with clear",
    "state ESCAPE execute rules",
    "state ESCAPE ignore",
    "trans ESCAPE --> GROUND with ecs_dispatch action",
    "trans ESCAPE --> ESCAPE_INTERMEDIATE with collect action",
    "state ESCAPE_INTERMEDIATE execute rules",
    "state ESCAPE_INTERMEDIATE ignore",
    "state ESCAPE_INTERMEDIATE collect action",
    "trans ESCAPE_INTERMEDIATE --> GROUND with esc_dispatch action",
    "trans ANYWHERE/ESCAPE --> CSI_ENTRY with clear",
    "state CSI_ENTRY execute rules",
    "state CSI_ENTRY ignore",
    "trans CSI_ENTRY --> GROUND with csi_dispatch action",
    "trans CSI_ENTRY --> CSI_PARAM with param/collect actions",
    "state CSI_PARAM execute rules",
    "state CSI_PARAM param action",
    "state CSI_PARAM ignore",
    "trans CSI_PARAM --> GROUND with csi_dispatch action",
    "trans CSI_ENTRY --> CSI_INTERMEDIATE with collect action",
    "trans CSI_PARAM --> CSI_INTERMEDIATE with collect action",
    "state CSI_INTERMEDIATE execute rules",
    "state CSI_INTERMEDIATE collect",
    "state CSI_INTERMEDIATE ignore",
    "trans CSI_INTERMEDIATE --> GROUND with csi_dispatch action",
    'trans CSI_ENTRY --> CSI_PARAM for ":" (0x3a)',
    "trans CSI_PARAM --> CSI_IGNORE",
    "trans CSI_PARAM --> CSI_IGNORE",
    "trans CSI_INTERMEDIATE --> CSI_IGNORE",
    "state CSI_IGNORE execute rules",
    "state CSI_IGNORE ignore",
    "trans CSI_IGNORE --> GROUND",
    "trans ANYWHERE/ESCAPE --> SOS_PM_STRING",
    "state SOS_PM_STRING ignore rules",
    "trans ANYWHERE/ESCAPE --> OSC_STRING",
    "state OSC_STRING ignore rules",
    "state OSC_STRING put action",
    "state DCS_ENTRY",
    "state DCS_ENTRY ignore rules",
    "state DCS_ENTRY --> DCS_PARAM with param/collect actions",
    "state DCS_PARAM ignore rules",
    "state DCS_PARAM param action",
    'trans DCS_ENTRY --> DCS_PARAM for ":" (0x3a)',
    "trans DCS_PARAM --> DCS_IGNORE",
    "trans DCS_INTERMEDIATE --> DCS_IGNORE",
    "state DCS_IGNORE ignore rules",
    "trans DCS_ENTRY --> DCS_INTERMEDIATE with collect action",
    "trans DCS_PARAM --> DCS_INTERMEDIATE with collect action",
    "state DCS_INTERMEDIATE ignore rules",
    "state DCS_INTERMEDIATE collect action",
    "trans DCS_INTERMEDIATE --> DCS_IGNORE",
    "trans DCS_ENTRY --> DCS_PASSTHROUGH with hook",
    "trans DCS_PARAM --> DCS_PASSTHROUGH with hook",
    "trans DCS_INTERMEDIATE --> DCS_PASSTHROUGH with hook",
    "state DCS_PASSTHROUGH put action",
    "state DCS_PASSTHROUGH ignore",
    "state APC_ENTRY",
    "state APC_ENTRY ignore rules",
    "trans APC_ENTRY --> APC_INTERMEDIATE with collect action",
    "trans APC_ENTRY --> APC_PASSTHROUGH with start",
    "trans APC_INTERMEDIATE --> APC_PASSTHROUGH with start",
    "state APC_INTERMEDIATE ignore rules",
    "state APC_PASSTHROUGH put action",
    "state APC_PASSTHROUGH ignore rules",
    "trans APC_PASSTHROUGH --> GROUND|ESCAPE with end action",
    "CSI with print and execute",
    "OSC",
    "single DCS",
    "multi DCS",
    "print + DCS(C1)",
    "print + PM(C1) + print",
    "print + OSC(C1) + print",
    "single APC",
    "multi APC",
    "print + DCS(C1) + print",
    "print + DCS(C0) + print",
    "error recovery",
    "7bit ST should be swallowed",
    "colon notation in CSI params",
    "colon notation in DCS params",
    "CAN should abort DCS",
    "SUB should abort DCS",
    "CAN should abort APC",
    "SUB should abort APC",
    "CAN should abort OSC",
    "SUB should abort OSC",
    "CSI_IGNORE error",
    "DCS_IGNORE error",
    "DCS_PASSTHROUGH error",
    "error else of if (code > 159)",
    "print handler",
    "ESC handler",
    "prevent fallback",
    "allow fallback",
    "Multiple custom handlers fallback once",
    "Multiple custom handlers no fallback",
    "Execution order should go from latest handler down to the original",
    "Dispose should work",
    "Should not corrupt the parser when dispose is called twice",
    "CSI handler",
    "Prevent fallback",
    "Allow fallback",
    "Multiple custom handlers fallback once",
    "Multiple custom handlers no fallback",
    "Execution order should go from latest handler down to the original",
    "Dispose should work",
    "Should not corrupt the parser when dispose is called twice",
    "EXECUTE handler",
    "OSC handler",
    "Prevent fallback",
    "Allow fallback",
    "Multiple custom handlers fallback once",
    "Multiple custom handlers no fallback",
    "Execution order should go from latest handler down to the original",
    "Dispose should work",
    "Should not corrupt the parser when dispose is called twice",
    "DCS handler",
    "Prevent fallback",
    "Allow fallback",
    "Multiple custom handlers fallback once",
    "Multiple custom handlers no fallback",
    "Execution order should go from latest handler down to the original",
    "Dispose should work",
    "Should not corrupt the parser when dispose is called twice",
    "APC handler",
    "Prevent fallback",
    "Allow fallback",
    "Multiple custom handlers fallback once",
    "Multiple custom handlers no fallback",
    "Execution order should go from latest handler down to the original",
    "Dispose should work",
    "Should not corrupt the parser when dispose is called twice",
    "ERROR handler",
    "prefix range 0x3c .. 0x3f, one byte",
    "intermediates range 0x20 .. 0x2f, up to two bytes",
    "final CSI/DCS range 0x40 .. 0x7e (default), one byte",
    "final ESC + APC range 0x30 .. 0x7e, one byte",
    "id calculation - should stacking prefix -> intermediate -> final",
    "ESC",
    "CSI",
    "DCS",
    "APC",
    "sync handlers keep being parsed in sync mode",
    "correct result on sync parse call",
    "correct result on async parse call",
    "sync parse call does not work anymore",
    "improper continuation should throw",
    "reset during async pause continues at next codepoint in chunk",
    "correct result on awaited parse call",
    "correct result on chunked awaited parse calls",
    "multiple async SGR handlers",
    "multiple async ESC handlers",
    "sync/async SGR mixed",
    "multiple async OSC handlers",
    "multiple async DCS handlers",
    "multiple async APC handlers",
)

C0_EXECUTE = (*range(0x00, 0x18), 0x19, *range(0x1C, 0x20))
C1_EXECUTE = (
    0x80,
    0x81,
    0x82,
    0x83,
    0x84,
    0x85,
    0x86,
    0x87,
    0x88,
    0x89,
    0x8A,
    0x8B,
    0x8C,
    0x8D,
    0x8E,
    0x8F,
    0x91,
    0x92,
    0x93,
    0x94,
    0x95,
    0x96,
    0x97,
    0x99,
    0x9A,
)
ESC_DISPATCH_FINALS = (
    *range(0x30, 0x50),
    *range(0x51, 0x58),
    0x59,
    0x5A,
    *range(0x60, 0x7F),
)

# These byte prefixes reach every state from the source case that has a
# terminal-wire counterpart.  APC entry/intermediate/passthrough collapse to
# one public control-string state in Shitty, but remain three separate inputs.
STATE_PREFIXES = (
    b"",                    # GROUND
    b"\x1b",               # ESCAPE
    b"\x1b!",              # ESCAPE_INTERMEDIATE
    b"\x1b[",              # CSI_ENTRY
    b"\x1b[1",             # CSI_PARAM
    b"\x1b[!",             # CSI_INTERMEDIATE
    b"\x1b[1?",            # CSI_IGNORE
    b"\x1bX",              # SOS_PM_STRING
    b"\x1b]2;pending",      # OSC_STRING
    b"\x1bP",              # DCS_ENTRY
    b"\x1bP1",             # DCS_PARAM
    b"\x1bP1?",            # DCS_IGNORE
    b"\x1bP!",             # DCS_INTERMEDIATE
    b"\x1bP$qpending",      # DCS_PASSTHROUGH
    b"\x1b_",              # APC_ENTRY
    b"\x1b_ ",             # APC_INTERMEDIATE
    b"\x1b_0pending",      # APC_PASSTHROUGH
)

HANDLER_INPUT = (
    b"\x1b[1;31mhello \x1b%Gwor\x1bEld!\x1b[0m\r\n$>"
    b"\x1b]1;foo=bar\x1b\\"
)
OSC_HANDLER_INPUT = b"\x1b]1;foo=bar\x1b\\"
DCS_HANDLER_INPUT = b"\x1bP1;2;3+pabc\x1b\\"
APC_HANDLER_INPUT = b"\x1b_+pabc\x1b\\"
DECRQSS_INPUT = b"\x1bP$q\"p\x1b\\"
DECRQSS_REPLY = b"\x1bP1$r64;1\"p\x1b\\"
ASYNC_HANDLER_INPUT = (
    b"\x1b[1;31mhello \x1b%Gwor\x1bEld!\x1b[0m\r\n$>"
    b"\x1bP1;2axyz\x1b\\"
    b"\x1b]1;foo=bar\x1b\\"
    b"\x1b_Xabc\x1b\\FIN"
)
ASYNC_HANDLER_TRACE = [
    ("csi", b"1;31m"),
    ("text", b"hello "),
    ("escape", b"%G"),
    ("text", b"wor"),
    ("escape", b"E"),
    ("text", b"ld!"),
    ("csi", b"0m"),
    ("control", b"\r"),
    ("control", b"\n"),
    ("text", b"$>"),
    ("dcs", b"1;2axyz"),
    ("osc", b"1;foo=bar"),
    ("apc", b"Xabc"),
    ("text", b"FIN"),
]


class XtermJsEscapeSequenceParserTest(unittest.TestCase):
    def setUp(self):
        self.terminal = Shitty(columns=128, rows=8)
        self.terminal.parser_trace_on()

    def tearDown(self):
        self.terminal.close()

    def assert_trace(self, sequence, expected):
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write(sequence)
        self.assertEqual(self.terminal.parser_trace(), expected)

    def test_inventory_accounts_for_all_161_upstream_cases_including_duplicates(self):
        self.assertEqual(len(PORTED_CASES), 161)
        # Upstream repeats both CSI_PARAM -> CSI_IGNORE and
        # DCS_INTERMEDIATE -> DCS_IGNORE. It also misnames an APC example as
        # DCS, but that case has a distinct " + print" suffix.
        # The lifecycle names recur for the ESC, CSI, OSC, DCS and APC handler
        # stacks, with capitalization differences in the first two blocks.
        self.assertEqual(len(set(PORTED_CASES)), 133)

    def test_ground_executes_every_c0_action_byte(self):
        payload = bytes(C0_EXECUTE)
        self.assert_trace(
            payload,
            [("control", bytes((byte,))) for byte in C0_EXECUTE if byte],
        )
        self.assertEqual(self.terminal.read_actions(), ["BELL"])

    def test_ground_prints_the_complete_ascii_graphic_range(self):
        payload = bytes(range(0x20, 0x7F))
        self.assert_trace(payload, [("text", payload)])
        self.assertEqual(self.terminal.snapshot().lines[0][:95], payload.decode())

    def test_anywhere_controls_abort_the_sequence_and_return_to_ground(self):
        for prefix in STATE_PREFIXES:
            for control in (0x18, 0x1A):
                with self.subTest(prefix=prefix, control=control):
                    self.assert_trace(
                        prefix + bytes((control,)) + b"X\x1b\\",
                        [
                            ("control", bytes((control,))),
                            ("text", b"X"),
                            ("escape", b"\\"),
                        ],
                    )

        # Shitty is UTF-8-only by default.  ESC %@ selects the existing ISO
        # single-byte input path where raw C1 controls are meaningful.
        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            for control in C1_EXECUTE:
                with self.subTest(prefix=prefix, control=control):
                    self.terminal.parser_trace_clear()
                    self.terminal.write(prefix + bytes((control,)) + b"X\x1b\\")
                    actual = self.terminal.parser_trace()
                    self.assertEqual(
                        actual[-3:],
                        [
                            ("control", bytes((control,))),
                            ("text", b"X"),
                            ("escape", b"\\"),
                        ],
                    )
                    self.assertFalse(
                        any(event in {"osc", "dcs", "apc", "pm", "sos"}
                            for event, _ in actual)
                    )

        # ST terminates an active control string (or is a no-op elsewhere),
        # and in every state leaves the following graphic in ground.
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, control=0x9C):
                self.terminal.parser_trace_clear()
                self.terminal.write(prefix + b"\x9cX")
                self.assertEqual(self.terminal.parser_trace()[-1:], [("text", b"X")])
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_escape_from_any_state_clears_the_abandoned_sequence(self):
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assert_trace(
                    prefix + b"\x1bDX\x1b\\",
                    [
                        ("escape", b"D"),
                        ("text", b"X"),
                        ("escape", b"\\"),
                    ],
                )

    def test_escape_executes_c0_without_losing_escape_state(self):
        for control in C0_EXECUTE:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b" + bytes((control,)) + b"A",
                    [("escape", b"A")],
                )
                if control == 0x07:
                    self.assertEqual(self.terminal.read_actions(), ["BELL"])

    def test_escape_ignores_del_without_losing_escape_state(self):
        self.assert_trace(b"\x1b\x7fA", [("escape", b"A")])

    def test_escape_dispatches_every_non_introducer_final(self):
        for final in ESC_DISPATCH_FINALS:
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(b"\x1b" + value, [("escape", value)])

    def test_escape_collects_each_intermediate_byte(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b" + value + b"A",
                    [("escape", value + b"A")],
                )

    def test_escape_intermediate_executes_c0_and_keeps_collected_bytes(self):
        for intermediate in range(0x20, 0x30):
            for control in C0_EXECUTE:
                with self.subTest(intermediate=intermediate, control=control):
                    value = bytes((intermediate,))
                    self.assert_trace(
                        b"\x1b" + value + bytes((control,)) + b"A",
                        [("escape", value + b"A")],
                    )
                    if control == 0x07:
                        self.assertEqual(self.terminal.read_actions(), ["BELL"])

    def test_escape_intermediate_ignores_del(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b" + value + b"\x7fA",
                    [("escape", value + b"A")],
                )

    def test_escape_intermediate_collects_multiple_bytes(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b!" + value + b"A",
                    [("escape", b"!" + value + b"A")],
                )

    def test_escape_intermediate_dispatches_every_final(self):
        for final in range(0x30, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1b!" + value,
                    [("escape", b"!" + value)],
                )

    def test_csi_introducer_from_any_state_clears_old_parameters(self):
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x1b["):
                self.assert_trace(
                    prefix + b"\x1b[HX\x1b\\",
                    [("csi", b"H"), ("text", b"X"), ("escape", b"\\")],
                )

        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x9b"):
                self.assert_trace(
                    prefix + b"\x9bHX\x1b\\",
                    [("csi", b"H"), ("text", b"X"), ("escape", b"\\")],
                )
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_csi_entry_executes_c0_without_losing_csi_state(self):
        for control in C0_EXECUTE:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b[" + bytes((control,)) + b"H",
                    [("csi", b"H")],
                )
                if control == 0x07:
                    self.assertEqual(self.terminal.read_actions(), ["BELL"])

    def test_csi_entry_ignores_del(self):
        self.assert_trace(b"\x1b[\x7fH", [("csi", b"H")])

    def test_csi_entry_dispatches_every_final(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(b"\x1b[" + value, [("csi", value)])

    def test_csi_entry_collects_parameters_and_private_prefixes(self):
        for digit in range(10):
            with self.subTest(digit=digit):
                raw = str(digit).encode()
                self.assert_trace(b"\x1b[" + raw + b"m", [("csi", raw + b"m")])
        self.assert_trace(b"\x1b[;m", [("csi", b"0;0m")])
        for prefix in b"<=>?":
            with self.subTest(prefix=prefix):
                raw = bytes((prefix,))
                self.assert_trace(b"\x1b[" + raw + b"m", [("csi", raw + b"m")])

    def test_csi_param_executes_c0_without_losing_parameters(self):
        for control in C0_EXECUTE:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b[1" + bytes((control,)) + b"m",
                    [("csi", b"1m")],
                )
                if control == 0x07:
                    self.assertEqual(self.terminal.read_actions(), ["BELL"])

    def test_csi_param_accumulates_digits_and_empty_parameters(self):
        for digit in range(10):
            with self.subTest(digit=digit):
                raw = str(digit).encode()
                self.assert_trace(b"\x1b[" + raw + b"m", [("csi", raw + b"m")])
        self.assert_trace(b"\x1b[;m", [("csi", b"0;0m")])

    def test_csi_param_ignores_del(self):
        self.assert_trace(b"\x1b[1\x7fm", [("csi", b"1m")])

    def test_csi_param_dispatches_every_final_with_all_parameters(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1b[0;1" + value,
                    [("csi", b"0;1" + value)],
                )

    def test_csi_entry_collects_each_intermediate_byte(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b[" + value + b"m",
                    [("csi", value + b"m")],
                )

    def test_csi_param_collects_each_intermediate_byte(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b[1" + value + b"m",
                    [("csi", b"1" + value + b"m")],
                )

    def test_csi_intermediate_executes_c0_and_keeps_collected_bytes(self):
        for control in C0_EXECUTE:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b[!" + bytes((control,)) + b"m",
                    [("csi", b"!m")],
                )
                self.assertEqual(
                    self.terminal.read_actions(),
                    ["BELL"] if control == 0x07 else [],
                )

    def test_csi_intermediate_collects_multiple_bytes(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1b[!" + value + b"m",
                    [("csi", b"!" + value + b"m")],
                )

    def test_csi_intermediate_ignores_del(self):
        self.assert_trace(b"\x1b[!\x7fm", [("csi", b"!m")])

    def test_csi_intermediate_dispatches_every_final(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1b[!" + value,
                    [("csi", b"!" + value)],
                )

    def test_csi_entry_accepts_a_leading_subparameter_separator(self):
        self.assert_trace(b"\x1b[:m", [("csi", b"0:0m")])

    def test_csi_param_private_marker_enters_ignore(self):
        for marker in b"<=>?":
            with self.subTest(marker=marker):
                self.assert_trace(
                    b"\x1b[1;" + bytes((marker,)) + b"mX",
                    [("text", b"X")],
                )

    def test_csi_param_duplicate_upstream_ignore_case_keeps_empty_parameter(self):
        for marker in b"<=>?":
            with self.subTest(marker=marker):
                self.assert_trace(
                    b"\x1b[;" + bytes((marker,)) + b"mX",
                    [("text", b"X")],
                )

    def test_csi_intermediate_parameter_bytes_enter_ignore(self):
        for parameter in range(0x30, 0x40):
            with self.subTest(parameter=parameter):
                self.assert_trace(
                    b"\x1b[!" + bytes((parameter,)) + b"mX",
                    [("text", b"X")],
                )

    def test_csi_ignore_executes_c0_without_leaving_ignore(self):
        for control in C0_EXECUTE:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b[!0" + bytes((control,)) + b"mX",
                    [("text", b"X")],
                )
                self.assertEqual(
                    self.terminal.read_actions(),
                    ["BELL"] if control == 0x07 else [],
                )

    def test_csi_ignore_discards_parameter_bytes_and_del(self):
        for ignored in (*range(0x20, 0x40), 0x7F):
            with self.subTest(ignored=ignored):
                self.assert_trace(
                    b"\x1b[!0" + bytes((ignored,)) + b"mX",
                    [("text", b"X")],
                )

    def test_csi_ignore_returns_to_ground_on_every_final(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                self.assert_trace(
                    b"\x1b[!0" + bytes((final,)) + b"X",
                    [("text", b"X")],
                )

    def test_sos_and_pm_introducers_replace_every_parser_state(self):
        for prefix in STATE_PREFIXES:
            for introducer, event in ((b"\x1bX", "sos"), (b"\x1b^", "pm")):
                with self.subTest(prefix=prefix, introducer=introducer):
                    self.assert_trace(
                        prefix + introducer + b"a\x1b\\X",
                        [(event, b"a"), ("text", b"X")],
                    )

        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            for introducer, event in ((b"\x98", "sos"), (b"\x9e", "pm")):
                with self.subTest(prefix=prefix, introducer=introducer):
                    self.assert_trace(
                        prefix + introducer + b"a\x9cX",
                        [(event, b"a"), ("text", b"X")],
                    )
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_sos_and_pm_payload_is_inert_until_st(self):
        payload = bytes((*range(0x00, 0x18), 0x19, *range(0x1C, 0x7F)))
        for introducer, event in ((b"\x1bX", "sos"), (b"\x1b^", "pm")):
            with self.subTest(introducer=introducer):
                self.assert_trace(
                    introducer + payload + b"\x1b\\X",
                    [(event, payload), ("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_osc_introducers_replace_every_parser_state(self):
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x1b]"):
                self.assert_trace(
                    prefix + b"\x1b]999;a\x1b\\X",
                    [("osc", b"999;a"), ("text", b"X")],
                )

        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x9d"):
                self.assert_trace(
                    prefix + b"\x9d999;a\x9cX",
                    [("osc", b"999;a"), ("text", b"X")],
                )
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_osc_ignores_c0_without_losing_payload(self):
        ignored = (*range(0x00, 0x07), *range(0x08, 0x18), 0x19,
                   *range(0x1C, 0x20))
        for control in ignored:
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1b]999;a" + bytes((control,)) + b"b\x1b\\X",
                    [("osc", b"999;ab"), ("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), ["OSC 999 6162"])

    def test_osc_collects_every_ascii_payload_byte(self):
        for byte in range(0x20, 0x7F):
            with self.subTest(byte=byte):
                value = bytes((byte,))
                self.assert_trace(
                    b"\x1b]999;" + value + b"\x1b\\X",
                    [("osc", b"999;" + value), ("text", b"X")],
                )

    def test_dcs_introducers_replace_every_parser_state(self):
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x1bP"):
                self.assert_trace(
                    prefix + b"\x1bP$qm\x1b\\X",
                    [("dcs", b"$qm"), ("text", b"X")],
                )

        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x90"):
                self.assert_trace(
                    prefix + b"\x90$qm\x9cX",
                    [("dcs", b"$qm"), ("text", b"X")],
                )
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_dcs_entry_ignores_c0_and_del(self):
        for control in (*C0_EXECUTE, 0x7F):
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1bP" + bytes((control,)) + b"$qm\x1b\\X",
                    [("dcs", b"$qm"), ("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_dcs_entry_collects_parameters_and_private_markers(self):
        for digit in range(10):
            with self.subTest(digit=digit):
                value = str(digit).encode()
                self.assert_trace(
                    b"\x1bP" + value + b"$qm\x1b\\",
                    [("dcs", value + b"$qm")],
                )
        self.assert_trace(b"\x1bP;$qm\x1b\\", [("dcs", b";$qm")])
        for marker in b"<=>?":
            with self.subTest(marker=marker):
                value = bytes((marker,))
                self.assert_trace(
                    b"\x1bP" + value + b"$qm\x1b\\",
                    [("dcs", value + b"$qm")],
                )

    def test_dcs_param_ignores_c0_and_del(self):
        for control in (*C0_EXECUTE, 0x7F):
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1bP1" + bytes((control,)) + b"$qm\x1b\\X",
                    [("dcs", b"1$qm"), ("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_dcs_param_accumulates_digits_and_empty_parameters(self):
        for digit in range(10):
            with self.subTest(digit=digit):
                value = str(digit).encode()
                self.assert_trace(
                    b"\x1bP1" + value + b"$qm\x1b\\",
                    [("dcs", b"1" + value + b"$qm")],
                )
        self.assert_trace(b"\x1bP1;$qm\x1b\\", [("dcs", b"1;$qm")])

    def test_dcs_leading_colon_enters_ignore_by_consensus(self):
        self.assert_trace(b"\x1bP:$qm\x1b\\X", [("text", b"X")])

    def test_dcs_param_private_marker_enters_ignore(self):
        for marker in b"<=>?":
            with self.subTest(marker=marker):
                self.assert_trace(
                    b"\x1bP1;" + bytes((marker,)) + b"mignored\x1b\\X",
                    [("text", b"X")],
                )

    def test_dcs_intermediate_parameter_byte_enters_ignore(self):
        for parameter in range(0x30, 0x40):
            with self.subTest(parameter=parameter):
                self.assert_trace(
                    b"\x1bP!" + bytes((parameter,)) + b"ignored\x1b\\X",
                    [("text", b"X")],
                )

    def test_dcs_ignore_discards_every_non_terminating_byte(self):
        ignored = (*C0_EXECUTE, *range(0x20, 0x80))
        for byte in ignored:
            with self.subTest(byte=byte):
                self.assert_trace(
                    b"\x1bP!0" + bytes((byte,)) + b"\x1b\\X",
                    [("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_dcs_entry_collects_each_intermediate_byte(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1bP" + value + b"zm\x1b\\",
                    [("dcs", value + b"zm")],
                )

    def test_dcs_param_collects_each_intermediate_byte(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1bP1" + value + b"zm\x1b\\",
                    [("dcs", b"1" + value + b"zm")],
                )

    def test_dcs_intermediate_ignores_c0_and_del(self):
        for control in (*C0_EXECUTE, 0x7F):
            with self.subTest(control=control):
                self.assert_trace(
                    b"\x1bP!" + bytes((control,)) + b"zm\x1b\\",
                    [("dcs", b"!zm")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_dcs_intermediate_collects_multiple_bytes(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(
                    b"\x1bP!" + value + b"zm\x1b\\",
                    [("dcs", b"!" + value + b"zm")],
                )

    def test_dcs_collected_intermediate_then_parameter_enters_ignore(self):
        for parameter in range(0x30, 0x40):
            with self.subTest(parameter=parameter):
                self.assert_trace(
                    b"\x1bP !" + bytes((parameter,)) + b"ignored\x1b\\X",
                    [("text", b"X")],
                )

    def test_dcs_entry_dispatches_every_final_to_a_payload_handler(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1bP" + value + b"\x1b\\",
                    [("dcs", value)],
                )

    def test_dcs_param_dispatches_every_final_with_parameters(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1bP1;2" + value + b"\x1b\\",
                    [("dcs", b"1;2" + value)],
                )

    def test_dcs_intermediate_dispatches_every_final_with_collection(self):
        for final in range(0x40, 0x7F):
            with self.subTest(final=final):
                value = bytes((final,))
                self.assert_trace(
                    b"\x1bP!" + value + b"\x1b\\",
                    [("dcs", b"!" + value)],
                )

    def test_dcs_passthrough_delivers_every_payload_byte_without_executing_c0(self):
        payload_bytes = (*range(0x00, 0x18), 0x19,
                         *range(0x1C, 0x7F))
        for byte in payload_bytes:
            with self.subTest(byte=byte):
                value = bytes((byte,))
                self.assert_trace(
                    b"\x1bPz" + value + b"\x1b\\",
                    [("dcs", b"z" + value)],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_dcs_passthrough_ignores_del(self):
        self.assert_trace(b"\x1bPz\x7f\x1b\\", [("dcs", b"z")])

    def test_apc_introducers_replace_every_parser_state(self):
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x1b_"):
                self.assert_trace(
                    prefix + b"\x1b_a\x1b\\X",
                    [("apc", b"a"), ("text", b"X")],
                )

        self.terminal.write(b"\x1b%@")
        for prefix in STATE_PREFIXES:
            with self.subTest(prefix=prefix, introducer=b"\x9f"):
                self.assert_trace(
                    prefix + b"\x9fa\x9cX",
                    [("apc", b"a"), ("text", b"X")],
                )
        self.terminal.write(b"\x1b%G")
        self.terminal.parser_trace_clear()

    def test_apc_entry_preserves_inert_c0_but_ignores_del(self):
        for byte in (*C0_EXECUTE, 0x7F):
            with self.subTest(byte=byte):
                value = bytes((byte,))
                payload = b"" if byte == 0x7F else value
                self.assert_trace(
                    b"\x1b_" + value + b"\x1b\\X",
                    [("apc", payload), ("text", b"X")],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_apc_entry_preserves_each_intermediate_prefix(self):
        for intermediate in range(0x20, 0x30):
            with self.subTest(intermediate=intermediate):
                value = bytes((intermediate,))
                self.assert_trace(b"\x1b_" + value + b"\x1b\\", [("apc", value)])

    def test_apc_entry_preserves_every_start_byte(self):
        for start in range(0x30, 0x7F):
            with self.subTest(start=start):
                value = bytes((start,))
                self.assert_trace(b"\x1b_" + value + b"\x1b\\", [("apc", value)])

    def test_apc_intermediate_preserves_every_start_byte(self):
        for start in range(0x30, 0x7F):
            with self.subTest(start=start):
                value = bytes((start,))
                self.assert_trace(
                    b"\x1b_ " + value + b"\x1b\\",
                    [("apc", b" " + value)],
                )

    def test_apc_intermediate_preserves_inert_c0_but_ignores_del(self):
        for byte in (*C0_EXECUTE, 0x7F):
            with self.subTest(byte=byte):
                value = bytes((byte,))
                payload = b" " if byte == 0x7F else b" " + value
                self.assert_trace(
                    b"\x1b_ " + value + b"\x1b\\",
                    [("apc", payload)],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_apc_passthrough_preserves_standard_command_bytes(self):
        for byte in (*range(0x08, 0x0E), *range(0x20, 0x7F)):
            with self.subTest(byte=byte):
                value = bytes((byte,))
                self.assert_trace(
                    b"\x1b_0" + value + b"\x1b\\",
                    [("apc", b"0" + value)],
                )

    def test_apc_passthrough_keeps_other_bytes_inert_in_its_public_payload(self):
        other = (*range(0x00, 0x08), *range(0x0E, 0x18), 0x19,
                 *range(0x1C, 0x20), 0x7F)
        for byte in other:
            with self.subTest(byte=byte):
                value = bytes((byte,))
                payload = b"0" if byte == 0x7F else b"0" + value
                self.assert_trace(
                    b"\x1b_0" + value + b"\x1b\\",
                    [("apc", payload)],
                )
                self.assertEqual(self.terminal.read_actions(), [])

    def test_apc_termination_cancellation_and_escape_recovery(self):
        self.assert_trace(
            b"\x1b_0\x1b\\X",
            [("apc", b"0"), ("text", b"X")],
        )
        for cancel in (0x18, 0x1A):
            with self.subTest(cancel=cancel):
                self.assert_trace(
                    b"\x1b_0" + bytes((cancel,)) + b"X",
                    [("control", bytes((cancel,))), ("text", b"X")],
                )
        self.assert_trace(
            b"\x1b_0\x1bDX",
            [("escape", b"D"), ("text", b"X")],
        )

    def test_example_csi_interleaves_dispatch_text_and_execute(self):
        self.assert_trace(
            b"\x1b[<31;5mHello World! \xc3\xb6\xc3\xa4\xc3\xbc\xe2\x82\xac\nabc",
            [
                ("csi", b"<31;5m"),
                ("text", b"Hello World! \xc3\xb6\xc3\xa4\xc3\xbc\xe2\x82\xac"),
                ("control", b"\n"),
                ("text", b"abc"),
            ],
        )

    def test_example_osc_bel_dispatches_the_complete_utf8_payload(self):
        self.assert_trace(
            b"\x1b]0;abc123\xe2\x82\xac\xc3\xb6\xc3\xa4\xc3\xbc\x07",
            [("osc", b"0;abc123\xe2\x82\xac\xc3\xb6\xc3\xa4\xc3\xbc")],
        )

    def test_example_single_dcs_accepts_a_mixed_c1_terminator(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"\x1bP1;2;3+$a\xc3\xa4bc;d\xc3\xa4e\x9c",
            [("dcs", b"1;2;3+$abc;de")],
        )

    def test_example_dcs_state_and_payload_survive_multiple_writes(self):
        self.terminal.write(b"\x1bP1;2;3+$abc;de")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.terminal.write(b"abc\x1b\\")
        self.assertEqual(
            self.terminal.parser_trace(),
            [("dcs", b"1;2;3+$abc;deabc")],
        )

    def test_example_c1_dcs_is_atomic_between_print_runs(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x901;2;3+$abc;de\x9cxyz",
            [
                ("text", b"abc"),
                ("dcs", b"1;2;3+$abc;de"),
                ("text", b"xyz"),
            ],
        )

    def test_example_c1_sos_is_inert_between_print_runs(self):
        # The upstream name says PM, but 0x98 is SOS in ECMA-48.
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x98123tzf\x9cdefg",
            [
                ("text", b"abc"),
                ("sos", b"123tzf"),
                ("text", b"defg"),
            ],
        )

    def test_example_c1_osc_is_atomic_between_print_runs(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x9d123;tzf\x9cdefg",
            [
                ("text", b"abc"),
                ("osc", b"123;tzf"),
                ("text", b"defg"),
            ],
        )

    def test_example_single_apc_accepts_a_mixed_c1_terminator(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"\x1b_X3+$a\xc3\xa4bc;d\xc3\xa4e\x9c",
            [("apc", b"X3+$a\xc3\xa4bc;d\xc3\xa4e")],
        )

    def test_example_apc_state_and_payload_survive_multiple_writes(self):
        self.terminal.write(b"\x1b_Xabc;de")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.terminal.write(b"abc\x1b\\")
        self.assertEqual(
            self.terminal.parser_trace(),
            [("apc", b"Xabc;deabc")],
        )

    def test_example_c1_apc_is_atomic_between_print_runs(self):
        # The upstream name says DCS, but 0x9f is APC in ECMA-48.
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x9fAbc;de\x9cxyz",
            [
                ("text", b"abc"),
                ("apc", b"Abc;de"),
                ("text", b"xyz"),
            ],
        )

    def test_example_c0_apc_is_atomic_between_print_runs(self):
        self.assert_trace(
            b"abc\x1b_Abc;de\x1b\\xyz",
            [
                ("text", b"abc"),
                ("apc", b"Abc;de"),
                ("text", b"xyz"),
            ],
        )

    def test_example_unicode_error_recovery_discards_the_invalid_csi_graphic(self):
        # Use a 7-bit CSI for the following recovery sequence so this case is
        # independent of the configured C1 input mode.
        self.assert_trace(
            b"\x1b[1\xe2\x82\xacabcdefg\x1b[<;c",
            [
                ("text", b"abcdefg"),
                ("csi", b"<0;0c"),
            ],
        )

        self.terminal.parser_trace_clear()
        self.terminal.write_chunks(
            b"\x1b[1\xe2",
            b"\x82",
            b"\xacabcdefg\x1b[<;c",
        )
        self.assertEqual(
            self.terminal.parser_trace(),
            [("text", b"abcdefg"), ("csi", b"<0;0c")],
        )

    def test_example_seven_bit_st_terminates_a_c1_osc_without_leaking(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x9d123;tzf\x1b\\defg",
            [
                ("text", b"abc"),
                ("osc", b"123;tzf"),
                ("text", b"defg"),
            ],
        )

    def test_example_colon_csi_preserves_empty_subparameters(self):
        self.assert_trace(
            b"\x1b[<31;5::123:;8mHello World! \xc3\xb6\xc3\xa4\xc3\xbc\xe2\x82\xac\nabc",
            [
                ("csi", b"<31;5:0:123:0;8m"),
                ("text", b"Hello World! \xc3\xb6\xc3\xa4\xc3\xbc\xe2\x82\xac"),
                ("control", b"\n"),
                ("text", b"abc"),
            ],
        )

    def test_example_colon_dcs_is_ignored_by_consensus(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"abc\x901;2::55;3+$abc;de\x9cX",
            [("text", b"abcX")],
        )

    def test_example_can_aborts_an_active_dcs(self):
        self.assert_trace(
            b"abc\x1bP1;2;55;3+$abc;de\x18X",
            [("text", b"abc"), ("control", b"\x18"), ("text", b"X")],
        )

    def test_example_sub_aborts_an_active_dcs(self):
        self.assert_trace(
            b"abc\x1bP1;2;55;3+$abc;de\x1aX",
            [("text", b"abc"), ("control", b"\x1a"), ("text", b"X")],
        )

    def test_example_can_aborts_an_active_apc(self):
        self.assert_trace(
            b"abc\x1b_Xbc;de\x18X",
            [("text", b"abc"), ("control", b"\x18"), ("text", b"X")],
        )

    def test_example_sub_aborts_an_active_apc(self):
        self.assert_trace(
            b"abc\x1b_Xbc;de\x1aX",
            [("text", b"abc"), ("control", b"\x1a"), ("text", b"X")],
        )

    def test_example_can_aborts_an_active_osc(self):
        self.assert_trace(
            b"abc\x1b]0;title\x18X",
            [("text", b"abc"), ("control", b"\x18"), ("text", b"X")],
        )

    def test_example_sub_aborts_an_active_osc(self):
        self.assert_trace(
            b"abc\x1b]0;title\x1aX",
            [("text", b"abc"), ("control", b"\x1a"), ("text", b"X")],
        )

    def test_coverage_csi_ignore_recovers_after_the_invalid_codepoint(self):
        self.assert_trace(
            b"\x1b[1?\xe2\x82\xac\xc3\xb6\xc3\xa4\xc3\xbcmy",
            [("text", b"\xc3\xb6\xc3\xa4\xc3\xbcmy")],
        )

    def test_coverage_dcs_ignore_swallows_unicode_until_st(self):
        self.assert_trace(
            b"A\x1bP:\xe2\x82\xac\xc3\xb6\xc3\xa4\xc3\xbc\x1b\\B",
            [("text", b"AB")],
        )

    def test_coverage_dcs_passthrough_discards_unicode_across_writes(self):
        self.terminal.parser_trace_clear()
        self.terminal.write(b"\x1bP1;2;3+$a\xe2\x82\xac\xc3\xb6\xc3\xa4\xc3\xbc")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.terminal.write(b"\x1b\\X")
        self.assertEqual(
            self.terminal.parser_trace(),
            [
                ("dcs", b"1;2;3+$a"),
                ("text", b"X"),
            ],
        )

    def test_coverage_standalone_c1_st_is_inert_in_ground(self):
        self.terminal.write(b"\x1b%@")
        self.assert_trace(
            b"A\x9cB",
            [("text", b"A"), ("control", b"\x9c"), ("text", b"B")],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][:2], "AB")

    def test_handler_print_case_preserves_every_public_text_run(self):
        self.assert_trace(
            HANDLER_INPUT,
            [
                ("csi", b"1;31m"),
                ("text", b"hello "),
                ("escape", b"%G"),
                ("text", b"wor"),
                ("escape", b"E"),
                ("text", b"ld!"),
                ("csi", b"0m"),
                ("control", b"\r"),
                ("control", b"\n"),
                ("text", b"$>"),
                ("osc", b"1;foo=bar"),
            ],
        )
        self.assertEqual(
            [line.rstrip() for line in self.terminal.snapshot().lines[:3]],
            ["hello wor", "ld!", "$>"],
        )

    def test_handler_esc_case_dispatches_utf8_selection_and_nel(self):
        self.assert_trace(
            b"a\x1b%Gb\x1bEc",
            [
                ("text", b"a"),
                ("escape", b"%G"),
                ("text", b"b"),
                ("escape", b"E"),
                ("text", b"c"),
            ],
        )
        snapshot = self.terminal.snapshot()
        self.assertEqual(snapshot.lines[0][:2], "ab")
        self.assertEqual(snapshot.lines[1][0], "c")

    def test_handler_esc_prevent_fallback_maps_to_one_known_dispatch(self):
        self.assert_trace(
            b"a\x1bEb",
            [("text", b"a"), ("escape", b"E"), ("text", b"b")],
        )
        self.assertEqual(self.terminal.snapshot().cursor_y, 1)

    def test_handler_esc_allow_fallback_maps_to_the_standard_nel_effect(self):
        self.terminal.write(b"a\x1bEb")
        snapshot = self.terminal.snapshot()
        self.assertEqual(snapshot.lines[0][0], "a")
        self.assertEqual(snapshot.lines[1][0], "b")
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_handler_esc_multiple_fallback_runs_the_effect_once(self):
        self.terminal.write(b"a\x1bEb")
        self.assertEqual(self.terminal.snapshot().cursor_y, 1)

    def test_handler_esc_multiple_no_fallback_maps_to_an_unknown_dispatch(self):
        self.assert_trace(
            b"a\x1b%zb",
            [("text", b"a"), ("escape", b"%z"), ("text", b"b")],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][:2], "ab")

    def test_handler_esc_latest_to_original_maps_to_identifier_byte_order(self):
        self.assert_trace(b"\x1b%G", [("escape", b"%G")])

    def test_handler_esc_dispose_maps_to_fallback_remaining_available(self):
        self.terminal.write(b"\x1b%z\x1bEX")
        snapshot = self.terminal.snapshot()
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
        self.assertEqual(snapshot.lines[1][0], "X")

    def test_handler_esc_double_dispose_does_not_corrupt_following_dispatch(self):
        self.terminal.write(b"\x1b%z\x1b#z\x1bEX")
        snapshot = self.terminal.snapshot()
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
        self.assertEqual(snapshot.lines[1][0], "X")

    def test_handler_csi_case_dispatches_both_sgr_sequences(self):
        self.assert_trace(
            b"\x1b[1;31mX\x1b[0mY",
            [
                ("csi", b"1;31m"),
                ("text", b"X"),
                ("csi", b"0m"),
                ("text", b"Y"),
            ],
        )
        snapshot = self.terminal.model_snapshot()
        self.assertTrue(snapshot.cell(0, 0).bold)
        self.assertEqual(snapshot.cell(0, 0).foreground_index, 1)
        self.assertFalse(snapshot.cell(1, 0).bold)

    def test_handler_csi_prevent_fallback_maps_to_no_unknown_default_effect(self):
        before = self.terminal.pen_state()
        self.assert_trace(b"\x1b[1;31zX", [("csi", b"1;31z"), ("text", b"X")])
        self.assertEqual(self.terminal.pen_state(), before)

    def test_handler_csi_allow_fallback_maps_to_the_standard_sgr_effect(self):
        self.terminal.write(b"\x1b[1;31m")
        pen = self.terminal.pen_state()
        self.assertTrue(pen.bold)
        self.assertEqual(pen.foreground_index, 1)

    def test_handler_csi_multiple_fallback_runs_sgr_once(self):
        self.assert_trace(b"\x1b[1;31m", [("csi", b"1;31m")])
        pen = self.terminal.pen_state()
        self.assertTrue(pen.bold)
        self.assertEqual(pen.foreground_index, 1)

    def test_handler_csi_multiple_no_fallback_maps_to_unknown_csi(self):
        before = self.terminal.pen_state()
        self.terminal.write(b"\x1b[1;31z")
        self.assertEqual(self.terminal.pen_state(), before)

    def test_handler_csi_latest_to_original_maps_to_wire_order(self):
        self.terminal.write(b"\x1b[31m\x1b[32mX")
        self.assertEqual(self.terminal.model_snapshot().cell(0, 0).foreground_index, 2)

    def test_handler_csi_dispose_keeps_the_standard_handler_available(self):
        self.terminal.write(b"\x1b[1;31z\x1b[1;31m")
        pen = self.terminal.pen_state()
        self.assertTrue(pen.bold)
        self.assertEqual(pen.foreground_index, 1)

    def test_handler_csi_double_dispose_does_not_corrupt_following_dispatch(self):
        self.terminal.write(b"\x1b[1;31z\x1b[1;31z\x1b[1;31m")
        pen = self.terminal.pen_state()
        self.assertTrue(pen.bold)
        self.assertEqual(pen.foreground_index, 1)

    def test_handler_execute_dispatches_cr_and_lf_and_survives_repeat(self):
        self.assert_trace(
            b"ab\rX\nY",
            [
                ("text", b"ab"),
                ("control", b"\r"),
                ("text", b"X"),
                ("control", b"\n"),
                ("text", b"Y"),
            ],
        )
        snapshot = self.terminal.snapshot()
        self.assertEqual(snapshot.lines[0][:2], "Xb")
        self.assertEqual(snapshot.lines[1][:2], " Y")

        self.assert_trace(
            b"\r\nZ",
            [("control", b"\r"), ("control", b"\n"), ("text", b"Z")],
        )
        self.assertEqual(self.terminal.snapshot().lines[2][0], "Z")

    def test_handler_osc_dispatches_icon_title_payload(self):
        self.assert_trace(OSC_HANDLER_INPUT, [("osc", b"1;foo=bar")])
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 1 666f6f3d626172"],
        )

        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(OSC_HANDLER_INPUT + b"\x1b[20t")
            self.assertEqual(terminal.read_input(), b"\x1b]Lfoo=bar\x1b\\")

    def test_handler_osc_prevent_fallback_maps_to_one_listener_dispatch(self):
        self.assert_trace(OSC_HANDLER_INPUT, [("osc", b"1;foo=bar")])
        self.assertEqual(self.terminal.read_actions(), ["OSC 1 666f6f3d626172"])

    def test_handler_osc_allow_fallback_maps_to_the_supported_icon_handler(self):
        self.terminal.write(OSC_HANDLER_INPUT)
        self.assertEqual(self.terminal.read_actions(), ["OSC 1 666f6f3d626172"])

    def test_handler_osc_multiple_fallback_dispatches_the_sequence_once(self):
        self.assert_trace(OSC_HANDLER_INPUT, [("osc", b"1;foo=bar")])
        self.assertEqual(len(self.terminal.read_actions()), 1)

    def test_handler_osc_multiple_no_fallback_maps_to_an_unknown_command(self):
        self.assert_trace(
            b"\x1b]999;foo=bar\x1b\\X",
            [("osc", b"999;foo=bar"), ("text", b"X")],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][0], "X")

    def test_handler_osc_latest_to_original_maps_to_wire_order(self):
        self.assert_trace(
            b"\x1b]1;one\x1b\\\x1b]1;two\x1b\\\x1b]1;three\x1b\\",
            [("osc", b"1;one"), ("osc", b"1;two"), ("osc", b"1;three")],
        )
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 1 6f6e65", "OSC 1 74776f", "OSC 1 7468726565"],
        )

    def test_handler_osc_dispose_keeps_standard_dispatch_available(self):
        self.terminal.write(b"\x1b]999;discarded\x1b\\" + OSC_HANDLER_INPUT)
        self.assertEqual(
            self.terminal.parser_trace(),
            [("osc", b"999;discarded"), ("osc", b"1;foo=bar")],
        )
        self.assertEqual(self.terminal.read_actions()[-1], "OSC 1 666f6f3d626172")

    def test_handler_osc_double_dispose_does_not_corrupt_standard_dispatch(self):
        self.terminal.write(
            b"\x1b]998;discarded\x1b\\\x1b]999;discarded\x1b\\"
            + OSC_HANDLER_INPUT
        )
        self.assertEqual(self.terminal.parser_trace()[-1], ("osc", b"1;foo=bar"))
        self.assertEqual(self.terminal.read_actions()[-1], "OSC 1 666f6f3d626172")

    def test_handler_dcs_streams_header_and_payload_across_writes(self):
        self.terminal.write(b"\x1bP1;2;3+pabc")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.assertEqual(self.terminal.read_input(), b"")
        self.terminal.write(b";de\x1b\\")
        self.assertEqual(
            self.terminal.parser_trace(),
            [("dcs", b"1;2;3+pabc;de")],
        )
        self.assertEqual(self.terminal.read_input(), b"")

    def test_handler_dcs_prevent_fallback_maps_to_one_unknown_dispatch(self):
        self.assert_trace(DCS_HANDLER_INPUT, [("dcs", b"1;2;3+pabc")])
        self.assertEqual(self.terminal.read_input(), b"")

    def test_handler_dcs_allow_fallback_maps_to_decrqss(self):
        self.assert_trace(DECRQSS_INPUT, [("dcs", b"$q\"p")])
        self.assertEqual(self.terminal.read_input(), DECRQSS_REPLY)

    def test_handler_dcs_multiple_fallback_dispatches_decrqss_once(self):
        self.assert_trace(DECRQSS_INPUT, [("dcs", b"$q\"p")])
        self.assertEqual(self.terminal.read_input(), DECRQSS_REPLY)

    def test_handler_dcs_multiple_no_fallback_maps_to_unknown_dcs(self):
        self.assert_trace(DCS_HANDLER_INPUT, [("dcs", b"1;2;3+pabc")])
        self.assertEqual(self.terminal.read_input(), b"")

    def test_handler_dcs_latest_to_original_maps_to_wire_order(self):
        self.assert_trace(
            b"\x1bP+pfirst\x1b\\\x1bP+psecond\x1b\\\x1bP+pthird\x1b\\",
            [("dcs", b"+pfirst"), ("dcs", b"+psecond"), ("dcs", b"+pthird")],
        )

    def test_handler_dcs_dispose_keeps_standard_dispatch_available(self):
        self.terminal.write(DCS_HANDLER_INPUT + DECRQSS_INPUT)
        self.assertEqual(
            self.terminal.parser_trace(),
            [("dcs", b"1;2;3+pabc"), ("dcs", b"$q\"p")],
        )
        self.assertEqual(self.terminal.read_input(), DECRQSS_REPLY)

    def test_handler_dcs_double_dispose_does_not_corrupt_standard_dispatch(self):
        self.terminal.write(DCS_HANDLER_INPUT + DCS_HANDLER_INPUT + DECRQSS_INPUT)
        self.assertEqual(self.terminal.parser_trace()[-1], ("dcs", b"$q\"p"))
        self.assertEqual(self.terminal.read_input(), DECRQSS_REPLY)

    def test_handler_apc_streams_payload_across_writes(self):
        self.terminal.write(b"\x1b_+pabc")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.terminal.write(b";de\x1b\\")
        self.assertEqual(self.terminal.parser_trace(), [("apc", b"+pabc;de")])

    def test_handler_apc_prevent_fallback_consumes_unknown_apc(self):
        self.assert_trace(
            APC_HANDLER_INPUT + b"X",
            [("apc", b"+pabc"), ("text", b"X")],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][0], "X")

    def test_handler_apc_allow_fallback_returns_to_ground(self):
        self.assert_trace(
            APC_HANDLER_INPUT + b"X",
            [("apc", b"+pabc"), ("text", b"X")],
        )

    def test_handler_apc_multiple_fallback_dispatches_fragmented_apc_once(self):
        self.terminal.write(b"\x1b_+p")
        self.terminal.write(b"abc")
        self.assertEqual(self.terminal.parser_trace(), [])
        self.terminal.write(b"\x1b\\")
        self.assertEqual(self.terminal.parser_trace(), [("apc", b"+pabc")])

    def test_handler_apc_multiple_no_fallback_has_no_terminal_effect(self):
        before = self.terminal.snapshot()
        self.assert_trace(APC_HANDLER_INPUT, [("apc", b"+pabc")])
        after = self.terminal.snapshot()
        self.assertEqual(after.lines, before.lines)
        self.assertEqual(
            (after.cursor_x, after.cursor_y),
            (before.cursor_x, before.cursor_y),
        )

    def test_handler_apc_latest_to_original_maps_to_wire_order(self):
        self.assert_trace(
            b"\x1b_+pfirst\x1b\\\x1b_+psecond\x1b\\\x1b_+pthird\x1b\\",
            [("apc", b"+pfirst"), ("apc", b"+psecond"), ("apc", b"+pthird")],
        )

    def test_handler_apc_dispose_keeps_following_dispatch_available(self):
        self.assert_trace(
            APC_HANDLER_INPUT + OSC_HANDLER_INPUT,
            [("apc", b"+pabc"), ("osc", b"1;foo=bar")],
        )
        self.assertEqual(self.terminal.read_actions()[-1], "OSC 1 666f6f3d626172")

    def test_handler_apc_double_dispose_does_not_corrupt_following_dispatch(self):
        self.assert_trace(
            APC_HANDLER_INPUT + APC_HANDLER_INPUT + OSC_HANDLER_INPUT,
            [("apc", b"+pabc"), ("apc", b"+pabc"), ("osc", b"1;foo=bar")],
        )
        self.assertEqual(self.terminal.read_actions()[-1], "OSC 1 666f6f3d626172")

    def test_constructor_installs_the_complete_public_transition_machine(self):
        # The source case compares a private transition-table object.  A fresh
        # terminal instead proves that every public transition family is
        # installed and reachable without any test-only parser injection.
        self.assert_trace(ASYNC_HANDLER_INPUT, ASYNC_HANDLER_TRACE)

    def test_initial_state_is_ground_with_empty_sequence_accumulators(self):
        self.assert_trace(
            b"A\x1b[31mB\x1b]1;fresh\x1b\\C",
            [
                ("text", b"A"),
                ("csi", b"31m"),
                ("text", b"B"),
                ("osc", b"1;fresh"),
                ("text", b"C"),
            ],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][:3], "ABC")

    def test_reset_clears_every_partial_parser_state(self):
        prefixes = (
            b"\x1b!",
            b"\x1b[1;2",
            b"\x1b]1;stale",
            b"\x1bP1;2astale",
            b"\x1b_Xstale",
        )
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                self.terminal.write(prefix)
                self.terminal.hard_reset()
                self.assert_trace(b"XY", [("text", b"XY")])
                self.assertEqual(self.terminal.snapshot().lines[0][:2], "XY")

    def test_error_handler_case_uses_the_public_unicode_recovery_policy(self):
        # xterm.js exposes the exact private error-state record.  The public
        # operation is recovery: Shitty drops the invalid CSI codepoint,
        # returns to ground immediately, and processes the remaining bytes.
        self.assert_trace(
            b"\x1b[1;2;\xe2\x82\xac;3mX",
            [("text", b";3mX")],
        )
        self.assertEqual(self.terminal.snapshot().lines[0][:4], ";3mX")
        self.assertEqual(self.terminal.read_actions(), [])

    def test_identifier_prefix_range_is_one_private_parameter_byte(self):
        payload = bytearray()
        expected = []
        for prefix in range(0x3C, 0x40):
            value = bytes((prefix,))
            payload += b"\x1b[" + value + b"1z"
            expected.append(("csi", value + b"1z"))
            payload += b"\x1bP" + value + b"1zA\x1b\\"
            expected.append(("dcs", value + b"1zA"))
        self.assert_trace(bytes(payload), expected)

    def test_identifier_intermediate_range_accepts_two_bytes(self):
        payload = bytearray()
        expected = []
        for intermediate in range(0x20, 0x30):
            value = bytes((intermediate, intermediate))
            payload += b"\x1b[1" + value + b"z"
            expected.append(("csi", b"1" + value + b"z"))
            payload += b"\x1bP1" + value + b"zA\x1b\\"
            expected.append(("dcs", b"1" + value + b"zA"))
        # The source's two-byte ceiling belongs to its packed callback key,
        # not to ECMA-48.  Keep Shitty's supported three- and four-byte wire
        # identifiers executable instead of copying that private limit.
        payload += b"\x1b[1!!!z\x1bP1!!!!zA\x1b\\"
        expected.extend((("csi", b"1!!!z"), ("dcs", b"1!!!!zA")))
        self.assert_trace(bytes(payload), expected)

    def test_identifier_csi_and_dcs_final_range_is_complete(self):
        payload = bytearray()
        expected = []
        for final in range(0x40, 0x7F):
            value = bytes((final,))
            payload += b"\x1b[!" + value
            expected.append(("csi", b"!" + value))
            payload += b"\x1bP!" + value + b"\x1b\\"
            expected.append(("dcs", b"!" + value))
        self.assert_trace(bytes(payload), expected)

    def test_identifier_escape_and_apc_final_ranges_follow_the_wire_grammars(self):
        payload = bytearray()
        expected = []
        for final in range(0x30, 0x7F):
            value = bytes((final,))
            # An intermediate makes introducer-looking finals such as '[' a
            # regular ESC sequence final on the wire.
            payload += b"\x1b!" + value
            expected.append(("escape", b"!" + value))
            payload += b"\x1b_" + value + b"AB\x1b\\"
            expected.append(("apc", value + b"AB"))
        # xterm.js rejects '/' as an APC callback identifier.  ECMA-48 APC is
        # one command string, so '/' is valid data while DEL is ignored.
        payload += b"\x1b_/AB\x1b\\\x1b_\x7fAB\x1b\\"
        expected.extend((("apc", b"/AB"), ("apc", b"AB")))
        self.assert_trace(bytes(payload), expected)

    def test_identifier_order_is_prefix_then_intermediates_then_final(self):
        self.assert_trace(
            b"\x1b[?1!!z\x1bP?1!!zAB\x1b\\",
            [("csi", b"?1!!z"), ("dcs", b"?1!!zAB")],
        )

    def test_identifier_invocation_distinguishes_escape_ids(self):
        sequence = b"\x1bz\x1b!z\x1b!!z"
        expected = [("escape", b"z"), ("escape", b"!z"), ("escape", b"!!z")]
        self.assert_trace(sequence, expected)

    def test_identifier_invocation_distinguishes_csi_ids(self):
        sequence = (
            b"\x1b[1;z\x1b[1;!z\x1b[1;!!z"
            b"\x1b[?1;z\x1b[?1;!z\x1b[?1;!!z"
        )
        self.assert_trace(
            sequence,
            [
                ("csi", b"1;0z"),
                ("csi", b"1;0!z"),
                ("csi", b"1;0!!z"),
                ("csi", b"?1;0z"),
                ("csi", b"?1;0!z"),
                ("csi", b"?1;0!!z"),
            ],
        )

    def test_identifier_invocation_distinguishes_dcs_ids(self):
        sequence = (
            b"\x1bP1;zAB\x1b\\\x1bP1;!zAB\x1b\\\x1bP1;!!zAB\x1b\\"
            b"\x1bP?1;zAB\x1b\\\x1bP?1;!zAB\x1b\\\x1bP?1;!!zAB\x1b\\"
        )
        self.assert_trace(
            sequence,
            [
                ("dcs", b"1;zAB"),
                ("dcs", b"1;!zAB"),
                ("dcs", b"1;!!zAB"),
                ("dcs", b"?1;zAB"),
                ("dcs", b"?1;!zAB"),
                ("dcs", b"?1;!!zAB"),
            ],
        )

    def test_identifier_invocation_distinguishes_apc_ids(self):
        self.assert_trace(
            b"\x1b_zAB\x1b\\\x1b_!zAB\x1b\\\x1b_!!zAB\x1b\\",
            [("apc", b"zAB"), ("apc", b"!zAB"), ("apc", b"!!zAB")],
        )

    # The eight audited terminal parsers dispatch synchronously and expose no
    # Promise-returning handler stack.  The following fourteen source cases
    # therefore retain their distinct public stream/reset/order postconditions
    # without inventing an async callback API in Shitty.

    def test_sync_handlers_keep_parsing_the_complete_stream_without_a_pause(self):
        self.assert_trace(ASYNC_HANDLER_INPUT, ASYNC_HANDLER_TRACE)

    def test_sync_parse_call_has_the_complete_ordered_public_result(self):
        self.assert_trace(ASYNC_HANDLER_INPUT, ASYNC_HANDLER_TRACE)
        snapshot = self.terminal.model_snapshot()
        self.assertTrue(snapshot.cell(0, 0).bold)
        self.assertEqual(snapshot.cell(0, 0).foreground_index, 1)
        self.assertEqual(snapshot.lines[2][:5], "$>FIN")

    def test_async_source_call_maps_to_chunk_safe_public_parsing(self):
        chunks = (
            b"\x1b[1;31mhello ",
            b"\x1b%Gwor\x1bEld!",
            b"\x1b[0m\r\n$>",
            b"\x1bP1;2axyz\x1b\\",
            b"\x1b]1;foo=bar\x1b\\",
            b"\x1b_Xabc\x1b\\FIN",
        )
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write_chunks(*chunks)
        self.assertEqual(self.terminal.parser_trace(), ASYNC_HANDLER_TRACE)

    def test_async_private_handlers_cannot_disable_public_sync_streaming(self):
        self.terminal.parser_trace_clear()
        self.terminal.write(ASYNC_HANDLER_INPUT)
        self.terminal.write(ASYNC_HANDLER_INPUT)
        self.assertEqual(self.terminal.parser_trace(), ASYNC_HANDLER_TRACE * 2)

    def test_arbitrary_public_continuation_never_poison_the_parser(self):
        chunks = (
            b"\x1b[1;",
            b"31mhello \x1b%",
            b"Gwor\x1b",
            b"Eld!\x1b[0",
            b"m\r\n$>\x1bP1;",
            b"2axyz\x1b",
            b"\\\x1b]1;foo",
            b"=bar\x1b\\\x1b_Xa",
            b"bc\x1b\\FIN",
        )
        self.terminal.parser_trace_clear()
        self.terminal.write_chunks(*chunks)
        self.assertEqual(self.terminal.parser_trace(), ASYNC_HANDLER_TRACE)

    def test_reset_after_dispatch_continues_with_the_next_public_codepoint(self):
        self.terminal.write(b"\x1b[1m")
        self.terminal.hard_reset()
        self.assert_trace(b"XY", [("text", b"XY")])
        self.assertEqual(self.terminal.snapshot().lines[0][:2], "XY")

    def test_awaited_source_call_maps_to_logically_chunked_public_input(self):
        chunks = (
            b"\x1b[1;31m",
            b"hello ",
            b"\x1b%G",
            b"wor",
            b"\x1bE",
            b"ld!",
            b"\x1b[0m",
            b"\r",
            b"\n",
            b"$>",
            b"\x1bP1;2axyz\x1b\\",
            b"\x1b]1;foo=bar\x1b\\",
            b"\x1b_Xabc\x1b\\",
            b"FIN",
        )
        self.terminal.parser_trace_clear()
        self.terminal.write_chunks(*chunks)
        self.assertEqual(self.terminal.parser_trace(), ASYNC_HANDLER_TRACE)

    def test_chunked_awaited_source_call_survives_single_byte_writes(self):
        self.terminal.parser_trace_clear()
        self.terminal.write_chunks(*(bytes((byte,)) for byte in ASYNC_HANDLER_INPUT))
        self.assertEqual(self.terminal.parser_trace(), ASYNC_HANDLER_TRACE)

    def test_multiple_async_sgr_source_handlers_preserve_sgr_order(self):
        self.assert_trace(
            b"\x1b[1;31mA\x1b[4;32mB\x1b[0mC",
            [
                ("csi", b"1;31m"),
                ("text", b"A"),
                ("csi", b"4;32m"),
                ("text", b"B"),
                ("csi", b"0m"),
                ("text", b"C"),
            ],
        )
        snapshot = self.terminal.model_snapshot()
        self.assertTrue(snapshot.cell(0, 0).bold)
        self.assertEqual(snapshot.cell(0, 0).foreground_index, 1)
        self.assertTrue(snapshot.cell(1, 0).underline)
        self.assertEqual(snapshot.cell(1, 0).foreground_index, 2)
        self.assertFalse(snapshot.cell(2, 0).bold)
        self.assertFalse(snapshot.cell(2, 0).underline)

    def test_multiple_async_escape_source_handlers_preserve_escape_order(self):
        self.assert_trace(
            b"A\x1b%GB\x1bEC\x1bED",
            [
                ("text", b"A"),
                ("escape", b"%G"),
                ("text", b"B"),
                ("escape", b"E"),
                ("text", b"C"),
                ("escape", b"E"),
                ("text", b"D"),
            ],
        )
        snapshot = self.terminal.snapshot()
        self.assertEqual(snapshot.lines[0][:2], "AB")
        self.assertEqual(snapshot.lines[1][0], "C")
        self.assertEqual(snapshot.lines[2][0], "D")

    def test_mixed_sync_async_sgr_source_handlers_share_one_wire_order(self):
        self.assert_trace(
            b"\x1b[31mA\x1b[1mB\x1b[39mC\x1b[22mD",
            [
                ("csi", b"31m"),
                ("text", b"A"),
                ("csi", b"1m"),
                ("text", b"B"),
                ("csi", b"39m"),
                ("text", b"C"),
                ("csi", b"22m"),
                ("text", b"D"),
            ],
        )
        snapshot = self.terminal.model_snapshot()
        self.assertEqual(snapshot.cell(0, 0).foreground_index, 1)
        self.assertFalse(snapshot.cell(0, 0).bold)
        self.assertEqual(snapshot.cell(1, 0).foreground_index, 1)
        self.assertTrue(snapshot.cell(1, 0).bold)
        self.assertEqual(snapshot.cell(2, 0).foreground_index, -2)
        self.assertTrue(snapshot.cell(2, 0).bold)
        self.assertFalse(snapshot.cell(3, 0).bold)

    def test_multiple_async_osc_source_handlers_dispatch_each_string_once(self):
        self.assert_trace(
            b"\x1b]1;one\x1b\\\x1b]1;two\x1b\\",
            [("osc", b"1;one"), ("osc", b"1;two")],
        )
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 1 6f6e65", "OSC 1 74776f"],
        )

    def test_multiple_async_dcs_source_handlers_dispatch_each_string_once(self):
        self.assert_trace(
            b"\x1bP1;2aone\x1b\\\x1bP3;4atwo\x1b\\",
            [("dcs", b"1;2aone"), ("dcs", b"3;4atwo")],
        )
        self.assertEqual(self.terminal.read_input(), b"")

    def test_multiple_async_apc_source_handlers_dispatch_each_string_once(self):
        self.assert_trace(
            b"\x1b_Xone\x1b\\\x1b_Xtwo\x1b\\",
            [("apc", b"Xone"), ("apc", b"Xtwo")],
        )


if __name__ == "__main__":
    unittest.main()

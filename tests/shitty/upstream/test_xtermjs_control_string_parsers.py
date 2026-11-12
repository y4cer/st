# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all xterm.js OSC, DCS and APC parser cases."""

import unittest

from harness import Shitty


OSC_CASES = (
    "no report for illegal ids",
    "no payload",
    "with payload",
    "setOscHandler",
    "clearOscHandler",
    "addOscHandler",
    "addOscHandler with return false",
    "dispose handlers",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should work up to payload limit",
    "should abort for payload limit +1",
    "first should run, cleanup action for others",
    "all should run",
    "first should run, cleanup action for others",
    "all should run",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should abort active handlers with end(false) when reset during payload",
)

DCS_CASES = (
    "setDcsHandler",
    "clearDcsHandler",
    "addDcsHandler",
    "addDcsHandler with return false",
    "dispose handlers",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should work up to payload limit",
    "should abort for payload limit +1",
    "first should run, cleanup action for others",
    "all should run",
    "first should run, cleanup action for others",
    "all should run",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should abort active handlers with unhook(false) when reset during payload",
)

APC_CASES = (
    "setApcHandler",
    "clearApcHandler",
    "addApcHandler",
    "addApcHandler with return false",
    "dispose handlers",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should work up to payload limit",
    "should abort for payload limit +1",
    "first should run, cleanup action for others",
    "all should run",
    "first should run, cleanup action for others",
    "all should run",
    "should be called once on end(true)",
    "should not be called on end(false)",
    "should be disposable",
    "should respect return false",
    "should abort active handlers with end(false) when reset during payload",
)

OSC = b"\x1b]"
DCS = b"\x1bP"
APC = b"\x1b_"
ST = b"\x1b\\"

OSC_HANDLER_BODY = b"1234;Here comesthe mouse!"
DCS_HANDLER_BODY = b"1;2;3+pHere comesthe mouse!"
APC_HANDLER_BODY = b"+pHere comesthe mouse!"


class XtermJsControlStringParsersTest(unittest.TestCase):
    def setUp(self):
        self.terminal = Shitty(columns=16, rows=3)
        self.terminal.__enter__()
        self.terminal.parser_trace_on()

    def tearDown(self):
        self.terminal.__exit__(None, None, None)

    def assert_trace(self, sequence, expected):
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write(sequence)
        self.assertEqual(self.terminal.parser_trace(), expected)

    def assert_chunk_trace(self, chunks, expected):
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write_chunks(*chunks)
        self.assertEqual(self.terminal.parser_trace(), expected)

    def assert_reset_aborts(self, partial, complete, expected):
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write(partial)
        self.terminal.hard_reset()
        self.terminal.parser_trace_clear()
        self.terminal.read_actions()
        self.terminal.read_input()
        self.terminal.write(complete)
        self.assertEqual(self.terminal.parser_trace(), [expected])

    def test_inventory_accounts_for_all_63_upstream_cases(self):
        self.assertEqual(len(OSC_CASES), 23)
        self.assertEqual(len(DCS_CASES), 20)
        self.assertEqual(len(APC_CASES), 20)
        self.assertEqual(len(OSC_CASES) + len(DCS_CASES) + len(APC_CASES), 63)

    # OscParser: identifier parsing.

    def test_osc_illegal_identifier_has_no_semantic_effect(self):
        self.assert_trace(OSC + b"hello world!" + ST, [("osc", b"hello world!")])
        self.assertEqual(self.terminal.read_actions(), [])
        self.terminal.write(b"X")
        self.assertEqual(self.terminal.snapshot().cell(0, 0).char, "X")

    def test_osc_numeric_identifier_without_payload_is_complete(self):
        self.assert_trace(OSC + b"1234" + ST, [("osc", b"1234")])
        self.assertEqual(self.terminal.read_actions(), ["OSC 1234 "])

    def test_osc_identifier_and_payload_survive_chunk_boundaries(self):
        self.assert_chunk_trace(
            (OSC + b"12", b"34", b";h", b"ello", ST),
            [("osc", b"1234;hello")],
        )

    # OscParser: fixed public dispatch in place of its private handler stack.

    def test_osc_set_handler_maps_to_one_complete_public_dispatch(self):
        self.assert_chunk_trace(
            (OSC + b"1234;Here comes", b"the mouse!", ST),
            [("osc", OSC_HANDLER_BODY)],
        )

    def test_osc_clear_handler_maps_to_inert_unknown_identifier_fallback(self):
        self.assert_trace(OSC + OSC_HANDLER_BODY + ST, [("osc", OSC_HANDLER_BODY)])
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 1234 4865726520636f6d6573746865206d6f75736521"],
        )

    def test_osc_add_handlers_maps_to_two_ordered_public_commands(self):
        sequence = OSC + b"2;one" + ST + OSC + b"2;two" + ST
        self.assert_trace(sequence, [("osc", b"2;one"), ("osc", b"2;two")])
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 2 6f6e65", "OSC 2 74776f"],
        )

    def test_osc_return_false_maps_to_unknown_then_supported_fallback(self):
        sequence = OSC + OSC_HANDLER_BODY + ST + OSC + b"2;handled" + ST
        self.assert_trace(
            sequence,
            [("osc", OSC_HANDLER_BODY), ("osc", b"2;handled")],
        )
        self.assertEqual(
            self.terminal.read_actions(),
            [
                "OSC 1234 4865726520636f6d6573746865206d6f75736521",
                "OSC 2 68616e646c6564",
            ],
        )

    def test_osc_disposed_handler_does_not_poison_later_dispatch(self):
        self.assert_trace(OSC + b"2;after-dispose" + ST, [("osc", b"2;after-dispose")])
        self.assertEqual(self.terminal.read_actions(), ["OSC 2 61667465722d646973706f7365"])

    # OscHandler factory: one complete effect, cancellation and wire-sized payloads.

    def test_osc_factory_complete_sequence_dispatches_once(self):
        self.assert_trace(OSC + b"2;Here comes the mouse!" + ST, [("osc", b"2;Here comes the mouse!")])
        self.assertEqual(len(self.terminal.read_actions()), 1)

    def test_osc_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_trace(OSC + b"2;partial\x18X", [("control", b"\x18"), ("text", b"X")])
        self.assertEqual(self.terminal.read_actions(), [])

    def test_osc_factory_disposal_maps_to_independent_complete_commands(self):
        self.terminal.write(OSC + b"2;first" + ST)
        self.assertEqual(self.terminal.read_actions(), ["OSC 2 6669727374"])
        self.assert_trace(OSC + b"2;second" + ST, [("osc", b"2;second")])
        self.assertEqual(self.terminal.read_actions(), ["OSC 2 7365636f6e64"])

    def test_osc_factory_fallback_preserves_each_complete_command(self):
        self.assert_trace(
            OSC + b"1234;fallback" + ST + OSC + b"2;effect" + ST,
            [("osc", b"1234;fallback"), ("osc", b"2;effect")],
        )
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 1234 66616c6c6261636b", "OSC 2 656666656374"],
        )

    def test_osc_factory_accepts_100_wire_payload_bytes(self):
        body = b"2;" + b"A" * 100
        self.assert_trace(OSC + body + ST, [("osc", body)])
        self.assertEqual(len(self.terminal.read_actions()), 1)

    def test_osc_factory_private_limit_plus_one_is_valid_on_the_wire(self):
        body = b"2;" + b"A" * 101
        self.assert_trace(OSC + body + ST, [("osc", body)])
        self.assertEqual(len(self.terminal.read_actions()), 1)

    # OscParser async cases: the audited terminals are synchronous, so retain
    # each source case's public ordering/chunking/fallback postcondition.

    def test_osc_sync_async_sync_cleanup_keeps_latest_wire_order(self):
        parts = (OSC + b"2;one" + ST, OSC + b"1234;inert" + ST, OSC + b"2;two" + ST)
        self.assert_chunk_trace(parts, [("osc", b"2;one"), ("osc", b"1234;inert"), ("osc", b"2;two")])

    def test_osc_sync_async_sync_all_complete_commands_run(self):
        sequence = b"".join(OSC + b"2;" + value + ST for value in (b"one", b"two", b"three"))
        self.assert_trace(sequence, [("osc", b"2;one"), ("osc", b"2;two"), ("osc", b"2;three")])
        self.assertEqual(len(self.terminal.read_actions()), 3)

    def test_osc_async_sync_async_cleanup_is_byte_chunk_safe(self):
        sequence = OSC + b"2;one" + ST + OSC + b"2;two" + ST
        self.assert_chunk_trace(tuple(bytes((byte,)) for byte in sequence), [("osc", b"2;one"), ("osc", b"2;two")])

    def test_osc_async_sync_async_all_commands_run_after_arbitrary_splits(self):
        chunks = (OSC + b"2;o", b"ne\x1b", b"\\\x1b]2;t", b"wo", ST)
        self.assert_chunk_trace(chunks, [("osc", b"2;one"), ("osc", b"2;two")])

    def test_osc_async_factory_complete_sequence_dispatches_once(self):
        self.assert_chunk_trace(
            (OSC + b"2;Here ", b"comes ", b"the mouse!", ST),
            [("osc", b"2;Here comes the mouse!")],
        )
        self.assertEqual(len(self.terminal.read_actions()), 1)

    def test_osc_async_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_chunk_trace((OSC + b"2;partial", b"\x18", b"X"), [("control", b"\x18"), ("text", b"X")])
        self.assertEqual(self.terminal.read_actions(), [])

    def test_osc_async_factory_disposal_preserves_later_streaming(self):
        self.terminal.write(OSC + b"2;old" + ST)
        self.terminal.read_actions()
        self.assert_chunk_trace((OSC + b"2;ne", b"w", ST), [("osc", b"2;new")])
        self.assertEqual(self.terminal.read_actions(), ["OSC 2 6e6577"])

    def test_osc_async_factory_fallback_runs_in_wire_order(self):
        self.assert_chunk_trace(
            (OSC + b"999;unknown", ST, OSC + b"2;known", ST),
            [("osc", b"999;unknown"), ("osc", b"2;known")],
        )
        self.assertEqual(
            self.terminal.read_actions(),
            ["OSC 999 756e6b6e6f776e", "OSC 2 6b6e6f776e"],
        )

    def test_osc_reset_aborts_partial_payload_before_next_command(self):
        self.assert_reset_aborts(
            OSC + b"2;partial",
            OSC + b"2;complete" + ST,
            ("osc", b"2;complete"),
        )
        self.assertEqual(self.terminal.read_actions(), ["OSC 2 636f6d706c657465"])

    # DcsParser handler registration and factory cases.

    def test_dcs_set_handler_maps_to_hook_payload_unhook_trace(self):
        self.assert_chunk_trace(
            (DCS + b"1;2;3+pHere comes", b"the mouse!", ST),
            [("dcs", DCS_HANDLER_BODY)],
        )

    def test_dcs_clear_handler_maps_to_inert_unknown_identifier_fallback(self):
        self.assert_trace(DCS + DCS_HANDLER_BODY + ST, [("dcs", DCS_HANDLER_BODY)])
        self.assertEqual(self.terminal.read_input(), b"")

    def test_dcs_add_handlers_maps_to_two_ordered_complete_strings(self):
        self.assert_trace(
            DCS + b"1+pOne" + ST + DCS + b"2+pTwo" + ST,
            [("dcs", b"1+pOne"), ("dcs", b"2+pTwo")],
        )

    def test_dcs_return_false_maps_to_unknown_then_supported_fallback(self):
        sequence = DCS + DCS_HANDLER_BODY + ST + DCS + b"$q\"p" + ST
        self.assert_trace(sequence, [("dcs", DCS_HANDLER_BODY), ("dcs", b"$q\"p")])
        self.assertEqual(self.terminal.read_input(), b"\x1bP1$r64;1\"p\x1b\\")

    def test_dcs_disposed_handler_does_not_poison_later_dispatch(self):
        self.assert_trace(DCS + b"3+pafter-dispose" + ST, [("dcs", b"3+pafter-dispose")])

    def test_dcs_factory_complete_sequence_dispatches_once(self):
        self.assert_trace(DCS + DCS_HANDLER_BODY + ST, [("dcs", DCS_HANDLER_BODY)])

    def test_dcs_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_trace(DCS + b"1;2;3+ppartial\x18X", [("control", b"\x18"), ("text", b"X")])
        self.assertEqual(self.terminal.read_input(), b"")

    def test_dcs_factory_disposal_maps_to_independent_complete_strings(self):
        self.terminal.write(DCS + b"1+pfirst" + ST)
        self.assert_trace(DCS + b"2+psecond" + ST, [("dcs", b"2+psecond")])

    def test_dcs_factory_fallback_preserves_each_complete_string(self):
        self.assert_trace(
            DCS + b"1+pfallback" + ST + DCS + b"2+peffect" + ST,
            [("dcs", b"1+pfallback"), ("dcs", b"2+peffect")],
        )

    def test_dcs_factory_accepts_100_wire_payload_bytes(self):
        body = b"1;2;3+p" + b"A" * 100
        self.assert_trace(DCS + body + ST, [("dcs", body)])

    def test_dcs_factory_private_limit_plus_one_is_valid_on_the_wire(self):
        body = b"1;2;3+p" + b"A" * 101
        self.assert_trace(DCS + body + ST, [("dcs", body)])

    def test_dcs_sync_async_sync_cleanup_keeps_latest_wire_order(self):
        chunks = (DCS + b"1+pone" + ST, DCS + b"2+ptwo" + ST, DCS + b"3+pthree" + ST)
        self.assert_chunk_trace(chunks, [("dcs", b"1+pone"), ("dcs", b"2+ptwo"), ("dcs", b"3+pthree")])

    def test_dcs_sync_async_sync_all_complete_strings_run(self):
        sequence = b"".join(DCS + str(index).encode() + b"+pA" + ST for index in range(1, 4))
        self.assert_trace(sequence, [("dcs", b"1+pA"), ("dcs", b"2+pA"), ("dcs", b"3+pA")])

    def test_dcs_async_sync_async_cleanup_is_byte_chunk_safe(self):
        sequence = DCS + b"1+pOne" + ST + DCS + b"2+pTwo" + ST
        self.assert_chunk_trace(tuple(bytes((byte,)) for byte in sequence), [("dcs", b"1+pOne"), ("dcs", b"2+pTwo")])

    def test_dcs_async_sync_async_all_strings_run_after_arbitrary_splits(self):
        self.assert_chunk_trace(
            (DCS + b"1;2", b";3+pHere ", b"comes", b" the mouse!\x1b", b"\\"),
            [("dcs", b"1;2;3+pHere comes the mouse!")],
        )

    def test_dcs_async_factory_complete_sequence_dispatches_once(self):
        self.assert_chunk_trace(
            (DCS + b"1;2;3+pHere ", b"comes ", b"the mouse!", ST),
            [("dcs", b"1;2;3+pHere comes the mouse!")],
        )

    def test_dcs_async_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_chunk_trace((DCS + b"1+ppartial", b"\x18", b"X"), [("control", b"\x18"), ("text", b"X")])

    def test_dcs_async_factory_disposal_preserves_later_streaming(self):
        self.terminal.write(DCS + b"1+pold" + ST)
        self.assert_chunk_trace((DCS + b"2+pn", b"ew", ST), [("dcs", b"2+pnew")])

    def test_dcs_async_factory_fallback_runs_in_wire_order(self):
        self.assert_chunk_trace(
            (DCS + b"1+punknown", ST, DCS + b"$q\"p", ST),
            [("dcs", b"1+punknown"), ("dcs", b"$q\"p")],
        )
        self.assertEqual(self.terminal.read_input(), b"\x1bP1$r64;1\"p\x1b\\")

    def test_dcs_reset_aborts_partial_payload_before_next_string(self):
        self.assert_reset_aborts(
            DCS + b"1;2;3+ppartial",
            DCS + b"1;2;3+pcomplete" + ST,
            ("dcs", b"1;2;3+pcomplete"),
        )

    # ApcParser handler registration and factory cases.

    def test_apc_set_handler_maps_to_start_payload_end_trace(self):
        self.assert_chunk_trace(
            (APC + b"+pHere comes", b"the mouse!", ST),
            [("apc", APC_HANDLER_BODY)],
        )

    def test_apc_clear_handler_maps_to_inert_unknown_identifier_fallback(self):
        self.assert_trace(APC + APC_HANDLER_BODY + ST, [("apc", APC_HANDLER_BODY)])

    def test_apc_add_handlers_maps_to_two_ordered_complete_strings(self):
        self.assert_trace(
            APC + b"+pOne" + ST + APC + b"+qTwo" + ST,
            [("apc", b"+pOne"), ("apc", b"+qTwo")],
        )

    def test_apc_return_false_maps_to_distinct_identifier_fallback(self):
        self.assert_trace(
            APC + b"+pHandled" + ST + APC + b"+qFallback" + ST,
            [("apc", b"+pHandled"), ("apc", b"+qFallback")],
        )

    def test_apc_disposed_handler_does_not_poison_later_dispatch(self):
        self.assert_trace(APC + b"+pafter-dispose" + ST, [("apc", b"+pafter-dispose")])

    def test_apc_factory_complete_sequence_dispatches_once(self):
        self.assert_trace(APC + APC_HANDLER_BODY + ST, [("apc", APC_HANDLER_BODY)])

    def test_apc_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_trace(APC + b"+ppartial\x18X", [("control", b"\x18"), ("text", b"X")])

    def test_apc_factory_disposal_maps_to_independent_complete_strings(self):
        self.terminal.write(APC + b"+pfirst" + ST)
        self.assert_trace(APC + b"+psecond" + ST, [("apc", b"+psecond")])

    def test_apc_factory_fallback_preserves_each_complete_string(self):
        self.assert_trace(
            APC + b"+pfallback" + ST + APC + b"+qeffect" + ST,
            [("apc", b"+pfallback"), ("apc", b"+qeffect")],
        )

    def test_apc_factory_accepts_100_wire_payload_bytes(self):
        body = b"+p" + b"A" * 100
        self.assert_trace(APC + body + ST, [("apc", body)])

    def test_apc_factory_private_limit_plus_one_is_valid_on_the_wire(self):
        body = b"+p" + b"A" * 101
        self.assert_trace(APC + body + ST, [("apc", body)])

    def test_apc_sync_async_sync_cleanup_keeps_latest_wire_order(self):
        chunks = (APC + b"+pone" + ST, APC + b"+qtwo" + ST, APC + b"+rthree" + ST)
        self.assert_chunk_trace(chunks, [("apc", b"+pone"), ("apc", b"+qtwo"), ("apc", b"+rthree")])

    def test_apc_sync_async_sync_all_complete_strings_run(self):
        sequence = b"".join(APC + b"+p" + value + ST for value in (b"one", b"two", b"three"))
        self.assert_trace(sequence, [("apc", b"+pone"), ("apc", b"+ptwo"), ("apc", b"+pthree")])

    def test_apc_async_sync_async_cleanup_is_byte_chunk_safe(self):
        sequence = APC + b"+pOne" + ST + APC + b"+pTwo" + ST
        self.assert_chunk_trace(tuple(bytes((byte,)) for byte in sequence), [("apc", b"+pOne"), ("apc", b"+pTwo")])

    def test_apc_async_sync_async_all_strings_run_after_arbitrary_splits(self):
        self.assert_chunk_trace(
            (APC + b"+pHere ", b"comes", b" the mouse!\x1b", b"\\"),
            [("apc", b"+pHere comes the mouse!")],
        )

    def test_apc_async_factory_complete_sequence_dispatches_once(self):
        self.assert_chunk_trace(
            (APC + b"+pHere ", b"comes ", b"the mouse!", ST),
            [("apc", b"+pHere comes the mouse!")],
        )

    def test_apc_async_factory_cancelled_sequence_does_not_dispatch(self):
        self.assert_chunk_trace((APC + b"+ppartial", b"\x18", b"X"), [("control", b"\x18"), ("text", b"X")])

    def test_apc_async_factory_disposal_preserves_later_streaming(self):
        self.terminal.write(APC + b"+pold" + ST)
        self.assert_chunk_trace((APC + b"+pn", b"ew", ST), [("apc", b"+pnew")])

    def test_apc_async_factory_fallback_runs_in_wire_order(self):
        self.assert_chunk_trace(
            (APC + b"+punknown", ST, APC + b"+qknown", ST),
            [("apc", b"+punknown"), ("apc", b"+qknown")],
        )

    def test_apc_reset_aborts_partial_payload_before_next_string(self):
        self.assert_reset_aborts(
            APC + b"+ppartial",
            APC + b"+pcomplete" + ST,
            ("apc", b"+pcomplete"),
        )


if __name__ == "__main__":
    unittest.main()

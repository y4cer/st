# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def outcome(terminal):
    snapshot = terminal.snapshot()
    cells = tuple(
        (
            cell.char,
            cell.bold,
            cell.italic,
            cell.underline,
            cell.foreground,
            cell.background,
            cell.protected,
        )
        for cell in snapshot.cells
    )
    return (
        snapshot.cursor_x,
        snapshot.cursor_y,
        cells,
        terminal.read_input(),
        tuple(terminal.read_actions()),
    )


class ParserStateMachineTest(unittest.TestCase):
    def assert_chunkings_equal(self, payload):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(payload)
            expected = outcome(terminal)

        chunkings = [
            (payload[:split], payload[split:])
            for split in range(1, len(payload))
        ]
        chunkings.append(tuple(bytes((byte,)) for byte in payload))
        for chunks in chunkings:
            with self.subTest(chunks=chunks):
                with Shitty(columns=8, rows=3) as terminal:
                    terminal.write_chunks(*chunks)
                    self.assertEqual(outcome(terminal), expected)

    def test_del_is_ignored_in_ground_state(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x7fB")
            self.assertEqual(terminal.snapshot().lines[0], "AB      ")

    def test_del_is_ignored_in_escape_state(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b\x7f[2;3HX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(2, 1).char, "X")
            self.assertEqual(snapshot.lines[0], "        ")

    def test_del_is_ignored_in_csi_state(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2\x7f;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_del_is_not_part_of_osc_payload(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]2;a\x7fb\x1b\\")
            self.assertEqual(terminal.read_actions(), ["OSC 2 6162"])

    def test_nul_is_inert_dcs_payload_but_not_part_of_osc_payload(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1bP$q\x00m\x1b\\"
                b"\x1b]2;a\x00b\x1b\\"
            )
            self.assertIn(b"\x1bP1$r0", terminal.read_input())
            self.assertEqual(terminal.read_actions(), ["OSC 2 6162"])

    def test_bell_is_inert_inside_dcs_but_terminates_osc(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1bP$q\am\x1b\\"
                b"\x1b]2;title\aX"
            )
            self.assertIn(b"\x1bP1$r0", terminal.read_input())
            self.assertEqual(
                terminal.read_actions(),
                ["OSC 2 7469746c65"],
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_c0_is_inert_inside_ignored_string(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"A\x1b_ignored\nmore\x1b\\B")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(1, 0).char, "B")

    def test_nul_is_ignored_without_cancelling_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2\x00;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_bell_executes_without_cancelling_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2\a;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")
            self.assertEqual(terminal.read_actions(), ["BELL"])

    def test_linefeed_executes_without_cancelling_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"A\x1b[2\n;3CX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(3, 1).char, "X")
            self.assertEqual(snapshot.cell(0, 0).char, "A")

    def test_c0_executes_while_rejecting_invalid_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"A\x1b[1?\n2mB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(1, 1).char, "B")

    def test_shift_controls_execute_without_cancelling_csi(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0\x1b[\x0e0mqq\x0f")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "─")
            self.assertEqual(snapshot.cell(1, 0).char, "─")

    def test_c1_csi_restarts_incomplete_seven_bit_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[999;\x9b2;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_seven_bit_csi_restarts_incomplete_eight_bit_csi(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x9b999;\x1b[2;3HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_c1_osc_restarts_incomplete_csi(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[999;\x9d2;title\x9cX")
            self.assertEqual(terminal.read_actions(), ["OSC 2 7469746c65"])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_c1_dcs_restarts_incomplete_osc(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]2;discarded\x90$q\"p\x9c")
            self.assertEqual(terminal.read_actions(), [])
            self.assertEqual(
                terminal.read_input(), b"\x1bP1$r64;1\"p\x1b\\"
            )

    def test_can_and_sub_cancel_every_string_state(self):
        introducers = (b"\x1bP", b"\x1b]", b"\x1bX", b"\x1b^", b"\x1b_")
        for introducer in introducers:
            for cancel in (b"\x18", b"\x1a"):
                with self.subTest(introducer=introducer, cancel=cancel):
                    with Shitty(columns=8, rows=2) as terminal:
                        terminal.write(introducer + b"discard" + cancel + b"X")
                        self.assertEqual(
                            terminal.snapshot().lines[0], "X       "
                        )
                        self.assertEqual(terminal.read_actions(), [])
                        self.assertEqual(terminal.read_input(), b"")

    def test_repeated_escape_aborts_dcs_without_dispatch(self):
        # xterm/vte: the first ESC aborts the string, the second starts a
        # fresh escape sequence which the following backslash completes as
        # a bare (no-op) ST.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP$qz\x1b\x1b\\X")
            self.assertEqual(terminal.read_input(), b"")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_repeated_escape_aborts_osc_without_dispatch(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]2;a\x1b\x1b\\X")
            self.assertEqual(terminal.read_actions(), [])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_repeated_escape_still_allows_ignored_string_terminator(self):
        for introducer in (b"\x1bX", b"\x1b^", b"\x1b_"):
            with self.subTest(introducer=introducer):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(introducer + b"a\x1b\x1b\\X")
                    self.assertEqual(terminal.snapshot().lines[0], "X       ")

    def test_exactly_thirty_two_csi_parameters_are_accepted(self):
        parameters = b"2;3" + b";0" * 30
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[" + parameters + b"HX")
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "X")

    def test_thirty_third_csi_parameter_discards_sequence(self):
        parameters = b"2;3" + b";0" * 31
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[" + parameters + b"HX")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_four_csi_intermediates_are_consumed_atomically(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x1b[    qB")
            self.assertEqual(terminal.snapshot().lines[0], "AB      ")

    def test_fifth_csi_intermediate_discards_through_final(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x1b[     qB")
            self.assertEqual(terminal.snapshot().lines[0], "AB      ")

    def test_numeric_overflow_saturates_and_parser_recovers(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[999999999999999999999999CX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(7, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 7)

    def test_exact_dcs_limit_is_dispatched(self):
        payload = b"$q" + b"x" * (4095 - 2)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP" + payload + b"\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP0$r\x1b\\")

    def test_dcs_over_limit_is_discarded(self):
        payload = b"$q" + b"x" * (4096 - 2)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP" + payload + b"\x1b\\X")
            self.assertEqual(terminal.read_input(), b"")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_exact_osc_limit_is_dispatched(self):
        payload = b"x" * (1024 * 1024 - 2)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]2;" + payload + b"\x1b\\")
            actions = terminal.read_actions()
            self.assertEqual(len(actions), 1)
            self.assertEqual(len(actions[0]), len("OSC 2 ") + 2 * len(payload))

    def test_osc_over_limit_is_discarded_and_recovers(self):
        payload = b"x" * (1024 * 1024 - 1)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b]2;" + payload + b"\x1b\\X")
            self.assertEqual(terminal.read_actions(), [])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_over_limit_structured_payloads_discard_auxiliary_state(self):
        sequences = (
            b"\x1bP0;0|" + b"17/41;" * 1024 + b"\x1b\\",
            b"\x1b]4;" + b"1;#000;" * (1024 * 1024 // 7 + 16) + b"\x1b\\",
        )
        for sequence in sequences:
            with self.subTest(sequence=sequence[:8]):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(sequence + b"X")
                    self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
                    self.assertEqual(terminal.read_input(), b"")

    def test_utf8_continuation_in_c1_range_is_not_a_control(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(b"\xd0", b"\x9bX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "Л")
            self.assertEqual(snapshot.cell(1, 0).char, "X")

    def test_utf8_continuations_in_osc_are_not_c1_controls(self):
        old_spinner = "✽".encode()
        prompt = "❯".encode()
        title = "⠐ title".encode()
        new_spinner = "✻".encode()
        payload = (
            b"\x1b[1;1H" + old_spinner
            + b"\x1b[2;1H" + prompt
            + b"\x1b]0;" + title + b"\a"
            + b"\x1b[1;1H" + new_spinner
        )
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(*(bytes((byte,)) for byte in payload))
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "✻")
            self.assertEqual(snapshot.cell(0, 1).char, "❯")
            self.assertEqual(
                terminal.read_actions(),
                ["OSC 0 " + title.hex()],
            )

    def test_csi_c0_and_cancel_are_chunk_independent(self):
        self.assert_chunkings_equal(b"A\x1b[2\n;3H\x18\x1b[2;4HX")

    def test_dcs_escape_and_cancel_are_chunk_independent(self):
        self.assert_chunkings_equal(
            b"\x1bP$qz\x1bQ\x18\x1bP$q\"p\x1b\\X"
        )
        self.assert_chunkings_equal(
            b"\x1bP+q544e;436f;524742\x1b\\X"
        )

    def test_osc_escape_and_bel_are_chunk_independent(self):
        self.assert_chunkings_equal(
            b"\x1b]2;a\x1bQ\x18\x1b]2;title\aX"
        )

    def test_ignored_strings_are_chunk_independent(self):
        for payload in (
            b"\x1bXone\x1bQtwo\x1b\\X",
            b"\x1b^one\x1bQtwo\x1b\\X",
            b"\x1b_one\x1bQtwo\x1b\\X",
        ):
            with self.subTest(payload=payload[:2]):
                self.assert_chunkings_equal(payload)


if __name__ == "__main__":
    unittest.main()

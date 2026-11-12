# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 20 xterm.js Params cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "should respect ctor args",
    "addParam",
    "addSubParam",
    "should not add sub params without previous param",
    "reset",
    "Params.fromArray --> toArray",
    "clone",
    "hasSubParams / getSubParams",
    "getSubParamsAll",
    "param defaults to 0 (ZDM - zero default mode)",
    "sub param defaults to -1",
    "should correctly reset on new sequence",
    "should handle length restrictions correctly",
    "typical sequences",
    "reject params lesser -1",
    "reject subparams lesser -1",
    "clamp parsed params",
    "clamp parsed subparams",
    "should cancel subdigits if beyond params limit",
    "should carry forward isSub state",
)


class XtermJsParamsTest(unittest.TestCase):
    def trace(self, *chunks):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.parser_trace_on()
            terminal.write_chunks(*chunks)
            return terminal.parser_trace()

    def test_upstream_inventory_has_all_20_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len(set(PORTED_CASES)), 20)

    def test_ctor_capacities_have_a_common_public_below_limit_form(self):
        ordinary = b";".join(str(value).encode() for value in range(1, 13))
        grouped = b":".join(str(value).encode() for value in range(1, 13))
        self.assertEqual(
            self.trace(b"\x1b[" + ordinary + b"m", b"\x1b[" + grouped + b"m"),
            [("csi", ordinary + b"m"), ("csi", grouped + b"m")],
        )

    def test_add_param_preserves_two_ordinary_parameters(self):
        self.assertEqual(self.trace(b"\x1b[1;23m"), [("csi", b"1;23m")])

    def test_add_subparam_keeps_each_group_attached_to_its_parameter(self):
        self.assertEqual(
            self.trace(b"\x1b[1:2:3;12345:m"),
            [("csi", b"1:2:3;12345:0m")],
        )

    def test_leading_subparameter_separator_opens_an_empty_parameter(self):
        self.assertEqual(
            self.trace(b"\x1b[:2:3m"),
            [("csi", b"0:2:3m")],
        )

    def test_reset_discards_an_aborted_parameter_transaction(self):
        self.assertEqual(
            self.trace(b"\x1b[1:2:3;12345:\x1b[4:5mX"),
            [("csi", b"4:5m"), ("text", b"X")],
        )

    def test_array_forms_have_distinct_public_wire_roundtrips(self):
        payload = (
            b"\x1b[m"
            b"\x1b[1:2:3;12345:m"
            b"\x1b[38;2;50;100;150m"
            b"\x1b[38;2;50;100:150m"
            b"\x1b[38:2:50:100:150m"
            b"\x1b[5;6m"
        )
        self.assertEqual(
            self.trace(payload),
            [
                ("csi", b"m"),
                ("csi", b"1:2:3;12345:0m"),
                ("csi", b"38;2;50;100;150m"),
                ("csi", b"38;2;50;100:150m"),
                ("csi", b"38:2:50:100:150m"),
                ("csi", b"5;6m"),
            ],
        )

    def test_completed_parameter_state_is_stable_after_later_sequences(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[38:2::50:100:150mX\x1b[0mY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).foreground, (50, 100, 150))
            self.assertEqual(snapshot.cell(1, 0).foreground, (255, 255, 255))

    def test_grouped_indexed_colors_are_independently_addressable(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[38:5:1;48:5:0mX")
            pen = terminal.pen_state()
            self.assertEqual(pen.foreground_index, 1)
            self.assertEqual(pen.background_index, 0)

    def test_all_subparameter_groups_reach_their_public_consumers(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[4:3;38:2::50:100:150mX")
            cell = terminal.snapshot().cell(0, 0)
            self.assertEqual(cell.underline_style, 3)
            self.assertEqual(cell.foreground, (50, 100, 150))

    def test_empty_sgr_uses_its_zero_default_public_effect(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[1mA\x1b[mB")
            snapshot = terminal.snapshot()
            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertFalse(snapshot.cell(1, 0).bold)

    def test_empty_subparameter_uses_the_protocol_default(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[58:2::240:143:104mX")
            self.assertEqual(
                terminal.snapshot().cell(0, 0).underline_color,
                (240, 143, 104),
            )

    def test_each_completed_sequence_starts_with_fresh_parameters(self):
        self.assertEqual(
            self.trace(
                b"\x1b[1;2;3m"
                b"\x1b[4m"
                b"\x1b[4::123:5;6;7m"
                b"\x1b[m"
            ),
            [
                ("csi", b"1;2;3m"),
                ("csi", b"4m"),
                ("csi", b"4:0:123:5;6;7m"),
                ("csi", b"m"),
            ],
        )

    def test_public_parameter_capacity_accepts_32_and_discards_33(self):
        accepted = b";".join(b"1" for _ in range(32))
        rejected = b";".join(b"1" for _ in range(33))
        self.assertEqual(
            self.trace(
                b"\x1b[" + accepted + b"m",
                b"\x1b[" + rejected + b"mX",
            ),
            [("csi", accepted + b"m"), ("text", b"X")],
        )

    def test_typical_semicolon_mixed_and_colon_forms_remain_distinct(self):
        forms = (
            b"0;4;38;2;50;100;150;48;5;22",
            b"0;4;38;2;50:100:150;48;5:22",
            b"0;4;38:2::50:100:150;48:5:22",
        )
        self.assertEqual(
            self.trace(*(b"\x1b[" + form + b"m" for form in forms)),
            [("csi", form.replace(b"::", b":0:") + b"m") for form in forms],
        )

    def test_negative_main_parameter_spelling_is_rejected_and_recovers(self):
        with Shitty(columns=8, rows=1) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[-2CX")
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_negative_subparameter_spelling_is_rejected_and_recovers(self):
        with Shitty(columns=8, rows=1) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[1:-2mX")
            self.assertEqual(terminal.parser_trace(), [("text", b"X")])
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_large_main_parameter_stays_nonnegative_and_clamps_publicly(self):
        with Shitty(columns=8, rows=1) as terminal:
            terminal.write(b"\x1b[2147483648CX\x1b[2DY")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(7, 0).char, "X")
            self.assertEqual(snapshot.cell(5, 0).char, "Y")

    def test_large_subparameter_cannot_poison_the_following_transaction(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[58:5:2147483648mA\x1b[38:5:1mB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(1, 0).char, "B")
            self.assertEqual(terminal.pen_state().foreground_index, 1)

    def test_over_limit_subdigits_cannot_corrupt_the_next_sequence(self):
        source = b";;;;;;;;;10;;;;;;;;;;20;;;;;;;;;;30;31;32;33;34;35::::::::"
        with Shitty(columns=8, rows=3) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + source + b"mX\x1b[2;3HY")
            self.assertEqual(
                terminal.parser_trace(),
                [("text", b"X"), ("csi", b"2;3H"), ("text", b"Y")],
            )
            self.assertEqual(terminal.snapshot().cell(2, 1).char, "Y")

    def test_subparameter_digit_state_survives_chunk_boundaries(self):
        self.assertEqual(
            self.trace(b"\x1b[1:22:33", b"44m"),
            [("csi", b"1:22:3344m")],
        )


if __name__ == "__main__":
    unittest.main()

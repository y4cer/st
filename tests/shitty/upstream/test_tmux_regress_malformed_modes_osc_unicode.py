# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Malformed input, modes, OSC and Unicode streams from tmux regress."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/input-malformed.sh:csi-param-discard", "test_csi_parameter_overflow_recovers_at_can"),
    ("regress/input-malformed.sh:csi-interm-discard", "test_csi_intermediate_overflow_recovers_at_can"),
    ("regress/input-malformed.sh:osc-discard", "test_oversized_osc_recovers_at_st"),
    ("regress/input-malformed.sh:apc-discard", "test_oversized_apc_recovers_at_st"),
    ("regress/input-malformed.sh:unknown-csi", "test_unknown_csi_is_ignored"),
    ("regress/input-malformed.sh:unknown-osc", "test_unknown_osc_is_ignored"),
    ("regress/input-malformed.sh:malformed-osc", "test_malformed_osc_uses_consensus_hyperlink_recovery"),
    ("regress/input-malformed.sh:malformed-dcs", "test_bad_decrqss_gets_failure_reply"),
    ("regress/input-malformed.sh:malformed-utf8", "test_malformed_utf8_uses_unicode_maximal_subparts"),
    ("regress/input-modes.sh:alternate", "test_alternate_screen_restores_main_screen"),
    ("regress/input-modes.sh:osc133", "test_osc133_partitions_prompt_command_output_and_idle"),
    ("regress/input-osc.sh:hyperlink", "test_osc8_hyperlink_scope"),
    ("regress/input-osc.sh:palette", "test_palette_set_and_targeted_reset"),
    ("regress/input-osc.sh:osc-colours", "test_dynamic_colours_set_and_reset"),
    ("regress/input-osc.sh:progress", "test_progress_accepts_known_states_and_ignores_unknown_state"),
    ("regress/input-osc.sh:rename", "test_screen_title_extension_is_not_a_vt_string"),
    ("regress/input-osc.sh:apc-title", "test_plain_apc_is_not_a_title"),
    ("regress/input-osc.sh:title-stack", "test_title_stack_overflow_and_reset_are_safe"),
    ("regress/input-osc.sh:osc52", "test_osc52_sets_clipboard"),
    ("regress/input-unicode.sh:wide", "test_overwriting_wide_lead_clears_continuation"),
)


class TmuxRegressMalformedModesOscUnicodeTest(unittest.TestCase):
    def _assert_page(self, terminal, *lines):
        snapshot = terminal.snapshot()
        expected = [line.ljust(snapshot.columns) for line in lines]
        expected.extend([" " * snapshot.columns] * (snapshot.rows - len(expected)))
        self.assertEqual(snapshot.lines, expected)
        return snapshot

    def _write_oversized_string(self, terminal, introducer):
        terminal.write(introducer)
        block = b"x" * 65536
        remaining = 1_100_000
        while remaining:
            chunk = block[:remaining]
            terminal.write(chunk)
            remaining -= len(chunk)
        terminal.write(b"\x1b\\OK")

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_csi_parameter_overflow_recovers_at_can(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[" + b"1" * 80 + b"\x18OK")
            self._assert_page(terminal, "OK")

    def test_csi_intermediate_overflow_recovers_at_can(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[    \x18OK")
            self._assert_page(terminal, "OK")

    def test_oversized_osc_recovers_at_st(self):
        with Shitty(columns=8, rows=3) as terminal:
            self._write_oversized_string(terminal, b"\x1b]2;")
            self._assert_page(terminal, "OK")

    def test_oversized_apc_recovers_at_st(self):
        with Shitty(columns=8, rows=3) as terminal:
            self._write_oversized_string(terminal, b"\x1b_")
            self._assert_page(terminal, "OK")

    def test_unknown_csi_is_ignored(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[?9999zOK")
            self._assert_page(terminal, "OK")

    def test_unknown_osc_is_ignored(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b]999;bad\aOK")
            self._assert_page(terminal, "OK")

    def test_malformed_osc_uses_consensus_hyperlink_recovery(self):
        stream = (
            b"\x1b]8;id=a:id=b;http://bad\aX"
            b"\x1b]8;id=no-separator\aY"
            b"\x1b]9;4;5;200\a"
            b"\x1b]9;4;z\a"
            b"\x1b]10;notacolour\a"
            b"\x1b]11;notacolour\a"
            b"\x1b]12;notacolour\a"
            b"\x1b]4;999;red\a"
            b"\x1b]104;999\a"
            b"\x1b]52bad\a"
            b"\x1b]52;c;@@@\a"
            b"OK"
        )
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(stream)
            snapshot = self._assert_page(terminal, "XYOK")
            self.assertTrue(all(snapshot.cell(column, 0).hyperlink != 0 for column in range(4)))
            self.assertEqual(
                [terminal.hyperlink(column, 0) for column in range(4)],
                ["http://bad"] * 4,
            )
            self.assertEqual(terminal.get_selection(primary=False), b"")

    def test_bad_decrqss_gets_failure_reply(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1bP$qBAD\x1b\\OK")
            self._assert_page(terminal, "OK")
            self.assertEqual(terminal.read_input(), b"\x1bP0$r\x1b\\")

    def test_malformed_utf8_uses_unicode_maximal_subparts(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\xf0\x80\x80\x80A\xed\xa0\x80B")
            self._assert_page(terminal, "\ufffd\ufffd\ufffd\ufffdA\ufffd\ufffd\ufffdB")

    def test_alternate_screen_restores_main_screen(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"MAIN\x1b[?1049hALT\x1b[?1049lZ\r\n")
            self._assert_page(terminal, "MAINZ")

    def test_osc133_partitions_prompt_command_output_and_idle(self):
        stream = (
            b"xx\x1b]133;A\ap>\x1b]133;B\acmd\r\n"
            b"xy\x1b]133;P;k=s\amore\r\n"
            b"zz\x1b]133;C\aout\x1b]133;D;7\a\r\n"
            b"q\x1b]133;C\abad\x1b]133;D;-1\a\r\n"
            b"qq\x1b]133;C\abig\x1b]133;D;300\a\r\n"
            b"zzz\x1b]133;C\aok\x1b]133;D\a\r\n"
        )
        with Shitty(columns=20, rows=8) as terminal:
            terminal.write(stream)
            snapshot = self._assert_page(
                terminal,
                "xxp>cmd",
                "xymore",
                "zzout",
                "qbad",
                "qqbig",
                "zzzok",
            )
            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(7)],
                [0, 0, 1, 1, 2, 2, 2],
            )
            self.assertEqual(
                [snapshot.cell(column, 1).semantic for column in range(6)],
                [2, 2, 1, 1, 1, 1],
            )
            self.assertEqual(
                [snapshot.cell(column, 2).semantic for column in range(5)],
                [1, 1, 3, 3, 3],
            )
            self.assertEqual(
                [snapshot.cell(column, 3).semantic for column in range(4)],
                [0, 3, 3, 3],
            )
            self.assertEqual(
                [snapshot.cell(column, 4).semantic for column in range(5)],
                [0, 0, 3, 3, 3],
            )
            self.assertEqual(
                [snapshot.cell(column, 5).semantic for column in range(5)],
                [0, 0, 0, 3, 3],
            )

    def test_osc8_hyperlink_scope(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b]8;id=1;https://example.com\x1b\\"
                b"link\x1b]8;;\x1b\\ plain\r\n"
            )
            snapshot = self._assert_page(terminal, "link plain")
            self.assertEqual(terminal.hyperlink_count(), 1)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.com")
            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(snapshot.cell(4, 0).hyperlink, 0)

    def test_palette_set_and_targeted_reset(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b]4;1;rgb:11/22/33;2;red\a"
                b"\x1b]104;1;2\aX\r\n"
            )
            self._assert_page(terminal, "X")
            terminal.write(b"\x1b]4;1;?;2;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]4;1;rgb:aaaa/0000/0000\x1b\\"
                b"\x1b]4;2;rgb:0000/aaaa/0000\x1b\\",
            )

    def test_dynamic_colours_set_and_reset(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b]10;rgb:11/22/33\a"
                b"\x1b]11;rgb:44/55/66\a"
                b"\x1b]12;rgb:77/88/99\a"
                b"\x1b]110\a\x1b]111\a\x1b]112\aX\r\n"
            )
            self._assert_page(terminal, "X")
            terminal.write(b"\x1b]10;?\x1b\\\x1b]11;?\x1b\\\x1b]12;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]10;rgb:ffff/ffff/ffff\x1b\\"
                b"\x1b]11;rgb:0000/0000/0000\x1b\\"
                b"\x1b]12;rgb:ffff/ffff/ffff\x1b\\",
            )

    def test_progress_accepts_known_states_and_ignores_unknown_state(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b]9;4;1;25\a"
                b"\x1b]9;4;0\a"
                b"\x1b]9;4;5;200\aX\r\n"
            )
            self._assert_page(terminal, "X")
            self.assertEqual(
                terminal.read_actions(),
                ["PROGRESS 1 25", "PROGRESS 0 0"],
            )

    def test_screen_title_extension_is_not_a_vt_string(self):
        with Shitty(columns=20, rows=3) as terminal:
            title = terminal.window_title()
            terminal.write(b"\x1bkrenamed\x1b\\X\r\n")
            self._assert_page(terminal, "renamedX")
            self.assertEqual(terminal.window_title(), title)

    def test_plain_apc_is_not_a_title(self):
        with Shitty(columns=20, rows=3) as terminal:
            title = terminal.window_title()
            terminal.write(b"\x1b_test-title\x1b\\X\r\n")
            self._assert_page(terminal, "X")
            self.assertEqual(terminal.window_title(), title)

    def test_title_stack_overflow_and_reset_are_safe(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[22;0t" * 12 + b"X")
            self._assert_page(terminal, "X")
            terminal.hard_reset()
            terminal.write(b"\x1b[22;0tY")
            self._assert_page(terminal, "Y")

    def test_osc52_sets_clipboard(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b]52;c;SGVsbG8=\a")
            self.assertEqual(terminal.get_selection(primary=False), b"Hello")

    def test_overwriting_wide_lead_clears_continuation(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write("あB\rX\r\n".encode())
            snapshot = self._assert_page(terminal, "X B")
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)


if __name__ == "__main__":
    unittest.main()

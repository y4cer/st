# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Unicode and reply streams from current tmux regress tests."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/input-unicode.sh:widepad", "test_overwriting_wide_tail_clears_lead"),
    ("regress/input-unicode.sh:wideedge", "test_wide_character_at_right_edge_soft_wraps"),
    ("regress/input-unicode.sh:wideeol", "test_wide_character_without_room_moves_wholly_to_next_row"),
    ("regress/input-unicode.sh:combine", "test_combining_mark_joins_narrow_base"),
    ("regress/input-unicode.sh:combinewide", "test_combining_mark_joins_wide_base"),
    ("regress/input-unicode.sh:variation", "test_vs16_promotes_text_emoji_to_wide_cluster"),
    ("regress/input-unicode.sh:flag", "test_regional_indicator_pair_is_one_wide_cluster"),
    ("regress/input-unicode.sh:combining-left", "test_leading_combining_mark_does_not_shift_following_text"),
    ("regress/input-unicode.sh:combining-overflow", "test_long_combining_cluster_is_not_truncated_at_tmux_limit"),
    ("regress/input-replies.sh:dsr-ok", "test_dsr_reports_operating_status"),
    ("regress/input-replies.sh:dsr-cursor", "test_dsr_reports_cursor_position"),
    ("regress/input-replies.sh:da-primary", "test_primary_da_reports_shitty_capabilities"),
    ("regress/input-replies.sh:da-secondary", "test_secondary_da_reports_shitty_identity"),
    ("regress/input-replies.sh:decrqm-irm-reset", "test_decrqm_reports_irm_reset"),
    ("regress/input-replies.sh:decrqm-irm-set", "test_decrqm_reports_irm_set"),
    ("regress/input-replies.sh:decrqm-cursor-keys-reset", "test_decrqm_reports_decckm_reset"),
    ("regress/input-replies.sh:decrqm-cursor-keys-set", "test_decrqm_reports_decckm_set"),
    ("regress/input-replies.sh:decrqm-columns", "test_decrqm_reports_deccolm_as_mutable_reset"),
    ("regress/input-replies.sh:decrqm-origin-reset", "test_decrqm_reports_decom_reset"),
    ("regress/input-replies.sh:decrqm-origin-set", "test_decrqm_reports_decom_set"),
)


class TmuxRegressUnicodeRepliesTest(unittest.TestCase):
    def _run_unicode(self, columns, rows, payload):
        # start_pane writes through a normal PTY.  Preserve its ONLCR
        # conversion instead of changing the source scenario's cursor path.
        with Shitty(columns=columns, rows=rows) as terminal:
            terminal.write(payload.replace(b"\n", b"\r\n"))
            return terminal.model_snapshot()

    def _query(self, setup, request):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(setup + request)
            return terminal.read_input()

    def test_upstream_inventory_has_20_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 20)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 20)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_overwriting_wide_tail_clears_lead(self):
        snapshot = self._run_unicode(
            10, 3, "AあB\r\x1b[2CX\n".encode()
        )
        self.assertEqual(snapshot.lines, ["A XB      ", "          ", "          "])
        self.assertFalse(snapshot.cell(1, 0).double_width)
        self.assertFalse(snapshot.cell(2, 0).double_width_continuation)
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_wide_character_at_right_edge_soft_wraps(self):
        snapshot = self._run_unicode(5, 3, "abcあZ\n".encode())
        self.assertEqual(snapshot.lines, ["abcあ ", "Z    ", "     "])
        self.assertTrue(snapshot.cell(3, 0).double_width)
        self.assertTrue(snapshot.cell(4, 0).double_width_continuation)
        self.assertTrue(snapshot.cell(4, 0).wrapped)
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))

    def test_wide_character_without_room_moves_wholly_to_next_row(self):
        snapshot = self._run_unicode(5, 3, "abcdあZ\n".encode())
        self.assertEqual(snapshot.lines, ["abcd ", "あ Z  ", "     "])
        self.assertTrue(snapshot.cell(3, 0).wrapped)
        self.assertFalse(snapshot.cell(4, 0).drawn)
        self.assertTrue(snapshot.cell(0, 1).double_width)
        self.assertTrue(snapshot.cell(1, 1).double_width_continuation)
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))

    def test_combining_mark_joins_narrow_base(self):
        snapshot = self._run_unicode(10, 3, "e\u0301\n".encode())
        self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("e"), 0x0301))
        self.assertFalse(snapshot.cell(0, 0).double_width)
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_combining_mark_joins_wide_base(self):
        snapshot = self._run_unicode(10, 3, "あ\u0301X\n".encode())
        self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("あ"), 0x0301))
        self.assertTrue(snapshot.cell(0, 0).double_width)
        self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
        self.assertEqual(snapshot.cell(2, 0).char, "X")
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_vs16_promotes_text_emoji_to_wide_cluster(self):
        snapshot = self._run_unicode(10, 3, "\u2714\ufe0fX\n".encode())
        self.assertEqual(snapshot.cell(0, 0).grapheme, (0x2714, 0xFE0F))
        self.assertTrue(snapshot.cell(0, 0).double_width)
        self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
        self.assertEqual(snapshot.cell(2, 0).char, "X")
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_regional_indicator_pair_is_one_wide_cluster(self):
        snapshot = self._run_unicode(10, 3, "\U0001f1ec\U0001f1e7X\n".encode())
        self.assertEqual(snapshot.cell(0, 0).grapheme, (0x1F1EC, 0x1F1E7))
        self.assertTrue(snapshot.cell(0, 0).double_width)
        self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
        self.assertEqual(snapshot.cell(2, 0).char, "X")
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_leading_combining_mark_does_not_shift_following_text(self):
        snapshot = self._run_unicode(10, 3, "\u0301A\n".encode())
        self.assertEqual(snapshot.lines[0], "A         ")
        self.assertEqual(snapshot.cell(0, 0).char, "A")
        self.assertEqual(snapshot.cell(0, 0).grapheme, ())
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_long_combining_cluster_is_not_truncated_at_tmux_limit(self):
        cluster = "u" + "\u0325" * 16
        snapshot = self._run_unicode(10, 3, (cluster + "\n").encode())
        self.assertEqual(
            snapshot.cell(0, 0).grapheme,
            (ord("u"),) + (0x0325,) * 16,
        )
        self.assertEqual(snapshot.cell(1, 0).char, " ")
        self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_dsr_reports_operating_status(self):
        self.assertEqual(self._query(b"", b"\x1b[5n"), b"\x1b[0n")

    def test_dsr_reports_cursor_position(self):
        self.assertEqual(self._query(b"", b"\x1b[6n"), b"\x1b[1;1R")

    def test_primary_da_reports_shitty_capabilities(self):
        self.assertEqual(
            self._query(b"", b"\x1b[c"),
            b"\x1b[?64;1;2;4;6;8;9;15;21;22;28;29c",
        )

    def test_secondary_da_reports_shitty_identity(self):
        self.assertEqual(self._query(b"", b"\x1b[>c"), b"\x1b[>41;14;0c")

    def test_decrqm_reports_irm_reset(self):
        self.assertEqual(self._query(b"", b"\x1b[4$p"), b"\x1b[4;2$y")

    def test_decrqm_reports_irm_set(self):
        self.assertEqual(self._query(b"\x1b[4h", b"\x1b[4$p"), b"\x1b[4;1$y")

    def test_decrqm_reports_decckm_reset(self):
        self.assertEqual(self._query(b"", b"\x1b[?1$p"), b"\x1b[?1;2$y")

    def test_decrqm_reports_decckm_set(self):
        self.assertEqual(self._query(b"\x1b[?1h", b"\x1b[?1$p"), b"\x1b[?1;1$y")

    def test_decrqm_reports_deccolm_as_mutable_reset(self):
        self.assertEqual(self._query(b"", b"\x1b[?3$p"), b"\x1b[?3;2$y")

    def test_decrqm_reports_decom_reset(self):
        self.assertEqual(self._query(b"", b"\x1b[?6$p"), b"\x1b[?6;2$y")

    def test_decrqm_reports_decom_set(self):
        self.assertEqual(self._query(b"\x1b[?6h", b"\x1b[?6$p"), b"\x1b[?6;1$y")


if __name__ == "__main__":
    unittest.main()

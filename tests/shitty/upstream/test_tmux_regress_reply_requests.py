# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Remaining reply and terminal-request streams from current tmux regress."""

import unittest

from harness import Shitty


PORTED_CASES = (
    ("regress/input-replies.sh:decrqm-wrap-set", "test_decrqm_reports_decawm_set"),
    ("regress/input-replies.sh:decrqm-wrap-reset", "test_decrqm_reports_decawm_reset"),
    ("regress/input-replies.sh:decrqm-cursor-visible-set", "test_decrqm_reports_dectcem_set"),
    ("regress/input-replies.sh:decrqm-cursor-visible-reset", "test_decrqm_reports_dectcem_reset"),
    ("regress/input-replies.sh:decrqm-mouse-standard-set", "test_decrqm_reports_normal_mouse_set"),
    ("regress/input-replies.sh:decrqm-mouse-button-set", "test_decrqm_reports_button_mouse_set"),
    ("regress/input-replies.sh:decrqm-mouse-all-set", "test_decrqm_reports_any_mouse_set"),
    ("regress/input-replies.sh:decrqm-focus-set", "test_decrqm_reports_focus_events_set"),
    ("regress/input-replies.sh:decrqm-mouse-utf8-set", "test_decrqm_reports_utf8_mouse_set"),
    ("regress/input-replies.sh:decrqm-mouse-sgr-set", "test_decrqm_reports_sgr_mouse_set"),
    ("regress/input-replies.sh:decrqm-bracket-paste-set", "test_decrqm_reports_bracketed_paste_set"),
    ("regress/input-replies.sh:decrqm-theme-updates-set", "test_decrqm_reports_theme_updates_set"),
    ("regress/input-replies.sh:decrqss-cursor-style", "test_decrqss_reports_selected_cursor_style"),
    ("regress/input-replies.sh:osc-10-query", "test_osc10_queries_changed_foreground"),
    ("regress/input-replies.sh:osc-11-query", "test_osc11_queries_changed_background"),
    ("regress/input-replies.sh:osc-12-query", "test_osc12_queries_changed_cursor_color"),
    ("regress/input-replies.sh:osc-4-query", "test_osc4_queries_changed_palette_entry"),
    ("regress/input-replies.sh:osc-104-reset-query", "test_osc104_restores_queryable_palette_entry"),
    ("regress/input-replies.sh:osc-52-query", "test_osc52_queries_allowed_clipboard"),
    ("regress/input-requests.sh:palette-reply", "test_palette_request_round_trip"),
    ("regress/input-requests.sh:clipboard-reply", "test_clipboard_request_round_trip"),
)


class TmuxRegressReplyRequestsTest(unittest.TestCase):
    def _query(self, setup, request, extra_arguments=()):
        with Shitty(
            columns=80,
            rows=24,
            extra_arguments=extra_arguments,
        ) as terminal:
            terminal.write(setup + request)
            return terminal.read_input()

    def _private_mode_query(self, mode, setup):
        return self._query(setup, f"\x1b[?{mode}$p".encode())

    def test_upstream_inventory_has_21_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 21)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 21)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 21)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_decrqm_reports_decawm_set(self):
        self.assertEqual(
            self._private_mode_query(7, b""),
            b"\x1b[?7;1$y",
        )

    def test_decrqm_reports_decawm_reset(self):
        self.assertEqual(
            self._private_mode_query(7, b"\x1b[?7l"),
            b"\x1b[?7;2$y",
        )

    def test_decrqm_reports_dectcem_set(self):
        self.assertEqual(
            self._private_mode_query(25, b""),
            b"\x1b[?25;1$y",
        )

    def test_decrqm_reports_dectcem_reset(self):
        self.assertEqual(
            self._private_mode_query(25, b"\x1b[?25l"),
            b"\x1b[?25;2$y",
        )

    def test_decrqm_reports_normal_mouse_set(self):
        self.assertEqual(
            self._private_mode_query(1000, b"\x1b[?1000h"),
            b"\x1b[?1000;1$y",
        )

    def test_decrqm_reports_button_mouse_set(self):
        self.assertEqual(
            self._private_mode_query(1002, b"\x1b[?1002h"),
            b"\x1b[?1002;1$y",
        )

    def test_decrqm_reports_any_mouse_set(self):
        self.assertEqual(
            self._private_mode_query(1003, b"\x1b[?1003h"),
            b"\x1b[?1003;1$y",
        )

    def test_decrqm_reports_focus_events_set(self):
        self.assertEqual(
            self._private_mode_query(1004, b"\x1b[?1004h"),
            b"\x1b[?1004;1$y",
        )

    def test_decrqm_reports_utf8_mouse_set(self):
        self.assertEqual(
            self._private_mode_query(1005, b"\x1b[?1005h"),
            b"\x1b[?1005;1$y",
        )

    def test_decrqm_reports_sgr_mouse_set(self):
        self.assertEqual(
            self._private_mode_query(1006, b"\x1b[?1006h"),
            b"\x1b[?1006;1$y",
        )

    def test_decrqm_reports_bracketed_paste_set(self):
        self.assertEqual(
            self._private_mode_query(2004, b"\x1b[?2004h"),
            b"\x1b[?2004;1$y",
        )

    def test_decrqm_reports_theme_updates_set(self):
        self.assertEqual(
            self._private_mode_query(2031, b"\x1b[?2031h"),
            b"\x1b[?2031;1$y",
        )

    def test_decrqss_reports_selected_cursor_style(self):
        self.assertEqual(
            self._query(b"\x1b[6 q", b"\x1bP$q q\x1b\\"),
            b"\x1bP1$r6 q\x1b\\",
        )

    def test_osc10_queries_changed_foreground(self):
        self.assertEqual(
            self._query(b"\x1b]10;red\x07", b"\x1b]10;?\x07"),
            b"\x1b]10;rgb:ffff/0000/0000\x1b\\",
        )

    def test_osc11_queries_changed_background(self):
        self.assertEqual(
            self._query(b"\x1b]11;blue\x07", b"\x1b]11;?\x07"),
            b"\x1b]11;rgb:0000/0000/ffff\x1b\\",
        )

    def test_osc12_queries_changed_cursor_color(self):
        self.assertEqual(
            self._query(b"\x1b]12;green\x07", b"\x1b]12;?\x07"),
            b"\x1b]12;rgb:0000/ffff/0000\x1b\\",
        )

    def test_osc4_queries_changed_palette_entry(self):
        self.assertEqual(
            self._query(b"\x1b]4;1;red\x07", b"\x1b]4;1;?\x07"),
            b"\x1b]4;1;rgb:ffff/0000/0000\x1b\\",
        )

    def test_osc104_restores_queryable_palette_entry(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"\x1b]4;1;?\x07")
            original = terminal.read_input()
            terminal.write(
                b"\x1b]4;1;red\x07"
                b"\x1b]104;1\x07"
                b"\x1b]4;1;?\x07"
            )
            self.assertEqual(terminal.read_input(), original)

    def test_osc52_queries_allowed_clipboard(self):
        with Shitty(
            columns=80,
            rows=24,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_system_clipboard(b"Hello")
            terminal.write(b"\x1b]52;c;?\x07")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;c;SGVsbG8=\x1b\\",
            )

    def test_palette_request_round_trip(self):
        self.assertEqual(
            self._query(
                b"\x1b]4;99;rgb:01/02/03\x1b\\",
                b"\x1b]4;99;?\x1b\\",
            ),
            b"\x1b]4;99;rgb:0101/0202/0303\x1b\\",
        )

    def test_clipboard_request_round_trip(self):
        with Shitty(
            columns=80,
            rows=24,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_system_clipboard(b"Request")
            terminal.write(b"\x1b]52;c;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;c;UmVxdWVzdA==\x1b\\",
            )


if __name__ == "__main__":
    unittest.main()

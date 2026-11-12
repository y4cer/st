# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 181 through 194."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "DECRQM reports ANSI keyboard action mode",
    "DECRQM reports ANSI insert mode",
    "DECRQM reports ANSI send/receive mode",
    "DECRQM reports ANSI newline mode",
    "DECRQM reports an unknown ANSI mode",
    "DECRQM reports mutable DEC private modes",
    "DECRQM reports the cursor-blink quirk",
    "DECRQM reports permanent DEC private modes",
    "kitty keyboard stack evicts its oldest entry beyond depth 16",
    "kitty keyboard flags are separate on primary and alternate screens",
    "kitty keyboard pop beyond the stack resets flags",
    "a cursor-position report follows the preceding CUP",
    "text around an OSC handler remains ordered",
    "text around a DCS handler remains ordered",
)


def mode_query(terminal, mode, private=False):
    marker = "?" if private else ""
    terminal.write(f"\x1b[{marker}{mode}$p".encode())
    return terminal.read_input()


def mode_reply(mode, state, private=False):
    marker = "?" if private else ""
    return f"\x1b[{marker}{mode};{state}$y".encode()


def kitty_query(terminal):
    terminal.write(b"\x1b[?u")
    return terminal.read_input()


class XtermJsInputHandlerModesAsyncTest(unittest.TestCase):
    def test_upstream_inventory_has_14_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 14)
        self.assertEqual(len(set(UPSTREAM_CASES)), 14)

    @unittest.expectedFailure
    def test_decrqm_ansi_keyboard_action_mode(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 2), mode_reply(2, 4))

    def test_decrqm_ansi_insert_mode(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 4), mode_reply(4, 2))
            terminal.write(b"\x1b[4h")
            self.assertEqual(mode_query(terminal, 4), mode_reply(4, 1))
            terminal.write(b"\x1b[4l")
            self.assertEqual(mode_query(terminal, 4), mode_reply(4, 2))

    @unittest.expectedFailure
    def test_decrqm_ansi_send_receive_mode(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 12), mode_reply(12, 3))

    def test_decrqm_ansi_newline_mode(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 20), mode_reply(20, 2))
            terminal.write(b"\x1b[20h")
            self.assertEqual(mode_query(terminal, 20), mode_reply(20, 1))
            terminal.write(b"\x1b[20l")
            self.assertEqual(mode_query(terminal, 20), mode_reply(20, 2))

    def test_decrqm_unknown_ansi_mode(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 1234), mode_reply(1234, 0))

    def test_decrqm_mutable_dec_private_modes(self):
        initially_reset = (
            1, 6, 9, 45, 66, 1000, 1002, 1003, 1004, 1006,
            1016, 47, 1047, 1049, 2004, 2026,
        )
        initially_set = (7, 25)
        for mode in initially_reset:
            with self.subTest(mode=mode), Shitty() as terminal:
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 2, True),
                )
                terminal.write(f"\x1b[?{mode}h".encode())
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 1, True),
                )
                terminal.write(f"\x1b[?{mode}l".encode())
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 2, True),
                )
        for mode in initially_set:
            with self.subTest(mode=mode), Shitty() as terminal:
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 1, True),
                )
                terminal.write(f"\x1b[?{mode}l".encode())
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 2, True),
                )
                terminal.write(f"\x1b[?{mode}h".encode())
                self.assertEqual(
                    mode_query(terminal, mode, True),
                    mode_reply(mode, 1, True),
                )

    @unittest.expectedFailure
    def test_decrqm_cursor_blink_quirk(self):
        with Shitty() as terminal:
            self.assertEqual(mode_query(terminal, 12, True), mode_reply(12, 2, True))
            terminal.write(b"\x1b[?12h")
            self.assertEqual(mode_query(terminal, 12, True), mode_reply(12, 2, True))

    @unittest.expectedFailure
    def test_decrqm_permanent_dec_private_modes(self):
        expected = ((3, 0), (8, 3), (67, 4), (1005, 4), (1015, 4), (1048, 1))
        with Shitty() as terminal:
            actual = tuple(
                mode_query(terminal, mode, True)
                for mode, _ in expected
            )
            self.assertEqual(
                actual,
                tuple(mode_reply(mode, state, True) for mode, state in expected),
            )

    def test_decrqm_save_cursor_reports_recognized_live_state(self):
        with Shitty() as terminal:
            self.assertEqual(
                mode_query(terminal, 1048, True),
                mode_reply(1048, 2, True),
            )
            terminal.write(b"\x1b[?1048h")
            self.assertEqual(
                mode_query(terminal, 1048, True),
                mode_reply(1048, 1, True),
            )

    def test_kitty_keyboard_stack_evicts_oldest_beyond_16(self):
        with Shitty() as terminal:
            for flags in range(1, 21):
                terminal.write(f"\x1b[>{flags}u".encode())
            terminal.write(b"\x1b[<16u")
            self.assertEqual(kitty_query(terminal), b"\x1b[?4u")
            terminal.write(b"\x1b[<u")
            self.assertEqual(kitty_query(terminal), b"\x1b[?0u")

    def test_kitty_keyboard_flags_are_screen_local(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[>5u")
            self.assertEqual(kitty_query(terminal), b"\x1b[?5u")
            terminal.write(b"\x1b[?1049h")
            self.assertEqual(kitty_query(terminal), b"\x1b[?0u")
            terminal.write(b"\x1b[>7u")
            self.assertEqual(kitty_query(terminal), b"\x1b[?7u")
            terminal.write(b"\x1b[?1049l")
            self.assertEqual(kitty_query(terminal), b"\x1b[?5u")

    def test_kitty_keyboard_excessive_pop_resets_flags(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[>5u\x1b[<10u")
            self.assertEqual(kitty_query(terminal), b"\x1b[?0u")

    def test_cpr_observes_each_preceding_cup(self):
        with Shitty(columns=80, rows=30) as terminal:
            terminal.write(
                b"aaa\x1b[3;4H\x1b[6n"
                b"bbb\x1b[6;8H\x1b[6n"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[3;4R\x1b[6;8R")

    def test_text_around_osc_handler_remains_ordered(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"hello world!\r\n"
                b"\x1b]2;some data\x07"
                b"second line"
            )
            self.assertEqual(
                terminal.snapshot().lines[:2],
                ["hello world!        ", "second line         "],
            )

    def test_text_around_dcs_handler_remains_ordered(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"hello world!\r\n"
                b"\x1bP$q\"q\x1b\\"
                b"second line"
            )
            self.assertEqual(terminal.read_input(), b"\x1bP1$r0\"q\x1b\\")
            self.assertEqual(
                terminal.snapshot().lines[:2],
                ["hello world!        ", "second line         "],
            )


if __name__ == "__main__":
    unittest.main()

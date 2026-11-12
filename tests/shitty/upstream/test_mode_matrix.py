# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


ANSI_DEFAULTS = {
    2: 2,
    4: 2,
    6: 2,
    12: 1,
    20: 2,
}

ANSI_FIXED_RESET = (1, 3, 5, 7, 10, 11, 13, 14, 15, 16, 17, 18, 19)

PRIVATE_DEFAULTS = {
    1: 2,
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    7: 1,
    8: 1,
    9: 2,
    12: 2,
    25: 1,
    40: 2,
    41: 2,
    42: 2,
    45: 2,
    47: 2,
    67: 2,
    69: 2,
    1000: 2,
    1001: 2,
    1002: 2,
    1003: 2,
    1004: 2,
    1005: 2,
    1006: 2,
    1007: 2,
    1015: 2,
    1016: 2,
    1034: 2,
    1036: 1,
    1039: 1,
    1045: 2,
    1047: 2,
    1049: 2,
    2004: 2,
    2026: 2,
    2031: 2,
    2048: 2,
}


def mode_query(mode, private=False):
    prefix = "?" if private else ""
    return f"\x1b[{prefix}{mode}$p".encode()


def mode_reply(mode, state, private=False):
    prefix = "?" if private else ""
    return f"\x1b[{prefix}{mode};{state}$y".encode()


def query(terminal, mode, private=False):
    terminal.write(mode_query(mode, private))
    return terminal.read_input()


class ModeMatrixTest(unittest.TestCase):
    def test_every_ansi_mode_reports_its_default(self):
        with Shitty() as terminal:
            for mode, state in ANSI_DEFAULTS.items():
                with self.subTest(mode=mode):
                    self.assertEqual(query(terminal, mode), mode_reply(mode, state))

    def test_fixed_ansi_modes_report_permanently_reset(self):
        with Shitty() as terminal:
            for mode in ANSI_FIXED_RESET:
                with self.subTest(mode=mode):
                    terminal.write(f"\x1b[{mode}h".encode())
                    self.assertEqual(query(terminal, mode), mode_reply(mode, 4))
                    terminal.write(f"\x1b[{mode}l".encode())
                    self.assertEqual(query(terminal, mode), mode_reply(mode, 4))

    def test_every_mutable_ansi_mode_reports_set_and_reset(self):
        for mode in ANSI_DEFAULTS:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[{mode}h".encode())
                    self.assertEqual(query(terminal, mode), mode_reply(mode, 1))
                    terminal.write(f"\x1b[{mode}l".encode())
                    self.assertEqual(query(terminal, mode), mode_reply(mode, 2))

    def test_every_private_mode_reports_its_default(self):
        with Shitty() as terminal:
            for mode, state in PRIVATE_DEFAULTS.items():
                with self.subTest(mode=mode):
                    self.assertEqual(
                        query(terminal, mode, True),
                        mode_reply(mode, state, True),
                    )

    def test_every_mutable_private_mode_reports_set_and_reset(self):
        mutable = tuple(
            mode for mode, state in PRIVATE_DEFAULTS.items()
            if state in (1, 2) and mode != 2
        )
        for mode in mutable:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    if mode == 3:
                        terminal.write(b"\x1b[?40h")
                    terminal.write(f"\x1b[?{mode}h".encode())
                    if mode == 2048:
                        terminal.read_input()
                    self.assertEqual(
                        query(terminal, mode, True), mode_reply(mode, 1, True)
                    )
                    terminal.write(f"\x1b[?{mode}l".encode())
                    self.assertEqual(
                        query(terminal, mode, True), mode_reply(mode, 2, True)
                    )

    def test_unknown_modes_report_unknown_and_do_not_change_known_modes(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[4h\x1b[?7l\x1b[9999h\x1b[?9999h")
            self.assertEqual(query(terminal, 9999), mode_reply(9999, 0))
            self.assertEqual(query(terminal, 9999, True), mode_reply(9999, 0, True))
            self.assertEqual(query(terminal, 4), mode_reply(4, 1))
            self.assertEqual(query(terminal, 7, True), mode_reply(7, 2, True))

    def test_mouse_tracking_and_encoding_modes_are_mutually_exclusive(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?9h\x1b[?1000h\x1b[?1002h\x1b[?1003h")
            for mode in (9, 1000, 1002):
                self.assertEqual(query(terminal, mode, True), mode_reply(mode, 2, True))
            self.assertEqual(query(terminal, 1003, True), mode_reply(1003, 1, True))

            terminal.write(b"\x1b[?1005h\x1b[?1015h\x1b[?1006h\x1b[?1016h")
            for mode in (1005, 1015, 1006):
                self.assertEqual(query(terminal, mode, True), mode_reply(mode, 2, True))
            self.assertEqual(query(terminal, 1016, True), mode_reply(1016, 1, True))

    def test_xtsave_and_xtrestore_cover_every_side_effect_free_mode(self):
        modes = (
            1, 4, 5, 6, 7, 12, 25, 42, 45, 67, 69,
            1004, 1007, 1034, 1036, 1039, 1045, 2004, 2026, 2031,
        )
        for mode in modes:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    initial = PRIVATE_DEFAULTS[mode]
                    terminal.write(f"\x1b[?{mode}s".encode())
                    terminal.write(
                        f"\x1b[?{mode}{'l' if initial == 1 else 'h'}".encode()
                    )
                    terminal.write(f"\x1b[?{mode}r".encode())
                    self.assertEqual(
                        query(terminal, mode, True),
                        mode_reply(mode, initial, True),
                    )

    def test_xtrestore_without_save_is_noop_and_save_is_one_level(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1h\x1b[?1r")
            self.assertEqual(query(terminal, 1, True), mode_reply(1, 1, True))
            terminal.write(b"\x1b[?1l\x1b[?1s\x1b[?1h\x1b[?1s\x1b[?1l\x1b[?1r")
            self.assertEqual(query(terminal, 1, True), mode_reply(1, 1, True))

    def test_deccolm_does_not_reset_unrelated_modes(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?40htext\x1b[?1h\x1b[4h\x1b[?3h")
            self.assertEqual(query(terminal, 3, True), mode_reply(3, 1, True))
            self.assertEqual(query(terminal, 1, True), mode_reply(1, 1, True))
            self.assertEqual(query(terminal, 4), mode_reply(4, 1))
            self.assertEqual(terminal.snapshot().lines[0].strip(), "")

    def test_mode_47_preserves_alternate_contents_between_switches(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?47h\x1b[Halt\x1b[?47l\x1b[?47h")
            self.assertEqual(terminal.snapshot().lines[0], "alt     ")
            terminal.write(b"\x1b[?47l")
            self.assertEqual(terminal.snapshot().lines[0], "primary ")

    def test_mode_1047_clears_alternate_contents_on_exit(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?1047halt\x1b[?1047l\x1b[?1047h")
            self.assertEqual(terminal.snapshot().lines[0], "        ")
            terminal.write(b"\x1b[?1047l")
            self.assertEqual(terminal.snapshot().lines[0], "primary ")

    def test_modes_1048_and_1049_save_cursor_with_distinct_screen_effects(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[?1048h\x1b[3;7H\x1b[?1048l")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

            terminal.write(b"P\x1b[?1049halt\x1b[?1049l")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 1))
            self.assertEqual(snapshot.cell(2, 1).char, "P")
            terminal.write(b"\x1b[?1049h")
            self.assertEqual(terminal.snapshot().lines, ["        "] * 3)

    def test_decstr_resets_modes_and_margins_without_clearing_active_screen(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(
                b"content"
                b"\x1b[2;4r\x1b[?69h\x1b[2;7s"
                b"\x1b[2;4;20h"
                b"\x1b[?1;4;5;6;12;42;45;67;1000;1004;1006;1007;"
                b"1034;1045;2004h"
                b"\x1b[?1036l"
                b"\x1b[!p"
            )
            self.assertEqual(terminal.snapshot().lines[0], "content ")
            for mode, state in ANSI_DEFAULTS.items():
                self.assertEqual(query(terminal, mode), mode_reply(mode, state))
            for mode in (1, 4, 5, 6, 12, 42, 45, 67, 1000, 1004,
                         1006, 1007, 1034, 1036, 1045, 2004):
                self.assertEqual(
                    query(terminal, mode, True),
                    mode_reply(mode, PRIVATE_DEFAULTS[mode], True),
                )
            self.assertEqual(
                query(terminal, 69, True),
                mode_reply(69, PRIVATE_DEFAULTS[69], True),
            )
            terminal.write(b"\x1b[?6hX")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_ris_resets_modes_saved_values_and_both_screen_buffers(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?1s\x1b[?1h\x1b[?47halt\x1bc\x1b[?1r")
            self.assertEqual(terminal.snapshot().lines, ["        "] * 2)
            self.assertEqual(query(terminal, 1, True), mode_reply(1, 2, True))
            terminal.write(b"\x1b[?47h")
            self.assertEqual(terminal.snapshot().lines, ["        "] * 2)


if __name__ == "__main__":
    unittest.main()

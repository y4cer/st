# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def query(terminal, mode, private=False):
    marker = "?" if private else ""
    terminal.write(f"\x1b[{marker}{mode}$p".encode())
    return terminal.read_input()


def reply(mode, state, private=False, csi=b"\x1b["):
    marker = "?" if private else ""
    return csi + f"{marker}{mode};{state}$y".encode()


class ResetAndModeInteractionTest(unittest.TestCase):
    def test_repeated_ansi_set_and_reset_are_idempotent(self):
        for mode in (2, 4, 12, 20):
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[{mode};{mode}h".encode())
                    self.assertEqual(query(terminal, mode), reply(mode, 1))
                    terminal.write(f"\x1b[{mode};{mode}l".encode())
                    self.assertEqual(query(terminal, mode), reply(mode, 2))

    def test_repeated_private_set_and_reset_are_idempotent(self):
        for mode in (1, 5, 6, 7, 12, 25, 42, 45, 67, 69,
                     1004, 1007, 1034, 1036, 1045, 2004):
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[?{mode};{mode}h".encode())
                    self.assertEqual(query(terminal, mode, True), reply(mode, 1, True))
                    terminal.write(f"\x1b[?{mode};{mode}l".encode())
                    self.assertEqual(query(terminal, mode, True), reply(mode, 2, True))

    def test_multi_parameter_ansi_commands_update_every_mode(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[2;4;12;20h")
            for mode in (2, 4, 12, 20):
                self.assertEqual(query(terminal, mode), reply(mode, 1))
            terminal.write(b"\x1b[2;4;12;20l")
            for mode in (2, 4, 12, 20):
                self.assertEqual(query(terminal, mode), reply(mode, 2))

    def test_multi_parameter_private_commands_update_every_mode(self):
        modes = (1, 5, 6, 12, 42, 45, 67, 69, 1004, 1007, 1034, 1045, 2004)
        with Shitty() as terminal:
            joined = ";".join(map(str, modes))
            terminal.write(f"\x1b[?{joined}h".encode())
            for mode in modes:
                self.assertEqual(query(terminal, mode, True), reply(mode, 1, True))
            terminal.write(f"\x1b[?{joined}l".encode())
            for mode in modes:
                self.assertEqual(query(terminal, mode, True), reply(mode, 2, True))

    def test_global_modes_survive_primary_alternate_transitions(self):
        for mode in (1, 5, 7, 12, 42, 45, 67, 69, 1004, 1007,
                     1034, 1036, 1045, 2004):
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[?{mode}h\x1b[?47h".encode())
                    self.assertEqual(query(terminal, mode, True), reply(mode, 1, True))
                    terminal.write(b"\x1b[?47l")
                    self.assertEqual(query(terminal, mode, True), reply(mode, 1, True))

    def test_xtsave_keeps_mode_entries_independent(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1;5s\x1b[?1;5h\x1b[?1r")
            self.assertEqual(query(terminal, 1, True), reply(1, 2, True))
            self.assertEqual(query(terminal, 5, True), reply(5, 1, True))
            terminal.write(b"\x1b[?5r")
            self.assertEqual(query(terminal, 5, True), reply(5, 2, True))

    def test_xtrestore_changes_only_listed_modes(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1;5s\x1b[?1;5h\x1b[?1r")
            self.assertEqual(query(terminal, 1, True), reply(1, 2, True))
            self.assertEqual(query(terminal, 5, True), reply(5, 1, True))

    def test_alt_escape_aliases_can_be_saved_independently(self):
        with Shitty() as terminal:
            terminal.write(
                b"\x1b[?1036s\x1b[?1036l\x1b[?1039s"
                b"\x1b[?1036r"
            )
            self.assertEqual(query(terminal, 1036, True), reply(1036, 1, True))
            terminal.write(b"\x1b[?1039r")
            self.assertEqual(query(terminal, 1039, True), reply(1039, 2, True))

    def test_xtrestore_mouse_protocol_replaces_current_protocol(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1000h\x1b[?1000s\x1b[?1003h\x1b[?1000r")
            self.assertEqual(query(terminal, 1000, True), reply(1000, 1, True))
            self.assertEqual(query(terminal, 1003, True), reply(1003, 2, True))

    def test_xtrestore_mouse_encoding_replaces_current_encoding(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1006h\x1b[?1006s\x1b[?1016h\x1b[?1006r")
            self.assertEqual(query(terminal, 1006, True), reply(1006, 1, True))
            self.assertEqual(query(terminal, 1016, True), reply(1016, 2, True))

    def test_decstr_resets_saved_cursor_to_home(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[2;3H\x1b7\x1b[!p\x1b[4;7H\x1b8")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_decstr_preserves_custom_tab_stops(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[3g\x1b[1;4H\x1bH\r\x1b[!p\tX")
            self.assertEqual(terminal.snapshot().cell(3, 0).char, "X")

    def test_decstr_preserves_scrollback_history(self):
        with Shitty(columns=8, rows=2, save_lines=4) as terminal:
            terminal.write(b"one\r\ntwo\r\nthree\x1b[!p")
            terminal.page_up()
            self.assertEqual(terminal.snapshot().lines[0], "one     ")

    def test_decstr_keeps_active_alternate_screen_and_contents(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"primary\x1b[?47h\x1b[Halt\x1b[!p")
            self.assertEqual(query(terminal, 47, True), reply(47, 1, True))
            self.assertEqual(terminal.snapshot().lines[0], "alt     ")
            terminal.write(b"\x1b[?47l")
            self.assertEqual(terminal.snapshot().lines[0], "primary ")

    def test_decstr_resets_attributes_for_subsequent_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;3;4;5;7;8;9;31;42mA\x1b[!pB")
            cell = terminal.snapshot().cell(1, 0)
            self.assertFalse(cell.bold)
            self.assertFalse(cell.italic)
            self.assertFalse(cell.underline)
            self.assertFalse(cell.blink)
            self.assertFalse(cell.inverse)
            self.assertFalse(cell.conceal)
            self.assertFalse(cell.strike)

    def test_decstr_resets_cursor_shape_visibility_and_blink(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[5 q\x1b[?12h\x1b[?25l\x1b[!p")
            snapshot = terminal.snapshot()
            self.assertNotEqual(snapshot.cursor_style, 0)
            self.assertEqual(query(terminal, 12, True), reply(12, 2, True))
            self.assertEqual(query(terminal, 25, True), reply(25, 1, True))

    def test_decstr_clears_selection_without_touching_text(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"selection")
            terminal.select_start(0, 0)
            terminal.select_update(4, 0)
            terminal.write(b"\x1b[!p")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.selection, (-1, -1, -1, -1))
            self.assertEqual(snapshot.lines[0], "selectio")

    def test_ris_restores_default_tab_stops(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"\x1b[3g\x1bc\tX")
            self.assertEqual(terminal.snapshot().cell(8, 0).char, "X")

    def test_decrqm_reply_uses_selected_eight_bit_controls(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b G")
            self.assertEqual(query(terminal, 7, True), reply(7, 1, True, b"\x9b"))
            terminal.write(b"\x1b F")
            self.assertEqual(query(terminal, 7, True), reply(7, 1, True))

    def test_decrqm_is_silent_in_vt52_mode(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?2l\x1b[?7$p")
            self.assertEqual(terminal.read_input(), b"")
            terminal.write(b"\x1b<")
            self.assertEqual(query(terminal, 2, True), b"")
            terminal.write(b"\x1b[64;1\"p")
            self.assertEqual(query(terminal, 2, True), reply(2, 1, True))


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class WindowsTerminalInputTest(unittest.TestCase):
    def test_terminal_input_named_keys(self):
        expected = {
            "TAB": b"\t",
            "BACKSPACE": b"\x7f",
            "UP": b"\x1b[A",
            "DOWN": b"\x1b[B",
            "RIGHT": b"\x1b[C",
            "LEFT": b"\x1b[D",
            "HOME": b"\x1b[H",
            "INSERT": b"\x1b[2~",
            "DELETE": b"\x1b[3~",
            "END": b"\x1b[F",
            "PAGE_UP": b"\x1b[5~",
            "PAGE_DOWN": b"\x1b[6~",
            "F1": b"\x1bOP",
            "F4": b"\x1bOS",
            "F5": b"\x1b[15~",
            "F12": b"\x1b[24~",
            "F20": b"\x1b[34~",
        }
        with Shitty(columns=8, rows=2) as terminal:
            for key, sequence in expected.items():
                with self.subTest(key=key):
                    terminal.key(key)
                    self.assertEqual(terminal.read_input(), sequence)

    def test_focus_events(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.focus(False)
            terminal.focus(True)
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x1b[?1004h")
            terminal.focus(False)
            terminal.focus(True)
            self.assertEqual(terminal.read_input(), b"\x1b[O\x1b[I")

    def test_modifier_key_matrix(self):
        modifier_codes = {
            1: 2,
            2: 5,
            3: 6,
            4: 3,
            5: 4,
            6: 7,
            7: 8,
        }
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>0;1m")
            for modifiers, code in modifier_codes.items():
                for key, final in (
                    ("UP", "A"),
                    ("HOME", "H"),
                    ("DELETE", "3~"),
                    ("F1", "1P"),
                    ("F20", "34~"),
                ):
                    with self.subTest(key=key, modifiers=modifiers):
                        terminal.key(key, modifiers)
                        if final[0].isdigit():
                            prefix, suffix = final[:-1], final[-1]
                            expected = (
                                f"\x1b[{prefix};{code}{suffix}"
                            ).encode()
                        else:
                            expected = f"\x1b[1;{code}{final}".encode()
                        self.assertEqual(terminal.read_input(), expected)

    def test_null_control_keys(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control(" ")
            terminal.frontend_control(" ", alt=True)
            self.assertEqual(terminal.read_input(), b"\0\x1b\0")

    def test_different_modifier_edge_cases(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.key("BACKSPACE")
            terminal.key("BACKSPACE", modifiers=2)
            terminal.key("BACKSPACE", modifiers=4)
            terminal.key("DELETE", modifiers=2)
            terminal.key("DELETE", modifiers=4)
            terminal.key("TAB", modifiers=1)
            terminal.frontend_control("/")
            terminal.frontend_control("/", shifted=True)
            terminal.frontend_control("/", alt=True)
            self.assertEqual(
                terminal.read_input(),
                b"\x7f\x7f\x1b\x7f"
                b"\x1b[3;5~\x1b[3;3~\x1b[Z"
                b"\x1f\x1b[27;6;127~\x1b\x1f",
            )

    def test_control_number_mapping(self):
        expected = {
            "1": b"\x1b[27;5;49~",
            "2": b"\0",
            "3": b"\x1b",
            "4": b"\x1c",
            "5": b"\x1d",
            "6": b"\x1e",
            "7": b"\x1f",
            "8": b"\x1b[27;5;127~",
            "9": b"\x1b[27;5;57~",
        }
        with Shitty(columns=8, rows=2) as terminal:
            for key, sequence in expected.items():
                with self.subTest(key=key):
                    terminal.frontend_control(key)
                    self.assertEqual(terminal.read_input(), sequence)

    def test_backarrow_key_mode(self):
        combinations = ((0, b"\x7f", b"\x08"),)
        with Shitty(columns=8, rows=2) as terminal:
            for modifiers, normal, backarrow in combinations:
                terminal.key("BACKSPACE", modifiers)
                self.assertEqual(terminal.read_input(), normal)
            terminal.write(b"\x1b[?67h")
            for modifiers, normal, backarrow in combinations:
                terminal.key("BACKSPACE", modifiers)
                self.assertEqual(terminal.read_input(), backarrow)

    def test_auto_repeat_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?8l")
            terminal.frontend_key_event(ord("A"), 1)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(ord("A"), 2)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(ord("A"), 0)
            self.assertEqual(terminal.read_input(), b"a")

            terminal.write(b"\x1b[?8h")
            terminal.frontend_key_event(ord("A"), 1)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(ord("A"), 2)
            terminal.frontend_text_event("a")
            terminal.frontend_key_event(ord("A"), 0)
            self.assertEqual(terminal.read_input(), b"aa")

    def test_send_c1_control_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b G")
            terminal.key("HOME")
            terminal.key("F1")
            self.assertEqual(terminal.read_input(), b"\x9bH\x8fP")

            terminal.write(b"\x1b F")
            terminal.key("HOME")
            terminal.key("F1")
            self.assertEqual(terminal.read_input(), b"\x1b[H\x1bOP")


if __name__ == "__main__":
    unittest.main()

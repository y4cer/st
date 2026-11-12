# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


MODIFIER_CODES = {
    1: 2,
    2: 5,
    3: 6,
    4: 3,
    5: 4,
    6: 7,
    7: 8,
}


FUNCTION_KEYS = {
    "F1": (b"\x1bOP", b"\x1b[1;{}P"),
    "F2": (b"\x1bOQ", b"\x1b[1;{}Q"),
    "F3": (b"\x1bOR", b"\x1b[1;{}R"),
    "F4": (b"\x1bOS", b"\x1b[1;{}S"),
    "F5": (b"\x1b[15~", b"\x1b[15;{}~"),
    "F6": (b"\x1b[17~", b"\x1b[17;{}~"),
    "F7": (b"\x1b[18~", b"\x1b[18;{}~"),
    "F8": (b"\x1b[19~", b"\x1b[19;{}~"),
    "F9": (b"\x1b[20~", b"\x1b[20;{}~"),
    "F10": (b"\x1b[21~", b"\x1b[21;{}~"),
    "F11": (b"\x1b[23~", b"\x1b[23;{}~"),
    "F12": (b"\x1b[24~", b"\x1b[24;{}~"),
    "F13": (b"\x1b[25~", b"\x1b[25;{}~"),
    "F14": (b"\x1b[26~", b"\x1b[26;{}~"),
    "F15": (b"\x1b[28~", b"\x1b[28;{}~"),
    "F16": (b"\x1b[29~", b"\x1b[29;{}~"),
    "F17": (b"\x1b[31~", b"\x1b[31;{}~"),
    "F18": (b"\x1b[32~", b"\x1b[32;{}~"),
    "F19": (b"\x1b[33~", b"\x1b[33;{}~"),
    "F20": (b"\x1b[34~", b"\x1b[34;{}~"),
}


CURSOR_KEYS = {
    "UP": b"A",
    "DOWN": b"B",
    "RIGHT": b"C",
    "LEFT": b"D",
    "HOME": b"H",
    "END": b"F",
}


EDITING_KEYS = {
    "INSERT": (2, b"\x1b[2~"),
    "DELETE": (3, b"\x1b[3~"),
    "PAGE_UP": (5, b"\x1b[5~"),
    "PAGE_DOWN": (6, b"\x1b[6~"),
}


KEYPAD_KEYS = {
    "KP_SPACE": (b" ", b" "),
    "KP_TAB": (b"\t", b"I"),
    "KP_ENTER": (b"\r", b"M"),
    "KP_STAR": (b"*", b"j"),
    "KP_PLUS": (b"+", b"k"),
    "KP_COMMA": (b",", b"l"),
    "KP_MINUS": (b"-", b"m"),
    "KP_DOT": (b".", b"n"),
    "KP_SLASH": (b"/", b"o"),
    "KP_INSERT": (b"0", b"p"),
    "KP_0": (b"0", b"p"),
    "KP_END": (b"1", b"q"),
    "KP_1": (b"1", b"q"),
    "KP_DOWN": (b"2", b"r"),
    "KP_2": (b"2", b"r"),
    "KP_PAGE_DOWN": (b"3", b"s"),
    "KP_3": (b"3", b"s"),
    "KP_LEFT": (b"4", b"t"),
    "KP_4": (b"4", b"t"),
    "KP_BEGIN": (b"5", b"u"),
    "KP_5": (b"5", b"u"),
    "KP_RIGHT": (b"6", b"v"),
    "KP_6": (b"6", b"v"),
    "KP_HOME": (b"7", b"w"),
    "KP_7": (b"7", b"w"),
    "KP_UP": (b"8", b"x"),
    "KP_8": (b"8", b"x"),
    "KP_PAGE_UP": (b"9", b"y"),
    "KP_9": (b"9", b"y"),
    "KP_EQUAL": (b"=", b"X"),
}


class LegacyKeyboardMatrixTest(unittest.TestCase):
    def test_all_function_keys_in_unmodified_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            for name, (expected, _) in FUNCTION_KEYS.items():
                with self.subTest(key=name):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), expected)

    def test_all_function_keys_with_every_modifier(self):
        with Shitty(columns=8, rows=2) as terminal:
            for name, (_, template) in FUNCTION_KEYS.items():
                for modifiers, code in MODIFIER_CODES.items():
                    with self.subTest(key=name, modifiers=modifiers):
                        terminal.key(name, modifiers)
                        self.assertEqual(
                            terminal.read_input(),
                            template.replace(b"{}", str(code).encode()),
                        )

    def test_cursor_keys_in_normal_and_application_modes(self):
        with Shitty(columns=8, rows=2) as terminal:
            for name, final in CURSOR_KEYS.items():
                with self.subTest(key=name, mode="normal"):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), b"\x1b[" + final)

            terminal.write(b"\x1b[?1h")
            for name, final in CURSOR_KEYS.items():
                with self.subTest(key=name, mode="application"):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), b"\x1bO" + final)

    def test_cursor_keys_with_every_modifier_in_both_modes(self):
        for application in (False, True):
            with self.subTest(application=application):
                with Shitty(columns=8, rows=2) as terminal:
                    if application:
                        terminal.write(b"\x1b[?1h")
                    for name, final in CURSOR_KEYS.items():
                        for modifiers, code in MODIFIER_CODES.items():
                            with self.subTest(key=name, modifiers=modifiers):
                                terminal.key(name, modifiers)
                                self.assertEqual(
                                    terminal.read_input(),
                                    b"\x1b[1;" + str(code).encode() + final,
                                )

    def test_editing_keys_with_and_without_every_modifier(self):
        with Shitty(columns=8, rows=2) as terminal:
            for name, (number, unmodified) in EDITING_KEYS.items():
                with self.subTest(key=name, modifiers=0):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), unmodified)
            terminal.write(b"\x1b[>0;1m")
            for name, (number, _) in EDITING_KEYS.items():
                for modifiers, code in MODIFIER_CODES.items():
                    with self.subTest(key=name, modifiers=modifiers):
                        terminal.key(name, modifiers)
                        self.assertEqual(
                            terminal.read_input(),
                            f"\x1b[{number};{code}~".encode(),
                        )

    def test_complete_numeric_keypad(self):
        with Shitty(columns=8, rows=2) as terminal:
            for name, (expected, _) in KEYPAD_KEYS.items():
                with self.subTest(key=name):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), expected)

    def test_complete_application_keypad(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b=")
            for name, (_, final) in KEYPAD_KEYS.items():
                with self.subTest(key=name):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), b"\x1bO" + final)

    def test_application_keypad_with_every_modifier_when_enabled(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b=\x1b[>3;1m")
            for name, (_, final) in KEYPAD_KEYS.items():
                for modifiers, code in MODIFIER_CODES.items():
                    with self.subTest(key=name, modifiers=modifiers):
                        terminal.key(name, modifiers)
                        self.assertEqual(
                            terminal.read_input(),
                            b"\x1bO" + str(code).encode() + final,
                        )

    def test_pf_keys_in_ansi_application_and_vt52_modes(self):
        for prefix in (b"", b"\x1b=", b"\x1b[?2l\x1b="):
            with self.subTest(mode=prefix):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(prefix)
                    for number, final in enumerate(b"PQRS", 1):
                        terminal.key(f"KP_F{number}")
                        expected_prefix = (
                            b"\x1b" if b"?2l" in prefix else b"\x1bO"
                        )
                        self.assertEqual(
                            terminal.read_input(), expected_prefix + bytes([final])
                        )

    def test_complete_vt52_cursor_and_application_keypad(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?2l")
            for name, final in CURSOR_KEYS.items():
                with self.subTest(key=name, group="cursor"):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), b"\x1b" + final)

            terminal.write(b"\x1b=")
            for name, (_, final) in KEYPAD_KEYS.items():
                with self.subTest(key=name, group="keypad"):
                    terminal.key(name)
                    self.assertEqual(terminal.read_input(), b"\x1b?" + final)

    def test_keypad_mode_can_switch_repeatedly(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.key("KP_1")
            terminal.write(b"\x1b=")
            terminal.key("KP_1")
            terminal.write(b"\x1b>")
            terminal.key("KP_1")
            self.assertEqual(terminal.read_input(), b"1\x1bOq1")

    def test_modifier_resources_disable_and_reenable_key_groups(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>1;0m\x1b[>2;0m")
            terminal.key("UP", modifiers=1)
            terminal.key("F5", modifiers=1)
            self.assertEqual(terminal.read_input(), b"\x1b[A\x1b[15~")

            terminal.write(b"\x1b[>1;1m\x1b[>2;1m")
            terminal.key("UP", modifiers=1)
            terminal.key("F5", modifiers=1)
            self.assertEqual(
                terminal.read_input(), b"\x1b[1;2A\x1b[15;2~"
            )


if __name__ == "__main__":
    unittest.main()

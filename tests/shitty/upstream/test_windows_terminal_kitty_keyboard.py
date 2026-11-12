# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import ast
from pathlib import Path
import re
import unittest

from harness import Shitty


SOURCE = (
    Path(__file__).parent
    / "windows_terminal"
    / "upstream"
    / "KittyKeyboardProtocol.cpp"
)

FLAG_VALUES = {
    "D": 1,
    "E": 2,
    "A": 4,
    "K": 8,
    "T": 16,
}

STATE_VALUES = {
    "Shift": 1,
    "Alt": 2,
    "Ctrl": 4,
    "SHIFT_PRESSED": 1,
    "LEFT_ALT_PRESSED": 2,
    "RIGHT_ALT_PRESSED": 2,
    "LEFT_CTRL_PRESSED": 4,
    "RIGHT_CTRL_PRESSED": 4,
    "CAPSLOCK_ON": 64,
    "NUMLOCK_ON": 128,
    "ENHANCED_KEY": 256,
}

FRONTEND_MODIFIERS = {
    1: 1,
    2: 4,
    4: 2,
    64: 16,
    128: 32,
}

ROW = re.compile(
    r'^\s*\{\s*L"(?P<name>(?:\\.|[^"\\])*)",\s*'
    r'L"(?P<expected>(?:\\.|[^"\\])*)",\s*'
    r"(?P<flags>.*?),\s*(?P<down>true|false),\s*"
    r"(?P<vk>.*?),\s*(?P<scan>.*?),\s*"
    r"(?P<char>.*?),\s*(?P<state>.*?)\s*\},"
)


def expression_value(expression, values):
    expression = expression.strip()
    if expression == "0":
        return 0
    result = 0
    for token in expression.split("|"):
        result |= values[token.strip()]
    return result


def literal_value(token):
    token = token.strip()
    if token.startswith("L'"):
        token = token[1:]
    if token.startswith("'"):
        return ord(ast.literal_eval(token))
    return int(token, 0)


def decode_literal(contents):
    return ast.literal_eval(f'"{contents}"').encode("latin1")


def load_cases():
    result = []
    for line in SOURCE.read_text().splitlines():
        match = ROW.match(line)
        if match is None:
            continue
        result.append(
            {
                "name": decode_literal(match["name"]).decode(),
                "expected": decode_literal(match["expected"]),
                "flags": expression_value(match["flags"], FLAG_VALUES),
                "down": match["down"] == "true",
                "vk": match["vk"].strip(),
                "scan": literal_value(match["scan"]),
                "char": literal_value(match["char"]),
                "state": expression_value(match["state"], STATE_VALUES),
            }
        )
    return result


def kitty_modifiers(state):
    return state & 0xFF


def frontend_modifiers(state):
    result = 0
    for kitty_bit, frontend_bit in FRONTEND_MODIFIERS.items():
        if state & kitty_bit:
            result |= frontend_bit
    return result


def printable_vk(vk):
    if not (vk.startswith("'") and vk.endswith("'")):
        return None
    return ord(ast.literal_eval(vk))


def shifted_codepoint(key):
    if ord("A") <= key <= ord("Z"):
        return key
    if key == ord("1"):
        return ord("!")
    return 0


def primary_codepoint(key):
    if ord("A") <= key <= ord("Z"):
        return key + ord("a") - ord("A")
    return key


def named_key(case):
    vk = case["vk"]
    enhanced = bool(case["state"] & STATE_VALUES["ENHANCED_KEY"])
    fixed = {
        "VK_RETURN": "KP_ENTER" if enhanced else "RETURN",
        "VK_TAB": "TAB",
        "VK_BACK": "BACKSPACE",
        "VK_CAPITAL": "CAPS_LOCK",
        "VK_NUMLOCK": "NUM_LOCK",
        "VK_SCROLL": "SCROLL_LOCK",
        "VK_PAUSE": "PAUSE",
        "VK_SNAPSHOT": "PRINT",
        "VK_APPS": "MENU",
        "VK_LWIN": "LEFT_SUPER",
        "VK_RWIN": "RIGHT_SUPER",
        "VK_CLEAR": "CLEAR",
        "VK_MEDIA_PLAY_PAUSE": "MEDIA_PLAY_PAUSE",
        "VK_MEDIA_STOP": "MEDIA_STOP",
        "VK_MEDIA_NEXT_TRACK": "MEDIA_TRACK_NEXT",
        "VK_MEDIA_PREV_TRACK": "MEDIA_TRACK_PREVIOUS",
        "VK_VOLUME_DOWN": "VOLUME_DOWN",
        "VK_VOLUME_UP": "VOLUME_UP",
        "VK_VOLUME_MUTE": "VOLUME_MUTE",
        "VK_DECIMAL": "KP_DOT",
        "VK_DIVIDE": "KP_SLASH",
        "VK_MULTIPLY": "KP_STAR",
        "VK_SUBTRACT": "KP_MINUS",
        "VK_ADD": "KP_PLUS",
    }
    if vk in fixed:
        return fixed[vk]
    if vk == "VK_SHIFT":
        return "RIGHT_SHIFT" if case["scan"] == 0x36 else "LEFT_SHIFT"
    if vk == "VK_CONTROL":
        return "RIGHT_CONTROL" if enhanced else "LEFT_CONTROL"
    if vk == "VK_MENU":
        return "RIGHT_ALT" if enhanced else "LEFT_ALT"
    match = re.fullmatch(r"VK_NUMPAD([0-9])", vk)
    if match:
        return "KP_" + match.group(1)
    match = re.fullmatch(r"VK_F([0-9]+)", vk)
    if match:
        return "F" + match.group(1)
    navigation = {
        "VK_HOME": "HOME",
        "VK_END": "END",
        "VK_INSERT": "INSERT",
        "VK_DELETE": "DELETE",
        "VK_PRIOR": "PAGE_UP",
        "VK_NEXT": "PAGE_DOWN",
        "VK_UP": "UP",
        "VK_DOWN": "DOWN",
        "VK_LEFT": "LEFT",
        "VK_RIGHT": "RIGHT",
    }
    if vk in navigation:
        name = navigation[vk]
        return name if enhanced else "KP_" + name
    raise AssertionError(f"unmapped upstream key {vk}")


def send_frontend_printable(terminal, case, key, action):
    modifiers = frontend_modifiers(case["state"])
    terminal.frontend_key_event(key, action, modifiers=modifiers)
    if (
        action != 0
        and case["char"] != 0
        and not (case["state"] & 4)
    ):
        terminal.frontend_text_event(case["char"], modifiers=modifiers)


def process_case(terminal, case):
    terminal.write(f"\x1b[={case['flags']}u".encode())
    event = 1 if case["down"] else 3
    key = printable_vk(case["vk"])
    if key is not None:
        if case["flags"] & FLAG_VALUES["K"]:
            use_frontend = (
                case["flags"] & FLAG_VALUES["T"]
                and case["state"] & (4 | 8)
            )
            if use_frontend:
                send_frontend_printable(
                    terminal, case, key, 1 if case["down"] else 0
                )
            else:
                terminal.kitty_key(
                    primary_codepoint(key),
                    shifted=(
                        shifted_codepoint(key)
                        if case["state"] & 1
                        else 0
                    ),
                    modifiers=kitty_modifiers(case["state"]),
                    event=event,
                )
        else:
            send_frontend_printable(
                terminal, case, key, 1 if case["down"] else 0
            )
        return
    if case["vk"] == "VK_ESCAPE":
        terminal.kitty_key(
            27,
            modifiers=kitty_modifiers(case["state"]),
            event=event,
        )
        return
    terminal.kitty_special(
        named_key(case),
        modifiers=kitty_modifiers(case["state"]),
        event=event,
    )


class WindowsTerminalKittyKeyboardTest(unittest.TestCase):
    def test_all_key_press_rows(self):
        cases = load_cases()
        self.assertEqual(len(cases), 129)
        with Shitty(columns=8, rows=2) as terminal:
            for case in cases:
                with self.subTest(case=case["name"]):
                    process_case(terminal, case)
                    self.assertEqual(
                        terminal.read_input(), case["expected"]
                    )

    def test_key_repeat_events(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            for action, expected in (
                (1, b"\x1b[97u"),
                (2, b"\x1b[97;1:2u"),
                (2, b"\x1b[97;1:2u"),
                (0, b"\x1b[97;1:3u"),
                (1, b"\x1b[97u"),
            ):
                terminal.frontend_key_event(ord("A"), action)
                if action != 0:
                    terminal.frontend_text_event("a")
                self.assertEqual(terminal.read_input(), expected)

    def test_key_repeat_with_modifiers(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            for action, expected in (
                (1, b"\x1b[97;2u"),
                (2, b"\x1b[97;2:2u"),
            ):
                terminal.frontend_key_event(
                    ord("A"), action, modifiers=1
                )
                terminal.frontend_text_event("A", modifiers=1)
                self.assertEqual(terminal.read_input(), expected)

    def test_key_repeat_reset_on_different_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[=10u")
            for key, expected in (
                ("A", b"\x1b[97u"),
                ("B", b"\x1b[98u"),
                ("A", b"\x1b[97u"),
            ):
                terminal.frontend_key_event(ord(key), 1)
                terminal.frontend_text_event(key.lower())
                self.assertEqual(terminal.read_input(), expected)


if __name__ == "__main__":
    unittest.main()

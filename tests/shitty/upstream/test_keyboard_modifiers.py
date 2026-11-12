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


def expected_control(key, shifted=False):
    if ord("A") <= key <= ord("Z"):
        return key - ord("A") + 1
    aliases = {
        ord(" "): 0,
        ord("2"): 0,
        ord("3"): 27,
        ord("["): 27,
        ord("4"): 28,
        ord("\\"): 28,
        ord("5"): 29,
        ord("]"): 29,
        ord("6"): 30,
        ord("7"): 31,
        ord("8"): 127,
    }
    if key == ord("-"):
        return 31 if shifted else key
    if key == ord("/"):
        return 127 if shifted else 31
    return aliases.get(key, key)


def expected_modify_other(key, modifiers, level):
    code = MODIFIER_CODES[modifiers]
    exempt = b"!#$%&*()-+=?.,:;<>'\""
    encode = (
        (level == 2 and key not in exempt)
        or (level == 2 and bool(modifiers & 6))
        or (level == 1 and bool(modifiers & 2) and key > ord(" "))
    )
    if encode:
        return f"\x1b[27;{code};{key}~".encode()
    if modifiers & 4:
        return b"\x1b" + bytes([key])
    return bytes([key])


class KeyboardModifierTest(unittest.TestCase):
    def test_control_mapping_covers_every_printable_ascii_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            for key in range(32, 127):
                for shifted in (False, True):
                    with self.subTest(key=key, shifted=shifted):
                        self.assertEqual(
                            terminal.control_character(key, shifted),
                            expected_control(key, shifted),
                        )

    def test_frontend_control_letters_emit_c0_bytes(self):
        with Shitty(columns=8, rows=2) as terminal:
            for key in range(ord("A"), ord("Z") + 1):
                terminal.frontend_control(key)
            self.assertEqual(terminal.read_input(), bytes(range(1, 27)))

    def test_frontend_control_alt_and_shift_combinations(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.frontend_control("A", alt=True)
            terminal.frontend_control("A", shifted=True)
            terminal.frontend_control("/", shifted=True)
            self.assertEqual(
                terminal.read_input(), b"\x1b\x01\x01\x1b[27;6;127~"
            )

    def test_alt_modes_cover_escape_unicode_and_raw_eight_bit_forms(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.char("a", modifiers=4)
            terminal.write(b"\x1b[?1036l")
            terminal.char("a", modifiers=4)
            terminal.write(b"\x1b[?1034h")
            terminal.char("a", modifiers=4)
            terminal.write(b"\x1b[?1034l\x1b[?1036h")
            terminal.char("a", modifiers=4)
            self.assertEqual(
                terminal.read_input(), b"\x1ba\xc3\xa1\xe1\x1ba"
            )

    def test_modify_other_keys_levels_cover_ascii_and_all_modifiers(self):
        for level in (0, 1, 2):
            with self.subTest(level=level):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(f"\x1b[>4;{level}m".encode())
                    for key in range(32, 127):
                        for modifiers in MODIFIER_CODES:
                            with self.subTest(key=key, modifiers=modifiers):
                                terminal.char(key, modifiers)
                                self.assertEqual(
                                    terminal.read_input(),
                                    expected_modify_other(
                                        key, modifiers, level
                                    ),
                                )

    def test_modify_other_keys_two_encodes_control_boundaries(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[>4;2m")
            for key in (0, 31, 32, 127, 255):
                terminal.char(key, modifiers=2)
                expected_key = {0: ord(" "), 31: ord("/")}.get(key, key)
                self.assertEqual(
                    terminal.read_input(),
                    f"\x1b[27;5;{expected_key}~".encode(),
                )

    def test_modify_other_keys_rejects_levels_above_two(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[>4;2m\x1b[>4;3m\x1b[?4m"
                b"\x1b[>4;4m\x1b[?4m"
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b[>4;2m\x1b[>4;2m"
            )

    def test_other_modifier_resources_accept_and_report_zero_through_four(self):
        with Shitty(columns=8, rows=2) as terminal:
            for resource in (0, 1, 2, 3, 6, 7):
                for value in range(5):
                    terminal.write(
                        f"\x1b[>{resource};{value}m\x1b[?{resource}m".encode()
                    )
                    self.assertEqual(
                        terminal.read_input(),
                        f"\x1b[>{resource};{value}m".encode(),
                    )


if __name__ == "__main__":
    unittest.main()

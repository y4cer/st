# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


# Every mode the harness inspector distinguishes, exercised through the
# real set/reset sequences: the DECRQM matrix checks what the terminal
# reports, this one checks the state the inspector reads directly.
PRIVATE_MODES = (
    1,
    4,
    5,
    6,
    7,
    8,
    12,
    25,
    40,
    41,
    42,
    45,
    47,
    66,
    67,
    69,
    95,
    1004,
    1007,
    1034,
    1036,
    1039,
    1045,
    1047,
    2004,
    2026,
    2027,
    2031,
    2048,
    5522,
)

# One tracking mode and one encoding at a time; each still flips its own
# inspector answer.
MOUSE_MODES = (9, 1000, 1001, 1002, 1003)
MOUSE_ENCODINGS = (1005, 1006, 1015, 1016)

ANSI_MODES = (4, 6, 12, 20)


class ModeInspectionTest(unittest.TestCase):
    def test_private_modes_flip_the_inspector(self):
        preludes = {
            # DECNCSM only exists at VT500 conformance.
            95: b"\x1b[65\"p",
        }
        for mode in PRIVATE_MODES:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(preludes.get(mode, b""))
                    terminal.write(f"\x1b[?{mode}h".encode())
                    self.assertTrue(terminal.private_mode(mode))
                    terminal.write(f"\x1b[?{mode}l".encode())
                    self.assertFalse(terminal.private_mode(mode))

    def test_column_mode_needs_the_enabling_mode(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?40h\x1b[?3h")
            self.assertTrue(terminal.private_mode(3))
            self.assertTrue(terminal.private_mode(40))
            terminal.write(b"\x1b[?3l")
            self.assertFalse(terminal.private_mode(3))

    def test_mouse_tracking_modes_flip_the_inspector(self):
        for mode in MOUSE_MODES:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[?{mode}h".encode())
                    self.assertTrue(terminal.private_mode(mode))
                    terminal.write(f"\x1b[?{mode}l".encode())
                    self.assertFalse(terminal.private_mode(mode))

    def test_mouse_encodings_flip_the_inspector(self):
        for mode in MOUSE_ENCODINGS:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[?{mode}h".encode())
                    self.assertTrue(terminal.private_mode(mode))
                    terminal.write(f"\x1b[?{mode}l".encode())
                    self.assertFalse(terminal.private_mode(mode))

    def test_alternate_screen_aliases_share_state(self):
        with Shitty() as terminal:
            terminal.write(b"\x1b[?1049h")
            self.assertTrue(terminal.private_mode(47))
            self.assertTrue(terminal.private_mode(1047))
            terminal.write(b"\x1b[?1049l")
            self.assertFalse(terminal.private_mode(47))

    def test_ansi_modes_flip_the_inspector(self):
        for mode in ANSI_MODES:
            with self.subTest(mode=mode):
                with Shitty() as terminal:
                    terminal.write(f"\x1b[{mode}h".encode())
                    self.assertTrue(terminal.ansi_mode(mode))
                    terminal.write(f"\x1b[{mode}l".encode())
                    self.assertFalse(terminal.ansi_mode(mode))

    def test_unknown_modes_read_reset(self):
        with Shitty() as terminal:
            self.assertFalse(terminal.private_mode(31337))
            self.assertFalse(terminal.ansi_mode(31337))


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


COORDINATES = (
    (0, 0),
    (0, 1),
    (1, 1),
    (2, 2),
    (94, 94),
    (95, 95),
    (96, 96),
    (127, 127),
    (128, 128),
    (32734, 32734),
    (32735, 32735),
)

# Windows key-state inputs translated to Shitty's generic shift/alt/control
# bits, in the original data-source order.
MODIFIERS = (0, 1, 4, 2, 6)

# Left, middle and right, each pressed and released.
BUTTONS = (
    (1, 0),
    (1, 1),
    (2, 0),
    (2, 1),
    (3, 0),
    (3, 1),
)


def modifier_code(modifiers):
    return (
        (4 if modifiers & 1 else 0)
        + (8 if modifiers & 2 else 0)
        + (16 if modifiers & 4 else 0)
    )


def button_code(button, event, modifiers):
    base = 3 if event == 1 else button - 1
    return base + modifier_code(modifiers)


def legacy_expected(encoding, button, event, modifiers, x, y):
    maximum = 223 if encoding == 0 else 2015
    column = min(x + 1, maximum)
    row = min(y + 1, maximum)
    values = (32 + button_code(button, event, modifiers),
              32 + column, 32 + row)
    if encoding == 0:
        return b"\x1b[M" + bytes(values)
    return b"\x1b[M" + "".join(map(chr, values)).encode()


def sgr_expected(button, event, modifiers, x, y):
    code = button - 1 + modifier_code(modifiers)
    final = "m" if event == 1 else "M"
    return f"\x1b[<{code};{x + 1};{y + 1}{final}".encode()


class WindowsTerminalMouseTest(unittest.TestCase):
    def test_default_mode_matrix(self):
        with Shitty(columns=8, rows=2) as terminal:
            for button, event in BUTTONS:
                for modifiers in MODIFIERS:
                    for x, y in COORDINATES:
                        with self.subTest(
                            button=button,
                            event=event,
                            modifiers=modifiers,
                            x=x,
                            y=y,
                        ):
                            self.assertEqual(
                                terminal.mouse_encode(
                                    0, event, modifiers, 0,
                                    button, x + 1, y + 1,
                                ),
                                legacy_expected(
                                    0, button, event, modifiers, x, y
                                ),
                            )

    def test_utf8_mode_matrix(self):
        with Shitty(columns=8, rows=2) as terminal:
            for button, event in BUTTONS:
                for modifiers in MODIFIERS:
                    for x, y in COORDINATES:
                        with self.subTest(
                            button=button,
                            event=event,
                            modifiers=modifiers,
                            x=x,
                            y=y,
                        ):
                            self.assertEqual(
                                terminal.mouse_encode(
                                    1, event, modifiers, 0,
                                    button, x + 1, y + 1,
                                ),
                                legacy_expected(
                                    1, button, event, modifiers, x, y
                                ),
                            )

    def test_sgr_mode_matrix(self):
        with Shitty(columns=8, rows=2) as terminal:
            for button, event in BUTTONS:
                for modifiers in MODIFIERS:
                    for x, y in COORDINATES:
                        with self.subTest(
                            button=button,
                            event=event,
                            modifiers=modifiers,
                            x=x,
                            y=y,
                        ):
                            self.assertEqual(
                                terminal.mouse_encode(
                                    2, event, modifiers, 0,
                                    button, x + 1, y + 1,
                                ),
                                sgr_expected(
                                    button, event, modifiers, x, y
                                ),
                            )

    def test_sgr_motion_requires_tracking_policy_outside_encoder(self):
        with Shitty(columns=8, rows=2) as terminal:
            for modifiers in MODIFIERS:
                for x, y in COORDINATES:
                    expected = (
                        f"\x1b[<{35 + modifier_code(modifiers)};"
                        f"{x + 1};{y + 1}M"
                    ).encode()
                    self.assertEqual(
                        terminal.mouse_encode(
                            2, 2, modifiers, 0, 0, x + 1, y + 1
                        ),
                        expected,
                    )

    def test_scroll_wheel_matrix(self):
        with Shitty(columns=8, rows=2) as terminal:
            for delta in (-120, 120, -10000, 32736):
                button = 4 if delta > 0 else 5
                for modifiers in MODIFIERS:
                    for x, y in COORDINATES:
                        with self.subTest(
                            delta=delta,
                            modifiers=modifiers,
                            x=x,
                            y=y,
                        ):
                            code = (
                                64 + (button - 4)
                                + modifier_code(modifiers)
                            )
                            expected = (
                                f"\x1b[<{code};{x + 1};{y + 1}M"
                            ).encode()
                            self.assertEqual(
                                terminal.mouse_encode(
                                    2, 0, modifiers, 0,
                                    button, x + 1, y + 1,
                                ),
                                expected,
                            )

    def test_alternate_scroll_vertical_and_horizontal(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[?1049h\x1b[?1007h")
            terminal.scroll(0, 1)
            terminal.scroll(0, -1)
            terminal.scroll(1, 0)
            terminal.scroll(-1, 0)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[A\x1b[B\x1b[C\x1b[D",
            )

            terminal.write(b"\x1b[?1h")
            terminal.scroll(0, 1)
            terminal.scroll(0, -1)
            terminal.scroll(1, 0)
            terminal.scroll(-1, 0)
            self.assertEqual(
                terminal.read_input(),
                b"\x1bOA\x1bOB\x1bOC\x1bOD",
            )

            terminal.write(b"\x1b[?1007l")
            terminal.scroll(0, 1)
            self.assertEqual(terminal.read_input(), b"")


if __name__ == "__main__":
    unittest.main()

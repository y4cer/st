# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class MouseProtocolTest(unittest.TestCase):
    def test_highlight_tracking_reports_same_and_extended_ranges(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?1001h\x1b[1;2;1;1;4T")
            terminal.highlight_release(2, 1, 2, 1)
            self.assertEqual(terminal.read_input(), b"\x1b[t\"!")

            terminal.write(b"\x1b[1;2;1;1;4T")
            terminal.highlight_release(5, 3, 5, 3)
            self.assertEqual(terminal.read_input(), b"\x1b[T\"!%#%#")

    def test_highlight_tracking_uses_sgr_coordinates(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?1001h\x1b[?1006h\x1b[1;2;1;1;4T")
            terminal.highlight_release(5, 3, 5, 3)
            self.assertEqual(
                terminal.read_input(), b"\x1b[<2;1;5;3;5;3T"
            )

    def test_dec_locator_query_buttons_pixels_and_one_shot(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[1;3'{\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[1;0;2;4;0&w")
            terminal.locator_button(1, True)
            terminal.locator_button(1, False)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[2;4;2;4;0&w\x1b[3;0;2;4;0&w",
            )

            terminal.write(b"\x1b[2;1'z\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[1;0;20;40;0&w")
            terminal.write(b"\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")
    def test_default_encoding_press_and_release(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(0, 0, 0, 0, 1, 2, 3),
                b'\x1b[M "#',
            )
            self.assertEqual(
                terminal.mouse_encode(0, 1, 0, 0, 1, 2, 3),
                b'\x1b[M#"#',
            )

    def test_utf8_encoding_supports_large_coordinates(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(1, 0, 0, 0, 1, 200, 300),
                b"\x1b[M \xc3\xa8\xc5\x8c",
            )

    def test_sgr_encoding_distinguishes_press_release_and_motion(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(2, 0, 7, 0, 1, 12, 7),
                b"\x1b[<28;12;7M",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 1, 0, 0, 3, 12, 7),
                b"\x1b[<2;12;7m",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 2, 0, 1, 0, 12, 7),
                b"\x1b[<32;12;7M",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 2, 0, 0, 0, 12, 7),
                b"\x1b[<35;12;7M",
            )

    def test_sgr_wheel_and_extended_buttons(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(2, 0, 0, 0, 4, 1, 1),
                b"\x1b[<64;1;1M",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 0, 0, 0, 8, 1, 1),
                b"\x1b[<128;1;1M",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 0, 0, 0, 10, 1, 1),
                b"\x1b[<130;1;1M",
            )
            self.assertEqual(
                terminal.mouse_encode(2, 0, 0, 0, 11, 1, 1),
                b"\x1b[<131;1;1M",
            )

    def test_sgr_pixel_encoding_and_mode(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?1016h\x1b[?1016$p")
            self.assertEqual(terminal.state()[1], 4)
            self.assertEqual(terminal.read_input(), b"\x1b[?1016;1$y")
            self.assertEqual(
                terminal.mouse_encode(4, 0, 0, 0, 1, 321, 123),
                b"\x1b[<0;321;123M",
            )

    def test_legacy_coordinate_encodings_are_clamped(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(0, 0, 0, 0, 1, 999, -4),
                b"\x1b[M \xff!",
            )
            self.assertEqual(
                terminal.mouse_encode(1, 0, 0, 0, 1, 9999, -4),
                b"\x1b[M \xdf\xbf!",
            )

    def test_urxvt_encoding(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(3, 0, 4, 0, 2, 9, 4),
                b"\x1b[49;9;4M",
            )

    def test_invalid_button_is_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.mouse_encode(2, 0, 0, 0, 12, 1, 1),
                b"",
            )

    def test_dec_locator_filter_rectangle_reports_on_exit(self):
        with Shitty(columns=10, rows=4) as terminal:
            # One-shot pixel locator with a filter rectangle around the
            # pointer: leaving the rectangle reports event 10 and the
            # one-shot disarms the locator entirely.
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[2;1'z\x1b[10;10;30;60'w")
            self.assertEqual(terminal.read_input(), b"")
            terminal.locator_position(6, 3, 80, 25)
            self.assertEqual(terminal.read_input(), b"\x1b[10;0;25;80;0&w")
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")

    def test_dec_locator_filter_survives_in_continuous_mode(self):
        with Shitty(columns=10, rows=4) as terminal:
            # The same exit report in cell units with a persistent
            # locator: the filter disarms, the locator stays enabled.
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[1;1;3;6'w")
            terminal.locator_position(8, 4, 80, 40)
            self.assertEqual(terminal.read_input(), b"\x1b[10;0;4;8;0&w")
            terminal.write(b"\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[1;0;4;8;0&w")


    def test_highlight_tracking_with_a_zero_start_is_disarmed(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.write(b"\x1b[?1001h\x1b[0;2;1;1;4T")
            terminal.highlight_release(2, 1, 2, 1)
            self.assertEqual(terminal.read_input(), b"")


    def test_dec_locator_button_reports_can_be_switched_off(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[1;3'{\x1b[4'{")
            terminal.locator_button(1, True)
            terminal.locator_button(1, False)
            self.assertEqual(terminal.read_input(), b"\x1b[2;4;2;4;0&w")
            terminal.write(b"\x1b[2'{")
            terminal.locator_button(1, True)
            terminal.locator_button(1, False)
            self.assertEqual(terminal.read_input(), b"")


    def test_one_shot_locator_disarms_after_a_button_report(self):
        with Shitty(columns=10, rows=4) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[2;1'z\x1b[1;3'{")
            terminal.locator_button(1, True)
            terminal.locator_button(1, False)
            self.assertEqual(terminal.read_input(), b"\x1b[2;4;20;40;0&w")
            terminal.write(b"\x1b['|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")


    def test_non_finite_wheel_deltas_are_ignored(self):
        with Shitty(columns=10, rows=4, save_lines=10) as terminal:
            terminal.write(b"\r\n".join(str(i).encode() for i in range(1, 15)))
            terminal.write(b"\x1b[?1000h\x1b[?1006h")
            terminal.scroll(0, float("nan"))
            terminal.scroll(0, float("inf"))
            self.assertEqual(terminal.read_input(), b"")
            self.assertEqual(terminal.snapshot().view_offset, 0)
            terminal.scroll(0, 1)
            self.assertNotEqual(terminal.read_input(), b"")


    def test_drags_with_the_other_buttons_report_their_motion_codes(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[?1002h\x1b[?1006h")
            for button in (1, 2):
                terminal.button(button, True, x=4, y=3)
                terminal.pointer(5, 3)
                terminal.pointer(6, 4)
                terminal.button(button, False, x=6, y=4)
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[<2;3;2M\x1b[<34;4;2M\x1b[<34;5;3M\x1b[<2;5;3m"
                b"\x1b[<1;3;2M\x1b[<33;4;2M\x1b[<33;5;3M\x1b[<1;5;3m",
            )
            terminal.write(b"\x1b[?1006l")
            for button in (1, 2):
                terminal.button(button, True, x=4, y=3)
                terminal.pointer(5, 3)
                terminal.button(button, False, x=5, y=3)
            self.assertEqual(
                terminal.read_input(),
                b'\x1b[M"#"\x1b[MB$"\x1b[M#$"\x1b[M!#"\x1b[M#$"',
            )


if __name__ == "__main__":
    unittest.main()

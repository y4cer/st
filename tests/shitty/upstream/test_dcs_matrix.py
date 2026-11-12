# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def hex_name(name):
    return name.encode().hex().encode()


class DcsMatrixTest(unittest.TestCase):
    def test_xtgettcap_reports_every_declared_name(self):
        expected = {
            "TN": b"xterm-256color",
            "Co": b"256",
            "colors": b"256",
            "RGB": b"8",
        }
        with Shitty(columns=8, rows=2) as terminal:
            request = b";".join(hex_name(name) for name in expected)
            terminal.write(b"\x1bP+q" + request + b"\x1b\\")

            self.assertEqual(
                terminal.read_input(),
                b"".join(
                    b"\x1bP1+r"
                    + hex_name(name)
                    + b"="
                    + value.hex().encode()
                    + b"\x1b\\"
                    for name, value in expected.items()
                ),
            )

    def test_xtgettcap_preserves_request_case_and_known_unknown_order(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP+q544e;626f677573;436F;524742\x1b\\")

            self.assertEqual(
                terminal.read_input(),
                b"\x1bP1+r544e=787465726d2d323536636f6c6f72\x1b\\"
                b"\x1bP0+r626f677573\x1b\\"
                b"\x1bP1+r436F=323536\x1b\\"
                b"\x1bP1+r524742=38\x1b\\",
            )

    def test_xtgettcap_rejects_each_malformed_hex_name_independently(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP+q5;5g;544e;;436f\x1b\\")

            self.assertEqual(
                terminal.read_input(),
                b"\x1bP0+r5\x1b\\"
                b"\x1bP0+r5g\x1b\\"
                b"\x1bP1+r544e=787465726d2d323536636f6c6f72\x1b\\"
                b"\x1bP0+r\x1b\\"
                b"\x1bP1+r436f=323536\x1b\\",
            )

    def test_xtgettcap_uses_selected_eight_bit_response_controls(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b G\x1bP+q436f;00\x1b\\")

            self.assertEqual(
                terminal.read_input(),
                b"\x901+r436f=323536\x9c\x900+r00\x9c",
            )

    def test_xtgettcap_publishes_queued_replies_only_after_terminator(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP+q544e;")
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x18")
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x1bP+q544e\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1bP1+r544e=787465726d2d323536636f6c6f72\x1b\\",
            )

    def test_decudk_programs_every_defined_function_key(self):
        codes = (17, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 31, 32, 33, 34)
        keys = tuple(f"F{number}" for number in range(6, 21))
        with Shitty(columns=8, rows=2) as terminal:
            definitions = b";".join(
                f"{code}/{0x41 + index:02x}".encode()
                for index, code in enumerate(codes)
            )
            terminal.write(b"\x1bP0;1|" + definitions + b"\x1b\\")
            for key in keys:
                terminal.key(key)

            self.assertEqual(terminal.read_input(), b"ABCDEFGHIJKLMNO")

    def test_decudk_default_parameters_clear_and_lock(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP|17/41\x1b\\")
            terminal.write(b"\x1bP1;1|17/42\x1b\\")
            terminal.key("F6")

            self.assertEqual(terminal.read_input(), b"A")

    def test_decudk_clear_and_preserve_apply_to_the_whole_definition_set(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP0;1|17/41;18/42\x1b\\")
            terminal.write(b"\x1bP1;1|17/43\x1b\\")
            terminal.key("F6")
            terminal.key("F7")
            self.assertEqual(terminal.read_input(), b"CB")

            terminal.write(b"\x1bP0;1|18/44\x1b\\")
            terminal.key("F6")
            terminal.key("F7")
            self.assertEqual(terminal.read_input(), b"\x1b[17~D")

    def test_decudk_lock_blocks_clear_and_programming(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP0;0|17/41\x1b\\")
            terminal.write(b"\x1bP0;1|17/42;18/43\x1b\\")
            terminal.key("F6")
            terminal.key("F7")

            self.assertEqual(terminal.read_input(), b"A\x1b[18~")

    def test_decudk_rejects_malformed_parameters_atomically(self):
        malformed = (
            b"0x;1|17/42",
            b"1;1x|17/42",
            b"2;1|17/42",
            b"1;2|17/42",
        )
        for request in malformed:
            with self.subTest(request=request):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(b"\x1bP0;1|17/41\x1b\\")
                    terminal.write(b"\x1bP" + request + b"\x1b\\")
                    terminal.key("F6")

                    self.assertEqual(terminal.read_input(), b"A")

    def test_decudk_ignores_bad_definitions_but_keeps_valid_siblings(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1bP0;1|"
                b"17x/58;18/4;19/gg;22/59;20/5a;21;23/"
                b"\x1b\\"
            )
            terminal.key("F6")
            terminal.key("F7")
            terminal.key("F8")
            terminal.key("F9")
            terminal.key("F10")
            terminal.key("F11")

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[17~\x1b[18~\x1b[19~Z\x1b[21~",
            )

    def test_decudk_accepts_255_bytes_and_rejects_256(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP0;1|17/" + b"41" * 255 + b"\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A" * 255)

            terminal.write(b"\x1bP1;1|17/" + b"42" * 256 + b"\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A" * 255)

    def test_decudk_empty_value_disables_a_programmed_key(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1bP0;1|17/41\x1b\\")
            terminal.write(b"\x1bP1;1|17/\x1b\\")
            terminal.key("F6")

            self.assertEqual(terminal.read_input(), b"")


if __name__ == "__main__":
    unittest.main()

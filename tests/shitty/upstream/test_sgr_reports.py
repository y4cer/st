# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def query(terminal, setting):
    terminal.write(b"\x1bP$q" + setting + b"\x1b\\")
    return terminal.read_input()


class SgrStatusReportTest(unittest.TestCase):
    def test_default_sgr_report_is_minimal_and_replayable(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(query(terminal, b"m"), b"\x1bP1$r0m\x1b\\")

    def test_sgr_report_includes_every_boolean_attribute(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[1;2;3;4;5;7;8;9;53m")

            self.assertEqual(
                query(terminal, b"m"),
                b"\x1bP1$r0;1;2;3;4;5;7;8;9;53m\x1b\\",
            )

    def test_sgr_report_preserves_every_underline_style(self):
        for style in range(1, 6):
            with self.subTest(style=style):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(f"\x1b[4:{style}m".encode())

                    self.assertEqual(
                        query(terminal, b"m"),
                        (
                            b"\x1bP1$r0;4m\x1b\\"
                            if style == 1
                            else f"\x1bP1$r0;4:{style}m\x1b\\".encode()
                        ),
                    )

    def test_sgr_report_preserves_indexed_and_truecolor_channels(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b[38;2;1;2;3;48;5;21;58;2;4;5;6m"
            )

            self.assertEqual(
                query(terminal, b"m"),
                b"\x1bP1$r0;38:2::1:2:3;48:5:21;58:2::4:5:6m\x1b\\",
            )

    def test_sgr_report_omits_default_underline_color(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[31;4;58;5;46;59m")

            self.assertEqual(
                query(terminal, b"m"),
                b"\x1bP1$r0;4;31m\x1b\\",
            )

    def test_sgr_report_uses_logical_colors_while_inverse_is_active(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[38;5;1;48;5;4;7m")

            self.assertEqual(
                query(terminal, b"m"),
                b"\x1bP1$r0;7;31;44m\x1b\\",
            )

    def test_sgr_report_replays_equivalent_cell_state(self):
        with Shitty(columns=8, rows=2) as source:
            source.write(
                b"\x1b[1;2;3;4:3;5;7;8;9;53;"
                b"38;2;1;2;3;48;5;21;58;5;46mA"
            )
            report = query(source, b"m")[5:-2]
            expected = source.snapshot().cell(0, 0)

        with Shitty(columns=8, rows=2) as target:
            target.write(b"\x1b[" + report + b"B")
            actual = target.snapshot().cell(0, 0)

        for field in (
            "bold",
            "faint",
            "italic",
            "underline_style",
            "blink",
            "conceal",
            "strike",
            "overline",
            "foreground",
            "background",
            "underline_color",
        ):
            with self.subTest(field=field):
                self.assertEqual(getattr(actual, field), getattr(expected, field))

    def test_decsca_report_tracks_protected_state(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(query(terminal, b'"q'), b'\x1bP1$r0"q\x1b\\')

            terminal.write(b'\x1b[1"q')
            self.assertEqual(query(terminal, b'"q'), b'\x1bP1$r1"q\x1b\\')

            terminal.write(b'\x1b[2"q')
            self.assertEqual(query(terminal, b'"q'), b'\x1bP1$r0"q\x1b\\')

    def test_sgr_queries_do_not_mutate_attributes(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[2;4:4;8;58;5;46mA")
            first = query(terminal, b"m")
            second = query(terminal, b"m")
            terminal.write(b"B")
            snapshot = terminal.snapshot()

            self.assertEqual(first, second)
            first_cell = snapshot.cell(0, 0)
            second_cell = snapshot.cell(1, 0)
            for field in first_cell.__dataclass_fields__:
                if field != "char":
                    self.assertEqual(
                        getattr(first_cell, field), getattr(second_cell, field)
                    )

    def test_out_of_range_palette_indices_change_nothing(self):
        # 256-color selectors cap at index 255: larger indices are not
        # colors and the attribute keeps its previous value.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"A\x1b[38;5;300m\x1b[48;5;999mB")
            snapshot = terminal.snapshot()
            plain = snapshot.cell(0, 0)
            after = snapshot.cell(1, 0)
            self.assertEqual(after.foreground, plain.foreground)
            self.assertEqual(after.background, plain.background)


if __name__ == "__main__":
    unittest.main()

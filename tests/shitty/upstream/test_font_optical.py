# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import tempfile
import unittest
from pathlib import Path

from font_fixture import make_optical_font
from harness import Shitty


def ink_runs(width, height, pixels):
    columns = []
    for x in range(width):
        ink = any(
            max(pixels[3 * (y * width + x) : 3 * (y * width + x + 1)]) > 40
            for y in range(height)
        )
        if ink:
            columns.append(x)

    runs = []
    for column in columns:
        if not runs or column != runs[-1][1] + 1:
            runs.append([column, column])
        else:
            runs[-1][1] = column
    return runs


def gaps(runs):
    return [right[0] - left[1] - 1 for left, right in zip(runs, runs[1:])]


class OpticalFontTest(unittest.TestCase):
    def render(self, font, text, optical):
        arguments = ("-fontsize", "16")
        if optical:
            arguments += ("-optical",)
        with Shitty(
            columns=len(text),
            rows=1,
            extra_arguments=arguments,
        ) as terminal:
            terminal.write(("\x1b[?25l" + text).encode())
            metrics = terminal.load_font(str(font))
            return metrics, terminal.render_image(str(font))

    def test_latin_and_cyrillic_runs_are_optically_reflowed(self):
        with tempfile.TemporaryDirectory() as directory:
            font = Path(directory) / "optical.ttf"
            font.write_bytes(make_optical_font("Shitty Optical Fixture"))
            for text in ("AVAV", "АУАУ"):
                with self.subTest(text=text):
                    metrics, ordinary = self.render(font, text, False)
                    _, optical = self.render(font, text, True)

                    self.assertEqual(ordinary[:2], optical[:2])
                    ordinary_runs = ink_runs(*ordinary)
                    optical_runs = ink_runs(*optical)
                    self.assertEqual(len(ordinary_runs), len(text))
                    self.assertEqual(len(optical_runs), len(text))
                    ordinary_gaps = gaps(ordinary_runs)
                    optical_gaps = gaps(optical_runs)
                    self.assertGreater(
                        max(ordinary_gaps) - min(ordinary_gaps),
                        metrics["px"] // 2,
                    )
                    self.assertLessEqual(
                        max(optical_gaps) - min(optical_gaps),
                        2,
                    )

    def test_unsupported_codepoint_passes_the_whole_run_through(self):
        with tempfile.TemporaryDirectory() as directory:
            font = Path(directory) / "optical.ttf"
            font.write_bytes(make_optical_font("Shitty Optical Fixture"))
            _, ordinary = self.render(font, "A+V", False)
            _, optical = self.render(font, "A+V", True)

        self.assertEqual(ordinary, optical)


if __name__ == "__main__":
    unittest.main()

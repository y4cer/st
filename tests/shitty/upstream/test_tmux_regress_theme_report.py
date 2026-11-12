# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Terminal-visible adaptation of current tmux theme-report regress."""

import unittest

from harness import Shitty


PORTED_CASES = (
    (
        "regress/theme-report.sh:reported-theme-wins-over-background",
        "test_reported_theme_wins_over_application_background",
    ),
)


class TmuxRegressThemeReportTest(unittest.TestCase):
    def test_upstream_inventory_has_one_executable_case(self):
        self.assertEqual(len(PORTED_CASES), 1)
        self.assertTrue(callable(getattr(self, PORTED_CASES[0][1])))

    def test_reported_theme_wins_over_application_background(self):
        with Shitty(extra_arguments=("-bg", "#ffffff")) as terminal:
            terminal.write(b"\x1b]11;#000000\x1b\\\x1b[?996n")
            self.assertEqual(terminal.read_input(), b"\x1b[?997;2n")


if __name__ == "__main__":
    unittest.main()

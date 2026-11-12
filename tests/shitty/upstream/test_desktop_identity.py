# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ST = ROOT / "bin" / "st"


class DesktopIdentityTests(unittest.TestCase):
    def setUp(self):
        self.desktop = (ST / "shitty.desktop").read_text()

    def desktop_value(self, key):
        match = re.search(
            rf"^{re.escape(key)}=(.+)$",
            self.desktop,
            re.MULTILINE,
        )
        self.assertIsNotNone(match)
        return match.group(1)

    def test_desktop_comment_describes_cross_platform_frontend(self):
        self.assertEqual(
            self.desktop_value("Comment"),
            "Cross-platform terminal with Vulkan rendering",
        )

    def test_desktop_entry_launches_st(self):
        self.assertEqual(self.desktop_value("Exec"), "st")

    def test_desktop_icon_matches_installed_svg(self):
        self.assertEqual(self.desktop_value("Icon"), (ST / "shitty.svg").stem)

    def test_desktop_window_class_matches_application_identity(self):
        self.assertEqual(
            self.desktop_value("StartupWMClass"),
            self.desktop_value("Icon"),
        )


if __name__ == "__main__":
    unittest.main()

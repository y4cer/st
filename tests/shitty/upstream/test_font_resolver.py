# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import os
import tempfile
import unittest
from pathlib import Path

from font_fixture import COLOR_EMOJI_FONT, make_collection, make_font
from harness import Shitty


FONTCONFIG_AVAILABLE = os.environ.get("SHITTY_TEST_FONTCONFIG", "1") == "1"


class FontResolverTest(unittest.TestCase):
    @staticmethod
    def write_fontconfig(root):
        config = root / "fonts.conf"
        config.write_text(
            "<?xml version=\"1.0\"?>\n"
            "<!DOCTYPE fontconfig SYSTEM \"urn:fontconfig:fonts.dtd\">\n"
            "<fontconfig>\n"
            f"  <dir>{root}</dir>\n"
            f"  <cachedir>{root / 'cache'}</cachedir>\n"
            "  <config><rescan><int>0</int></rescan></config>\n"
            "</fontconfig>\n"
        )
        return config

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_collection_face_and_representative_advances_define_cells(self):
        collection = make_collection(
            make_font("Shitty Wrong Face", 750, 1500, 2000),
            make_font("Shitty Test Mono", 500, 1000, 3000),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            font = root / "fixture.ttc"
            font.write_bytes(collection)
            config = self.write_fontconfig(root)
            with Shitty(
                extra_environment={"FONTCONFIG_FILE": str(config)}
            ) as terminal:
                loaded = terminal.load_font("Shitty Test Mono")

        self.assertEqual(loaded["px"], 8)

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_overlay_width_is_independent_but_vertical_metrics_must_match(self):
        family = "Shitty Overlay Test"
        collection = make_collection(
            make_font(family, 500, 1000, 500),
            make_font(family, 700, 1400, 700, style="Bold"),
            make_font(
                family,
                500,
                1000,
                500,
                descender=-300,
                style="Italic",
            ),
            make_font(
                family,
                500,
                1000,
                500,
                ascender=700,
                descender=-300,
                style="Bold Italic",
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            font = root / "overlay.ttc"
            font.write_bytes(collection)
            config = self.write_fontconfig(root)
            with Shitty(
                extra_environment={"FONTCONFIG_FILE": str(config)}
            ) as terminal:
                loaded = terminal.load_font(family)

        # The italic faces mismatch the vertical metrics and are rejected;
        # synthetic styles take their place.
        self.assertEqual(
            (loaded["bold"], loaded["italic"], loaded["bold_italic"]),
            (1, 1, 1),
        )

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_extra_fallback_fonts_keep_primary_metrics(self):
        with Shitty() as terminal:
            primary = terminal.load_font("monospace")
            extended = terminal.load_font("monospace", "Arial")
        self.assertEqual(
            (extended["px"], extended["py"]),
            (primary["px"], primary["py"]),
        )

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_fontconfig_resolves_family_and_alias(self):
        with Shitty() as terminal:
            for family in ("monospace", "IBM Plex Mono"):
                with self.subTest(family=family):
                    loaded = terminal.load_font(family)
                    self.assertGreater(loaded["px"], 0)
                    self.assertGreater(loaded["py"], 0)

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_fontconfig_loads_all_four_style_faces_when_available(self):
        with Shitty() as terminal:
            loaded = terminal.load_font("IBM Plex Mono")
        self.assertEqual(
            (loaded["bold"], loaded["italic"], loaded["bold_italic"]),
            (1, 1, 1),
        )

    @unittest.skipUnless(FONTCONFIG_AVAILABLE, "Fontconfig is not available")
    def test_fontconfig_family_loads_without_a_search_path(self):
        with Shitty() as terminal:
            loaded = terminal.load_font("monospace")
        self.assertGreater(loaded["px"], 0)
        self.assertGreater(loaded["py"], 0)

    def test_unresolvable_family_falls_back_to_the_embedded_font(self):
        with Shitty() as terminal:
            loaded = terminal.load_font("Shitty No Such Family 8b3f")
        self.assertGreater(loaded["px"], 0)
        self.assertGreater(loaded["py"], 0)

    def test_font_file_path_is_not_treated_as_a_family(self):
        with Shitty(extra_arguments=("-fontsize", "32")) as terminal:
            primary = terminal.load_font(COLOR_EMOJI_FONT)
        self.assertLessEqual(primary["py"], 64)

    def test_font_file_paths_load_primary_and_fallback_fonts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            primary_font = root / "primary.ttf"
            fallback_font = root / "fallback.ttf"
            primary_font.write_bytes(
                make_font("Shitty Path Primary", 500, 1000, 1000)
            )
            fallback_font.write_bytes(
                make_font("Shitty Path Fallback", 1000, 1000, 1000)
            )
            with Shitty() as terminal:
                loaded = terminal.load_font(primary_font, fallback_font)

        self.assertEqual(loaded["px"], 8)


if __name__ == "__main__":
    unittest.main()

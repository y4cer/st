# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "lib" / "shitty" / "terminal_colors.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("terminal_colors_generator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TerminalColorsDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()

    def test_catalog_is_normalized_and_has_all_collections(self):
        catalog = self.generator.load_catalog()
        sources = {source["id"]: source for source in catalog["sources"]}
        self.assertEqual(
            {
                "alacritty-theme",
                "gogh",
                "iterm2-color-schemes",
                "kitty-themes",
                "terminal-sexy",
            },
            {
                source["id"]
                for source in catalog["sources"]
                if source["kind"] == "collection"
            },
        )
        self.assertEqual(sources["iterm2-color-schemes"]["license"], "MIT")
        self.assertEqual(sources["gogh"]["license"], "MIT")
        self.assertEqual(sources["alacritty-theme"]["license"], "Apache-2.0")
        self.assertEqual(sources["kitty-themes"]["license"], "GPL-3.0-only")
        self.assertEqual(sources["terminal-sexy"]["license"], "MIT")
        for source in sources.values():
            self.assertEqual(len(source["revision"]), 40)
            if "licenseFile" in source:
                self.assertTrue((ROOT / source["licenseFile"]).is_file())

        schemes_by_source = {}
        for scheme in catalog["schemes"]:
            schemes_by_source.setdefault(scheme["source"], []).append(scheme)
        self.assertGreaterEqual(len(schemes_by_source["iterm2-color-schemes"]), 500)
        self.assertGreaterEqual(len(schemes_by_source["gogh"]), 300)
        self.assertGreaterEqual(len(schemes_by_source["alacritty-theme"]), 150)
        self.assertGreaterEqual(len(schemes_by_source["kitty-themes"]), 400)
        self.assertGreaterEqual(len(schemes_by_source["terminal-sexy"]), 150)
        self.assertGreaterEqual(len(catalog["schemes"]), 1700)

        names = [scheme["name"] for scheme in catalog["schemes"]]
        self.assertIn("3024 Night", names)
        self.assertIn("Nord", names)
        self.assertIn("Gogh: 3024 Night", names)
        self.assertIn("Alacritty: dracula", names)
        self.assertIn("Kitty: Dracula", names)
        self.assertIn("terminal.sexy: Tomorrow (dark) (base16)", names)
        self.assertEqual(len(names), len({name.casefold() for name in names}))

    def test_canonical_terminal_defaults_are_separate_schemes(self):
        catalog = self.generator.load_catalog()
        schemes = {scheme["name"]: scheme for scheme in catalog["schemes"]}
        expected_sources = {
            "Alacritty": "alacritty",
            "foot": "foot",
            "Ghostty": "ghostty",
            "GNOME Terminal": "gnome-terminal",
            "kitty": "kitty",
            "Konsole": "konsole",
            "WezTerm": "wezterm",
            "Windows Terminal": "windows-terminal",
        }
        for name, source in expected_sources.items():
            self.assertEqual(schemes[name]["source"], source)

        self.assertEqual(schemes["kitty"]["foreground"], "#dddddd")
        self.assertEqual(schemes["kitty"]["ansi"][9], "#f2201f")
        self.assertEqual(schemes["Ghostty"]["background"], "#282c34")
        self.assertEqual(schemes["foot"]["ansi"][1], "#f62b5a")
        self.assertEqual(schemes["Konsole"]["ansi"][12], "#3daee9")
        self.assertEqual(schemes["Windows Terminal"]["background"], "#0c0c0c")

    def test_alacritty_import_overlays_partial_themes_on_defaults(self):
        spec = next(
            spec
            for spec in self.generator.COLLECTIONS
            if spec["id"] == "alacritty-theme"
        )
        files = {
            "themes/partial.toml": """
[colors.primary]
background = '#010203'

[colors.normal]
red = '#040506'
""",
        }
        imported = self.generator.import_alacritty_files(files, spec)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0]["name"], "Alacritty: partial")
        self.assertEqual(imported[0]["background"], "#010203")
        self.assertEqual(imported[0]["foreground"], "#d8d8d8")
        self.assertEqual(imported[0]["ansi"][1], "#040506")
        self.assertEqual(imported[0]["ansi"][3], "#f4bf75")

    def test_cpp_table_generation_is_deterministic_and_complete(self):
        self.assertFalse((ROOT / "terminal_colors.json.h").exists())
        catalog = self.generator.load_catalog()
        first = self.generator.generate_header(catalog)
        second = self.generator.generate_header(catalog)
        self.assertEqual(first, second)
        self.assertEqual(
            first.count("    {\n        \""),
            len(catalog["schemes"]),
        )
        self.assertIn(
            "static constexpr TerminalColorScheme terminalColorSchemes[]",
            first,
        )


if __name__ == "__main__":
    unittest.main()

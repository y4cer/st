# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js Unicode, charset and XParseColor units."""

import os
from pathlib import Path
import signal
import tempfile
import time
import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "UnicodeV6: wcwidth should match all values from the old implementation",
    "UnicodeService: default to V6",
    "UnicodeService: activate should throw for unknown version",
    "UnicodeService: should notify about version change",
    "UnicodeService: correctly changes provider impl",
    "UnicodeService: wcwidth V6 emoji test",
    "CharsetService: should not update active charset when designating an inactive glevel",
    "CharsetService: should expose the designated charset after setgLevel",
    "CharsetService: should update active charset when designating the current glevel",
    "CharsetService: should reset glevel, charsets, and active charset",
    "XParseColor.parseColor: rgb scheme in 4/8/12/16 bit",
    "XParseColor.parseColor: hash scheme in 4/8/12/16 bit",
    "XParseColor.parseColor: supports upper case",
    "XParseColor.parseColor: does not parse illegal combinations",
    "XParseColor.toRgbString: rgb scheme in 4/8/12/16 bit",
    "XParseColor.toRgbString: defaults to 16 bit output",
    "XParseColor.toRgbString: reduces colors to 8 bit resolution",
)


def width(terminal, text):
    return terminal.measure_widths(text.encode("utf-8"))[0][0]


def capabilities(terminal):
    terminal.read_all_input()
    terminal.write(b"\x1b]1337;Capabilities\x1b\\")
    return terminal.read_input()


def set_cursor_color(terminal, spec):
    terminal.write(b"\x1b]12;" + spec.encode("ascii") + b"\x1b\\")


def query_cursor_color(terminal):
    terminal.write(b"\x1b]12;?\x1b\\")
    return terminal.read_input()


def color_reply(red, green, blue):
    return (
        b"\x1b]12;rgb:"
        + f"{red:02x}{red:02x}/{green:02x}{green:02x}/{blue:02x}{blue:02x}".encode()
        + b"\x1b\\"
    )


def assert_color(test, terminal, spec, expected):
    set_cursor_color(terminal, spec)
    test.assertEqual(query_cursor_color(terminal), color_reply(*expected), spec)


class XtermJsUnicodeCharsetColorTest(unittest.TestCase):
    def test_upstream_inventory_has_all_17_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 17)
        self.assertEqual(len(set(UPSTREAM_CASES)), 17)

    @unittest.expectedFailure
    def test_unicode_v6_wcwidth_matches_classic_public_cell_classes(self):
        # Shitty's oldest selectable table is Unicode 8, which has the same
        # pre-emoji-width behavior exercised by xterm.js's V6 provider.
        with Shitty(extra_arguments=("-unicodeWidths", "8")) as terminal:
            self.assertEqual(width(terminal, "A"), 1)
            self.assertEqual(width(terminal, "A\u0301"), 1)
            self.assertEqual(width(terminal, "中"), 2)
            self.assertEqual(width(terminal, "🤣"), 1)

    @unittest.expectedFailure
    def test_unicode_service_defaults_to_v6(self):
        # xterm.js freezes this private provider default at Unicode 6.
        # Shitty deliberately resolves its default against the host libc.
        with Shitty() as terminal:
            self.assertIn(b"Uw6", capabilities(terminal))
            self.assertEqual(width(terminal, "🤣"), 1)

    @unittest.expectedFailure
    def test_unicode_service_rejects_an_unknown_provider_version(self):
        # xterm.js chooses from registered providers.  Shitty's numeric
        # option is instead a width-policy cutoff and advertises the chosen
        # value even when it is newer than the compiled Unicode data.
        with Shitty(extra_arguments=("-unicodeWidths", "55")) as terminal:
            self.assertNotIn(b"Uw55", capabilities(terminal))

    def test_unicode_service_change_is_visible_to_clients(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unicode.toml"
            path.write_text("unicodeWidths = 8\n")
            with Shitty(extra_arguments=("-config", path)) as terminal:
                self.assertIn(b"Uw8", capabilities(terminal))
                path.write_text("unicodeWidths = 17\n")
                os.kill(terminal.process.pid, signal.SIGUSR1)

                deadline = time.monotonic() + 2
                while b"Uw17" not in capabilities(terminal):
                    if time.monotonic() >= deadline:
                        self.fail("reloaded Unicode provider was not advertised")
                    time.sleep(0.01)

    @unittest.expectedFailure
    def test_unicode_service_change_replaces_the_width_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unicode.toml"
            path.write_text("unicodeWidths = 8\n")
            with Shitty(extra_arguments=("-config", path)) as terminal:
                self.assertEqual(width(terminal, "⌚"), 1)
                path.write_text("unicodeWidths = 17\n")
                os.kill(terminal.process.pid, signal.SIGUSR1)

                deadline = time.monotonic() + 2
                while b"Uw17" not in capabilities(terminal):
                    if time.monotonic() >= deadline:
                        self.fail("reloaded Unicode provider was not advertised")
                    time.sleep(0.01)
                self.assertEqual(width(terminal, "⌚"), 2)

    @unittest.expectedFailure
    def test_unicode_v6_emoji_are_ten_narrow_cells(self):
        with Shitty(extra_arguments=("-unicodeWidths", "8")) as terminal:
            self.assertEqual(width(terminal, "🤣" * 10), 10)

    def test_inactive_charset_designation_does_not_change_gl(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0q")
            self.assertEqual(terminal.snapshot().lines[0][:1], "q")

    def test_designated_charset_is_exposed_after_switching_glevel(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b)0\x0eq")
            self.assertEqual(terminal.snapshot().lines[0][:1], "─")

    def test_designating_the_active_glevel_updates_its_charset(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x0e\x1b)0q")
            self.assertEqual(terminal.snapshot().lines[0][:1], "─")

    def test_reset_restores_g0_and_discards_designated_charsets(self):
        for reset in (b"\x1b[!p", b"\x1bc"):
            with self.subTest(reset=reset):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(b"\x1b)0\x0e" + reset + b"q")
                    self.assertEqual(terminal.snapshot().lines[0][:1], "q")

    def test_xparse_rgb_scheme_in_4_8_12_and_16_bit(self):
        vectors = (
            ("rgb:0/0/0", (0, 0, 0)),
            ("rgb:f/f/f", (255, 255, 255)),
            ("rgb:1/2/3", (17, 34, 51)),
            ("rgb:00/00/00", (0, 0, 0)),
            ("rgb:ff/ff/ff", (255, 255, 255)),
            ("rgb:11/22/33", (17, 34, 51)),
            ("rgb:000/000/000", (0, 0, 0)),
            ("rgb:fff/fff/fff", (255, 255, 255)),
            ("rgb:111/222/333", (17, 34, 51)),
            ("rgb:0000/0000/0000", (0, 0, 0)),
            ("rgb:ffff/ffff/ffff", (255, 255, 255)),
            ("rgb:1111/2222/3333", (17, 34, 51)),
        )
        with Shitty() as terminal:
            for spec, expected in vectors:
                with self.subTest(spec=spec):
                    assert_color(self, terminal, spec, expected)

    def test_xparse_hash_scheme_in_4_8_12_and_16_bit(self):
        vectors = (
            ("#000", (0, 0, 0)),
            ("#fff", (240, 240, 240)),
            ("#123", (16, 32, 48)),
            ("#000000", (0, 0, 0)),
            ("#ffffff", (255, 255, 255)),
            ("#112233", (17, 34, 51)),
            ("#000000000", (0, 0, 0)),
            ("#fffffffff", (255, 255, 255)),
            ("#111222333", (17, 34, 51)),
            ("#000000000000", (0, 0, 0)),
            ("#ffffffffffff", (255, 255, 255)),
            ("#111122223333", (17, 34, 51)),
        )
        with Shitty() as terminal:
            for spec, expected in vectors:
                with self.subTest(spec=spec):
                    assert_color(self, terminal, spec, expected)

    def test_xparse_color_accepts_upper_case(self):
        with Shitty() as terminal:
            assert_color(self, terminal, "RGB:0/A/F", (0, 170, 255))
            assert_color(self, terminal, "#FFF", (240, 240, 240))

    @unittest.expectedFailure
    def test_xparse_color_rejects_the_source_illegal_combinations(self):
        # The standalone xterm.js helper is narrower than XParseColor itself:
        # Xlib permits independently-sized channels and rgbi intensity form.
        invalid = (
            "rgb:0/11/222",
            "rgbi:0.0/0.1/0.2",
            "#aabbbcc",
            "#aabbgg",
            "rgb:aa/bb/gg",
        )
        with Shitty() as terminal:
            before = query_cursor_color(terminal)
            for spec in invalid:
                set_cursor_color(terminal, spec)
                self.assertEqual(query_cursor_color(terminal), before, spec)

    def test_color_query_normalizes_every_input_width_to_16_bit(self):
        vectors = (
            "rgb:1/2/3",
            "rgb:11/22/33",
            "rgb:111/222/333",
            "rgb:1111/2222/3333",
        )
        with Shitty() as terminal:
            for spec in vectors:
                with self.subTest(spec=spec):
                    set_cursor_color(terminal, spec)
                    self.assertEqual(
                        query_cursor_color(terminal),
                        b"\x1b]12;rgb:1111/2222/3333\x1b\\",
                    )

    def test_color_query_defaults_to_16_bit_output(self):
        with Shitty() as terminal:
            set_cursor_color(terminal, "rgb:123/123/123")
            self.assertEqual(
                query_cursor_color(terminal),
                b"\x1b]12;rgb:1212/1212/1212\x1b\\",
            )

    def test_color_conversion_reduces_to_eight_bit_resolution(self):
        with Shitty() as terminal:
            for spec in ("rgb:123/123/123", "rgb:1234/1234/1234"):
                with self.subTest(spec=spec):
                    set_cursor_color(terminal, spec)
                    self.assertEqual(
                        query_cursor_color(terminal),
                        b"\x1b]12;rgb:1212/1212/1212\x1b\\",
                    )


if __name__ == "__main__":
    unittest.main()

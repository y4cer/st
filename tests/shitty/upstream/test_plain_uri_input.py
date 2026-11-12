# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


CONTROL = 2


def cell_pixels(image, width, border, cell_width, cell_height, column):
    result = bytearray()
    left = border + column * cell_width
    for y in range(border, border + cell_height):
        begin = 3 * (y * width + left)
        result.extend(image[begin : begin + 3 * cell_width])
    return bytes(result)


class PlainUriInputTest(unittest.TestCase):
    def assert_opened(self, terminal, column, row, expected):
        terminal.button(
            0,
            True,
            x=2 + column,
            y=2 + row,
            modifiers=CONTROL,
        )
        terminal.button(
            0,
            False,
            x=2 + column,
            y=2 + row,
            modifiers=CONTROL,
        )
        state = terminal.desktop_state()
        self.assertEqual(state["opened_uri"], expected)
        return state

    def test_scheme_is_case_insensitive_and_uri_is_preserved(self):
        with Shitty(columns=48, rows=2) as terminal:
            uri = b"HTTPS://Example.Test/Original"
            terminal.write(uri + b" file://example.test")

            terminal.pointer(2 + 10, 2, modifiers=CONTROL)
            state = terminal.desktop_state()
            self.assertEqual(state["icon"], 1)
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (0, len(uri)),
            )
            state = self.assert_opened(terminal, 10, 0, uri)
            self.assertEqual(state["open_count"], 1)

            terminal.pointer(2 + len(uri) + 5, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 1)
            state = self.assert_opened(
                terminal,
                len(uri) + 5,
                0,
                b"file://example.test",
            )
            self.assertEqual(state["open_count"], 2)

    def test_malformed_scheme_and_empty_target_are_not_links(self):
        cases = (
            b"1https://example.test",
            b"https//example.test",
            b"https:",
        )
        for value in cases:
            with self.subTest(value=value):
                with Shitty(columns=32, rows=1) as terminal:
                    terminal.write(value)
                    terminal.pointer(2 + min(8, len(value) - 1), 2, modifiers=CONTROL)
                    self.assertEqual(terminal.desktop_state()["icon"], 0)

    def test_stationary_hover_is_recomputed_after_content_changes(self):
        with Shitty(columns=32, rows=1) as terminal:
            uri = b"https://changing.test"
            terminal.write(uri)
            terminal.pointer(2 + 8, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 1)

            terminal.write(b"\r" + b" " * len(uri))
            state = terminal.desktop_state()
            self.assertEqual(state["icon"], 0)
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (0, 0),
            )

    def test_surrounding_punctuation_is_trimmed_but_balanced_uri_is_kept(self):
        with Shitty(columns=48, rows=1) as terminal:
            uri = b"https://host.test/a(b)c"
            terminal.write(b"see(" + uri + b"), then")

            state = self.assert_opened(terminal, 10, 0, uri)
            self.assertEqual(state["open_count"], 1)

            terminal.pointer(2 + 3, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)
            terminal.pointer(2 + 4 + len(uri), 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)

    def test_soft_wrap_joins_but_hard_newline_does_not(self):
        uri = b"https://example.test/path"
        with Shitty(columns=12, rows=3) as terminal:
            terminal.write(uri)
            state = self.assert_opened(terminal, 3, 1, uri)
            self.assertEqual(state["open_count"], 1)
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (0, len(uri)),
            )

        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"https://one.\r\ntest/path")
            terminal.pointer(2 + 3, 3, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)

    def test_scrollback_wide_grapheme_and_dec_double_width_map_to_uri(self):
        with Shitty(columns=24, rows=2, save_lines=4) as terminal:
            uri = "https://x.test/界e\u0301".encode()
            terminal.write(uri + b"\r\nnext\r\nlast")
            terminal.page_up()
            state = self.assert_opened(terminal, 16, 0, uri)
            self.assertEqual(state["open_count"], 1)

        with Shitty(columns=48, rows=1) as terminal:
            uri = b"https://double.test"
            terminal.write(b"\x1b#6" + uri)
            state = self.assert_opened(terminal, 12, 0, uri)
            self.assertEqual(state["open_count"], 1)

    def test_concealed_plain_text_is_ignored_and_osc8_is_authoritative(self):
        with Shitty(columns=40, rows=2) as terminal:
            terminal.write(b"\x1b[8mhttps://hidden.test\x1b[0m")
            terminal.pointer(2 + 8, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)

            explicit = b"custom://authoritative"
            terminal.write(
                b"\x1b[2;1H"
                b"\x1b]8;id=explicit;"
                + explicit
                + b"\x1b\\https://plain.test\x1b]8;;\x1b\\"
            )
            state = self.assert_opened(terminal, 8, 1, explicit)
            self.assertNotEqual(state["hovered_hyperlink"], 0)
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (0, 0),
            )

    def test_reference_renderer_underlines_the_complete_plain_uri(self):
        with Shitty(columns=12, rows=1) as terminal:
            uri = b"https://x"
            terminal.write(b"\x1b[?25l" + uri + b" Z")
            metrics = terminal.load_font("monospace", "")
            border = terminal.options()["border"]
            width, _, original = terminal.render_image("monospace", "")

            terminal.pointer(2 + 4, 2, modifiers=CONTROL)
            _, _, hovered = terminal.render_image("monospace", "")

            for column in range(len(uri)):
                self.assertNotEqual(
                    cell_pixels(
                        original,
                        width,
                        border,
                        metrics["px"],
                        metrics["py"],
                        column,
                    ),
                    cell_pixels(
                        hovered,
                        width,
                        border,
                        metrics["px"],
                        metrics["py"],
                        column,
                    ),
                )
            self.assertEqual(
                cell_pixels(
                    original,
                    width,
                    border,
                    metrics["px"],
                    metrics["py"],
                    10,
                ),
                cell_pixels(
                    hovered,
                    width,
                    border,
                    metrics["px"],
                    metrics["py"],
                    10,
                ),
            )

    def test_scan_limit_rejects_a_truncated_candidate(self):
        with Shitty(columns=4200, rows=1) as terminal:
            terminal.write(b"https://" + b"a" * 4180)
            terminal.pointer(2 + 4100, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)


class PlainUriSchemeListTest(unittest.TestCase):
    def click(self, terminal, column, row=0):
        terminal.button(0, True, x=2 + column, y=2 + row, modifiers=CONTROL)
        terminal.button(0, False, x=2 + column, y=2 + row, modifiers=CONTROL)
        return terminal.desktop_state()

    def test_unlisted_scheme_stays_plain_text_by_default(self):
        with Shitty(columns=32, rows=1) as terminal:
            terminal.write(b"nosuch://example.test")
            terminal.pointer(2 + 8, 2, modifiers=CONTROL)
            state = terminal.desktop_state()
            self.assertEqual(state["icon"], 0)
            self.assertEqual(
                (state["hovered_link_begin"], state["hovered_link_end"]),
                (0, 0),
            )
            self.assertEqual(self.click(terminal, 8)["open_count"], 0)

    def test_configured_list_replaces_the_default(self):
        arguments = ("-uriScheme", "NoSuch")
        with Shitty(columns=64, rows=1, extra_arguments=arguments) as terminal:
            uri = b"nosuch://example.test"
            terminal.write(uri + b" https://example.test")

            terminal.pointer(2 + 8, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 1)
            state = self.click(terminal, 8)
            self.assertEqual(state["opened_uri"], uri)
            self.assertEqual(state["open_count"], 1)

            terminal.pointer(2 + len(uri) + 5, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 0)
            self.assertEqual(self.click(terminal, len(uri) + 5)["open_count"], 1)

    def test_osc8_ignores_the_scheme_list(self):
        with Shitty(columns=40, rows=1) as terminal:
            explicit = b"nosuch://authoritative"
            terminal.write(
                b"\x1b]8;id=explicit;" + explicit + b"\x1b\\follow me\x1b]8;;\x1b\\"
            )
            terminal.pointer(2 + 4, 2, modifiers=CONTROL)
            self.assertEqual(terminal.desktop_state()["icon"], 1)
            self.assertEqual(self.click(terminal, 4)["opened_uri"], explicit)


if __name__ == "__main__":
    unittest.main()

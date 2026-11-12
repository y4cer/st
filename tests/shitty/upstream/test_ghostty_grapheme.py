# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class GhosttyGraphemeTest(unittest.TestCase):
    def assert_streaming_grapheme(self, text, width):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write_chunks(*(character.encode() for character in text))
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (width, 0))
            self.assertEqual(
                snapshot.cell(0, 0).grapheme,
                tuple(map(ord, text)),
            )
            self.assertEqual(snapshot.cell(0, 0).double_width, width == 2)
            if width == 2:
                self.assertTrue(
                    snapshot.cell(1, 0).double_width_continuation
                )

    def test_zwj_sequences_are_one_wide_streaming_grapheme(self):
        for text in ("👨‍👩‍👧", "🏴‍☠️"):
            with self.subTest(text=text):
                self.assert_streaming_grapheme(text, 2)

    def test_variation_selectors_change_streaming_cluster_width(self):
        self.assert_streaming_grapheme("#︎", 1)
        self.assert_streaming_grapheme("#️", 2)

    def test_valid_emoji_modifier_stays_with_its_base(self):
        self.assert_streaming_grapheme("👋🏿", 2)

    def test_emoji_modifier_after_non_emoji_follows_unicode_17(self):
        # Current UAX #29 classifies Emoji_Modifier as Extend, so GB9 keeps it
        # with the preceding quote. Ghostty retains the pre-Unicode-11 GB10
        # exception and is the outlier here; Kitty and UAX #29 follow GB9.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write_chunks(*("\"🏿\""[index].encode() for index in range(3)))
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))
            self.assertEqual(
                snapshot.cell(0, 0).grapheme,
                (ord('"'), 0x1F3FF),
            )
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, '"')

    def test_each_codepoint_of_streaming_grapheme_damages_its_row(self):
        with Shitty(columns=8, rows=2) as terminal:
            for character in "👨‍👩‍👧":
                terminal.write(character.encode())
                cells, rows = terminal.last_update()
                # Damage is row-granular: the row re-renders wholly.
                self.assertEqual((cells, rows), (8, 1))
                self.assertEqual(terminal.last_update_rows(), (0,))

    def test_vs15_narrows_wide_cluster_and_clears_pending_wrap(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write("🍋☔".encode())
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write("︎".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 0))
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertEqual(
                snapshot.cell(2, 0).grapheme,
                (ord("☔"), 0xFE0E),
            )
            self.assertFalse(snapshot.cell(2, 0).double_width)
            self.assertFalse(snapshot.cell(3, 0).double_width_continuation)

            terminal.write(b"X")
            self.assertEqual(terminal.snapshot().lines[0], "🍋 ☔X")

    def test_vs16_moves_right_edge_cluster_to_next_row(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"\x1b[3G#")
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write("️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertEqual(terminal.last_update_rows(), (0, 1))
            self.assertEqual(snapshot.lines, ["   ", "#  "])
            self.assertEqual(
                snapshot.cell(0, 1).grapheme,
                (ord("#"), 0xFE0F),
            )
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_vs16_right_edge_move_preserves_hyperlink(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;http://example.com\x1b\\"
                b"\x1b[3G#"
            )
            terminal.write("️".encode())
            snapshot = terminal.model_snapshot()
            self.assertNotEqual(snapshot.cell(0, 1).hyperlink, 0)
            self.assertEqual(
                snapshot.cell(0, 1).hyperlink,
                snapshot.cell(1, 1).hyperlink,
            )
            self.assertEqual(
                terminal.hyperlink(0, 1),
                "http://example.com",
            )

    def test_vs16_at_last_two_cells_enters_pending_wrap(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"\x1b[2G#")
            terminal.write("️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertTrue(terminal.cursor_pending_wrap())
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)

            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(snapshot.cell(0, 1).char, "X")

    def test_vs16_without_autowrap_does_not_make_half_wide_cluster(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[?7lAAAA" + "❤".encode())
            before = terminal.model_digest()
            terminal.write("️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], "AAAA❤")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            self.assertEqual(snapshot.cell(4, 0).grapheme, ())
            self.assertFalse(snapshot.cell(4, 0).double_width)
            self.assertFalse(
                snapshot.cell(4, 0).double_width_continuation
            )
            self.assertEqual(terminal.model_digest(), before)
            self.assertEqual(terminal.last_update(), (0, 0))

    def test_repeated_vs16_clusters_remain_distinct(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write_chunks(
                "❤".encode(),
                "️".encode(),
                "❤".encode(),
                "️".encode(),
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            for column in (0, 2):
                self.assertEqual(
                    snapshot.cell(column, 0).grapheme,
                    (ord("❤"), 0xFE0F),
                )
                self.assertTrue(snapshot.cell(column, 0).double_width)
                self.assertTrue(
                    snapshot.cell(
                        column + 1,
                        0,
                    ).double_width_continuation
                )

    def test_variation_selectors_remain_in_nonstandard_sequences(self):
        cases = (
            ("🧠︎", 2, (ord("🧠"), 0xFE0E)),
            ("x️", 1, (ord("x"), 0xFE0F)),
            ("n️̃", 1, (ord("n"), 0xFE0F, 0x0303)),
        )
        for text, width, grapheme in cases:
            with self.subTest(text=text), Shitty(
                columns=8,
                rows=2,
            ) as terminal:
                terminal.write_chunks(
                    *(character.encode() for character in text)
                )
                snapshot = terminal.model_snapshot()
                self.assertEqual(snapshot.cursor_x, width)
                self.assertEqual(snapshot.cell(0, 0).grapheme, grapheme)
                self.assertEqual(
                    snapshot.cell(0, 0).double_width,
                    width == 2,
                )

    def test_devanagari_width_growth_at_bottom_scrolls_atomically(self):
        cluster = "क्‍ष"
        with Shitty(columns=3, rows=2, save_lines=4) as terminal:
            terminal.write(b"top\x1b[2;3H")
            terminal.write_chunks(
                *(character.encode() for character in cluster)
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))
            self.assertEqual(snapshot.lines, ["   ", "क  "])
            self.assertEqual(
                snapshot.cell(0, 1).grapheme,
                tuple(map(ord, cluster)),
            )
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

            terminal.page_up()
            self.assertEqual(terminal.snapshot().lines, ["top", "   "])

    def test_overwriting_grapheme_lead_or_tail_clears_payload(self):
        cases = (
            ("⛈︎".encode() + b"\x1b[HA", "A"),
            ("👨‍👩‍👧".encode() + b"\x1b[HX", "X"),
            ("👨‍👩‍👧".encode() + b"\x1b[1;2HX", " X"),
        )
        for payload, expected in cases:
            with self.subTest(expected=expected), Shitty(
                columns=10,
                rows=2,
            ) as terminal:
                terminal.write(payload)
                snapshot = terminal.model_snapshot()
                self.assertTrue(snapshot.lines[0].startswith(expected))
                for cell in snapshot.cells[:2]:
                    self.assertEqual(cell.grapheme, ())
                    self.assertFalse(cell.double_width)
                    self.assertFalse(cell.double_width_continuation)


if __name__ == "__main__":
    unittest.main()

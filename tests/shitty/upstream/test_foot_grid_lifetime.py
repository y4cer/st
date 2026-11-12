# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of Foot URI-range and scrollback-lifetime units."""

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "grid URI put: adjacent cells merge",
    "grid URI put: repeating the head is a no-op",
    "grid URI put: replacing the head splits the range",
    "grid URI put: replacing the tail splits the range",
    "grid URI put: matching the tail extends its head",
    "grid URI put: matching the head extends its tail",
    "grid URI put: replacement can splice equal ranges apart",
    "grid URI erase: an empty row remains empty",
    "grid URI erase: a covering erase removes both ranges",
    "grid URI erase: an erase trims two neighboring ranges",
    "grid URI erase: an interior erase splits one range",
    "grid URI erase: splitting remains safe when storage moves",
    "erase scrollback: all non-visible rows are deleted",
    "erase scrollback: a selection touching history is cancelled",
    "erase scrollback: a visible-only selection is preserved",
    "erase scrollback: a sixel touching history is destroyed",
    "erase scrollback: a visible-only sixel is preserved",
)


BORDER = 2
RED_CELL = b"\x1bPq#1;2;100;0;0#1!6~-!6~\x1b\\"


def osc8(uri, text, link_id):
    return (
        b"\x1b]8;id=" + str(link_id).encode() + b";" + uri.encode()
        + b"\x1b\\" + text + b"\x1b]8;;\x1b\\"
    )


def put_link(terminal, column, uri, text=b"X", link_id=1):
    terminal.write(
        f"\x1b[1;{column + 1}H".encode() + osc8(uri, text, link_id)
    )


def links(terminal, columns):
    return tuple(terminal.hyperlink(column, 0) for column in range(columns))


def erase(terminal, start, count):
    terminal.write(f"\x1b[1;{start + 1}H\x1b[{count}X".encode())


def make_four_cell_source_state(terminal):
    put_link(terminal, 0, "https://foo.test", b"XXXX", 123)


def pixel(image, x, y):
    width, _, data = image
    offset = (y * width + x) * 3
    return tuple(data[offset:offset + 3])


def make_history(terminal, count=12):
    terminal.write(
        b"".join(f"row-{index}\r\n".encode() for index in range(count))
    )


class FootGridLifetimeTest(unittest.TestCase):
    def test_upstream_inventory_has_all_17_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 17)
        self.assertEqual(len(set(UPSTREAM_CASES)), 17)

    def test_adjacent_equal_uri_cells_form_one_public_run(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            snapshot = terminal.snapshot()
            ids = tuple(snapshot.cell(column, 0).hyperlink for column in range(4))
            self.assertNotEqual(ids[0], 0)
            self.assertEqual(ids, (ids[0],) * 4)
            self.assertEqual(links(terminal, 4), ("https://foo.test",) * 4)

    def test_repeating_the_uri_head_is_a_noop(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            before = terminal.snapshot().cell(0, 0).hyperlink
            put_link(terminal, 0, "https://foo.test", link_id=123)
            self.assertEqual(terminal.snapshot().cell(0, 0).hyperlink, before)
            self.assertEqual(links(terminal, 4), ("https://foo.test",) * 4)

    def test_replacing_the_uri_head_splits_the_run(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            put_link(terminal, 0, "https://head.test", link_id=456)
            self.assertEqual(
                links(terminal, 4),
                ("https://head.test",) + ("https://foo.test",) * 3,
            )

    def test_replacing_the_uri_tail_splits_the_run(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            put_link(terminal, 0, "https://head.test", link_id=456)
            put_link(terminal, 3, "https://tail.test", link_id=789)
            self.assertEqual(
                links(terminal, 4),
                ("https://head.test", "https://foo.test",
                 "https://foo.test", "https://tail.test"),
            )

    def test_matching_the_tail_extends_its_head(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            put_link(terminal, 0, "https://head.test", link_id=456)
            put_link(terminal, 3, "https://tail.test", link_id=789)
            put_link(terminal, 2, "https://tail.test", link_id=789)
            self.assertEqual(
                links(terminal, 4),
                ("https://head.test", "https://foo.test",
                 "https://tail.test", "https://tail.test"),
            )

    def test_matching_the_head_extends_its_tail(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            put_link(terminal, 0, "https://head.test", link_id=456)
            put_link(terminal, 3, "https://tail.test", link_id=789)
            put_link(terminal, 2, "https://tail.test", link_id=789)
            put_link(terminal, 1, "https://head.test", link_id=456)
            self.assertEqual(
                links(terminal, 4),
                ("https://head.test", "https://head.test",
                 "https://tail.test", "https://tail.test"),
            )

    def test_replacement_can_splice_equal_uri_runs_apart(self):
        with Shitty(columns=8, rows=2, save_lines=0) as terminal:
            make_four_cell_source_state(terminal)
            put_link(terminal, 0, "https://head.test", link_id=456)
            put_link(terminal, 3, "https://tail.test", link_id=789)
            put_link(terminal, 2, "https://tail.test", link_id=789)
            put_link(terminal, 1, "https://tail.test", link_id=789)
            put_link(terminal, 2, "https://splice.test", link_id=0)
            self.assertEqual(
                links(terminal, 4),
                ("https://head.test", "https://tail.test",
                 "https://splice.test", "https://tail.test"),
            )

    def test_erasing_an_empty_row_leaves_no_uri(self):
        with Shitty(columns=24, rows=2, save_lines=0) as terminal:
            erase(terminal, 0, 24)
            self.assertEqual(links(terminal, 24), ("",) * 24)

    def test_covering_erase_removes_both_uri_runs(self):
        with Shitty(columns=24, rows=2, save_lines=0) as terminal:
            put_link(terminal, 1, "https://one.test", b"A" * 10, 1)
            put_link(terminal, 11, "https://two.test", b"B" * 10, 2)
            erase(terminal, 1, 20)
            self.assertEqual(links(terminal, 24), ("",) * 24)

    def test_erase_trims_two_neighboring_uri_runs(self):
        with Shitty(columns=24, rows=2, save_lines=0) as terminal:
            put_link(terminal, 1, "https://one.test", b"A" * 10, 1)
            put_link(terminal, 11, "https://two.test", b"B" * 10, 2)
            erase(terminal, 5, 11)
            expected = (
                ("",) + ("https://one.test",) * 4 + ("",) * 11
                + ("https://two.test",) * 5 + ("",) * 3
            )
            self.assertEqual(links(terminal, 24), expected)

    def test_interior_erase_splits_one_uri_run(self):
        with Shitty(columns=16, rows=2, save_lines=0) as terminal:
            put_link(terminal, 1, "https://one.test", b"A" * 10, 1)
            erase(terminal, 5, 2)
            expected = (
                ("",) + ("https://one.test",) * 4 + ("",) * 2
                + ("https://one.test",) * 4 + ("",) * 5
            )
            self.assertEqual(links(terminal, 16), expected)

    def test_interior_split_remains_stable_after_later_edits(self):
        with Shitty(columns=16, rows=2, save_lines=0) as terminal:
            put_link(terminal, 1, "https://one.test", b"A" * 10, 1)
            erase(terminal, 5, 3)
            put_link(terminal, 12, "https://later.test", b"ZZ", 2)
            self.assertEqual(
                links(terminal, 16),
                (("",) + ("https://one.test",) * 4 + ("",) * 3
                 + ("https://one.test",) * 3 + ("",)
                 + ("https://later.test",) * 2 + ("",) * 2),
            )

    def test_erase_scrollback_deletes_history_but_not_the_page(self):
        with Shitty(columns=12, rows=5, save_lines=32) as terminal:
            make_history(terminal)
            before = terminal.model_snapshot().lines
            self.assertGreater(terminal.scrollback_state()[0], 0)
            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(terminal.model_snapshot().lines, before)

    def test_erase_scrollback_cancels_a_selection_touching_history(self):
        with Shitty(columns=12, rows=5, save_lines=32) as terminal:
            make_history(terminal)
            terminal.wheel_up(100)
            terminal.select_start(0, 0)
            terminal.select_update(5, 1)
            self.assertTrue(terminal.has_selection())
            terminal.write(b"\x1b[3J")
            self.assertFalse(terminal.has_selection())

    def test_erase_scrollback_preserves_a_visible_only_selection(self):
        with Shitty(columns=12, rows=5, save_lines=32) as terminal:
            make_history(terminal)
            terminal.select_start(0, 2)
            terminal.select_update(5, 3)
            before = terminal.select_finish()
            terminal.write(b"\x1b[3J")
            self.assertTrue(terminal.has_selection())
            self.assertEqual(terminal.select_finish(), before)

    def test_erase_scrollback_does_not_resurrect_a_hidden_sixel(self):
        with Shitty(
            columns=8, rows=4, save_lines=16, glyph_px=6, glyph_py=12,
        ) as terminal:
            terminal.write(b"\x1b[?25l" + RED_CELL)
            terminal.write(b"\r\n" * 8)
            terminal.write(b"\x1b[3J")
            terminal.write(b"\r\n" * 16)
            terminal.present()
            image = terminal.reference_image()
        self.assertNotIn(b"\xff\x00\x00", image[2])

    def test_erase_scrollback_preserves_a_visible_only_sixel(self):
        with Shitty(
            columns=8, rows=4, save_lines=16, glyph_px=6, glyph_py=12,
        ) as terminal:
            make_history(terminal, 8)
            terminal.write(b"\x1b[1;1H\x1b[?25l" + RED_CELL)
            terminal.write(b"\x1b[3J")
            terminal.present()
            image = terminal.reference_image()
        self.assertEqual(pixel(image, BORDER, BORDER), (255, 0, 0))


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows


UPSTREAM_CASES = (
    "PageList resize reflow more cols clears kitty placeholder",
    "PageList resize reflow wrap moves kitty placeholder",
    "PageList reset",
    "PageList reset invalidates stale untracked refs even if node memory is reused",
    "PageList reset across two pages",
    "PageList reset moves tracked pins and marks them as garbage",
    "PageList clears history",
    "PageList resize reflow grapheme map capacity exceeded",
    "PageList resize grow cols with unwrap fixes viewport pin",
    "PageList grow reuses non-standard page without leak",
    "PageList grow non-standard page prune protection",
    "PageList resize (no reflow) more cols remaps pins in backfill path",
    "PageList compact pool page produces exact-size heap page",
    "PageList compact then grow allocates new page",
    "PageList compact then reset frees heap pages",
    "PageList compact then clone",
    "PageList compact oversized page",
    "PageList destroyed pool page reuse is zeroed",
    "PageList increaseCapacity from zero-capacity dimensions",
    "PageList compact after increaseCapacity",
)


KITTY_PLACEHOLDER = "\U0010eeee"


def numbered_lines(first, last, width=3):
    return b"\r\n".join(
        str(value).zfill(width).encode()
        for value in range(first, last + 1)
    )


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


class GhosttyPageListResetCompactTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_placeholder_rows_created_by_shrink_do_not_taint_the_blank_row_after_widening(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write((KITTY_PLACEHOLDER * 3).encode())

            terminal.resize(2, 2)
            terminal.resize(4, 2)

            self.assertEqual(visible_lines(terminal), (KITTY_PLACEHOLDER * 3, ""))

    def test_wrapping_moves_a_placeholder_stream_to_the_new_physical_row(self):
        with Shitty(columns=4, rows=2, save_lines=0) as terminal:
            terminal.write(b"\x1b[1;3H" + KITTY_PLACEHOLDER.encode())

            terminal.resize(2, 2)

            self.assertEqual(visible_lines(terminal), ("", KITTY_PLACEHOLDER))

    def test_hard_reset_restores_an_empty_active_screen_and_home_cursor(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(numbered_lines(1, 8) + b"\x1bc")
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("", "", ""))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(snapshot.view_offset, 0)

    def test_repeated_hard_reset_never_revalidates_an_old_screen_generation(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            for value in range(12):
                terminal.write(f"OLD-{value}".encode() + b"\x1bc")
            terminal.write(b"CURRENT")

            self.assertEqual(visible_lines(terminal), ("CURRENT", "", ""))
            self.assertEqual(terminal.all_text(), ("CURRENT", "", ""))

    def test_hard_reset_rebuilds_a_screen_larger_than_one_storage_page(self):
        with Shitty(columns=8, rows=300, save_lines=0) as terminal:
            terminal.write(b"\x1b[300;1HOLD\x1bcNEW")
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (8, 300))
            self.assertEqual(snapshot.lines[0].rstrip(), "NEW")
            self.assertEqual(snapshot.lines[-1].rstrip(), "")

    def test_hard_reset_drops_viewport_and_selection_anchors_from_old_storage(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 12))
            terminal.wheel_up(5)
            terminal.select_start(0, 0)
            terminal.select_update(2, 0)

            terminal.write(b"\x1bc")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.view_offset, 0)
            self.assertEqual(snapshot.selection, (-1, -1, -1, -1))
            self.assertEqual(terminal.select_finish(), b"")

    def test_hard_reset_discards_all_history_before_accepting_new_rows(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 12) + b"\x1bc")
            terminal.write(numbered_lines(101, 104))

            self.assertEqual(terminal.all_text(), ("101", "102", "103", "104"))
            self.assertNotIn("12", terminal.all_text())

    def test_dense_grapheme_storage_survives_cross_page_reflow(self):
        acute = "A\N{COMBINING ACUTE ACCENT}"
        grave = "B\N{COMBINING GRAVE ACCENT}"
        rows = tuple(acute if index % 2 == 0 else grave for index in range(320))
        with Shitty(columns=4, rows=10, save_lines=400) as terminal:
            terminal.write(b"\r\n".join(row.encode() for row in rows))

            terminal.resize(2, 10)

            self.assertEqual(terminal.all_text(), rows)
            terminal.wheel_up(10_000)
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, tuple(map(ord, acute)))

    def test_widening_soft_wrapped_history_keeps_a_parked_viewport_valid(self):
        with Shitty(columns=2, rows=10, save_lines=40) as terminal:
            terminal.write(b"A" * 80)
            terminal.wheel_up(2)

            terminal.resize(4, 10)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.view_offset, 0)
            self.assertTrue(all(line.rstrip("A ") == "" for line in snapshot.lines))
            terminal.wheel_down(10_000)
            self.assertEqual("".join(terminal.all_text()).strip(), "A" * 80)

    def test_bounded_pruning_of_dense_graphemes_keeps_the_newest_rows_readable(self):
        cluster = "x\N{COMBINING ACUTE ACCENT}\N{COMBINING DOT BELOW}"
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(b"\r\n".join(cluster.encode() for _ in range(300)))

            self.assertEqual(terminal.all_text(), tuple([cluster] * 23))
            snapshot = terminal.model_snapshot()
            self.assertEqual(visible_lines(terminal), ("x", "x", "x"))
            self.assertEqual(snapshot.cell(0, 0).grapheme, tuple(map(ord, cluster)))
            self.assertEqual(snapshot.cell(0, 2).grapheme, tuple(map(ord, cluster)))

    def test_pruning_never_reduces_the_live_screen_below_its_configured_height(self):
        with Shitty(columns=8, rows=300, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 599))
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.rows, 300)
            self.assertEqual(len(snapshot.lines), 300)
            self.assertEqual(snapshot.lines[0].rstrip(), "300")
            self.assertEqual(snapshot.lines[-1].rstrip(), "599")

    def test_selection_pin_follows_a_history_row_through_width_growth(self):
        with Shitty(columns=5, rows=300, save_lines=120) as terminal:
            terminal.write(numbered_lines(0, 399))
            terminal.wheel_up(100)
            self.assertEqual(visible_lines(terminal)[0], "000")
            terminal.select_start(0, 150)
            terminal.select_update(3, 150)

            terminal.resize(6, 300)

            self.assertEqual(terminal.select_finish(), b"150")

    def test_plain_single_page_snapshot_has_exact_public_geometry_and_content(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(b"\x1b[3;2HX")
            snapshot = terminal.model_snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (80, 24))
            self.assertEqual(snapshot.cell(1, 2).char, "X")
            self.assertEqual(snapshot.lines[2][1], "X")

    def test_growing_past_a_full_active_page_preserves_the_old_page_and_new_row(self):
        with Shitty(columns=8, rows=24, save_lines=1) as terminal:
            terminal.write(numbered_lines(0, 24))

            self.assertEqual(len(terminal.all_text()), 25)
            self.assertEqual(terminal.all_text()[0], "000")
            self.assertEqual(terminal.all_text()[-1], "024")

    def test_hard_reset_reclaims_rich_storage_before_rebuilding_the_screen(self):
        rich = osc8(b"https://old.example") + b"\x1b[1mA\xcc\x81" + osc8()
        with Shitty(columns=8, rows=3, save_lines=50) as terminal:
            terminal.write(b"\r\n".join(rich for _ in range(60)) + b"\x1bcNEW")

            self.assertEqual(visible_lines(terminal), ("NEW", "", ""))
            self.assertEqual(terminal.hyperlink(0, 0), "")
            self.assertFalse(terminal.snapshot().cell(0, 0).bold)

    def test_model_snapshot_of_rich_content_is_independent_of_later_mutation(self):
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.write(osc8(b"https://example.test") + b"\x1b[1mA\xcc\x81" + osc8())
            cloned = terminal.model_snapshot()

            terminal.write(b"\x1bcREPLACED")

            self.assertEqual(cloned.cell(0, 0).grapheme, (ord("A"), 0x0301))
            self.assertTrue(cloned.cell(0, 0).bold)
            self.assertNotEqual(cloned.cell(0, 0).hyperlink, 0)

    def test_large_rich_page_keeps_content_and_selection_through_resize(self):
        with Shitty(columns=40, rows=300, save_lines=20) as terminal:
            payload = bytearray()
            for row in range(320):
                payload.extend(f"\x1b[38;2;{row % 256};1;2m{row:03}".encode())
                payload.extend(b"A\xcc\x81\r\n")
            terminal.write(bytes(payload[:-2]))
            terminal.select_start(0, 150)
            terminal.select_update(3, 150)

            terminal.resize(41, 300)
            snapshot = terminal.model_snapshot()

            self.assertEqual(terminal.select_finish(), b"170")
            self.assertEqual(snapshot.lines[-1].rstrip(), "319A")
            self.assertEqual(snapshot.cell(3, 299).grapheme, (ord("A"), 0x0301))

    def test_reused_blank_storage_has_no_old_cell_metadata(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            rich = osc8(b"https://old.example") + b"\x1b[1;4mA\xcc\x81" + osc8()
            terminal.write(b"\r\n".join(rich for _ in range(30)) + b"\x1bc")
            cell = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(cell.char, " ")
            self.assertEqual(cell.grapheme, ())
            self.assertFalse(cell.bold)
            self.assertFalse(cell.underline)
            self.assertEqual(cell.hyperlink, 0)
            self.assertFalse(cell.drawn)

    def test_first_rich_cell_allocates_every_zero_capacity_metadata_family(self):
        with Shitty(columns=8, rows=3, save_lines=0) as terminal:
            terminal.write(
                osc8(b"https://example.test/first")
                + b"\x1b[1;38;2;7;8;9mA\xcc\x81"
                + osc8()
            )
            cell = terminal.model_snapshot().cell(0, 0)

            self.assertEqual(cell.grapheme, (ord("A"), 0x0301))
            self.assertTrue(cell.bold)
            self.assertEqual(cell.foreground, (7, 8, 9))
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.test/first")

    def test_history_reclamation_after_rich_capacity_growth_accepts_plain_cells(self):
        rich = osc8(b"https://old.example") + b"\x1b[1mA\xcc\x81" + osc8()
        with Shitty(columns=8, rows=3, save_lines=30) as terminal:
            terminal.write(b"\r\n".join(rich for _ in range(60)))
            terminal.write(b"\x1b[3J\x1b[H\x1b[0mPLAIN")
            snapshot = terminal.model_snapshot()

            self.assertEqual(terminal.all_text(), ("PLAIN", "A\N{COMBINING ACUTE ACCENT}", "A\N{COMBINING ACUTE ACCENT}"))
            self.assertEqual(snapshot.lines[0].rstrip(), "PLAIN")
            self.assertEqual(snapshot.cell(0, 0).char, "P")
            self.assertEqual(snapshot.cell(0, 0).grapheme, ())
            self.assertFalse(snapshot.cell(0, 0).bold)
            self.assertEqual(terminal.hyperlink(0, 0), "")


if __name__ == "__main__":
    unittest.main()

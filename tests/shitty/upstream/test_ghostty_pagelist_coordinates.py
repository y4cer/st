# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty, put_rows, run_startup_failure


UPSTREAM_CASES = (
    "PageList cold compression continues after an incompressible page",
    "PageList compression restores through page access",
    "PageList compression uses temporary scratch for oversized pages",
    "PageList compression leaves incompressible pages resident",
    "PageList reset discards malformed compressed data",
    "PageList deinit discards malformed compressed data",
    "PageList prune reuses malformed compressed page memory",
    "PageList",
    "PageList init error",
    "PageList init rows across two pages",
    "PageList init more than max cols",
    "PageList pointFromPin active no history",
    "PageList pointFromPin active with history",
    "PageList pointFromPin active from prior page",
    "PageList pointFromPin traverse pages",
    "PageList pointFromPin rejects overflowing screen coordinate",
    "PageList active after grow",
    "PageList grow allows exceeding max size for active area",
    "PageList grow prune required with a single page",
    "PageList scrollbar with max_size 0 after grow",
)


def numbered_lines(first, last, width=0):
    values = []
    for value in range(first, last + 1):
        text = str(value).zfill(width) if width else str(value)
        values.append(text.encode())
    return b"\r\n".join(values)


def visible_lines(terminal):
    return tuple(line.rstrip() for line in terminal.snapshot().lines)


def osc8(uri=b""):
    return b"\x1b]8;;" + uri + b"\x1b\\"


class GhosttyPageListCoordinatesTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_dense_history_does_not_block_later_cold_rows(self):
        with Shitty(columns=12, rows=4, save_lines=240) as terminal:
            payload = bytearray()
            for index in range(180):
                payload.extend(
                    f"\x1b[38;2;{index % 256};{(index * 7) % 256};{(index * 13) % 256}m{index:03}\r\n".encode()
                )
            payload.extend(b"180")
            terminal.write(bytes(payload))

            terminal.wheel_up(10_000)
            self.assertEqual(visible_lines(terminal), ("000", "001", "002", "003"))
            terminal.wheel_down(10_000)
            self.assertEqual(visible_lines(terminal), ("177", "178", "179", "180"))

    def test_history_access_restores_text_style_and_hyperlink(self):
        uri = "https://example.test/cold-access"
        with Shitty(columns=10, rows=3, save_lines=80) as terminal:
            terminal.write(b"\x1b[1m" + osc8(uri.encode()) + b"linked" + osc8())
            terminal.write(b"\x1b[0m\r\n" + numbered_lines(1, 60))
            terminal.wheel_up(10_000)
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0].rstrip(), "linked")
            self.assertTrue(snapshot.cell(0, 0).bold)
            self.assertEqual(terminal.hyperlink(0, 0), uri)

    def test_oversized_auxiliary_storage_survives_cold_history(self):
        with Shitty(columns=4, rows=3, save_lines=160) as terminal:
            payload = bytearray()
            for index in range(100):
                uri = (f"https://example.test/{index}/" + "x" * 512).encode()
                payload.extend(osc8(uri) + b"X" + osc8() + b"\r\n")
            payload.extend(b"end")
            terminal.write(bytes(payload))
            terminal.wheel_up(10_000)

            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            self.assertTrue(terminal.hyperlink(0, 0).startswith("https://example.test/0/"))

    def test_high_entropy_rendition_history_remains_resident_or_readable(self):
        with Shitty(columns=6, rows=3, save_lines=260) as terminal:
            payload = bytearray()
            for index in range(256):
                payload.extend(
                    f"\x1b[38;2;{index};{255 - index};{index ^ 0x55}mX{index:03}\r\n".encode()
                )
            payload.extend(b"tail")
            terminal.write(bytes(payload))

            terminal.wheel_up(128)
            self.assertTrue(visible_lines(terminal)[0].startswith("X"))
            terminal.wheel_down(128)
            self.assertEqual(visible_lines(terminal)[-1], "tail")

    def test_hard_reset_discards_old_storage_without_decoding_it(self):
        with Shitty(columns=8, rows=3, save_lines=100) as terminal:
            terminal.write(numbered_lines(1, 80))
            terminal.write(b"\x1bcNEW")

            self.assertEqual(visible_lines(terminal), ("NEW", "", ""))
            self.assertNotIn("80", terminal.all_text())

    def test_session_destruction_accepts_an_unfinished_cold_payload(self):
        completed = False
        with Shitty(columns=8, rows=3, save_lines=100) as terminal:
            terminal.write(numbered_lines(1, 80))
            terminal.write(b"\x1b]8;;https://example.test/unfinished")
        completed = True

        self.assertTrue(completed)

    def test_bounded_pruning_reuses_storage_and_keeps_new_cells_valid(self):
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(numbered_lines(0, 100))
            terminal.write(b"\r\n\x1b[1;4mFINAL")
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[-1].rstrip(), "FINAL")
            self.assertTrue(snapshot.cell(0, 2).bold)
            self.assertTrue(snapshot.cell(0, 2).underline)
            self.assertEqual(terminal.scrollback_state()[0], 4)

    def test_initial_page_geometry_and_scrollbar_are_consistent(self):
        with Shitty(columns=80, rows=24, save_lines=100) as terminal:
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (80, 24))
            self.assertEqual(len(snapshot.cells), 80 * 24)
            self.assertEqual(terminal.scrollback_state(), (0, 24, 24, 0))

    def test_invalid_initial_dimensions_fail_without_a_live_session(self):
        for geometry in ("0x3", "3x0"):
            with self.subTest(geometry=geometry):
                result = run_startup_failure(
                    extra_arguments=("-geometry", geometry)
                )
                self.assertEqual(result.returncode, 255)
                self.assertIn(b"-geometry", result.stdout)

    def test_large_initial_height_exposes_every_active_cell(self):
        with Shitty(columns=8, rows=200, save_lines=0) as terminal:
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (8, 200))
            self.assertEqual(len(snapshot.cells), 1600)
            self.assertEqual(terminal.scrollback_state(), (0, 200, 200, 0))

    def test_nonstandard_initial_width_has_complete_storage(self):
        with Shitty(columns=2048, rows=2, save_lines=0) as terminal:
            terminal.write(b"A\x1b[2048GZ")
            snapshot = terminal.snapshot()

            self.assertEqual((snapshot.columns, snapshot.rows), (2048, 2))
            self.assertEqual(snapshot.cell(0, 0).char, "A")
            self.assertEqual(snapshot.cell(2047, 0).char, "Z")

    def test_active_coordinates_without_history_map_directly(self):
        with Shitty(columns=10, rows=4, save_lines=0) as terminal:
            terminal.write(put_rows(b"zero", b"one", b"two", b"three"))
            terminal.select_start(1, 2)
            terminal.select_update(3, 2)

            self.assertEqual(terminal.selection_state()["raw"], (1, 2, 3, 2))
            self.assertEqual(terminal.select_finish(), b"wo")

    def test_active_coordinates_ignore_rows_in_history(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 10))
            snapshot = terminal.snapshot()

            self.assertEqual(visible_lines(terminal), ("8", "9", "10"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 2))
            self.assertEqual(snapshot.cell(0, 0).char, "8")

    def test_history_coordinates_do_not_alias_the_active_page(self):
        with Shitty(columns=8, rows=3, save_lines=100) as terminal:
            terminal.write(numbered_lines(0, 79, width=2))
            terminal.wheel_up(10_000)
            top = visible_lines(terminal)
            terminal.wheel_down(10_000)
            active = visible_lines(terminal)

            self.assertEqual(top, ("00", "01", "02"))
            self.assertEqual(active, ("77", "78", "79"))

    def test_public_coordinates_traverse_long_history(self):
        with Shitty(columns=8, rows=5, save_lines=300) as terminal:
            terminal.write(numbered_lines(0, 249, width=3))
            terminal.wheel_up(123)
            terminal.select_start(0, 1)
            terminal.select_update(3, 3)

            self.assertEqual(terminal.select_finish(), b"123\n124\n125")

    def test_overflowing_public_coordinate_is_clamped_not_wrapped(self):
        with Shitty(columns=8, rows=3, save_lines=10) as terminal:
            terminal.write(put_rows(b"one", b"two", b"three"))
            terminal.select_start(0, 0)
            terminal.select_update(2_000_000_000, 2_000_000_000)

            self.assertEqual(terminal.selection_state()["raw"], (0, 0, 8, 2))
            self.assertEqual(terminal.select_finish(), b"one\ntwo\nthree")

    def test_active_area_and_scrollbar_advance_after_growth(self):
        with Shitty(columns=8, rows=3, save_lines=20) as terminal:
            terminal.write(numbered_lines(1, 10))

            self.assertEqual(terminal.scrollback_state(), (7, 10, 3, 7))
            self.assertEqual(visible_lines(terminal), ("8", "9", "10"))

    def test_zero_history_still_allocates_the_entire_active_area(self):
        with Shitty(columns=5, rows=50, save_lines=0) as terminal:
            terminal.write(numbered_lines(1, 50))
            snapshot = terminal.snapshot()

            self.assertEqual(len(snapshot.cells), 250)
            self.assertEqual(visible_lines(terminal)[0], "1")
            self.assertEqual(visible_lines(terminal)[-1], "50")
            self.assertEqual(terminal.scrollback_state()[0], 0)

    def test_required_pruning_keeps_scrollbar_and_active_rows_valid(self):
        with Shitty(columns=80, rows=24, save_lines=1) as terminal:
            terminal.write(numbered_lines(0, 80))
            state = terminal.scrollback_state()

            self.assertEqual(state, (1, 25, 24, 1))
            self.assertEqual(visible_lines(terminal)[-1], "80")

    def test_zero_history_scrollbar_stays_at_the_active_area(self):
        with Shitty(columns=80, rows=24, save_lines=0) as terminal:
            terminal.write(numbered_lines(0, 40))

            self.assertEqual(terminal.scrollback_state(), (0, 24, 24, 0))
            terminal.wheel_up(100)
            self.assertEqual(terminal.snapshot().view_offset, 0)


if __name__ == "__main__":
    unittest.main()

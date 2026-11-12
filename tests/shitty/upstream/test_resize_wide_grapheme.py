# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ResizeWideGraphemeTest(unittest.TestCase):
    def test_shrink_never_leaves_wide_lead_without_continuation(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write("abc界".encode())
            terminal.resize(4, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "abc ")
            self.assertFalse(snapshot.cell(3, 0).double_width)
            self.assertFalse(snapshot.cell(3, 0).double_width_continuation)

    def test_shrink_keeps_a_complete_wide_cell(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write("ab界cd".encode())
            terminal.resize(4, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "ab界 ")
            self.assertTrue(snapshot.cell(2, 0).double_width)
            self.assertTrue(snapshot.cell(3, 0).double_width_continuation)

    def test_grapheme_payload_survives_width_and_height_resize(self):
        cluster = "👩\N{ZERO WIDTH JOINER}💻"
        with Shitty(columns=8, rows=3, save_lines=4) as terminal:
            terminal.write(("a" + cluster + "b\r\nsecond\r\nthird").encode())
            terminal.resize(6, 2)
            terminal.resize(9, 4)
            snapshot = terminal.snapshot()
            terminal.select_start(1, 0)
            terminal.select_update(3, 0)
            self.assertEqual(terminal.select_finish(), cluster.encode())
            self.assertTrue(snapshot.cell(1, 0).double_width)
            self.assertTrue(snapshot.cell(2, 0).double_width_continuation)

    def test_reflow_preserves_wide_grapheme_hyperlink_and_selection(self):
        cluster = "👩\N{ZERO WIDTH JOINER}💻"
        codepoints = tuple(map(ord, cluster))
        open_link = b"\x1b]8;id=wide;https://example.test/wide\x1b\\"
        close_link = b"\x1b]8;;\x1b\\"
        with Shitty(columns=8, rows=3, save_lines=6) as terminal:
            terminal.write(
                b"ab" + open_link + cluster.encode() + close_link + b"cdef"
            )
            terminal.select_start(2, 0)
            terminal.select_update(4, 0)
            identity = terminal.model_snapshot().cell(2, 0).hyperlink
            self.assertNotEqual(identity, 0)

            for columns, rows in ((5, 2), (10, 4), (6, 3), (8, 3)):
                terminal.resize(columns, rows)
                history = terminal.scrollback_state()[0]
                terminal.wheel_up(history)
                snapshot = terminal.model_snapshot()
                leads = [
                    (index, cell)
                    for index, cell in enumerate(snapshot.cells)
                    if cell.grapheme == codepoints
                ]
                self.assertEqual(len(leads), 1)
                index, lead = leads[0]
                self.assertTrue(lead.double_width)
                self.assertEqual(lead.hyperlink, identity)
                self.assertTrue(snapshot.cells[index + 1].double_width_continuation)
                self.assertEqual(
                    terminal.hyperlink_bytes(
                        index % snapshot.columns,
                        index // snapshot.columns,
                    ),
                    b"https://example.test/wide",
                )
                self.assertEqual(terminal.select_finish(), cluster.encode())
                terminal.wheel_down(history)

            self.assertEqual(terminal.select_finish(), cluster.encode())


if __name__ == "__main__":
    unittest.main()

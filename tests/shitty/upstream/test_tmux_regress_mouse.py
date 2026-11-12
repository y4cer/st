# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public mouse adaptations of current tmux mouse regress scripts."""

import unittest

from harness import Shitty


CONTROL = 2


PORTED_CASES = (
    ("regress/format-mouse.sh:binding-fired", "test_format_binding_fires"),
    ("regress/format-mouse.sh:mouse-x", "test_format_mouse_x"),
    ("regress/format-mouse.sh:mouse-y", "test_format_mouse_y"),
    ("regress/format-mouse.sh:word-alpha", "test_format_word_alpha"),
    ("regress/format-mouse.sh:line", "test_format_line"),
    ("regress/format-mouse.sh:word-beta", "test_format_word_beta"),
    (
        "regress/format-mouse.sh:copy-mode-word-beta",
        "test_format_history_word_beta",
    ),
    ("regress/format-mouse.sh:hyperlink", "test_format_hyperlink"),
    (
        "regress/menu-mouse.sh:status-top-choice",
        "test_menu_status_top_coordinates",
    ),
    (
        "regress/new-pane-mouse.sh:first-drag-stream",
        "test_first_drag_stream",
    ),
    (
        "regress/new-pane-mouse.sh:first-drag-control",
        "test_first_drag_control",
    ),
    (
        "regress/new-pane-mouse.sh:first-drag-motion",
        "test_first_drag_motion",
    ),
    (
        "regress/new-pane-mouse.sh:first-drag-release",
        "test_first_drag_release",
    ),
    (
        "regress/new-pane-mouse.sh:first-drag-end",
        "test_first_drag_end",
    ),
    (
        "regress/new-pane-mouse.sh:right-click",
        "test_right_click_coordinates",
    ),
    (
        "regress/new-pane-mouse.sh:right-menu-key",
        "test_right_menu_key",
    ),
    (
        "regress/new-pane-mouse.sh:empty-drag-stream",
        "test_empty_drag_stream",
    ),
    (
        "regress/new-pane-mouse.sh:empty-drag-start",
        "test_empty_drag_start",
    ),
    (
        "regress/new-pane-mouse.sh:empty-drag-end",
        "test_empty_drag_end",
    ),
)


class TmuxRegressMouseTest(unittest.TestCase):
    def _click_packets(self, column, row, button=0, modifiers=0):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"\x1b[?1000h\x1b[?1006h")
            x = column + 1
            y = row + 1
            terminal.button(button, True, x=x, y=y, modifiers=modifiers)
            terminal.button(button, False, x=x, y=y, modifiers=modifiers)
            return terminal.read_input()

    def _drag_packets(self, start, end):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.write(b"\x1b[?1002h\x1b[?1006h")
            start_x, start_y = start
            end_x, end_y = end
            terminal.button(
                0,
                True,
                x=start_x + 1,
                y=start_y + 1,
                modifiers=CONTROL,
            )
            terminal.pointer(
                end_x + 1,
                end_y + 1,
                modifiers=CONTROL,
            )
            terminal.button(
                0,
                False,
                x=end_x + 1,
                y=end_y + 1,
                modifiers=CONTROL,
            )
            return terminal.read_input()

    def _selected_cycle(self, column, clicks):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"alpha beta gamma")
            selected = b""
            for index in range(clicks):
                timestamp = 1 + index / 10
                terminal.button(
                    0,
                    True,
                    x=column + 1,
                    y=2,
                    time=timestamp,
                )
                selected = terminal.button(
                    0,
                    False,
                    x=column + 1,
                    y=2,
                    time=timestamp + 0.01,
                )
            return selected

    def test_upstream_inventory_has_19_distinct_executable_cases(self):
        self.assertEqual(len(PORTED_CASES), 19)
        self.assertEqual(len({source for source, _ in PORTED_CASES}), 19)
        self.assertEqual(len({test for _, test in PORTED_CASES}), 19)
        for _, test in PORTED_CASES:
            self.assertTrue(callable(getattr(self, test)))

    def test_format_binding_fires(self):
        self.assertEqual(
            self._click_packets(3, 1),
            b"\x1b[<0;3;1M\x1b[<0;3;1m",
        )

    def test_format_mouse_x(self):
        packets = self._click_packets(3, 1)
        self.assertEqual(packets.split(b";")[1], b"3")

    def test_format_mouse_y(self):
        packets = self._click_packets(3, 1)
        self.assertTrue(packets.startswith(b"\x1b[<0;3;1M"))

    def test_format_word_alpha(self):
        self.assertEqual(self._selected_cycle(3, 2), b"alpha")

    def test_format_line(self):
        self.assertEqual(self._selected_cycle(3, 3), b"alpha beta gamma")

    def test_format_word_beta(self):
        self.assertEqual(self._selected_cycle(8, 2), b"beta")

    def test_format_history_word_beta(self):
        with Shitty(columns=20, rows=2, save_lines=4) as terminal:
            terminal.write(b"alpha beta gamma\r\nline2\r\nline3")
            terminal.page_up()
            terminal.button(0, True, x=9, y=2, time=1)
            terminal.button(0, False, x=9, y=2, time=1.01)
            terminal.button(0, True, x=9, y=2, time=1.1)
            selected = terminal.button(0, False, x=9, y=2, time=1.11)
            self.assertEqual(selected, b"beta")

    def test_format_hyperlink(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b]8;;http://example.com\x1b\\LINKED"
                b"\x1b]8;;\x1b\\"
            )
            terminal.button(0, True, x=4, y=2, modifiers=CONTROL)
            self.assertEqual(
                terminal.desktop_state()["opened_uri"],
                b"http://example.com",
            )

    def test_menu_status_top_coordinates(self):
        self.assertEqual(
            self._click_packets(8, 6),
            b"\x1b[<0;8;6M\x1b[<0;8;6m",
        )

    def test_first_drag_stream(self):
        self.assertEqual(
            self._drag_packets((3, 1), (10, 5)),
            b"\x1b[<16;3;1M\x1b[<48;10;5M\x1b[<16;10;5m",
        )

    def test_first_drag_control(self):
        self.assertTrue(
            self._drag_packets((3, 1), (10, 5)).startswith(
                b"\x1b[<16;3;1M"
            )
        )

    def test_first_drag_motion(self):
        self.assertIn(
            b"\x1b[<48;10;5M",
            self._drag_packets((3, 1), (10, 5)),
        )

    def test_first_drag_release(self):
        self.assertTrue(
            self._drag_packets((3, 1), (10, 5)).endswith(
                b"\x1b[<16;10;5m"
            )
        )

    def test_first_drag_end(self):
        packets = self._drag_packets((3, 1), (10, 5))
        self.assertEqual(packets.count(b";10;5"), 2)

    def test_right_click_coordinates(self):
        packets = self._click_packets(20, 8, button=1)
        self.assertEqual(packets, b"\x1b[<2;20;8M\x1b[<2;20;8m")

    def test_right_menu_key(self):
        with Shitty(columns=80, rows=24) as terminal:
            terminal.frontend_text_event("p")
            self.assertEqual(terminal.read_input(), b"p")

    def test_empty_drag_stream(self):
        self.assertEqual(
            self._drag_packets((40, 10), (50, 15)),
            b"\x1b[<16;40;10M\x1b[<48;50;15M\x1b[<16;50;15m",
        )

    def test_empty_drag_start(self):
        self.assertTrue(
            self._drag_packets((40, 10), (50, 15)).startswith(
                b"\x1b[<16;40;10M"
            )
        )

    def test_empty_drag_end(self):
        self.assertTrue(
            self._drag_packets((40, 10), (50, 15)).endswith(
                b"\x1b[<16;50;15m"
            )
        )


if __name__ == "__main__":
    unittest.main()

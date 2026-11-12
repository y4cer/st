# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of xterm.js InputHandler cases 161 through 180."""

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "OSC 10 foreground set and query events",
    "OSC 110 restores the foreground",
    "OSC 11 background set and query events",
    "OSC 111 restores the background",
    "OSC 12 cursor set and query events",
    "OSC 112 restores the cursor color",
    "EL 0 preserves a cursor at buffer.cols",
    "EL 1 preserves a cursor at buffer.cols",
    "EL 2 preserves a cursor at buffer.cols",
    "ED 0 preserves a cursor at buffer.cols",
    "ED 1 preserves a cursor at buffer.cols",
    "ED 2 preserves a cursor at buffer.cols",
    "ED 3 preserves a cursor at buffer.cols",
    "a following sequence never advances beyond buffer.cols",
    "ED 3 unlocks a viewport whose history was erased",
    "ED 3 on a resized alternate buffer preserves the primary viewport",
    "DECSED and DECSEL treat cells as unprotected by default",
    "DECSCA 1 protects cells from DECSEL",
    "DECSCA 1 protects cells from DECSED",
    "DECRQSS reports the DECSCA state",
)


def dynamic_query(terminal, *commands):
    terminal.write(
        b"".join(f"\x1b]{command};?\x1b\\".encode()
                 for command in commands)
    )
    return terminal.read_input()


def set_dynamic(terminal, command, *values):
    payload = b";".join(value.encode() for value in values)
    terminal.write(f"\x1b]{command};".encode() + payload + b"\x1b\\")


class XtermJsInputHandlerColorsEraseTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_osc10_foreground_set_and_query_events(self):
        with Shitty(columns=10, rows=5) as terminal:
            foreground = dynamic_query(terminal, 10)
            background = dynamic_query(terminal, 11)
            cursor = dynamic_query(terminal, 12)

            terminal.write(b"\x1b]10;?;?;?;?\x1b\\")
            self.assertEqual(
                terminal.read_input(), foreground + background + cursor
            )

            set_dynamic(terminal, 10, "rgb:01/02/03")
            self.assertEqual(
                dynamic_query(terminal, 10),
                b"\x1b]10;rgb:0101/0202/0303\x1b\\",
            )
            set_dynamic(terminal, 10, "#aabbcc")
            self.assertEqual(
                dynamic_query(terminal, 10),
                b"\x1b]10;rgb:aaaa/bbbb/cccc\x1b\\",
            )

            set_dynamic(
                terminal, 10,
                "rgb:aa/bb/cc", "#001122", "rgb:12/34/56",
            )
            self.assertEqual(
                dynamic_query(terminal, 10, 11, 12),
                b"\x1b]10;rgb:aaaa/bbbb/cccc\x1b\\"
                b"\x1b]11;rgb:0000/1111/2222\x1b\\"
                b"\x1b]12;rgb:1212/3434/5656\x1b\\",
            )

    def test_osc110_restores_foreground_color(self):
        with Shitty(columns=10, rows=5) as terminal:
            original = dynamic_query(terminal, 10)
            set_dynamic(terminal, 10, "#010203")
            terminal.write(b"\x1b]110\x1b\\")
            self.assertEqual(dynamic_query(terminal, 10), original)

    def test_osc11_background_set_and_query_events(self):
        with Shitty(columns=10, rows=5) as terminal:
            background = dynamic_query(terminal, 11)
            cursor = dynamic_query(terminal, 12)

            terminal.write(b"\x1b]11;?;?;?;?\x1b\\")
            self.assertEqual(terminal.read_input(), background + cursor)

            set_dynamic(terminal, 11, "rgb:01/02/03")
            self.assertEqual(
                dynamic_query(terminal, 11),
                b"\x1b]11;rgb:0101/0202/0303\x1b\\",
            )
            set_dynamic(terminal, 11, "#aabbcc")
            self.assertEqual(
                dynamic_query(terminal, 11),
                b"\x1b]11;rgb:aaaa/bbbb/cccc\x1b\\",
            )

            set_dynamic(terminal, 11, "#001122", "rgb:12/34/56")
            self.assertEqual(
                dynamic_query(terminal, 11, 12),
                b"\x1b]11;rgb:0000/1111/2222\x1b\\"
                b"\x1b]12;rgb:1212/3434/5656\x1b\\",
            )

    def test_osc111_restores_background_color(self):
        with Shitty(columns=10, rows=5) as terminal:
            original = dynamic_query(terminal, 11)
            set_dynamic(terminal, 11, "#010203")
            terminal.write(b"\x1b]111\x1b\\")
            self.assertEqual(dynamic_query(terminal, 11), original)

    def test_osc12_cursor_color_set_and_query_events(self):
        with Shitty(columns=10, rows=5) as terminal:
            cursor = dynamic_query(terminal, 12)

            terminal.write(b"\x1b]12;?;?;?;?\x1b\\")
            self.assertEqual(terminal.read_input(), cursor)

            set_dynamic(terminal, 12, "rgb:01/02/03")
            self.assertEqual(
                dynamic_query(terminal, 12),
                b"\x1b]12;rgb:0101/0202/0303\x1b\\",
            )
            set_dynamic(terminal, 12, "#aabbcc")
            self.assertEqual(
                dynamic_query(terminal, 12),
                b"\x1b]12;rgb:aaaa/bbbb/cccc\x1b\\",
            )

    def test_osc112_restores_cursor_color(self):
        with Shitty(columns=10, rows=5) as terminal:
            original = dynamic_query(terminal, 12)
            set_dynamic(terminal, 12, "#010203")
            terminal.write(b"\x1b]112\x1b\\")
            self.assertEqual(dynamic_query(terminal, 12), original)

    def assert_erase_preserves_pending_wrap(self, sequence, first_line):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"#" * 10 + sequence)
            self.assertEqual(terminal.snapshot().lines[0], first_line)

            terminal.write(b"X")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 1).char, "X")
            self.assertEqual(snapshot.cursor_x, 1)
            self.assertEqual(snapshot.cursor_y, 1)

    @unittest.expectedFailure
    def test_el0_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[0K", "#" * 10)

    @unittest.expectedFailure
    def test_el1_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[1K", " " * 10)

    @unittest.expectedFailure
    def test_el2_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[2K", " " * 10)

    @unittest.expectedFailure
    def test_ed0_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[0J", "#" * 10)

    @unittest.expectedFailure
    def test_ed1_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[1J", " " * 10)

    @unittest.expectedFailure
    def test_ed2_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[2J", " " * 10)

    def test_ed3_preserves_pending_wrap(self):
        self.assert_erase_preserves_pending_wrap(b"\x1b[3J", "#" * 10)

    def test_following_sequence_never_advances_beyond_the_page(self):
        sequences = (
            b"\x1b[10@", b"\x1b[10 @", b"\x1b[10A", b"\x1b[10 A",
            b"\x1b[10B", b"\x1b[10C", b"\x1b[10D", b"\x1b[10E",
            b"\x1b[10F", b"\x1b[10G", b"\x1b[10;10H", b"\x1b[10I",
            b"\x1b[10L", b"\x1b[10M", b"\x1b[10P", b"\x1b[10S",
            b"\x1b[10T", b"\x1b[10X", b"\x1b[10Z", b"\x1b[10`",
            b"\x1b[10a", b"\x1b[10b", b"\x1b[10d", b"\x1b[10e",
            b"\x1b[10;10f", b"\x1b[0g", b"\x1b[s", b"\x1b[10'}",
            b"\x1b[10'~",
        )
        for sequence in sequences:
            with self.subTest(sequence=sequence):
                with Shitty(columns=10, rows=5) as terminal:
                    terminal.write(b"#" * 10 + b"\x1b[2J" + sequence + b"X")
                    snapshot = terminal.snapshot()
                    self.assertLess(snapshot.cursor_x, snapshot.columns)
                    self.assertLess(snapshot.cursor_y, snapshot.rows)
                    self.assertEqual(
                        sum(cell.char == "X" for cell in snapshot.cells), 1
                    )

    def test_ed3_unlocks_viewport_after_erasing_history(self):
        with Shitty(columns=10, rows=5, save_lines=100) as terminal:
            for index in range(20):
                terminal.write(f"old {index}\r\n".encode())
            terminal.wheel_up(5)
            self.assertGreater(terminal.snapshot().view_offset, 0)

            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.scrollback_state(), (0, 5, 5, 0))
            self.assertEqual(terminal.snapshot().view_offset, 0)

            for index in range(20):
                terminal.write(f"new {index}\r\n".encode())
            state = terminal.scrollback_state()
            self.assertEqual(state[3], state[0])
            self.assertEqual(terminal.snapshot().view_offset, 0)

    def test_alt_ed3_preserves_resized_primary_viewport(self):
        with Shitty(columns=10, rows=50, save_lines=100) as terminal:
            terminal.resize(10, 5)
            for index in range(20):
                terminal.write(f"old {index}\r\n".encode())
            terminal.wheel_up(5)
            before = terminal.snapshot()
            before_state = terminal.scrollback_state()

            terminal.write(b"\x1b[?1049h")
            for index in range(20):
                terminal.write(f"new {index}\r\n".encode())
            terminal.write(b"\x1b[3J\x1b[?1049l")

            self.assertEqual(terminal.snapshot().lines, before.lines)
            self.assertEqual(terminal.scrollback_state(), before_state)

            terminal.write(b"more\r\n")
            self.assertEqual(terminal.snapshot().lines, before.lines)
            self.assertEqual(terminal.scrollback_state()[3], before_state[3])

    def test_decsca_defaults_to_unprotected(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(b"some text\x1b[?2K")
            self.assertEqual(terminal.snapshot().lines, [" " * 12] * 2)
            terminal.write(b"some text\x1b[?2J")
            self.assertEqual(terminal.snapshot().lines, [" " * 12] * 2)

    def test_decsca_one_protects_cells_from_decsel(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"###\x1b[1\"qlineerase\x1b[0\"q***\x1b[?2K")
            self.assertEqual(terminal.snapshot().lines[0], "   lineerase    ")
            terminal.write(b"\x1b[2K")
            self.assertEqual(terminal.snapshot().lines[0], " " * 16)

    def test_decsca_one_protects_cells_from_decsed(self):
        with Shitty(columns=18, rows=2) as terminal:
            terminal.write(
                b"###\x1b[1\"qdisplayerase\x1b[0\"q***\x1b[?2J"
            )
            self.assertEqual(
                terminal.snapshot().lines[0], "   displayerase   "
            )
            terminal.write(b"\x1b[2J")
            self.assertEqual(terminal.snapshot().lines, [" " * 18] * 2)

    def test_decrqss_reports_decsca_state(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1bP$q\"q\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r0\"q\x1b\\")

            terminal.write(b"\x1b[1\"q\x1bP$q\"q\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r1\"q\x1b\\")

            terminal.write(b"\x1b[2\"q\x1bP$q\"q\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r0\"q\x1b\\")


if __name__ == "__main__":
    unittest.main()

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class ShellIntegrationTest(unittest.TestCase):
    def test_ordered_markers_partition_prompt_command_output_and_idle(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\prompt"
                b"\x1b]133;B\x1b\\command"
                b"\x1b]133;C\x1b\\output"
                b"\x1b]133;D;0\x1b\\idle"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.cell(0, 0).semantic, 1)
            self.assertEqual(snapshot.cell(6, 0).semantic, 2)
            self.assertEqual(snapshot.cell(13, 0).semantic, 3)
            self.assertEqual(snapshot.cell(3, 1).semantic, 0)

    def test_marker_parameters_are_accepted_but_never_rendered(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A;cl=m\x1b\\A"
                b"\x1b]133;B;future=value\x1b\\B"
                b"\x1b]133;C;future=value\x1b\\C"
                b"\x1b]133;D;127\x1b\\D"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(snapshot.lines[0][:4], "ABCD")
            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(4)],
                [1, 2, 3, 0],
            )

    def test_each_marker_resynchronizes_from_idle(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;B\x1b\\B"
                b"\x1b]133;C\x1b\\C"
                b"\x1b]133;D;1\x1b\\D"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(3)],
                [2, 3, 0],
            )

    def test_each_marker_resynchronizes_from_any_region(self):
        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\A"
                b"\x1b]133;C\x1b\\a"
                b"\x1b]133;B\x1b\\B"
                b"\x1b]133;D\x1b\\b"
                b"\x1b]133;C\x1b\\C"
                b"\x1b]133;B\x1b\\c"
                b"\x1b]133;D\x1b\\D"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(7)],
                [1, 3, 2, 0, 3, 2, 0],
            )

    def test_repeated_markers_are_idempotent(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\\x1b]133;A\x1b\\A"
                b"\x1b]133;B\x1b\\\x1b]133;B\x1b\\B"
                b"\x1b]133;C\x1b\\\x1b]133;C\x1b\\C"
                b"\x1b]133;D\x1b\\\x1b]133;D\x1b\\D"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(4)],
                [1, 2, 3, 0],
            )

    def test_prompt_marker_resynchronizes_from_any_region(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\"
                b"\x1b]133;B\x1b\\B"
                b"\x1b]133;A\x1b\\A"
                b"\x1b]133;B\x1b\\\x1b]133;C\x1b\\C"
                b"\x1b]133;A\x1b\\a"
            )
            snapshot = terminal.snapshot()

            # OSC 133;A marks the cursor position without moving it.  OSC
            # 133;L is the explicit fresh-line operation.
            self.assertEqual(snapshot.lines, ["BACa    ", "        "])
            self.assertEqual(
                [
                    snapshot.cell(0, 0).semantic,
                    snapshot.cell(1, 0).semantic,
                    snapshot.cell(2, 0).semantic,
                    snapshot.cell(3, 0).semantic,
                ],
                [2, 1, 3, 1],
            )

    def test_d_marker_accepts_omitted_numeric_and_unknown_exit_status(self):
        for suffix in (b"", b";0", b";255", b";not-a-number"):
            with self.subTest(suffix=suffix):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(
                        b"\x1b]133;A\x1b\\"
                        b"\x1b]133;B\x1b\\"
                        b"\x1b]133;C\x1b\\O"
                        b"\x1b]133;D" + suffix + b"\x1b\\I"
                    )
                    snapshot = terminal.snapshot()

                    self.assertEqual(snapshot.cell(0, 0).semantic, 3)
                    self.assertEqual(snapshot.cell(1, 0).semantic, 0)

    def test_unknown_and_empty_markers_do_not_change_region(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]133;A\x1b\\A"
                b"\x1b]133;E;command\x1b\\E"
                b"\x1b]133;\x1b\\X"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                [snapshot.cell(column, 0).semantic for column in range(3)],
                [1, 1, 1],
            )


if __name__ == "__main__":
    unittest.main()

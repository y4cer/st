# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class FontMissStormTest(unittest.TestCase):
    # PR 62: a flood of text no loaded face covers. Every fresh cluster
    # unwinds the frame with FontFaceMiss and re-runs it after adoption
    # settles the verdict; on the Vulkan path the unwind used to escape
    # after frame acquisition and crash the driver. The renderer-shared
    # half of that machinery must survive the storm, settle each cluster
    # once, and leave the terminal fully responsive.
    def test_uncovered_script_flood_stays_responsive(self):
        line = "हिन्दी বাংলা ৪২ ద్రావిడ " * 4
        with Shitty(columns=100, rows=24, save_lines=200) as terminal:
            for _ in range(100):
                terminal.write((line + "\r\n").encode())
            terminal.write(b"\x1b[2J\x1b[HDONE marker")
            snapshot = terminal.snapshot()
        self.assertEqual(snapshot.lines[0].rstrip()[:11], "DONE marker")

    def test_repeated_flood_reuses_the_settled_verdicts(self):
        # The second wave must hit the verdict caches: same digest, no
        # divergence between runs of identical content.
        line = ("হাজার বছর ধরে " * 6 + "\r\n").encode()
        with Shitty(columns=90, rows=12) as terminal:
            for _ in range(12):
                terminal.write(line)
            first = terminal.model_digest()
            terminal.write(b"\x1b[2J\x1b[H")
            for _ in range(12):
                terminal.write(line)
            second = terminal.model_digest()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

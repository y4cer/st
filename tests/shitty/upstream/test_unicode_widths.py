"""-unicodeWidths: which Unicode version's cell widths the grid emulates."""

import re
import unittest

from harness import Shitty

WATCH = "⌚".encode()      # wide since the Unicode 9 emoji batch
TRIGRAM = "☲".encode()    # wide since the Unicode 15.1 trigram batch
IDEOGRAPH = "一".encode()  # wide since forever


def width(terminal, encoded):
    column, _ = terminal.measure_widths(encoded)[0]
    return column


def features(terminal):
    terminal.read_input()
    terminal.write(b"\x1b]1337;Capabilities\x1b\\")
    return terminal.read_input()


class UnicodeWidthsTest(unittest.TestCase):
    def test_level_8_predates_both_batches(self):
        with Shitty(extra_arguments=("-unicodeWidths", "8")) as terminal:
            self.assertEqual(width(terminal, WATCH), 1)
            self.assertEqual(width(terminal, TRIGRAM), 1)
            self.assertEqual(width(terminal, IDEOGRAPH), 2)
            self.assertIn(b"Uw8", features(terminal))

    def test_level_15_has_emoji_but_not_trigrams(self):
        with Shitty(extra_arguments=("-unicodeWidths", "15")) as terminal:
            self.assertEqual(width(terminal, WATCH), 2)
            self.assertEqual(width(terminal, TRIGRAM), 1)
            self.assertEqual(width(terminal, IDEOGRAPH), 2)
            self.assertIn(b"Uw15", features(terminal))

    def test_level_17_is_the_full_tables(self):
        with Shitty(extra_arguments=("-unicodeWidths", "17")) as terminal:
            self.assertEqual(width(terminal, WATCH), 2)
            self.assertEqual(width(terminal, TRIGRAM), 2)
            self.assertEqual(width(terminal, IDEOGRAPH), 2)
            self.assertIn(b"Uw17", features(terminal))

    def test_the_default_level_matches_its_own_advertisement(self):
        # The auto default probes the host libc, so the level itself is
        # environment-specific; what must always hold is that the widths
        # agree with the Uw the terminal advertises.
        with Shitty() as terminal:
            match = re.search(rb"Uw([0-9]+)", features(terminal))
            self.assertIsNotNone(match)
            level = int(match.group(1))
            self.assertEqual(width(terminal, WATCH), 2 if level >= 9 else 1)
            self.assertEqual(width(terminal, TRIGRAM), 2 if level >= 16 else 1)
            self.assertEqual(width(terminal, IDEOGRAPH), 2)


if __name__ == "__main__":
    unittest.main()

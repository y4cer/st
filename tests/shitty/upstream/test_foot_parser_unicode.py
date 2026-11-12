# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of Foot parser collection and emoji-VS metadata units."""

from pathlib import Path
import unittest

from harness import Shitty, put_rows


UPSTREAM_PARSER_CASES = (
    "action_collect stores the first byte",
    "action_collect stores the second byte",
    "action_collect stores the third byte",
    "action_collect stores the fourth byte",
    "action_collect does not overflow its four-byte storage",
)

UNICODE_DATA = (
    Path(__file__).parent.parent
    / "ext"
    / "unicode"
    / "emoji-variation-sequences-17.0.0.txt"
)

# These registered bases already have a two-cell text presentation.  VS15
# selects that presentation but must not squeeze its glyph into one cell.
WIDTH_NEUTRAL_BASES = frozenset(
    {
        0x3030,
        0x303D,
        0x3297,
        0x3299,
        0x1F202,
        0x1F21A,
        0x1F22F,
        0x1F237,
    }
)


def read_variation_sequences():
    result = []
    for line in UNICODE_DATA.read_text(encoding="utf-8").splitlines():
        data = line.split("#", 1)[0].strip()
        if not data:
            continue
        codepoints, _ = data.split(";", 1)
        result.append(tuple(int(value, 16) for value in codepoints.split()))
    return tuple(result)


VARIATION_SEQUENCES = read_variation_sequences()
VARIATION_BASES = tuple(sorted({base for base, _ in VARIATION_SEQUENCES}))


class FootParserUnicodeTest(unittest.TestCase):
    def test_upstream_parser_inventory_has_all_five_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_PARSER_CASES), 5)
        self.assertEqual(len(set(UPSTREAM_PARSER_CASES)), 5)

    def assert_csi_intermediates_collected(self, count):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            intermediates = bytes(range(0x20, 0x20 + count))
            terminal.write(b"\x1b[" + intermediates + b"pX")
            self.assertEqual(
                terminal.parser_trace(),
                [("csi", intermediates + b"p"), ("text", b"X")],
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")

    def test_first_csi_intermediate_is_collected(self):
        self.assert_csi_intermediates_collected(1)

    def test_second_csi_intermediate_is_collected(self):
        self.assert_csi_intermediates_collected(2)

    def test_third_csi_intermediate_is_collected(self):
        self.assert_csi_intermediates_collected(3)

    def test_fourth_csi_intermediate_is_collected(self):
        self.assert_csi_intermediates_collected(4)

    def test_fifth_csi_intermediate_rejects_sequence_and_parser_recovers(self):
        intermediates = bytes(range(0x20, 0x25))
        with Shitty(columns=8, rows=2) as terminal:
            terminal.parser_trace_on()
            terminal.write(b"\x1b[" + intermediates + b"pX\x1b[?2026$p")
            self.assertEqual(
                terminal.parser_trace(),
                [("text", b"X"), ("csi", b"?2026$p")],
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "X")
            self.assertEqual(terminal.read_input(), b"\x1b[?2026;2$y")


class FootVariationSelectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terminal = Shitty(columns=4, rows=2)

    @classmethod
    def tearDownClass(cls):
        cls.terminal.close()

    def test_unicode_17_variation_metadata_is_complete_and_ordered(self):
        self.assertEqual(len(VARIATION_SEQUENCES), 742)
        self.assertEqual(len(set(VARIATION_SEQUENCES)), 742)
        self.assertEqual(VARIATION_SEQUENCES, tuple(sorted(VARIATION_SEQUENCES)))
        self.assertEqual(len(VARIATION_BASES), 371)
        for base in VARIATION_BASES:
            with self.subTest(base=f"U+{base:04X}"):
                self.assertIn((base, 0xFE0E), VARIATION_SEQUENCES)
                self.assertIn((base, 0xFE0F), VARIATION_SEQUENCES)

    def assert_variation_base_widths(self, base):
        text = chr(base)
        self.terminal.write(
            b"\x1bc"
            + put_rows(
                (text + "\uFE0E").encode(),
                (text + "\uFE0F").encode(),
            )
        )
        snapshot = self.terminal.model_snapshot()
        vs15_width = 2 if base in WIDTH_NEUTRAL_BASES else 1
        for row, selector, width in (
            (0, 0xFE0E, vs15_width),
            (1, 0xFE0F, 2),
        ):
            cell = snapshot.cell(0, row)
            self.assertEqual(cell.grapheme, (base, selector))
            self.assertEqual(cell.double_width, width == 2)
            self.assertEqual(
                snapshot.cell(1, row).double_width_continuation,
                width == 2,
            )


def make_variation_base_test(base):
    def test(self):
        self.assert_variation_base_widths(base)

    test.__name__ = f"test_variation_base_{base:06x}"
    test.__doc__ = f"Foot emoji variation metadata entry U+{base:04X}."
    return test


for variation_base in VARIATION_BASES:
    setattr(
        FootVariationSelectorTest,
        f"test_variation_base_{variation_base:06x}",
        make_variation_base_test(variation_base),
    )


if __name__ == "__main__":
    unittest.main()

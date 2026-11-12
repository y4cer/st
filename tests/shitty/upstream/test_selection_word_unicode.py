# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


def double_click(terminal, column, row=0, time=1.0):
    x = column + 2
    y = row + 2
    terminal.button(0, True, x=x, y=y, time=time)
    terminal.button(0, False, x=x, y=y, time=time + 0.01)
    terminal.button(0, True, x=x, y=y, time=time + 0.1)
    return terminal.button(0, False, x=x, y=y, time=time + 0.11)


class SelectionWordUnicodeTest(unittest.TestCase):
    def test_ascii_punctuation_separates_words(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"foo.bar")
            self.assertEqual(double_click(terminal, 3), b".")

    def test_different_punctuation_is_separate_but_repeats_group(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"a.,!!b")
            self.assertEqual(double_click(terminal, 1), b".")
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"a.,!!b")
            self.assertEqual(double_click(terminal, 3), b"!!")

    def test_connector_punctuation_remains_part_of_identifier(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"one baz_qux two")
            self.assertEqual(double_click(terminal, 7), b"baz_qux")

    def test_compound_identifiers_expand_from_identifier_characters(self):
        cases = [
            (b"namespace::symbol", 12),
            (b"object.member", 8),
            (b"some-name", 6),
            (b"user@example.com", 6),
        ]
        for text, column in cases:
            with self.subTest(text=text):
                with Shitty(columns=32, rows=2) as terminal:
                    terminal.write(text)
                    self.assertEqual(double_click(terminal, column), text)

    def test_compound_punctuation_keeps_direct_click_behavior(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"namespace::symbol")
            self.assertEqual(double_click(terminal, 9), b"::")
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"some-name")
            self.assertEqual(double_click(terminal, 4), b"-")

    def test_compound_tokens_exclude_prose_prefixes(self):
        cases = [
            (b"...object.member", 3, b"object.member"),
            (b"...object.member", 10, b"object.member"),
            (b"---foo", 3, b"foo"),
        ]
        for text, column, expected in cases:
            with self.subTest(text=text, column=column):
                with Shitty(columns=32, rows=2) as terminal:
                    terminal.write(text)
                    self.assertEqual(double_click(terminal, column), expected)

    def test_compound_tokens_preserve_valid_prefixes(self):
        cases = [
            (b"./source.cpp", 2),
            (b"../source.cpp", 3),
            (b".git/config", 1),
            (b"--verbose", 3),
        ]
        for text, column in cases:
            with self.subTest(text=text):
                with Shitty(columns=32, rows=2) as terminal:
                    terminal.write(text)
                    self.assertEqual(double_click(terminal, column), text)

    def test_path_location_expands_from_an_identifier_character(self):
        with Shitty(columns=40, rows=2) as terminal:
            token = b"/home/user/source.cpp:42"
            terminal.write(b"(" + token + b") next")
            self.assertEqual(double_click(terminal, 8), token)

    def test_uri_excludes_surrounding_punctuation(self):
        with Shitty(columns=64, rows=2) as terminal:
            uri = b"https://example.com/path?key=value#section"
            terminal.write(b"(" + uri + b").")
            self.assertEqual(double_click(terminal, 10), uri)

    def test_uri_expands_when_clicking_uri_punctuation(self):
        with Shitty(columns=40, rows=2) as terminal:
            uri = b"https://example.com/path"
            terminal.write(uri)
            self.assertEqual(double_click(terminal, 6), uri)

    def test_uri_excludes_complete_trailing_prose_suffix(self):
        uri = b"https://example.com/a:b"
        for opening, suffix in [(b"(", b"):"), (b"[", b"]:"), (b"", b":")]:
            with self.subTest(suffix=suffix):
                with Shitty(columns=48, rows=2) as terminal:
                    terminal.write(opening + uri + suffix + b" next")
                    self.assertEqual(double_click(terminal, len(opening) + 10), uri)

    def test_semantic_selection_crosses_soft_wrapped_rows(self):
        cases = [
            (6, b"https://example.com", [(1, 0), (1, 1), (4, 2)]),
            (7, b"object.member", [(2, 0), (1, 1)]),
            (7, "object.東京".encode(), [(2, 0), (1, 1), (2, 1)]),
        ]
        for columns, text, clicks in cases:
            for column, row in clicks:
                with self.subTest(text=text, column=column, row=row):
                    with Shitty(columns=columns, rows=4) as terminal:
                        terminal.write(text)
                        self.assertEqual(
                            double_click(terminal, column, row),
                            text,
                        )

    def test_scheme_less_url_expands_from_each_component(self):
        uri = b"example.com/path?key=value#fragment"
        for column in [2, 13, 18, 28]:
            with self.subTest(column=column):
                with Shitty(columns=48, rows=2) as terminal:
                    terminal.write(uri)
                    self.assertEqual(double_click(terminal, column), uri)

    def test_question_and_equals_do_not_join_ordinary_prose(self):
        cases = [
            (b"what?maybe", 6, b"maybe"),
            (b"alpha=beta", 7, b"beta"),
        ]
        for text, column, expected in cases:
            with self.subTest(text=text):
                with Shitty(columns=24, rows=2) as terminal:
                    terminal.write(text)
                    self.assertEqual(double_click(terminal, column), expected)

    def test_unicode_letters_and_marks_form_words(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write("café Ελληνικά".encode())
            self.assertEqual(double_click(terminal, 3), "café".encode())
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write("café Ελληνικά".encode())
            self.assertEqual(double_click(terminal, 7), "Ελληνικά".encode())

    def test_clicking_wide_continuation_selects_the_unicode_word(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write("go 東京 now".encode())
            self.assertEqual(double_click(terminal, 4), "東京".encode())

    def test_whitespace_run_is_selectable_as_one_class(self):
        with Shitty(columns=16, rows=2) as terminal:
            terminal.write(b"foo   bar")
            self.assertEqual(double_click(terminal, 4), b"   ")


    def test_double_click_past_an_early_wrap_snaps_to_the_padding(self):
        # A wide character that did not fit wraps the row early; a
        # double click on the padding past that wrap selects only it.
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write("ab日本語".encode())
            self.assertEqual(double_click(terminal, 4, 0), b"")
            self.assertEqual(terminal.selection_state()["snapped"], (4, 0, 5, 0))
            self.assertEqual(
                double_click(terminal, 3, 0, time=3.0),
                "ab日本語".encode(),
            )
            self.assertEqual(terminal.selection_state()["snapped"], (0, 0, 4, 1))


if __name__ == "__main__":
    unittest.main()

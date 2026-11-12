# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public consequences of the final 23 Ghostty Binding.zig tests."""

import unittest

from harness import Shitty, TEST_PLATFORM


CONTROL = 0x0002
SHIFT = 0x0001
SUPER = 0x0008


UPSTREAM_CASES = (
    "Action: clone",
    "parse: increase_font_size",
    "parse: decrease_font_size",
    "parse: reset_font_size",
    "parse: set_font_size",
    "parse: copy to clipboard default",
    "parse: copy to clipboard explicit",
    "parse: write screen file no format",
    "parse: write screen file format",
    "parse: write screen file format as string",
    "parse: write screen file invalid",
    "action: format",
    "action: format set title",
    "set: appendChain with no parent returns error",
    "set: appendChain after put converts to leaf_chained",
    "set: appendChain after putFlags preserves flags",
    "set: appendChain multiple times",
    "set: appendChain removes reverse mapping",
    "set: appendChain with performable does not affect reverse mapping",
    "set: appendChain restores next valid reverse mapping",
    "set: formatEntries leaf_chained",
    "set: formatEntries leaf_chained multiple chains",
    "set: formatEntries leaf_chained with text action",
)


def remaps(*rules):
    return tuple(part for rule in rules for part in ("-remap", rule))


def control_key(terminal, character):
    terminal.layout_key(character.upper(), character, character, modifiers=CONTROL)


def shortcut(terminal, key, text, modifiers):
    terminal.frontend_key_event(key, 1, modifiers=modifiers)
    if text is not None:
        terminal.frontend_text_event(text, modifiers=modifiers)
    terminal.frontend_key_event(key, 0, modifiers=modifiers)


def font_shortcuts():
    if TEST_PLATFORM == "cocoa":
        return (
            (ord("="), None, SUPER),
            (ord("-"), None, SUPER),
            (ord("0"), None, SUPER),
        )
    return (
        (ord("="), "+", CONTROL | SHIFT),
        (ord("-"), "-", CONTROL),
        (ord("0"), "0", CONTROL),
    )


class GhosttyBindingActionsTailTest(unittest.TestCase):
    def test_upstream_inventory_has_23_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 23)
        self.assertEqual(len(set(UPSTREAM_CASES)), 23)

    @unittest.expectedFailure
    def test_cloned_ignore_and_allocated_text_actions_keep_behavior(self):
        arguments = remaps("ctrl+a=none", "ctrl+b=text:foo")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"foo")

    @unittest.expectedFailure
    def test_increase_font_size_accepts_fractional_amount(self):
        arguments = remaps("ctrl+a=increase_font_size:1.5")
        with Shitty(extra_arguments=("-fontsize", "16", *arguments)) as terminal:
            control_key(terminal, "a")

            self.assertEqual((terminal.font_state()[0], terminal.read_input()), (17.5, b""))

    @unittest.expectedFailure
    def test_decrease_font_size_accepts_fractional_amount(self):
        arguments = remaps("ctrl+a=decrease_font_size:2.5")
        with Shitty(extra_arguments=("-fontsize", "16", *arguments)) as terminal:
            control_key(terminal, "a")

            self.assertEqual((terminal.font_state()[0], terminal.read_input()), (13.5, b""))

    def test_reset_font_size_action_restores_configured_size(self):
        increase, _, reset = font_shortcuts()
        with Shitty(extra_arguments=("-fontsize", "16")) as terminal:
            shortcut(terminal, *increase)
            self.assertEqual(terminal.font_state()[0], 17)
            shortcut(terminal, *reset)

            self.assertEqual((terminal.font_state()[0], terminal.read_input()), (16, b""))

    @unittest.expectedFailure
    def test_set_font_size_accepts_fractional_absolute_size(self):
        arguments = remaps("ctrl+a=set_font_size:13.5")
        with Shitty(extra_arguments=("-fontsize", "16", *arguments)) as terminal:
            control_key(terminal, "a")

            self.assertEqual((terminal.font_state()[0], terminal.read_input()), (13.5, b""))

    def test_default_copy_action_copies_current_selection(self):
        # Upstream sources copy_to_clipboard from the live screen
        # selection and does nothing without one - a staged pasteboard
        # is not a selection.
        copy_modifiers = SUPER if TEST_PLATFORM == "cocoa" else CONTROL | SHIFT
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"abcd")
            terminal.set_system_clipboard(b"external")
            terminal.button(0, True, x=2, y=2, time=1)
            terminal.button(0, False, x=2, y=2, time=1.01)
            terminal.button(1, True, x=5, y=2, time=2)
            terminal.button(1, False, x=5, y=2, time=2.01)
            terminal.frontend_key_event(ord("C"), 1, modifiers=copy_modifiers)
            terminal.frontend_key_event(ord("C"), 0, modifiers=copy_modifiers)

            self.assertEqual(terminal.get_selection(primary=False), b"abc")

    @unittest.expectedFailure
    def test_explicit_html_copy_action_is_accepted_and_consumed(self):
        arguments = remaps("ctrl+a=copy_to_clipboard:html")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.set_primary_selection(b"selected")
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_write_screen_file_action_accepts_default_format(self):
        arguments = remaps("ctrl+a=write_screen_file:copy")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_write_screen_file_action_accepts_html_format(self):
        arguments = remaps("ctrl+b=write_screen_file:copy,html")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_write_screen_file_action_round_trips_its_format(self):
        arguments = remaps("ctrl+c=write_screen_file:copy,html")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"")

    def test_invalid_write_screen_file_forms_do_not_damage_valid_rule(self):
        arguments = remaps(
            "ctrl+a=write_screen_file:",
            "ctrl+b=write_screen_file:,,",
            "ctrl+c=write_screen_file:copy,",
            "ctrl+d=write_screen_file:copy,html,extra",
            "ctrl+e=ctrl+f",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "e")

            self.assertEqual(terminal.read_input(), b"\x06")

    @unittest.expectedFailure
    def test_text_action_format_round_trip_preserves_unicode_and_quotes(self):
        arguments = remaps("ctrl+a=text:👻Ghostty'\"")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), "👻Ghostty'\"".encode())

    @unittest.expectedFailure
    def test_set_title_action_format_preserves_spaces(self):
        arguments = remaps("ctrl+a=set_tab_title:foo bar")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.window_title(), "foo bar")

    def test_append_chain_without_parent_is_rejected_in_isolation(self):
        arguments = remaps("chain=ctrl+c", "ctrl+a=ctrl+b")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02")

    @unittest.expectedFailure
    def test_append_chain_converts_one_action_to_two(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    @unittest.expectedFailure
    def test_append_chain_preserves_unconsumed_flag(self):
        arguments = remaps("unconsumed:ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x01")

    @unittest.expectedFailure
    def test_append_chain_multiple_times_keeps_action_order(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "chain=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x04")

    @unittest.expectedFailure
    def test_append_chain_changes_single_action_to_chained_behavior(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    def test_performable_chain_attempt_does_not_damage_normal_mapping(self):
        arguments = remaps(
            "ctrl+b=ctrl+c",
            "performable:ctrl+a=ctrl+d",
            "chain=ctrl+e",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03")

    @unittest.expectedFailure
    def test_chaining_latest_duplicate_restores_earlier_direct_action(self):
        arguments = remaps(
            "ctrl+a=ctrl+c",
            "ctrl+b=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03\x03\x04")

    @unittest.expectedFailure
    def test_formatted_leaf_chain_replays_both_actions(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    @unittest.expectedFailure
    def test_formatted_multi_chain_replays_all_actions(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "chain=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x04")

    @unittest.expectedFailure
    def test_formatted_text_chain_replays_owned_strings(self):
        arguments = remaps("ctrl+a=text:hello", "chain=text:world")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"helloworld")


if __name__ == "__main__":
    unittest.main()

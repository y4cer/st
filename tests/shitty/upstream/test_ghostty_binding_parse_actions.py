# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public consequences of the first 20 Ghostty Binding.zig tests.

Ghostty's parser and tagged action union are private implementation APIs.
These scenarios drive Shitty's public ``-remap`` option and observe the PTY,
window title, or tab/session routing instead of adding a parser test hook.
"""

import unittest

from harness import Shitty


SHIFT = 0x0001
CONTROL = 0x0002
ALT = 0x0004
SUPER = 0x0008

F5 = 294
F6 = 295
F7 = 296
F8 = 297
F9 = 298


UPSTREAM_CASES = (
    "parse: triggers",
    "parse: w3c key names",
    "parse: catch_all",
    "parse: plus sign",
    "parse: equals sign",
    "parse: text action equals sign",
    "parse: backwards compatibility with <= 1.1.x",
    "parse: global triggers",
    "parse: all triggers",
    "Trigger: equal",
    "parse: modifier aliases",
    "parse: action invalid",
    "parse: action no parameters",
    "parse: action with string",
    "parse: action with enum",
    "parse: action with enum with default",
    "parse: action with int",
    "parse: action with float",
    "parse: action with a tuple",
    "parse: chain",
)


def remaps(*rules):
    return tuple(part for rule in rules for part in ("-remap", rule))


class GhosttyBindingParseActionsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    @unittest.expectedFailure
    def test_parse_triggers_including_unicode_and_flags(self):
        arguments = remaps(
            "a=none",
            "shift+b=none",
            "ctrl+shift+c=none",
            "shift+d=none",
            "shift+ö=none",
            "unconsumed:shift+e=none",
            "performable:shift+f=none",
            "shift+shift+g=none",
            "g+h=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            # Report-all makes an unmatched printable key observable without
            # synthesizing a separate frontend text callback.
            terminal.write(b"\x1b[>9u")
            terminal.layout_key("A", "a", "a")
            terminal.layout_key("B", "B", "b", modifiers=SHIFT)
            terminal.layout_key("C", "C", "c", modifiers=SHIFT | CONTROL)
            terminal.layout_key("D", "д", "d", modifiers=SHIFT)
            terminal.layout_key(0, "Ö", 0, modifiers=SHIFT)
            terminal.layout_key("E", "E", "e", modifiers=SHIFT)
            terminal.layout_key("F", "F", "f", modifiers=SHIFT)

            self.assertEqual(terminal.read_input(), b"")

    def test_parse_w3c_key_name_is_exact_and_case_sensitive(self):
        # W3C's KeyA spelling is Ghostty's config API.  Shitty's public
        # equivalent is its generated symbolic-name table, also exact.
        with Shitty(extra_arguments=remaps("f5=none", "F6=none")) as terminal:
            terminal.frontend_key_event(F5, 1)
            terminal.frontend_key_event(F6, 1)

            self.assertEqual(terminal.read_input(), b"\x1b[17~")

    @unittest.expectedFailure
    def test_parse_catch_all_with_and_without_modifiers(self):
        arguments = remaps("catch_all=none", "ctrl+catch_all=none")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.frontend_key_event(F6, 1)
            terminal.frontend_key_event(F7, 1, modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_plus_sign_as_a_trigger(self):
        with Shitty(extra_arguments=remaps("+=none", "ctrl++=none")) as terminal:
            terminal.write(b"\x1b[>9u")
            terminal.layout_key("+", "+", "+")
            terminal.layout_key("+", "+", "+", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_equals_sign_as_a_trigger(self):
        with Shitty(extra_arguments=remaps("==none", "ctrl+==none")) as terminal:
            terminal.write(b"\x1b[>9u")
            terminal.layout_key("=", "=", "=")
            terminal.layout_key("=", "=", "=", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_equals_trigger_preserves_equals_in_text_action(self):
        arguments = remaps("==text:=", "ctrl+==text:=hello")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.write(b"\x1b[>9u")
            terminal.layout_key("=", "=", "=")
            terminal.layout_key("=", "=", "=", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"==hello")

    def test_parse_pre_1_2_key_name_compatibility(self):
        # Shitty has not renamed its public key vocabulary.  Exercise the
        # corresponding stable canonical and physical/base-layout forms.
        arguments = remaps("ctrl+3=none", "ctrl+up=none")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("3", "№", "3", modifiers=CONTROL)
            terminal.frontend_key_event(265, 1, modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_global_trigger_and_reject_global_sequence(self):
        arguments = remaps(
            "global:ctrl+a=none",
            "unconsumed:global:ctrl+b=none",
            "global:ctrl+c>ctrl+d=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_all_trigger_and_reject_all_sequence(self):
        arguments = remaps(
            "all:ctrl+a=none",
            "unconsumed:all:ctrl+b=none",
            "all:ctrl+c>ctrl+d=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    def test_trigger_equality_uses_key_kind_and_exact_modifiers(self):
        arguments = remaps("ctrl+up=f5", "alt+up=f6")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.frontend_key_event(265, 1, modifiers=CONTROL)
            terminal.frontend_key_event(265, 1, modifiers=ALT)
            terminal.frontend_key_event(265, 1)

            self.assertEqual(
                terminal.read_input(),
                b"\x1b[15~\x1b[17~\x1b[A",
            )

    def test_parse_modifier_aliases(self):
        arguments = remaps(
            "cmd+f5=none",
            "command+f6=none",
            "opt+f7=none",
            "option+f8=none",
            "control+f9=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.frontend_key_event(F5, 1, modifiers=SUPER)
            terminal.frontend_key_event(F6, 1, modifiers=SUPER)
            terminal.frontend_key_event(F7, 1, modifiers=ALT)
            terminal.frontend_key_event(F8, 1, modifiers=ALT)
            terminal.frontend_key_event(F9, 1, modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    def test_parse_invalid_action_rejects_only_that_rule(self):
        arguments = remaps("ctrl+a=nopenopenope", "ctrl+b=ctrl+d")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"\x01\x04")

    def test_parse_no_parameter_action_and_reject_parameter(self):
        arguments = remaps("ctrl+a=none", "ctrl+b=none:A")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"\x02")

    @unittest.expectedFailure
    def test_parse_string_actions(self):
        arguments = remaps(
            "ctrl+a=csi:A",
            "ctrl+b=esc:A",
            "ctrl+c=set_surface_title:surface",
            "ctrl+d=set_tab_title:tab",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            terminal.layout_key("D", "d", "d", modifiers=CONTROL)

            self.assertEqual(
                (terminal.read_input(), terminal.window_title()),
                (b"\x1b[A\x1bA", "tab"),
            )

    @unittest.expectedFailure
    def test_parse_enum_action(self):
        with Shitty(extra_arguments=remaps("ctrl+a=new_split:right")) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_enum_action_with_default(self):
        with Shitty(extra_arguments=remaps("ctrl+a=new_split")) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_signed_integer_action(self):
        arguments = remaps(
            "ctrl+a=jump_to_prompt:-1",
            "ctrl+b=jump_to_prompt:10",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_float_action(self):
        arguments = remaps(
            "ctrl+a=scroll_page_fractional:-0.5",
            "ctrl+b=scroll_page_fractional:+0.5",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parse_tuple_action_and_reject_bad_tuples(self):
        arguments = remaps(
            "ctrl+a=resize_split:up,10",
            "ctrl+b=resize_split:up",
            "ctrl+c=resize_split:up,10,12",
            "ctrl+d=resize_split:up,four",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            terminal.layout_key("D", "d", "d", modifiers=CONTROL)

            # Only the well-formed tuple is consumed.
            self.assertEqual(terminal.read_input(), b"\x02\x03\x04")

    @unittest.expectedFailure
    def test_parse_chained_action_and_reject_flagged_or_sequenced_chain(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "chain=ctrl+c",
            "global:chain=none",
            "ctrl+d>chain=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("A", "a", "a", modifiers=CONTROL)

            self.assertEqual(terminal.read_input(), b"\x02\x03")


if __name__ == "__main__":
    unittest.main()

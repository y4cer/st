# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public consequences of Ghostty Binding.zig cases 41 through 60."""

import os
import signal
import tempfile
import time
import unittest
from pathlib import Path

from harness import Shitty


CONTROL = 0x0002
ALT = 0x0004

F5 = 294
F6 = 295


UPSTREAM_CASES = (
    "set: parseAndPut unbind sequence unbinds leader",
    "set: parseAndPut unbind sequence unbinds leader if not set",
    "set: parseAndPut sequence preserves reverse mapping",
    "set: put overwrites sequence",
    "set: maintains reverse mapping",
    "set: performable is not part of reverse mappings",
    "set: overriding a mapping updates reverse",
    "set: consumed state",
    "set: parseAndPut chain",
    "set: parseAndPut chain without parent is error",
    "set: parseAndPut chain multiple times",
    "set: parseAndPut chain preserves flags",
    "set: parseAndPut chain after unbind is error",
    "set: parseAndPut chain on sequence",
    "set: parseAndPut chain with unbind is error",
    "set: getEvent physical",
    "set: getEvent codepoint",
    "set: getEvent codepoint case folding",
    "set: getEvent catch_all fallback",
    "set: getEvent catch_all with modifiers",
)


def remaps(*rules):
    return tuple(part for rule in rules for part in ("-remap", rule))


def config_text(*rules):
    values = ", ".join(repr(rule) for rule in rules)
    return f"remap = [{values}]\n"


def control_key(terminal, character, layout=None, base=None):
    terminal.layout_key(
        character.upper(),
        character if layout is None else layout,
        character if base is None else base,
        modifiers=CONTROL,
    )


def wait_for_key_output(terminal, character, expected):
    deadline = time.monotonic() + 2
    while True:
        control_key(terminal, character)
        output = terminal.read_input()
        if output == expected:
            return
        if time.monotonic() >= deadline:
            raise AssertionError(f"expected {expected!r}, got {output!r}")
        time.sleep(0.01)


class GhosttyBindingSetEventsTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    def test_unbinding_only_sequence_leaf_removes_the_leader(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "ctrl+a>ctrl+b=unbind",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x01\x02")

    def test_unbinding_missing_sequence_leaves_no_leader(self):
        with Shitty(extra_arguments=remaps("ctrl+c>ctrl+d=unbind")) as terminal:
            control_key(terminal, "c")
            control_key(terminal, "d")

            self.assertEqual(terminal.read_input(), b"\x03\x04")

    def test_sequence_does_not_displace_direct_forward_mapping(self):
        arguments = remaps(
            "ctrl+a=ctrl+c",
            "ctrl+a>ctrl+b=ctrl+c",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x03")

    def test_direct_mapping_after_sequence_routes_immediately(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "ctrl+a=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x04")

    def test_latest_mapping_wins_and_reload_restores_earlier_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bindings.toml"
            path.write_text(config_text("ctrl+a=ctrl+b", "ctrl+a=ctrl+c"))
            with Shitty(extra_arguments=("-config", path)) as terminal:
                control_key(terminal, "a")
                self.assertEqual(terminal.read_input(), b"\x03")

                path.write_text(config_text("ctrl+a=ctrl+b"))
                os.kill(terminal.process.pid, signal.SIGUSR1)
                wait_for_key_output(terminal, "a", b"\x02")

    def test_performable_rule_does_not_replace_normal_mapping(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "performable:ctrl+c=ctrl+b",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    def test_overriding_mapping_routes_only_to_new_target(self):
        arguments = remaps("ctrl+a=ctrl+b", "ctrl+a=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x03")

    def test_final_consumed_mapping_replaces_unconsumed_intermediate(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "unconsumed:ctrl+a=ctrl+c",
            "ctrl+a=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x04")

    @unittest.expectedFailure
    def test_parse_and_put_chain_runs_both_actions(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    def test_chain_without_parent_is_rejected_in_isolation(self):
        arguments = remaps("chain=ctrl+c", "ctrl+a=ctrl+b")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02")

    @unittest.expectedFailure
    def test_multiple_chain_entries_run_in_order(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "chain=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x04")

    @unittest.expectedFailure
    def test_chained_actions_preserve_unconsumed_flag(self):
        arguments = remaps(
            "unconsumed:ctrl+a=ctrl+b",
            "chain=ctrl+c",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x01")

    @unittest.expectedFailure
    def test_chain_after_unbind_is_rejected(self):
        arguments = remaps(
            "ctrl+a=ctrl+b",
            "ctrl+a=unbind",
            "chain=ctrl+c",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x01")

    @unittest.expectedFailure
    def test_sequence_final_leaf_can_own_a_chain(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03\x04")

    def test_chain_unbind_is_rejected_without_damaging_parent(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=unbind")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02")

    def test_physical_key_mapping_does_not_match_printable_identity(self):
        with Shitty(extra_arguments=remaps("ctrl+up=f5")) as terminal:
            terminal.frontend_key_event(265, 1, modifiers=CONTROL)
            control_key(terminal, "a", layout="↑", base="a")

            self.assertEqual(terminal.read_input(), b"\x1b[15~\x01")

    def test_codepoint_mapping_uses_base_layout_identity(self):
        with Shitty(extra_arguments=remaps("ctrl+'=f5")) as terminal:
            control_key(terminal, "a", layout="'", base="'")

            self.assertEqual(terminal.read_input(), b"\x1b[15~")

    def test_codepoint_mapping_case_folds_source_and_event(self):
        with Shitty(extra_arguments=remaps("ctrl+A=f5")) as terminal:
            control_key(terminal, "j", layout="a", base="a")
            control_key(terminal, "a", layout="A", base="A")

            self.assertEqual(terminal.read_input(), b"\x1b[15~\x1b[15~")

    @unittest.expectedFailure
    def test_catch_all_is_fallback_after_specific_mapping(self):
        arguments = remaps("catch_all=none", "ctrl+b=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03")

    @unittest.expectedFailure
    def test_modified_catch_all_precedes_unmodified_fallback(self):
        arguments = remaps("ctrl+catch_all=none", "catch_all=none")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.frontend_key_event(F5, 1, modifiers=CONTROL)
            terminal.frontend_key_event(F6, 1)
            terminal.frontend_key_event(F5, 1, modifiers=ALT)

            self.assertEqual(terminal.read_input(), b"")


if __name__ == "__main__":
    unittest.main()

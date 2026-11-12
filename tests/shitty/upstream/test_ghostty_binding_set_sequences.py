# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public consequences of Ghostty Binding.zig cases 21 through 40."""

import os
import signal
import tempfile
import time
import unittest
from pathlib import Path

from harness import Shitty


CONTROL = 0x0002


UPSTREAM_CASES = (
    "sequence iterator",
    "parse: sequences",
    "set: parseAndPut typical binding",
    "set: parseAndPut unconsumed binding",
    "set: parseAndPut removed binding",
    "set: put sets chain_parent",
    "set: putFlags sets chain_parent",
    "set: sequence sets chain_parent to final leaf",
    "set: multiple leaves under leader updates chain_parent",
    "set: sequence unbind clears chain_parent",
    "set: sequence unbind with remaining leaves clears chain_parent",
    "set: direct remove clears chain_parent",
    "set: invalid format preserves chain_parent",
    "set: clone produces null chain_parent",
    "set: clone with leaf_chained",
    "set: clone with leaf_chained containing allocated data",
    "set: parseAndPut sequence",
    "set: parseAndPut sequence with two actions",
    "set: parseAndPut overwrite sequence",
    "set: parseAndPut overwrite leader",
)


def remaps(*rules):
    return tuple(part for rule in rules for part in ("-remap", rule))


def config_text(*rules):
    values = ", ".join(repr(rule) for rule in rules)
    return f"remap = [{values}]\n"


def control_key(terminal, character):
    terminal.layout_key(character.upper(), character, character, modifiers=CONTROL)


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


class GhosttyBindingSetSequencesTest(unittest.TestCase):
    def test_upstream_inventory_has_20_distinct_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 20)
        self.assertEqual(len(set(UPSTREAM_CASES)), 20)

    @unittest.expectedFailure
    def test_sequence_iterator_accepts_one_or_many_nonempty_chords(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=none",
            ">ctrl+c=none",
            "ctrl+d>=none",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"")

    @unittest.expectedFailure
    def test_parser_turns_a_sequence_into_leader_and_final_binding(self):
        arguments = remaps("ctrl+c>ctrl+d=none", "ctrl+e=none")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "c")
            control_key(terminal, "d")
            control_key(terminal, "e")

            self.assertEqual(terminal.read_input(), b"")

    def test_parse_and_put_typical_binding_routes_forward(self):
        with Shitty(extra_arguments=remaps("ctrl+a=ctrl+b")) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02")

    @unittest.expectedFailure
    def test_unconsumed_binding_runs_action_and_forwards_original_key(self):
        with Shitty(extra_arguments=remaps("unconsumed:ctrl+a=new_tab")) as terminal:
            control_key(terminal, "a")

            self.assertEqual(
                (terminal.read_input(), terminal.session_state()),
                (b"\x01", (2, 1)),
            )

    def test_removed_binding_no_longer_routes_its_sequence(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "ctrl+a>ctrl+b=unbind",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x01\x02")

    @unittest.expectedFailure
    def test_put_makes_the_binding_the_parent_of_the_next_action(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    @unittest.expectedFailure
    def test_put_flags_keeps_unconsumed_on_the_chained_binding(self):
        arguments = remaps("unconsumed:ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03\x01")

    @unittest.expectedFailure
    def test_sequence_makes_its_final_leaf_the_chain_parent(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03\x04")

    @unittest.expectedFailure
    def test_latest_leaf_under_a_leader_receives_the_chain(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+d",
            "ctrl+a>ctrl+c=ctrl+e",
            "chain=ctrl+f",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"\x05\x06")

    def test_unbinding_sequence_clears_its_chain_parent(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "ctrl+a>ctrl+b=unbind",
            "chain=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x01\x02")

    @unittest.expectedFailure
    def test_unbinding_one_sequence_leaf_preserves_its_sibling(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+d",
            "ctrl+a>ctrl+c=ctrl+e",
            "ctrl+a>ctrl+b=unbind",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")
            control_key(terminal, "a")
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"\x01\x02\x05")

    def test_direct_remove_rebuilds_without_the_old_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bindings.toml"
            path.write_text(config_text("ctrl+a=ctrl+b"))
            with Shitty(extra_arguments=("-config", path)) as terminal:
                control_key(terminal, "a")
                self.assertEqual(terminal.read_input(), b"\x02")

                path.write_text(config_text())
                os.kill(terminal.process.pid, signal.SIGUSR1)
                wait_for_key_output(terminal, "a", b"\x01")

    def test_invalid_rule_preserves_the_last_valid_mapping(self):
        arguments = remaps("ctrl+a=ctrl+b", "ctrl+c=invalid_action_xyz")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    def test_reloaded_binding_state_preserves_the_forward_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bindings.toml"
            path.write_text(config_text("ctrl+a=ctrl+b"))
            with Shitty(extra_arguments=("-config", path)) as terminal:
                os.kill(terminal.process.pid, signal.SIGUSR1)
                wait_for_key_output(terminal, "a", b"\x02")

    @unittest.expectedFailure
    def test_rebuilt_state_preserves_chained_actions(self):
        arguments = remaps("ctrl+a=ctrl+b", "chain=ctrl+c")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"\x02\x03")

    @unittest.expectedFailure
    def test_rebuilt_state_owns_independent_chained_text(self):
        arguments = remaps("ctrl+a=text:hello", "chain=text:world")
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")

            self.assertEqual(terminal.read_input(), b"helloworld")

    @unittest.expectedFailure
    def test_parse_and_put_sequence_routes_only_after_final_chord(self):
        with Shitty(extra_arguments=remaps("ctrl+a>ctrl+b=ctrl+c")) as terminal:
            control_key(terminal, "a")
            self.assertEqual(terminal.read_input(), b"")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x03")

    @unittest.expectedFailure
    def test_sequence_leader_can_have_two_actions(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+d",
            "ctrl+a>ctrl+c=ctrl+e",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")
            control_key(terminal, "a")
            control_key(terminal, "c")

            self.assertEqual(terminal.read_input(), b"\x04\x05")

    @unittest.expectedFailure
    def test_later_sequence_replaces_the_same_final_action(self):
        arguments = remaps(
            "ctrl+a>ctrl+b=ctrl+c",
            "ctrl+a>ctrl+b=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x04")

    @unittest.expectedFailure
    def test_sequence_replaces_a_direct_binding_at_its_leader(self):
        arguments = remaps(
            "ctrl+a=ctrl+c",
            "ctrl+a>ctrl+b=ctrl+d",
        )
        with Shitty(extra_arguments=arguments) as terminal:
            control_key(terminal, "a")
            self.assertEqual(terminal.read_input(), b"")
            control_key(terminal, "b")

            self.assertEqual(terminal.read_input(), b"\x04")


if __name__ == "__main__":
    unittest.main()

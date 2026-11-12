# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Chord remapping: -remap rewrites key events before anything reads them.

The rewrite happens at the router, so the legacy encoder, the kitty
protocol, and the application shortcuts all see the substituted chord;
the physical key keeps following its press-time remap through repeat and
release even when the modifiers were let go first.
"""

import tempfile
import unittest
from pathlib import Path

from harness import Shitty


SHIFT = 0x0001
CONTROL = 0x0002
ALT = 0x0004

PRESS = 1
RELEASE = 0

F5 = 294
F6 = 295


class RemapTest(unittest.TestCase):
    def test_control_chord_becomes_another_control_chord(self):
        with Shitty(extra_arguments=("-remap", "ctrl+b=ctrl+d")) as terminal:
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x04")

    def test_other_chords_pass_through(self):
        with Shitty(extra_arguments=("-remap", "ctrl+b=ctrl+d")) as terminal:
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            terminal.layout_key("B", "b", "b")
            terminal.frontend_text_event("b")
            self.assertEqual(terminal.read_input(), b"\x03b")

    def test_remap_matches_the_base_layout_identity(self):
        # On a Russian layout the physical B prints и, but the chord is
        # still ctrl+b - remaps follow the same ASCII-layout identity as
        # the control bytes themselves.
        with Shitty(extra_arguments=("-remap", "ctrl+b=ctrl+d")) as terminal:
            terminal.layout_key("B", "и", "b", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x04")

    def test_named_keys_remap(self):
        with Shitty(extra_arguments=("-remap", "f5=f6")) as terminal:
            terminal.layout_key(F5, 0, 0)
            self.assertEqual(terminal.read_input(), b"\x1b[17~")

    def test_modifiers_can_change_shape(self):
        with Shitty(extra_arguments=("-remap", "ctrl+shift+b=f5")) as terminal:
            terminal.layout_key("B", "b", "b", modifiers=CONTROL | SHIFT)
            self.assertEqual(terminal.read_input(), b"\x1b[15~")

    def test_none_swallows_the_chord(self):
        with Shitty(extra_arguments=("-remap", "ctrl+l=none")) as terminal:
            terminal.layout_key("L", "l", "l", modifiers=CONTROL)
            terminal.layout_key("C", "c", "c", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x03")

    def test_release_follows_the_press_remap(self):
        # Kitty mode reports releases. The user releases ctrl first, so
        # the release event no longer matches the chord textually - it
        # must still report d, or the application's key state desyncs.
        with Shitty(extra_arguments=("-remap", "ctrl+b=ctrl+d")) as terminal:
            terminal.write(b"\x1b[>3u")
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)
            press = terminal.read_input()
            terminal.layout_key("B", "b", "b", modifiers=0, action=RELEASE)
            release = terminal.read_input()
            self.assertIn(b"100", press)
            self.assertIn(b"100", release)
            self.assertNotIn(b"98", release)

    def test_remap_comes_from_the_config_file(self):
        text = 'remap = ["ctrl+b=ctrl+d", "ctrl+l=none"]\n'
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "shitty"
            home.mkdir(parents=True)
            (home / "shitty.toml").write_text(text)
            environment = {"XDG_CONFIG_HOME": directory}
            with Shitty(extra_environment=environment) as terminal:
                terminal.layout_key("B", "b", "b", modifiers=CONTROL)
                terminal.layout_key("L", "l", "l", modifiers=CONTROL)
                self.assertEqual(terminal.read_input(), b"\x04")

    def test_broken_rules_warn_and_are_ignored(self):
        arguments = ("-remap", "ctrl+=x", "-remap", "ctrl+b=ctrl+d")
        with Shitty(extra_arguments=arguments) as terminal:
            terminal.layout_key("B", "b", "b", modifiers=CONTROL)
            self.assertEqual(terminal.read_input(), b"\x04")


if __name__ == "__main__":
    unittest.main()

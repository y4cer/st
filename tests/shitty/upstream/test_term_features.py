"""iTerm2 feature reporting: OSC 1337;Capabilities and TERM_FEATURES."""

import sys
import unittest

from harness import Shitty


# The exact string pins the advertised capability set: growing it is a
# conscious edit here. Uw follows -unicodeWidths, pinned explicitly so
# the assertion does not depend on the host libc the auto-probe reads.
FEATURES = b"T3CwLrMSc7UUw17Ts3BFGsGoSyHNoSxP"
PINNED = ("-unicodeWidths", "17")


class TermFeaturesTest(unittest.TestCase):
    def test_capabilities_query_reports_the_feature_string(self):
        with Shitty(extra_arguments=PINNED) as terminal:
            terminal.read_input()
            terminal.write(b"\x1b]1337;Capabilities\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]1337;Capabilities=" + FEATURES + b"\x1b\\",
            )

    def test_bell_terminated_query_is_answered_too(self):
        with Shitty(extra_arguments=PINNED) as terminal:
            terminal.read_input()
            terminal.write(b"\x1b]1337;Capabilities\x07")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]1337;Capabilities=" + FEATURES + b"\x1b\\",
            )

    def test_other_1337_payloads_stay_silent(self):
        with Shitty(extra_arguments=PINNED) as terminal:
            terminal.read_input()
            terminal.write(b"\x1b]1337;SetUserVar=x\x1b\\")
            self.assertEqual(terminal.read_input(), b"")

    def test_the_reply_goes_to_the_asking_session(self):
        with Shitty(columns=8, rows=2, extra_arguments=PINNED) as terminal:
            terminal.new_session()
            terminal.read_input_of(0)
            terminal.read_input_of(1)
            terminal.write_to(0, b"\x1b]1337;Capabilities\x1b\\")
            self.assertEqual(
                terminal.read_input_of(0),
                b"\x1b]1337;Capabilities=" + FEATURES + b"\x1b\\",
            )
            self.assertEqual(terminal.read_input_of(1), b"")

    def test_children_get_term_features_in_the_environment(self):
        program = "import os\nos.write(1, os.environ['TERM_FEATURES'].encode() + b'\\r\\n')\n"
        with Shitty(columns=72, rows=3, extra_arguments=PINNED) as terminal:
            terminal.spawn(sys.executable, "-c", program)
            terminal.wait_read_pty()
            self.assertEqual(
                terminal.snapshot().lines[0].rstrip(),
                FEATURES.decode(),
            )


if __name__ == "__main__":
    unittest.main()

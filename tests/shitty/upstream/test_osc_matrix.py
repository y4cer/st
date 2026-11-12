# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


class OscMatrixTest(unittest.TestCase):
    def test_osc4_invalid_indices_do_not_block_valid_siblings(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b]4;1;#010203;2x;#aabbcc;3;#040506;"
                b"-1;#aabbcc;256;#aabbcc\x1b\\"
                b"\x1b]4;1;?;2;?;3;?\x1b\\"
            )
            reply = terminal.read_input()

            self.assertIn(b"\x1b]4;1;rgb:0101/0202/0303\x1b\\", reply)
            self.assertIn(b"\x1b]4;2;rgb:0000/aaaa/0000\x1b\\", reply)
            self.assertIn(b"\x1b]4;3;rgb:0404/0505/0606\x1b\\", reply)

    def test_osc4_invalid_specs_do_not_block_valid_siblings(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b]4;1;#010203;2;rgb:1/2;3;#040506\x1b\\"
                b"\x1b]4;1;?;2;?;3;?\x1b\\"
            )
            reply = terminal.read_input()

            self.assertIn(b"\x1b]4;1;rgb:0101/0202/0303\x1b\\", reply)
            self.assertIn(b"\x1b]4;2;rgb:0000/aaaa/0000\x1b\\", reply)
            self.assertIn(b"\x1b]4;3;rgb:0404/0505/0606\x1b\\", reply)

    def test_osc104_rejects_non_numeric_index_suffixes(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b]4;1;#010203;2;#040506\x1b\\"
                b"\x1b]104;1x;2\x1b\\"
                b"\x1b]4;1;?;2;?\x1b\\"
            )
            reply = terminal.read_input()

            self.assertIn(b"\x1b]4;1;rgb:0101/0202/0303\x1b\\", reply)
            self.assertIn(b"\x1b]4;2;rgb:0000/aaaa/0000\x1b\\", reply)

    def test_osc7_accepts_local_and_remote_file_authorities(self):
        with Shitty(columns=8, rows=2) as terminal:
            for uri in (
                b"file:///tmp/work",
                b"file://localhost/tmp/work",
                b"file://remote.example/tmp/work",
            ):
                with self.subTest(uri=uri):
                    self.assertEqual(terminal.osc7_cwd(uri), b"/tmp/work")

    def test_osc7_decodes_upper_and_lower_hex_escapes(self):
        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                terminal.osc7_cwd(b"file://host/a%2fb%2Fc%20d%7e"),
                b"/a/b/c d~",
            )

    def test_osc7_rejects_malformed_percent_escapes(self):
        with Shitty(columns=8, rows=2) as terminal:
            for uri in (b"/tmp/%", b"/tmp/%1", b"/tmp/%gg", b"/tmp/a%2"):
                with self.subTest(uri=uri):
                    self.assertEqual(terminal.osc7_cwd(uri), b"")

    def test_osc7_rejects_other_schemes_and_missing_file_paths(self):
        with Shitty(columns=8, rows=2) as terminal:
            for uri in (
                b"https://host/tmp",
                b"file://host",
                b"file://",
                b"relative",
                b"",
            ):
                with self.subTest(uri=uri):
                    self.assertEqual(terminal.osc7_cwd(uri), b"")

    def test_osc8_implicit_identity_reuses_equal_uris(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test/a\x1b\\A"
                b"\x1b]8;;\x1b\\"
                b"\x1b]8;;https://example.test/a\x1b\\B"
                b"\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                snapshot.cell(0, 0).hyperlink, snapshot.cell(1, 0).hyperlink
            )
            self.assertEqual(terminal.hyperlink_count(), 1)

    def test_osc8_id_and_uri_together_define_identity(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;id=x;https://example.test/a\x1b\\A"
                b"\x1b]8;id=x;https://example.test/a\x1b\\B"
                b"\x1b]8;id=x;https://example.test/b\x1b\\C"
                b"\x1b]8;;\x1b\\"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                snapshot.cell(0, 0).hyperlink, snapshot.cell(1, 0).hyperlink
            )
            self.assertNotEqual(
                snapshot.cell(1, 0).hyperlink, snapshot.cell(2, 0).hyperlink
            )
            self.assertEqual(terminal.hyperlink_count(), 2)

    def test_osc8_empty_uri_closes_link_even_with_parameters(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;id=x;https://example.test\x1b\\A"
                b"\x1b]8;id=ignored;\x1b\\B"
            )
            snapshot = terminal.snapshot()

            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(snapshot.cell(1, 0).hyperlink, 0)

    def test_malformed_osc8_does_not_change_active_link(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test\x1b\\A"
                b"\x1b]8;missing-uri-separator\x1b\\B"
                b"\x1b]8;;\x1b\\C"
            )
            snapshot = terminal.snapshot()

            self.assertEqual(
                snapshot.cell(0, 0).hyperlink, snapshot.cell(1, 0).hyperlink
            )
            self.assertEqual(snapshot.cell(2, 0).hyperlink, 0)

    def test_osc8_links_survive_scrollback_and_resolve_in_the_view(self):
        with Shitty(columns=4, rows=2, save_lines=4) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.test/history\x1b\\link"
                b"\x1b]8;;\x1b\\\r\nnext\r\nlive"
            )
            terminal.wheel_up()

            self.assertEqual(
                terminal.hyperlink(0, 0), "https://example.test/history"
            )

    def test_osc52_empty_payload_clears_selected_destinations(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(b"\x1b]52;pc;\x1b\\")
            self.assertEqual(terminal.get_selection(primary=True), b"")
            self.assertEqual(terminal.get_selection(primary=False), b"")

    def test_osc52_selector_order_does_not_change_destinations(self):
        with Shitty(columns=8, rows=2) as terminal:
            for selectors in (b"pc", b"cp", b"ppcc", b"spc"):
                with self.subTest(selectors=selectors):
                    terminal.set_primary_selection(b"primary")
                    terminal.set_system_clipboard(b"clipboard")
                    terminal.write(
                        b"\x1b]52;" + selectors + b";WA==\x1b\\"
                    )
                    self.assertEqual(
                        terminal.get_selection(primary=True), b"X"
                    )
                    self.assertEqual(
                        terminal.get_selection(primary=False), b"X"
                    )

    def test_osc52_rejects_malformed_base64_without_partial_content(self):
        with Shitty(columns=8, rows=2) as terminal:
            for payload in (
                b"=AAA",
                b"A===",
                b"AA=A",
                b"SGVsbG8!",
                b"A",
                b"AB",
            ):
                with self.subTest(payload=payload):
                    terminal.set_system_clipboard(b"unchanged")
                    terminal.write(b"\x1b]52;c;" + payload + b"\x1b\\")
                    self.assertEqual(
                        terminal.get_selection(primary=False),
                        b"unchanged",
                    )

    def test_osc52_executes_c0_without_feeding_it_to_base64(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_system_clipboard(b"unchanged")
            terminal.write(b"\x1b]52;c;AA==\n\x1b\\")
            self.assertEqual(terminal.get_selection(primary=False), b"\0")

    def test_osc52_allowed_empty_selection_reply_is_well_formed(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.write(b"\x1b]52;p;?\x1b\\")
            self.assertEqual(
                terminal.read_input(), b"\x1b]52;p;\x1b\\"
            )

    def test_osc52_read_policy_is_silent(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_primary_selection(b"secret")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(b"\x1b]52;p;?\x1b\\")
            self.assertEqual(terminal.read_input(), b"")

    def test_osc52_read_prefers_primary_and_falls_back_to_clipboard(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(b"\x1b]52;pc;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;p;cHJpbWFyeQ==\x1b\\",
            )
            terminal.set_primary_selection(b"")
            terminal.write(b"\x1b]52;pc;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;p;Y2xpcGJvYXJk\x1b\\",
            )

    def test_osc52_default_selector_reports_xterm_s0_alias(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.write(b"\x1b]52;;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;s0;cHJpbWFyeQ==\x1b\\",
            )

    def test_osc52_select_resource_redirects_selector_s(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(b"\x1b]52;s;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;s;cHJpbWFyeQ==\x1b\\",
            )
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=(
                "-allowOsc52Read",
                "true",
                "-osc52Select",
                "clipboard",
            ),
        ) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(b"\x1b]52;s;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]52;s;Y2xpcGJvYXJk\x1b\\",
            )


if __name__ == "__main__":
    unittest.main()

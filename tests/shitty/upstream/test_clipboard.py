# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import TEST_PLATFORM, Shitty


class ClipboardTest(unittest.TestCase):
    def test_primary_ownership_and_auto_copy_are_independent(self):
        with Shitty() as terminal:
            terminal.set_system_clipboard(b"external")
            terminal.set_primary_selection(b"primary", auto_copy=False)
            self.assertEqual(terminal.get_selection(primary=True), b"primary")
            self.assertEqual(terminal.get_selection(primary=False), b"external")

            terminal.set_primary_selection(b"mirrored", auto_copy=True)
            self.assertEqual(terminal.get_selection(primary=True), b"mirrored")
            self.assertEqual(terminal.get_selection(primary=False), b"mirrored")

    def test_osc52_writes_only_requested_owned_selections(self):
        with Shitty() as terminal:
            terminal.set_primary_selection(b"old-primary")
            terminal.set_system_clipboard(b"old-clipboard")
            terminal.write(b"\x1b]52;p;bmV3LXByaW1hcnk=\x1b\\")
            self.assertEqual(terminal.get_selection(primary=True), b"new-primary")
            self.assertEqual(
                terminal.get_selection(primary=False), b"old-clipboard"
            )

            terminal.write(b"\x1b]52;c;bmV3LWNsaXBib2FyZA==\x1b\\")
            self.assertEqual(terminal.get_selection(primary=True), b"new-primary")
            self.assertEqual(
                terminal.get_selection(primary=False), b"new-clipboard"
            )

    def test_copy_shortcut_follows_platform_convention(self):
        with Shitty(columns=8, rows=3) as terminal:
            terminal.write(b"abcd")
            for turn, (modifiers, clipboard, forwarded) in enumerate((
                (8, b"abc", b""),
                (1 | 2, b"external", b"\x03"),
            ) if TEST_PLATFORM == "cocoa" else (
                (8, b"external", b""),
                (1 | 2, b"abc", b""),
            )):
                terminal.set_system_clipboard(b"external")
                # A real window selection: the chord copies it.
                terminal.button(0, True, x=2, y=2, time=10 * turn + 1)
                terminal.button(0, False, x=2, y=2, time=10 * turn + 1.01)
                terminal.button(1, True, x=5, y=2, time=10 * turn + 2)
                terminal.button(1, False, x=5, y=2, time=10 * turn + 2.01)
                terminal.frontend_key_event(ord("C"), 1, modifiers=modifiers)
                terminal.frontend_key_event(ord("C"), 0, modifiers=modifiers)
                self.assertEqual(terminal.get_selection(primary=True), b"abc")
                self.assertEqual(terminal.get_selection(primary=False), clipboard)
                self.assertEqual(terminal.read_input(), forwarded)

    def test_copy_shortcut_without_selection_keeps_the_clipboard(self):
        # A TUI that selects for itself fills the clipboard through
        # OSC 52; the copy chord pressed out of habit right after must
        # not clobber it with a stale staged selection.
        with Shitty() as terminal:
            modifiers = 8 if TEST_PLATFORM == "cocoa" else 1 | 2
            terminal.set_primary_selection(b"stale")
            terminal.write(b"\x1b]52;c;ZnJlc2g=\x1b\\")
            self.assertEqual(terminal.get_selection(primary=False), b"fresh")
            terminal.frontend_key_event(ord("C"), 1, modifiers=modifiers)
            terminal.frontend_key_event(ord("C"), 0, modifiers=modifiers)
            self.assertEqual(terminal.get_selection(primary=False), b"fresh")
            self.assertEqual(terminal.get_selection(primary=True), b"stale")
            self.assertEqual(terminal.read_input(), b"")

    def test_paste_shortcut_follows_platform_convention(self):
        with Shitty() as terminal:
            for modifiers, forwarded in (
                (8, b"pasted text"),
                (1 | 2, b"\x16"),
            ) if TEST_PLATFORM == "cocoa" else (
                (8, b""),
                (1 | 2, b"pasted text"),
            ):
                terminal.set_system_clipboard(b"pasted text")
                terminal.frontend_key_event(ord("V"), 1, modifiers=modifiers)
                terminal.frontend_key_event(ord("V"), 0, modifiers=modifiers)
                self.assertEqual(terminal.read_input(), forwarded)

    def test_super_c_with_other_modifiers_is_not_copy(self):
        with Shitty() as terminal:
            terminal.set_system_clipboard(b"external")
            terminal.set_primary_selection(b"selected")
            terminal.frontend_key_event(ord("C"), 1, modifiers=8 | 2)
            terminal.frontend_key_event(ord("C"), 0, modifiers=8 | 2)
            self.assertEqual(terminal.get_selection(primary=False), b"external")
            self.assertEqual(terminal.read_input(), b"\x03")

    def test_paste_converts_newlines_and_brackets(self):
        # The pasteboard path every frontend shares: newlines become
        # carriage returns, and bracketed paste mode wraps the payload.
        with Shitty(columns=8, rows=2) as terminal:
            terminal.paste(b"one\ntwo")
            self.assertEqual(terminal.read_input(), b"one\rtwo")
            terminal.write(b"\x1b[?2004h")
            terminal.paste(b"three\nfour")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[200~three\rfour\x1b[201~",
            )
            terminal.paste(b"")
            self.assertEqual(terminal.read_input(), b"\x1b[200~\x1b[201~")

    def test_paste_shortcut_carries_large_and_truncated_payloads(self):
        # Over a kilobyte the paste transaction copies the payload to an
        # owned buffer before parking; a payload ending in a bare C1 lead
        # byte flushes that lead when the stream closes.
        modifiers = 8 if TEST_PLATFORM == "cocoa" else 1 | 2
        big = b"a" * 2000
        with Shitty() as terminal:
            terminal.set_system_clipboard(big)
            terminal.frontend_key_event(ord("V"), 1, modifiers=modifiers)
            terminal.frontend_key_event(ord("V"), 0, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), big)
            terminal.set_system_clipboard(b"x\xc2")
            terminal.frontend_key_event(ord("V"), 1, modifiers=modifiers)
            terminal.frontend_key_event(ord("V"), 0, modifiers=modifiers)
            self.assertEqual(terminal.read_input(), b"x\xc2")


    def test_clipboard_paste_neutralizes_c1_and_pictures_controls(self):
        # A C1 control after its UTF-8 lead becomes U+FFFD, a lone lead
        # before a plain byte stays, C0 bytes turn into control pictures,
        # and a trailing lead is flushed as is.
        modifiers = 8 if TEST_PLATFORM == "cocoa" else 1 | 2

        def paste(terminal, payload):
            terminal.set_system_clipboard(payload)
            terminal.frontend_key_event(ord("V"), 1, modifiers=modifiers)
            terminal.frontend_key_event(ord("V"), 0, modifiers=modifiers)
            return terminal.read_input()

        with Shitty(columns=8, rows=2) as terminal:
            self.assertEqual(
                paste(terminal, b"a\xc2\x85b\xc2\x41\x7f\x01"),
                b"a\xef\xbf\xbdb\xc2A\xe2\x90\xa1\xe2\x90\x81",
            )
            self.assertEqual(paste(terminal, b"x\xc2"), b"x\xc2")
            self.assertEqual(
                paste(terminal, b"\x85\xc2\xc2\x85"), b"\x85\xc2\xef\xbf\xbd"
            )


    def test_auto_copy_mirrors_a_mouse_selection_into_the_clipboard(self):
        with Shitty(
            columns=10, rows=4, extra_arguments=("-autoCopy",),
            glyph_px=10, glyph_py=10,
        ) as terminal:
            terminal.write(b"hello world")
            terminal.button(0, True, x=2, y=2, time=1)
            terminal.pointer(42, 2)
            terminal.button(0, False, x=42, y=2, time=1.5)
            self.assertEqual(terminal.get_selection(primary=True), b"hell")
            self.assertEqual(terminal.get_selection(primary=False), b"hell")


if __name__ == "__main__":
    unittest.main()

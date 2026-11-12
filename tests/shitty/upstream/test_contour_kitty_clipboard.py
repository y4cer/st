# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import base64
import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "KittyClipboard.parse.read_request",
    "KittyClipboard.parse.metadata_is_colon_separated",
    "KittyClipboard.parse.primary_selection",
    "KittyClipboard.parse.rejects_malformed",
    "KittyClipboard.parse.ignores_unknown_keys",
    "KittyClipboard.supported_mime_types",
    "KittyClipboard.mode_5522_is_a_recognised_mode",
    "KittyClipboard.write_transmission_reaches_the_clipboard",
    "KittyClipboard.chunks_are_reassembled_in_order",
    "KittyClipboard.an_endless_write_stream_is_abandoned_not_accumulated",
    "KittyClipboard.data_without_an_open_write_is_refused",
    "KittyClipboard.an_unsupported_mime_type_is_refused_not_dropped",
    "KittyClipboard.read_is_refused_when_not_permitted",
    "KittyClipboard.a_write_to_the_primary_selection_is_refused",
    "KittyClipboard.the_targets_probe_lists_the_available_types",
    "KittyClipboard.a_large_read_is_chunked",
    "KittyClipboard.a_write_survives_a_status_line_switch",
    "KittyClipboard.a_read_is_answered_in_the_5522_protocol",
    "KittyClipboard.a_read_for_only_unsupported_types_is_refused",
)


def encoded(value):
    return base64.b64encode(value)


def packet(metadata, payload=None):
    result = b"\x1b]5522;" + metadata
    if payload is not None:
        result += b";" + encoded(payload)
    return result + b"\x1b\\"


def parse_packets(data):
    packets = []
    while data:
        assert data.startswith(b"\x1b]5522;"), data
        end = data.index(b"\x1b\\")
        body = data[7:end]
        data = data[end + 2:]
        if b";" in body:
            metadata, payload = body.split(b";", 1)
            payload = base64.b64decode(payload, validate=True)
        else:
            metadata = body
            payload = None
        fields = {}
        for record in metadata.split(b":"):
            key, value = record.split(b"=", 1)
            fields[key.decode()] = value.decode()
        packets.append((fields, payload))
    return packets


class ContourKittyClipboardTest(unittest.TestCase):
    def test_upstream_inventory_is_complete(self):
        self.assertEqual(len(UPSTREAM_CASES), 19)
        self.assertEqual(len(set(UPSTREAM_CASES)), 19)

    def test_read_request_and_id_are_parsed(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_system_clipboard(b"hello")
            terminal.write(
                packet(
                    b"type=read:id=a!b+c.",
                    b"text/plain",
                )
            )
            replies = parse_packets(terminal.read_input())
            self.assertEqual([entry[0]["status"] for entry in replies], ["OK", "DATA", "DONE"])
            self.assertEqual([entry[0]["id"] for entry in replies], ["ab+c."] * 3)
            self.assertEqual(replies[1][1], b"hello")

    def test_metadata_is_colon_separated_and_mime_is_decoded(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:id=7"))
            terminal.write(
                packet(
                    b"type=wdata:mime=" + encoded(b"text/plain") + b":id=7",
                    b"AB",
                )
            )
            terminal.write(packet(b"type=wdata:id=7"))
            self.assertEqual(terminal.get_selection(primary=False), b"AB")

    def test_primary_selection_is_distinct_and_supported(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_primary_selection(b"primary")
            terminal.set_system_clipboard(b"clipboard")
            terminal.write(packet(b"type=read:loc=primary", b"text/plain"))
            replies = parse_packets(terminal.read_input())
            self.assertEqual(replies[0][0]["loc"], "primary")
            self.assertEqual(replies[1][1], b"primary")

    def test_malformed_and_unknown_packets_are_rejected(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:novalue"))
            replies = parse_packets(terminal.read_input())
            self.assertEqual(replies[0][0]["status"], "EINVAL")
            terminal.write(packet(b"type=nonsense"))
            self.assertEqual(terminal.read_input(), b"")

    def test_unknown_metadata_keys_do_not_hide_known_operation(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:name=Zm9v:pw=cHc=:id=1"))
            terminal.write(
                packet(
                    b"type=wdata:mime=" + encoded(b"text/plain"),
                    b"hello",
                )
            )
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"hello")

    def test_supported_text_mime_aliases_and_unsupported_mime(self):
        supported = (b"", b"text/plain", b"text/plain;charset=utf-8", b"UTF8_STRING", b"STRING", b"TEXT")
        for mime in supported:
            with self.subTest(mime=mime):
                with Shitty(columns=8, rows=2) as terminal:
                    terminal.write(packet(b"type=write"))
                    metadata = b"type=wdata"
                    if mime:
                        metadata += b":mime=" + encoded(mime)
                    terminal.write(packet(metadata, b"x"))
                    terminal.write(packet(b"type=wdata"))
                    self.assertEqual(terminal.get_selection(primary=False), b"x")
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write"))
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"image/png"), b"x"))
            self.assertEqual(parse_packets(terminal.read_input())[0][0]["status"], "ENOSYS")

    def test_mode_5522_is_recognised(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b[?5522$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?5522;2$y")

    def test_mode_5522_turns_paste_into_a_mime_notification(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_system_clipboard(b"not pasted directly")
            terminal.write(b"\x1b[?5522h")
            self.assertTrue(terminal.paste_clipboard())
            replies = parse_packets(terminal.read_input())
            self.assertEqual([entry[0]["status"] for entry in replies], ["OK", "DATA", "DONE"])
            self.assertEqual(base64.b64decode(replies[1][0]["mime"]), b".")
            self.assertIn(b"text/plain", replies[1][1].split())

    def test_write_transmission_reaches_clipboard(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:id=1"))
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), b"hello"))
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"hello")
            self.assertEqual(parse_packets(terminal.read_input())[0][0], {"type": "write", "status": "DONE", "id": "1"})

    def test_write_chunks_are_reassembled_in_order(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:id=2"))
            for part in (b"one ", b"two ", b"three"):
                terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), part))
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"one two three")

    def test_endless_write_is_abandoned_at_eight_mib(self):
        chunk = b"x" * (256 * 1024)
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:id=9"))
            for _ in range(33):
                terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), chunk))
            replies = parse_packets(terminal.read_input())
            self.assertEqual(replies[-1][0]["status"], "EIO")
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"")

    def test_data_without_open_write_is_ignored(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), b"x"))
            self.assertEqual(terminal.read_input(), b"")
            self.assertEqual(terminal.get_selection(primary=False), b"")

    def test_unsupported_mime_aborts_the_transmission(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write:id=3"))
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"image/png"), b"\x89PNG"))
            self.assertEqual(parse_packets(terminal.read_input())[0][0]["status"], "ENOSYS")
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"")

    def test_read_requires_permission(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=read:id=4", b"text/plain"))
            reply = parse_packets(terminal.read_input())[0][0]
            self.assertEqual(reply["status"], "EPERM")
            self.assertEqual(reply["id"], "4")

    def test_primary_write_uses_primary_instead_of_system_clipboard(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_system_clipboard(b"user clipboard")
            terminal.write(packet(b"type=write:loc=primary"))
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), b"selection"))
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=True), b"selection")
            self.assertEqual(terminal.get_selection(primary=False), b"user clipboard")

    def test_targets_probe_lists_text_plain_without_read_permission(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.set_system_clipboard(b"hello")
            terminal.write(packet(b"type=read", b"."))
            replies = parse_packets(terminal.read_input())
            self.assertEqual([entry[0]["status"] for entry in replies], ["OK", "DATA", "DONE"])
            self.assertEqual(base64.b64decode(replies[1][0]["mime"]), b".")
            self.assertIn(b"text/plain", replies[1][1].split())

    def test_large_read_is_split_before_base64_encoding(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_system_clipboard(b"x" * 10000)
            terminal.write(packet(b"type=read", b"text/plain"))
            replies = parse_packets(terminal.read_all_input())
            data = [payload for fields, payload in replies if fields["status"] == "DATA"]
            self.assertEqual(list(map(len, data)), [4096, 4096, 1808])
            self.assertEqual(b"".join(data), b"x" * 10000)

    def test_write_state_survives_screen_switch(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=write"))
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), b"one "))
            terminal.write(b"\x1b[?1049h")
            terminal.write(packet(b"type=wdata:mime=" + encoded(b"text/plain"), b"two"))
            terminal.write(b"\x1b[?1049l")
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"one two")

    def test_read_uses_only_osc_5522_packets(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.set_system_clipboard(b"hello")
            terminal.write(packet(b"type=read", b"text/plain"))
            reply = terminal.read_input()
            self.assertNotIn(b"\x1b]52;", reply)
            packets = parse_packets(reply)
            self.assertEqual(packets[1][1], b"hello")

    def test_read_for_only_unsupported_types_is_refused(self):
        with Shitty(
            columns=8,
            rows=2,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.write(packet(b"type=read:id=5", b"image/png application/octet-stream"))
            reply = parse_packets(terminal.read_input())[0][0]
            self.assertEqual(reply["status"], "ENOSYS")
            self.assertEqual(reply["id"], "5")


    def test_malformed_metadata_is_refused_per_operation(self):
        with Shitty(columns=8, rows=2) as terminal:
            # A record without "=" poisons the packet: a read answers
            # ENOSYS, a data chunk with broken base64 aborts the open
            # write, and a malformed alias record aborts the next one.
            terminal.write(packet(b"type=read:bogus"))
            self.assertEqual(
                parse_packets(terminal.read_input())[0][0],
                {"type": "read", "status": "ENOSYS"},
            )
            terminal.write(packet(b"type=write:id=1"))
            terminal.write(b"\x1b]5522;type=wdata:mime=" + encoded(b"text/plain") + b";!!!\x1b\\")
            self.assertEqual(
                parse_packets(terminal.read_input())[0][0],
                {"type": "write", "status": "EINVAL", "id": "1"},
            )
            terminal.write(packet(b"type=write:id=2"))
            terminal.write(b"\x1b]5522;type=walias:bogus\x1b\\")
            self.assertEqual(
                parse_packets(terminal.read_input())[0][0],
                {"type": "write", "status": "EINVAL", "id": "2"},
            )
            terminal.write(packet(b"type=wdata"))
            self.assertEqual(terminal.get_selection(primary=False), b"")


    def test_empty_metadata_records_are_skipped(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(packet(b"type=read::id=1", b"."))
            replies = parse_packets(terminal.read_input())
            self.assertEqual(replies[0][0], {"type": "read", "status": "OK", "id": "1"})
            self.assertEqual(replies[-1][0]["status"], "DONE")


if __name__ == "__main__":
    unittest.main()

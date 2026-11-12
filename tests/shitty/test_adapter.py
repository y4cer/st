"""Contract checks for the real-code bridges and protocol representation."""
import unittest
from harness import Shitty, Unsupported

class AdapterTest(unittest.TestCase):
    def test_cursor_and_embedded_nul(self):
        with Shitty(columns=8,rows=3) as t:
            t.write(b'\x1b[2\0;3HX')
            self.assertEqual((t.snapshot().cursor_x,t.snapshot().cursor_y),(3,1))
            self.assertEqual(t.snapshot().cell(2,1).char,'X')
    def test_partial_utf8_is_retained_across_commands(self):
        with Shitty(columns=8,rows=2) as t:
            t.write_chunks(b'A\xe7',b'\x95',b'\x8cB')
            s=t.snapshot()
            self.assertEqual(s.lines[0],'A界 B    ')
            self.assertTrue(s.cell(1,0).double_width)
            self.assertTrue(s.cell(2,0).double_width_continuation)
    def test_replies_larger_than_socket_packet_capacity(self):
        with Shitty(columns=8,rows=2) as t:
            for _ in range(2):
                t.write(b'\x1b[5n'*4096)
                self.assertEqual(t.read_input(),b'\x1b[0n'*4096)
    def test_palette_and_truecolor_source_indices(self):
        with Shitty(columns=8,rows=2) as t:
            t.write(b'\x1b[31mA\x1b[38;2;1;2;3mB\x1b[0mC')
            s=t.model_snapshot()
            self.assertEqual([s.cell(x,0).foreground_index for x in range(3)],[1,-1,-2])
            self.assertEqual(s.cell(1,0).foreground,(1,2,3))
    def test_live_and_scrollback_snapshots(self):
        with Shitty(columns=4,rows=2) as t:
            t.write(b'A\r\nB\r\nC'); t.wheel_up()
            self.assertEqual(t.snapshot().lines,['A   ','B   '])
            self.assertEqual(t.all_text(),('A','B','C'))
    def test_half_open_selection_maps_to_st_cells(self):
        with Shitty(columns=8,rows=2) as t:
            t.write(b'abcdef'); t.select_start(1,0); t.select_update(4,0)
            self.assertEqual(t.select_finish(),b'bcd')
            t.select_clear();self.assertFalse(t.has_selection())
    def test_real_x11_key_focus_and_mouse_routes(self):
        with Shitty(columns=8,rows=2) as t:
            t.key('UP');self.assertEqual(t.read_input(),b'\x1b[A')
            t.write(b'\x1b[?1h');t.key('UP');self.assertEqual(t.read_input(),b'\x1bOA')
            t.key('ENTER',2);self.assertEqual(t.read_input(),b'\x1b[13;5u')
            t.write(b'\x1b[?1004h');t.focus(False);self.assertEqual(t.read_input(),b'\x1b[O')
            self.assertEqual(t.mouse_encode(2,0,0,0,1,2,3),b'\x1b[<0;2;3M')
    def test_real_utf8_encoder_for_alt_8bit(self):
        with Shitty() as t:
            t.write(b'\x1b[?1034h');t.char('a',4)
            self.assertEqual(t.read_input(),b'\xc3\xa1')
    def test_unavailable_palette_cannot_pass(self):
        with Shitty() as t:
            with self.assertRaisesRegex(Unsupported,'dynamic Xft palette'):
                t.write(b'\x1b]4;1;?\x07')
    def test_large_cursor_counts_saturate_without_overflow(self):
        with Shitty(columns=8,rows=4) as t:
            for count in (2147483647,2147483648,999999999999999999999):
                for op in ('C','a','B','e','E'):
                    t.write(b'\x1b[2;2H'+f'\x1b[{count}{op}'.encode())
                    s=t.snapshot()
                    self.assertEqual((s.cursor_x,s.cursor_y), (7,1) if op in ('C','a') else (0,3) if op=='E' else (1,3))
                t.write(b'\x1b[2;2H'+f'\x1b[{count}X'.encode())
                t.write(b'\x1b[2;4r\x1b[?6h'+f'\x1b[{count};1H'.encode())
                self.assertEqual(t.snapshot().cursor_y,3)
                t.write(b'\x1b[?6l\x1b[r')
    def test_negative_edit_counts_do_not_default_to_one(self):
        with Shitty(columns=8,rows=3) as t:
            t.write(b'abcdefgh\r\nijklmnop\r\nqrstuvwx\x1b[2;4H')
            before=t.snapshot().lines
            for op in ('P','@','L','M','X','S','T'):
                t.write(f'\x1b[-2{op}'.encode())
                self.assertEqual(t.snapshot().lines,before)
    def test_growing_screen_preserves_last_old_cell(self):
        with Shitty(columns=4,rows=2) as t:
            t.write(b'abcd');t.resize(8,4)
            self.assertEqual(t.snapshot().lines[0],'abcd    ')
    def test_real_x11_paste(self):
        with Shitty(columns=8,rows=2) as t:
            t.write(b'\x1b[?2004h');t.paste(b'a\nb')
            self.assertEqual(t.read_input(),b'\x1b[200~a\rb\x1b[201~')
if __name__=='__main__':unittest.main()

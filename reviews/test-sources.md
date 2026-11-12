## Findings

Read-only inspection completed; no files modified and no tests executed. Failures below are established by code inspection, not runtime verification.

### Concrete bugs in this custom st

- **Reverse index corrupts scrollback.** `st.c:2432` calls `tscrolldown(..., 1)`, which decrements `histi`, adds the region’s bottom row to history, and increments `histlen` (`st.c:1126–1131`). RI should move screen rows, not rewrite existing history.
- **Interior scrolling leaks rows into history.** LF/IND always request history capture (`st.c:1205,2419`); `tscrollup()` checks alternate-screen mode but not whether the region starts at row zero (`st.c:1155`). This also contaminates the history exposed by `browse.c:29`.
- **Alternate screen can display primary history.** `tswapscreen()` leaves `term.scr` unchanged (`st.c:1075`), while `TLINE()` uses it regardless of alternate-screen mode (`st.c:48`). Alternate scrolling can additionally increment it (`st.c:1163`).
- **Scrollback navigation exceeds populated history.** `kscrollup()` bounds against `HISTSIZE`, not `histlen`, and has no alternate-screen guard (`st.c:1104`).
- **Wide-cell integrity is broken by erase, editing, and resize.** `tclearregion()`, `tdeletechar()`, `tinsertblank()`, and `tresize()` do not repair split `ATTR_WIDE`/`ATTR_WDUMMY` pairs (`st.c:1308,1338,1355,2654`). These appear inherited rather than specific to the custom scrollback patch.

## Recommended headless cases

Use real `tnew(cols, rows)`, `twrite(bytes, length, 0)`, and `tresize()`. Coordinates below are zero-based; `ESC` means byte `0x1b`. Run each case with fresh terminal state.

| # | Case and bytes | Expected outcome / relevance |
|---|---|---|
| 1 | **Parser controls and chunking**, 8×3: `ESC[2\x00;3HX`, separately `ESC[2\x7f;3HX`. Feed whole and split at every byte. | `X` at `(2,1)`, cursor `(3,1)`; NUL/DEL must not cancel CSI. Source: `tst/test_parser_states.py`. |
| 2 | **Interior scroll with BCE**, 5×5: `A ESC[2;1HB ESC[3;1HC ESC[4;1HD ESC[5;1HE` **without the explanatory spaces**, then `ESC[2;4r ESC[4;1H ESC[42m\n`. | Rows begin `A,C,D,blank,E`; cursor `(0,3)`; new blank row has background index 2 and no rendition flags. `histlen` stays zero. **Fails history assertion.** Sources: `test_scrollback.py`, `test_ghostty_screen_scroll_region_history.py`. |
| 3 | **RI preserves real history**, 4×3: `A\r\nB\r\nC\r\nD`, then `ESC[H ESC M` (concatenated). | Initial history contains `A`; afterward visible rows are blank, `B`, `C`, and history remains exactly `A`, including index/count. Repeat with `ESC[2;3r ESC[2;1H ESC M` from fresh setup: rows `B,blank,C`, same history. **Fails.** Source: `test_scrollback.py::test_codex_*reverse_index_preserves_real_history`. |
| 4 | **1049 round trip and history isolation**, 4×3: `A\r\nB\r\nC\r\nD`; `kscrollup({.i=1})`; then `ESC[?1049h ESC[H1\r\n2\r\n3\r\n4 ESC[?1049l` (concatenated). | While alternate is active, show `2,3,4`, never primary history; primary history remains `A`. On return, primary cells `B,C,D` and saved cursor `(1,2)` survive. Assert alternate navigation cannot expose history. **Current `scr` handling fails isolation.** Source: `test_scrollback.py`. |
| 5 | **Navigation clamps to actual history**, 4×3: first no bytes; call `kscrollup({.i=1})`. Then fresh setup with `A\r\nB\r\nC\r\nD`, call `kscrollup({.i=2})`. | `scr` is respectively 0 and 1, not 1 and 2. This is a custom-history invariant, not an escape-sequence standard. **Fails.** Source: `test_scrollback.py::test_new_output_preserves_scrolled_view`. |
| 6 | **Delayed wrap**, 5×3: write `ABCDE`, inspect, then `F`. Fresh variant: `ABCDE\rZ`. | First checkpoint: cursor `(4,0)`, `CURSOR_WRAPNEXT`, no scroll. `F` starts row 2 and marks row 1 `ATTR_WRAP`. CR variant produces `ZBCDE`, no wrap. Also test `ESC[?7lABCDEF` → `ABCDF` on row 1. Source: `tst/libvterm/upstream/20state_wrapping.test`. |
| 7 | **Wide erase boundaries**, 6×2: `A\xe7\x95\x8cB ESC[1;3H ESC[X` (concatenated); repeat using `ESC[K`. | Both cells occupied by `界` become ordinary blanks; no orphan lead or dummy. ECH retains `B` at column 3; EL clears it. **Fails pair repair.** Source: `test_xtermjs_input_handler_wide.py`. |
| 8 | **Wide editing boundaries**, 6×2: `A\xe7\x95\x8cBC ESC[1;3H ESC[P`; fresh variant substitutes `ESC[@`. | DCH: cells spell `A BC  `. ICH: `A   BC`. In both, the split wide glyph is removed and every remaining wide lead/dummy is paired. **Fails.** Source: `test_xtermjs_input_handler_wide.py`. |
| 9 | **Resize truncating a wide glyph**, 5×2: `abc\xe7\x95\x8c`; call `tresize(4,2)`, then `tresize(6,2)`. | Shrink yields `abc ` with no wide flag on column 3; growth must not resurrect an orphan wide glyph. Apply integrity checks to primary, alternate, and populated history rows. **Fails.** Source: `test_resize_wide_grapheme.py::test_shrink_never_leaves_wide_lead_without_continuation`. |
| 10 | **RIS restores core defaults**, 12×4: `ESC[3g ESC[2;3r ESC[?6h ESC[?7l ESC[31;42m ESC c\tX` (concatenated). | Default margins `(0,3)`, origin off, autowrap on, default colors; cleared screen with `X` at `(8,0)`. Repeat from alternate screen and check both buffers are cleared and normal-screen mode is active. Source: `test_reset_matrix.py::test_ris_restores_default_tab_stops`, extended for st state. |

### Harness cautions

- Use a UTF-8 locale and verify `wcwidth(U+754C)==2`.
- For split UTF-8 input, retain and refeed bytes not consumed by `twrite()`; it deliberately returns short for incomplete characters.
- Stub frontend callbacks, not terminal operations. Inspect cells, cursor, margins, modes, and history directly.
- Do not import expectations for unsupported DECSTR, horizontal margins, grapheme clusters, or resize reflow as ordinary st regressions.

## Sources and attribution

All `tst/...` paths above are under **`/tmp/st-review/shitty/`**; st paths are under **`/home/lesorub/progs/st/`**.

- Referenced first-party Python files carry **Copyright © 2026 Shitty team, MIT**, with terms in `/tmp/st-review/shitty/LICENSE.MIT`.
- `/tmp/st-review/shitty/LICENSE` explicitly says the imported baseline remains **GPL-3.0-or-later**; do not treat the entire repository as MIT.
- libvterm wrapping source: `/tmp/st-review/shitty/tst/libvterm/LICENSE.upstream`, **MIT, Copyright © 2008 Paul Evans**.
- For xterm.js-derived wide-cell adaptations, retain upstream attribution too: `/tmp/st-review/shitty/tst/xtermjs/LICENSE.upstream`, **MIT**, xterm.js authors, SourceLair, and Christopher Jeffrey.

Preserve applicable copyright and permission notices when copying/adapting substantial test material.

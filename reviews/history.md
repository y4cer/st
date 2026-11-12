Read-only audit; no files modified. Findings below are source-derived, with proposed regression cases—not executed tests. Paths are relative to `/home/lesorub/progs/st`.

1. **High — Resize leaves selection coordinates pointing outside the screen.**  
   **Location:** `st.c:2654–2745`, `st.c:610–620`  
   Height reduction neither clears nor remaps `sel`. A subsequent `getsel()` accesses `TLINE(y)` using old row coordinates, potentially reading beyond the resized `term.line` allocation. Closing copy mode does not address ordinary selections.  
   **Regression:** Select rows 20–23 of a 24-row terminal, shrink to 10 rows, then press Print (`printsel`). Run under ASan; expect selection invalidation or safe remapping, not an out-of-bounds read.  
   **Fix:** Clear or correctly transform selections before resizing. This is inherited code.

2. **High — Rectangular selection can read before a line allocation.**  
   **Location:** `st.c:624–644`  
   Trimming spaces can decrement `last` to before the line start. The newline condition subsequently evaluates `last->mode`, even for rectangular selections, because the rectangular check comes afterward.  
   **Regression:** Put `"    X"` on two consecutive rows; rectangular-select columns 0–1 across both and copy. On the first row, `last` becomes `line - 1`; ASan should catch the read.  
   **Fix:** Never derive wrapping from the decremented trimming pointer; retain a valid boundary glyph and handle empty ranges explicitly. Inherited code.

3. **Medium — Reverse index breaks the new populated-history invariant.**  
   **Location:** `st.c:1126–1131`; `browse.c:39–42`  
   Copy mode assumes `histlen` populated entries end at `histi` and extend backward. Reverse scrolling instead decrements `histi` while increasing `histlen`. After ordinary history accumulation, this overwrites an older entry and makes the snapshot include unpopulated/stale slots while omitting recent history.  
   **Regression:** From a fresh terminal, generate exactly one history line `A`, put `B` on the bottom screen row, then send `ESC[H ESC M`. The resulting two-entry snapshot includes an unused slot and `B`, rather than retaining `A`.  
   **Fix:** Use a consistent append direction for every history producer, or exclude reverse-index output from history.

4. **Medium — Scrollback navigation ignores `histlen` and alternate-screen isolation.**  
   **Location:** `st.c:48–50`, `st.c:1104–1116`  
   `kscrollup()` permits scrolling into all 2,000 slots regardless of populated history. It also operates on the alternate screen; `TLINE()` then displays primary-screen history there, despite the custom changes preventing alternate-screen history writes.  
   **Regression:** In a fresh terminal, scroll upward: blank, nonexistent history becomes navigable. Separately, populate primary history, enter `ESC[?1049h`, and press Shift–PageUp: primary history appears over the alternate screen.  
   **Fix:** Clamp upward movement to available history and reject it on the alternate screen.

5. **Medium — Copy-mode search cannot match text spanning a wide glyph’s dummy cell.**  
   **Location:** `browse.c:113–125`  
   Search compares query runes against consecutive physical cells. A wide character occupies a real cell plus `ATTR_WDUMMY`, so queries such as `界a` or `界界` cannot match their displayed text.  
   **Regression:** Display `界a`, enter copy mode, move elsewhere, and search `/界a`. Assert the cursor reaches that string.  
   **Fix:** Match logical characters, skipping dummy cells while retaining physical cursor coordinates.

6. **Medium — Copy-mode cursor can select only half of a wide character, yielding empty text.**  
   **Location:** `browse.c:91–93`, `browse.c:175–182`  
   Horizontal movement and `$` can land on `ATTR_WDUMMY`. Yanking a characterwise selection containing only that cell silently skips it. The cursor/highlight also does not reliably identify the corresponding visible character.  
   **Regression:** Display `界` at column zero; in copy mode move to column zero, then press `lvy`. The clipboard becomes empty rather than containing `界`.  
   **Fix:** Move between glyph boundaries and normalize selection endpoints to include the wide glyph’s leading cell.

7. **Medium — Copy mode deletes significant spaces at soft-wrap boundaries.**  
   **Location:** `browse.c:88–96`  
   `browseyank()` trims trailing spaces unconditionally, including spaces belonging to a wrapped logical line. It then suppresses the newline, joining words without their original separator.  
   **Regression:** At width 5, output `abcd ef` without an explicit newline. Characterwise-select both physical rows through `f` and yank. Actual result is `abcdef`; expected is `abcd ef`.  
   **Fix:** Preserve spaces at selected soft-wrap boundaries; trim only appropriate hard-line padding.

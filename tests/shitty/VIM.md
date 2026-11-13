# Copy-mode yank operators

User request, 2026-11-13: compose read-only Vim-style commands such as `y$` and
`yw`, rather than copying a whole line immediately on the first `y`.

The real `browse.c` now keeps per-session operator/count state. In NORMAL, `y`
waits; `yy` copies the current physical row. In VISUAL, `y` still copies at once.
`y` plus `h/l/0/^/$/w/b/e/W/B/E` produces a character range; `j/k/gg/G/H/M/L`
produces complete rows. Arrow/Home/End motions are accepted too. Counts multiply
(`2y3w` means six word motions), capped at 10000. Counts on `gg/G` address a
physical snapshot row. A failed/unsupported motion or Escape cancels without
changing the clipboard; q/i and Ctrl+c still exit the viewer. The status line
shows the pending sequence.

Exclusive motions do not copy the target cell; `e/$` include it. `yw` includes
spaces before the next word on the same logical line, but its final step stops
at text before a hard newline. Empty hard rows are individual w/b stops; e
skips them. Exclusive backwards motions from column zero become linewise when
they reach the first nonblank of an earlier row. Vertical yj/yk at the snapshot
boundary are no-ops. The final empty row at EOF has no following hard break
and does not add an extra newline to an exclusive word yank. Soft-wrapped rows are joined when extracting;
hard breaks are retained. Wide continuations are skipped for word/operator
motions, and ranges include complete wide glyphs. Forward yanks retain the
origin; backwards yanks move to the range start. The immutable snapshot and
live terminal contents are unchanged; PRIMARY/CLIPBOARD and the existing yank
flash are updated only after a complete command.

Reference: Shitty revision `509bd3f95778729d9890c68ab150d94bff372a0e`, unchanged
`upstream/test_selection_wrapped_lines.py`, `test_selection_word_unicode.py`,
`test_selection_direction_matrix.py`: soft/hard boundaries, reverse ranges,
Unicode/wide cells, and copy extraction. These remain selection invariants,
not a claim that Shitty exposes our copy-mode command grammar. Existing native
visual/copy tests remain active; their old single-y line commands now use yy.
Ten real-core operator cases are in `tests/test_browse_ops.h`, included by
`tests/test_terminal.c`. They cover operators, multiplied counts, hard-newline
word behavior, line ranges, cancellation/status, punctuation versus WORD,
wide wraps, empty hard rows, padding/end-of-buffer cancellation, immutable
snapshots and per-session pending operators.

Local Neovim (`/usr/bin/vim` resolves to `/usr/bin/nvim`, run with
`-Nu NONE -n -es`) was used as a Vim-compatible oracle for representative
ASCII `yw/ye/yb/y0/y$/yy/yj/yk/ygg/yG` register contents and cursor positions.
No Vim code is imported. This viewer deliberately uses physical terminal rows
for vertical/line motions and st's existing snapshot representation; it has no
Vim buffer text objects, f/t motions, marks, registers, change/delete operators,
macros, or editing. Combining graphemes and unrecorded early wide-wrap padding
retain st's existing limitations. Normal h/l retain cell-wise viewer movement;
operator h/l copy whole wide glyphs. Trailing terminal padding cannot be
distinguished from explicit blanks.

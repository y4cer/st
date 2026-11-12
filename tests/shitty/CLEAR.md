# Full-screen clear policy review

2026-11-12: user requested Ctrl+L to move old output into scrollback. Fish 3.3.1
already strips ED3 from its `clear` command; the lost text was the live viewport.
The new ED2 policy saves populated primary rows before clearing, as exercised by
Shitty's xterm.js `scrollOnEraseInDisplay` source case. Alternate-screen and
partial erases retain their previous behavior. Repeated empty clears do not add
rows. Blank lines between content, colors, wide flags and session ownership are
preserved; unused trailing blanks and synthetic resize padding are omitted.

Six Python cases change: one newly passes, two formerly passed but require no
retained history, and three known failures have updated fingerprints. See
README.md's ED2 paragraph for their precise source assertions and limitations.
All failures remain real assertions; no source assertions were edited.

Twelve Alacritty recordings also change their full-history row counts. Ten
previously passed; `alt_reset` and `selective_erasure` already had unsupported
foreground-reset/selective-erase differences. Each recording was inspected for
ED2 (including unsupported private ?2J in selective_erasure). All twelve reports
agree between ordinary and sanitizer builds. Their full-history assertions
remain enabled, with the reviewed diagnostics below.

For review, a separate diagnostic replay compared **only the final viewport**
using the exact same character, width/wrap, rendition and color comparisons.
All ten formerly passing viewports still match their source golden cells. The
two previously failing viewports retain exactly their old diagnostics:
`foreground index 33,0: got '1'; expected '-2'` and
`char 0,0: got ' '; expected 'A'`. This diagnostic does not turn a full-history
failure into a passing compatibility claim. The standard runner still stops on
the history-length assertion; later comparisons are not counted as covered by
those failing cases. The standalone diagnostic used for this review is
`/tmp/st-clear-corpus-review.py` (a local artifact, not a dependency).

## Reviewed corpus diagnostics

- `alacritty/main/alt_reset`: history + screen row count: got '34'; expected '30'
- `alacritty/main/clear_underline`: history + screen row count: got '35'; expected '32'
- `alacritty/main/colored_reset`: history + screen row count: got '65'; expected '63'
- `alacritty/main/newline_with_cursor_beyond_scroll_region`: history + screen row count: got '30'; expected '29'
- `alacritty/main/origin_goto`: history + screen row count: got '38'; expected '37'
- `alacritty/main/selective_erasure`: history + screen row count: got '4'; expected '3'
- `alacritty/main/vttest_cursor_movement_1`: history + screen row count: got '51'; expected '29'
- `alacritty/main/vttest_insert`: history + screen row count: got '51'; expected '29'
- `alacritty/main/vttest_origin_mode_1`: history + screen row count: got '292'; expected '29'
- `alacritty/main/vttest_origin_mode_2`: history + screen row count: got '242'; expected '29'
- `alacritty/main/vttest_scroll`: history + screen row count: got '194'; expected '29'
- `alacritty/main/vttest_tab_clear_set`: history + screen row count: got '61'; expected '31'

## Validation

Five native clear cases, background-session isolation, real X11 pixel recovery
after ED2/PageUp, and actual fish Ctrl+L with an unsubmitted command were checked.
The fish test explicitly initializes fish_key_bindings and loads the stock
function, because --no-config omits the configuration variable handler.
This is a self-review; the independent review in REVIEW.md predates this change.

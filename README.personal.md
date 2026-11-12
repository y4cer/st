# Personal st

Upstream: https://git.suckless.org/st (remote `upstream`).

Build and install without root:

```sh
make
make PREFIX="$HOME/.local" install
```

Installation also adds the `st` application launcher with the official suckless
logo. Open `st` from Ubuntu's application search, then right-click its dock icon
and choose **Add to Favorites**. To install just the launcher and icon, run
`make PREFIX="$HOME/.local" install-desktop`. The launcher matches existing
default `st-256color` window classes without changing terminal identification.

## Tabs

- **Ctrl+Shift+T**: open a tab; **Ctrl+Shift+W**: close the active tab.
- **Ctrl+Tab / Ctrl+Shift+Tab**: next/previous tab, wrapping at the ends.
- **Alt+1…9**: select an existing tab by number.
- Click the tab bar to select a tab; scroll over it to cycle tabs.

The bar is hidden with one tab. With multiple tabs it has padded, separated
blocks and a bright active tab with dark text and an underline. Its opaque
colors (`tabcolorname` in config.h) are independent of application palettes.
A `*` marks background output. Each tab owns
its shell/PTY, screen, history, selection, copy mode, title, terminal modes and
palette. Background processes continue running and receive their own terminal
replies. Exiting a shell closes its tab; closing the last tab closes the window.
Closing a tab sends SIGHUP to its shell process group.

Switching tabs preserves copy mode and history position. Resizing the terminal,
including showing/hiding the bar, exits copy mode as before. All PTYs receive
the current viewport size. An ongoing paste remains attached to its original
tab; closing that tab discards the rest of the paste.

New tabs use the original launch directory and command (`-e`, if supplied),
otherwise the configured shell. They do not inherit the active shell's current
directory. Opening another tab is disabled with `-l` (an attached device).
Alt-number and cycling shortcuts are passed through when there is no eligible
target. Tab actions remain available in copy mode and with application keyboard
lock enabled.

## Clear screen without losing output

`Ctrl+L` in fish moves the prompt to the top while keeping the previous screen
in scrollback. Use the mouse wheel or Shift+PageUp to see it. Pending command
text remains in the shell's editing buffer.

This applies to full-screen erase (`CSI 2 J`) on the normal screen, including
`clear`: populated rows move into history before the screen is blanked. Repeated
clears of an empty screen add nothing. Partial erases and the alternate screen
used by fullscreen applications retain their normal erase behavior. The history
limit remains 2000 lines.

## Vertical resizing

When the normal screen's cursor is on its last row, increasing the window height
keeps that row at the bottom and reveals older history above it. If history is
too short, the remaining space appears above the output. A short greeting/prompt
near the top stays in place. Alternate-screen applications keep their own layout.

Shrinking saves the rows displaced above the cursor into scrollback; growing
restores them without duplicating history. Empty padding introduced by resizing
does not become shell history. Width resizing still uses st's existing behavior
without line reflow.

## Read-only copy mode

Enter with **Ctrl+Shift+Space**. This takes an immutable snapshot of the
populated scrollback and visible screen. The child process keeps running,
but keyboard input, mouse reports and clipboard pastes are not forwarded
while copy mode is active. The bottom row displays `COPY [RO]`.

- `h/j/k/l`, arrows: move; a numeric prefix repeats movement.
- `w/b/e`: word motions; `0/$`: start/end of line.
- `gg/G`: oldest/newest line; `H/M/L`: top/middle/bottom of viewport.
- Ctrl+u/d: half-page up/down; Ctrl+b/f or PageUp/PageDown: full page.
- `v`: character selection; `V`: line selection.
- `y`: copy selection to PRIMARY and CLIPBOARD, staying in copy mode.
  Without a selection, copy the current line.
- `/` or `?`: enter forward/backward search; Enter runs it, `n/N` repeat.
- Escape: cancel search/selection, or leave copy mode.
- `q`, `i`, Ctrl+c, Ctrl+Shift+Space: leave copy mode.
- Mouse wheel: move three lines.

Normal-mode commands use physical QWERTY keys and work with the Russian
layout too. Search text uses the active layout. Resizing the terminal exits
copy mode. In an alternate-screen application, only its current screen is
captured, not the normal shell's history. The history limit is currently
2000 lines. This is a Vim-style viewer, not a complete Vim implementation.

Ctrl+c outside copy mode remains the normal interrupt key.

## Other customizations

- Alpha transparency: 90% opacity, or override with `st -A 0.8`.
- Adwaita Mono 11, with the system monospace font as fallback; Ctrl+plus/equal and Ctrl+minus zoom, Ctrl+0 resets.
- Scrollback via mouse wheel or Shift+PageUp/PageDown.
- Customized Gruvbox Material Dark Hard palette.
- Distinct Ctrl+Enter sequence for Pi (`CSI 13;5u`).

Keep `config.h` and `config.def.h` synchronized when changing settings.

## Regression tests and review

```sh
make test
make test-sanitize
make test-x11
```

All C targets use `-Wall -Werror -Wpedantic`. Shitty is the reference for future
changes; the full portable reference inventory runs in both targets with explicit
known differences and exclusions (see `tests/shitty/README.md`).

The suite runs headlessly, including selected MIT-licensed cases adapted from
`pg83/shitty`, copy-mode/history regressions, and simulated X11 INCR paste tests.
See `tests/README.md` for coverage, provenance and limitations. Independent
review reports and their resolution are in `reviews/`. `make test-x11` additionally
runs an isolated Xvfb window with real PTYs and keyboard/pointer events; it needs
Xvfb, libXtst and Pillow. GitHub Actions runs the build and all three test targets.

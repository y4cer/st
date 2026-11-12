# Personal st

Upstream: https://git.suckless.org/st (remote `upstream`).

Build and install without root:

```sh
make
make PREFIX="$HOME/.local" install
```

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
```

The suite runs headlessly, including selected MIT-licensed cases adapted from
`pg83/shitty`, copy-mode/history regressions, and simulated X11 INCR paste tests.
See `tests/README.md` for coverage, provenance and limitations. Independent
review reports and their resolution are in `reviews/`. GitHub Actions runs the
build and both test targets on pushes and pull requests.

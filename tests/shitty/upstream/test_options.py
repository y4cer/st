# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import os
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness import SHITTY, Shitty, run_startup_failure


class OptionTest(unittest.TestCase):
    def test_missing_locale_environment_is_forced_to_utf8(self):
        # A launchd/Automator start ships no locale at all (issue 63);
        # the terminal must land in a UTF-8 character type on its own,
        # without complaining.
        result = run_startup_failure(
            extra_arguments=("-version",),
            extra_environment={"LANG": "", "LC_ALL": "", "LC_CTYPE": ""},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        self.assertNotIn(b"Warning", result.stdout)

    def test_invalid_option_values_fail_loudly(self):
        cases = (
            (("-unicodeWidths", "x"), b"expected a Unicode major version"),
            (("-osc52Select", "nope"), b"expected primary or clipboard"),
            (("-fontsize",), b"missing value"),
            (("+fontsize", "12"), b"'+' is invalid here"),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                result = run_startup_failure(extra_arguments=arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout + result.stderr)

    def test_malformed_test_fd_fails_loudly(self):
        environment = os.environ.copy()
        environment["XDG_CONFIG_HOME"] = "/nonexistent"
        for arguments, message in (
            (("--test-fd",), b"--test-fd requires a descriptor"),
            (("--test-fd", "abc"), b"invalid --test-fd descriptor"),
            (("--test-fd", "-5"), b"invalid --test-fd descriptor"),
        ):
            with self.subTest(arguments=arguments):
                completed = subprocess.run(
                    [str(SHITTY), *arguments],
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                    check=False,
                )
                self.assertEqual(completed.returncode, 1)
                self.assertIn(message, completed.stderr)

    def test_shell_names_resolve_through_path_and_shell_env(self):
        with tempfile.TemporaryDirectory() as tools:
            tool = Path(tools) / "shitty-probe-shell"
            tool.write_text("#!/bin/sh\n")
            tool.chmod(0o755)
            environment = {"PATH": f"{tools}:{os.environ.get('PATH', '/bin')}"}
            with Shitty(extra_arguments=("-shell", "shitty-probe-shell"), extra_environment=environment) as terminal:
                executable, argv = terminal.launch_command()
                self.assertEqual(executable, os.path.realpath(tool))
                self.assertEqual(argv, ["shitty-probe-shell"])

        # A name nowhere on PATH falls back to $SHELL.
        environment = {"PATH": "/nonexistent", "SHELL": "/bin/sh"}
        with Shitty(extra_arguments=("-shell", "no-such-shell-anywhere"), extra_environment=environment) as terminal:
            executable, argv = terminal.launch_command()
            self.assertEqual(executable, "/bin/sh")

    def test_no_decorations_is_a_boolean_option(self):
        result = run_startup_failure(extra_arguments=("-help",))
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"-no-decorations", result.stdout)

        with Shitty() as terminal:
            self.assertEqual(terminal.options()["no_decorations"], 0)
        with Shitty(extra_arguments=("-no-decorations",)) as terminal:
            self.assertEqual(terminal.options()["no_decorations"], 1)
        with Shitty(
            extra_arguments=("-no-decorations", "+no-decorations")
        ) as terminal:
            self.assertEqual(terminal.options()["no_decorations"], 0)

    def test_maximized_is_a_boolean_startup_option(self):
        result = run_startup_failure(extra_arguments=("-help",))
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"-maximized", result.stdout)

        with Shitty() as terminal:
            self.assertEqual(terminal.options()["maximized"], 0)
        with Shitty(extra_arguments=("-maximized",)) as terminal:
            self.assertEqual(terminal.options()["maximized"], 1)
        with Shitty(
            extra_arguments=("-maximized", "+maximized")
        ) as terminal:
            self.assertEqual(terminal.options()["maximized"], 0)

    def test_fullscreen_is_a_boolean_startup_option(self):
        result = run_startup_failure(extra_arguments=("-help",))
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"-fullscreen", result.stdout)

        with Shitty() as terminal:
            self.assertEqual(terminal.options()["fullscreen"], 0)
        with Shitty(extra_arguments=("-fullscreen",)) as terminal:
            self.assertEqual(terminal.options()["fullscreen"], 1)
        with Shitty(
            extra_arguments=("-fullscreen", "+fullscreen")
        ) as terminal:
            self.assertEqual(terminal.options()["fullscreen"], 0)

    def test_fullscreen_and_maximized_are_independent_options(self):
        # Both may be configured at once; the startup path prefers
        # fullscreen, so the parsed pair must survive intact for it to
        # make that choice.
        with Shitty(
            extra_arguments=("-fullscreen", "-maximized")
        ) as terminal:
            options = terminal.options()
            self.assertEqual(options["fullscreen"], 1)
            self.assertEqual(options["maximized"], 1)

    def test_kitty_ctrl_base_layout_is_listed_in_help(self):
        result = run_startup_failure(extra_arguments=("-help",))
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"-kittyCtrlBaseLayout", result.stdout)

    def test_shell_and_login_argv_are_built_from_selected_executable(self):
        with Shitty(extra_arguments=("-shell", "/bin/sh")) as terminal:
            self.assertEqual(terminal.launch_command(), ("/bin/sh", ["sh"]))

        with Shitty(
            extra_arguments=("-shell", "/bin/sh", "-login")
        ) as terminal:
            self.assertEqual(terminal.launch_command(), ("/bin/sh", ["-sh"]))

        with Shitty(
            extra_arguments=("-shell", "/bin/sh", "/bin/bash")
        ) as terminal:
            self.assertEqual(
                terminal.launch_command(),
                ("/bin/bash", ["bash"]),
            )

        with Shitty(
            extra_arguments=("-login", "-e", "/tmp/tool", "one", "two")
        ) as terminal:
            self.assertEqual(
                terminal.launch_command(),
                ("/tmp/tool", ["/tmp/tool", "one", "two"]),
            )

    def test_dash_e_ends_option_parsing_and_preserves_command_argv(self):
        command = (
            "probe",
            "-fontsize",
            "99",
            "+rv",
            "-unknown",
            "plain argument",
        )
        with Shitty(
            extra_arguments=("-fontsize", "18", "-e", *command)
        ) as terminal:
            self.assertEqual(terminal.options()["fontsize"], 18)
            self.assertEqual(terminal.argv()[1:], ["-e", *command])

    def test_geometry_accepts_valid_grid_and_rejects_invalid_or_overflow(self):
        with Shitty(extra_arguments=("-geometry", "7x3")) as terminal:
            options = terminal.options()
            self.assertEqual((options["columns"], options["rows"]), (7, 3))

        for value in ("0x24", "80x0", "80X24", "70000x24", "80x70000"):
            with self.subTest(value=value):
                result = run_startup_failure(
                    extra_arguments=("-geometry", value)
                )
                self.assertEqual(result.returncode, 255)
                self.assertIn(b"-geometry", result.stdout)

    def test_colors_accept_short_and_full_rgb_and_reverse_swaps_defaults(self):
        with Shitty(
            extra_arguments=(
                "-fg", "#1aF", "-bg", "010203", "-cr", "#abcdef"
            )
        ) as terminal:
            options = terminal.options()
            self.assertEqual(options["fg"], 0x11AAFF)
            self.assertEqual(options["bg"], 0x010203)
            self.assertEqual(options["cr"], 0xABCDEF)

        with Shitty(
            extra_arguments=("-fg", "#123", "-bg", "#456", "-rv")
        ) as terminal:
            options = terminal.options()
            self.assertEqual(options["fg"], 0x445566)
            self.assertEqual(options["bg"], 0x112233)
            self.assertEqual(options["cr"], options["fg"])

        for value in ("#12", "#1234", "#ggg", "#1234567"):
            with self.subTest(value=value):
                result = run_startup_failure(extra_arguments=("-fg", value))
                self.assertEqual(result.returncode, 255)
                self.assertIn(b"-fg", result.stdout)

    def test_boolean_minus_plus_and_advanced_values(self):
        with Shitty(
            extra_arguments=(
                "-altScroll", "-boldColors", "-autoCopy",
                "-allowOsc52Read", "true",
                "-allowWindowOps", "true",
            )
        ) as terminal:
            options = terminal.options()
            self.assertEqual(options["alt_scroll"], 1)
            self.assertEqual(options["bold_colors"], 1)
            self.assertEqual(options["auto_copy"], 1)
            self.assertEqual(options["allow_osc52_read"], 1)
            self.assertEqual(options["allow_window_ops"], 1)

        with Shitty() as terminal:
            # Bold must not repaint a themed palette by default (issue 59).
            self.assertEqual(terminal.options()["bold_colors"], 0)

        result = run_startup_failure(
            extra_arguments=("-allowOsc52Read", "yes")
        )
        self.assertEqual(result.returncode, 255)
        self.assertIn(b"expected true or false", result.stdout)

    def test_unique_abbreviations_work_and_ambiguous_ones_fail(self):
        with Shitty(
            extra_arguments=("-fontsi", "19", "-geom", "7x3", "-altS")
        ) as terminal:
            options = terminal.options()
            self.assertEqual(options["fontsize"], 19)
            self.assertEqual((options["columns"], options["rows"]), (7, 3))
            self.assertEqual(options["alt_scroll"], 1)

        for abbreviation in ("-a", "-b", "-f"):
            with self.subTest(abbreviation=abbreviation):
                result = run_startup_failure(
                    extra_arguments=(abbreviation,)
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn(b"ambiguous option", result.stderr)

    def test_fontpath_option_is_removed(self):
        result = run_startup_failure(
            extra_arguments=("-fontpath", "/tmp/fonts")
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unknown option", result.stderr)

    def test_font_size_accepts_inclusive_one_and_255_boundaries(self):
        for value in (1, 255):
            with self.subTest(source="cli", value=value):
                with Shitty(
                    extra_arguments=("-fontsize", str(value))
                ) as terminal:
                    self.assertEqual(terminal.options()["fontsize"], value)
            with self.subTest(source="env", value=value):
                with Shitty(font_size_env=str(value)) as terminal:
                    self.assertEqual(terminal.options()["fontsize"], value)

    def test_font_size_rejects_values_outside_byte_range(self):
        for value in ("0", "256", "-1"):
            with self.subTest(source="cli", value=value):
                result = run_startup_failure(
                    extra_arguments=("-fontsize", value)
                )
                self.assertEqual(result.returncode, 255)
                self.assertIn(b"expected integer within 1..255", result.stdout)
            with self.subTest(source="env", value=value):
                result = run_startup_failure(font_size_env=value)
                self.assertEqual(result.returncode, 255)
                self.assertIn(b"expected integer within 1..255", result.stdout)

    def test_numeric_options_reject_trailing_garbage(self):
        cases = (
            ("fontsize", ("-fontsize", "16wat")),
            ("border", ("-border", "2px")),
            ("saveLines", ("-saveLines", "500rows")),
            ("geometry", ("-geometry", "80x24junk")),
            ("modifyOtherKeys", ("-modifyOtherKeys", "1foo")),
        )
        for name, arguments in cases:
            with self.subTest(name=name):
                result = run_startup_failure(extra_arguments=arguments)
                self.assertEqual(result.returncode, 255)
                self.assertIn(f"-{name}".encode(), result.stdout)

        result = run_startup_failure(font_size_env="16wat")
        self.assertEqual(result.returncode, 255)
        self.assertIn(b"SHITTY_FONT_SIZE", result.stdout)

    def test_font_size_source_priority_is_cli_then_env_then_default(self):
        with Shitty(font_size_env=None) as terminal:
            self.assertEqual(terminal.options()["fontsize"], 16)

        with Shitty(font_size_env="23") as terminal:
            self.assertEqual(terminal.options()["fontsize"], 23)

        with Shitty(
            font_size_env="23",
            extra_arguments=("-fontsize", "31"),
        ) as terminal:
            self.assertEqual(terminal.options()["fontsize"], 31)


    def test_dump_records_the_raw_pty_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "dump.bin")
            with Shitty(
                columns=10, rows=2, extra_arguments=("-dump", path)
            ) as terminal:
                terminal.write(b"hello\x1b[1mworld")
                self.assertEqual(terminal.snapshot().lines[0], "helloworld")
            with open(path, "rb") as dump:
                self.assertEqual(dump.read(), b"hello\x1b[1mworld")


    def test_verbose_startup_reports_sessions_and_resizes(self):
        with Shitty(extra_arguments=("-verbose",)) as terminal:
            terminal.write(b"x")
            self.assertEqual(terminal.snapshot().lines[0][:1], "x")
            terminal.resize(12, 4)
            self.assertEqual(terminal.snapshot().columns, 12)

    @unittest.skipUnless(platform.libc_ver()[0] == "glibc", "musl silently maps every locale to UTF-8")
    def test_non_utf8_and_unknown_locales_warn(self):
        result = run_startup_failure(
            extra_arguments=("-version",),
            extra_environment={"LC_ALL": "C", "LC_CTYPE": "C", "LANG": "C"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"non-UTF-8 locale", result.stdout + result.stderr)
        result = run_startup_failure(
            extra_arguments=("-version",),
            extra_environment={"LC_ALL": "xx_XX.bogus", "LC_CTYPE": "xx_XX.bogus", "LANG": "xx_XX.bogus"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"locale", result.stdout + result.stderr)

    def test_an_option_without_its_value_fails(self):
        result = run_startup_failure(extra_arguments=("-fontsize",))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"missing value", result.stdout + result.stderr)

    def test_title_fallback_none_keeps_the_brand_title(self):
        with Shitty(extra_arguments=("-titleFallback", "none")) as terminal:
            self.assertIn(terminal.window_title(), ("Shitty", "Pretty"))
            terminal.write(b"\x1b]2;app\x1b\\")
            self.assertEqual(terminal.window_title(), "app")

    def test_symbol_font_ranges_take_hex_bounds_and_refuse_lists(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "symbols.toml"
            config.write_text(
                "[[symbolFont]]\n"
                'font = "One"\n'
                "first = 0xe0b0\n"
                "last = 0xE0BF\n"
                "[[symbolFont]]\n"
                'font = "Two"\n'
                "first = [1]\n"
                "[[symbolFont]]\n"
                'font = "Three"\n'
                "first = 0o777\n"
                "last = 0b1111111111\n"
            )
            result = run_startup_failure(
                extra_arguments=("-config", config, "-version")
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn(
                b"symbolFont values are scalars", result.stdout + result.stderr
            )


if __name__ == "__main__":
    unittest.main()

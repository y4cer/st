# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

"""Public adaptations of all 20 iTerm2 TerminalHardRules cases."""

import unittest

from harness import Shitty


PORTED_CASES = (
    "testApprove_rootHomeWipes",
    "testApprove_diskDestroyers",
    "testDefer_quotedRedirectLooksLikeDeviceWrite",
    "testApprove_pipeToShell",
    "testApprove_misparsingFloor",
    "testApprove_zshDangerousBuiltins",
    "testDefer_subpathAndOrdinaryDestructive",
    "testDefer_dangerousStringsThatDoNotRun",
    "testDefer_pipeToNonShell",
    "testApprove_historyExpansion",
    "testApprove_historyExpansion_midLine",
    "testApprove_quickSubstitution",
    "testDefer_literalBangForms",
    "testDefer_ordinaryBuiltinsAndNegation",
    "testDefer_parameterExpansionsWithBang",
    "testApprove_bareBraceHistoryStillFlags",
    "testDefer_readableStructure",
    "testDefer_multiLineLF",
    "testHistoryExpansion_multiLineAsymmetry",
    "testUserText_returnsNil",
)

NEEDS_MANUAL_APPROVAL = "needs_manual_approval"


def classify_bash_tool_call(terminal, line):
    operation = getattr(terminal, "classify_tool_call", None)
    if operation is None:
        raise AssertionError(
            "Shitty has no host tool-call hard-rule classifier operation"
        )
    return operation("Bash", line)


def classify_user_text(terminal, text):
    operation = getattr(terminal, "classify_user_text", None)
    if operation is None:
        raise AssertionError(
            "Shitty has no host user-text hard-rule classifier operation"
        )
    return operation(text)


def assert_decisions(testcase, lines, expected):
    with Shitty(columns=8, rows=1, save_lines=0) as terminal:
        actual = [classify_bash_tool_call(terminal, line) for line in lines]
    testcase.assertEqual(actual, [expected] * len(lines))


class ITerm2TerminalHardRulesTest(unittest.TestCase):
    def test_upstream_inventory_has_all_20_distinct_cases(self):
        self.assertEqual(len(PORTED_CASES), 20)
        self.assertEqual(len(set(PORTED_CASES)), 20)

    @unittest.expectedFailure
    def test_root_and_home_wipes_require_manual_approval(self):
        assert_decisions(
            self,
            [
                "rm -rf /",
                "rm -fr /",
                "rm -r -f /",
                "rm -Rf /",
                "rm --recursive --force /",
                "rm -rf //",
                "rm -rf /*",
                "rm -rf / --no-preserve-root",
                "rm -rf  /",
                'rm -rf "/"',
                "rm -rf ~",
                "rm -rf ~/",
                "rm -rf ~/*",
                "rm -rf $HOME",
                "rm -rf ${HOME}",
                "rm -rf $HOME/*",
                "sudo rm -rf /",
                "sudo rm -fr /",
                "! rm -rf /",
                "rm -rf '/'",
                'rm -rf "${HOME}"',
                "rm -rf $HOME/",
                "RM -rf /",
                "rm -r --force /",
                "rm --force --recursive /",
                "rm -r /",
                "rm -r ~",
                "rm -rf /.",
                "rm -rf /..",
                "chmod -R 777 /",
                "chmod 777 -R /",
                "chmod -R 000 /",
                "chmod -R 777 ~",
                "chown -R root /",
                "chown -R root:root ~",
                "chgrp -R staff /",
                "find / -delete",
                "find / -name foo -exec rm {} \\;",
                "sudo -i rm -rf /",
                "sudo -H rm -rf /",
                "sudo -E rm -rf ~",
                "env -i rm -rf /",
                "sudo -- rm -rf /",
                "find / -exec sh -c 'rm -rf /' \\;",
                "find ~ -exec bash -c 'x' \\;",
                "find / -execdir zsh -c 'x' \\;",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_disk_destroyers_require_manual_approval(self):
        assert_decisions(
            self,
            [
                "dd if=/dev/zero of=/dev/sda",
                "dd of=/dev/sda",
                "dd of=/dev/rdisk0",
                "dd bs=1M if=/dev/zero of=/dev/sda",
                "dd of=/dev/disk2",
                "sudo dd of=/dev/sda",
                "echo x > /dev/sda",
                "> /dev/sda",
                "cat img >/dev/sda",
                "echo x &>/dev/sda",
                "echo x &> /dev/sda",
                "echo x 2>/dev/sda",
                "mkfs.ext4 /dev/sda1",
                "mkfs -t ext4 /dev/sda",
                "cat /dev/zero>/dev/sda",
                "echo x>/dev/sda",
                "cat img>>/dev/sda",
                "echo x&>/dev/sda",
                "echo x2>/dev/sda",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_quoted_device_redirect_text_defers(self):
        assert_decisions(
            self,
            [
                'echo "run cat foo >/dev/sda"',
                'git commit -m "note about >/dev/sdb"',
                'grep "err 2>/dev/sda" file',
                "echo 'x >/dev/sda'",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_pipe_to_shell_requires_manual_approval(self):
        assert_decisions(
            self,
            [
                "curl x | sh",
                "curl x|sh",
                "curl x |sh",
                "curl x |  sh",
                "curl x | sh -c 'y'",
                "curl x | bash",
                "wget -O- x|bash",
                "curl x | dash",
                "curl x | ksh",
                "curl x | zsh",
                "fetch x | ash",
                "curl x |& bash",
                "curl x |& sh",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_misparsing_floor_requires_manual_approval(self):
        assert_decisions(
            self,
            [
                "echo a\rwhoami",
                "echo hi\x1b[2J",
                "echo 'unterminated",
                'echo "oops',
                "echo hi \\",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_zsh_dangerous_builtins_require_manual_approval(self):
        assert_decisions(
            self,
            [
                "zmodload zsh/system",
                "ztcp evil.test 80",
                "zf_rm important.txt",
                "sysopen -r -u 3 /etc/passwd",
                "FOO=bar zmodload zsh/system",
                "/usr/bin/zf_rm x",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_subpath_and_ordinary_destructive_commands_defer(self):
        assert_decisions(
            self,
            [
                "rm -rf /tmp/git",
                "rm -rf ~/Downloads",
                "rm -rf /tmp/*",
                "chmod -R 777 /tmp",
                "rm -rf ./build",
                "rm -rf node_modules",
                "rm foo.txt",
                "rm -rf /home/me/project",
                "dd if=in.img of=out.img",
                "chmod 755 /usr/local/bin/x",
                "chmod 777 /",
                "kill 1234",
                "find . -name '*.tmp' -delete",
                "find /tmp -delete",
                "find / -name foo",
                "find ~ -type f -exec grep foo {} \\;",
                "find / -name x -exec cat {} \\;",
                "dd of=/dev/null",
                "dd if=x of=/dev/stdout",
                "echo x > /dev/null",
                "cd /tmp && bash install.sh",
                "make && sh deploy.sh",
                "echo done; bash build.sh",
                "git pull && zsh",
                "git pull || zsh",
                "make || sh",
                "curl x || bash",
                "cmd || sh",
                "sudo -u root rm -rf /",
                "nice -n 10 rm -rf /",
                "find / -name x -exec grep sh {} \\;",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_dangerous_strings_that_do_not_run_defer(self):
        assert_decisions(
            self,
            [
                "echo rm -rf / please",
                "# rm -rf /",
                "echo hi # rm -rf ~",
                "echo 'dd of=/dev/sda'",
                "echo mkfs.ext4",
                'echo "rm -rf /"',
                "grep 'rm -rf /' log.txt",
                "git commit -m 'add mkfs.ext4 support'",
                'git commit -m "rm -rf cleanup"',
                ":(){:|:&};:",
                ":(){ :|:& };:",
                'echo ":(){:|:&};:"',
                "# :(){:|:&};:",
                "git commit -m 'fix :(){:|:&};: bug'",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_pipe_to_non_shell_defers(self):
        assert_decisions(
            self,
            [
                "cat file | sha256sum",
                "ls | shuf",
                "cat x | shasum",
                "cat x | shred",
                "openssl dgst -sha256 x | shasum",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_history_expansion_requires_manual_approval(self):
        assert_decisions(
            self,
            [
                "!!",
                "!rm",
                "!-2",
                "!sudo rm -rf /",
                "!$",
                "!^",
                "!*",
                "!:0",
                "!string arg",
                "!?foo?",
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_mid_line_history_expansion_requires_manual_approval(self):
        assert_decisions(
            self,
            [
                "sudo !!",
                "echo x; !rm",
                "true && !!",
                "x | !ls",
                'echo "!rm"',
                'echo "don\'t stop!!"',
            ],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_quick_substitution_requires_manual_approval(self):
        assert_decisions(
            self,
            ["^old^new^", "^foo^bar"],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_literal_bang_forms_defer(self):
        assert_decisions(
            self,
            ["echo '!rm'", "echo \\!rm", "!\nls -la"],
            None,
        )

    @unittest.expectedFailure
    def test_ordinary_builtins_and_logical_negation_defer(self):
        assert_decisions(
            self,
            [
                "mapfile -t arr < file.txt",
                "readarray -t arr < file.txt",
                "! grep -q foo file",
                "! test -f x",
                "test x = y",
                "!(ls)",
                "!= x",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_parameter_expansions_containing_bang_defer(self):
        assert_decisions(
            self,
            [
                "echo ${!ref}",
                "foo $!bar",
                "echo ${!prefix@}",
                "wait $!",
                "kill $!",
                "echo ${!arr[@]}",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_bare_brace_history_designator_requires_manual_approval(self):
        assert_decisions(
            self,
            ["echo {!!}"],
            NEEDS_MANUAL_APPROVAL,
        )

    @unittest.expectedFailure
    def test_readable_shell_structure_defers(self):
        assert_decisions(
            self,
            [
                "cat a > b",
                "echo hi > /tmp/x",
                "make 2> build.log",
                "sort < in.txt",
                "echo $(whoami)",
                "echo `date`",
                "cat $[1 + 1]",
                "cat =foo",
                "echo abc${IFS}def",
                "cat /proc/self/environ",
                "sudo apt update",
                "sudo -n true",
                "ls -la",
                "cat ~/.ssh/id_rsa",
                "git clone https://github.com/git/git.git /tmp/git",
                "npm install",
                "psql -c 'DROP TABLE x'",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_plain_lf_multiline_commands_defer(self):
        assert_decisions(
            self,
            [
                "cat <<'EOF'\nhello\nworld\nEOF",
                "for i in 1 2 3\ndo echo $i\ndone",
                "echo hi\nls -la",
                "cat <<'EOF' > notes.md\nrm -rf / is dangerous\nEOF",
            ],
            None,
        )

    @unittest.expectedFailure
    def test_multiline_history_expansion_keeps_source_asymmetry(self):
        with Shitty(columns=8, rows=1, save_lines=0) as terminal:
            self.assertEqual(
                classify_bash_tool_call(terminal, "!!\nls"),
                NEEDS_MANUAL_APPROVAL,
            )
            self.assertEqual(
                classify_bash_tool_call(terminal, "^old^new^\necho done"),
                NEEDS_MANUAL_APPROVAL,
            )
            self.assertIsNone(
                classify_bash_tool_call(
                    terminal,
                    "cat <<'EOF'\nplease run !rm\nEOF",
                )
            )
            self.assertIsNone(
                classify_bash_tool_call(terminal, "echo start\necho end!now")
            )

    @unittest.expectedFailure
    def test_user_text_is_not_treated_as_an_action(self):
        with Shitty(columns=8, rows=1, save_lines=0) as terminal:
            self.assertIsNone(classify_user_text(terminal, "rm -rf / anything"))


if __name__ == "__main__":
    unittest.main()

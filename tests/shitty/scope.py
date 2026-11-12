"""Explicit capability boundaries. No rule depends on whether a test passes."""
import ast
from pathlib import Path

API_EXCLUSIONS = {}
def group(reason, names):
    API_EXCLUSIONS.update({name:reason for name in names.split()})

group('Shitty parser callback/trace instrumentation has no st API; parser state/output tests run separately',
      'parser_trace_on parser_trace parser_trace_clear parser_diagnostics')
group('st has no OSC 8 hyperlink or URI opening subsystem',
      'hyperlink hyperlink_count hyperlink_bytes osc7_cwd drop drop_path')
group('st has no shell semantic annotations / prompt metadata',
      'row_semantic semantic_click cursor_at_prompt classify_tool_call classify_user_text attach_annotation save_annotation_state reset_preserving_prompt current_cwd')
group('st has no Kitty keyboard protocol', 'kitty_key kitty_special protocol_state')
group('st has no multiple sessions, tabs or embedded multiplexer',
      'new_session close_session session_state write_to read_input_of chord_prev_tab chord_next_tab chord_close_tab chord_clear tmux_control_events')
group('Shitty desktop actions/notifications have no st equivalent', 'read_actions desktop_state')
group('st uses libc wcwidth, without Shitty Unicode table/version APIs', 'measure_widths grapheme_breaks utf8_push utf8_reset')
group('st has no DEC locator/highlight tracking protocol', 'locator_position locator_button highlight_release')
group('Shitty test-only PTY scheduling/fault-injection API; st byte-stream tests run through twrite/ttywrite',
      'script_pty_reads script_pty_writes script_pty_repeat read_pty read_written_pty read_child_output wait_read_pty wait_child spawn service_pty pending_scripted_pty_read_bytes flush_output_result pump')
group('Shitty renderer/layout lifecycle API; st uses X11/Xft',
      'reference_image presented_pixel present repaint render_image render_state load_font blink_tick last_update record_frame fail_next_present resize_pixels winsize winsize_full rectangle_origin font_state preedit shape_generation frontend_content_scale selection_autoscroll_tick pointer_presence window_info')
group('st has no synchronized-output timeout protocol', 'sync_timeout')
group('Shitty direct buffer search API differs from st copy-mode search (covered by native copy_* tests)', 'find_text')
group('Shitty conformance metadata API has no st equivalent', 'conformance_state')
group('Shitty platform control-character helper, not a terminal operation; real X11 kpress tests cover st input', 'control_character')
group('external clipboard ownership setup is platform-specific; st INCR/paste tests cover its X11 transport', 'set_system_clipboard set_primary_selection get_selection paste_clipboard')

FIELDS = {
    'grapheme':'st has no grapheme-cluster storage',
    'hyperlink':'st has no OSC 8 hyperlink storage',
    'semantic':'st has no shell semantic cell metadata',
    'protected':'st has no ISO/DEC protected cells or selective erase',
    'line_attribute':'st has no double-height/width row attributes',
    'drawn':'st does not distinguish written spaces from erased cells',
    'overline':'st does not implement SGR overline',
    'underline_color':'st does not implement independent underline colors',
    'underline_index':'st does not implement independent underline colors',
    'refresh_count':'Shitty renderer refresh scheduling is not the st X11 event loop',
}

def case_reasons(path):
    """Follow helpers within this module so a shared helper is not overlooked."""
    tree=ast.parse(Path(path).read_text())
    functions={node.name:node for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
    result={}
    def inspect(node,seen):
        reasons=set()
        for n in ast.walk(node):
            if isinstance(n,ast.Constant) and isinstance(n.value,(str,bytes)):
                value=n.value.encode() if isinstance(n.value,str) else n.value
                for pattern,feature in PROTOCOLS:
                    if re.search(pattern,value):reasons.add('st does not implement '+feature)
            if isinstance(n,ast.Attribute) and n.attr in FIELDS:reasons.add(FIELDS[n.attr])
            if isinstance(n,ast.Call):
                name=n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else ''
                if name in API_EXCLUSIONS:reasons.add(API_EXCLUSIONS[name])
                if name in functions and name not in seen:
                    reasons.update(inspect(functions[name],seen|{name}))
        return reasons
    for cls in tree.body:
        if not isinstance(cls,ast.ClassDef):continue
        for fn in cls.body:
            if not isinstance(fn,ast.FunctionDef) or not fn.name.startswith('test_'):continue
            id=f'{Path(path).stem}.{cls.name}.{fn.name}'
            if 'inventory' in fn.name:result[id]=['upstream inventory bookkeeping, not a terminal behavior test']
            else:
                reasons=inspect(fn,{fn.name})
                if reasons:result[id]=sorted(reasons)
    return result

# Protocol extensions absent from this st fork. Match explicit sequences in
# the case/helper source, not arbitrary unknown/malformed escape sequences.
import re
PROTOCOLS = [
    (rb'\x1b\[[?0-9;]*\$p', 'DECRQM mode reports'),
    (rb'\x1bP\$q', 'DECRQSS setting reports'),
    (rb'\x1b\][0-9]*105;', 'OSC 105 special-color reset'),
    (rb'\x1b\[>q', 'Shitty version-identification query'),
    (rb'\x1bP[12]\$[tu]', 'DECTABSR tab-stop save/restore'),
    (rb'\x1bP\+q', 'XTGETTCAP capability queries'),
    (rb'\x1b\[!p', 'DECSTR soft reset'),
    (rb'\x1b\[\?69[hl]', 'DECLRMM horizontal margins'),
    (rb'\x1b\[[><=][0-9;:]*u', 'Kitty keyboard negotiation'),
    (rb'\x1b\[>4[;m]', 'modifyOtherKeys extended keyboard protocol'),
    (rb'\x1b\[[0-9;:]*:[0-9;:]*m', 'colon SGR subparameters'),
    (rb'\x1b\[[0-9;]*\$[vxz{rt]', 'DEC rectangle editing/checksum operations'),
    (rb'\x1b\][78];', 'OSC 7/8 cwd/hyperlinks'),
    (rb'\x1b\](?:9|99|133|1337|5522);', 'notification/shell/Kitty/iTerm extensions'),
    (rb'\x1b\[[0-9;]*[SP]#', 'SGR attribute stack'),
]

# Copyright (C) 2026 Shitty team
# MIT licensed
# See the file LICENSE.MIT for the full license.

import unittest

from harness import Shitty


UPSTREAM_CASES = (
    "writeText.bulk.A.1",
    "writeText.bulk.A.2",
    "writeText.bulk.A.3",
    "writeText.autowrap.threeIdenticalFullLines",
    "writeText.bulk.B",
    "writeText.bulk.C",
    "writeText.bulk.D",
    "writeText.bulk.E",
    "writeText.bulk.F",
    "writeText.bulk.G",
    "writeText.bulk.H",
    "AppendChar",
)

UNICODE_UPSTREAM_CASES = (
    "AppendChar_CR_LF",
    "AppendChar.emoji_exclamationmark",
    "AppendChar.VS15_selects_text_presentation_without_changing_the_width",
    "AppendChar.VS15_is_inert_without_a_defined_variation_sequence",
    "AppendChar.a_zero_width_codepoint_after_an_ASCII_base_joins_its_cell",
    "AppendChar.a_wide_char_at_the_second_to_last_column_claims_the_last_one",
    "AppendChar.overwriting_a_wide_char_at_the_second_to_last_column_clears_its_tail",
    "AppendChar.a_wide_char_still_wraps_when_only_one_column_is_left",
    "AppendChar.emoji_VS16_copyright_sign",
    "AppendChar.width_revision_is_gated_on_mode_2027",
    "AppendChar.width_revision_resumes_when_2027_is_set_again",
    "AppendChar.width_revision_at_right_edge_keeps_cursor_on_page",
    "AppendChar.abandoned_width_revision_restores_the_head_cell",
    "Screen.copyArea_does_not_remeasure_cluster_widths",
    "AppendChar.emoji_VS16_i",
    "AppendChar.emoji_family",
    "AppendChar.emoji_zwj_1",
    "AppendChar.emoji_zwj_ten_codepoints",
    "AppendChar.emoji_1",
    "AppendChar_WideChar",
    "AppendChar_Into_WideChar_Right_Half",
    "AppendChar_AutoWrap",
    "AppendChar_AutoWrap_LF",
)

VIEWPORT_ERASE_UPSTREAM_CASES = (
    "Screen.isLineVisible",
    "Backspace",
    "Linefeed",
    "DSR.Unsolicited_ColorPaletteUpdated",
    "ClearToEndOfScreen",
    "ClearToBeginOfScreen",
    "ClearScreen",
    "ClearToEndOfLine",
    "ClearToBeginOfLine",
    "ClearLine",
    "DECFI",
    "InsertColumns",
)

EDITING_PROTECTION_UPSTREAM_CASES = (
    "InsertCharacters.NoMargins",
    "InsertCharacters.Margins",
    "InsertMode",
    "InsertLines",
    "DECSCA: enable and disable character protection",
    "DECSCA: default parameter disables protection",
    "DECSCA: protection is independent of SGR rendition",
    "DECSCA: save and restore cursor preserves protection state",
    "DECSEL-0",
    "DECSEL-1",
    "DECSEL-2",
    "DECSED-0",
)

ISO_PROTECTION_UPSTREAM_CASES = (
    "DECSED-1",
    "DECSED-2",
    "DECSED-2: lines without protected characters are erased correctly",
    "SPA/EPA: ED respects ISO protection",
    "SPA/EPA: EL respects ISO protection",
    "SPA/EPA: ECH respects ISO protection",
    "SPA/EPA: 8-bit C1 forms behave like ESC V / ESC W",
    "SPA/EPA: 8-bit C1 protection survives inside a coalesced text run",
    "DECSCA: regular ED does not respect DEC protection",
    "SPA/EPA: soft reset clears ISO protection mode",
    "SPA/EPA: selective erases do NOT respect ISO protection",
    "DECSCA: selective erase still respects DEC protection after the ISO split",
)

VT52_RECTANGLE_UPSTREAM_CASES = (
    "VT52: enter, cursor movement, and leave",
    "VT52: identify responds with ESC / Z",
    "VT52: erase to end of line and screen",
    "DECSERA-all-defaults",
    "DECSERA",
    "DeleteLines",
    "DECFRA",
    "DECFRA.Vertical",
    "DECFRA.Horizontal",
    "DECFRA.Invalid",
    "DECFRA.Default",
    "DECFRA.Full",
)

EDIT_SCROLL_CURSOR_UPSTREAM_CASES = (
    "DeleteColumns",
    "DeleteCharacters",
    "ClearScrollbackBuffer",
    "EraseCharacters",
    "ScrollUp.WithMargins",
    "ScrollUp",
    "ScrollDown",
    "Unscroll",
    "Sequence.CUU",
    "MoveCursorDown",
    "MoveCursorForward",
    "MoveCursorBackward",
)

POSITION_MARGIN_UPSTREAM_CASES = (
    "HorizontalPositionAbsolute",
    "HorizontalPositionRelative",
    "MoveCursorToColumn",
    "MoveCursorToLine",
    "MoveCursorToBeginOfLine",
    "CarriageReturn_honours_left_margin",
    "NEL_indexes_and_returns_to_margin",
    "SD_respects_left_right_margin",
    "IL_over_region_clears_the_band",
    "Autowrap_within_left_right_margin",
    "DECBI_back_index",
    "CNL_CPL_clamp_to_scroll_region_and_left_margin",
)

CURSOR_MODE_UPSTREAM_CASES = (
    "MoveCursorTo",
    "MoveCursorToNextTab",
    "SaveCursor and RestoreCursor",
    "SaveRestoreCursor.AltVsMain",
    "AlternateScreen.DECSET_47_1047_1049",
    "DCH.worksOutsideTopBottomMargin",
    "ED.2_ignoresScrollRegion",
    "CBT.ignoresLeftRightMargin",
    "CBT.ignoresLeftRightMarginUnderOriginMode",
    "LNM.VT_and_FF_honor_linefeed_mode",
    "DECSCL.conformance_level_gating",
    "DECSTR.resets_left_right_margin_mode",
)

SCROLL_QUERY_UPSTREAM_CASES = (
    "DECRQCRA.honors_origin_mode",
    "Index_outside_margin",
    "Index_inside_margin",
    "Index_at_bottom_margin",
    "VerticalScroll_confined_to_left_right_margins",
    "ReverseIndex_without_custom_margins",
    "ReverseIndex_with_vertical_margin",
    "ReverseIndex_with_vertical_and_horizontal_margin",
    "ScreenAlignmentPattern",
    "CursorNextLine",
    "CursorPreviousLine",
    "DECRQSS reports the scroll-region margins",
)

STATUS_MODE_UPSTREAM_CASES = (
    "DECRQSS reports the current SGR",
    "DECRQSS reports the attribute change extent (DECSACE)",
    "DECRQSS reports the VT525 keyboard settings",
    "Eight-bit C1 controls on input",
    "S8C1T selects 8-bit C1 control transmission for replies",
    "DECID identifies the terminal like DA1",
    "ReportCursorPosition",
    "ReportExtendedCursorPosition",
    "InBandWindowResize",
    "RequestMode",
    "DECNKM",
    "DECARM",
)

HISTORY_TAB_SEARCH_UPSTREAM_CASES = (
    "DECBKM",
    "peek into history",
    "captureBuffer",
    "render into history",
    "HorizontalTabClear.AllTabs",
    "HorizontalTabClear.UnderCursor",
    "HorizontalTabSet",
    "CursorBackwardTab.fixedTabWidth",
    "CursorBackwardTab.manualTabs",
    "searchReverse",
    "search.smartCaseIsCodepointAware",
    "findMarkerDownwards",
)

REPORT_COLOR_RESIZE_UPSTREAM_CASES = (
    "findMarkerUpwards",
    "DECTABSR",
    "save_restore_DEC_modes",
    "OSC.2.Unicode",
    "OSC.4",
    "OSC.10-19",
    "XTGETTCAP",
    "setMaxHistoryLineCount",
    "resize",
    "DECCRA.DownLeft.intersecting",
    "DECCRA.trailing semicolon",
    "DECCRA.Right.intersecting",
)

SIXEL_CHARSET_UPSTREAM_CASES = (
    "DECCRA.Left.intersecting",
    "Screen.tcap.string",
    "Sixel.simple",
    "Sixel.AutoScroll-1",
    "Sixel.status_line",
    "DECSTR",
    "DECTST",
    "SGRSAVE and SGRRESTORE",
    "LS1 and LS0",
    "LS2 and LS3 (locking shift into GL)",
    "LS1R LS2R LS3R (locking shift into GR)",
    "SCS 96-charset designation (ESC - / . / / )",
)

UPSS_TAB_UPSTREAM_CASES = (
    "DECRQUPSS reports DEC Supplemental Graphic before any DECAUPSS",
    "DECAUPSS round-trips every set in the table",
    "DECAUPSS Ps names the set's size, not a free parameter",
    "DECAUPSS treats an omitted Ps as zero",
    "DECAUPSS ignores a designator that names no set",
    "DECAUPSS gates a set on the conformance level DEC introduced it at",
    "UPSS survives a screen switch and a cursor save/restore",
    "UPSS returns to its configured value on both kinds of reset",
    "SCS designator '<' designates the User-Preferred Supplemental Set",
    "HorizontalTab.FillsCellsWithSpaces",
    "HorizontalTab.AfterBulkText",
    "HorizontalTab.MultipleTabs",
)

DECCIR_UPSTREAM_CASES = (
    "HorizontalTab.AtChunkBoundary", "HorizontalTab.AfterScreenClear",
    "DECCIR.default_state", "DECCIR.cursor_position", "DECCIR.bold_and_underline",
    "DECCIR.blinking_and_inverse", "DECCIR.all_rendition_attributes",
    "DECCIR.character_protection", "DECCIR.origin_mode", "DECCIR.wrap_pending",
    "DECCIR.charset_designation_special", "DECCIR.charset_designation_g1",
)

MULTIPAGE_UPSTREAM_CASES = (
    "MultiPage.NP_PP_navigation", "MultiPage.NP_PP_clamping",
    "MultiPage.NP_PP_never_reach_alternate", "MultiPage.PPA_PPR_PPB_navigation",
    "MultiPage.DECPCCM_coupling", "MultiPage.DECRQDE_response",
    "MultiPage.DECXCPR_page_number", "MultiPage.DECCIR_page_number",
)

DECSCL_UPSTREAM_CASES = (
    "DECSCL: DA1 always reports max level 65",
    "DECSCL: level 62 reveals required-at-5 extensions as optional",
    "DECSCL: level 63 hides StatusDisplay (required at 3+)",
    "DECSCL: level 64 hides RectangularEditing (required at 4+)",
    "DECSCL: set level 65 round-trip",
    "DECSCL: implies soft reset",
    "DECSCL: C1 mode 7-bit",
    "DECSCL: C1 mode 8-bit",
    "DECSCL: C1 mode 8-bit with Ps2=2",
    "DECSCL: level 61 forces 7-bit C1",
    "DECSCL: DECRQSS reports current level",
)

C1_RESET_UPSTREAM_CASES = (
    "foldC1ControlsToEightBit",
    "S8C1T: DECRQSS reply uses 8-bit C1 at VT level >= 2",
    "S8C1T: replies revert to 7-bit after a VT52 round-trip",
    "DECSCL resets the terminal (esctest DECSCL_RISOnChange)",
    "DECRQCRA answers regardless of the operating level",
)

TITLE_MODE_UPSTREAM_CASES = (
    "XTSMTITLE: hex/UTF-8 title set and query modes",
)

MORE_FIX_UPSTREAM_CASES = (
    "DECSET 41 (MoreFix): a tab honours a pending wrap",
)

OSC52_UPSTREAM_CASES = (
    "OSC 52: clipboard write and gated read",
)

DYNAMIC_COLOR_RESET_UPSTREAM_CASES = (
    "OSC 110/111 reset dynamic colors to the default palette",
)

TEXT_MACRO_UPSTREAM_CASES = (
    "DECDMAC: define and invoke simple text macro",
    "DECDMAC: define macro with VT sequences",
    "DECDMAC: hex-encoded macro (Pen=1)",
    "DECDMAC: delete all macros (Pdt=1)",
    "DECDMAC: overwrite existing macro",
    "DECDMAC: max 64 macros",
    "DECINVM: invoke undefined macro",
    "DECINVM: nested macro invocation",
    "DECINVM: recursive macro guard",
    "DECDMAC: empty macro body",
    "DECDMAC: ext 32 implied at level 65, listed at level 62",
)

USER_DEFINED_KEY_UPSTREAM_CASES = (
    "DECUDK: program single key",
    "DECUDK: program multiple keys",
    "DECUDK: clear all before loading (Pc=0)",
    "DECUDK: keep existing (Pc=1)",
    "DECUDK: lock keys (Pl=0)",
    "DECUDK: hex decode",
    "DECUDK: soft reset clears UDKs",
    "DECUDK: ext 8 implied at level 65, listed at level 62",
    "DECUDK: udkStringForKey maps Key enum to UDK ID",
)

NATIONAL_REPLACEMENT_UPSTREAM_CASES = (
    "NRCS: British charset substitution",
    "NRCS: German charset substitution",
    "NRCS: French charset substitution",
    "NRCS: switch back to USASCII",
    "NRCS: G1 charset via locking shift",
    "NRCS: DA1 includes ext 9",
    "NRCS: two-byte DRCS designator accepted via SCS fallback",
    "NRCS: single-byte SCS fallback designates British to G2",
)

TECHNICAL_CHARSET_UPSTREAM_CASES = (
    "Technical charset: designate and use",
    "Technical charset: pi mapping",
    "Technical charset: switch back to USASCII",
    "Technical charset: ext 15 implied at level 65, listed at level 62",
)

DEC_LOCATOR_UPSTREAM_CASES = (
    "DECELR: enable locator reporting",
    "DECELR: disable locator reporting",
    "DECELR: one-shot mode (Ps=2)",
    "DECELR: pixel coordinates (Pu=1)",
    "DECSLE: select locator events",
    "DECRQLP: request locator position",
    "DECELR: soft reset disables locator",
    "DEC Locator: DA1 includes ext 29",
)

DRCS_UPSTREAM_CASES = (
    "DECDLD: define single character glyph",
    "DECDLD: erase control clears existing",
    "DECDLD: multiple glyphs separated by semicolons",
    "DECDLD: soft reset clears DRCS",
    "DECDLD: DA1 includes ext 7 (SoftCharacterSet)",
    "DECDLD: cell has image fragment after writing DRCS character",
    "DECDLD: switching away from DRCS uses normal font",
)

DECALN_UPSTREAM_CASES = (
    "DECALN: fills the page with E's",
    "DECALN: page that wraps the history ring is still filled in bounds",
)

VPR_UPSTREAM_CASES = (
    "VPR: moves the cursor down, keeping its column",
)

RECTANGULAR_CHECKSUM_UPSTREAM_CASES = (
    "DECRQCRA: reports the checksum of a rectangular area",
    "XTCHECKSUM: selects how DECRQCRA computes its checksum",
    "XTCHECKSUM: a reset restores the configured extension, not zero",
)

DECSNLS_UPSTREAM_CASES = (
    "DECSNLS: selects the number of lines per screen",
)

LINE_FEED_MARGIN_UPSTREAM_CASES = (
    "LF below the scrolling region stops at the last line of the page",
)

ONE_BASED_PARAMETER_UPSTREAM_CASES = (
    "An omitted one-based parameter takes its default",
    "A zero count moves or edits by one",
)

RECTANGULAR_AREA_UPSTREAM_CASES = (
    "DECCRA with a defaulted source corner",
    "A rectangular area is clamped to the page",
    "A rectangular area is relative to the origin",
)

DECCRA_EDGE_UPSTREAM_CASES = (
    "DECCRA truncates a copy at the page's edge",
)

DECDC_UPSTREAM_CASES = (
    "DECDC deletes a column from every line, including the blank ones",
)

TITLE_UPSTREAM_CASES = (
    "The icon and window titles are set independently",
    "A title is reported with its own OSC",
    "XTPUSHTITLE and XTPOPTITLE share one stack of optional pairs",
)

XTWINOPS_UPSTREAM_CASES = (
    "XTWINOPS reads its operation from the first parameter",
    "DECSLPP sets the page's length",
)

SPECIAL_COLORS_UPSTREAM_CASES = (
    "OSC.5 addresses the special colors",
    "OSC.105 resets the special colors",
)

DEC_DSR_UPSTREAM_CASES = (
    "DECXCPR reports the cursor's position and its page",
    "DECCKSR carries back the id it was asked with",
)

BACKSPACE_WRAP_UPSTREAM_CASES = (
    "Backspace stops at the left margin",
    "Reverse wraparound carries the cursor to the line above",
)

DELTA_UPSTREAM_CASES = (
    "Delta.imagePlacementBumpsExactlyTheCoveredLines",
    "Delta.sizedTextBumpsHeadAndContinuationRows",
    "Delta.decdwlBumpsTheLine",
    "Delta.hyperlinkedTextCarriesItsIdThroughADeltaCycle",
    "a prompt mark on a scrolled-out logical line reaches the change stream",
)

ANSI_MODE_UPSTREAM_CASES = (
    "LNM: set makes LF also return the carriage",
    "LF outside the left/right margins does not scroll",
    "LNM: set makes the Return key send CR LF",
    "KAM: set locks the keyboard out",
    "SRM turns local echo on and off",
)

FINAL_SCREEN_UPSTREAM_CASES = (
    "SRM: echoing input that queries keeps the send buffer intact",
    "SRM: a reply issued from inside the parser is echoed, not deadlocked",
    "RIS restores SRM",
    "A hard reset leaves VT52",
    "DECRQM answers for a mode it knows but can never turn on",
    "DECRQM reports a DEC mode the terminal remembers but cannot act on",
    "DECRQM answers 4 for a DEC mode that can never turn on",
    "VT525 keyboard/national modes are settable toggles",
    "DECREQTPARM: reports the terminal's communication parameters",
    "XTWINOPS reports the window's place on the screen",
    "XTWINOPS resizes to the display when a dimension is zero",
    "DECDSR answers for the devices the terminal does not have",
)


def contour_checkerboard_sixel():
    """Contour's 100x100-pixel black/white checkerboard fixture."""

    def run_length(values):
        result = bytearray()
        start = 0
        while start < len(values):
            end = start + 1
            while end < len(values) and values[end] == values[start]:
                end += 1
            if end - start > 1:
                result.extend(b"!" + str(end - start).encode())
            result.append(0x3F + values[start])
            start = end
        return result

    result = bytearray(
        b"\x1bP0;0;0q\"1;1;100;100"
        b"#0;2;0;0;0#1;2;100;100;100"
    )
    for band in range(17):
        for color in (0, 1):
            values = []
            for column in range(100):
                mask = sum(
                    1 << bit
                    for bit in range(6)
                    if band * 6 + bit < 100
                    and ((column // 10 + (band * 6 + bit) // 10) & 1)
                    == color
                )
                values.append(mask)
            result.extend(b"#" + str(color).encode() + run_length(values))
            result.extend(b"$" if color == 0 else b"-")
    return bytes(result) + b"\x1b\\"


def image_pixel(image, x, y):
    width, _, pixels = image
    offset = (y * width + x) * 3
    return tuple(pixels[offset:offset + 3])


def request_upss(terminal):
    terminal.write(b"\x1b[&u")
    return terminal.read_input()


def assign_upss(terminal, size, designator):
    terminal.write(b"\x1bP" + str(size).encode() + b"!u" + designator + b"\x1b\\")


def deccir(terminal):
    terminal.write(b"\x1b[1$w")
    return terminal.read_input()


class ContourScreenTest(unittest.TestCase):
    def test_upstream_inventory_has_all_12_cases(self):
        self.assertEqual(len(UPSTREAM_CASES), 12)
        self.assertEqual(len(set(UPSTREAM_CASES)), 12)

    def test_unicode_inventory_has_all_23_cases(self):
        self.assertEqual(len(UNICODE_UPSTREAM_CASES), 23)
        self.assertEqual(len(set(UNICODE_UPSTREAM_CASES)), 23)

    def test_cursor_mode_inventory_has_all_12_cases(self):
        self.assertEqual(len(CURSOR_MODE_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(CURSOR_MODE_UPSTREAM_CASES)), 12)

    def test_scroll_query_inventory_has_all_12_cases(self):
        self.assertEqual(len(SCROLL_QUERY_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(SCROLL_QUERY_UPSTREAM_CASES)), 12)

    def test_status_mode_inventory_has_all_12_cases(self):
        self.assertEqual(len(STATUS_MODE_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(STATUS_MODE_UPSTREAM_CASES)), 12)

    def test_decscl_inventory_has_all_11_cases(self):
        self.assertEqual(len(DECSCL_UPSTREAM_CASES), 11)
        self.assertEqual(len(set(DECSCL_UPSTREAM_CASES)), 11)

    def test_c1_reset_inventory_has_all_5_cases(self):
        self.assertEqual(len(C1_RESET_UPSTREAM_CASES), 5)
        self.assertEqual(len(set(C1_RESET_UPSTREAM_CASES)), 5)

    def test_title_mode_inventory_has_the_xterm_case(self):
        self.assertEqual(TITLE_MODE_UPSTREAM_CASES, (
            "XTSMTITLE: hex/UTF-8 title set and query modes",
        ))

    def test_more_fix_inventory_has_the_xterm_case(self):
        self.assertEqual(MORE_FIX_UPSTREAM_CASES, (
            "DECSET 41 (MoreFix): a tab honours a pending wrap",
        ))

    def test_osc52_inventory_has_the_contour_case(self):
        self.assertEqual(OSC52_UPSTREAM_CASES, (
            "OSC 52: clipboard write and gated read",
        ))

    def test_dynamic_color_reset_inventory_has_the_contour_case(self):
        self.assertEqual(DYNAMIC_COLOR_RESET_UPSTREAM_CASES, (
            "OSC 110/111 reset dynamic colors to the default palette",
        ))

    def test_text_macro_inventory_has_all_11_cases(self):
        self.assertEqual(len(TEXT_MACRO_UPSTREAM_CASES), 11)
        self.assertEqual(len(set(TEXT_MACRO_UPSTREAM_CASES)), 11)

    def test_user_defined_key_inventory_has_all_9_cases(self):
        self.assertEqual(len(USER_DEFINED_KEY_UPSTREAM_CASES), 9)
        self.assertEqual(len(set(USER_DEFINED_KEY_UPSTREAM_CASES)), 9)

    def test_national_replacement_inventory_has_all_8_cases(self):
        self.assertEqual(len(NATIONAL_REPLACEMENT_UPSTREAM_CASES), 8)
        self.assertEqual(len(set(NATIONAL_REPLACEMENT_UPSTREAM_CASES)), 8)

    def test_technical_charset_inventory_has_all_4_cases(self):
        self.assertEqual(len(TECHNICAL_CHARSET_UPSTREAM_CASES), 4)
        self.assertEqual(len(set(TECHNICAL_CHARSET_UPSTREAM_CASES)), 4)

    def test_dec_locator_inventory_has_all_8_cases(self):
        self.assertEqual(len(DEC_LOCATOR_UPSTREAM_CASES), 8)
        self.assertEqual(len(set(DEC_LOCATOR_UPSTREAM_CASES)), 8)

    def test_drcs_inventory_has_all_7_cases(self):
        self.assertEqual(len(DRCS_UPSTREAM_CASES), 7)
        self.assertEqual(len(set(DRCS_UPSTREAM_CASES)), 7)

    def test_decaln_inventory_has_all_2_cases(self):
        self.assertEqual(len(DECALN_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(DECALN_UPSTREAM_CASES)), 2)

    def test_vpr_inventory_has_all_1_case(self):
        self.assertEqual(len(VPR_UPSTREAM_CASES), 1)
        self.assertEqual(len(set(VPR_UPSTREAM_CASES)), 1)

    def test_rectangular_checksum_inventory_has_all_3_cases(self):
        self.assertEqual(len(RECTANGULAR_CHECKSUM_UPSTREAM_CASES), 3)
        self.assertEqual(len(set(RECTANGULAR_CHECKSUM_UPSTREAM_CASES)), 3)

    def test_decsnls_inventory_has_all_1_case(self):
        self.assertEqual(DECSNLS_UPSTREAM_CASES, (
            "DECSNLS: selects the number of lines per screen",
        ))

    def test_line_feed_margin_inventory_has_all_1_case(self):
        self.assertEqual(LINE_FEED_MARGIN_UPSTREAM_CASES, (
            "LF below the scrolling region stops at the last line of the page",
        ))

    def test_one_based_parameter_inventory_has_all_2_cases(self):
        self.assertEqual(len(ONE_BASED_PARAMETER_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(ONE_BASED_PARAMETER_UPSTREAM_CASES)), 2)

    def test_rectangular_area_inventory_has_all_3_cases(self):
        self.assertEqual(len(RECTANGULAR_AREA_UPSTREAM_CASES), 3)
        self.assertEqual(len(set(RECTANGULAR_AREA_UPSTREAM_CASES)), 3)

    def test_deccra_edge_inventory_has_all_1_case(self):
        self.assertEqual(DECCRA_EDGE_UPSTREAM_CASES, (
            "DECCRA truncates a copy at the page's edge",
        ))

    def test_decdc_inventory_has_all_1_case(self):
        self.assertEqual(DECDC_UPSTREAM_CASES, (
            "DECDC deletes a column from every line, including the blank ones",
        ))

    def test_title_inventory_has_all_3_cases(self):
        self.assertEqual(len(TITLE_UPSTREAM_CASES), 3)
        self.assertEqual(len(set(TITLE_UPSTREAM_CASES)), 3)

    def test_xtwinops_inventory_has_all_2_cases(self):
        self.assertEqual(len(XTWINOPS_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(XTWINOPS_UPSTREAM_CASES)), 2)

    def test_special_colors_inventory_has_all_2_cases(self):
        self.assertEqual(len(SPECIAL_COLORS_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(SPECIAL_COLORS_UPSTREAM_CASES)), 2)

    def test_dec_dsr_inventory_has_all_2_cases(self):
        self.assertEqual(len(DEC_DSR_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(DEC_DSR_UPSTREAM_CASES)), 2)

    def test_backspace_wrap_inventory_has_all_2_cases(self):
        self.assertEqual(len(BACKSPACE_WRAP_UPSTREAM_CASES), 2)
        self.assertEqual(len(set(BACKSPACE_WRAP_UPSTREAM_CASES)), 2)

    def test_delta_inventory_has_all_5_transferred_cases(self):
        self.assertEqual(len(DELTA_UPSTREAM_CASES), 5)
        self.assertEqual(len(set(DELTA_UPSTREAM_CASES)), 5)

    def test_ansi_mode_inventory_has_first_5_cases(self):
        self.assertEqual(len(ANSI_MODE_UPSTREAM_CASES), 5)
        self.assertEqual(len(set(ANSI_MODE_UPSTREAM_CASES)), 5)

    def test_final_screen_inventory_has_all_12_cases(self):
        self.assertEqual(len(FINAL_SCREEN_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(FINAL_SCREEN_UPSTREAM_CASES)), 12)

    def test_history_tab_search_inventory_has_all_12_cases(self):
        self.assertEqual(len(HISTORY_TAB_SEARCH_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(HISTORY_TAB_SEARCH_UPSTREAM_CASES)), 12)

    def test_report_color_resize_inventory_has_all_12_cases(self):
        self.assertEqual(len(REPORT_COLOR_RESIZE_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(REPORT_COLOR_RESIZE_UPSTREAM_CASES)), 12)

    def test_sixel_charset_inventory_has_all_12_cases(self):
        self.assertEqual(len(SIXEL_CHARSET_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(SIXEL_CHARSET_UPSTREAM_CASES)), 12)

    def test_upss_tab_inventory_has_all_12_cases(self):
        self.assertEqual(len(UPSS_TAB_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(UPSS_TAB_UPSTREAM_CASES)), 12)

    def test_deccir_inventory_has_all_12_cases(self):
        self.assertEqual(len(DECCIR_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(DECCIR_UPSTREAM_CASES)), 12)

    def test_multipage_inventory_has_all_8_cases(self):
        self.assertEqual(len(MULTIPAGE_UPSTREAM_CASES), 8)
        self.assertEqual(len(set(MULTIPAGE_UPSTREAM_CASES)), 8)

    def test_width_revision_at_right_edge_keeps_cursor_on_page(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write_chunks(b"abc", "ℹ".encode(), "️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))
            self.assertTrue(snapshot.cursor_x < snapshot.columns)
            self.assertEqual(snapshot.cell(3, 0).grapheme, (0x2139, 0xFE0F))
            self.assertTrue(snapshot.cell(3, 0).double_width)
            self.assertTrue(snapshot.cell(4, 0).double_width_continuation)
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(b"X")
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(snapshot.cell(0, 1).char, "X")

    def test_right_edge_width_revision_moves_cluster_to_next_line(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write_chunks(b"abcd", "ℹ".encode())
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write("️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))
            self.assertFalse(terminal.cursor_pending_wrap())
            self.assertFalse(snapshot.cell(4, 0).drawn)
            self.assertEqual(snapshot.cell(0, 1).grapheme, (0x2139, 0xFE0F))
            self.assertTrue(snapshot.cell(0, 1).double_width)
            self.assertTrue(snapshot.cell(1, 1).double_width_continuation)

    def test_information_emoji_vs16_promotes_to_two_columns(self):
        with Shitty(columns=5, rows=1) as terminal:
            terminal.write("ℹ".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 1)
            self.assertEqual(snapshot.cell(0, 0).char, "ℹ")
            self.assertFalse(snapshot.cell(0, 0).double_width)

            terminal.write_chunks("️".encode(), b"X")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 3)
            self.assertEqual(snapshot.cell(0, 0).grapheme, (0x2139, 0xFE0F))
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "X")

    def test_family_emoji_is_one_two_column_cluster(self):
        codepoints = (0x1F468, 0x200D, 0x1F468, 0x200D, 0x1F467)
        with Shitty(columns=5, rows=1) as terminal:
            for text in ("👨", "‍", "👨", "‍", "👧"):
                terminal.write(text.encode())
                self.assertEqual(terminal.snapshot().cursor_x, 2)

            terminal.write(b"X")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, codepoints)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 3)

    def test_facepalm_zwj_emoji_is_one_two_column_cluster(self):
        codepoints = (0x1F926, 0x1F3FC, 0x200D, 0x2642, 0xFE0F)
        with Shitty(columns=5, rows=1) as terminal:
            terminal.write(b"\x1b[?7l" + "🤦🏼‍♂️".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, codepoints)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cursor_x, 2)
            self.assertTrue(all(not snapshot.cell(x, 0).drawn for x in range(2, 5)))

    def test_ten_codepoint_zwj_emoji_is_not_truncated(self):
        codepoints = (
            0x1F468,
            0x1F3FB,
            0x200D,
            0x2764,
            0xFE0F,
            0x200D,
            0x1F48B,
            0x200D,
            0x1F468,
            0x1F3FB,
        )
        with Shitty(columns=6, rows=1) as terminal:
            terminal.write(b"\x1b[?7l" + "👨🏻‍❤️‍💋‍👨🏻".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, codepoints)
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cursor_x, 2)
            self.assertTrue(all(not snapshot.cell(x, 0).drawn for x in range(2, 6)))

    def test_single_emoji_then_ascii_uses_last_column(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write("😀".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "😀")
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cursor_x, 2)

            terminal.write(b"B")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(2, 0).char, "B")
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_append_wide_character_advances_two_columns(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write("😀".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

    def test_write_into_wide_character_right_half_clears_the_glyph(self):
        with Shitty(columns=4, rows=2, save_lines=5) as terminal:
            terminal.write("😀B".encode() + b"\x1b[2GX")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines[0], " XB ")
            self.assertEqual(snapshot.cell(1, 0).char, "X")
            self.assertFalse(snapshot.cell(0, 0).drawn)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)

    def test_append_char_autowrap_contour_scenario(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"ABC")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

            terminal.write(b"D")
            self.assertEqual(terminal.snapshot().lines, ["ABC", "D  "])
            terminal.write(b"EF")
            self.assertEqual(terminal.snapshot().lines, ["ABC", "DEF"])
            terminal.write(b"G")
            self.assertEqual(terminal.snapshot().lines, ["DEF", "G  "])

    def test_append_char_autowrap_then_crlf(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"ABC")
            self.assertTrue(terminal.cursor_pending_wrap())
            terminal.write(b"\r\n")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

            terminal.write(b"D")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "D  "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_emoji_exclamation_mark_keeps_background_on_both_cells(self):
        with Shitty(columns=5, rows=1) as terminal:
            terminal.write("\x1b[44m❗M".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "❗")
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "M")
            for column in (0, 1, 2):
                self.assertEqual(snapshot.cell(column, 0).background_index, 4)

    def test_vs15_narrows_watch_by_consensus(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write_chunks("⌚".encode(), "︎".encode(), b"X")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (0x231A, 0xFE0E))
            self.assertFalse(snapshot.cell(0, 0).double_width)
            self.assertFalse(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(1, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 2)

    def test_vs15_is_inert_without_defined_variation_sequence(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write_chunks("😀".encode(), "︎".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (0x1F600, 0xFE0E))
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cursor_x, 2)

    def test_zero_width_codepoint_after_ascii_joins_its_cell(self):
        with Shitty(columns=10, rows=1) as terminal:
            terminal.write("é".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 1)
            self.assertEqual(snapshot.cell(0, 0).grapheme, (ord("e"), 0x0301))
            self.assertFalse(snapshot.cell(0, 0).double_width)

        with Shitty(columns=10, rows=1) as terminal:
            terminal.write("abcdéfgh".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cursor_x, 8)
            self.assertEqual(snapshot.cell(4, 0).grapheme, (ord("e"), 0x0301))
            self.assertEqual(snapshot.cell(5, 0).char, "f")

    def test_wide_char_at_second_to_last_column_claims_last(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"AAAAAAAAAA\x1b[1;9H" + "中".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(8, 0).char, "中")
            self.assertTrue(snapshot.cell(8, 0).double_width)
            self.assertTrue(snapshot.cell(9, 0).double_width_continuation)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_overwriting_wide_char_at_second_to_last_clears_tail(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[1;9H" + "中".encode())
            self.assertTrue(terminal.model_snapshot().cell(9, 0).double_width_continuation)

            terminal.write(b"\x1b[1;9Hx")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(8, 0).char, "x")
            self.assertFalse(snapshot.cell(8, 0).double_width)
            self.assertFalse(snapshot.cell(9, 0).double_width_continuation)

    def test_last_column_pending_wrap_moves_next_character(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[1;10Ha")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(b"b")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 1).char, "b")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_copyright_vs16_promotes_to_two_columns(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write_chunks("©".encode(), "️".encode(), b"X")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.cell(0, 0).grapheme, (0x00A9, 0xFE0F))
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)
            self.assertEqual(snapshot.cell(2, 0).char, "X")
            self.assertEqual(snapshot.cursor_x, 3)

    def test_viewport_erase_inventory_has_all_12_cases(self):
        self.assertEqual(len(VIEWPORT_ERASE_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(VIEWPORT_ERASE_UPSTREAM_CASES)), 12)

    def test_screen_is_line_visible_at_each_view_offset(self):
        with Shitty(columns=2, rows=1, save_lines=5) as terminal:
            terminal.write(b"10203040")
            self.assertEqual(terminal.all_text(), ("10", "20", "30", "40"))
            self.assertEqual(terminal.snapshot().lines, ["40"])

            for offset, expected in ((1, "30"), (2, "20"), (3, "10")):
                terminal.wheel_up()
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.view_offset, offset)
                self.assertEqual(snapshot.lines, [expected])

    def test_backspace_contour_scenario(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"12")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "12 ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

            for expected_x in (1, 0, 0):
                terminal.write(b"\b")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], "12 ")
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (expected_x, 0))

    def test_linefeed_contour_scenario(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"1\r\n2")
            self.assertEqual(terminal.snapshot().lines, ["1 ", "2 "])

            terminal.write(b"\r\n3")
            self.assertEqual(terminal.snapshot().lines, ["2 ", "3 "])

    def test_clear_to_end_of_screen_contour_scenario(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"ABC\r\nDEF\r\nGHI\x1b[2;2H\x1b[J")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "D  ", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_clear_to_begin_of_screen_contour_scenario(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"ABC\r\nDEF\r\nGHI\x1b[2;2H\x1b[1J")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["   ", "  F", "GHI"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_clear_screen_contour_scenario(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"AB\r\nC\x1b[2J")
            self.assertEqual(terminal.snapshot().lines, ["  ", "  "])

    def test_clear_to_end_of_line_contour_scenario(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ABC\x1b[1;2H\x1b[K")
            self.assertEqual(terminal.snapshot().lines, ["A  "])

    def test_clear_to_begin_of_line_contour_scenario(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"\x1b[?7lABC\x1b[1;2H\x1b[1K")
            self.assertEqual(terminal.snapshot().lines, ["  C"])

    def test_clear_line_contour_scenario(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"\x1b[?7lABC\x1b[2K")
            self.assertEqual(terminal.snapshot().lines, ["   "])

    def test_decfi_contour_scenario(self):
        expected = (
            ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            ["12345", "689 0", "ACD E", "FHI J", "KLMNO"],
            ["12345", "69  0", "AD  E", "FI  J", "KLMNO"],
            ["12345", "6   0", "A   E", "F   J", "KLMNO"],
            ["12345", "6   0", "A   E", "F   J", "KLMNO"],
        )
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[?69h\x1b[2;4s\x1b[2;4r"
            )
            for index, lines in enumerate(expected, 1):
                terminal.write(b"\x1b9")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, lines, f"DECFI {index}")
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (min(index, 3), 0),
                )

    def test_insert_columns_contour_scenario(self):
        page = (
            b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
            b"\x1b[?69h\x1b[2;4s\x1b[2;4r"
        )
        for position in (b"\x1b[1;1H", b"\x1b[5;5H"):
            with self.subTest(outside=position), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page + position + b"\x1b[1'}")
                self.assertEqual(
                    terminal.snapshot().lines,
                    ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
                )

        for position, count, expected in (
            (b"\x1b[2;3H", 1, ["12345", "67 80", "AB CE", "FG HJ", "KLMNO"]),
            (b"\x1b[2;3H", 2, ["12345", "67  0", "AB  E", "FG  J", "KLMNO"]),
            (b"\x1b[2;2H", 2, ["12345", "6  70", "A  BE", "F  GJ", "KLMNO"]),
            (b"\x1b[2;3H", 3, ["12345", "67  0", "AB  E", "FG  J", "KLMNO"]),
        ):
            with self.subTest(position=position, count=count), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(page + position + f"\x1b[{count}'}}".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[2;2H\x1b[1'}")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "6 780", "A BCE", "F GHJ", "KLMNO"],
            )
            terminal.write(b"\x1b[1'}")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "6  70", "A  BE", "F  GJ", "KLMNO"],
            )

    def test_editing_protection_inventory_has_all_12_cases(self):
        self.assertEqual(len(EDITING_PROTECTION_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(EDITING_PROTECTION_UPSTREAM_CASES)), 12)

    def test_insert_characters_without_margins(self):
        for position, command, expected in (
            (b"\x1b[2;2H", b"\x1b[@", "4 5"),
            (b"\x1b[2;2H", b"\x1b[1@", "4 5"),
            (b"\x1b[2;2H", b"\x1b[2@", "4  "),
            (b"\x1b[2;2H", b"\x1b[3@", "4  "),
            (b"\x1b[2;1H", b"\x1b[2@", "  4"),
            (b"\x1b[2;1H", b"\x1b[3@", "   "),
            (b"\x1b[2;1H", b"\x1b[4@", "   "),
        ):
            with self.subTest(position=position, command=command), Shitty(
                columns=3,
                rows=2,
            ) as terminal:
                terminal.write(b"123\r\n456" + position + command)
                self.assertEqual(terminal.snapshot().lines, ["123", expected])

    def test_insert_characters_with_margins(self):
        page = b"12345\r\n67890\x1b[?69h\x1b[2;4s"
        for position in (b"\x1b[1;1H", b"\x1b[1;5H"):
            with self.subTest(outside=position), Shitty(columns=5, rows=2) as terminal:
                terminal.write(page + position + b"\x1b[@")
                self.assertEqual(terminal.snapshot().lines, ["12345", "67890"])

        for count, expected in ((1, "12 35"), (2, "12  5"), (3, "12  5")):
            with self.subTest(count=count), Shitty(columns=5, rows=2) as terminal:
                terminal.write(page + b"\x1b[1;3H" + f"\x1b[{count}@".encode())
                self.assertEqual(terminal.snapshot().lines, [expected, "67890"])

    def test_insert_mode(self):
        with Shitty(columns=10, rows=1) as terminal:
            terminal.write(b"ABCDEFGHIJ\x1b[1;4H\x1b[4hXY")
            self.assertEqual(terminal.snapshot().lines, ["ABCXYDEFGH"])

        with Shitty(columns=10, rows=1) as terminal:
            terminal.write(b"ABCDEFGHIJ\x1b[1;4H\x1b[4hX\x1b[4lZ")
            self.assertEqual(terminal.snapshot().lines, ["ABCXZEFGHI"])

        with Shitty(columns=10, rows=1) as terminal:
            terminal.write(b"ABCDEFGHIJ\x1b[1;10H\x1b[4hX")
            self.assertEqual(terminal.snapshot().lines, ["ABCDEFGHIX"])

    def test_insert_lines_contour_scenario(self):
        with Shitty(columns=2, rows=3) as terminal:
            terminal.write(b"AB\r\nCD\x1b[L")
            self.assertEqual(terminal.snapshot().lines, ["AB", "  ", "CD"])

            terminal.write(b"\x1b[1;1H\x1b[L")
            self.assertEqual(terminal.snapshot().lines, ["  ", "AB", "  "])

    def test_decsca_enable_and_disable_character_protection(self):
        with Shitty(columns=6, rows=1) as terminal:
            terminal.write(b"A\x1b[1\"qBC\x1b[0\"qD\x1b[2\"qEF")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["ABCDEF"])
            self.assertEqual(
                [snapshot.cell(column, 0).protected for column in range(6)],
                [False, True, True, False, False, False],
            )

    def test_decsca_default_parameter_disables_protection(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[1\"qAB\x1b[\"qCD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                [snapshot.cell(column, 0).protected for column in range(4)],
                [True, True, False, False],
            )

    def test_decsca_protection_is_independent_of_sgr(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[1\"q\x1b[1mAB\x1b[0\"qCD")
            snapshot = terminal.model_snapshot()
            for column in (0, 1):
                self.assertTrue(snapshot.cell(column, 0).protected)
                self.assertTrue(snapshot.cell(column, 0).bold)

    def test_saved_cursor_restores_decsca_protection_state(self):
        with Shitty(columns=4, rows=1) as terminal:
            terminal.write(b"\x1b[1\"q\x1b7\x1b[0\"qAB\x1b8CD")
            snapshot = terminal.model_snapshot()
            self.assertEqual(snapshot.lines, ["CD  "])
            self.assertTrue(snapshot.cell(0, 0).protected)
            self.assertTrue(snapshot.cell(1, 0).protected)
            self.assertFalse(snapshot.cell(2, 0).protected)
            self.assertFalse(snapshot.cell(3, 0).protected)

    def test_decsel_zero_and_default(self):
        for command in (b"\x1b[?0K", b"\x1b[?K"):
            with self.subTest(command=command), Shitty(columns=6, rows=2) as terminal:
                terminal.write(
                    b"AB\x1b[1\"qCDE\x1b[2\"qF\x1b[1;2H" + command
                )
                self.assertEqual(terminal.snapshot().lines[0], "A CDE ")

    def test_decsel_one(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"A\x1b[1\"qBCD\x1b[2\"qEF\x1b[1;5H\x1b[?1K")
            self.assertEqual(terminal.snapshot().lines[0], " BCD F")

    def test_decsel_two(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"ABCD\ra\x1b[1\"qbc\x1b[2\"qd\r\x1b[?2K")
            self.assertEqual(terminal.snapshot().lines[0], " bc ")

            terminal.write(b"\r\x1b[1\"qA\x1b[2\"qBC\x1b[1\"qD\x1b[?2K")
            self.assertEqual(terminal.snapshot().lines[0], "A  D")

    def test_decsed_zero_and_default(self):
        for command in (b"\x1b[?0J", b"\x1b[?J"):
            with self.subTest(command=command), Shitty(columns=3, rows=3) as terminal:
                terminal.write(
                    b"\x1b[1\"qA\x1b[2\"qB\x1b[1\"qC\x1b[2\"q\r\n"
                    b"D\x1b[1\"qE\x1b[2\"qF\r\n"
                    b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                    b"\x1b[2;2H" + command
                )
                self.assertEqual(terminal.snapshot().lines, ["ABC", "DE ", "G I"])

    def test_iso_protection_inventory_has_all_12_cases(self):
        self.assertEqual(len(ISO_PROTECTION_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(ISO_PROTECTION_UPSTREAM_CASES)), 12)

    def test_decsed_one_contour_scenario(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[1\"qA\x1b[2\"qB\x1b[1\"qC\x1b[2\"q\r\n"
                b"D\x1b[1\"qE\x1b[2\"qF\r\n"
                b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                b"\x1b[2;2H\x1b[?1J"
            )
            self.assertEqual(terminal.snapshot().lines, ["A C", " EF", "GHI"])

    def test_decsed_two_contour_scenario(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[1\"qA\x1b[2\"qB\x1b[1\"qC\x1b[2\"q\r\n"
                b"D\x1b[1\"qE\x1b[2\"qF\r\n"
                b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                b"\x1b[2;2H\x1b[?2J"
            )
            self.assertEqual(terminal.snapshot().lines, ["A C", " E ", "G I"])

    def test_decsed_two_erases_rows_without_protected_cells(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"ABC\r\nDEF\r\n"
                b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                b"\x1b[2;2H\x1b[?2J"
            )
            self.assertEqual(terminal.snapshot().lines, ["   ", "   ", "G I"])

    def test_spa_epa_ed_respects_iso_protection(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1bVc\x1bW\x1b[H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["  c"])

    def test_spa_epa_el_respects_iso_protection(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1bVc\x1bW\x1b[H\x1b[2K")
            self.assertEqual(terminal.snapshot().lines, ["  c"])

    def test_spa_epa_ech_respects_iso_protection(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1bVc\x1bW\x1b[H\x1b[3X")
            self.assertEqual(terminal.snapshot().lines, ["  c"])

    def test_raw_spa_epa_c1_are_ignored_in_utf8_mode(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x96c\x97\x1b[H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["   "])

    def test_raw_spa_epa_c1_in_coalesced_utf8_text_are_ignored(self):
        with Shitty(columns=20, rows=1) as terminal:
            terminal.write(b"ab\x96c\x97defghijklmnop\x1b[H\x1b[K")
            self.assertEqual(terminal.snapshot().lines, [" " * 20])

    def test_regular_ed_does_not_respect_decsca_protection(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1b[1\"qc\x1b[0\"q\x1b[H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["   "])

    def test_soft_reset_clears_iso_protection_mode(self):
        with Shitty(columns=3, rows=1) as terminal:
            terminal.write(b"ab\x1bVc\x1bW\x1b[!p\x1b[H\x1b[J")
            self.assertEqual(terminal.snapshot().lines, ["   "])

    def test_selective_erases_do_not_respect_iso_protection(self):
        for erase in (b"\x1b[?2J", b"\x1b[?2K", b"\x1b[1;1;1;2${"):
            with self.subTest(erase=erase), Shitty(columns=2, rows=1) as terminal:
                terminal.write(b"a\x1bVb\x1bW" + erase)
                self.assertEqual(terminal.snapshot().lines, ["  "])

    def test_selective_erase_still_respects_decsca_protection(self):
        with Shitty(columns=2, rows=1) as terminal:
            terminal.write(b"a\x1b[1\"qb\x1b[0\"q\x1b[?2J")
            self.assertEqual(terminal.snapshot().lines, [" b"])

    def test_vt52_rectangle_inventory_has_all_12_cases(self):
        self.assertEqual(len(VT52_RECTANGLE_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(VT52_RECTANGLE_UPSTREAM_CASES)), 12)

    def test_vt52_enter_cursor_movement_and_leave(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?2l\x1bY\x23\x25")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 3))

            terminal.write(b"\x1bH\x1bB\x1bB\x1bC")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 2))

            terminal.write(b"\x1bA\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

            terminal.write(b"\x1b<\x1b[3;4H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 2))

    def test_vt52_identify_responds_with_escape_slash_z(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b[?2l\x1bZ")
            self.assertEqual(terminal.read_input(), b"\x1b/Z")

    def test_vt52_erase_to_end_of_line(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"abcd\x1b[?2l\x1bY\x20\x22\x1bK")
            self.assertEqual(terminal.snapshot().lines[0], "ab  ")

    def test_decsera_all_defaults(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[1\"qA\x1b[2\"qB\x1b[1\"qC\x1b[2\"q\r\n"
                b"D\x1b[1\"qE\x1b[2\"qF\r\n"
                b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                b"\x1b[${"
            )
            self.assertEqual(terminal.snapshot().lines, ["A C", " E ", "G I"])

    def test_decsera_explicit_rectangle(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[1\"qA\x1b[2\"qB\x1b[1\"qC\x1b[2\"q\r\n"
                b"D\x1b[1\"qE\x1b[2\"qF\r\n"
                b"\x1b[1\"qG\x1b[2\"qH\x1b[1\"qI\x1b[2\"q"
                b"\x1b[2;2;3;3${"
            )
            self.assertEqual(terminal.snapshot().lines, ["ABC", "DE ", "G I"])

    def test_delete_lines_contour_scenario(self):
        page = b"AB\r\nCD\r\nEF\x1b[2;1H"
        for count, expected in (
            (1, ["AB", "EF", "  "]),
            (5, ["AB", "  ", "  "]),
        ):
            with self.subTest(count=count), Shitty(columns=2, rows=3) as terminal:
                terminal.write(page + f"\x1b[{count}M".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_decfra_rectangle(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46;2;2;4;4$x"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "6...0", "A...E", "F...J", "KLMNO"],
            )

    def test_decfra_vertical_rectangle(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46;3;1;3;5$x"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "67890", ".....", "FGHIJ", "KLMNO"],
            )

    def test_decfra_horizontal_rectangle(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46;1;3;5;3$x"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["12.45", "67.90", "AB.DE", "FG.IJ", "KL.NO"],
            )

    def test_decfra_zero_edges_default_to_page_edges(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46;0;0;5;5$x"
            )
            self.assertEqual(terminal.snapshot().lines, ["....."] * 5)

    def test_decfra_omitted_edges_default_to_page_edges(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46$x"
            )
            self.assertEqual(terminal.snapshot().lines, ["....."] * 5)

    def test_decfra_explicit_full_page(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[46;1;1;5;5$x"
            )
            self.assertEqual(terminal.snapshot().lines, ["....."] * 5)

    def test_edit_scroll_cursor_inventory_has_all_12_cases(self):
        self.assertEqual(len(EDIT_SCROLL_CURSOR_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(EDIT_SCROLL_CURSOR_UPSTREAM_CASES)), 12)

    def test_position_margin_inventory_has_all_12_cases(self):
        self.assertEqual(len(POSITION_MARGIN_UPSTREAM_CASES), 12)
        self.assertEqual(len(set(POSITION_MARGIN_UPSTREAM_CASES)), 12)

    def test_delete_columns(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for count, expected in (
            (1, ["12345", "679 0", "ABD E", "FGI J", "KLMNO"]),
            (2, ["12345", "67  0", "AB  E", "FG  J", "KLMNO"]),
            (4, ["12345", "67  0", "AB  E", "FG  J", "KLMNO"]),
        ):
            with self.subTest(count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page)
                terminal.write(b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[2;3H")
                terminal.write(f"\x1b[{count}'~".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page)
            terminal.write(b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[5;5H\x1b[1'~")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            )

    def test_delete_characters(self):
        page = b"12345\r\n67890"
        for count, expected in (
            (1, "1345 "),
            (2, "145  "),
            (4, "1    "),
            (5, "1    "),
        ):
            with self.subTest(margins=False, count=count), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(page + b"\x1b[1;2H")
                terminal.write(f"\x1b[{count}P".encode())
                self.assertEqual(terminal.snapshot().lines, [expected, "67890"])

        for count, expected in (
            (1, "134 5"),
            (2, "14  5"),
            (4, "1   5"),
        ):
            with self.subTest(margins=True, count=count), Shitty(
                columns=5,
                rows=2,
            ) as terminal:
                terminal.write(page + b"\x1b[?69h\x1b[1;4s\x1b[1;2H")
                terminal.write(f"\x1b[{count}P".encode())
                self.assertEqual(terminal.snapshot().lines, [expected, "67890"])

        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(page + b"\x1b[?69h\x1b[2;4s\x1b[1;1H\x1b[P")
            self.assertEqual(terminal.snapshot().lines, ["12345", "67890"])

    def test_clear_scrollback_buffer(self):
        with Shitty(columns=5, rows=5, save_lines=1) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO\r\nPQRST\x1b[H"
            )
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(terminal.all_text()[0], "12345")
            self.assertEqual(
                terminal.snapshot().lines,
                ["67890", "ABCDE", "FGHIJ", "KLMNO", "PQRST"],
            )

            terminal.write(b"\x1b[3J")
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(
                terminal.snapshot().lines,
                ["67890", "ABCDE", "FGHIJ", "KLMNO", "PQRST"],
            )

    def test_erase_characters(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for position, count, expected_line in (
            (b"\x1b[H", 0, " 2345"),
            (b"\x1b[H", 1, " 2345"),
            (b"\x1b[H", 2, "  345"),
            (b"\x1b[2;2H", 2, "6  90"),
            (b"\x1b[H", 4, "    5"),
            (b"\x1b[H", 5, "     "),
            (b"\x1b[H", 6, "     "),
        ):
            with self.subTest(position=position, count=count), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(page + position + f"\x1b[{count}X".encode())
                expected = ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"]
                expected[1 if position == b"\x1b[2;2H" else 0] = expected_line
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_scroll_up_with_margins(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for count, expected in (
            (1, ["12345", "6BCD0", "AGHIE", "F   J", "KLMNO"]),
            (2, ["12345", "6GHI0", "A   E", "F   J", "KLMNO"]),
            (3, ["12345", "6   0", "A   E", "F   J", "KLMNO"]),
            (4, ["12345", "6   0", "A   E", "F   J", "KLMNO"]),
        ):
            with self.subTest(count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page + b"\x1b[?69h\x1b[2;4s\x1b[2;4r")
                terminal.write(f"\x1b[{count}S".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_scroll_up(self):
        page = b"ABC\r\nDEF\r\nGHI"
        for count, expected in (
            (1, ["DEF", "GHI", "   "]),
            (2, ["GHI", "   ", "   "]),
            (3, ["   ", "   ", "   "]),
            (4, ["   ", "   ", "   "]),
        ):
            with self.subTest(count=count), Shitty(columns=3, rows=3) as terminal:
                terminal.write(page + f"\x1b[{count}S".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_scroll_down(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for count, expected in (
            (1, ["12345", "     ", "67890", "ABCDE", "KLMNO"]),
            (3, ["12345", "     ", "     ", "     ", "KLMNO"]),
            (4, ["12345", "     ", "     ", "     ", "KLMNO"]),
        ):
            with self.subTest(margins=True, count=count), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(page + b"\x1b[2;4r")
                terminal.write(f"\x1b[{count}T".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

        for count, expected in (
            (1, ["     ", "12345", "67890", "ABCDE", "FGHIJ"]),
            (5, ["     "] * 5),
            (6, ["     "] * 5),
        ):
            with self.subTest(margins=False, count=count), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(page + f"\x1b[{count}T".encode())
                self.assertEqual(terminal.snapshot().lines, expected)

    def test_unscroll_via_page_growth(self):
        with Shitty(columns=5, rows=5, save_lines=5) as terminal:
            terminal.write(
                b"AAAAA\r\nBBBBB\r\nCCCCC\r\nDDDDD\r\nEEEEE\r\nFFFFF\r\nGGGGG\r\nHHHHH"
            )
            self.assertEqual(terminal.scrollback_state()[0], 3)
            self.assertEqual(
                terminal.snapshot().lines,
                ["DDDDD", "EEEEE", "FFFFF", "GGGGG", "HHHHH"],
            )

            terminal.resize(5, 7)
            self.assertEqual(terminal.scrollback_state()[0], 1)
            self.assertEqual(
                terminal.snapshot().lines,
                ["BBBBB", "CCCCC", "DDDDD", "EEEEE", "FFFFF", "GGGGG", "HHHHH"],
            )

        with Shitty(columns=5, rows=5, save_lines=3) as terminal:
            terminal.write(
                b"AAAAA\r\nBBBBB\r\nCCCCC\r\nDDDDD\r\nEEEEE\r\nFFFFF\r\nGGGGG"
            )
            terminal.resize(5, 9)
            self.assertEqual(terminal.scrollback_state()[0], 0)
            self.assertEqual(
                terminal.snapshot().lines,
                ["AAAAA", "BBBBB", "CCCCC", "DDDDD", "EEEEE", "FFFFF", "GGGGG", "     ", "     "],
            )

    def test_sequence_cuu(self):
        for command, expected in (
            (b"\x1b[A", (1, 1)),
            (b"\x1b[0A", (1, 1)),
            (b"\x1b[1A", (1, 1)),
            (b"\x1b[5A", (1, 0)),
        ):
            with self.subTest(command=command), Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[3;2H" + command)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

        for start, command, expected in (
            (b"\x1b[2;4r\x1b[3;2H", b"\x1b[A", (1, 1)),
            (b"\x1b[2;4r\x1b[3;2H", b"\x1b[5A", (1, 1)),
            (b"\x1b[3;4r\x1b[2;3H", b"\x1b[A", (2, 0)),
        ):
            with self.subTest(start=start, command=command), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(start + command)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

    def test_move_cursor_down(self):
        for count, expected_y in ((1, 1), (5, 2)):
            with self.subTest(count=count), Shitty(columns=2, rows=3) as terminal:
                terminal.write(b"A" + f"\x1b[{count}B".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, expected_y))

    def test_move_cursor_forward(self):
        for count, expected_x in ((1, 1), (3, 2), (4, 2)):
            with self.subTest(count=count), Shitty(columns=3, rows=3) as terminal:
                terminal.write(f"\x1b[{count}C".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (expected_x, 0))

    def test_move_cursor_backward(self):
        for count, expected_x in ((1, 1), (5, 0)):
            with self.subTest(count=count), Shitty(columns=3, rows=3) as terminal:
                terminal.write(b"ABC" + f"\x1b[{count}D".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (expected_x, 0))

    def test_horizontal_position_absolute(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"\x1b[3`")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

            terminal.write(b"\x1b[2`")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

            terminal.write(b"\x1b[5`")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

    def test_horizontal_position_relative(self):
        for command, expected_x in (
            (b"\x1b[a", 1),
            (b"\x1b[1a", 1),
            (b"\x1b[3a", 2),
            (b"\x1b[4a", 2),
        ):
            with self.subTest(command=command), Shitty(columns=3, rows=3) as terminal:
                terminal.write(command)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (expected_x, 0))

    def test_move_cursor_to_column(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"\x1b[3G")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

            terminal.write(b"\x1b[2G")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

            terminal.write(b"\x1b[4G")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

        with Shitty(columns=3, rows=3) as terminal:
            terminal.write("⚡".encode())
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_move_cursor_to_line(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"\x1b[3d")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))

            terminal.write(b"\x1b[2d")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

            terminal.write(b"\x1b[4d")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))

    def test_move_cursor_to_begin_of_line(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"\r\nAB")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

            terminal.write(b"\r")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_carriage_return_honours_left_margin(self):
        setup = b"\x1b[?69h\x1b[5;10s"
        for position, expected_x in (
            (b"\x1b[1;6H", 4),
            (b"\x1b[1;5H", 4),
            (b"\x1b[1;4H", 0),
        ):
            with self.subTest(position=position), Shitty(columns=12, rows=2) as terminal:
                terminal.write(setup + position + b"\r")
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (expected_x, 0))

        with Shitty(columns=12, rows=2) as terminal:
            terminal.write(setup + b"\x1b[?6h\x1b[1;4H\r")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 0))

    def test_nel_indexes_and_returns_to_margin(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[3;5H\x1bE")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))

        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(b"111\r\n222\r\n333\x1b[3;3H\x1bE")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["222", "333", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 2))

        margins = b"\x1b[2;4r\x1b[?69h\x1b[2;4s"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + margins + b"\x1b[4;5H\x1bE")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + margins + b"\x1b[4;3H\x1bE")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "6BCD0", "AGHIE", "F   J", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

    def test_sd_respects_left_right_margin(self):
        with Shitty(columns=5, rows=7) as terminal:
            terminal.write(
                b"abcde\r\nfghij\r\nklmno\r\npqrst\r\nuvwxy"
                b"\x1b[?69h\x1b[2;4s\x1b[2;3H\x1b[2T"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["a   e", "f   j", "kbcdo", "pghit", "ulmny", " qrs ", " vwx "],
            )

    def test_il_over_region_clears_the_band(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"abcde\r\nfGHIj\r\nkLMNo\r\npQRSt\r\nuvwxy"
                b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[2;3H\x1b[99L"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcde", "f   j", "k   o", "p   t", "uvwxy"],
            )

    def test_autowrap_within_left_right_margin(self):
        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;4s\x1b[1;2Hxyzw")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, [" xyz  ", " w    "])

        with Shitty(columns=6, rows=2) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;4s\x1b[?7l\x1b[1;2Hxyzw")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, [" xyw  ", "      "])

    def test_decbi_back_index(self):
        with Shitty(columns=6, rows=6) as terminal:
            terminal.write(b"\x1b[6;5H\x1b6")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (3, 5))

        with Shitty(columns=6, rows=6) as terminal:
            terminal.write(b"\x1b[2;1H\x1b6")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

        with Shitty(columns=12, rows=6) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;5s\x1b[1;2H\x1b6")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

        with Shitty(columns=6, rows=7) as terminal:
            terminal.write(
                b"\x1b[3;2Habcde\x1b[4;2Hfghij\x1b[5;2Hklmno"
                b"\x1b[6;2Hpqrst\x1b[7;2Huvwxy"
                b"\x1b[?69h\x1b[3;5s\x1b[4;6r\x1b[5;3H\x1b6"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[2], " abcde")
            self.assertEqual(snapshot.lines[3], " f ghj")
            self.assertEqual(snapshot.lines[4], " k lmo")
            self.assertEqual(snapshot.lines[5], " p qrt")
            self.assertEqual(snapshot.lines[6], " uvwxy")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 4))

    def test_cnl_cpl_clamp_to_scroll_region_and_left_margin(self):
        setup = b"\x1b[2;4r\x1b[?69h\x1b[5;10s"
        for position, command, expected in (
            (b"\x1b[3;7H", b"\x1b[99E", (4, 3)),
            (b"\x1b[3;7H", b"\x1b[99F", (4, 1)),
        ):
            with self.subTest(command=command), Shitty(columns=12, rows=6) as terminal:
                terminal.write(setup + position + command)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

        with Shitty(columns=12, rows=6) as terminal:
            terminal.write(b"\x1b[3;4r\x1b[?69h\x1b[5;10s\x1b[5;7H\x1b[99E")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 5))

        with Shitty(columns=12, rows=6) as terminal:
            terminal.write(b"\x1b[3;7H\x1b[99E")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 5))

    def test_move_cursor_to_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for command, expected in (
            (b"\x1b[3;2H", (1, 2)),
            (b"\x1b[H", (0, 0)),
            (b"\x1b[6;6H", (4, 4)),
        ):
            with self.subTest(command=command), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page + command)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                page
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[?6h\x1b[H"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertEqual(snapshot.cell(1, 1).char, "7")
            self.assertEqual(snapshot.cell(3, 3).char, "I")

    def test_move_cursor_to_next_tab_contour_scenario(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().cursor_x, 8)

            for _ in range(2):
                terminal.write(b"\x1b[8G\t")
                self.assertEqual(terminal.snapshot().cursor_x, 8)

            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().cursor_x, 16)
            terminal.write(b"\t")
            self.assertEqual(terminal.snapshot().cursor_x, 19)

            terminal.write_chunks(b"A", b"B", b"\t")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (8, 1))
            self.assertEqual(snapshot.cell(19, 0).char, "A")
            self.assertEqual(snapshot.cell(0, 1).char, "B")

    def test_save_and_restore_cursor_contour_scenario(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[?7l\x1b7"
                b"\x1b[3;3H\x1b[?7h\x1b[?6h"
                b"\x1b8\x1b[?7$p\x1b[?6$p"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[?7;1$y\x1b[?6;2$y",
            )

    def test_saved_cursors_are_independent_between_screens(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(
                b"\x1b[2;3H\x1b7"
                b"\x1b[?47h\x1b[6;7H\x1b7"
                b"\x1b[?47l\x1b8"
            )
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

            terminal.write(b"\x1b[?47h\x1b8")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (6, 5))

    def test_alternate_screen_modes_contour_scenario(self):
        for mode, carried, erased in (
            (47, True, False),
            (1047, True, True),
            (1049, False, True),
        ):
            set_mode = f"\x1b[?{mode}h".encode()
            reset_mode = f"\x1b[?{mode}l".encode()
            with self.subTest(mode=mode), Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"abc\r\nabc")
                primary_cursor = (3, 1)
                self.assertEqual(
                    (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                    primary_cursor,
                )

                terminal.write(set_mode)
                if carried:
                    snapshot = terminal.snapshot()
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        primary_cursor,
                    )

                terminal.write(b"\x1b[2J\x1b[2;1Hdef\r\ndef")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[:3], ["     ", "def  ", "def  "])
                alternate_cursor = (snapshot.cursor_x, snapshot.cursor_y)

                terminal.write(reset_mode)
                snapshot = terminal.snapshot()
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    alternate_cursor if carried else primary_cursor,
                )
                self.assertEqual(snapshot.lines[:3], ["abc  ", "abc  ", "     "])

                terminal.write(set_mode)
                snapshot = terminal.snapshot()
                expected = "     " if erased else "def  "
                self.assertEqual(snapshot.lines[1:3], [expected, expected])

    def test_dch_works_outside_top_bottom_margin(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"abcde\x1b[2;3r\x1b[1;1H\x1b[99P")
            self.assertEqual(terminal.snapshot().lines[0], "     ")

    def test_ed_two_ignores_scroll_region(self):
        with Shitty(columns=3, rows=3) as terminal:
            terminal.write(
                b"\x1b[Haaa\r\nbbb\r\nccc"
                b"\x1b[2;2r\x1b[2J\x1b[r"
            )
            self.assertEqual(terminal.snapshot().lines, ["   "] * 3)

    def test_cbt_ignores_left_right_margin(self):
        with Shitty(columns=40, rows=3) as terminal:
            terminal.write(b"\x1b[?69h\x1b[5;30s\x1b[1;9H\x1b[2Z")
            self.assertEqual(terminal.snapshot().cursor_x, 0)

    def test_cbt_ignores_left_right_margin_under_origin_mode(self):
        setup = b"\x1b[?69h\x1b[5;30s\x1b[?6h"
        for position, command, before, after in (
            (b"\x1b[1;20H", b"\x1b[Z", 23, 16),
            (b"\x1b[1;5H", b"\x1b[4Z", 8, 4),
        ):
            with self.subTest(position=position), Shitty(columns=40, rows=3) as terminal:
                terminal.write(setup + position)
                self.assertEqual(terminal.snapshot().cursor_x, before)
                terminal.write(command)
                self.assertEqual(terminal.snapshot().cursor_x, after)

    def test_vt_and_ff_honor_linefeed_mode(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[20l\x1b[1;5H\v")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 1))

            terminal.write(b"\x1b[20h\x1b[1;5H\f")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_decscl_conformance_level_gating_contour_scenario(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(b"\x1b[62;1\"p\x1b[4$p")
            self.assertEqual(terminal.read_input(), b"")
            terminal.write(b"\x1b[63;1\"p\x1b[4$p")
            self.assertEqual(terminal.read_input(), b"\x1b[4;2$y")

        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                b"\x1b[63;1\"p\x1b[?69h\x1b[5;6s"
                b"\x1b[1;5Habc"
            )
            self.assertEqual(terminal.snapshot().cursor_x, 7)

        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(
                b"\x1b[61\"p\x1b[65;1\"p"
                b"\x1bP$q\"p\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1bP1$r65;1\"p\x1b\\",
            )

    def test_decstr_resets_left_right_margin_mode(self):
        with Shitty(columns=20, rows=5) as terminal:
            terminal.write(b"\x1b[?69h\x1b[?69$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?69;1$y")

            terminal.write(b"\x1b[!p\x1b[?69$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?69;2$y")

            terminal.write(b"\x1b[2;4s\x1b[1;3Habc")
            self.assertEqual(terminal.snapshot().cursor_x, 5)

    def test_decrqcra_honors_origin_mode(self):
        with Shitty(columns=10, rows=10) as terminal:
            terminal.write(
                b"\x1b[5;5HX"
                b"\x1b[5;7r\x1b[?69h\x1b[5;7s\x1b[?6h"
                b"\x1b[1;1;1;1;1;1*y"
            )
            origin_reply = terminal.read_input()
            self.assertTrue(origin_reply.startswith(b"\x1bP1!~"))
            self.assertTrue(origin_reply.endswith(b"\x1b\\"))

            terminal.write(b"\x1b[?6l\x1b[1;1;1;1;1;1*y")
            absolute_reply = terminal.read_input()
            self.assertTrue(absolute_reply.startswith(b"\x1bP1!~"))
            self.assertNotEqual(origin_reply, absolute_reply)

    def test_decrqcra_reports_a_rectangular_area(self):
        # xterm answers these byte-for-byte; VTE has the same parser and
        # request-id framing, although outside VTE's test mode it deliberately
        # substitutes 0000 to avoid exposing screen contents.
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"ab")

            for sequence, expected in (
                # The final/intermediate pair is part of the protocol: $y is
                # DECRPM, not the DECRQCRA request form.
                (b"\x1b[1;1;1;1;1;1*y", b"\x1bP1!~FF9F\x1b\\"),
                (b"\x1b[42;1;1;1;1;1*y", b"\x1bP42!~FF9F\x1b\\"),
                (b"\x1b[1;1;1;1;1;2*y", b"\x1bP1!~FF3D\x1b\\"),
                (b"\x1b[1*y", b"\x1bP1!~FF3D\x1b\\"),
                (b"\x1b[1;1;3;1;3;5*y", b"\x1bP1!~0000\x1b\\"),
            ):
                with self.subTest(sequence=sequence):
                    terminal.write(sequence)
                    self.assertEqual(terminal.read_input(), expected)

            terminal.write(b"\x1b[2;1H ")
            terminal.write(b"\x1b[1;1;2;1;2;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FFE0\x1b\\")

            terminal.write(b"\x1b[2;1H\x1b[1ma")
            terminal.write(b"\x1b[1;1;2;1;2;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FF1F\x1b\\")

            terminal.write(b"\x1b[1;1;1;1;1;1$y")
            self.assertEqual(terminal.read_input(), b"")

    def test_xtchecksum_selects_the_decrqcra_algorithm(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[1ma")

            def first_cell():
                terminal.write(b"\x1b[1;1;1;1;1;1*y")
                return terminal.read_input()

            self.assertEqual(first_cell(), b"\x1bP1!~FF1F\x1b\\")

            terminal.write(b"\x1b[1#y")
            self.assertEqual(first_cell(), b"\x1bP1!~00E1\x1b\\")

            terminal.write(b"\x1b[2#y")
            self.assertEqual(first_cell(), b"\x1bP1!~FF9F\x1b\\")

            terminal.write(b"\x1b[8#y\x1b[1;1;3;1;3;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FFE0\x1b\\")

            terminal.write(b"\x1b[10#y")
            self.assertEqual(first_cell(), b"\x1bP1!~FF9F\x1b\\")
            terminal.write(b"\x1b[1;1;3;1;3;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FFE0\x1b\\")

            terminal.write(b"\x1b[#y")
            self.assertEqual(first_cell(), b"\x1bP1!~FF1F\x1b\\")

    def test_xtchecksum_reset_restores_the_configured_default(self):
        # xterm restores its checksumExtension resource on both resets. Shitty
        # deliberately exposes no equivalent application setting, therefore
        # its configured default is zero and is observed through DECRQCRA.
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[1ma\x1b[1#y\x1b[1;1;1;1;1;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~00E1\x1b\\")

            terminal.write(b"\x1b[!p\x1b[1;1;1;1;1;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FF1F\x1b\\")

            terminal.write(b"\x1b[1#y\x1bc\x1b[1ma\x1b[1;1;1;1;1;1*y")
            self.assertEqual(terminal.read_input(), b"\x1bP1!~FF1F\x1b\\")

    def test_decsnls_is_a_noop_without_xterm_window_operations(self):
        # xterm may resize after CSI Ps * | only when window operations are
        # allowed. VTE leaves this VT525 control unimplemented, and the local
        # Ghostty, Kitty and Alacritty sources have no implementation. Keep
        # the source boundaries while asserting the common no-op contract.
        with Shitty(columns=80, rows=25) as terminal:
            terminal.write(b"\x1b[25;80H")
            before = terminal.snapshot()

            for sequence in (b"\x1b[24*|", b"\x1b[*|", b"\x1b[0*|"):
                with self.subTest(sequence=sequence):
                    terminal.write(sequence)
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.lines, before.lines)
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (79, 24),
                    )

            terminal.write(b"\x1bP$q*|\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP0$r\x1b\\")

    def test_line_feed_below_the_scrolling_region_stops_at_page_bottom(self):
        def below_region(controls):
            with Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[1;2r\x1b[5;1H" + controls)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 4))
                self.assertEqual(snapshot.lines, ["     "] * 5)

        with self.subTest("one LF at page bottom"):
            below_region(b"\n")
        with self.subTest("many LFs at page bottom"):
            below_region(b"\n" * 10)

        with self.subTest("the bottom margin still scrolls"):
            with Shitty(columns=5, rows=5) as terminal:
                terminal.write(
                    b"\x1b[1;2r\x1b[1;1HA\x1b[2;1HB"
                    b"\x1b[2;1H\n"
                )
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, ["B    "] + ["     "] * 4)
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

        with self.subTest("below region but above page bottom advances"):
            with Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[1;2r\x1b[3;1H\n")
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 3))

    def test_omitted_one_based_parameter_takes_its_default(self):
        def cursor_after(sequence):
            with Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[3;3H" + sequence)
                snapshot = terminal.snapshot()
                return snapshot.cursor_x, snapshot.cursor_y

        for sequence, expected in (
            (b"\x1b[;4H", (3, 0)),
            (b"\x1b[4;H", (0, 3)),
            (b"\x1b[0;0H", (0, 0)),
            (b"\x1b[;4f", (3, 0)),
            (b"\x1b[0G\x1b[0d", (0, 0)),
            (b"\x1b[`", (0, 2)),
        ):
            with self.subTest(sequence=sequence):
                self.assertEqual(cursor_after(sequence), expected)

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(b"\x1b[1;1H\x1b[a")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_zero_count_moves_or_edits_by_one(self):
        with self.subTest("CUU, CUD, CUF, CUB"):
            with Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[3;3H\x1b[0A")
                self.assertEqual(terminal.snapshot().cursor_y, 1)
                terminal.write(b"\x1b[0B")
                self.assertEqual(terminal.snapshot().cursor_y, 2)
                terminal.write(b"\x1b[0C")
                self.assertEqual(terminal.snapshot().cursor_x, 3)
                terminal.write(b"\x1b[0D")
                self.assertEqual(terminal.snapshot().cursor_x, 2)

        for sequence, expected in (
            (b"\x1b[0@", " ABCD"),
            (b"\x1b[0P", "BCDE "),
            (b"\x1b[0X", " BCDE"),
        ):
            with self.subTest(sequence=sequence), Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"ABCDE\x1b[1;1H" + sequence)
                self.assertEqual(terminal.snapshot().lines[0], expected)

    def test_deccra_defaults_an_omitted_source_corner(self):
        with Shitty(columns=8, rows=8) as terminal:
            terminal.write(
                b"abcdefgh\r\nijklmnop\r\nqrstuvwx\r\nyz012345\r\n"
                b"ABCDEFGH\r\nIJKLMNOP\r\nQRSTUVWX\r\nYZ6789!@"
                b"\x1b[;;2;2;;5;5;1$v"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[4], "ABCDabGH")
            self.assertEqual(snapshot.lines[5], "IJKLijOP")
            self.assertEqual(snapshot.lines[0], "abcdefgh")
            self.assertEqual(snapshot.lines[6], "QRSTUVWX")

    def test_rectangular_area_is_clamped_to_the_page(self):
        with self.subTest("DECFRA"):
            with Shitty(columns=4, rows=4) as terminal:
                terminal.write(b"\x1b[88;1;1;99;99$x")
                self.assertEqual(terminal.snapshot().lines, ["XXXX"] * 4)

        for sequence in (b"\x1b[2;2;99;99$z", b"\x1b[2;2;99;99${"):
            with self.subTest(sequence=sequence), Shitty(columns=4, rows=4) as terminal:
                terminal.write(b"abcd\r\nefgh\r\nijkl\r\nmnop" + sequence)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], "abcd")
                self.assertEqual(snapshot.lines[1], "e   ")
                self.assertEqual(snapshot.lines[3], "m   ")

    def test_rectangular_area_is_relative_to_the_origin(self):
        with Shitty(columns=4, rows=6) as terminal:
            terminal.write(
                b"aaaa\r\nbbbb\r\ncccc\r\ndddd\r\neeee\r\nffff"
                b"\x1b[3;5r\x1b[?6h\x1b[88;1;1;2;4$x"
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["aaaa", "bbbb", "XXXX", "XXXX", "eeee", "ffff"],
            )

    def test_deccra_truncates_a_copy_at_the_page_edge(self):
        with Shitty(columns=8, rows=8) as terminal:
            terminal.write(
                b"abcdefgh\r\nijklmnop\r\nqrstuvwx\r\nyz012345\r\n"
                b"ABCDEFGH\r\nIJKLMNOP\r\nQRSTUVWX\r\nYZ6789!@"
                b"\x1b[2;2;4;4;1;7;7;1$v"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[6], "QRSTUVjk")
            self.assertEqual(snapshot.lines[7], "YZ6789rs")
            self.assertEqual(snapshot.lines[:6], [
                "abcdefgh", "ijklmnop", "qrstuvwx", "yz012345",
                "ABCDEFGH", "IJKLMNOP",
            ])

    def test_decdc_deletes_a_column_from_blank_rows_too(self):
        with Shitty(columns=7, rows=5) as terminal:
            terminal.write(b"abcdefg\r\nABCDEFG\x1b[1;2H\x1b['~")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "acdefg ")
            self.assertEqual(snapshot.lines[1], "ACDEFG ")
            self.assertEqual(snapshot.lines[4], "       ")

    def test_icon_and_window_titles_are_set_independently(self):
        def titles_after(sequence):
            with Shitty(
                columns=4,
                rows=2,
                extra_arguments=("-allowWindowOps", "true"),
            ) as terminal:
                terminal.write(sequence + b"\x1b[20t\x1b[21t")
                return terminal.read_input()

        self.assertEqual(
            titles_after(b"\x1b]0;both\x1b\\"),
            b"\x1b]Lboth\x1b\\\x1b]lboth\x1b\\",
        )
        self.assertEqual(
            titles_after(b"\x1b]2;window\x1b\\\x1b]1;icon\x1b\\"),
            b"\x1b]Licon\x1b\\\x1b]lwindow\x1b\\",
        )
        self.assertEqual(
            titles_after(b"\x1b]1;icon\x1b\\\x1b]2;window\x1b\\"),
            b"\x1b]Licon\x1b\\\x1b]lwindow\x1b\\",
        )

    def test_each_title_is_reported_with_its_own_osc(self):
        with Shitty(
            columns=4,
            rows=2,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(
                b"\x1b]1;the-icon\x1b\\\x1b]2;the-window\x1b\\"
                b"\x1b[20t\x1b[21t"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]Lthe-icon\x1b\\\x1b]lthe-window\x1b\\",
            )

    def test_xtpushtitle_and_xtpoptitle_share_optional_pair_stack(self):
        def query_titles(terminal):
            terminal.write(b"\x1b[20t\x1b[21t")
            return terminal.read_input()

        def fresh():
            return Shitty(
                columns=4,
                rows=2,
                extra_arguments=("-allowWindowOps", "true"),
            )

        with self.subTest("pop icon consumes a pair"):
            with fresh() as terminal:
                terminal.write(
                    b"\x1b]0;first\x1b\\\x1b[22;0t\x1b]0;x\x1b\\"
                    b"\x1b[23;1t"
                )
                self.assertEqual(query_titles(terminal), b"\x1b]Lfirst\x1b\\\x1b]lx\x1b\\")
                terminal.write(b"\x1b[23;2t")
                self.assertEqual(query_titles(terminal), b"\x1b]Lfirst\x1b\\\x1b]lx\x1b\\")

        with self.subTest("pop window consumes a pair"):
            with fresh() as terminal:
                terminal.write(
                    b"\x1b]0;first\x1b\\\x1b[22;0t\x1b]0;x\x1b\\"
                    b"\x1b[23;2t"
                )
                self.assertEqual(query_titles(terminal), b"\x1b]Lx\x1b\\\x1b]lfirst\x1b\\")
                terminal.write(b"\x1b[23;1t")
                self.assertEqual(query_titles(terminal), b"\x1b]Lx\x1b\\\x1b]lfirst\x1b\\")

        with self.subTest("pop both"):
            with fresh() as terminal:
                terminal.write(
                    b"\x1b]0;first\x1b\\\x1b[22;0t\x1b]0;x\x1b\\"
                    b"\x1b[23;0t"
                )
                self.assertEqual(query_titles(terminal), b"\x1b]Lfirst\x1b\\\x1b]lfirst\x1b\\")

        with self.subTest("partial pairs search the older stack entry"):
            with fresh() as terminal:
                terminal.write(
                    b"\x1b]2;win\x1b\\\x1b]1;ico\x1b\\"
                    b"\x1b[22;1t\x1b[22;2t\x1b]2;y\x1b\\\x1b]1;z\x1b\\"
                    b"\x1b[23;0t"
                )
                self.assertEqual(query_titles(terminal), b"\x1b]Lico\x1b\\\x1b]lwin\x1b\\")

        with self.subTest("LIFO, empty pop, and bounded depth"):
            with fresh() as terminal:
                terminal.write(
                    b"\x1b]2;window\x1b\\\x1b]1;a\x1b\\\x1b[22;1t\x1b]1;b\x1b\\"
                    b"\x1b[22;1t\x1b]1;z\x1b\\\x1b[23;1t"
                )
                self.assertEqual(query_titles(terminal), b"\x1b]Lb\x1b\\\x1b]lwindow\x1b\\")
                terminal.write(b"\x1b[23;1t")
                self.assertEqual(query_titles(terminal), b"\x1b]La\x1b\\\x1b]lwindow\x1b\\")
                terminal.write(b"\x1b]0;kept\x1b\\\x1b[23;0t")
                self.assertEqual(query_titles(terminal), b"\x1b]Lkept\x1b\\\x1b]lkept\x1b\\")
                for index in range(20):
                    terminal.write(f"\x1b]1;t{index}\x1b\\\x1b[22;1t".encode())
                terminal.write(b"\x1b[23;1t")
                self.assertEqual(query_titles(terminal), b"\x1b]Lt19\x1b\\\x1b]lkept\x1b\\")

    def test_xtwinops_reads_its_operation_from_first_parameter(self):
        def resize_and_report(sequence):
            with Shitty(
                columns=20,
                rows=10,
                extra_arguments=("-allowWindowOps", "true"),
            ) as terminal:
                terminal.write(sequence + b"\x1b[18t")
                return terminal.read_input()

        # The implementations that accept resize requests agree on CSI 8 ;
        # height ; width t. CSI 18 t observes the resulting text area.
        self.assertEqual(resize_and_report(b"\x1b[8;5;12t"), b"\x1b[8;5;12t")

    def test_decslpp_sets_page_length(self):
        with Shitty(
            columns=20,
            rows=10,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            # CSI Ps t is DECSLPP for Ps >= 24, not an XTWINOPS opcode.
            terminal.write(b"\x1b[42t\x1b[18t")
            self.assertEqual(terminal.read_input(), b"\x1b[8;42;20t")

    def test_osc5_addresses_special_colors_and_osc4_aliases(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b]5;0;rgb:f0f0/f0f0/f0f0;4;rgb:1010/2020/3030\x1b\\"
                b"\x1b]5;0;?\x1b\\\x1b]5;4;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]5;0;rgb:f0f0/f0f0/f0f0\x1b\\"
                b"\x1b]5;4;rgb:1010/2020/3030\x1b\\",
            )

            terminal.write(
                b"\x1b]4;256;rgb:aaaa/bbbb/cccc\x1b\\"
                b"\x1b]5;0;?\x1b\\\x1b]4;256;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]5;0;rgb:aaaa/bbbb/cccc\x1b\\"
                b"\x1b]4;256;rgb:aaaa/bbbb/cccc\x1b\\",
            )

            terminal.write(b"\x1b]5;5;rgb:0000/0000/0000\x1b\\")
            self.assertEqual(terminal.read_input(), b"")

    def test_osc105_resets_selected_or_all_special_colors(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(b"\x1b]5;0;?\x1b\\\x1b]5;4;?\x1b\\")
            originals = terminal.read_input()
            second_reply = originals.index(b"\x1b]5;4;")
            original0 = originals[:second_reply]

            terminal.write(
                b"\x1b]5;0;rgb:f0f0/f0f0/f0f0;4;rgb:1010/2020/3030\x1b\\"
                b"\x1b]105;0\x1b\\\x1b]5;0;?\x1b\\\x1b]5;4;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                original0 + b"\x1b]5;4;rgb:1010/2020/3030\x1b\\",
            )

            terminal.write(
                b"\x1b]5;0;rgb:f0f0/f0f0/f0f0;4;rgb:1010/2020/3030\x1b\\"
                b"\x1b]105\x1b\\\x1b]5;0;?\x1b\\\x1b]5;4;?\x1b\\"
            )
            self.assertEqual(terminal.read_input(), originals)

    def test_decxcpr_reports_cursor_position_and_page(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[5;6H\x1b[?6n")
            self.assertEqual(terminal.read_input(), b"\x1b[?5;6;1R")

    def test_deccksr_echoes_request_id_with_empty_macro_checksum(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write(b"\x1b[?63;123n")
            self.assertEqual(terminal.read_input(), b"\x1bP123!~0000\x1b\\")

    def test_backspace_stops_at_decsrlm_left_margin(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[5;10s"
                b"\x1b[1;5H\b\x1b[6n"
                b"\x1b[1;3H\b\x1b[6n"
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b[1;5R\x1b[1;2R"
            )

    def test_reverse_wraparound_carries_cursor_to_previous_line(self):
        def cpr_after(sequence):
            with Shitty(columns=5, rows=3) as terminal:
                terminal.write(sequence + b"\x1b[6n")
                return terminal.read_input()

        # Reverse wrap requires autowrap and, for mode 45, a soft-wrapped
        # preceding line. Mode 1045 permits the hard-line boundary.
        self.assertEqual(
            cpr_after(b"\x1b[?7l\x1b[?45h\x1b[2;1H\b"),
            b"\x1b[2;1R",
        )
        self.assertEqual(
            cpr_after(b"\x1b[?7h\x1b[?45h\x1b[2;1H\b"),
            b"\x1b[2;1R",
        )
        self.assertEqual(
            cpr_after(b"\x1b[?7h\x1b[1;1HABCDEF\x1b[?45h\x1b[2;1H\b"),
            b"\x1b[1;5R",
        )
        self.assertEqual(
            cpr_after(b"\x1b[?7h\x1b[?1045h\x1b[2;1H\b"),
            b"\x1b[1;5R",
        )
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[?7h\x1b[?1045h\x1b[!p\x1b[?1045$p\x1b[?45$p")
            self.assertEqual(
                terminal.read_input(), b"\x1b[?1045;2$y\x1b[?45;2$y"
            )

    def test_sixel_placement_updates_exactly_the_covered_render_rows(self):
        with Shitty(columns=18, rows=10, glyph_px=6, glyph_py=12) as terminal:
            terminal.write(contour_checkerboard_sixel())

            self.assertEqual(terminal.last_update_rows(), tuple(range(9)))

    def test_decdwl_reaches_the_render_update_as_a_double_width_line(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b#6")

            snapshot = terminal.snapshot()
            self.assertEqual(terminal.last_update_rows(), (0,))
            self.assertEqual(snapshot.cell(0, 0).line_attribute, 3)

    def test_hyperlinked_text_reaches_the_render_update_with_its_id(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(
                b"\x1b]8;;https://example.com\x1b\\"
                b"ab"
                b"\x1b]8;;\x1b\\"
            )

            snapshot = terminal.snapshot()
            self.assertEqual(terminal.last_update_rows(), (0,))
            self.assertNotEqual(snapshot.cell(0, 0).hyperlink, 0)
            self.assertEqual(
                snapshot.cell(1, 0).hyperlink,
                snapshot.cell(0, 0).hyperlink,
            )
            self.assertEqual(snapshot.cell(2, 0).hyperlink, 0)
            self.assertEqual(terminal.hyperlink(0, 0), "https://example.com")
            self.assertEqual(terminal.hyperlink(1, 0), "https://example.com")
            self.assertEqual(terminal.hyperlink(2, 0), "")

    def test_index_outside_margin_contour_scenario(self):
        page = b"1234\r\n5678\r\nABCD\r\nEFGH\r\nIJKL\r\nMNOP"
        expected = ["1234", "5678", "ABCD", "EFGH", "IJKL", "MNOP"]
        with Shitty(columns=4, rows=6) as terminal:
            terminal.write(page + b"\x1b[2;4r")

            for position, expected_cursor in (
                (b"\x1b[1;3H", (2, 1)),
                (b"\x1b[5;3H", (2, 5)),
                (b"\x1b[6;3H", (2, 5)),
            ):
                terminal.write(position + b"\x1bD")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, expected)
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    expected_cursor,
                )

    def test_index_inside_margin_contour_scenario(self):
        with Shitty(columns=2, rows=6) as terminal:
            terminal.write(
                b"11\r\n22\r\n33\r\n44\r\n55\r\n66"
                b"\x1b[2;4r\x1b[3;2H\x1bD"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["11", "22", "33", "44", "55", "66"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

    def test_index_at_bottom_margin_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[2;4r\x1b[4;2H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "ABCDE", "FGHIJ", "     ", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                page
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r"
                b"\x1b[4;2H\x1bD"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "6BCD0", "AGHIE", "F   J", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

    def test_vertical_scroll_is_confined_to_left_right_margins(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        setup = page + b"\x1b[2;4r\x1b[?69h\x1b[2;4s"
        untouched = ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"]

        for position, control, expected_cursor in (
            (b"\x1b[4;5H", b"\x1bD", (4, 3)),
            (b"\x1b[4;1H", b"\x1bD", (0, 3)),
            (b"\x1b[3;5H", b"\x1bD", (4, 3)),
            (b"\x1b[2;5H", b"\x1bM", (4, 1)),
            (b"\x1b[4;5H", b"\n", (4, 3)),
        ):
            with self.subTest(control=control, position=position), Shitty(
                columns=5,
                rows=5,
            ) as terminal:
                terminal.write(setup + position + control)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, untouched)
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    expected_cursor,
                )

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(setup + b"\x1b[4;5H\f")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, untouched)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 3))
            terminal.write(b"\v")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, untouched)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 3))

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(setup + b"\x1b[4;2H\x1bD")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "6BCD0", "AGHIE", "F   J", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 3))

    def test_reverse_index_without_custom_margins(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[5;2H")
            for expected_y in (3, 2, 1, 0):
                terminal.write(b"\x1bM")
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, expected_y))

            terminal.write(b"\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["     ", "12345", "67890", "ABCDE", "FGHIJ"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

            terminal.write(b"\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["     ", "     ", "12345", "67890", "ABCDE"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_reverse_index_with_vertical_margin(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        original = ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"]
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[2;4r\x1b[5;2H")
            for expected_y in (3, 2, 1):
                terminal.write(b"\x1bM")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, original)
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, expected_y))

            terminal.write(b"\x1bM")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "     ", "67890", "ABCDE", "KLMNO"],
            )
            terminal.write(b"\x1bM")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "     ", "     ", "67890", "KLMNO"],
            )

            terminal.write(b"\x1b[1;2H\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["12345", "     ", "     ", "67890", "KLMNO"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            terminal.write(b"\x1bM")
            self.assertEqual(terminal.snapshot().lines, snapshot.lines)

    def test_reverse_index_with_both_margin_pairs(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        original = ["12345", "67890", "ABCDE", "FGHIJ", "KLMNO"]
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                page
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[5;2H"
            )
            for expected_y in (3, 2, 1):
                terminal.write(b"\x1bM")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines, original)
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, expected_y))

            terminal.write(b"\x1bM")
            self.assertEqual(
                terminal.snapshot().lines,
                ["12345", "6   0", "A789E", "FBCDJ", "KLMNO"],
            )
            terminal.write(b"\x1bM")
            expected = ["12345", "6   0", "A   E", "F789J", "KLMNO"]
            self.assertEqual(terminal.snapshot().lines, expected)

            terminal.write(b"\x1b[1;2H\x1bM")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, expected)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_screen_alignment_pattern_contour_scenario(self):
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
                b"\x1b[2;4r\x1b#8"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["EEEEE"] * 5)
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\x1bP$qr\x1b\\\x1bP$qs\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1bP1$r1;5r\x1b\\\x1bP1$r1;5s\x1b\\",
            )

    def test_cursor_next_line_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for count, expected in ((1, (0, 2)), (5, (0, 4))):
            with self.subTest(count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page + b"\x1b[2;3H" + f"\x1b[{count}E".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

        setup = page + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[?6h"
        for count, expected in (
            (1, (1, 2)),
            (2, (1, 3)),
            (3, (1, 3)),
            (4, (1, 3)),
        ):
            with self.subTest(origin_count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(setup + b"\x1b[1;2H")
                self.assertEqual(terminal.snapshot().cell(2, 1).char, "8")
                terminal.write(f"\x1b[{count}E".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

    def test_cursor_previous_line_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        for count, expected in ((1, (0, 3)), (5, (0, 0))):
            with self.subTest(count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(page + f"\x1b[{count}F".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

        setup = page + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[?6h"
        for count, expected in (
            (1, (1, 2)),
            (2, (1, 1)),
            (3, (1, 1)),
        ):
            with self.subTest(origin_count=count), Shitty(columns=5, rows=5) as terminal:
                terminal.write(setup + b"\x1b[3;3H" + f"\x1b[{count}F".encode())
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), expected)

    def test_decrqss_reports_scroll_region_margins(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[5;6r\x1bP$qr\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r5;6r\x1b\\")

        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[?69h\x1b[3;4s\x1bP$qs\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r3;4s\x1b\\")

    def test_decrqss_reports_current_sgr_contour_scenario(self):
        for setting, expected in (
            (b"\x1b[1m", b"\x1bP1$r0;1m\x1b\\"),
            (b"\x1b[1;3m", b"\x1bP1$r0;1;3m\x1b\\"),
            (
                b"\x1b[31;44;4:3;58:5:1m",
                b"\x1bP1$r0;4:3;31;44;58:5:1m\x1b\\",
            ),
        ):
            with self.subTest(setting=setting), Shitty(columns=20, rows=4) as terminal:
                terminal.write(setting + b"\x1bP$qm\x1b\\")
                self.assertEqual(terminal.read_input(), expected)

    def test_decrqss_reports_attribute_change_extent(self):
        for mode, expected in (
            (0, b"\x1bP1$r0*x\x1b\\"),
            (2, b"\x1bP1$r2*x\x1b\\"),
        ):
            with self.subTest(mode=mode), Shitty(columns=20, rows=4) as terminal:
                terminal.write(
                    f"\x1b[{mode}*x".encode()
                    + b"\x1bP$q*x\x1b\\"
                )
                self.assertEqual(terminal.read_input(), expected)

    def test_decrqss_reports_vt525_keyboard_settings(self):
        for setting, request in (
            (b"\x1b[0+q", b"+q"),
            (b"\x1b[0*}", b"*}"),
            (b"\x1b[0+r", b"+r"),
            (b"\x1b[2+r", b"+r"),
        ):
            with self.subTest(setting=setting), Shitty(columns=20, rows=4) as terminal:
                terminal.write(setting + b"\x1bP$q" + request + b"\x1b\\")
                self.assertEqual(terminal.read_input(), b"\x1bP0$r\x1b\\")

    def test_raw_eight_bit_c1_input_follows_utf8_consensus(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x9b3;5H")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (5, 0))
            self.assertEqual(snapshot.lines[0], "�3;5H     ")

        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[3;4H\x84")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (4, 2))
            self.assertEqual(snapshot.cell(3, 2).char, "�")

        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b]2;before\x1b\\")
            terminal.read_actions()
            terminal.write(b"\x9d2;hi\x9c")
            self.assertEqual(terminal.read_actions(), [])
            self.assertEqual(terminal.snapshot().lines[0], "�2;hi�    ")

        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\xc9\x90X")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertEqual(snapshot.lines[0][:2], "ɐX")

    def test_s8c1t_selects_eight_bit_reply_controls(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")

        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b G\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x9b1;1R")

    def test_decid_identifies_terminal_like_primary_da(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1bZ")
            via_decid = terminal.read_input()
            terminal.write(b"\x1b[c")
            via_da1 = terminal.read_input()
            self.assertTrue(via_decid.startswith(b"\x1b[?"))
            self.assertTrue(via_decid.endswith(b"c"))
            self.assertEqual(via_decid, via_da1)

    def test_report_cursor_position_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[2;3H\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[2;3R")

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                page
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[?6h"
                b"\x1b[3;2H\x1b[6n"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[3;2R")

    def test_report_extended_cursor_position_contour_scenario(self):
        page = b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO"
        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(page + b"\x1b[2;3H\x1b[?6n")
            self.assertEqual(terminal.read_input(), b"\x1b[?2;3;1R")

        with Shitty(columns=5, rows=5) as terminal:
            terminal.write(
                page
                + b"\x1b[?69h\x1b[2;4s\x1b[2;4r\x1b[?6h"
                b"\x1b[3;2H\x1b[?6n"
            )
            self.assertEqual(terminal.read_input(), b"\x1b[?3;2;1R")

    def test_in_band_window_resize_contour_scenario(self):
        with Shitty(
            columns=20,
            rows=10,
            glyph_px=9,
            glyph_py=18,
        ) as terminal:
            terminal.write(b"\x1b[?2048h")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b[48;10;20;180;180t",
            )

        with Shitty(
            columns=20,
            rows=10,
            glyph_px=9,
            glyph_py=18,
        ) as terminal:
            terminal.write(b"\x1b[?2048h")
            first = terminal.read_input()
            terminal.resize(80, 24)
            self.assertEqual(
                first + terminal.read_input(),
                b"\x1b[48;10;20;180;180t"
                b"\x1b[48;24;80;432;720t",
            )

        with Shitty(
            columns=20,
            rows=10,
            glyph_px=9,
            glyph_py=18,
        ) as terminal:
            terminal.resize(80, 24)
            self.assertEqual(terminal.read_input(), b"")

        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[?2048$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?2048;2$y")

    def test_request_mode_contour_scenario(self):
        for setting, request, expected in (
            (b"\x1b[4h", b"\x1b[4$p", b"\x1b[4;1$y"),
            (b"\x1b[4l", b"\x1b[4$p", b"\x1b[4;2$y"),
            (b"\x1b[1234h", b"\x1b[1234$p", b"\x1b[1234;0$y"),
            (b"\x1b[?6h", b"\x1b[?6$p", b"\x1b[?6;1$y"),
            (b"\x1b[?6l", b"\x1b[?6$p", b"\x1b[?6;2$y"),
            (
                b"\x1b[?65535h",
                b"\x1b[?65535$p",
                b"\x1b[?65535;0$y",
            ),
        ):
            with self.subTest(setting=setting), Shitty(columns=5, rows=5) as terminal:
                terminal.write(setting + request)
                self.assertEqual(terminal.read_input(), expected)

    def test_decnkm_contour_scenario(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[?66h\x1b[?66$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?66;1$y")
            terminal.write(b"\x1b[?66l\x1b[?66$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?66;2$y")
            terminal.write(b"\x1b[?66h\x1b[?66$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?66;1$y")

    def test_decarm_contour_scenario(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[?8$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?8;1$y")
            terminal.write(b"\x1b[?8l\x1b[?8$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?8;2$y")
            terminal.write(b"\x1b[?8h\x1b[?8$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?8;1$y")

    def test_decbkm_contour_scenario(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[?67$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?67;2$y")
            terminal.write(b"\x1b[?67h\x1b[?67$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?67;1$y")
            terminal.write(b"\x1b[?67l\x1b[?67$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?67;2$y")

    def test_peek_into_history_contour_scenario(self):
        with Shitty(columns=3, rows=2, save_lines=5) as terminal:
            terminal.write(b"123\r\n456\r\nABC\r\nDEF")

            self.assertEqual(terminal.all_text(), ("123", "456", "ABC", "DEF"))
            self.assertEqual(terminal.scrollback_state()[0], 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "DEF"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 1))

    def test_capture_buffer_source_contour_scenario(self):
        expected = ("12345", "67890", "ABCDE", "FGHIJ", "KLMNO")
        for requested in range(7):
            with self.subTest(requested=requested), Shitty(
                columns=5,
                rows=2,
                save_lines=5,
            ) as terminal:
                terminal.write(b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO")
                contents = terminal.all_text()
                self.assertEqual(contents, expected)
                count = min(requested, len(expected))
                captured = contents[-count:] if count else ()
                expected_capture = expected[-count:] if count else ()
                self.assertEqual(captured, expected_capture)

    def test_render_into_history_contour_scenario(self):
        expected = (
            ("FGHIJ", "KLMNO"),
            ("ABCDE", "FGHIJ"),
            ("67890", "ABCDE"),
            ("12345", "67890"),
        )
        with Shitty(columns=5, rows=2, save_lines=5) as terminal:
            terminal.write(b"12345\r\n67890\r\nABCDE\r\nFGHIJ\r\nKLMNO")
            self.assertEqual(tuple(terminal.snapshot().lines), expected[0])
            for offset in range(1, 4):
                terminal.wheel_up()
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.view_offset, offset)
                self.assertEqual(tuple(snapshot.lines), expected[offset])

    def test_horizontal_tab_clear_all_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[3gX\tY")
            self.assertEqual(terminal.snapshot().lines[0], "X   Y")
            terminal.write(b"\tZ")
            self.assertEqual(terminal.snapshot().lines[:2], ["X   Y", "Z    "])
            terminal.write(b"\tA")
            self.assertEqual(terminal.snapshot().lines[:2], ["X   Y", "Z   A"])

    def test_horizontal_tab_clear_under_cursor_contour_scenario(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[8G\x1b[g\x1b[1GA\tB")
            self.assertEqual(terminal.snapshot().lines[0], "A       B           ")
            terminal.write(b"\tC")
            self.assertEqual(terminal.snapshot().lines[:2], [
                "A       B       C   ",
                "                    ",
            ])

    def test_horizontal_tab_set_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(
                b"\x1b[3g"
                b"\x1b[3G\x1bH\x1b[5G\x1bH\x1b[8G\x1bH"
                b"\x1b[1G1\t3\t5\t8\tA"
            )
            self.assertEqual(terminal.snapshot().lines[0], "1 3 5  8 A")
            terminal.write(b"\tB\t\t\tC")
            self.assertEqual(terminal.snapshot().lines[:2], [
                "1 3 5  8 A",
                "B      C  ",
            ])

    def test_cursor_backward_tab_fixed_width_contour_scenario(self):
        expected = {
            0: (16, "a       b       X   "),
            1: (16, "a       b       X   "),
            2: (8, "a       X       c   "),
            3: (0, "X       b       c   "),
            4: (0, "X       b       c   "),
        }
        for count, (column, line) in expected.items():
            with self.subTest(count=count), Shitty(columns=20, rows=3) as terminal:
                terminal.write(b"a\tb\tc")
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (17, 0))
                terminal.write(f"\x1b[{count}Z".encode() + b"X")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.cell(column, 0).char, "X")
                self.assertEqual(snapshot.lines[0], line)

    def test_cursor_backward_tab_manual_tabs_contour_scenario(self):
        expected = {
            0: (8, "a   b   X "),
            1: (8, "a   b   X "),
            2: (4, "a   X   c "),
            3: (0, "X   b   c "),
            4: (0, "X   b   c "),
        }
        for count, (column, line) in expected.items():
            with self.subTest(count=count), Shitty(columns=10, rows=3) as terminal:
                terminal.write(
                    b"\x1b[5G\x1bH\x1b[9G\x1bH\x1b[1Ga\tb\tc"
                )
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))
                terminal.write(f"\x1b[{count}Z".encode() + b"X")
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.cell(column, 0).char, "X")
                self.assertEqual(snapshot.lines[0], line)

    def test_search_reverse_source_contour_scenario(self):
        with Shitty(columns=4, rows=3, save_lines=10) as terminal:
            terminal.write_chunks(
                b"1abc", b"2def", b"3ghi", b"4jkl", b"5mno", b"6pqr"
            )
            self.assertEqual(
                terminal.all_text(),
                ("1abc", "2def", "3ghi", "4jkl", "5mno", "6pqr"),
            )
            terminal.write(b"7abcd")
            self.assertEqual(
                terminal.all_text(),
                ("1abc", "2def", "3ghi", "4jkl", "5mno", "6pqr", "7abc", "d"),
            )

    def test_search_smart_case_source_is_codepoint_aware(self):
        with Shitty(columns=10, rows=3, save_lines=10) as terminal:
            terminal.write("Привет".encode())
            self.assertEqual(terminal.all_text(), ("Привет", "", ""))
            snapshot = terminal.model_snapshot()
            self.assertEqual(
                "".join(cell.char for cell in snapshot.cells[:6]),
                "Привет",
            )

    def test_find_marker_downwards_source_contour_scenario(self):
        with Shitty(columns=4, rows=3, save_lines=10) as terminal:
            terminal.write_chunks(
                b"1abc", b"2def", b"3ghi", b"4jkl", b"5mno", b"6pqr"
            )
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(-4, 4)),
                (0,) * 8,
            )

        with Shitty(columns=4, rows=3, save_lines=10) as terminal:
            terminal.write(
                b"\x1b[>M1abc\x1b]133;D\x1b\\\r\n"
                b"2def\r\n"
                b"\x1b[>M3ghi\x1b]133;D\x1b\\\r\n"
                b"\x1b[>M4jkl\x1b]133;D\x1b\\\r\n"
                b"5mno\r\n"
                b"\x1b[>M6pqr"
            )
            self.assertEqual(terminal.scrollback_state()[0], 3)
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(-3, 3)),
                (1, 0, 1, 1, 0, 1),
            )

    def test_find_marker_upwards_source_contour_scenario(self):
        with Shitty(columns=4, rows=3, save_lines=10) as terminal:
            terminal.write_chunks(
                b"1abc", b"2def", b"3ghi", b"4jkl", b"5mno", b"6pqr"
            )
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(-4, 4)),
                (0,) * 8,
            )

        with Shitty(columns=4, rows=3, save_lines=10) as terminal:
            terminal.write(
                b"\x1b[>M1abc\x1b]133;D\x1b\\\r\n"
                b"2def\r\n"
                b"\x1b[>M3ghi\x1b]133;D\x1b\\\r\n"
                b"\x1b[>M4jkl\x1b]133;D\x1b\\\r\n"
                b"5mno\r\n"
                b"\x1b[>M6pqr"
            )
            self.assertEqual(
                tuple(terminal.row_semantic(row) for row in range(-4, 4)),
                (0, 1, 0, 1, 1, 0, 1, 0),
            )

    def test_dectabsr_contour_scenario(self):
        def report(terminal):
            terminal.write(b"\x1b[2$w")
            return terminal.read_input()

        with Shitty(columns=35, rows=2) as terminal:
            self.assertEqual(report(terminal), b"\x1bP2$u9/17/25/33\x1b\\")

        with Shitty(columns=35, rows=2) as terminal:
            terminal.write(b"\x1b[3g")
            self.assertEqual(report(terminal), b"\x1bP2$u\x1b\\")

        with Shitty(columns=35, rows=2) as terminal:
            terminal.write(
                b"\x1b[3g"
                b"\x1b[2G\x1bH\x1b[4G\x1bH"
                b"\x1b[8G\x1bH\x1b[16G\x1bH"
            )
            self.assertEqual(report(terminal), b"\x1bP2$u2/4/8/16\x1b\\")

    def test_save_restore_dec_modes_contour_scenario(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"\x1b[?1001l\x1b[?1001s\x1b[?1001h\x1b[?1001$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?1001;1$y")
            terminal.write(b"\x1b[?1001r\x1b[?1001$p")
            self.assertEqual(terminal.read_input(), b"\x1b[?1001;2$y")

    def test_osc_2_unicode_contour_scenario(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write("\x1b]2;😀\x1b\\".encode())
            self.assertEqual(terminal.window_title(), "😀")

    def test_osc_4_contour_scenario(self):
        cases = (
            (b"\x1b]4;7;rgb:ab/cd/ef\x1b\\", b"abab/cdcd/efef"),
            (b"\x1b]4;7;#abcdef\x1b\\", b"abab/cdcd/efef"),
            (b"\x1b]4;7;#abc\x1b\\", b"a0a0/b0b0/c0c0"),
            (b"\x1b]4;7;rgb:abab/cdcd/efef\x1b\\", b"abab/cdcd/efef"),
        )
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(b"\x1b]4;7;?\x1b\\")
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]4;7;rgb:aaaa/aaaa/aaaa\x1b\\",
            )

        for setting, expected in cases:
            with self.subTest(setting=setting), Shitty(columns=2, rows=2) as terminal:
                terminal.write(setting + b"\x1b]4;7;?\x1b\\")
                self.assertEqual(
                    terminal.read_input(),
                    b"\x1b]4;7;rgb:" + expected + b"\x1b\\",
                )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]4;0;rgb:f0f0/f0f0/f0f0;1;rgb:f0f0/0000/0000\x1b\\"
                b"\x1b]4;0;?;1;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]4;0;rgb:f0f0/f0f0/f0f0\x1b\\"
                b"\x1b]4;1;rgb:f0f0/0000/0000\x1b\\",
            )

    def test_osc_10_through_19_contour_scenario(self):
        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;rgb:f0f0/f0f0/f0f0;rgb:f0f0/0000/0000\x1b\\"
                b"\x1b]10;?;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]10;rgb:f0f0/f0f0/f0f0\x1b\\"
                b"\x1b]11;rgb:f0f0/0000/0000\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]11;rgb:0101/0202/0303;rgb:0404/0505/0606\x1b\\"
                b"\x1b]11;?;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]11;rgb:0101/0202/0303\x1b\\"
                b"\x1b]12;rgb:0404/0505/0606\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;rgb:0f0f/0f0f/0f0f\x1b\\"
                b"\x1b]10;;rgb:f0f0/0000/0000\x1b\\"
                b"\x1b]10;?;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]10;rgb:0f0f/0f0f/0f0f\x1b\\"
                b"\x1b]11;rgb:f0f0/0000/0000\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;rgb:0101/0101/0101;rgb:0202/0202/0202;"
                b"rgb:0303/0303/0303;rgb:0404/0404/0404;"
                b"rgb:0505/0505/0505;rgb:0606/0606/0606;"
                b"rgb:0707/0707/0707;rgb:0808/0808/0808;"
                b"rgb:0909/0909/0909;rgb:0a0a/0a0a/0a0a;"
                b"rgb:0b0b/0b0b/0b0b\x1b\\"
                b"\x1b]10;?\x1b\\\x1b]11;?\x1b\\\x1b]12;?\x1b\\"
                b"\x1b]17;?\x1b\\\x1b]19;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]10;rgb:0101/0101/0101\x1b\\"
                b"\x1b]11;rgb:0202/0202/0202\x1b\\"
                b"\x1b]12;rgb:0303/0303/0303\x1b\\"
                b"\x1b]17;rgb:0808/0808/0808\x1b\\"
                b"\x1b]19;rgb:0a0a/0a0a/0a0a\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;rgb:0b0b/0b0b/0b0b\x1b\\"
                b"\x1b]10;not-a-color;rgb:0c0c/0c0c/0c0c\x1b\\"
                b"\x1b]10;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]10;rgb:0b0b/0b0b/0b0b\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]17;rgb:1111/2222/3333\x1b\\"
                b"\x1b]19;rgb:4444/5555/6666\x1b\\"
                b"\x1b]17;?\x1b\\\x1b]19;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]17;rgb:1111/2222/3333\x1b\\"
                b"\x1b]19;rgb:4444/5555/6666\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]10;rgb:1212/3434/5656\x1b\\"
                b"\x1b]19;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]19;rgb:1212/3434/5656\x1b\\",
            )

        with Shitty(columns=2, rows=2) as terminal:
            terminal.write(
                b"\x1b]17;rgb:1111/2222/3333\x1b\\"
                b"\x1b]117\x1b\\\x1b]17;?\x1b\\"
            )
            self.assertEqual(
                terminal.read_input(),
                b"\x1b]17;rgb:0000/0000/0000\x1b\\",
            )

    def test_xtgettcap_contour_scenario(self):
        expected = {
            b"524742": b"\x1bP1+r524742=38\x1b\\",
            b"636f6c6f7273": b"\x1bP1+r636f6c6f7273=323536\x1b\\",
            b"616d": b"\x1bP0+r616d\x1b\\",
            b"7878": b"\x1bP0+r7878\x1b\\",
        }
        for name, reply in expected.items():
            with self.subTest(name=name), Shitty(columns=2, rows=2) as terminal:
                terminal.write(b"\x1bP+q" + name + b"\x1b\\")
                self.assertEqual(terminal.read_input(), reply)

    def test_set_max_history_line_count_source_contour_scenario(self):
        with Shitty(columns=2, rows=2, save_lines=0) as terminal:
            terminal.write(b"AB\r\nCD")
            self.assertEqual(terminal.all_text(), ("AB", "CD"))
            self.assertEqual(terminal.scrollback_state()[0], 0)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["AB", "CD"])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

    def test_resize_source_contour_scenario(self):
        with Shitty(columns=2, rows=2, save_lines=10) as terminal:
            terminal.write(b"AB\r\nCD")
            terminal.resize(2, 2)
            self.assertEqual(terminal.snapshot().lines, ["AB", "CD"])

        with Shitty(columns=2, rows=2, save_lines=10) as terminal:
            terminal.write(b"AB\r\nCD")
            terminal.resize(2, 3)
            self.assertEqual(terminal.snapshot().lines, ["AB", "CD", "  "])
            terminal.write(b"\r\nE")
            self.assertEqual(terminal.snapshot().lines, ["AB", "CD", "E "])
            terminal.write(b"F")
            self.assertEqual(terminal.snapshot().lines, ["AB", "CD", "EF"])

        resized = {
            (2, 1): (["CD"], ("AB", "CD"), (1, 0)),
            (3, 2): (["AB ", "CD "], ("AB", "CD"), (2, 1)),
            (1, 2): (["C", "D"], ("A", "B", "C", "D"), (0, 1)),
            (3, 3): (["AB ", "CD ", "   "], ("AB", "CD", ""), (2, 1)),
            (1, 3): (["B", "C", "D"], ("A", "B", "C", "D"), (0, 2)),
            (3, 1): (["CD "], ("AB", "CD"), (2, 0)),
            (1, 1): (["D"], ("A", "B", "C", "D"), (0, 0)),
        }
        for (columns, rows), (lines, all_text, cursor) in resized.items():
            with self.subTest(columns=columns, rows=rows), Shitty(
                columns=2,
                rows=2,
                save_lines=10,
            ) as terminal:
                terminal.write(b"AB\r\nCD")
                terminal.resize(columns, rows)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.columns, snapshot.rows), (columns, rows))
                self.assertEqual(snapshot.lines, lines)
                self.assertEqual(terminal.all_text(), all_text)
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), cursor)

        with Shitty(columns=2, rows=2, save_lines=10) as terminal:
            terminal.write(b"AB\r\nCD")
            terminal.resize(3, 2)
            terminal.write(b"Y\x1b[1;3H\x1b7X")
            self.assertEqual(terminal.snapshot().lines, ["ABX", "CDY"])
            terminal.resize(2, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["CD", "Y "])
            self.assertEqual(terminal.all_text(), ("AB", "X", "CD", "Y"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))
            terminal.write(b"\x1b8Z")
            self.assertEqual(terminal.snapshot().lines, ["ZD", "Y "])
            terminal.resize(3, 2)
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABX", "ZDY"])
            self.assertEqual(terminal.all_text(), ("ABX", "ZDY"))
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))

        with Shitty(columns=2, rows=2, save_lines=10) as terminal:
            terminal.write(b"AB\r\nCD")
            terminal.resize(3, 3)
            terminal.write(b"1\r\n234")
            self.assertEqual(terminal.snapshot().lines, ["AB ", "CD1", "234"])

    def test_deccra_down_left_intersecting_contour_scenario(self):
        with Shitty(columns=6, rows=5) as terminal:
            terminal.write(
                b"ABCDEF\r\nabcdef\r\n123456\r\n"
                b"\x1b[43mGHIJKL\r\nghijkl\x1b[0m"
                b"\x1b[4;3;5;6;0;3;2;0$v"
            )
            self.assertEqual(terminal.snapshot().lines, [
                "ABCDEF", "abcdef", "1IJKL6", "GijklL", "ghijkl",
            ])

    def test_deccra_trailing_semicolon_contour_scenario(self):
        with Shitty(columns=6, rows=5) as terminal:
            terminal.write(
                b"ABCDEF\r\nabcdef\r\n123456\r\n"
                b"\x1b[43mGHIJKL\r\nghijkl\x1b[0m"
                b"\x1b[4;3;5;6;0;3;2;0;$v"
            )
            self.assertEqual(terminal.snapshot().lines, [
                "ABCDEF", "abcdef", "1IJKL6", "GijklL", "ghijkl",
            ])

    def test_deccra_right_intersecting_contour_scenario(self):
        with Shitty(columns=6, rows=5) as terminal:
            terminal.write(
                b"ABCDEF\r\nabcdef\r\n123456\r\n"
                b"\x1b[43mGHIJKL\r\nghijkl\x1b[0m"
                b"\x1b[2;2;4;4;0;2;3;0$v"
            )
            self.assertEqual(terminal.snapshot().lines, [
                "ABCDEF", "abbcdf", "122346", "GHHIJL", "ghijkl",
            ])

    def test_deccra_left_intersecting_contour_scenario(self):
        with Shitty(columns=6, rows=5) as terminal:
            terminal.write(
                b"ABCDEF\r\nabcdef\r\n123456\r\n"
                b"GHIJKL\r\nghijkl"
                b"\x1b[2;4;3;6;0;2;3;0$v"
            )
            self.assertEqual(terminal.snapshot().lines, [
                "ABCDEF", "abdeff", "124566", "GHIJKL", "ghijkl",
            ])

    def test_tcap_string_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1bP+q687061\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP0+r687061\x1b\\")

    def test_sixel_simple_source_contour_scenario(self):
        # Contour configures 10x10 pixel cells. Shitty's documented sixel
        # patches are fixed at 6x12 pixels, so the same 100x100 fixture spans
        # 17x9 cells and the cursor ends on its last row.
        with Shitty(columns=18, rows=10, glyph_px=6, glyph_py=12) as terminal:
            terminal.write(contour_checkerboard_sixel())
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 8),
            )
            terminal.present()
            image = terminal.reference_image()
        for row in range(10):
            for column in range(10):
                expected = (255, 255, 255) if (column + row) & 1 else (0, 0, 0)
                self.assertEqual(
                    image_pixel(image, 2 + column * 10 + 5, 2 + row * 10 + 5),
                    expected,
                )

    def test_sixel_auto_scroll_source_contour_scenario(self):
        with Shitty(columns=18, rows=8, glyph_px=6, glyph_py=12) as terminal:
            terminal.write(contour_checkerboard_sixel())
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 7),
            )
            terminal.present()
            image = terminal.reference_image()
        # Nine sixel rows in an eight-row page scroll the first 12 image
        # pixels away. Both sampled white checker squares remain visible.
        self.assertEqual(image_pixel(image, 7, 5), (255, 255, 255))
        self.assertEqual(image_pixel(image, 7, 85), (255, 255, 255))

    def test_sixel_status_line_source_contour_scenario(self):
        # Contour enables its private host status-display API for this case.
        # Shitty has no status-line concept or wire control, so the observable
        # public fallback is an ordinary short page: its final row remains an
        # image row rather than a hidden host reservation.
        with Shitty(columns=18, rows=5, glyph_px=6, glyph_py=12) as terminal:
            terminal.write(contour_checkerboard_sixel())
            self.assertEqual(
                (terminal.snapshot().cursor_x, terminal.snapshot().cursor_y),
                (0, 4),
            )
            terminal.present()
            image = terminal.reference_image()
        self.assertEqual(image_pixel(image, 7, 45), (255, 255, 255))

    def test_decstr_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1b[?69h\x1b[2;4s\x1b[?69$p"
                b"\x1b[!p\x1b[?69$p\x1b[?69h\x1b[2;4sX"
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b[?69;1$y\x1b[?69;2$y"
            )
            self.assertEqual(terminal.snapshot().lines[0], "X    ")

    def test_dectst_source_contour_scenario(self):
        # Contour treats the power-up test as a reset. xterm, Kitty and
        # Ghostty do not implement DECTST, so the common observable behavior
        # is an ignored sequence with no reply.
        for sequence in (
            b"\x1b[2;1y",
            b"\x1b[4;1y",
            b"\x1b[2;0y",
            b"\x1b[2;2y",
            b"\x1b[2y",
            b"\x1b[3;1y",
            b"\x1b[2;1;42y",
        ):
            with self.subTest(sequence=sequence), Shitty(columns=10, rows=4) as terminal:
                terminal.write(b"ABCD" + sequence)
                self.assertEqual(terminal.snapshot().lines[0], "ABCD      ")
                self.assertEqual(terminal.read_input(), b"")

    def test_sgrsave_and_sgrrestore_source_contour_scenario(self):
        with Shitty(columns=4, rows=2) as terminal:
            terminal.write(
                b"\x1b[31;42;4m\x1b[#{\x1b[33;44;24mA\x1b[#}B"
            )
            changed = terminal.snapshot().cell(0, 0)
            restored = terminal.snapshot().cell(1, 0)
            self.assertEqual(
                (changed.foreground, changed.background, changed.underline),
                ((170, 85, 0), (0, 0, 170), False),
            )
            self.assertEqual(
                (restored.foreground, restored.background, restored.underline),
                ((170, 0, 0), (0, 170, 0), True),
            )

    def test_ls1_and_ls0_source_contour_scenario(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"ab\x1b)0\x0eab\x0fab")
            self.assertEqual(terminal.snapshot().lines[0], "ab▒␉ab  ")

    def test_ls2_and_ls3_source_contour_scenario(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(b"\x1b*0\x1b+0\x1bnq\x1box\x0fq")
            self.assertEqual(terminal.snapshot().lines[0], "─│q     ")

    def test_ls1r_ls2r_ls3r_source_contour_scenario(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b)0\x1b*B\x1b+0"
                b"\x1b~\xf1\x1b}\xf1\x1b|\xf1q"
            )
            self.assertEqual(terminal.snapshot().lines[0], "─�─q    ")

    def test_scs_96_charset_designation_source_contour_scenario(self):
        with Shitty(columns=8, rows=2) as terminal:
            terminal.write(
                b"\x1b-A\x1b~\xa3"
                b"\x1b.A\x1b}\xa3"
                b"\x1b/A\x1b|\xa3"
                b"\x1b)B\x1b~\xa3"
            )
            self.assertEqual(terminal.snapshot().lines[0], "£££�    ")

    def test_decrqupss_default_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            self.assertEqual(request_upss(terminal), b"\x1bP0!u%5\x1b\\")

    def test_decaupss_round_trips_table_source_contour_scenario(self):
        cases = (
            (0, b"%5"), (0, b'"?'), (0, b'"4'), (0, b"%0"),
            (0, b"&4"), (1, b"A"), (1, b"B"), (1, b"F"),
            (1, b"H"), (1, b"L"), (1, b"M"),
        )
        for size, designator in cases:
            with self.subTest(size=size, designator=designator), Shitty(
                columns=10, rows=3
            ) as terminal:
                assign_upss(terminal, size, designator)
                self.assertEqual(
                    request_upss(terminal),
                    b"\x1bP" + str(size).encode() + b"!u" + designator + b"\x1b\\",
                )

    def test_decaupss_size_selects_charset_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 0, b"A")
            self.assertEqual(request_upss(terminal), b"\x1bP0!uA\x1b\\")
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 1, b"A")
            self.assertEqual(request_upss(terminal), b"\x1bP1!uA\x1b\\")
            assign_upss(terminal, 1, b"%5")
            self.assertEqual(request_upss(terminal), b"\x1bP1!uA\x1b\\")

    def test_decaupss_omitted_size_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 1, b"A")
            terminal.write(b"\x1bP!u>\x1b\\")
            self.assertEqual(request_upss(terminal), b"\x1bP0!u>\x1b\\")

    def test_decaupss_unknown_designator_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 0, b"ZZ")
            self.assertEqual(request_upss(terminal), b"\x1bP0!u%5\x1b\\")

    def test_decaupss_conformance_source_contour_scenario(self):
        # xterm-410's decode_upss only gates the feature at VT320; its table's
        # per-set min_level fields are not consulted. Contour's stricter
        # VT500-only expectation for DEC Greek is therefore not the oracle.
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[63;1\"p")
            assign_upss(terminal, 0, b'"?')
            self.assertEqual(request_upss(terminal), b"\x1bP0!u\"?\x1b\\")
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[61\"p")
            self.assertEqual(request_upss(terminal), b"\x1bP0!u%5\x1b\\")

    def test_upss_survives_screen_and_cursor_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 1, b"A")
            terminal.write(b"\x1b[?1049h")
            self.assertEqual(request_upss(terminal), b"\x1bP1!uA\x1b\\")
            terminal.write(b"\x1b[?1049l\x1b7")
            assign_upss(terminal, 0, b">")
            terminal.write(b"\x1b8")
            self.assertEqual(request_upss(terminal), b"\x1bP0!u>\x1b\\")

    def test_upss_resets_source_contour_scenario(self):
        for reset in (b"\x1b[!p", b"\x1bc"):
            with self.subTest(reset=reset), Shitty(columns=10, rows=3) as terminal:
                assign_upss(terminal, 1, b"A")
                terminal.write(reset)
                self.assertEqual(request_upss(terminal), b"\x1bP0!u%5\x1b\\")

    def test_scs_user_preferred_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            assign_upss(terminal, 0, b">")
            terminal.write(b"\x1b(<q")
            self.assertEqual(terminal.snapshot().lines[0], "ψ         ")

    def test_horizontal_tab_fills_cells_source_contour_scenario(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"A\tB")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "A       B           ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))

    def test_horizontal_tab_after_bulk_text_source_contour_scenario(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write_chunks(b"AB", b"\t", b"CD")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "AB      CD          ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (10, 0))

    def test_horizontal_tab_multiple_source_contour_scenario(self):
        with Shitty(columns=25, rows=2) as terminal:
            terminal.write(b"A\tB\tC")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "A       B       C        ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (17, 0))

    def test_horizontal_tab_chunk_boundary_source_contour_scenario(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write_chunks(b"AB", b"C\t", b"D")
            self.assertEqual(terminal.snapshot().lines[0], "ABC     D           ")

    def test_horizontal_tab_after_clear_source_contour_scenario(self):
        with Shitty(columns=20, rows=2) as terminal:
            terminal.write(b"Hello World\x1b[2J\x1b[HX\tY")
            self.assertEqual(terminal.snapshot().lines[0], "X       Y           ")

    def test_deccir_default_state_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;0;2;@;BBBB\x1b\\")

    def test_deccir_cursor_position_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[3;7H")
            self.assertEqual(deccir(terminal), b"\x1bP1$u3;7;1;@;@;@;0;2;@;BBBB\x1b\\")

    def test_deccir_bold_underline_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1;4m")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;C;@;@;0;2;@;BBBB\x1b\\")

    def test_deccir_blink_inverse_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[5;7m")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;L;@;@;0;2;@;BBBB\x1b\\")

    def test_deccir_all_rendition_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1;4;5;7m")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;O;@;@;0;2;@;BBBB\x1b\\")

    def test_deccir_protection_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[1\"q")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;A;@;0;2;@;BBBB\x1b\\")

    def test_deccir_origin_mode_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[?6h")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;A;0;2;@;BBBB\x1b\\")

    def test_deccir_wrap_pending_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"ABCDE")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;5;1;@;@;H;0;2;@;BBBB\x1b\\")

    def test_deccir_charset_special_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b(0")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;0;2;@;0BBB\x1b\\")

    def test_deccir_charset_g1_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b)0")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;0;2;@;B0BB\x1b\\")

    def test_deccir_gl_locking_shift_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x0e")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;1;2;@;BBBB\x1b\\")

    def test_deccir_gr_locking_shift_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b|")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;0;3;@;BBBB\x1b\\")

    def test_deccir_96_charset_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b-A")
            self.assertEqual(deccir(terminal), b"\x1bP1$u1;1;1;@;@;@;0;2;B;BABB\x1b\\")

    def test_multipage_np_pp_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"Hello\x1b[1UWorld\x1b[1V")
            self.assertEqual(terminal.snapshot().lines, ["Hello", "World", "     "])

    def test_multipage_np_pp_clamping_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"A\x1b[100U\x1b[100VB")
            self.assertEqual(terminal.snapshot().lines[0], "AB   ")

    def test_multipage_never_alternate_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"main\x1b[100U")
            self.assertEqual(terminal.snapshot().lines[0], "main ")

    def test_multipage_ppa_ppr_ppb_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[5 P\x1b[2 Q\x1b[3 R\x1b[1 PX")
            self.assertEqual(terminal.snapshot().lines[1], "  X  ")

    def test_multipage_decpccm_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[?64l\x1b[5 P\x1b[?64hA")
            self.assertEqual(terminal.snapshot().lines[0], "A    ")

    def test_multipage_decrqde_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[\"v")
            self.assertEqual(terminal.read_input(), b"\x1b[5;10;1;1;1\"w")

    def test_multipage_decxcpr_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;3H\x1b[?6n")
            self.assertEqual(terminal.read_input(), b"\x1b[?2;3;1R")

    def test_multipage_deccir_page_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[3 P")
            self.assertTrue(deccir(terminal).startswith(b"\x1bP1$u1;1;1;"))

    def test_multipage_save_restore_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[3 P\x1b[2;3H\x1b7\x1b[1 P\x1b[H\x1b8X")
            self.assertEqual(terminal.snapshot().lines[1][2], "X")

    def test_multipage_restore_without_save_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[4 P\x1b[3;4H\x1b8X")
            self.assertEqual(terminal.snapshot().lines[0][0], "X")

    def test_multipage_cross_page_deccra_source_contour_scenario(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"ABCDE\x1b[2 P\x1b[1;1;1;5;1;2;1;2$v")
            self.assertEqual(terminal.snapshot().lines[1][:5], "ABCDE")

    def test_multipage_alternate_compatibility_source_contour_scenario(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"Prima\x1b[?1049hAlt!!\x1b[?1049l")
            self.assertEqual(terminal.snapshot().lines[0], "Prima")

    def test_multipage_hard_reset_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[3 PTest!\x1bc")
            self.assertEqual(terminal.snapshot().lines, ["     ", "     "])

    def test_multipage_content_isolation_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"Page1\x1b[1UPage2\x1b[1UPage3\x1b[1 P")
            self.assertEqual(terminal.all_text(), ("Page1", "Page2", "Page3"))

    def test_multipage_per_page_margins_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[2 P\x1b[3;5r\x1b[1 P\x1b[2;1H\n")
            self.assertEqual(terminal.snapshot().lines[3], "          ")

    def test_multipage_alt_margin_copy_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[?1049h\x1b[1;5r\x1b[?1049l\x1b[4;1H\n")
            self.assertEqual(terminal.snapshot().lines[1], "          ")

    def test_multipage_resize_margins_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r")
            terminal.resize(10, 6)
            terminal.write(b"\x1b[6;1H\n")
            self.assertEqual(terminal.snapshot().lines[-1], "          ")

    def test_multipage_reset_margins_source_contour_scenario(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1bc\x1b[5;1H\n")
            self.assertEqual(terminal.snapshot().lines[-1], "          ")

    def test_rep_basic_ascii_source_contour_scenario(self):
        with Shitty(columns=20, rows=1) as terminal:
            terminal.write(b"|\x1b[9b")
            self.assertEqual(terminal.snapshot().lines[0], "||||||||||          ")

    def test_rep_omitted_parameter_source_contour_scenario(self):
        with Shitty(columns=8, rows=1) as terminal:
            terminal.write(b"X\x1b[b")
            self.assertEqual(terminal.snapshot().lines[0], "XX      ")

    def test_rep_zero_parameter_source_contour_scenario(self):
        with Shitty(columns=8, rows=1) as terminal:
            terminal.write(b"X\x1b[0b")
            self.assertEqual(terminal.snapshot().lines[0], "XX      ")

    def test_rep_after_bulk_text_source_contour_scenario(self):
        with Shitty(columns=20, rows=1) as terminal:
            terminal.write_chunks(b"Hello", b"|\x1b[3b")
            self.assertEqual(terminal.snapshot().lines[0], "Hello||||           ")

    def test_rep_left_right_margin_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[?69h\x1b[2;4s\x1b[1;2Ha\x1b[3b")
            self.assertEqual(terminal.snapshot().lines, [" aaa ", " a   "])

    def test_rep_bottom_margin_source_contour_scenario(self):
        with Shitty(columns=6, rows=5) as terminal:
            terminal.write(b"\x1b[2;4r\x1b[4;4Ha\x1b[3b")
            self.assertEqual(terminal.snapshot().lines, ["      ", "      ", "   aaa", "a     ", "      "])

    def test_rep_without_character_source_contour_scenario(self):
        with Shitty(columns=10, rows=1) as terminal:
            terminal.write(b"\x1b[5b")
            self.assertEqual(terminal.snapshot().lines[0], "          ")

    def test_ht_preserves_existing_content_source_contour_scenario(self):
        with Shitty(columns=20, rows=1) as terminal:
            terminal.write(b"ABCDEFGHIJKLMNOPQRST\x1b[1;3H\tX")
            self.assertEqual(terminal.snapshot().lines[0], "ABCDEFGHXJKLMNOPQRST")

    def test_da1_level_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[c")
            self.assertEqual(
                terminal.read_input(), b"\x1b[?64;1;2;4;6;8;9;15;21;22;28;29c"
            )

    def test_da1_extensions_source_contour_scenario(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[c")
            values = set(map(int, terminal.read_input()[3:-1].split(b";")))
            self.assertEqual(values, {1, 2, 4, 6, 8, 9, 15, 21, 22, 28, 29, 64})

    def test_decscl_da1_reports_the_device_capability_level(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[62;1\"p\x1b[c")
            self.assertEqual(
                terminal.read_input(), b"\x1b[?64;1;2;4;6;8;9;15;21;22;28;29c"
            )

    def test_decscl_level_62_keeps_da1_as_a_device_descriptor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[62;1\"p\x1b[c")
            values = set(map(int, terminal.read_input()[3:-1].split(b";")))
            self.assertEqual(values, {1, 2, 4, 6, 8, 9, 15, 21, 22, 28, 29, 64})

    def test_decscl_level_63_keeps_da1_as_a_device_descriptor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[63;1\"p\x1b[c")
            values = set(map(int, terminal.read_input()[3:-1].split(b";")))
            self.assertNotIn(11, values)

    def test_decscl_level_64_keeps_da1_as_a_device_descriptor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[64;1\"p\x1b[c")
            values = set(map(int, terminal.read_input()[3:-1].split(b";")))
            self.assertIn(28, values)

    def test_decscl_level_65_round_trips_through_decrqss(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[62;1\"p\x1b[65;1\"p\x1bP$q\"p\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r65;1\"p\x1b\\")

    def test_decscl_resets_the_screen_and_saved_cursor(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"x\x1b[2;4H\x1b7\x1b[61;1\"p\x1b8")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["     ", "     "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

    def test_decscl_c1_mode_7_bit(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[65;1\"p\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")

    def test_decscl_c1_mode_8_bit(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[65;0\"p\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x9b1;1R")

    def test_decscl_c1_mode_8_bit_with_ps2_2(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[65;2\"p\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x9b1;1R")

    def test_decscl_level_61_forces_7_bit_c1(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[61;0\"p\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[1;1R")

    def test_decscl_decrqss_reports_the_selected_level(self):
        with Shitty(columns=5, rows=2) as terminal:
            terminal.write(b"\x1b[64;1\"p\x1bP$q\"p\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x1bP1$r64;1\"p\x1b\\")

    def test_c1_folding_is_observable_on_csi_dcs_and_osc_responses(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b G\x1b[3;4H\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x9b3;4R")

            terminal.write(b"\x1b[5;6r\x1bP$qr\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x901$r5;6r\x9c")

            terminal.write(b"\x1b]10;?\x1b\\")
            self.assertEqual(
                terminal.read_input(), b"\x9d10;rgb:ffff/ffff/ffff\x9c"
            )

    def test_s8c1t_decrqss_reply_uses_eight_bit_controls(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[5;6r\x1b G\x1bP$qr\x1b\\")
            self.assertEqual(terminal.read_input(), b"\x901$r5;6r\x9c")

    def test_s8c1t_reverts_to_seven_bit_after_vt52_round_trip(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b G\x1b[3;4H\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x9b3;4R")

            terminal.write(b"\x1b[?2l\x1b<\x1b[6n")
            self.assertEqual(terminal.read_input(), b"\x1b[3;4R")

    def test_decscl_reset_clears_insert_mode_and_saved_cursor(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(
                b"x\x1b[3;4H\x1b7\x1b[4h\x1b[61\"p"
                b"\x1b8\x1b[1;1Ha\x1b[1;1Hb"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "b         ")
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))

    def test_decrqcra_answers_at_vt100_operating_level(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[61\"p\x1b[1;1;1;1;1;1*y")
            reply = terminal.read_input()
            self.assertTrue(reply.startswith(b"\x1bP1!~"))
            self.assertTrue(reply.endswith(b"\x1b\\"))

    def test_xtsmtitle_hex_utf8_set_and_query_modes(self):
        with Shitty(
            columns=10,
            rows=4,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.write(
                b"\x1b[>2;1T\x1b[>0;3t"
                b"\x1b]2;6162\x1b\\\x1b[21t"
            )
            self.assertEqual(terminal.read_input(), b"\x1b]lab\x1b\\")

            terminal.write(
                b"\x1b[>0;3T\x1b[>2;1t"
                b"\x1b]1;ab\x1b\\\x1b]2;ab\x1b\\"
                b"\x1b[20t\x1b[21t"
            )
            self.assertEqual(
                terminal.read_input(), b"\x1b]L6162\x1b\\\x1b]l6162\x1b\\"
            )

            terminal.write(b"\x1b[>T\x1b]2;cd\x1b\\\x1b[21t")
            self.assertEqual(terminal.read_input(), b"\x1b]lcd\x1b\\")

            terminal.write(b"\x1b[>1t\x1bc\x1b]2;ef\x1b\\\x1b[21t")
            self.assertEqual(terminal.read_input(), b"\x1b]lef\x1b\\")

    def test_decset_41_tab_honors_pending_wrap(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[?7h\x1b[?41hxxxxxxxxxx\t")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (8, 1))
            self.assertFalse(terminal.cursor_pending_wrap())

        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[?7hxxxxxxxxxx\t")
            snapshot = terminal.snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 0))
            self.assertTrue(terminal.cursor_pending_wrap())

    def test_osc52_clipboard_write_and_gated_read(self):
        with Shitty(
            columns=20,
            rows=3,
            extra_arguments=("-allowOsc52Read", "true"),
        ) as terminal:
            terminal.write(b"\x1b]52;;dGVzdGluZyAxMjM=\x1b\\\x1b]52;;?\x1b\\")
            self.assertEqual(
                terminal.read_input(), b"\x1b]52;s0;dGVzdGluZyAxMjM=\x1b\\"
            )

        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b]52;;dGVzdGluZyAxMjM=\x1b\\\x1b]52;;?\x1b\\")
            self.assertEqual(terminal.read_input(), b"")

    def test_osc_110_111_reset_dynamic_colors_to_defaults(self):
        for query, override, reset in (
            (b"10", b"#aaaabbbbcccc", b"110"),
            (b"11", b"#111122223333", b"111"),
        ):
            with self.subTest(query=query), Shitty(columns=10, rows=3) as terminal:
                terminal.write(b"\x1b]" + query + b";?\x1b\\")
                original = terminal.read_input()

                terminal.write(b"\x1b]" + query + b";" + override + b"\x1b\\")
                terminal.write(b"\x1b]" + query + b";?\x1b\\")
                self.assertNotEqual(terminal.read_input(), original)

                terminal.write(b"\x1b]" + reset + b"\x1b\\")
                terminal.write(b"\x1b]" + query + b";?\x1b\\")
                self.assertEqual(terminal.read_input(), original)

    def test_decdmac_simple_definition_and_invocation_are_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0!zHello\x1b\\\x1b[0*zX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdmac_vt_sequence_aborts_unknown_dcs_and_recovers(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP1;0;0!z\x1b[1mBold\x1b\\\x1b[1*zX")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[0], "BoldX               ")
            self.assertTrue(snapshot.cell(0, 0).bold)

    def test_decdmac_hex_body_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP2;0;1!z4869\x1b\\\x1b[2*zX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdmac_delete_all_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP0;0;0!zFirst\x1b\\"
                b"\x1bP5;1;0!zSecond\x1b\\\x1b[0*z\x1b[5*zX"
            )
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdmac_redefinition_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0!zOld\x1b\\\x1bP0;0;0!zNew\x1b\\\x1b[0*zX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdmac_64_definition_boundary_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP0;0;0!zM0\x1b\\"
                b"\x1bP63;0;0!zM63\x1b\\"
                b"\x1bP64;0;0!zBad\x1b\\"
                b"\x1b[0*z\x1b[63*z\x1b[64*zX"
            )
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decinvm_undefined_macro_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[42*zX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decinvm_nested_macro_sequence_aborts_unknown_dcs_and_recovers(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP1;0;0!zB\x1b\\"
                b"\x1bP0;0;0!zA\x1b[1*zC\x1b\\\x1b[0*zX"
            )
            self.assertEqual(terminal.snapshot().lines[0], "CX                  ")

    def test_decinvm_recursive_macro_stream_recovers(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0!z\x1b[0*z\x1b\\\x1b[0*zOK")
            self.assertEqual(terminal.snapshot().lines[0], "OK                  ")

    def test_decdmac_empty_body_is_ignored(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP3;0;0!z\x1b\\\x1b[3*zX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdmac_extension_32_is_not_advertised_at_any_level(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[c\x1b[62;1\"p\x1b[c")
            first, second = terminal.read_input().split(b"c")[:2]
            self.assertNotIn(b";32", first)
            self.assertNotIn(b";32", second)

    def test_decudk_programs_single_function_key(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;1|17/48656C6C6F\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"Hello")

    def test_decudk_programs_multiple_function_keys(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;1|17/41;18/42\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A")
            terminal.key("F7")
            self.assertEqual(terminal.read_input(), b"B")

    def test_decudk_clear_before_loading_discards_old_definition(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP1;1|17/41\x1b\\\x1bP0;1|18/42\x1b\\")
            terminal.key("F6")
            self.assertNotEqual(terminal.read_input(), b"A")
            terminal.key("F7")
            self.assertEqual(terminal.read_input(), b"B")

    def test_decudk_keep_existing_preserves_old_definition(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP1;1|17/41\x1b\\\x1bP1;1|18/42\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A")
            terminal.key("F7")
            self.assertEqual(terminal.read_input(), b"B")

    def test_decudk_lock_prevents_later_reprogramming(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0|17/41\x1b\\\x1bP0;0|17/42\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A")

    def test_decudk_hex_decodes_to_function_key_input(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;1|17/1B5B316D\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"\x1b[1m")

    def test_decudk_soft_reset_preserves_function_key_definition(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;1|17/41\x1b\\\x1b[!p")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"A")

    def test_decudk_extension_8_stays_advertised_after_decscl(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[c\x1b[62;1\"p\x1b[c")
            first, second = terminal.read_input().split(b"c")[:2]
            self.assertIn(b";8", first)
            self.assertIn(b";8", second)

    def test_decudk_key_id_17_maps_to_f6_but_not_f5(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;1|17/74657374\x1b\\")
            terminal.key("F6")
            self.assertEqual(terminal.read_input(), b"test")
            terminal.key("F5")
            self.assertNotEqual(terminal.read_input(), b"test")

    def test_nrcs_british_designation_replaces_hash(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b(A#")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "£")

    def test_nrcs_german_designation_replaces_left_bracket(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b(K[")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "Ä")

    def test_nrcs_french_designation_replaces_hash(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b(R#")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "£")

    def test_nrcs_usascii_designation_stops_replacement(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b(A#\x1b(B#")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "£")
            self.assertEqual(snapshot.cell(1, 0).char, "#")

    def test_nrcs_g1_designation_works_after_locking_shift(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b)A\x0e#")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "£")

    def test_nrcs_advertises_extension_9_in_da1(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[c")
            self.assertIn(b";9", terminal.read_input())

    def test_nrcs_two_byte_drcs_designator_is_consumed(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b) AOK")
            self.assertEqual(terminal.snapshot().lines[0], "OK                  ")

    def test_nrcs_g2_designation_works_with_single_shift(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[?42h\x1b*A\x1bN#")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "£")

    def test_dec_technical_charset_maps_a_to_proportional_to(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b(>A")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "∝")

    def test_dec_technical_charset_maps_p_to_pi(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b(>p")
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "π")

    def test_dec_technical_charset_usascii_restores_plain_letters(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b(>A\x1b(BA")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.cell(0, 0).char, "∝")
            self.assertEqual(snapshot.cell(1, 0).char, "A")

    def test_dec_technical_charset_extension_15_stays_advertised_after_decscl(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[c\x1b[62;1\"p\x1b[c")
            first, second = terminal.read_input().split(b"c")[:2]
            self.assertIn(b";15", first)
            self.assertIn(b";15", second)

    def test_decelr_enables_character_cell_locator_report(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[0'|")
            self.assertEqual(terminal.read_input(), b"\x1b[1;0;2;4;0&w")

    def test_decelr_disable_makes_locator_unavailable(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[0;2'z\x1b[0'|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")

    def test_decelr_one_shot_disables_after_first_position_report(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[2;2'z\x1b[0'|\x1b[0'|")
            first, second = terminal.read_input().split(b"\x1b", 2)[1:]
            self.assertEqual(b"\x1b" + first, b"\x1b[1;0;2;4;0&w")
            self.assertEqual(b"\x1b" + second, b"\x1b[0&w")

    def test_decelr_pixel_coordinates_are_reported_in_pixels(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;1'z\x1b[0'|")
            self.assertEqual(terminal.read_input(), b"\x1b[1;0;20;40;0&w")

    def test_decsle_can_select_button_up_without_button_down(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[2;3'{")
            terminal.locator_button(1, True)
            self.assertEqual(terminal.read_input(), b"")
            terminal.locator_button(1, False)
            self.assertEqual(terminal.read_input(), b"\x1b[3;0;2;4;0&w")

    def test_decrqlp_reports_unavailable_when_locator_is_disabled(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[0'|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")

    def test_decelr_soft_reset_disables_locator(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.locator_position(4, 2, 40, 20)
            terminal.write(b"\x1b[1;2'z\x1b[!p\x1b[0'|")
            self.assertEqual(terminal.read_input(), b"\x1b[0&w")

    def test_dec_locator_advertises_extension_29_in_da1(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(b"\x1b[c")
            self.assertIn(b";29", terminal.read_input())

    def test_decdld_single_glyph_definition_is_ignored_without_screen_leak(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0;10;10;0;20;0{A@\x1b\\X")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdld_erase_control_stream_is_ignored_without_screen_leak(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP0;0;0;10;10;0;20;0{A@\x1b\\"
                b"\x1bP0;0;0;10;10;0;20;0{B@\x1b\\X"
            )
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdld_multiple_glyph_stream_is_ignored_without_screen_leak(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0;10;10;0;20;0{A@;A\x1b\\X")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdld_then_decstr_recovers_cleanly(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1bP0;0;0;10;10;0;20;0{A@\x1b\\\x1b[!pX")
            self.assertEqual(terminal.snapshot().lines[0], "X                   ")

    def test_decdld_does_not_advertise_unimplemented_extension_7(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[c")
            self.assertNotIn(b";7", terminal.read_input())

    def test_decdld_designation_falls_back_to_plain_character_cell(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP1;0;0;10;10;0;20;0{ A@\x1b\\"
                b"\x1b) A\x0e!\x0f"
            )
            self.assertEqual(terminal.snapshot().cell(0, 0).char, "!")

    def test_decdld_switching_back_to_g0_keeps_plain_text_visible(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(
                b"\x1bP1;0;0;10;10;0;20;0{ A@\x1b\\"
                b"\x1b) A\x0e!\x0fX"
            )
            self.assertEqual(terminal.snapshot().lines[0], "!X                  ")

    def test_decaln_fills_entire_page_with_es(self):
        with Shitty(columns=4, rows=3) as terminal:
            terminal.write(b"\x1b#8")
            self.assertEqual(terminal.snapshot().lines, ["EEEE", "EEEE", "EEEE"])

    def test_decaln_fills_page_after_history_ring_wrap(self):
        with Shitty(columns=4, rows=3, save_lines=2) as terminal:
            for _ in range(6):
                terminal.write(b"x\r\n")
            terminal.write(b"\x1b#8")
            self.assertEqual(terminal.snapshot().lines, ["EEEE", "EEEE", "EEEE"])

    def test_vpr_moves_down_keeps_column_and_clamps_to_page(self):
        for sequence, expected_y in ((b"\x1b[e", 2), (b"\x1b[2e", 3), (b"\x1b[99e", 4)):
            with self.subTest(sequence=sequence), Shitty(columns=5, rows=5) as terminal:
                terminal.write(b"\x1b[2;3H" + sequence)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.cursor_x, 2)
                self.assertEqual(snapshot.cursor_y, expected_y)

    def test_bulk_text_with_autowrap_disabled(self):
        for suffix, expected in (
            (b"CD", "abCD "),
            (b"CDE", "abCDE"),
            (b"CDEF", "abCDF"),
        ):
            with self.subTest(suffix=suffix), Shitty(
                columns=5,
                rows=3,
                save_lines=2,
            ) as terminal:
                terminal.write_chunks(b"\x1b[?7l", b"a", b"b", suffix)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[:2], [expected, "     "])
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (4, 0),
                )

    def test_autowrap_fills_three_identical_lines_without_a_gap(self):
        with Shitty(columns=10, rows=6) as terminal:
            terminal.write(b"\x1b[H\x1b[?7h")
            terminal.write_chunks(*(b"*" for _ in range(20)))
            terminal.write(b"\x1b[?7l\x1b[3;1H")
            terminal.write_chunks(*(b"*" for _ in range(20)))
            terminal.write(b"\x1b[?7h")

            self.assertEqual(
                terminal.snapshot().lines[:4],
                ["*" * 10, "*" * 10, "*" * 10, " " * 10],
            )

    def test_bulk_text_stops_before_and_exactly_at_right_edge(self):
        for suffix, expected, cursor_x, pending in (
            (b"CD", "abCD ", 4, False),
            (b"CDE", "abCDE", 4, True),
        ):
            with self.subTest(suffix=suffix), Shitty(
                columns=5,
                rows=3,
                save_lines=2,
            ) as terminal:
                terminal.write_chunks(b"a", b"b", suffix)
                snapshot = terminal.snapshot()
                self.assertEqual(snapshot.lines[0], expected)
                self.assertEqual(
                    (snapshot.cursor_x, snapshot.cursor_y),
                    (cursor_x, 0),
                )
                self.assertEqual(terminal.cursor_pending_wrap(), pending)

                if pending:
                    terminal.write(b"F")
                    snapshot = terminal.snapshot()
                    self.assertEqual(snapshot.lines[:2], ["abCDE", "F    "])
                    self.assertEqual(
                        (snapshot.cursor_x, snapshot.cursor_y),
                        (1, 1),
                    )

    def test_bulk_text_wraps_one_character_onto_the_next_line(self):
        with Shitty(columns=5, rows=3, save_lines=2) as terminal:
            terminal.write_chunks(b"a", b"b", b"CDEF")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines[:2], ["abCDE", "F    "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 1))
            self.assertFalse(terminal.cursor_pending_wrap())

    def test_bulk_text_wraps_across_page_and_history(self):
        cases = (
            (
                3,
                10,
                1,
                (b"a", b"b", b"CDEFGHIJABcdefghij01234"),
                ("abCDEFGHIJ", "ABcdefghij", "01234"),
                (5, 2),
                False,
            ),
            (
                3,
                10,
                1,
                (
                    b"a",
                    b"b",
                    b"CDEFGHIJABCDEFGHIJabcdefghij01234",
                ),
                ("abCDEFGHIJ", "ABCDEFGHIJ", "abcdefghij", "01234"),
                (5, 2),
                False,
            ),
            (
                2,
                10,
                1,
                (b"ABCDEFGHIJKLMNOPQRSTabcdefghij0123456789",),
                (
                    "KLMNOPQRST",
                    "abcdefghij",
                    "0123456789",
                ),
                (9, 1),
                True,
            ),
        )
        for rows, columns, history, chunks, expected, cursor, pending in cases:
            with self.subTest(chunks=chunks), Shitty(
                columns=columns,
                rows=rows,
                save_lines=history,
            ) as terminal:
                terminal.write_chunks(*chunks)
                self.assertEqual(terminal.all_text(), expected)
                snapshot = terminal.snapshot()
                self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), cursor)
                self.assertEqual(terminal.cursor_pending_wrap(), pending)

    def test_full_page_defers_scroll_until_the_next_character(self):
        with Shitty(columns=10, rows=3, save_lines=2) as terminal:
            terminal.write(
                b"0123456789"
                b"abcdefghij"
                b"ABCDEFGHIJ"
            )
            snapshot = terminal.snapshot()
            self.assertEqual(
                snapshot.lines,
                ["0123456789", "abcdefghij", "ABCDEFGHIJ"],
            )
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (9, 2))
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(b"X")
            self.assertEqual(
                terminal.all_text(),
                ("0123456789", "abcdefghij", "ABCDEFGHIJ", "X"),
            )
            self.assertEqual(
                terminal.snapshot().lines,
                ["abcdefghij", "ABCDEFGHIJ", "X         "],
            )

    def test_enabling_autowrap_preserves_the_right_edge_position(self):
        with Shitty(columns=3, rows=1, save_lines=1) as terminal:
            terminal.write(b"\x1b[?7l")
            terminal.write_chunks(b"A", b"B", b"C", b"D")
            self.assertEqual(terminal.snapshot().lines, ["ABD"])

            terminal.write(b"\x1b[?7hE")
            self.assertEqual(terminal.snapshot().lines, ["ABE"])
            self.assertTrue(terminal.cursor_pending_wrap())

            terminal.write(b"F")
            self.assertEqual(terminal.all_text(), ("ABE", "F"))
            self.assertEqual(terminal.snapshot().lines, ["F  "])

    def test_cr_lf_with_autowrap_disabled(self):
        with Shitty(columns=3, rows=2) as terminal:
            terminal.write(b"\x1b[?7lABC")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))

            terminal.write(b"\r")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 0))

            terminal.write(b"\n")
            snapshot = terminal.snapshot()
            self.assertEqual(snapshot.lines, ["ABC", "   "])
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (0, 1))

    def test_mode_2027_gates_streaming_cluster_width_revision(self):
        with Shitty(columns=5, rows=1) as terminal:
            terminal.write_chunks(
                b"\x1b[?2027l",
                "ℹ".encode(),
                "️".encode(),
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (1, 0))
            self.assertEqual(
                snapshot.cell(0, 0).grapheme,
                (0x2139, 0xFE0F),
            )
            self.assertFalse(snapshot.cell(0, 0).double_width)

    def test_mode_2027_width_revision_resumes_when_reenabled(self):
        with Shitty(columns=5, rows=1) as terminal:
            terminal.write_chunks(
                b"\x1b[?2027l\x1b[?2027h",
                "ℹ".encode(),
                "️".encode(),
            )
            snapshot = terminal.model_snapshot()
            self.assertEqual((snapshot.cursor_x, snapshot.cursor_y), (2, 0))
            self.assertEqual(
                snapshot.cell(0, 0).grapheme,
                (0x2139, 0xFE0F),
            )
            self.assertTrue(snapshot.cell(0, 0).double_width)
            self.assertTrue(snapshot.cell(1, 0).double_width_continuation)

    def test_copy_rectangle_does_not_remeasure_cluster_width(self):
        with Shitty(columns=8, rows=4) as terminal:
            terminal.write_chunks(
                b"\x1b[?2027l",
                "ℹ".encode(),
                "️".encode(),
                b"X",
            )
            terminal.write(b"\x1b[?2027h\x1b[1;1;1;2;1;3;1;1$v")
            snapshot = terminal.model_snapshot()

            self.assertEqual(snapshot.cell(0, 2).grapheme, (0x2139, 0xFE0F))
            self.assertFalse(snapshot.cell(0, 2).double_width)
            self.assertFalse(snapshot.cell(1, 2).double_width_continuation)
            self.assertEqual(snapshot.cell(1, 2).char, "X")

    def test_lnm_makes_line_feed_return_the_carriage(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"ab\ncd")
            self.assertEqual(
                terminal.snapshot().lines,
                ["ab   ", "  cd ", "     "],
            )

        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[20hab\ncd")
            self.assertEqual(
                terminal.snapshot().lines,
                ["ab   ", "cd   ", "     "],
            )

    def test_lf_outside_horizontal_margins_does_not_scroll(self):
        setup = (
            b"\x1b[1;3r"
            b"\x1b[?69h"
            b"\x1b[10;20s"
            b"\x1b[20h"
            b"\x1b[1;10Htop"
        )

        with Shitty(columns=40, rows=5) as terminal:
            terminal.write(setup + b"\x1b[3;30H\n")
            snapshot = terminal.snapshot()
            self.assertIn("top", snapshot.lines[0])
            self.assertEqual(
                (snapshot.cursor_x, snapshot.cursor_y), (9, 2)
            )

        with Shitty(columns=40, rows=5) as terminal:
            terminal.write(setup + b"\x1b[3;15H\n")
            self.assertNotIn("top", terminal.snapshot().lines[0])

    def test_lnm_makes_return_send_crlf(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.frontend_key_event(257, 1)
            terminal.frontend_key_event(257, 0)
            self.assertEqual(terminal.read_input(), b"\r")

            terminal.write(b"\x1b[20h")
            terminal.frontend_key_event(257, 1)
            terminal.frontend_key_event(257, 0)
            self.assertEqual(terminal.read_input(), b"\r\n")

            terminal.write(b"\x1b[20l")
            terminal.frontend_key_event(257, 1)
            terminal.frontend_key_event(257, 0)
            self.assertEqual(terminal.read_input(), b"\r")

    def test_kam_locks_and_unlocks_frontend_text_input(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[2h")
            terminal.frontend_text_event("x")
            self.assertEqual(terminal.read_input(), b"")

            terminal.write(b"\x1b[2l")
            terminal.frontend_text_event("x")
            self.assertEqual(terminal.read_input(), b"x")

    def test_srm_controls_local_echo_without_suppressing_host_input(self):
        for modes, expected_screen in (
            (b"", "     "),
            (b"\x1b[12l", "abc  "),
            (b"\x1b[12l\x1b[12h", "     "),
        ):
            with self.subTest(modes=modes), Shitty(
                columns=5, rows=3
            ) as terminal:
                terminal.write(modes)
                for character in "abc":
                    terminal.frontend_text_event(character)

                self.assertEqual(terminal.read_input(), b"abc")
                self.assertEqual(
                    terminal.snapshot().lines[0], expected_screen
                )

    @unittest.expectedFailure
    def test_srm_raw_query_echo_keeps_original_and_reply_ordered(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[12l")
            terminal.user_input(b"\x1b[6n")
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[6n\x1b[1;1R",
            )

    @unittest.expectedFailure
    def test_srm_echoes_a_parser_generated_reply_after_parser_returns(self):
        with Shitty(columns=20, rows=3) as terminal:
            terminal.write(b"\x1b[12l")
            terminal.parser_trace_on()
            terminal.parser_trace_clear()
            terminal.write(b"\x1b[?996n")
            trace = terminal.parser_trace()
            self.assertEqual(trace[0], ("csi", b"?996n"))
            self.assertEqual(len(trace), 2)
            self.assertEqual(trace[1][0], "csi")
            self.assertTrue(trace[1][1].startswith(b"?997;"))
            terminal.write(b"ok")
            self.assertEqual(terminal.snapshot().lines[0][:2], "ok")

    def test_ris_restores_srm_to_send_receive(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[12l\x1bc")
            terminal.user_input(b"abc")
            self.assertEqual(terminal.read_all_input(), b"abc")
            self.assertEqual(terminal.snapshot().lines[0], "     ")

    @unittest.expectedFailure
    def test_frontend_hard_reset_leaves_vt52_and_restores_configured_level(self):
        with Shitty(columns=10, rows=5) as terminal:
            terminal.write(b"\x1b[65;1\"p\x1b[?2l")
            terminal.hard_reset()
            terminal.write(b"\x1bP$q\"p\x1b\\\x1b[3;4H")
            self.assertEqual(
                (
                    terminal.read_all_input(),
                    (
                        terminal.snapshot().cursor_x,
                        terminal.snapshot().cursor_y,
                    ),
                ),
                (b"\x1bP1$r65;1\"p\x1b\\", (3, 2)),
            )

    def test_decrqm_distinguishes_live_fixed_and_unknown_ansi_modes(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1b[4$p\x1b[4h\x1b[4$p"
                b"\x1b[1$p\x1b[19$p\x1b[123$p"
            )
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[4;2$y\x1b[4;1$y"
                b"\x1b[1;4$y\x1b[19;4$y\x1b[123;0$y",
            )

    @unittest.expectedFailure
    def test_decpff_is_remembered_even_without_a_printer(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(
                b"\x1b[?18$p"
                b"\x1b[?18h\x1b[?18$p"
                b"\x1b[?18l\x1b[?18$p"
            )
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[?18;2$y\x1b[?18;1$y\x1b[?18;2$y",
            )

    def test_dechccm_reports_permanently_reset(self):
        with Shitty(columns=5, rows=3) as terminal:
            terminal.write(b"\x1b[?60$p")
            self.assertEqual(terminal.read_all_input(), b"\x1b[?60;4$y")

    @unittest.expectedFailure
    def test_vt525_national_modes_are_settable_reportable_toggles(self):
        with Shitty(columns=10, rows=3) as terminal:
            terminal.write(b"\x1b[65;1\"p")
            expected = bytearray()
            for mode in (34, 36, 61, 100, 106):
                terminal.write(
                    f"\x1b[?{mode}l\x1b[?{mode}$p"
                    f"\x1b[?{mode}h\x1b[?{mode}$p".encode()
                )
                expected.extend(f"\x1b[?{mode};2$y\x1b[?{mode};1$y".encode())
            self.assertEqual(terminal.read_all_input(), bytes(expected))

    def test_decreqtparm_reports_supported_requests_and_rejects_two(self):
        with Shitty(columns=10, rows=2) as terminal:
            terminal.write(b"\x1b[x\x1b[0x\x1b[1x\x1b[2x")
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[2;1;1;128;128;1;0x"
                b"\x1b[2;1;1;128;128;1;0x"
                b"\x1b[3;1;1;128;128;1;0x",
            )

    def test_xtwinops_reports_frontend_position_and_display_geometry(self):
        with Shitty(
            columns=20,
            rows=10,
            glyph_px=8,
            glyph_py=16,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(
                x=40, y=25, screen_width=800, screen_height=480
            )
            terminal.write(b"\x1b[13t\x1b[11t\x1b[15t\x1b[19t\x1b[18t")
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[3;40;25t\x1b[1t\x1b[5;480;800t"
                b"\x1b[9;29;99t\x1b[8;10;20t",
            )

    def test_xtwinops_zero_dimensions_resize_to_display(self):
        with Shitty(
            columns=20,
            rows=10,
            glyph_px=8,
            glyph_py=16,
            extra_arguments=("-allowWindowOps", "true"),
        ) as terminal:
            terminal.window_info(screen_width=800, screen_height=480)
            terminal.write(b"\x1b[8;0;12t\x1b[8;5;0t\x1b[8;;12t")
            self.assertEqual(
                terminal.read_actions(),
                ["WINDOW 8 29 12", "WINDOW 8 5 99", "WINDOW 8 5 12"],
            )

    def test_decdsr_answers_the_supported_device_matrix(self):
        with Shitty(columns=20, rows=10) as terminal:
            terminal.write(
                b"\x1b[?15n\x1b[?25n\x1b[?26n"
                b"\x1b[?55n\x1b[?56n\x1b[?62n"
                b"\x1b[?75n\x1b[?85n"
            )
            self.assertEqual(
                terminal.read_all_input(),
                b"\x1b[?13n\x1b[?20n\x1b[?27;1;0;0n"
                b"\x1b[?50n\x1b[?57;1n\x1b[0*{"
                b"\x1b[?70n\x1b[?83n",
            )


if __name__ == "__main__":
    unittest.main()

/* Headless tests of the real st parser/history/copy mode, not a model.
 * Selected terminal cases adapted from pg83/shitty (MIT contribution layer).
 * See tests/README.md and tests/LICENSE.shitty.
 */
#include <assert.h>
#include <locale.h>
#include "../st.c"

char *utmp, *scroll, *stty_args = "", *vtiden = "\033[?6c", *termname = "st";
wchar_t *worddelimiters = L" ,.;:/()[]{}";
int allowaltscreen = 1, allowwindowops = 0;
unsigned int tabspaces = 8, defaultfg = 258, defaultbg = 259, defaultcs = 256;
static char *clipboard;
static int copies, flash_cells;
#ifndef ST_REFERENCE_BRIDGE
void xbell(void) {}
void xclipcopy(void)
{
    copies++;
}
void xpastecancel(void) {}
void xdrawcursor(int a, int b, Glyph c, int d, int e, Glyph f)
{
    (void)a;
    (void)b;
    (void)c;
    (void)d;
    (void)e;
    (void)f;
}
void xdrawline(Line l, int a, int y, int b)
{
    assert(l && a >= 0 && b <= term.col && y < term.row);
    if (y < term.row - 1)
        for (int x = a; x < b; x++)
            if (l[x].bg == 3 && l[x].fg == defaultbg) flash_cells++;
}
void xfinishdraw(void) {}
void xloadcols(void) {}
int xsetcolorname(int i, const char *s)
{
    (void)i;
    (void)s;
    return 0;
}
int xgetcolor(int i, unsigned char *r, unsigned char *g, unsigned char *b)
{
    (void)i;
    *r = *g = *b = 0;
    return 0;
}
void xseticontitle(char *s)
{
    (void)s;
}
void xsettitle(char *s)
{
    (void)s;
}
int xsetcursor(int i)
{
    (void)i;
    return 0;
}
void xsetmode(int i, unsigned int m)
{
    (void)i;
    (void)m;
}
void xsetpointermotion(int i)
{
    (void)i;
}
void xsetsel(char *s)
{
    free(clipboard);
    clipboard = s;
}
int xstartdraw(void)
{
    return 1;
}
void xximspot(int x, int y)
{
    (void)x;
    (void)y;
}

#endif

static void init(int cols, int rows)
{
    assert(setlocale(LC_CTYPE, "C.UTF-8"));
    selinit();
    tnew(cols, rows);
}
static void feed(const char *s)
{
    assert(twrite(s, strlen(s), 0) == (int)strlen(s));
}
static void key(unsigned long k)
{
    browseinput(k, 0, NULL, 0);
}
static void roweq(int y, const char *s)
{
    int x;
    for (x = 0; s[x]; x++)
        assert(term.line[y][x].u == (unsigned char)s[x]);
    for (; x < term.col; x++)
        assert(term.line[y][x].u == ' ');
}
static void initialrows(void)
{
    feed("0\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6\r\n7\r\n8\r\n9");
}
static void history(void)
{
    init(20, 3);
    feed("oldest\r\nmiddle\r\nnewest\r\nlive\r\nend");
    assert(term.histlen == 2);
}

/* Adaptations of Shitty test_xtermjs_input_handler_margins.py. */
static void margins_home(void)
{
    init(10, 10);
    feed("\033[10;10H\033[2;7r");
    assert(term.c.x == 0 && term.c.y == 0 && term.top == 1 && term.bot == 6);
}
static void margins_default(void)
{
    init(10, 10);
    feed("\033[3;7r\033[0;0r");
    assert(term.top == 0 && term.bot == 9);
}
static void margins_clamp(void)
{
    init(10, 10);
    feed("\033[3;1000r");
    assert(term.top == 2 && term.bot == 9);
}
static void margins_scrollup(void)
{
    init(10, 10);
    initialrows();
    feed("\033[2;4r\033[2Sm");
    roweq(0, "m");
    roweq(1, "3");
    roweq(2, "");
    roweq(3, "");
    roweq(4, "4");
    assert(term.histlen == 0);
}
static void margins_scrolldown(void)
{
    init(10, 10);
    initialrows();
    feed("\033[2;4r\033[2Tm");
    roweq(0, "m");
    roweq(1, "");
    roweq(2, "");
    roweq(3, "1");
    roweq(4, "4");
}
static void insert_outside(void)
{
    init(10, 10);
    initialrows();
    feed("\033[3;6r\033[2Lm");
    roweq(0, "m");
    roweq(1, "1");
    roweq(5, "5");
}
static void insert_inside(void)
{
    init(10, 10);
    initialrows();
    feed("\033[3;6r\033[3H\033[2Lm");
    roweq(2, "m");
    roweq(3, "");
    roweq(4, "2");
    roweq(5, "3");
    roweq(6, "6");
}
static void delete_inside(void)
{
    init(10, 10);
    initialrows();
    feed("\033[3;6r\033[3H\033[2Mm");
    roweq(2, "m");
    roweq(3, "5");
    roweq(4, "");
    roweq(5, "");
    roweq(6, "6");
}
static void ich_pending_wrap(void)
{
    init(10, 10);
    feed("0123456789\033[@");
    roweq(0, "012345678");
}
/* Terminal rendition/alternate-screen cases from Shitty text suite. */
static void sgr_bold_reset(void)
{
    init(10, 3);
    feed("\033[1mA\033[22mB");
    assert(term.line[0][0].mode & ATTR_BOLD);
    assert(!(term.line[0][1].mode & ATTR_BOLD));
}
static void sgr_truecolor(void)
{
    init(10, 3);
    feed("\033[38;2;12;34;56mA");
    assert(term.line[0][0].fg == TRUECOLOR(12, 34, 56));
}
static void alternate_restore(void)
{
    init(10, 3);
    feed("main\033[2;3H\033[?1049hALT\033[?1049l");
    roweq(0, "main");
    assert(!tisaltscr() && term.c.x == 2 && term.c.y == 1);
}
static void dec_graphics(void)
{
    init(10, 3);
    feed("\033(0q\033(Bq");
    assert(term.line[0][0].u == 0x2500 && term.line[0][1].u == 'q');
}
static void wide_cells(void)
{
    init(10, 3);
    feed("A界B");
    assert(term.line[0][1].mode & ATTR_WIDE);
    assert(term.line[0][2].mode & ATTR_WDUMMY);
    assert(term.line[0][3].u == 'B');
}

/* Custom patch regressions: these go through actual terminal operations. */
static void empty_scrollback(void)
{
    init(10, 3);
    kscrollup(&(Arg){.i = 10});
    assert(term.scr == 0);
}
static void scroll_clamp(void)
{
    history();
    kscrollup(&(Arg){.i = 9999});
    assert(term.scr == term.histlen);
}
static void scroll_one_row(void)
{
    init(10, 1);
    feed("a\r\nb");
    kscrollup(&(Arg){.i = -1});
    assert(term.scr == 1);
}
static void reset_history(void)
{
    history();
    kscrollup(&(Arg){.i = 1});
    feed("\033c");
    assert(term.scr == 0 && term.histlen == 0);
}
static void alt_history(void)
{
    history();
    int n = term.histlen;
    feed("\033[?1049hA\r\nB\r\nC\r\nD\033[?1049l");
    assert(term.histlen == n);
}
static void alt_scroll(void)
{
    history();
    kscrollup(&(Arg){.i = 1});
    feed("\033[?1049h");
    assert(term.scr == 0);
    kscrollup(&(Arg){.i = 1});
    assert(term.scr == 0);
}
static void partial_region_history(void)
{
    init(10, 5);
    feed("a\r\nb\r\nc\r\nd\r\ne\033[2;4r\033[4H\n");
    assert(term.histlen == 0);
}
static void reverse_index_history(void)
{
    history();
    int n = term.histlen;
    feed("\033[H\033M");
    assert(term.histlen == n);
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_y);
    assert(!strcmp(clipboard, "oldest\n"));
}
static void yank_flash(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_y);
    assert(br.flashing && br.flashstart == 0 && br.flashend == term.col - 1);
    assert(browsetimeout() > 0 && browsetimeout() <= 200);
    assert(br.cells[0].bg == defaultbg); /* snapshot is not mutated */
    flash_cells = 0;
    browsedraw();
    assert(flash_cells == term.col);
    key(XK_j);
    key(XK_v);
    key(XK_l);
    key(XK_y);
    assert(br.flashstart == term.col && br.flashend == term.col + 1);
    /* Deterministic expiry: no sleep or timing-sensitive assertion needed. */
    br.flashuntil.tv_sec -= 1;
    assert(browsetimeout() == 0 && !br.flashing);
    assert(browsetimeout() == -1);
    flash_cells = 0;
    browsedraw();
    assert(flash_cells == 0);
    key(XK_y);
    assert(br.flashing);
    key(XK_q);
    assert(browsetimeout() == -1);
}

static void copy_snapshot(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    feed("\r\nchanged\r\nmore");
    key(XK_y);
    assert(!strcmp(clipboard, "oldest\n") && copies == 1);
}
static void copy_background_reset(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    feed("\033c");
    assert(browseactive());
    key(XK_y);
    assert(!strcmp(clipboard, "oldest\n"));
}
static void copy_visual(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_v);
    key(XK_l);
    key(XK_l);
    key(XK_y);
    assert(!strcmp(clipboard, "old"));
}
static void copy_visual_lines(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_V);
    key(XK_j);
    key(XK_y);
    assert(!strcmp(clipboard, "oldest\nmiddle\n"));
}
static void copy_search(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_slash);
    browseinput(XK_m, 0, "middle", 6);
    key(XK_Return);
    assert(br.y == 1 && br.x == 0);
}
static void copy_search_position(void)
{
    history();
    browse(NULL);
    key(XK_g);
    key(XK_g);
    browsedraw();
    key(XK_slash);
    browseinput(XK_e, 0, "end", 3);
    key(XK_Return);
    assert(br.y == 4);
    browsedraw();
    assert(br.top <= br.y && br.y < br.top + term.row - 1);
}
static void copy_wide_dummy(void)
{
    init(10, 3);
    feed("界X");
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_l);
    key(XK_v);
    key(XK_y);
    assert(!strcmp(clipboard, "界"));
}
static void copy_trailing_spaces(void)
{
    init(10, 3);
    feed("a  b");
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_v);
    key(XK_l);
    key(XK_l);
    key(XK_y);
    assert(!strcmp(clipboard, "a  "));
}
static void copy_wrap_lines(void)
{
    init(4, 3);
    feed("abcdef");
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_V);
    key(XK_j);
    key(XK_y);
    assert(!strcmp(clipboard, "abcdef\n"));
}
static void copy_resize(void)
{
    history();
    browse(NULL);
    tresize(12, 2);
    assert(!browseactive());
    draw();
}
static void copy_tiny(void)
{
    init(1, 1);
    feed("x");
    browse(NULL);
    browsedraw();
    key(XK_y);
    assert(!strcmp(clipboard, "x\n"));
    key(XK_q);
    assert(!browseactive());
}
static void copy_live_selection(void)
{
    history();
    browse(NULL);
    selstart(0, 0, 0);
    selextend(3, 0, SEL_REGULAR, 0);
    selextend(3, 0, SEL_REGULAR, 1);
    browsedraw();
    assert(browseactive());
}
static void ring_wrap(void)
{
    init(20, 3);
    char s[32];
    for (int i = 0; i < HISTSIZE + 10; i++) {
        snprintf(s, sizeof s, "line%04d\r\n", i);
        feed(s);
    }
    assert(term.histlen == HISTSIZE);
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_y);
    assert(!strcmp(clipboard, "line0008\n"));
}

static void copy_wide_search(void)
{
    init(10, 3);
    feed("a界文b");
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_slash);
    browseinput(XK_a, 0, "界文b", 7);
    key(XK_Return);
    assert(br.y == 0 && br.x == 1);
}
static void selection_resize(void)
{
    init(10, 24);
    feed("\033[21Hlast\033[24Hend");
    selstart(0, 20, 0);
    selextend(3, 23, SEL_REGULAR, 0);
    selextend(3, 23, SEL_REGULAR, 1);
    tresize(10, 10);
    char *s = getsel();
    assert(s == NULL);
}
static void selection_rectangle(void)
{
    init(10, 3);
    feed("    X\r\n    X");
    selstart(0, 0, 0);
    selextend(1, 1, SEL_RECTANGULAR, 0);
    selextend(1, 1, SEL_RECTANGULAR, 1);
    char *s = getsel();
    assert(s && s[0] == '\n');
    free(s);
}
static void copy_wrapped_space(void)
{
    init(5, 3);
    feed("abcd ef");
    browse(NULL);
    key(XK_g);
    key(XK_g);
    key(XK_v);
    key(XK_j);
    key(XK_l);
    key(XK_y);
    assert(!strcmp(clipboard, "abcd ef"));
}
static void wide_integrity(Line line, int cols)
{
    for (int x = 0; x < cols; x++) {
        if (line[x].mode & ATTR_WIDE)
            assert(x + 1 < cols && (line[x + 1].mode & ATTR_WDUMMY));
        if (line[x].mode & ATTR_WDUMMY)
            assert(x > 0 && (line[x - 1].mode & ATTR_WIDE));
    }
}
static void wide_erase(void)
{
    init(6, 2);
    feed("A界B\033[1;3H\033[X");
    wide_integrity(term.line[0], 6);
    roweq(0, "A  B");
}
static void wide_delete(void)
{
    init(6, 2);
    feed("A界BC\033[1;3H\033[P");
    wide_integrity(term.line[0], 6);
    roweq(0, "A BC");
}
static void wide_insert(void)
{
    init(6, 2);
    feed("A界BC\033[1;3H\033[@");
    wide_integrity(term.line[0], 6);
    roweq(0, "A   BC");
}
static void wide_resize(void)
{
    init(5, 2);
    feed("abc界");
    tresize(4, 2);
    wide_integrity(term.line[0], 4);
    roweq(0, "abc");
    tresize(6, 2);
    wide_integrity(term.line[0], 6);
    roweq(0, "abc");
}
static void parser_chunking(void)
{
    init(8, 3);
    const char bytes[] = {27, '[', '2', 0, ';', '3', 'H', 'X'};
    for (size_t i = 0; i < sizeof bytes; i++)
        assert(twrite(bytes + i, 1, 0) == 1);
    assert(term.line[1][2].u == 'X' && term.c.x == 3 && term.c.y == 1);
}
static void delayed_wrap(void)
{
    init(5, 3);
    feed("ABCDE");
    assert(term.c.x == 4 && term.c.y == 0 && (term.c.state & CURSOR_WRAPNEXT));
    feed("F");
    assert(term.line[0][4].mode & ATTR_WRAP);
    roweq(1, "F");
}
static void reset_defaults(void)
{
    init(12, 4);
    feed("\033[3g\033[2;3r\033[?6h\033[?7l\033[31;42m\033c\tX");
    assert(term.top == 0 && term.bot == 3);
    assert(term.mode & MODE_WRAP);
    assert(term.line[0][8].u == 'X' && term.line[0][8].fg == defaultfg);
}

static void deterministic_stress(void)
{
    const char *ops[] = {"abc",    "界",          "\r\n",        "\033[2J", "\033[H",
                         "\033M",  "\033[?1049h", "\033[?1049l", "\033[@",  "\033[P",
                         "\033[X", "\033[2;3r",   "\033[r",      "\033c"};
    unsigned seed = 12345;
    init(12, 5);
    for (int i = 0; i < 2000; i++) {
        seed = seed * 1664525u + 1013904223u;
        switch (seed % 5) {
        case 0:
            feed(ops[(seed >> 8) % LEN(ops)]);
            break;
        case 1:
            tresize(2 + (seed >> 8) % 20, 1 + (seed >> 16) % 8);
            break;
        case 2:
            kscrollup(&(Arg){.i = (seed >> 8) % 20});
            break;
        case 3:
            kscrolldown(&(Arg){.i = 3});
            break;
        case 4:
            browse(NULL);
            if (browseactive()) {
                key(XK_g);
                key(XK_g);
                key(XK_y);
                browsedraw();
                key(XK_q);
            }
            break;
        }
        assert(term.scr >= 0 && term.scr <= term.histlen && term.histlen <= HISTSIZE);
        assert(term.c.x >= 0 && term.c.x < term.col && term.c.y >= 0 && term.c.y < term.row);
        for (int y = 0; y < term.row; y++) {
            wide_integrity(term.line[y], term.col);
            wide_integrity(term.alt[y], term.col);
        }
    }
}
static void cleanup(void)
{
    if (browseactive())
        browseclose();
    for (int i = 0; i < term.row; i++) {
        free(term.line[i]);
        free(term.alt[i]);
    }
    for (int i = 0; i < HISTSIZE; i++)
        free(term.hist[i]);
    free(term.line);
    free(term.alt);
    free(term.tabs);
    free(term.dirty);
    free(strescseq.buf);
    free(clipboard);
}
struct test {
    const char *name;
    void (*run)(void);
} tests[] = {
#define T(n) {#n, n}
    T(yank_flash), T(deterministic_stress),  T(copy_wide_search),   T(selection_resize),
    T(selection_rectangle),   T(copy_wrapped_space), T(wide_erase),
    T(wide_delete),           T(wide_insert),        T(wide_resize),
    T(parser_chunking),       T(delayed_wrap),       T(reset_defaults),
    T(margins_home),          T(margins_default),    T(margins_clamp),
    T(margins_scrollup),      T(margins_scrolldown), T(insert_outside),
    T(insert_inside),         T(delete_inside),      T(ich_pending_wrap),
    T(sgr_bold_reset),        T(sgr_truecolor),      T(alternate_restore),
    T(dec_graphics),          T(wide_cells),         T(empty_scrollback),
    T(scroll_clamp),          T(scroll_one_row),     T(reset_history),
    T(alt_history),           T(alt_scroll),         T(partial_region_history),
    T(reverse_index_history), T(copy_snapshot),      T(copy_background_reset),
    T(copy_visual),           T(copy_visual_lines),  T(copy_search),
    T(copy_search_position),  T(copy_wide_dummy),    T(copy_trailing_spaces),
    T(copy_wrap_lines),       T(copy_resize),        T(copy_tiny),
    T(copy_live_selection),   T(ring_wrap)};
int main(int argc, char **argv)
{
    if (argc == 1) {
        for (size_t i = 0; i < LEN(tests); i++)
            puts(tests[i].name);
        return 0;
    }
    for (size_t i = 0; i < LEN(tests); i++)
        if (!strcmp(argv[1], tests[i].name)) {
            tests[i].run();
            cleanup();
            printf("PASS %s\n", tests[i].name);
            return 0;
        }
    return 2;
}

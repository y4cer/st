/* Unit tests of real x.c routing using a deterministic X11 property transport.
 * No X server, clipboard owner, or user session is touched.
 */
#include <assert.h>
#define main st_application_main
#include "../x.c"
#undef main
/* Core dependencies not exercised by these frontend unit tests. */
void selclear(void) {}
void redraw(void) {}
void tresize(int c, int r)
{
    (void)c;
    (void)r;
}
void *xrealloc(void *p, size_t n)
{
    return realloc(p, n);
}
void ttyresize(int w, int h)
{
    (void)w;
    (void)h;
}
void selextend(int x, int y, int t, int d)
{
    (void)x;
    (void)y;
    (void)t;
    (void)d;
}
char *getsel(void)
{
    return NULL;
}
int tisaltscr(void)
{
    return 0;
}
void browseinput(unsigned long k, unsigned int s, const char *b, int n)
{
    (void)k;
    (void)s;
    (void)b;
    (void)n;
}
void selstart(int x, int y, int s)
{
    (void)x;
    (void)y;
    (void)s;
}
char *xstrdup(const char *s)
{
    return strdup(s);
}
void ttyhangup(void) {}
void browse(const Arg *a)
{
    (void)a;
}
void sendbreak(const Arg *a)
{
    (void)a;
}
void toggleprinter(const Arg *a)
{
    (void)a;
}
void printscreen(const Arg *a)
{
    (void)a;
}
void printsel(const Arg *a)
{
    (void)a;
}
void kscrollup(const Arg *a)
{
    (void)a;
}
void kscrolldown(const Arg *a)
{
    (void)a;
}
static int ro, deleted, outstanding;
static Atom property_type;
static const char *chunk;
static char delivered[8192];
static size_t delivered_len;
int browseactive(void)
{
    return ro;
}
void ttywrite(const char *s, size_t n, int echo)
{
    (void)echo;
    assert(delivered_len + n < sizeof delivered);
    memcpy(delivered + delivered_len, s, n);
    delivered_len += n;
    delivered[delivered_len] = 0;
}
void die(const char *fmt, ...)
{
    (void)fmt;
    exit(2);
}
Atom XInternAtom(Display *d, const char *s, Bool only)
{
    (void)d;
    (void)only;
    return !strcmp(s, "INCR") ? 100 : 101;
}
int XGetWindowProperty(Display *d, Window w, Atom a, long o, long l, Bool del, Atom req, Atom *type,
                       int *format, unsigned long *n, unsigned long *remaining,
                       unsigned char **value)
{
    (void)d;
    (void)w;
    (void)a;
    (void)o;
    (void)l;
    (void)del;
    (void)req;
    *type = property_type;
    *format = 8;
    *n = strlen(chunk);
    *remaining = 0;
    *value = (unsigned char *)strdup(chunk);
    outstanding++;
    return Success;
}
int XFree(void *p)
{
    free(p);
    outstanding--;
    return 0;
}
int XDeleteProperty(Display *d, Window w, Atom a)
{
    (void)d;
    (void)w;
    (void)a;
    deleted++;
    return 0;
}
int XChangeWindowAttributes(Display *d, Window w, unsigned long m, XSetWindowAttributes *a)
{
    (void)d;
    (void)w;
    (void)m;
    (void)a;
    return 0;
}
static void event(int type, Atom data_type, const char *data)
{
    XEvent e = {0};
    e.type = type;
    if (type == SelectionNotify)
        e.xselection.property = 101;
    else
        e.xproperty.atom = 101;
    property_type = data_type;
    chunk = data;
    selnotify(&e);
}
static void reset(void)
{
    memset(&paste, 0, sizeof paste);
    ro = deleted = outstanding = 0;
    delivered_len = 0;
    delivered[0] = 0;
    win.mode = MODE_BRCKTPASTE;
}
static void incr_complete(void)
{
    reset();
    event(SelectionNotify, 100, "size");
    event(PropertyNotify, 101, "hello");
    event(PropertyNotify, 101, " world");
    event(PropertyNotify, 101, "");
    assert(!strcmp(delivered, "\033[200~hello world\033[201~"));
    assert(deleted == 4 && outstanding == 0 && !paste.active);
}
static void incr_cancel(void)
{
    reset();
    event(SelectionNotify, 100, "size");
    event(PropertyNotify, 101, "first");
    xpastecancel();
    ro = 1;
    event(PropertyNotify, 101, "discard");
    ro = 0;
    event(PropertyNotify, 101, "still discarded");
    event(PropertyNotify, 101, "");
    assert(!strcmp(delivered, "\033[200~first\033[201~"));
    assert(deleted == 5 && outstanding == 0 && !paste.active);
    event(SelectionNotify, 101, "new");
    assert(strstr(delivered, "\033[200~new\033[201~"));
}
static void incr_ro_start(void)
{
    reset();
    ro = 1;
    event(SelectionNotify, 100, "size");
    ro = 0;
    event(PropertyNotify, 101, "discard");
    event(PropertyNotify, 101, "");
    assert(!delivered_len && deleted == 3 && outstanding == 0);
}
static void normal_paste(void)
{
    reset();
    event(SelectionNotify, 101, "a\nb");
    assert(!strcmp(delivered, "\033[200~a\rb\033[201~") && outstanding == 0);
}
static void empty_paste(void)
{
    reset();
    event(SelectionNotify, 101, "");
    assert(!delivered_len && !paste.active);
}
static void focus_ro(void)
{
    reset();
    ro = 1;
    win.mode |= MODE_FOCUS;
    XEvent e = {0};
    e.type = FocusOut;
    focus(&e);
    assert(!delivered_len);
    ro = 0;
    focus(&e);
    assert(!strcmp(delivered, "\033[O"));
}
static void ctrl_enter(void)
{
    assert(!strcmp(kmap(XK_Return, ControlMask | LockMask), "\033[13;5u"));
    assert(!strcmp(kmap(XK_Return, ControlMask | ShiftMask), "\033[13;6u"));
    assert(!strcmp(kmap(XK_Return, ControlMask | Mod1Mask), "\033[13;7u"));
}
static void alpha_zero(void)
{
    Color c = {.color = {65535, 65535, 65535, 65535}, .pixel = 0xffffff};
    xw.depth = 32;
    alpha = 0;
    xapplyalpha(&c);
    assert(c.pixel == 0 && c.color.red == 0 && c.color.alpha == 0);
}
static void alpha_half(void)
{
    Color c = {.color = {65535, 32768, 0, 65535}, .pixel = 0xffff8000};
    xw.depth = 32;
    alpha = .5f;
    xapplyalpha(&c);
    assert(c.pixel == 0x7f7f4000 && c.color.red == 32767 && c.color.green == 16384);
}
static void alpha_opaque_visual(void)
{
    Color c = {.color = {65535, 65535, 65535, 65535}, .pixel = 0xffffff};
    xw.depth = 24;
    alpha = 0;
    xapplyalpha(&c);
    assert(c.pixel == 0xffffff && c.color.alpha == 65535);
}
static void alpha_parse(void)
{
    assert(parsealpha("0.5") == .5f && parsealpha("-2") == 0 && parsealpha("2") == 1);
}
static void russian_commands(void)
{
    assert(browsekeysym(XK_Cyrillic_er, 0) == XK_h);
    assert(browsekeysym(XK_Cyrillic_o, 0) == XK_j);
    assert(browsekeysym(XK_Cyrillic_ve, 0) == XK_d);
    assert(browsekeysym(XK_Cyrillic_EM, ShiftMask) == XK_V);
    assert(browsekeysym(XK_Cyrillic_en, 0) == XK_y);
    assert(browsekeysym(XK_Escape, 0) == XK_Escape);
}
struct test {
    const char *name;
    void (*run)(void);
} cases[] = {
#define T(n) {#n, n}
    T(incr_complete), T(incr_cancel),     T(incr_ro_start), T(normal_paste), T(empty_paste),
    T(focus_ro),      T(ctrl_enter),      T(alpha_zero),    T(alpha_half),   T(alpha_opaque_visual),
    T(alpha_parse),   T(russian_commands)};
#ifndef ST_FRONTEND_BRIDGE
int main(int argc, char **argv)
{
    if (argc == 1) {
        for (size_t i = 0; i < LEN(cases); i++)
            puts(cases[i].name);
        return 0;
    }
    for (size_t i = 0; i < LEN(cases); i++)
        if (!strcmp(argv[1], cases[i].name)) {
            cases[i].run();
            printf("PASS %s\n", cases[i].name);
            return 0;
        }
    return 2;
}

#endif

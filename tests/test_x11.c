/* Unit tests of real x.c routing using a deterministic X11 property transport.
 * No X server, clipboard owner, or user session is touched.
 */
#include <assert.h>
#define main st_application_main
#include "../x.c"
#undef main
/* Frontend tests supply one core endpoint, never a terminal model. */
struct Session { SessionView view; char received[8192]; size_t length; };
static Session test_session = {.view = {.id = 1, .cursor = 1}};
static Session test_second = {.view = {.id = 2, .cursor = 1}};
static Session *test_active = &test_session, *test_context = &test_session;
static int test_live_first = 1, test_live_second;
Session *session_current(void) { return test_context; }
Session *session_active(void) { return test_active; }
Session *session_find(uint64_t id) { return id == 1 && test_live_first ? &test_session : id == 2 && test_live_second ? &test_second : NULL; }
Session *session_bind(Session *s) { Session *old=test_context;test_context=s;return old; }
SessionView *session_view(Session *s) { return &s->view; }
size_t session_count(void) { return test_live_first + test_live_second; }
size_t session_index(Session *s) { (void)s; return 0; }
Session *session_at(size_t i) { if(test_live_first){if(!i)return &test_session;i--;}return !i && test_live_second?&test_second:NULL; }
Session *session_new(int c, int r) { (void)c; (void)r; return NULL; }
void session_select(Session *s) { test_active=test_context=s; }
void session_switch(Session *s,int focused) { (void)s;(void)focused; }
void session_close(Session *s) { (void)s; }
void sessions_free(void) {}
void sessions_resize(int c,int r,int w,int h) { tresize(c,r);ttyresize(w,h); }
void session_write(Session *s,const char *data,size_t len,int echo) { Session *old=session_bind(s);ttywrite(data,len,echo);session_bind(old); }
int ttynew(const char *l,char *c,const char *o,char **a) { (void)l;(void)c;(void)o;(void)a;return -1; }
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
void *xmalloc(size_t n)
{
    void *p = malloc(n);
    assert(p);
    return p;
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
    Session *endpoint=session_current();
    assert(endpoint->length+n<sizeof endpoint->received);
    memcpy(endpoint->received+endpoint->length,s,n);endpoint->length+=n;
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
    test_live_first=1;test_live_second=0;test_active=test_context=&test_session;
    test_session.length=test_second.length=0;
    test_session.view.mode=test_second.view.mode=0;
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
static void incr_switch_keeps_destination(void)
{
    reset();test_live_second=1;
    event(SelectionNotify,100,"size");
    event(PropertyNotify,101,"first");
    session_select(&test_second);
    xpastecancel(); /* Entering copy mode in B must not cancel A's paste. */
    event(PropertyNotify,101,"second");
    event(PropertyNotify,101,"");
    assert(test_second.length==0);
    assert(test_session.length==strlen("\033[200~firstsecond\033[201~"));
    assert(!memcmp(test_session.received,"\033[200~firstsecond\033[201~",test_session.length));
    assert(!paste.active && outstanding==0 && deleted==4);
}
static void incr_close_discards_remaining_chunks(void)
{
    reset();test_live_second=1;
    event(SelectionNotify,100,"size");
    event(PropertyNotify,101,"first");
    size_t before=test_session.length;
    xsessionfree(&test_session);test_live_first=0;session_select(&test_second);
    event(PropertyNotify,101,"discard");
    event(PropertyNotify,101,"");
    assert(test_session.length==before && test_second.length==0);
    assert(!paste.active && outstanding==0 && deleted==4);
}
struct test {
    const char *name;
    void (*run)(void);
} cases[] = {
#define T(n) {#n, n}
    T(incr_switch_keeps_destination), T(incr_close_discards_remaining_chunks), T(incr_complete), T(incr_cancel),     T(incr_ro_start), T(normal_paste), T(empty_paste),
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

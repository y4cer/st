/* X11 projection of the session model. Included by x.c. */
static int tabheight(void) { return session_count() > 1 ? win.ch + 12 : 0; }

void
xsessionfree(Session *s)
{
    SessionView *v = session_view(s);
    if (paste.target == v->id) { paste.discard = 1; paste.bracketed = 0; paste.target = 0; }
    if (v->palette) {
        Color *colors = v->palette;
        for (size_t i = 0; i < v->palette_len; i++) XftColorFree(xw.dpy, xw.vis, xw.cmap, &colors[i]);
        free(v->palette); v->palette = NULL; v->palette_len = 0;
    }
    if (!session_count() && tabcolorsready) {
        for (size_t i = 0; i < LEN(tabcolors); i++)
            XftColorFree(xw.dpy, xw.vis, xw.cmap, &tabcolors[i]);
        tabcolorsready = 0;
    }
}

static void
tabschanged(void)
{
    if (!session_count()) return;
    SessionView *v = session_view(session_active());
    buttons = 0;
    win.mode &= ~MODE_BLINK;
    xsetpointermotion(v->mode & MODE_MOUSEMANY);
    xsettitle(v->title); xseticontitle(v->icon);
    cresize(0, 0); xhints(); redraw();
    xximspot(0, 0);
}

static void
tabactivate(Session *s)
{
    Session *old = session_active();
    if (!s || s == old) return;
    session_switch(s, win.mode & MODE_FOCUSED);
    buttons = 0;
    win.mode &= ~MODE_BLINK;
    xsetpointermotion(session_view(s)->mode & MODE_MOUSEMANY);
    xsettitle(session_view(s)->title); xseticontitle(session_view(s)->icon);
    redraw();
    xximspot(0, 0);
}

static void
tabnew(const Arg *arg)
{
    (void)arg;
    if (opt_line) return; /* a supplied device is not a shell launch recipe */
    Session *old = session_active();
    Session *s = session_new(MAX(1, win.tw / win.cw), MAX(1, win.th / win.ch));
    if (!s) return;
    session_bind(s);
    xloadcols();
    int fd = ttynew(NULL, shell, NULL, opt_cmd);
    session_bind(old);
    if (fd < 0) { fprintf(stderr, "cannot open tab: %s\n", strerror(errno)); session_close(s); return; }
    tabactivate(s);
    tabschanged();
}

static void
tabclose(const Arg *arg)
{
    (void)arg;
    session_close(session_active());
    if (!session_count()) return;
    tabschanged();
    if ((win.mode & MODE_FOCUSED) && IS_SET(MODE_FOCUS)) ttywrite("\033[I", 3, 0);
}

static void
tabnext(const Arg *arg)
{
    size_t count = session_count(), at = session_index(session_active());
    if (!count) return;
    tabactivate(session_at((at + count + (arg->i < 0 ? -1 : 1)) % count));
}

static void
tabselect(const Arg *arg)
{
    if (arg->i >= 0) tabactivate(session_at(arg->i));
}

static void
drawtabs(void)
{
    int height = tabheight();
    if (!height) return;
    size_t n = session_count(), at = session_index(session_active());
    size_t visible = MIN(n, (size_t)MAX(1, win.w / MAX(1, 12 * win.cw)));
    size_t first = at >= visible ? at - visible + 1 : 0;
    int width = win.w / visible;
    XftDrawRect(xw.draw, &tabcolors[TabBar], 0, 0, win.w, height);
    XftDrawRect(xw.draw, &tabcolors[TabBorder], 0, height - 2, win.w, 2);
    for (size_t i = 0; i < visible && i + first < n; i++) {
        Session *s = session_at(first + i);
        SessionView *v = session_view(s);
        char label[512];
        int len = snprintf(label, sizeof label, "%zu%s %s", first + i + 1,
                           v->activity ? "*" : "", v->title ? v->title : "st");
        len = MIN(len, (int)sizeof(label) - 1);
        /* Clip each label, preserving whole UTF-8 sequences at the byte cap. */
        int used = 0;
        while (used < len) { Rune u; size_t bytes = utf8decode(label + used, &u, len - used); if (!bytes) break; used += bytes; }
        int left = i * width + 2, blockwidth = MAX(1, width - 4);
        int selected = s == session_active();
        XRectangle clip = {.x = left, .y = 3, .width = blockwidth, .height = height - 6};
        XftDrawSetClipRectangles(xw.draw, 0, 0, &clip, 1);
        XftDrawRect(xw.draw, &tabcolors[selected ? TabActive : TabInactive], left, 3, blockwidth, height - 6);
        if (selected)
            XftDrawRect(xw.draw, &tabcolors[TabAccent], left, height - 6, blockwidth, 3);
        XftDrawStringUtf8(xw.draw, &tabcolors[selected ? TabActiveText : v->activity ? TabActivity : TabText], dc.font.match,
                         left + 8, (height - dc.font.height) / 2 + dc.font.ascent - 1,
                         (FcChar8 *)label, used);
        XftDrawSetClip(xw.draw, NULL);
    }
}

/* Session ownership and synchronous context dispatch. Included by st.c. */
Session *session_current(void) { return context; }
Session *session_active(void) { return active; }
Session *session_bind(Session *s) { Session *old = context; context = s; return old; }
SessionView *session_view(Session *s) { return &s->view; }
size_t session_count(void) { size_t n = 0; for (Session *s = head; s; s = s->next) n++; return n; }
Session *session_at(size_t n) { Session *s = head; while (s && n--) s = s->next; return s; }
Session *session_find(uint64_t id) { for (Session *s = head; s; s = s->next) if (s->view.id == id) return s; return NULL; }
size_t session_index(Session *s) { size_t i = 0; for (Session *p = head; p && p != s; p = p->next) i++; return i; }
int session_fd(Session *s) { return s->ptyfd; }
int session_pending(Session *s) { return s->outputlen > s->outputpos; }

Session *
session_new(int cols, int rows)
{
    Session *s = calloc(1, sizeof(*s)), *old;
    if (!s) return NULL;
    s->ptyfd = -1; s->logfd = 1;
    s->view.id = next_session_id++; s->view.cursor = 1;
    old = session_bind(s);
    selinit(); tnew(cols, rows);
    session_bind(old);
    Session **tail = &head;
    while (*tail) tail = &(*tail)->next;
    *tail = s;
    return s;
}

void
session_select(Session *s)
{
    if (!s) return;
    active = context = s;
    s->view.activity = 0;
    tfulldirt();
}

void
session_switch(Session *s, int focused)
{
    if (!s || s == active) return;
    if (active && focused && (active->view.mode & MODE_FOCUS))
        session_write(active, "\033[O", 3, 0);
    session_select(s);
    if (focused && (s->view.mode & MODE_FOCUS)) session_write(s, "\033[I", 3, 0);
}

void
session_close(Session *s)
{
    Session **slot = &head, *previous = NULL;
    while (*slot && *slot != s) { previous = *slot; slot = &(*slot)->next; }
    if (!*slot) return;
    if (active == s) active = s->next ? s->next : previous;
    *slot = s->next;
    context = s;
    xsessionfree(s);
    if (s->child > 0 && kill(-s->child, SIGHUP) < 0) kill(s->child, SIGHUP);
    if (s->ptyfd >= 0) close(s->ptyfd);
    if (s->logfd > 2) close(s->logfd);
    for (int y = 0; y < term.row; y++) { free(term.line[y]); free(term.alt[y]); }
    for (int y = 0; y < HISTSIZE; y++) free(term.hist[y]);
    free(term.line); free(term.alt); free(term.tabs); free(term.dirty);
    free(strescseq.buf); free(br.cells); free(br.view); free(s->output);
    free(s->view.title); free(s->view.icon);
    if (s != &initial) free(s);
    else memset(s, 0, sizeof(*s));
    context = active;
    if (active) tfulldirt();
}

void
sessions_free(void)
{
    while (head) session_close(head);
    for (int i = 0; i < 2; i++) if (childpipe[i] >= 0) { close(childpipe[i]); childpipe[i] = -1; }
}

void
sessions_resize(int cols, int rows, int width, int height)
{
    Session *old = context;
    for (Session *s = head; s; s = s->next) {
        context = s;
        if (term.col != cols || term.row != rows) tresize(cols, rows);
        if (cmdfd >= 0) ttyresize(width, height);
    }
    context = old;
}

void
session_read(Session *s)
{
    Session *old = session_bind(s);
    ttyread();
    session_bind(old);
}

void
session_flush(Session *s)
{
    if (s->ptyfd < 0 || !session_pending(s)) return;
    ssize_t n = write(s->ptyfd, s->output + s->outputpos,
                      MIN(s->outputlen - s->outputpos, 65536));
    if (n > 0) {
        s->outputpos += n;
        if (s->outputpos == s->outputlen) s->outputpos = s->outputlen = 0;
    } else if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
        s->ended = 1;
    }
}

void
session_write(Session *s, const char *data, size_t len, int echo)
{
    Session *old = session_bind(s);
    ttywrite(data, len, echo);
    session_bind(old);
}

void
session_feed(Session *s, const char *data, size_t len)
{
    Session *old = session_bind(s);
    while (len) {
        size_t n = MIN(len, sizeof(s->input) - s->inputlen);
        memcpy(s->input + s->inputlen, data, n);
        s->inputlen += n; data += n; len -= n;
        size_t used = twrite(s->input, s->inputlen, 0);
        s->inputlen -= used;
        memmove(s->input, s->input + used, s->inputlen);
    }
    if (s != active) s->view.activity = 1;
    session_bind(old);
}

int
session_signal_fd(void)
{
    if (childpipe[0] < 0) {
        if (pipe(childpipe) < 0) return -1;
        for (int i = 0; i < 2; i++) {
            fcntl(childpipe[i], F_SETFL, O_NONBLOCK);
            fcntl(childpipe[i], F_SETFD, FD_CLOEXEC);
        }
        signal(SIGCHLD, sigchld);
    }
    return childpipe[0];
}

int
sessions_reap(void)
{
    char bytes[64]; int status, changed = 0; pid_t child;
    if (childpipe[0] >= 0) while (read(childpipe[0], bytes, sizeof bytes) > 0) {}
    while ((child = waitpid(-1, &status, WNOHANG)) > 0) {
        for (Session *s = head; s; s = s->next)
            if (s->child == child) {
                s->child = 0;
                /* Drain the bounded PTY kernel buffer before disposing the
                 * exited shell. Descendants cannot keep its tab alive forever. */
                Session *old = session_bind(s);
                for (int i = 0; i < 16 && ttyread() > 0; i++) {}
                session_bind(old);
                s->ended = 1; break;
            }
    }
    for (Session *s = head, *next; s; s = next) {
        next = s->next;
        if (s->ended) { session_close(s); changed = 1; }
    }
    return changed;
}

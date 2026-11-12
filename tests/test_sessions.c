/* Real st session ownership, routing and PTY lifecycle regressions. */
#include <sys/socket.h>
#include <poll.h>
#include <sys/resource.h>
#define main terminal_fixture_main
#include "test_terminal.c"
#undef main

static void pairfor(Session *s, int *peer)
{
    int fds[2];
    assert(socketpair(AF_UNIX, SOCK_STREAM, 0, fds) == 0);
    s->ptyfd = fds[0]; *peer = fds[1];
    for (int i = 0; i < 2; i++) assert(fcntl(fds[i], F_SETFL, O_NONBLOCK) == 0);
}

static void isolation(void)
{
    init(12, 3);
    Session *a = session_active(), *b = session_new(12, 3);
    int pa, pb; pairfor(a, &pa); pairfor(b, &pb);
    session_feed(a, "A\033[2;4H\0337\033[31m\033[", strlen("A\033[2;4H\0337\033[31m\033["));
    session_feed(b, "B\033[3;8H\0337\033[32m", strlen("B\033[3;8H\0337\033[32m"));
    /* Split parser/UTF-8 input belongs to its sender, never the active view. */
    session_select(b);
    session_feed(a, "1;1H\347", 5);
    session_feed(b, "x", 1);
    session_feed(a, "\225\214", 2);
    session_select(a);
    assert(term.line[0][0].u == 0x754c);
    session_feed(a, "\0338", 2);
    assert(term.c.x == 3 && term.c.y == 1);
    session_select(b); session_feed(b, "\0338", 2);
    assert(term.c.x == 7 && term.c.y == 2);
    session_feed(a, "\033[6n", 4);
    char reply[32];
    assert(read(pa, reply, sizeof reply) == 6 && !memcmp(reply, "\033[2;4R", 6));
    assert(read(pb, reply, sizeof reply) < 0 && errno == EAGAIN);
    session_write(b, "typed", 5, 0);
    assert(read(pb, reply, sizeof reply) == 5 && !memcmp(reply, "typed", 5));
    assert(session_current() == b);
    session_feed(a, "\033[H\033[2J", 7);
    assert(a->screen.histlen > 0 && b->screen.histlen == 0);
    assert(session_current() == b && b->screen.line[0][0].u == 'B');
    close(pa); close(pb);
}

static void copy_and_history(void)
{
    init(8, 3);
    Session *a = session_active();
    feed("one\r\ntwo\r\nthree\r\nfour");
    kscrollup(&(Arg){.i=1});
    int scroll = term.scr;
    browse(NULL); key(XK_k);
    int y = br.y;
    Session *b = session_new(8, 3); session_select(b);
    assert(!browseactive() && term.histlen == 0);
    feed("other");
    session_select(a);
    assert(browseactive() && br.y == y && term.scr == scroll);
    session_feed(b, "\r\nbackground", 12);
    assert(browseactive() && br.y == y);
    session_close(b);
    assert(session_active() == a && browseactive());
}

static void resize_and_lifetime(void)
{
    init(8, 3);
    Session *a = session_active(), *b = session_new(8, 3), *c = session_new(8, 3);
    uint64_t dead = b->view.id;
    session_select(c);
    sessions_resize(12, 4, 120, 40);
    assert(a->screen.col == 12 && b->screen.row == 4 && c->screen.row == 4);
    session_close(b);
    assert(session_count() == 2 && session_active() == c && !session_find(dead));
    session_close(c);
    assert(session_count() == 1 && session_active() == a);
    for (int i = 0; i < 30; i++) {
        Session *s = session_new(12, 4); assert(s->view.id != dead);
        session_select(s); session_close(s);
        assert(session_active() == a && session_count() == 1);
    }
}

static void backpressure_close(void)
{
    init(8, 3);
    Session *a = session_active(), *b = session_new(8, 3);
    int pa, pb; pairfor(a, &pa); pairfor(b, &pb);
    char data[65536]; memset(data, 'x', sizeof data);
    for (int i = 0; i < 32; i++) session_write(b, data, sizeof data, 0);
    assert(session_pending(b));
    session_write(a, "OK", 2, 0);
    char buf[8]; assert(read(pa, buf, sizeof buf) == 2 && !memcmp(buf, "OK", 2));
    uint64_t id = b->view.id;
    session_close(b);
    assert(!session_find(id) && session_active() == a);
    close(pa); close(pb);
}

static void child_exit(void)
{
    init(8, 3);
    Session *a = session_active(), *b = session_new(8, 3);
    session_bind(b);
    char *args[] = {"sh", "-c", "printf finished", NULL};
    assert(ttynew(NULL, "/bin/sh", NULL, args) >= 0);
    session_bind(a);
    for (int i = 0; i < 100 && session_count() > 1; i++) {
        struct pollfd wake = {.fd=session_signal_fd(),.events=POLLIN};
        assert(poll(&wake, 1, 50) >= 0 || errno == EINTR);
        sessions_reap();
    }
    assert(session_count() == 1 && session_active() == a);
    feed("alive"); roweq(0, "alive");
}

static void focus_routing(void)
{
    init(8,3);
    Session *a=session_active(),*b=session_new(8,3);
    int pa,pb;pairfor(a,&pa);pairfor(b,&pb);
    a->view.mode=b->view.mode=MODE_FOCUS;
    session_switch(b,1);
    char data[16];
    assert(read(pa,data,sizeof data)==3 && !memcmp(data,"\033[O",3));
    assert(read(pb,data,sizeof data)==3 && !memcmp(data,"\033[I",3));
    session_switch(a,0);
    assert(read(pa,data,sizeof data)<0 && errno==EAGAIN);
    assert(read(pb,data,sizeof data)<0 && errno==EAGAIN);
    session_switch(a,1); /* Selecting the current tab does not invent focus. */
    assert(read(pa,data,sizeof data)<0 && errno==EAGAIN);
    close(pa);close(pb);
}
static void refused_spawn(void)
{
    init(8,3);
    Session *a=session_active(),*b=session_new(8,3);
    struct rlimit before,limited;
    assert(getrlimit(RLIMIT_NOFILE,&before)==0);limited=before;limited.rlim_cur=0;
    assert(setrlimit(RLIMIT_NOFILE,&limited)==0);
    session_bind(b);
    int fd=ttynew(NULL,"/bin/sh",NULL,NULL);
    session_bind(a);
    assert(setrlimit(RLIMIT_NOFILE,&before)==0);
    assert(fd==-1 && session_active()==a && session_current()==a);
    session_close(b);
    feed("alive");roweq(0,"alive");
    assert(session_count()==1);
}

int main(int argc, char **argv)
{
    struct { const char *name; void (*run)(void); } cases[] = {
        {"isolation", isolation}, {"copy_history", copy_and_history},
        {"resize_lifetime", resize_and_lifetime}, {"backpressure_close", backpressure_close},
        {"child_exit", child_exit}, {"focus_routing",focus_routing}, {"refused_spawn",refused_spawn},
    };
    if (argc != 2) return 2;
    for (size_t i = 0; i < LEN(cases); i++) if (!strcmp(argv[1], cases[i].name)) {
        cases[i].run(); sessions_free(); free(clipboard);
        puts("PASS"); return 0;
    }
    return 2;
}

#define _POSIX_C_SOURCE 200809L
/* Test-only wire adapter around the real st core. No terminal model. */
#include <sys/socket.h>
#define ST_REFERENCE_BRIDGE
#define main existing_tests_main
#include "../test_terminal.c"
#undef main

#define frontend_mode (session_view(session_current())->mode)
static int palette_unavailable;
#define cursor_style (session_view(session_current())->cursor)
static int bells;
#define title (session_view(session_current())->title)
#define icon (session_view(session_current())->icon)
void xbell(void) { bells++; }
void xclipcopy(void) { copies++; }
void xpastecancel(void) {}
void xdrawcursor(int a,int b,Glyph c,int d,int e,Glyph f) {}
void xdrawline(Line l,int a,int y,int b) {}
void xfinishdraw(void) {}
void xloadcols(void) {}
int xsetcolorname(int i,const char *s) { palette_unavailable=1; return 1; }
int xgetcolor(int i,unsigned char *r,unsigned char *g,unsigned char *b) { palette_unavailable=1; return 1; }
void xseticontitle(char *s) { free(icon); icon=xstrdup(s ? s : "st"); }
void xsettitle(char *s) { free(title); title=xstrdup(s ? s : "st"); }
int xsetcursor(int i) { if (i < 0 || i > 7) return 1; cursor_style=i; return 0; }
void xsetmode(int set,unsigned int mode) { MODBIT(frontend_mode,set,mode); }
void xsetpointermotion(int i) {}
void xsetsel(char *s) { free(clipboard); clipboard=s; }
int xstartdraw(void) { return 1; }
void xximspot(int x,int y) {}

typedef struct Peer { uint64_t id; int fd; char *bytes; size_t length; struct Peer *next; } Peer;
static Peer *peers;
static Peer *peer(Session *s) {
    uint64_t id=session_view(s)->id;
    for(Peer *p=peers;p;p=p->next)if(p->id==id)return p;
    int fds[2];assert(socketpair(AF_UNIX,SOCK_STREAM,0,fds)==0);
    fcntl(fds[0],F_SETFL,O_NONBLOCK);fcntl(fds[1],F_SETFL,O_NONBLOCK);
    s->ptyfd=fds[0];
    Peer *p=calloc(1,sizeof(*p));assert(p);
    p->id=id;p->fd=fds[1];p->next=peers;peers=p;return p;
}
static unsigned unhex(char c) {
    if(c>='0' && c<='9')return c-'0';
    if(c>='a' && c<='f')return c-'a'+10;
    assert(0);return 0;
}
static void drain(Session *s) {
    Peer *p=peer(s);char buf[4096];ssize_t n;
    do {
        session_flush(s);
        while((n=read(p->fd,buf,sizeof buf))>0) {
            p->bytes=xrealloc(p->bytes,p->length+n);
            memcpy(p->bytes+p->length,buf,n);p->length+=n;
        }
    } while(session_pending(s));
}
static void feedhex(Session *s,const char *hex) {
    size_t n=strcspn(hex,"\r\n")/2; char bytes[64];
    for(size_t pos=0;pos<n;) {
        size_t len=MIN(sizeof bytes,n-pos);
        for(size_t i=0;i<len;i++)bytes[i]=(unhex(hex[2*(pos+i)])<<4)|unhex(hex[2*(pos+i)+1]);
        session_feed(s,bytes,len);drain(s);pos+=len;
    }
}
static void hexout(const char *s, size_t n) {
    putchar('"');
    for (size_t i=0;i<n;i++) printf("%02x",(unsigned char)s[i]);
    puts("\"");
}
static void cellout(Glyph g) { printf("[%u,%u,%u,%u]",g.u,g.mode,g.fg,g.bg); }
static void dump(int model) {
    printf("{\"session_id\":%llu,\"columns\":%d,\"rows\":%d,\"cursor_x\":%d,\"cursor_y\":%d,\"cursor_style\":%d,\"view_offset\":%d,\"mode\":%d,\"frontend\":%u,\"pending\":%d,\"origin\":%d,\"top\":%d,\"bottom\":%d,\"history\":%d,\"bells\":%d,\"selection\":[%d,%d,%d,%d],\"rectangular_selection\":%d,\"pen\":",
        (unsigned long long)session_view(session_current())->id,term.col,term.row,term.c.x,term.c.y,cursor_style,term.scr,term.mode,frontend_mode,
        !!(term.c.state & CURSOR_WRAPNEXT),!!(term.c.state & CURSOR_ORIGIN),term.top,term.bot,term.histlen,bells,
        sel.ob.x==-1?-1:sel.nb.x,sel.ob.x==-1?-1:sel.nb.y,sel.ob.x==-1?-1:sel.ne.x,sel.ob.x==-1?-1:sel.ne.y,sel.type==SEL_RECTANGULAR);
    cellout(term.c.attr);
    printf(",\"charset\":[%d,%d,%d,%d],\"tabs\":[",term.trantbl[0],term.trantbl[1],term.trantbl[2],term.trantbl[3]);
    for(int x=0;x<term.col;x++) printf("%s%d",x?",":"",!!term.tabs[x]);
    printf("],\"dirty\":[");
    for(int y=0;y<term.row;y++) printf("%s%d",y?",":"",!!term.dirty[y]);
    printf("],\"cells\":[");
    for(int y=0;y<term.row;y++) for(int x=0;x<term.col;x++) {
        if(x || y) putchar(',');
        cellout((model ? term.line[y] : TLINE(y))[x]);
    }
    puts("]}");
}
int main(int argc,char **argv) {
    if(argc!=3) return 2;
    init(atoi(argv[1]),atoi(argv[2]));
    peer(session_current());
    iofd=open("/dev/null",O_WRONLY);assert(iofd>=0);
    char *line=NULL;size_t cap=0;int focused=0;
    puts("{}"); fflush(stdout);
    while(getline(&line,&cap,stdin)>0) {
        int a=0,b=0,c=0,d=0;
        sscanf(line+1,"%d %d %d %d",&a,&b,&c,&d);
        switch(line[0]) {
        case 'W':
            memset(term.dirty,0,term.row*sizeof(*term.dirty));
            feedhex(session_current(),line+2);
            puts(palette_unavailable ? "{\"unsupported\":\"dynamic Xft palette requires a real display; headless callback unavailable\"}" : "null"); break;
        case 'w': {
            int offset=0;sscanf(line+2,"%d %n",&a,&offset);
            Session *s=session_at(a);assert(s);feedhex(s,line+2+offset);puts("null");break;
        }
        case 'N': {
            Session *s=session_new(term.col,term.row);assert(s);peer(s);
            session_switch(s,focused);puts("null");break;
        }
        case 'L': {
            Session *s=session_at(a);assert(s);int wasactive=s==session_active();
            session_close(s);assert(session_count());
            if(wasactive && focused && (frontend_mode & MODE_FOCUS))ttywrite("\033[I",3,0);
            puts("null");break;
        }
        case 'Z': assert(session_at(a));session_switch(session_at(a),focused);puts("null");break;
        case 'Y': printf("[%zu,%zu]\n",session_count(),session_index(session_active()));break;
        case 'F': focused=a;puts("null");break;
        case 'P': draw();puts("null");break;
        case 'J': {
            size_t n=strcspn(line+2,"\r\n")/2;
            char *buf=xmalloc(n+1);
            for(size_t i=0;i<n;i++) { buf[i]=(unhex(line[2+2*i])<<4)|unhex(line[3+2*i]); }
            for(size_t pos=0;pos<n;pos+=1024) { ttywrite(buf+pos,MIN(n-pos,1024),1);drain(session_current()); } free(buf); puts("null"); break;
        }
        case 'S': dump(a); break;
        case 'O': allowwindowops=a; puts("null"); break;
        case 'R': { Session *old=session_current(); for(Session *s=head;s;s=s->next){session_bind(s);tresize(a,b);}session_bind(old);puts("null");break; }
        case 'U': kscrollup(&(Arg){.i=a}); puts("null"); break;
        case 'D': kscrolldown(&(Arg){.i=a}); puts("null"); break;
        case 'I': { Session *s=line[1]==' '?session_at(a):session_current();assert(s);drain(s);Peer *p=peer(s);hexout(p->bytes,p->length);p->length=0;break; }
        case 'B': LIMIT(a,0,term.col-1); LIMIT(b,0,term.row-1); selstart(a,b,c); puts("null"); break;
        case 'E': LIMIT(a,0,term.col-1); LIMIT(b,0,term.row-1); selextend(a,b,c,d); puts("null"); break;
        case 'V': if(a>=0 && a<term.row) term.line[a][term.col-1].mode|=ATTR_WRAP; puts("null"); break;
        case 'C': selclear(); puts("null"); break;
        case 'G': { char *s=getsel(); hexout(s?s:"",s?strlen(s):0); free(s); break; }
        case 'T': { const char *raw=title?title:"st";size_t size=strlen(raw)+80;char *name=xmalloc(size);if(session_count()>1)snprintf(name,size,"[%zu/%zu] %s",session_index(session_active())+1,session_count(),raw);else snprintf(name,size,"%s",raw);hexout(name,strlen(name));free(name);break; }
        case 'A':
            putchar('[');
            for(int y=0;y<term.histlen+term.row;y++) {
                Line row=y<term.histlen ? term.hist[(term.histi-term.histlen+y+1+HISTSIZE)%HISTSIZE] : term.line[y-term.histlen];
                if(y) putchar(',');
                putchar('[');
                for(int x=0;x<term.col;x++) { if(x) putchar(','); cellout(row[x]); }
                putchar(']');
            }
            puts("]"); break;
        case 'Q': goto done;
        default: return 3;
        }
        fflush(stdout);
    }
done:
    free(line);cleanup();
    while(peers){Peer *p=peers;peers=p->next;close(p->fd);free(p->bytes);free(p);}
    return 0;
}

#define _POSIX_C_SOURCE 200809L
/* Test-only wire adapter around the real st core. No terminal model. */
#include <sys/socket.h>
#define ST_REFERENCE_BRIDGE
#define main existing_tests_main
#include "../test_terminal.c"
#undef main

static unsigned int frontend_mode;
static int palette_unavailable;
static int cursor_style = 1, bells;
static char *title, *icon;
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

static char *replies;
static size_t replies_len;
static unsigned unhex(char c) {
    if(c>='0' && c<='9')return c-'0';
    if(c>='a' && c<='f')return c-'a'+10;
    assert(0);return 0;
}
static void drain(int fd) {
    char buf[4096];ssize_t n;
    while((n=read(fd,buf,sizeof buf))>0) {
        replies=xrealloc(replies,replies_len+n);
        memcpy(replies+replies_len,buf,n);replies_len+=n;
    }
}
static void hexout(const char *s, size_t n) {
    putchar('"');
    for (size_t i=0;i<n;i++) printf("%02x",(unsigned char)s[i]);
    puts("\"");
}
static void cellout(Glyph g) { printf("[%u,%u,%u,%u]",g.u,g.mode,g.fg,g.bg); }
static void dump(int model) {
    printf("{\"columns\":%d,\"rows\":%d,\"cursor_x\":%d,\"cursor_y\":%d,\"cursor_style\":%d,\"view_offset\":%d,\"mode\":%d,\"frontend\":%u,\"pending\":%d,\"origin\":%d,\"top\":%d,\"bottom\":%d,\"history\":%d,\"bells\":%d,\"selection\":[%d,%d,%d,%d],\"rectangular_selection\":%d,\"pen\":",
        term.col,term.row,term.c.x,term.c.y,cursor_style,term.scr,term.mode,frontend_mode,
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
    int pair[2];
    assert(socketpair(AF_UNIX,SOCK_STREAM,0,pair)==0);
    cmdfd=pair[0]; fcntl(pair[1],F_SETFL,O_NONBLOCK);
    init(atoi(argv[1]),atoi(argv[2]));
    iofd=open("/dev/null",O_WRONLY); assert(iofd>=0);
    char *line=NULL, *pending=NULL; size_t cap=0, pendinglen=0;
    puts("{}"); fflush(stdout);
    while(getline(&line,&cap,stdin)>0) {
        int a=0,b=0,c=0,d=0;
        sscanf(line+1,"%d %d %d %d",&a,&b,&c,&d);
        switch(line[0]) {
        case 'W': {
            size_t n=strcspn(line+2,"\r\n")/2;
            pending=xrealloc(pending,pendinglen+n+1);
            for(size_t i=0;i<n;i++) { pending[pendinglen+i]=(unhex(line[2+2*i])<<4)|unhex(line[3+2*i]); }
            pendinglen+=n;
            memset(term.dirty,0,term.row*sizeof(*term.dirty));
            size_t pos=0;
            while(pos<pendinglen) {
                size_t used=twrite(pending+pos,MIN(pendinglen-pos,64),0);
                if(!used)break;
                pos+=used;drain(pair[1]);
            }
            pendinglen-=pos; memmove(pending,pending+pos,pendinglen);
            puts(palette_unavailable ? "{\"unsupported\":\"dynamic Xft palette requires a real display; headless callback unavailable\"}" : "null"); break;
        }
        case 'J': {
            size_t n=strcspn(line+2,"\r\n")/2;
            char *buf=xmalloc(n+1);
            for(size_t i=0;i<n;i++) { buf[i]=(unhex(line[2+2*i])<<4)|unhex(line[3+2*i]); }
            for(size_t pos=0;pos<n;pos+=1024) { ttywrite(buf+pos,MIN(n-pos,1024),1);drain(pair[1]); } free(buf); puts("null"); break;
        }
        case 'S': dump(a); break;
        case 'O': allowwindowops=a; puts("null"); break;
        case 'R': tresize(a,b); puts("null"); break;
        case 'U': kscrollup(&(Arg){.i=a}); puts("null"); break;
        case 'D': kscrolldown(&(Arg){.i=a}); puts("null"); break;
        case 'I': drain(pair[1]); hexout(replies,replies_len); replies_len=0; break;
        case 'B': LIMIT(a,0,term.col-1); LIMIT(b,0,term.row-1); selstart(a,b,c); puts("null"); break;
        case 'E': LIMIT(a,0,term.col-1); LIMIT(b,0,term.row-1); selextend(a,b,c,d); puts("null"); break;
        case 'V': if(a>=0 && a<term.row) term.line[a][term.col-1].mode|=ATTR_WRAP; puts("null"); break;
        case 'C': selclear(); puts("null"); break;
        case 'G': { char *s=getsel(); hexout(s?s:"",s?strlen(s):0); free(s); break; }
        case 'T': hexout(title?title:"st",strlen(title?title:"st")); break;
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
    free(line); free(pending); free(title); free(icon);free(replies);close(iofd);
    cleanup(); close(pair[0]); close(pair[1]); return 0;
}

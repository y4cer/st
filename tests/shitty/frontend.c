/* X11 event lookup is supplied by the test; routing/encoding is real x.c. */
#define _POSIX_C_SOURCE 200809L
#define ST_FRONTEND_BRIDGE
#include "../test_x11.c"
static KeySym input_key;
static char input_text[64];
static int input_length;
int XLookupString(XKeyEvent *e,char *buf,int cap,KeySym *key,XComposeStatus *status) {
    *key=input_key;
    assert(input_length<=cap);
    memcpy(buf,input_text,input_length);
    return input_length;
}
XWMHints *XGetWMHints(Display *d,Window w) { return NULL; }
int main(void) {
    char *line=NULL; size_t cap=0;
    while(getline(&line,&cap,stdin)>0) {
        unsigned mode=0,mods=0; unsigned long sym=0; char op;
        int offset=0;
        assert(sscanf(line,"%c %u %u %lu %n",&op,&mode,&mods,&sym,&offset)>=4);
        win.mode=mode; delivered_len=0;
        if(op=='K') {
            input_key=sym; input_length=0;
            char *hex=line+offset;
            while(hex[0] && hex[1] && hex[0]!='\n') {
                unsigned v; assert(sscanf(hex,"%2x",&v)==1);
                assert(input_length<(int)sizeof input_text);
                input_text[input_length++]=v; hex+=2;
            }
            /* UI shortcuts are not terminal input and require a real window. */
            int shortcut=0;
            for(size_t i=0;i<LEN(shortcuts);i++)
                if(input_key==shortcuts[i].keysym && match(shortcuts[i].mod,mods)) shortcut=1;
            if(shortcut) { puts("null"); fflush(stdout); continue; }
            XEvent event={0}; event.xkey.state=mods; kpress(&event);
        } else if(op=='F') {
            XEvent event={0}; event.type=sym?FocusIn:FocusOut; focus(&event);
        } else if(op=='P') {
            char payload[4096]; size_t n=0; char *hex=line+offset;
            while(hex[0] && hex[1] && hex[0]!='\n') {
                unsigned v; assert(sscanf(hex,"%2x",&v)==1); assert(n+1<sizeof payload); payload[n++]=v; hex+=2;
            }
            payload[n]=0; event(SelectionNotify,101,payload);
        } else if(op=='M') {
            int type,button,x,y,width,height,held;
            assert(sscanf(line+offset,"%d %d %d %d %d %d %d",&type,&button,&x,&y,&width,&height,&held)==7);
            win.cw=win.ch=1; win.tw=width; win.th=height;
            win.w=width+2*borderpx;win.h=height+2*borderpx;
            buttons=held;
            XEvent ev={0};ev.type=type==0?ButtonPress:type==1?ButtonRelease:MotionNotify;
            ev.xbutton.button=button;ev.xbutton.x=x+borderpx;ev.xbutton.y=y+borderpx;ev.xbutton.state=mods;
            mousereport(&ev);
        } else return 3;
        putchar('"');
        for(size_t i=0;i<delivered_len;i++)printf("%02x",(unsigned char)delivered[i]);
        puts("\"");fflush(stdout);
    }
    free(line); return 0;
}

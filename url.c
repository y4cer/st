/* Plain web URLs in the actual terminal/history or immutable copy snapshot.
 * Included by st.c; presentation never modifies stored glyphs. */
#define URL_MAX 4096
#define URL_NONE SIZE_MAX

static int
urlhistory(void)
{
    return tisaltscr() ? 0 : term.histlen;
}

static int
urlrows(void)
{
    return br.active ? br.rows : urlhistory() + term.row;
}

static Line
urlline(int row)
{
    if (br.active) return br.cells + (size_t)row * br.cols;
    if (row < urlhistory())
        return term.hist[(term.histi - term.histlen + row + HISTSIZE + 1) % HISTSIZE];
    return term.line[row - urlhistory()];
}

static Glyph
urlglyph(size_t p)
{
    return urlline(p / term.col)[p % term.col];
}

static size_t
urlnext(size_t p)
{
    if (p % term.col + 1 < (size_t)term.col) return p + 1;
    if (p / term.col + 1 < (size_t)urlrows() && tlinewrapped(urlline(p / term.col))) return p + 1;
    return URL_NONE;
}

static size_t
urlprev(size_t p)
{
    if (!p) return URL_NONE;
    if (p % term.col || tlinewrapped(urlline(p / term.col - 1))) return p - 1;
    return URL_NONE;
}

static int
urlword(Rune u)
{
    return u >= 128 || (u >= 'a' && u <= 'z') || (u >= 'A' && u <= 'Z') ||
           (u >= '0' && u <= '9') || u == '_' || u == '-' || u == '.';
}

static int
urlstop(Rune u)
{
    return u <= 32 || u == 127 || u == '<' || u == '>' || u == '"' ||
           u == '\'' || u == '`' || u == '\\' || u == 0xa0 ||
           (u >= 0x2000 && u <= 0x200f) || (u >= 0x2018 && u <= 0x201f) ||
           u == 0x2028 || u == 0x2029 || u == 0x3000;
}

static int
urlprefix(size_t p, const char *prefix)
{
    for (; *prefix; prefix++) {
        if (p == URL_NONE) return 0;
        Glyph g = urlglyph(p);
        Rune u = g.u;
        if (g.mode & (ATTR_INVISIBLE | ATTR_WDUMMY)) return 0;
        if (u >= 'A' && u <= 'Z') u += 'a' - 'A';
        if (u != (unsigned char)*prefix) return 0;
        p = urlnext(p);
    }
    return 1;
}

static size_t
urlcandidate(size_t start, char text[URL_MAX + 1], int *www)
{
    size_t previous = urlprev(start), p = start, end = start, length = 0;
    int prefix, parentheses = 0, brackets = 0, braces = 0;
    if (previous != URL_NONE && (urlglyph(previous).mode & ATTR_WDUMMY)) previous = urlprev(previous);
    if (previous != URL_NONE && urlword(urlglyph(previous).u)) return URL_NONE;
    *www = 0;
    if (urlprefix(start, "https://")) prefix = 8;
    else if (urlprefix(start, "http://")) prefix = 7;
    else if (urlprefix(start, "www.")) { prefix = 4; *www = 1; }
    else return URL_NONE;
    for (int steps = 0; p != URL_NONE; steps++) {
        Glyph g = urlglyph(p);
        if (steps >= URL_MAX * 2 || (g.mode & ATTR_INVISIBLE)) return URL_NONE;
        if (g.mode & ATTR_WDUMMY) { end = p + 1; p = urlnext(p); continue; }
        if (urlstop(g.u)) break;
        char encoded[4];
        size_t n = utf8encode(g.u, encoded);
        if (length + n > URL_MAX) return URL_NONE; /* never open a truncated URL */
        memcpy(text + length, encoded, n); length += n;
        parentheses += (g.u == '(') - (g.u == ')');
        brackets += (g.u == '[') - (g.u == ']');
        braces += (g.u == '{') - (g.u == '}');
        end = p + 1; p = urlnext(p);
    }
    while (length > (size_t)prefix) {
        char c = text[length - 1];
        if (strchr(".,;:!?", c)) {}
        else if (c == ')' && parentheses < 0) parentheses++;
        else if (c == ']' && brackets < 0) brackets++;
        else if (c == '}' && braces < 0) braces++;
        else break;
        length--; end--;
    }
    if (length <= (size_t)prefix || strchr("/?#.:;()]{}", text[prefix])) return URL_NONE;
    text[length] = 0;
    return end;
}

static char *
urlscan(int y, int click, unsigned char *mask, int columns, int hx, int hy)
{
    int height = br.active ? MAX(1, term.row - 1) : term.row;
    int top = br.active ? br.top : urlhistory() - term.scr;
    if (y < 0 || y >= height || top + y >= urlrows()) return NULL;
    size_t rowstart = (size_t)(top + y) * term.col, rowend = rowstart + term.col;
    size_t hover = hx >= 0 && hx < term.col && hy >= 0 && hy < height
                 ? (size_t)(top + hy) * term.col + hx : URL_NONE;
    size_t first = rowstart;
    for (int i = 0; i < URL_MAX * 2; i++) {
        size_t previous = urlprev(first);
        if (previous == URL_NONE) break;
        Glyph g = urlglyph(previous);
        /* Only the token touching this row can continue into it. */
        if (!(g.mode & ATTR_WDUMMY) && urlstop(g.u)) break;
        first = previous;
    }
    for (size_t p = first; p < rowend; ) {
        Rune u = urlglyph(p).u;
        if (u == 'h' || u == 'H' || u == 'w' || u == 'W') {
            char text[URL_MAX + 1]; int www;
            size_t end = urlcandidate(p, text, &www);
            if (end != URL_NONE) {
                if (mask && end > rowstart)
                    for (size_t x = MAX(p, rowstart); x < MIN(end, rowstart + columns); x++) mask[x - rowstart] = p <= hover && hover < end ? 2 : 1;
                if (click >= 0 && p <= rowstart + click && end > rowstart + click) {
                    char *result = xmalloc(strlen(text) + (www ? 9 : 1));
                    sprintf(result, "%s%s", www ? "https://" : "", text);
                    return result;
                }
                p = end;
                continue;
            }
        }
        p++;
    }
    return NULL;
}

char *
turlat(int x, int y)
{
    if (x < 0 || x >= term.col) return NULL;
    return urlscan(y, x, NULL, 0, -1, -1);
}

void
turlmask(int y, unsigned char *mask, int columns, int hx, int hy)
{
    memset(mask, 0, columns);
    urlscan(y, -1, mask, MIN(columns, term.col), hx, hy);
}

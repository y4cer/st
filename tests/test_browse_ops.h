/* Native operator/motion tests: real immutable copy snapshot and clipboard.
 * Shitty selection/Unicode/wrap invariants are referenced in shitty/VIM.md. */
static void browsekeys(const char *keys)
{
    while (*keys) key((unsigned char)*keys++);
}
static void browseat(int x, int y)
{
    assert(br.active && !br.yank);
    br.x = x; br.y = y;
}
static void yankeq(const char *keys, const char *expected)
{
    int before = copies;
    browsekeys(keys);
    assert(copies == before + 1);
    if (strcmp(clipboard, expected))
        fprintf(stderr, "%s: got <%s> expected <%s>\n", keys, clipboard, expected);
    assert(!strcmp(clipboard, expected));
    assert(!br.yank && !br.visual && br.flashing);
}
static void copy_operator_words(void)
{
    init(40, 5); feed("one two three\r\nfour five"); browse(NULL);
    browseat(0, 0); yankeq("yw", "one "); assert(br.x == 0 && br.y == 0);
    browseat(0, 0); yankeq("ye", "one");
    browseat(4, 0); yankeq("yb", "one "); assert(br.x == 0);
    browseat(8, 0); yankeq("yw", "three");
    browseat(8, 0); yankeq("y2w", "three\nfour ");
    browseat(1, 0); yankeq("y$", "ne two three");
    browseat(6, 0); yankeq("y0", "one tw"); assert(br.x == 0);
    browseat(4, 0); yankeq("yh", " "); assert(br.x == 3);
    browseat(4, 0); yankeq("yl", "t"); assert(br.x == 4);
}
static void copy_operator_counts(void)
{
    init(50, 5); feed("one two three four five six seven\r\nsecond\r\nthird"); browse(NULL);
    browseat(0, 0); yankeq("2yw", "one two ");
    browseat(0, 0); yankeq("y2w", "one two ");
    browseat(0, 0); yankeq("2y3w", "one two three four five six ");
    browseat(4, 0); yankeq("2yy", "one two three four five six seven\nsecond\n");
    browseat(4, 0); yankeq("y2$", "two three four five six seven\nsecond");
    browseat(0, 0); yankeq("y999999999999w", "one two three four five six seven\nsecond\nthird\n\n");
}
static void copy_operator_lines(void)
{
    init(16, 4); feed("first\r\nsecond\r\nthird\r\nlast"); browse(NULL);
    browseat(2, 0); browsekeys("yk"); assert(copies == 0 && br.x == 2 && br.y == 0);
    browseat(2, 3); browsekeys("yj"); assert(copies == 0 && br.x == 2 && br.y == 3);
    browseat(2, 1); yankeq("yy", "second\n"); assert(br.x == 2 && br.y == 1);
    browseat(2, 1); yankeq("yj", "second\nthird\n");
    browseat(2, 1); yankeq("yk", "first\nsecond\n"); assert(br.x == 2 && br.y == 0);
    browseat(2, 1); yankeq("yG", "second\nthird\nlast\n");
    browseat(2, 2); yankeq("ygg", "first\nsecond\nthird\n");
    browseat(2, 2); yankeq("y2gg", "second\nthird\n");
    browseat(2, 0); yankeq("y2G", "first\nsecond\n");
    browseat(2, 3); yankeq("2yy", "last\n");
}
static void copy_operator_pending(void)
{
    init(30, 4); feed("hello world"); browse(NULL); browseat(0, 0);
    key(XK_y); assert(br.yank && copies == 0 && !br.flashing);
    key(XK_Escape); assert(!br.yank && br.active && copies == 0);
    browsekeys("2y3"); assert(br.yankcount == 2 && br.count == 3 && copies == 0);
    browsedraw();
    char status[31];
    for (int x = 0; x < 30; x++) status[x] = br.view[x].u;
    status[30] = 0; assert(strstr(status, "2y3"));
    key(XK_Escape); assert(!br.yank && !br.count);
    browsekeys("ygz"); assert(!br.yank && copies == 0);
    browsekeys("yh"); assert(!br.yank && copies == 0); /* empty motion */
    browsekeys("yl"); assert(copies == 1 && !strcmp(clipboard, "h"));
    browsekeys("yq"); assert(!br.active && copies == 1);
}
static void copy_operator_punctuation(void)
{
    init(40, 4); feed("  foo.bar baz_qux end"); browse(NULL);
    browseat(2, 0); yankeq("yw", "foo");
    browseat(2, 0); yankeq("yW", "foo.bar ");
    browseat(2, 0); yankeq("yE", "foo.bar");
    browseat(10, 0); yankeq("yB", "foo.bar ");
    browseat(10, 0); yankeq("y^", "foo.bar ");
    browseat(0, 0); yankeq("y^", "  ");
    browseat(10, 0); yankeq("ye", "baz_qux");
}
static void copy_operator_wide_wrap(void)
{
    init(6, 4); feed("ab界界cd end"); browse(NULL);
    browseat(0, 0); yankeq("yw", "ab界界cd ");
    browseat(2, 0); yankeq("yl", "界");
    browseat(3, 0); yankeq("yl", "界"); /* start on dummy normalizes */
    browseat(4, 0); yankeq("yh", "界");
    browseat(0, 0); yankeq("y2$", "ab界界cd end");
    browseat(0, 0); yankeq("2yy", "ab界界cd end\n");
    assert(br.cells[2].mode & ATTR_WIDE);
    assert(br.cells[3].mode & ATTR_WDUMMY);
}
static void copy_operator_snapshot(void)
{
    history(); browse(NULL); browseat(0, 0);
    key(XK_y); feed("\033cNEW LIVE TEXT");
    key(XK_dollar); assert(!strcmp(clipboard, "oldest"));
    assert(br.active && term.line[0][0].u == 'N');
    key(XK_y); tresize(14, 4); assert(!br.active && !br.yank);
}
static void copy_operator_session(void)
{
    init(20, 3); feed("one two"); browse(NULL); browseat(0, 0); key(XK_y);
    Session *first = session_current(), *second = session_new(20, 3);
    session_select(second); feed("other value"); browse(NULL); browseat(0, 0);
    assert(!br.yank); yankeq("yw", "other ");
    session_select(first); assert(br.yank); key(XK_w);
    assert(!strcmp(clipboard, "one ") && copies == 2);
}
static void copy_operator_empty_lines(void)
{
    init(16, 4); feed("one\r\n\r\ntwo three\r\n"); browse(NULL);
    browseat(0, 0); yankeq("2yw", "one\n\n");
    browseat(0, 2); yankeq("yb", "\n");
    browseat(4, 2); yankeq("y2b", "\ntwo ");
    browseat(0, 1); yankeq("y$", "");
    browseat(0, 1); yankeq("ye", "\ntwo");
    browseat(0, 1); yankeq("yw", "\n");
    browseat(4, 2); yankeq("2yw", "three");
    browseat(0, 3); yankeq("yw", "");
    /* First-nonblank backwards boundary is linewise, later words are not. */
    key(XK_q); feed("\033cone\r\ntwo\r\none two\r\nnext"); browse(NULL);
    browseat(0, 1); yankeq("yb", "one\n");
    browseat(0, 3); yankeq("yb", "two");
    browseat(0, 3); yankeq("y2b", "one two\n");
}
static void copy_operator_padding_bounds(void)
{
    init(40, 4); feed("one\r\n\r\n\r\nlast"); browse(NULL);
    browseat(20, 3); browsekeys("yw");
    assert(br.x == 20 && br.y == 3 && copies == 0 && !br.yank);
    browsekeys("ywy"); /* Previously left y == rows, then read past cells. */
    assert(br.x == 20 && br.y == 3 && br.yank && copies == 0);
    key(XK_Escape); assert(br.active && !br.yank);
    key(XK_q); feed("\033cone"); browse(NULL);
    browseat(20, 3); browsekeys("ywy");
    assert(br.x == 20 && br.y == 3 && br.yank);
    key(XK_Escape); assert(br.active && !br.yank);
}
#define BROWSE_OPERATOR_TESTS \
    T(copy_operator_words), T(copy_operator_counts), T(copy_operator_lines), \
    T(copy_operator_pending), T(copy_operator_punctuation), T(copy_operator_wide_wrap), \
    T(copy_operator_snapshot), T(copy_operator_session), \
    T(copy_operator_empty_lines), T(copy_operator_padding_bounds),

/* Read-only Vim-style copy mode. Included by st.c to access terminal cells.
 * The snapshot is independent of the live terminal and its scrollback ring.
 */

int
browseactive(void)
{
	return br.active;
}

/* Remaining milliseconds also schedule a redraw when the terminal is idle. */
double
browsetimeout(void)
{
	struct timespec now;
	double remaining;
	if (!br.active || !br.flashing) return -1;
	clock_gettime(CLOCK_MONOTONIC, &now);
	remaining = (br.flashuntil.tv_sec - now.tv_sec) * 1000.0 +
	            (br.flashuntil.tv_nsec - now.tv_nsec) / 1000000.0;
	if (remaining > 0) return remaining;
	br.flashing = 0;
	tfulldirt();
	return 0; /* ensure a final redraw even if expiry occurred after draw() */
}

static void
browseclose(void)
{
	free(br.cells);
	free(br.view);
	memset(&br, 0, sizeof(br));
	tfulldirt();
}

void
browse(const Arg *unused)
{
	int i, history = IS_SET(MODE_ALTSCREEN) ? 0 : term.histlen;
	(void)unused;
	if (br.active) {
		browseclose();
		return;
	}
	xpastecancel();
	br.cols = term.col;
	br.rows = history + term.row;
	br.cells = xmalloc((size_t)br.rows * br.cols * sizeof(Glyph));
	br.view = xmalloc((size_t)br.cols * sizeof(Glyph));
	for (i = 0; i < history; i++)
		memcpy(br.cells + (size_t)i * br.cols,
		       term.hist[(term.histi - history + i + HISTSIZE + 1) % HISTSIZE],
		       br.cols * sizeof(Glyph));
	for (i = 0; i < term.row; i++)
		memcpy(br.cells + (size_t)(history + i) * br.cols,
		       term.line[i], br.cols * sizeof(Glyph));
	br.top = MAX(0, history - term.scr);
	br.y = MIN(br.rows - 1, br.top + term.c.y);
	br.x = term.c.x;
	br.direction = 1;
	br.active = 1;
	selclear();
	tfulldirt();
}

static int
browsepos(void)
{
	return br.y * br.cols + br.x;
}

static void
browserange(int *start, int *end)
{
	*start = MIN(br.anchor, browsepos());
	*end = MAX(br.anchor, browsepos());
	if (br.visual == 2) {
		*start = *start / br.cols * br.cols;
		*end = (*end / br.cols + 1) * br.cols - 1;
	}
	/* A selection touching a wide continuation includes its leading cell. */
	if (*start % br.cols && (br.cells[*start].mode & ATTR_WDUMMY)) (*start)--;
	if (*end % br.cols < br.cols - 1 && (br.cells[*end].mode & ATTR_WIDE)) (*end)++;
}

static int
browsewrapped(int row)
{
    Glyph *line = br.cells + (size_t)row * br.cols;
    return (line[br.cols - 1].mode & ATTR_WRAP) ||
           (br.cols > 1 && (line[br.cols - 1].mode & ATTR_WDUMMY) &&
            (line[br.cols - 2].mode & ATTR_WRAP));
}

static void
browseyank(void)
{
	int start, end, y, x, first, last, linelast;
	char *text, *p;
	Glyph *line;
	if (!br.visual) {
		br.anchor = browsepos();
		br.visual = 2;
	}
	browserange(&start, &end);
	text = p = xmalloc((size_t)(end - start + 1) * UTF_SIZ + br.rows + 1);
	for (y = start / br.cols; y <= end / br.cols; y++) {
		line = br.cells + (size_t)y * br.cols;
		first = y == start / br.cols ? start % br.cols : 0;
		linelast = y == end / br.cols ? end % br.cols : br.cols - 1;
		last = linelast;
		/* Preserve explicit character selections and spaces at soft wraps. */
		if (linelast == br.cols - 1 && !browsewrapped(y))
			while (last >= first && line[last].u == ' ') last--;
		for (x = first; x <= last; x++)
			if (!(line[x].mode & ATTR_WDUMMY))
				p += utf8encode(line[x].u, p);
		if ((y < end / br.cols || br.visual == 2) &&
		    !browsewrapped(y))
			*p++ = '\n';
	}
	*p = '\0';
	xsetsel(text);
	xclipcopy();
	br.flashstart = start;
	br.flashend = end;
	br.flashing = 1;
	clock_gettime(CLOCK_MONOTONIC, &br.flashuntil);
	br.flashuntil.tv_nsec += 200000000L;
	if (br.flashuntil.tv_nsec >= 1000000000L) {
		br.flashuntil.tv_nsec -= 1000000000L;
		br.flashuntil.tv_sec++;
	}
	br.visual = 0;
}

static int
browseword(int p)
{
	Rune u = br.cells[p].u;
	if (u == ' ' || u == '\t') return 0;
	return u == '_' || iswalnum(u) ? 2 : 1;
}

static void
browsefind(int direction)
{
	int i, j, cell, p = browsepos(), total = br.rows * br.cols;
	if (!br.querylen) return;
	for (i = 1; i < total; i++) {
		int candidate = (p + direction * i + total) % total;
		if (br.cells[candidate].mode & ATTR_WDUMMY) continue;
		for (j = 0, cell = candidate; j < br.querylen && cell < total; j++, cell++) {
			while (cell < total && (br.cells[cell].mode & ATTR_WDUMMY)) cell++;
			if (cell >= total || br.cells[cell].u != br.query[j]) break;
		}
		if (j == br.querylen) {
			br.y = candidate / br.cols;
			br.x = candidate % br.cols;
			return;
		}
	}
}

/* A physical cell step that never lands on a wide continuation. */
static int
browsestep(int p, int direction)
{
    int total = br.rows * br.cols;
    do { p += direction; } while (p >= 0 && p < total && (br.cells[p].mode & ATTR_WDUMMY));
    return p;
}

static int
browseemptyline(int row)
{
    if (browsewrapped(row) || (row > 0 && browsewrapped(row - 1))) return 0;
    for (int x = 0; x < br.cols; x++)
        if (br.cells[(size_t)row * br.cols + x].u != ' ') return 0;
    return 1;
}

static int
browseclass(int p, int big)
{
    int kind = browseword(p);
    if (p % br.cols == 0 && browseemptyline(p / br.cols)) return 3;
    return big && kind ? 2 : kind;
}

static int
browseboundary(int left, int right)
{
    return left / br.cols != right / br.cols && !browsewrapped(left / br.cols);
}

static int
browsewordmotion(int p, unsigned long key, int n, int *laststep)
{
    int total = br.rows * br.cols, next, old, kind;
    int big = key == XK_W || key == XK_B || key == XK_E;
    while (n--) {
        old = p;
        if (laststep) *laststep = p;
        if (key == XK_b || key == XK_B) {
            p = MAX(0, browsestep(p, -1));
            while (p > 0 && !browseclass(p, big)) p = MAX(0, browsestep(p, -1));
            kind = browseclass(p, big);
            while ((next = browsestep(p, -1)) >= 0 &&
                   !browseboundary(next, p) && browseclass(next, big) == kind) p = next;
        } else if (key == XK_w || key == XK_W) {
            kind = browseclass(p, big);
            while ((next = browsestep(p, 1)) < total &&
                   !browseboundary(p, next) && browseclass(next, big) == kind) p = next;
            p = next;
            while (p < total && !browseclass(p, big)) p = browsestep(p, 1);
            if (p >= total) return total;
        } else {
            next = browsestep(p, 1);
            if (next >= total) break;
            p = next;
            while (p < total && (!browseclass(p, big) || browseclass(p, big) == 3)) p = browsestep(p, 1);
            if (p >= total) return total - 1;
            kind = browseclass(p, big);
            while ((next = browsestep(p, 1)) < total &&
                   !browseboundary(p, next) && browseclass(next, big) == kind) p = next;
        }
        if (p == old) break;
    }
    return p;
}

static int
browselast(int row)
{
    int p = (row + 1) * br.cols - 1, first = row * br.cols;
    while (p > first && br.cells[p].u == ' ') p--;
    if (br.cells[p].mode & ATTR_WDUMMY) p--;
    return MAX(first, p);
}

static int
browsefirst(int row)
{
    int p = row * br.cols, end = (row + 1) * br.cols - 1;
    while (p < end && !browseword(p)) p++;
    return browseword(p) ? p : row * br.cols;
}

/* 1: exclusive character motion; 2: inclusive; 3: complete physical rows. */
static int
browsemotion(unsigned long key, int n, int counted, int operator, int *laststep)
{
    int p = browsepos(), row = br.y, type = 1;
    switch (key) {
    case XK_h: case XK_Left:
        if (operator) while (n-- && p > row * br.cols) p = MAX(row * br.cols, browsestep(p, -1));
        else p = MAX(row * br.cols, p - n);
        break;
    case XK_l: case XK_Right:
        if (operator) while (n-- && p < (row + 1) * br.cols) p = MIN((row + 1) * br.cols, browsestep(p, 1));
        else p = MIN((row + 1) * br.cols - 1, p + n);
        break;
    case XK_k: case XK_Up: row = MAX(0, row - n); type = 3; break;
    case XK_j: case XK_Down: row = MIN(br.rows - 1, row + n); type = 3; break;
    case XK_0: case XK_Home: p = row * br.cols; break;
    case XK_asciicircum: p = browsefirst(row); break;
    case XK_dollar: case XK_End:
        row = MIN(br.rows - 1, row + n - 1); p = browselast(row); type = 2; break;
    case XK_g: row = counted ? MIN(br.rows, n) - 1 : 0; type = 3; break;
    case XK_G: row = counted ? MIN(br.rows, n) - 1 : br.rows - 1; type = 3; break;
    case XK_H: row = MIN(br.rows - 1, br.top + n - 1); type = 3; break;
    case XK_M: row = MIN(br.rows - 1, br.top + MAX(0, term.row - 2) / 2); type = 3; break;
    case XK_L: row = MIN(br.rows - 1, MAX(br.top, br.top + MAX(0, term.row - 2) - n + 1)); type = 3; break;
    case XK_w: case XK_W: case XK_b: case XK_B: case XK_e: case XK_E:
        p = browsewordmotion(p, key, n, laststep);
        type = key == XK_e || key == XK_E ? 2 : 1;
        break;
    default: return 0;
    }
    if (type == 3) p = !operator && (key == XK_g || key == XK_G)
                        ? browsefirst(row) : row * br.cols + br.x;
    /* An exclusive operator may point one cell past the buffer/row. */
    if (!operator) p = MIN(p, br.rows * br.cols - 1);
    br.x = p % br.cols; br.y = p / br.cols;
    return type;
}

static void
browsecanceloperator(int restore)
{
    if (restore && br.yank) {
        br.x = br.yankstart % br.cols; br.y = br.yankstart / br.cols;
    }
    br.yank = br.yankcount = br.yankstart = br.yankg = br.count = br.g = 0;
}

static void
browseoperator(unsigned long key, unsigned int state)
{
    int n, start = br.yankstart, target, end, type, counted, cursor;
    int row = start / br.cols, col = start % br.cols, laststep = start;
    if (state & (ControlMask | Mod1Mask) || key == XK_Escape || key == XK_q || key == XK_i) {
        browsecanceloperator(1);
        if (key == XK_q || key == XK_i || ((state & ControlMask) && (key == XK_c || key == XK_space))) browseclose();
        return;
    }
    if (!br.yankg && key >= XK_0 && key <= XK_9 && (key != XK_0 || br.count)) {
        br.count = MIN(10000, br.count * 10 + key - XK_0);
        return;
    }
    if (key == XK_g && !br.yankg) { br.yankg = 1; return; }
    if (br.yankg && key != XK_g) { browsecanceloperator(1); return; }
    counted = br.yankcount != 0 || br.count != 0;
    n = MIN(10000, MAX(1, br.yankcount) * MAX(1, br.count));
    br.x = col; br.y = row;
    if (key == XK_y) {
        br.y = MIN(br.rows - 1, row + n - 1); type = 3;
    } else type = browsemotion(key, n, counted, 1, &laststep);
    target = browsepos();
    if (!type || (type == 1 && target == start) ||
        (target == start && (key == XK_j || key == XK_k || key == XK_Up || key == XK_Down))) {
        browsecanceloperator(1); return;
    }
    cursor = type == 3 ? MIN(row, target / br.cols) * br.cols + col : MIN(start, target);
    if ((key == XK_dollar || key == XK_End) && target / br.cols == row && browseemptyline(row)) {
        target = start; cursor = start;
    }
    end = MAX(start, target);
    start = MIN(start, target);
    if (type == 1) {
        end--;
        /* Exclusive backwards motions ending at column zero become linewise
         * when their other endpoint is at/before its first nonblank. */
        if ((key == XK_b || key == XK_B) && (br.yankstart % br.cols) == 0 &&
            start / br.cols < row && start <= browsefirst(start / br.cols)) type = 3;
    }
    if ((key == XK_dollar || key == XK_End) && browseemptyline(end / br.cols))
        end = (end / br.cols + 1) * br.cols - 1;
    /* Vim's operator-w stops at the previous hard line's text when its
     * final motion would land on the next line's first word. */
    if (key == XK_w || key == XK_W) {
        int lastrow = laststep / br.cols;
        while (lastrow + 1 < br.rows && browsewrapped(lastrow)) lastrow++;
        if (target / br.cols > lastrow) {
            end = browselast(lastrow);
            if (browseemptyline(lastrow)) {
                end = (lastrow + 1) * br.cols - 1;
                if (target == br.rows * br.cols) {
                    /* EOF has no following hard break. An empty final row
                     * contributes no extra newline to an exclusive motion. */
                    if (lastrow == start / br.cols) type = 2;
                    else {
                        end = lastrow * br.cols - 1;
                        type = start <= browsefirst(start / br.cols) ? 3 : 2;
                    }
                } else if (start <= browsefirst(start / br.cols)) type = 3;
            } else if (br.cells[end].mode & ATTR_WIDE) end++;
        }
    }
    end = MIN(end, br.rows * br.cols - 1);
    if (end < start) { browsecanceloperator(1); return; }
    br.anchor = start;
    br.x = end % br.cols; br.y = end / br.cols;
    br.visual = type == 3 ? 2 : 1;
    browseyank();
    /* Forward yanks retain the origin; backwards yanks move to range start. */
    br.y = cursor / br.cols; br.x = cursor % br.cols;
    browsecanceloperator(0);
}

void
browseinput(unsigned long key, unsigned int state, const char *buf, int len)
{
    int n;
    Rune rune;
    size_t used;
    if (!br.active) return;
    if (br.searching) {
        if (key == XK_Escape) br.searching = 0;
        else if (key == XK_Return || key == XK_KP_Enter) {
            br.searching = 0; browsefind(br.direction);
        } else if (key == XK_BackSpace) {
            if (br.querylen) br.querylen--;
        } else if (!(state & (ControlMask | Mod1Mask))) {
            while (len > 0 && br.querylen < (int)LEN(br.query)) {
                used = utf8decode(buf, &rune, len);
                if (!used) break;
                if (rune >= ' ') br.query[br.querylen++] = rune;
                buf += used; len -= used;
            }
        }
        tfulldirt(); return;
    }
    if (br.yank) { browseoperator(key, state); tfulldirt(); return; }
    n = br.count ? br.count : 1;
    if (state & ControlMask) {
        if (key == XK_u) br.y -= n * MAX(1, (term.row - 1) / 2);
        else if (key == XK_d) br.y += n * MAX(1, (term.row - 1) / 2);
        else if (key == XK_b) br.y -= n * MAX(1, term.row - 2);
        else if (key == XK_f) br.y += n * MAX(1, term.row - 2);
        else if (key == XK_c || key == XK_space) browseclose();
        br.count = br.g = 0;
    } else if (key >= XK_0 && key <= XK_9 && (key != XK_0 || br.count)) {
        br.count = MIN(10000, br.count * 10 + key - XK_0);
        tfulldirt(); return;
    } else {
        if (key != XK_g) br.g = 0;
        if (key == XK_g && !br.g) { br.g = 1; tfulldirt(); return; }
        if (key == XK_y && !br.visual) {
            br.yank = 1; br.yankcount = br.count; br.yankstart = browsepos();
            if (br.cells[br.yankstart].mode & ATTR_WDUMMY) br.yankstart--;
            br.count = br.g = 0; tfulldirt(); return;
        }
        if (!browsemotion(key, n, br.count != 0, 0, NULL)) switch (key) {
        case XK_Escape:
            if (br.visual) br.visual = 0; else browseclose();
            break;
        case XK_q: case XK_i: browseclose(); break;
        case XK_Page_Up: br.y -= n * MAX(1, term.row - 2); break;
        case XK_Page_Down: br.y += n * MAX(1, term.row - 2); break;
        case XK_v: case XK_V:
            if (br.visual == (key == XK_v ? 1 : 2)) br.visual = 0;
            else { br.anchor = browsepos(); br.visual = key == XK_v ? 1 : 2; }
            break;
        case XK_y: browseyank(); break;
        case XK_slash: case XK_question:
            br.searching = 1; br.querylen = 0;
            br.direction = key == XK_slash ? 1 : -1;
            break;
        case XK_n: browsefind(br.direction); break;
        case XK_N: browsefind(-br.direction); break;
        }
        br.count = br.g = 0;
    }
    if (br.active) {
        LIMIT(br.x, 0, br.cols - 1); LIMIT(br.y, 0, br.rows - 1);
    }
    tfulldirt();
}

static void
browsedraw(void)
{
	int x, y, row, pos, start = -1, end = -1;
	int height = MAX(1, term.row - 1);
	char status[128], pending[32] = "";
	Glyph blank = {.u = ' ', .fg = defaultfg, .bg = defaultbg};
	(void)browsetimeout();
	if (br.y < br.top) br.top = br.y;
	if (br.y >= br.top + height) br.top = br.y - height + 1;
	LIMIT(br.top, 0, MAX(0, br.rows - height));
	if (br.visual) browserange(&start, &end);
	for (y = 0; y < height; y++) {
		row = br.top + y;
		for (x = 0; x < br.cols; x++) {
			pos = row * br.cols + x;
			br.view[x] = row < br.rows ? br.cells[pos] : blank;
			if ((br.visual && pos >= start && pos <= end) ||
			    (row == br.y && (x == br.x ||
			     (x + 1 == br.x && (br.cells[row * br.cols + br.x].mode & ATTR_WDUMMY)))))
				br.view[x].mode ^= ATTR_REVERSE;
			if (br.flashing && pos >= br.flashstart && pos <= br.flashend) {
				br.view[x].mode &= ~(ATTR_REVERSE | ATTR_FAINT | ATTR_BLINK | ATTR_INVISIBLE);
				br.view[x].fg = defaultbg;
				br.view[x].bg = 3; /* palette yellow, fully opaque */
			}
		}
		xdrawline(br.view, 0, y, br.cols);
	}
	if (term.row > 1) {
		if (br.yank) {
            char before[12] = "", after[12] = "";
            if (br.yankcount) snprintf(before, sizeof(before), "%d", br.yankcount);
            if (br.count) snprintf(after, sizeof(after), "%d", br.count);
            snprintf(pending, sizeof(pending), " %sy%s%s", before, after, br.yankg ? "g" : "");
        } else if (br.count) snprintf(pending, sizeof(pending), " %d%s", br.count, br.g ? "g" : "");
        else if (br.g) strcpy(pending, " g");
        snprintf(status, sizeof(status), " COPY [RO]%s %s | %d/%d | v/V select, yy/y{motion} copy, / search, q exit ",
                 pending, br.visual == 2 ? "VISUAL LINE" : br.visual ? "VISUAL" : "NORMAL", br.y + 1, br.rows);
		for (x = 0; x < br.cols; x++) {
			br.view[x] = blank;
			br.view[x].mode = ATTR_REVERSE;
			if (br.searching) {
				br.view[x].u = x == 0 ? (br.direction > 0 ? '/' : '?') :
				               x <= br.querylen ? br.query[x - 1] : ' ';
			} else if (x < (int)strlen(status)) br.view[x].u = status[x];
		}
		xdrawline(br.view, 0, term.row - 1, br.cols);
	}
	xfinishdraw();
}

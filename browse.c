/* Read-only Vim-style copy mode. Included by st.c to access terminal cells.
 * The snapshot is independent of the live terminal and its scrollback ring.
 */
static struct {
	int active, cols, rows, top, x, y, anchor, visual, count, g;
	int searching, direction, querylen;
	int flashing, flashstart, flashend;
	struct timespec flashuntil;
	Rune query[128];
	Glyph *cells, *view;
} br;

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
		if (linelast == br.cols - 1 && !(line[linelast].mode & ATTR_WRAP))
			while (last >= first && line[last].u == ' ') last--;
		for (x = first; x <= last; x++)
			if (!(line[x].mode & ATTR_WDUMMY))
				p += utf8encode(line[x].u, p);
		if ((y < end / br.cols || br.visual == 2) &&
		    !(line[linelast].mode & ATTR_WRAP))
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
	return ISDELIM(u) ? 1 : 2;
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

void
browseinput(unsigned long key, unsigned int state, const char *buf, int len)
{
	int n, p, total = br.rows * br.cols, kind;
	Rune rune;
	size_t used;
	if (!br.active) return;
	if (br.searching) {
		if (key == XK_Escape) br.searching = 0;
		else if (key == XK_Return || key == XK_KP_Enter) {
			br.searching = 0;
			browsefind(br.direction);
		} else if (key == XK_BackSpace) {
			if (br.querylen) br.querylen--;
		} else if (!(state & (ControlMask | Mod1Mask))) {
			while (len > 0 && br.querylen < (int)LEN(br.query)) {
				used = utf8decode(buf, &rune, len);
				if (!used) break;
				if (rune >= ' ') br.query[br.querylen++] = rune;
				buf += used;
				len -= used;
			}
		}
		tfulldirt();
		return;
	}
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
		return;
	} else {
		if (key != XK_g) br.g = 0;
		switch (key) {
		case XK_Escape:
			if (br.visual) br.visual = 0;
			else browseclose();
			break;
		case XK_q: case XK_i: browseclose(); break;
		case XK_h: case XK_Left: br.x -= n; break;
		case XK_l: case XK_Right: br.x += n; break;
		case XK_k: case XK_Up: br.y -= n; break;
		case XK_j: case XK_Down: br.y += n; break;
		case XK_0: case XK_Home: br.x = 0; break;
		case XK_dollar: case XK_End:
			br.x = br.cols - 1;
			while (br.x > 0 && br.cells[(size_t)br.y * br.cols + br.x].u == ' ') br.x--;
			break;
		case XK_g:
			if (br.g) { br.y = 0; br.x = 0; br.g = 0; }
			else br.g = 1;
			break;
		case XK_G: br.y = br.rows - 1; br.x = 0; break;
		case XK_H: br.y = br.top; break;
		case XK_M: br.y = br.top + MAX(0, term.row - 2) / 2; break;
		case XK_L: br.y = br.top + MAX(0, term.row - 2); break;
		case XK_Page_Up: br.y -= n * MAX(1, term.row - 2); break;
		case XK_Page_Down: br.y += n * MAX(1, term.row - 2); break;
		case XK_w: case XK_b: case XK_e:
			p = browsepos();
			while (n--) {
				if (key == XK_b) {
					if (p > 0) p--;
					while (p > 0 && !browseword(p)) p--;
					kind = browseword(p);
					while (p > 0 && browseword(p - 1) == kind) p--;
				} else if (key == XK_w) {
					kind = browseword(p);
					while (p < total - 1 && browseword(p) == kind) p++;
					while (p < total - 1 && !browseword(p)) p++;
				} else {
					if (p < total - 1) p++;
					while (p < total - 1 && !browseword(p)) p++;
					kind = browseword(p);
					while (p < total - 1 && browseword(p + 1) == kind) p++;
				}
			}
			br.x = p % br.cols; br.y = p / br.cols;
			break;
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
		br.count = 0;
	}
	if (br.active) {
		LIMIT(br.x, 0, br.cols - 1);
		LIMIT(br.y, 0, br.rows - 1);
	}
	tfulldirt();
}

static void
browsedraw(void)
{
	int x, y, row, pos, start = -1, end = -1;
	int height = MAX(1, term.row - 1);
	char status[128];
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
		snprintf(status, sizeof(status), " COPY [RO] %s | %d/%d | v/V select, y copy, / search, q exit ",
		         br.visual == 2 ? "VISUAL LINE" : br.visual ? "VISUAL" : "NORMAL", br.y + 1, br.rows);
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

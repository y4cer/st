# st - simple terminal
# See LICENSE file for copyright and license details.
.POSIX:

include config.mk

SRC = st.c x.c utf8.c
OBJ = $(SRC:.c=.o)

all: st

config.h:
	cp config.def.h config.h

.c.o:
	$(CC) $(STCFLAGS) -c $<

st.o: config.h st.h win.h browse.c
x.o: arg.h config.h st.h win.h
utf8.o: st.h

$(OBJ): config.h config.mk

st: $(OBJ)
	$(CC) $(WARNFLAGS) -o $@ $(OBJ) $(STLDFLAGS)

# Test binaries are separate: sanitizers never contaminate the installed st.
TESTFLAGS = $(WARNFLAGS) $(INCS) -std=c99 -D_XOPEN_SOURCE=600 -DVERSION=\"test\" -g -O1 -ffunction-sections -fdata-sections -Wl,--gc-sections
TESTSAN = -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer

test: test-reference-build
	mkdir -p tests/bin
	$(CC) $(TESTFLAGS) tests/test_terminal.c utf8.c -o tests/bin/terminal -lutil
	$(CC) $(TESTFLAGS) tests/test_x11.c utf8.c -o tests/bin/x11 $(LIBS)
	python3 tests/run.py tests/bin/terminal tests/bin/x11
	python3 tests/shitty/check.py

test-sanitize: test-reference-sanitize-build
	mkdir -p tests/bin
	$(CC) $(TESTFLAGS) $(TESTSAN) tests/test_terminal.c utf8.c -o tests/bin/terminal-asan -lutil
	$(CC) $(TESTFLAGS) $(TESTSAN) tests/test_x11.c utf8.c -o tests/bin/x11-asan $(LIBS)
	python3 tests/run.py tests/bin/terminal-asan tests/bin/x11-asan
	ST_TEST_BRIDGE=tests/bin/shitty-bridge-asan ST_TEST_FRONTEND=tests/bin/shitty-frontend-asan python3 tests/shitty/check.py --sanitize

# Reference adapters execute the real core/frontend in isolated subprocesses.
test-reference-build:
	mkdir -p tests/bin
	$(CC) $(TESTFLAGS) tests/shitty/bridge.c utf8.c -o tests/bin/shitty-bridge -lutil
	$(CC) $(TESTFLAGS) tests/shitty/frontend.c utf8.c -o tests/bin/shitty-frontend $(LIBS)

test-reference-sanitize-build:
	mkdir -p tests/bin
	$(CC) $(TESTFLAGS) $(TESTSAN) tests/shitty/bridge.c utf8.c -o tests/bin/shitty-bridge-asan -lutil
	$(CC) $(TESTFLAGS) $(TESTSAN) tests/shitty/frontend.c utf8.c -o tests/bin/shitty-frontend-asan $(LIBS)

clean:
	rm -f st $(OBJ) st-$(VERSION).tar.gz
	rm -rf tests/bin

dist: clean
	mkdir -p st-$(VERSION)
	cp -R FAQ LEGACY TODO LICENSE Makefile README config.mk\
		config.def.h st.info st.1 arg.h st.h win.h browse.c README.personal.md tests $(SRC)\
		st-$(VERSION)
	tar -cf - st-$(VERSION) | gzip > st-$(VERSION).tar.gz
	rm -rf st-$(VERSION)

install: st
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp -f st $(DESTDIR)$(PREFIX)/bin
	chmod 755 $(DESTDIR)$(PREFIX)/bin/st
	mkdir -p $(DESTDIR)$(MANPREFIX)/man1
	sed "s/VERSION/$(VERSION)/g" < st.1 > $(DESTDIR)$(MANPREFIX)/man1/st.1
	chmod 644 $(DESTDIR)$(MANPREFIX)/man1/st.1
	tic -sx st.info
	@echo Please see the README file regarding the terminfo entry of st.

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/st
	rm -f $(DESTDIR)$(MANPREFIX)/man1/st.1

.PHONY: all clean dist install uninstall test test-sanitize test-reference-build test-reference-sanitize-build

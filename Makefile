#
# Copyright (c) 2008-2009 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any waranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#

SUBDIRS = as3


build: default-build

install: default-install

clean: default-clean

test: default-test

forcetag:
	hg tag -f smartform-$(VERSION)

tag:
	hg tag smartform-$(VERSION)



dist: archive

archive-snapshot:
	hg archive --exclude .hgignore -t tbz2 smartform-$$(hg id -i).tar.bz2

archive:
	hg archive --exclude .hgignore -t tbz2 smartform-$(VERSION).tar.bz2


export TOPDIR=$(shell pwd)
include $(TOPDIR)/Make.rules
include $(TOPDIR)/Make.defs

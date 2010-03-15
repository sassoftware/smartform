#
# Copyright (c) 2010 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any waranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#
SUBDIRS = smartform test xsd

build: default-build

install: default-install

clean: default-clean

test: subdirs-test

export TOPDIR=$(shell pwd)/..
include $(TOPDIR)/Make.rules
include $(TOPDIR)/Make.defs

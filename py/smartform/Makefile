#
# Copyright (c) 2009 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

export TOPDIR=$(shell pwd)/../..
python_files =	$(wildcard *.py)

SUBDIRS = xml_1_0

dist_files = Makefile constants.py.in $(python_files)

build: constants.py default-build python-build

clean: python-clean python-clean

test: default-test python-test

constants.py: constants.py.in $(TOPDIR)/Make.defs Makefile
	sed -e s,@version@,$(VERSION),g \
	$< > $@

install: constants.py default-install python-install

dist: default-dist

clean: default-clean
	rm -f proddef_constants.py

GENERATE_DS=~/hg/generateDS/generateDS.py
xmlDir = $(subst .,_,$(patsubst rule-%,xml_%,$(1)))
xmlVer = $(patsubst rule-%,%,$(1))

generate: $(patsubst ../xsd/descriptor-%.xsd,rule-%,$(wildcard ../xsd/descriptor-*.xsd))

rule-%:
	mkdir -p $(call xmlDir,$@)
	touch $(call xmlDir,$@)/__init__.py
	$(GENERATE_DS) -f --silence \
                --no-dates \
                --no-versions \
                --member-specs=list \
                --super=supers_descriptor \
                --external-encoding=utf-8 \
                -o $(call xmlDir,$@)/supers_descriptor.py \
                -s $(call xmlDir,$@)/subs_descriptor.py \
                --user-methods=gends_user_methods \
                ../xsd/descriptor-$(call xmlVer,$@).xsd
	$(GENERATE_DS) -f --silence \
                --no-dates \
                --no-versions \
                --member-specs=list \
                --super=supers_descriptordata \
                --external-encoding=utf-8 \
                -o $(call xmlDir,$@)/supers_descriptordata.py \
                -s $(call xmlDir,$@)/subs_descriptordata.py \
                --user-methods=gends_user_methods \
                ../xsd/descriptordata-$(call xmlVer,$@).xsd

include $(TOPDIR)/Make.rules
include $(TOPDIR)/Make.defs

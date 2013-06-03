#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


export TOPDIR=$(shell pwd)/../..
python_files =	$(wildcard *.py)
override DIR=/smartform

SUBDIRS = xml_1_0 xml_1_1

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
	for x in {subs,supers}_descriptor{,data}.py; do \
		echo "# pyflakes=ignore-file" >> $(call xmlDir,$@)/$$x; \
	done

include $(TOPDIR)/Make.rules
include $(TOPDIR)/Make.defs

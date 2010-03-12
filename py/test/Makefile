#
# Copyright (c) 2010 rPath, Inc.
# 

TESTS = testsuite.py

test:
	install -d $(TESTOUTPUTDIR) $(TESTCOVERAGEDIR)
	python $(TESTS) --xml-dir=$(TESTOUTPUTDIR) --always-succeed --coverage
	$(COVERAGEDUMP) -o $(TESTCOVERAGEDIR)/coverage.dat -t testsuite.py .  ../smartform

build install:

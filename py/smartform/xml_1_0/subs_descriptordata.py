#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import supers_descriptordata as supermod

#
# Globals
#

ExternalEncoding = 'utf-8'

#
# Data representation classes
#

class descriptorDataTypeSub(supermod.descriptorDataType):
    def __init__(self, valueOf_=''):
        supermod.descriptorDataType.__init__(self, valueOf_)
supermod.descriptorDataType.subclass = descriptorDataTypeSub
# end class descriptorDataTypeSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorDataType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="descriptorData",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorDataType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="descriptorData",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorDataType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from supers_descriptordata import *\n\n')
##     sys.stdout.write('import supers_descriptordata as model_\n\n')
##     sys.stdout.write('rootObj = model_.descriptorData(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="descriptorData")
##     sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


# pyflakes=ignore-file

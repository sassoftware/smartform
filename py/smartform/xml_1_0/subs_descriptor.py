#!/usr/bin/env python

#
# Generated  by generateDS.py.
#

import sys
from string import lower as str_lower
from xml.dom import minidom

import supers_descriptor as supermod

#
# Globals
#

ExternalEncoding = 'utf-8'

#
# Data representation classes
#

class descriptorTypeSub(supermod.descriptorType):
    def __init__(self, version=None, id=None, metadata=None, dataFields=None):
        supermod.descriptorType.__init__(self, version, id, metadata, dataFields)
supermod.descriptorType.subclass = descriptorTypeSub
# end class descriptorTypeSub


class metadataTypeSub(supermod.metadataType):
    def __init__(self, displayName=None, rootElement=None, descriptions=None, supportedFiles=None):
        supermod.metadataType.__init__(self, displayName, rootElement, descriptions, supportedFiles)
supermod.metadataType.subclass = metadataTypeSub
# end class metadataTypeSub


class descriptionsTypeSub(supermod.descriptionsType):
    def __init__(self, desc=None):
        supermod.descriptionsType.__init__(self, desc)
supermod.descriptionsType.subclass = descriptionsTypeSub
# end class descriptionsTypeSub


class supportedFilesTypeSub(supermod.supportedFilesType):
    def __init__(self, file=None):
        supermod.supportedFilesType.__init__(self, file)
supermod.supportedFilesType.subclass = supportedFilesTypeSub
# end class supportedFilesTypeSub


class descTypeSub(supermod.descType):
    def __init__(self, lang=None, valueOf_=''):
        supermod.descType.__init__(self, lang, valueOf_)
supermod.descType.subclass = descTypeSub
# end class descTypeSub


class dataFieldsTypeSub(supermod.dataFieldsType):
    def __init__(self, field=None):
        supermod.dataFieldsType.__init__(self, field)
supermod.dataFieldsType.subclass = dataFieldsTypeSub
# end class dataFieldsTypeSub


class helpTypeSub(supermod.helpType):
    def __init__(self, lang=None, href=None, valueOf_=''):
        supermod.helpType.__init__(self, lang, href, valueOf_)
supermod.helpType.subclass = helpTypeSub
# end class helpTypeSub


class dataFieldTypeSub(supermod.dataFieldType):
    def __init__(self, name=None, descriptions=None, help=None, type_=None, enumeratedType=None, multiple=None, default=None, constraints=None, required=None, allowFileContent=None, hidden=None, password=None, readonly=None, conditional=None):
        supermod.dataFieldType.__init__(self, name, descriptions, help, type_, enumeratedType, multiple, default, constraints, required, allowFileContent, hidden, password, readonly, conditional)
supermod.dataFieldType.subclass = dataFieldTypeSub
# end class dataFieldTypeSub


class enumeratedTypeTypeSub(supermod.enumeratedTypeType):
    def __init__(self, describedValue=None):
        supermod.enumeratedTypeType.__init__(self, describedValue)
supermod.enumeratedTypeType.subclass = enumeratedTypeTypeSub
# end class enumeratedTypeTypeSub


class describedValueTypeSub(supermod.describedValueType):
    def __init__(self, descriptions=None, key=None):
        supermod.describedValueType.__init__(self, descriptions, key)
supermod.describedValueType.subclass = describedValueTypeSub
# end class describedValueTypeSub


class constraintsTypeSub(supermod.constraintsType):
    def __init__(self, descriptions=None, range=None, legalValues=None, regexp=None, length=None):
        supermod.constraintsType.__init__(self, descriptions, range, legalValues, regexp, length)
supermod.constraintsType.subclass = constraintsTypeSub
# end class constraintsTypeSub


class rangeTypeSub(supermod.rangeType):
    def __init__(self, min=None, max=None):
        supermod.rangeType.__init__(self, min, max)
supermod.rangeType.subclass = rangeTypeSub
# end class rangeTypeSub


class legalValuesTypeSub(supermod.legalValuesType):
    def __init__(self, item=None):
        supermod.legalValuesType.__init__(self, item)
supermod.legalValuesType.subclass = legalValuesTypeSub
# end class legalValuesTypeSub


class regexpTypeSub(supermod.regexpType):
    def __init__(self, valueOf_=''):
        supermod.regexpType.__init__(self, valueOf_)
supermod.regexpType.subclass = regexpTypeSub
# end class regexpTypeSub


class lengthTypeSub(supermod.lengthType):
    def __init__(self, valueOf_=''):
        supermod.lengthType.__init__(self, valueOf_)
supermod.lengthType.subclass = lengthTypeSub
# end class lengthTypeSub


class conditionalTypeSub(supermod.conditionalType):
    def __init__(self, fieldName=None, operator=None, value=None):
        supermod.conditionalType.__init__(self, fieldName, operator, value)
supermod.conditionalType.subclass = conditionalTypeSub
# end class conditionalTypeSub



def parse(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="descriptor",
##         namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('<?xml version="1.0" ?>\n')
##     rootObj.export(sys.stdout, 0, name_="descriptor",
##         namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = minidom.parse(inFilename)
    rootNode = doc.documentElement
    rootObj = supermod.descriptorType.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
##     sys.stdout.write('#from supers_descriptor import *\n\n')
##     sys.stdout.write('import supers_descriptor as model_\n\n')
##     sys.stdout.write('rootObj = model_.descriptor(\n')
##     rootObj.exportLiteral(sys.stdout, 0, name_="descriptor")
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



#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

class Error(Exception):
    "Base error class"

class InvalidXML(Error):
    pass

class InvalidSchemaVersionError(Error):
    ""

class SchemaValidationError(Error):
    ""

class UnknownSchema(Error):
    ""

class DataValidationError(Error):
    ""

class ConstraintsValidationError(Error):
    ""

class InvalidDefaultValue(Error):
    ""

class MissingDefaultValue(Error):
    ""

class ReadOnlyFieldChanged(Error):
    ""

class UndefinedFactoryDataField(Error):
    ""

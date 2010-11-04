#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

import re

import descriptor_errors as errors

class _DescriptorDataField(object):
    __slots__ = [ '_node', '_nodeDescriptor' ]
    def __init__(self, node, nodeDescriptor, checkConstraints = True):
        self._node = node
        self._nodeDescriptor = nodeDescriptor
        if checkConstraints:
            self.checkConstraints()

    def checkConstraints(self):
        errorList = []
        descriptions = self._nodeDescriptor.get_descriptions()
        if self._nodeDescriptor.multiple:
            # Get the node's children as values
            values = [ x.text for x in self._node
                if hasattr(x, 'tag') and x.tag == 'item' ]
            if self._nodeDescriptor.required and not values:
                errorList.append("Missing field: '%s'" %
                    self._nodeDescriptor.name)
            elif isinstance(self._nodeDescriptor.type, list):
                errorList.extend(_validateEnumeratedValue(values,
                                 self._nodeDescriptor.type,
                                 descriptions.asDict()[None]))
            else:
                # It is conceivable that one has a multi-valued field with a
                # simple type
                errorList.extend(_validateMultiValue(values,
                                 self._nodeDescriptor.type,
                                 descriptions.asDict().get(None),
                                 self._nodeDescriptor.constraints))
        else:
            value = self._node.text
            constraints = (self._nodeDescriptor.constraints and
                self._nodeDescriptor.constraints.presentation() or [])
            errorList.extend(_validateSingleValue(value,
                             self._nodeDescriptor.type,
                             descriptions.asDict().get(None),
                             constraints,
                             required = self._nodeDescriptor.required))
        if errorList:
            raise errors.ConstraintsValidationError(errorList)

    def getName(self):
        return self._node.tag

    def getValue(self):
        vtype = self._nodeDescriptor.type
        if self._nodeDescriptor.multiple:
            return [ _cast(x.text, vtype)
                for x in self._node
                if x.tag == 'item' ]
        return _cast(self._node.text, vtype)

def _toStr(val):
    if isinstance(val, (str, unicode)):
        return val
    return str(val)

def _cast(val, typeStr):
    if typeStr == 'int':
        try:
            return int(val)
        except ValueError:
            raise errors.DataValidationError(val)
    elif typeStr == 'bool':
        val = _toStr(val)
        if val.upper() not in ('TRUE', '1', 'FALSE', '0'):
            raise errors.DataValidationError(val)
        return val.upper() in ('TRUE', '1')
    elif typeStr == 'str':
        if isinstance(val, unicode):
            return val

        try:
            return str(val).decode('utf-8')
        except UnicodeDecodeError, e_value:
            raise errors.DataValidationError('UnicodeDecodeError: %s'
                % str(e_value))
    return val

def _validateEnumeratedValue(values, valueType, description):
    assert(isinstance(valueType, list))
    valuesHash = dict((x.key, None) for x in valueType)
    errorList = []
    for value in values:
        if value in valuesHash:
            continue
        errorList.append("'%s': invalid value '%s'" % (
            description, value))
    return errorList

def _validateMultiValue(values, valueType, description, constraints):
    errorList = []
    constraints = (constraints and constraints.presentation() or [])
    for value in values:
        errorList.extend(_validateSingleValue(value, valueType, description,
                         constraints))
    return errorList

def _validateSingleValue(value, valueType, description, constraints,
        required=False):
    if value is None and required:
        return [ "'%s': a value is required" % description ]
    if isinstance(valueType, list):
        if value is None:
            value = []
        else:
            value = [ value ]
        return _validateEnumeratedValue(value, valueType, description)

    errorList = []
    try:
        cvalue = _cast(value, valueType)
    except errors.DataValidationError, e:
        errorList.append("'%s': invalid value '%s' for type '%s'" % (
            description, value, valueType))
        return errorList

    for constraint in constraints:
        if constraint['constraintName'] == 'legalValues':
            legalValues = [ _cast(v, valueType) for v in constraint['values'] ]
            if cvalue not in legalValues:
                errorList.append("'%s': '%s' is not a legal value" %
                                 (description, value))
            continue
        if constraint['constraintName'] == 'range':
            # Only applies to int
            if valueType != 'int':
                continue
            if 'min' in constraint:
                minVal = _cast(constraint['min'], valueType)
                if cvalue < minVal:
                    errorList.append(
                        "'%s': '%s' fails minimum range check '%s'" %
                            (description, value, minVal))
            if 'max' in constraint:
                maxVal = _cast(constraint['max'], valueType)
                if cvalue > maxVal:
                    errorList.append(
                        "'%s': '%s' fails maximum range check '%s'" %
                            (description, value, maxVal))
            continue
        if constraint['constraintName'] == 'length':
            # Only applies to str
            if valueType != 'str':
                continue
            if len(cvalue) > int(constraint['value']):
                errorList.append(
                    "'%s': '%s' fails length check '%s'" %
                            (description, value, constraint['value']))
            continue
        if constraint['constraintName'] == 'regexp':
            # Only applies to str
            if valueType != 'str':
                continue
            if not re.compile(constraint['value'], re.S).match(cvalue):
                errorList.append(
                    "'%s': '%s' fails regexp check '%s'" %
                            (description, value, constraint['value']))
            continue

    return errorList

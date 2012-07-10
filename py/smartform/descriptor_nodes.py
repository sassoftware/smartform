#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

import re

import descriptor_errors as errors

class ProtectedUnicode(unicode):
    """A string that is not printed in tracebacks"""
    __slots__ = []
    def __safe_str__(self):
        return "<Protected Value>"

    __repr__ = __safe_str__

class ListField(list):
    __slots__ = []
    def checkConstraints(self, raiseException=True):
        ret = []
        for x in self:
            ret.extend(x.checkConstraints(raiseException=False))
        if ret and raiseException:
            raise errors.ConstraintsValidationError(ret)
        return ret

class _DescriptorDataField(object):
    __slots__ = [ '_node', '_nodeDescriptor' ]
    def __init__(self, node, nodeDescriptor, checkConstraints = True):
        self._node = node
        self._nodeDescriptor = nodeDescriptor
        if checkConstraints:
            self.checkConstraints()

    def checkConstraints(self, raiseException=True):
        errorList = []
        errorList.extend(self._checkConstraints(self._nodeDescriptor,
            self._node))
        if errorList and raiseException:
            raise errors.ConstraintsValidationError(errorList)
        return errorList

    def _checkConstraints(self, nodeDescriptor, node):
        errorList = []
        descriptions = nodeDescriptor.get_descriptions()
        defaultLangDesc = descriptions.asDict().get(None)
        if nodeDescriptor.descriptor:
            errorList.extend(self._checkConstraintsCompoundType(
                nodeDescriptor.descriptor, node))
        elif nodeDescriptor.listType:
            subdesc = nodeDescriptor.descriptor
            childName = subdesc.getRootElement()
            for childNode in node.iterchildren(childName):
                errorList.extend(self._checkConstraintsCompoundType(
                    subdesc, childNode))
        elif nodeDescriptor.multiple:
            # Get the node's children as values
            values = [ x.text for x in node
                if hasattr(x, 'tag') and x.tag == 'item' ]
            if nodeDescriptor.required and not values:
                errorList.append("Missing field: '%s'" %
                    nodeDescriptor.name)
            elif isinstance(nodeDescriptor.type, list):
                errorList.extend(_validateEnumeratedValue(values,
                                 nodeDescriptor.type,
                                 defaultLangDesc))
            else:
                # It is conceivable that one has a multi-valued field with a
                # simple type
                errorList.extend(_validateMultiValue(values,
                                 nodeDescriptor.type,
                                 defaultLangDesc,
                                 nodeDescriptor.constraints))
        else:
            value = node.text
            constraints = (nodeDescriptor.constraints and
                nodeDescriptor.constraints.presentation() or [])
            errorList.extend(_validateSingleValue(value,
                             nodeDescriptor.type,
                             defaultLangDesc,
                             constraints,
                             required = nodeDescriptor.required))
            if nodeDescriptor.readonly:
                defaultVal = nodeDescriptor.getDefault()
                if defaultVal is None or (
                        nodeDescriptor.type == 'str' and not defaultVal):
                    """ Commented out until the image import metadata
                    descriptor becomes smarter
                    errorList.append("'%s': descriptor error: no defaults supplied for read-only field" % (
                        defaultLangDesc, ))
                    """
                elif value is not None and value != defaultVal:
                    errorList.append(
                        "'%s': invalid value '%s' for read-only field; expected '%s'" % (
                            defaultLangDesc, value, defaultVal))
        return errorList

    def _checkConstraintsCompoundType(self, descriptor, node):
        errorList = []
        fieldsMap = []
        for f in descriptor.getDataFields():
            subnode = list(node.iterchildren(f.name))
            if not subnode:
                continue
            subnode = subnode[0]
            errorList.extend(self._checkConstraints(f, subnode))
        # XXX check for required fields
        return errorList

    def getName(self):
        return self._node.tag

    def getValue(self):
        vtype = self._nodeDescriptor.type
        isPasswd = bool(self._nodeDescriptor.password)
        if self._nodeDescriptor.multiple:
            return [ _cast(x.text, vtype, isPassword=isPasswd)
                for x in self._node
                if x.tag == 'item' ]
        return _cast(self._node.text, vtype, isPassword=isPasswd)

def _toStr(val):
    if isinstance(val, (str, unicode)):
        return val
    return str(val)

def _cast(val, typeStr, isPassword=False):
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
        if val is None:
            return None
        if isinstance(val, unicode):
            if isPassword:
                return ProtectedUnicode(val)
            return val

        try:
            if isPassword:
                return ProtectedUnicode(str(val).decode('utf-8'))
            else:
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
            if valueType != 'str' or cvalue is None:
                continue
            if len(cvalue) > int(constraint['value']):
                errorList.append(
                    "'%s': '%s' fails length check '%s'" %
                            (description, value, constraint['value']))
            continue
        if constraint['constraintName'] == 'regexp':
            # Only applies to str
            if valueType != 'str' or cvalue is None:
                continue
            if not re.compile(constraint['value'], re.S).match(cvalue):
                errorList.append(
                    "'%s': '%s' fails regexp check '%s'" %
                            (description, value, constraint['value']))
            continue

    return errorList

#!/usr/bin/env python
# -*- mode: pymode; coding: latin1; -*-

import sys
import re

#
# You must include the following class definition at the top of
#   your method specification file.
#
class MethodSpec(object):
    def __init__(self, name='', source='', class_names='',
            class_names_compiled=None):
        """MethodSpec -- A specification of a method.
        Member variables:
            name -- The method name
            source -- The source code for the method.  Must be
                indented to fit in a class definition.
            class_names -- A regular expression that must match the
                class names in which the method is to be inserted.
            class_names_compiled -- The compiled class names.
                generateDS.py will do this compile for you.
        """
        self.name = name
        self.source = source
        if class_names is None:
            self.class_names = ('.*', )
        else:
            self.class_names = class_names
        if class_names_compiled is None:
            self.class_names_compiled = re.compile(self.class_names)
        else:
            self.class_names_compiled = class_names_compiled
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_source(self):
        return self.source
    def set_source(self, source):
        self.source = source
    def get_class_names(self):
        return self.class_names
    def set_class_names(self, class_names):
        self.class_names = class_names
        self.class_names_compiled = re.compile(class_names)
    def get_class_names_compiled(self):
        return self.class_names_compiled
    def set_class_names_compiled(self, class_names_compiled):
        self.class_names_compiled = class_names_compiled
    def match_name(self, class_name):
        """Match against the name of the class currently being generated.
        If this method returns True, the method will be inserted in
          the generated class.
        """
        if self.class_names_compiled.search(class_name):
            return True
        else:
            return False
    def get_interpolated_source(self, values_dict):
        """Get the method source code, interpolating values from values_dict
        into it.  The source returned by this method is inserted into
        the generated class.
        """
        source = self.source % values_dict
        return source
    def show(self):
        print 'specification:'
        print '    name: %s' % (self.name, )
        print self.source
        print '    class_names: %s' % (self.class_names, )
        print '    names pat  : %s' % (self.class_names_compiled.pattern, )

getId = MethodSpec(name = 'getId',
    source = '''
''',
    class_names = r'^descriptor$',)

descriptionsTypeMethods = MethodSpec(name = 'descriptionsTypeMethods',
    source = '''
    def asDict(self):
        return dict((x.get_lang(), x.getValueOf_()) for x in self.get_desc())
''',
    class_names = r'^descriptionsType$',)

fieldsAsDict = MethodSpec(name = 'fieldsAsDict',
    source = '''
''',
    class_names = r'^dataFieldsType$',)

dataFieldMethods = MethodSpec(name = 'dataFieldMethods',
    source = '''
    def _getType(self):
        if not self.enumeratedType:
            return self.type_
        return [ x for x in self.enumeratedType.describedValue ]
    type = property(_getType)

    def presentation(self):
        if self.constraints is None:
            return []
        return self.constraints.presentation()

    def getDefault(self):
        if not self.default:
            if self.multiple:
                return []
            return None
        from smartform.descriptor_nodes import _cast
        typ = self.type_
        if self.multiple:
            return [ _cast(x, typ) for x in self.default ]
        return _cast(self.default[0], typ)
    ''',
    class_names = r'^dataFieldType$',)


constraintsTypeMethods = MethodSpec(name = 'constraintsTypeMethods',
    source = '''
    def presentation(self):
        ret = []
        ret.extend(x.presentation() for x in self.range)
        ret.extend(x.presentation() for x in self.legalValues)
        ret.extend(x.presentation() for x in self.regexp)
        ret.extend(x.presentation() for x in self.length)
        return ret

    def fromData(self, dataList):
        for dataDict in dataList:
            self._fromData(dataDict)

    def _fromData(self, data):
        constraintName = data.get('constraintName')
        if constraintName is None:
            return
        potential = [ x for x in self.member_data_items_
            if x.name == constraintName ]
        if not potential:
            return
        dataType = potential[0].get_data_type()
        cls = globals().get(dataType)
        if not cls:
            return
        v = cls()
        v.fromData(data)
        method = getattr(self, 'add_' + potential[0].name)
        method(v)
    ''',
    class_names = r'^constraintsType$',)

rangeTypeMethods = MethodSpec(name = 'rangeTypeMethods',
    source = '''
    def presentation(self):
        ret = dict(constraintName = 'range')
        if self.min is not None:
            ret['min'] = self.min
        if self.max is not None:
            ret['max'] = self.max
        return ret

    def fromData(self, data):
        self.min = data.get('min')
        self.max = data.get('max')
    ''',
    class_names = r'^rangeType$')

legalValuesTypeMethods = MethodSpec(name = 'legalValuesTypeMethods',
    source = '''
    def presentation(self):
        return dict(constraintName = 'legalValues', values = (self.item or []))

    def fromData(self, data):
        for value in data.get('values', []):
            self.add_item(value)
    ''',
    class_names = r'^legalValuesType$')

regexpTypeMethods = MethodSpec(name = 'regexpTypeMethods',
    source = '''
    def presentation(self):
        return dict(constraintName = 'regexp', value = self.valueOf_)

    def fromData(self, data):
        self.setValueOf_(data.get('value'))
    ''',
    class_names = r'^regexpType$')

lengthTypeMethods = MethodSpec(name = 'lengthTypeMethods',
    source = '''
    def presentation(self):
        return dict(constraintName = 'length', value = int(self.valueOf_))

    def fromData(self, data):
        self.setValueOf_(str(data.get('value')))
    ''',
    class_names = r'^lengthType$')


METHOD_SPECS = (
    getId,
    descriptionsTypeMethods,
    fieldsAsDict,
    dataFieldMethods,
    constraintsTypeMethods,
    rangeTypeMethods,
    legalValuesTypeMethods,
    regexpTypeMethods,
    lengthTypeMethods,
)

def test():
    for spec in METHOD_SPECS:
        spec.show()

def main():
    test()


if __name__ == '__main__':
    main()

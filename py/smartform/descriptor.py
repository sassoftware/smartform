#!/usr/bin/python
#
# Copyright (c) 2008 rPath, Inc.
#

import os
import sys
import StringIO
from lxml import etree

import descriptor_errors as errors
import descriptor_nodes as dnodes
import constants

ProtectedUnicode = dnodes.ProtectedUnicode

class _BaseClass(object):
    version = constants.version
    defaultNamespace = constants.defaultNamespaceList[0]
    xmlSchemaNamespace = constants.xmlSchemaNamespace
    xmlSchemaLocation = constants.xmlSchemaLocation

    schemaDir = "/usr/share/smartform"

    _SchemaName = 'descriptor'

    def __init__(self, fromStream = None, validate = False, schemaDir = None):
        self._initFields()
        self._validate = validate
        if schemaDir:
            self.schemaDir = schemaDir

        if fromStream:
            self.parseStream(fromStream, validate = validate,
                schemaDir = self.schemaDir)

    def parseStream(self, fromStream, validate = False, schemaDir = None):
        """
        Initialize the current object from an XML stream.
        @param stream: An XML stream
        @type stream: C{file}
        @param validate: Validate before parsing (off by default)
        @type validate: C{bool}
        @param schemaDir: A directory where schema files are stored
        @type schemaDir: C{str}
        """
        self._initFields()

        from xml.dom import minidom
        if isinstance(fromStream, (str, unicode)):
            func = minidom.parseString
        else:
            func = minidom.parse
        try:
            doc = func(fromStream)
        except Exception, e:
            raise errors.InvalidXML(e), None, sys.exc_info()[2]
        rootNode = doc.documentElement
        if rootNode.attributes.has_key('version'):
            version = rootNode.attributes['version'].value.encode('ascii')
        else:
            # XXX default to the current version, hope for the best
            version = self.version
        xmlns = rootNode.attributes.get('xmlns')

        module = self.loadModule(version)

        rootObj = getattr(module, self.ClassFactoryName).factory()
        rootObj.build(rootNode)
        doc.unlink()
        if version != self.version:
            # Handle migrations here
            raise errors.InvalidSchemaVersionError(version)
        self._rootObj = rootObj
        self._postinit()
        self._postprocess()

    def getId(self):
        return self._rootObj.get_id()

    def setId(self, id):
        self._rootObj.set_id(id)

    @classmethod
    def loadModule(cls, version):
        moduleName = "xml_%s.subs_%s" % (version.replace('.', '_'),
            cls._SchemaName)
        try:
            module = __import__(moduleName, globals(), None, [moduleName])
        except ImportError, e:
            raise errors.InvalidSchemaVersionError(version)
        return module

    @classmethod
    def getSchemaFile(cls, schemaDir, version):
        schemaFile = os.path.join(schemaDir, "%s-%s.xsd" % (cls._SchemaName,
            version))
        try:
            file(schemaFile)
        except OSError:
            raise errors.SchemaValidationError("Unable to load schema file %s" % schemaFile)
        return schemaFile

    @classmethod
    def validate(cls, stream, schemaDir, version):
        schemaFile = cls.getSchemaFile(schemaDir, version)
        schema = etree.XMLSchema(file = schemaFile)
        tree = etree.parse(stream)
        if not schema.validate(tree):
            raise errors.SchemaValidationError(str(schema.error_log))
        return tree

    def serialize(self, stream, validate = True):
        """
        Serialize the current object as an XML stream.
        @param stream: stream to write the serialized object
        @type stream: C{file}
        """
        tree = self.getElementTree(validate=validate)
        tree.write(stream, encoding = 'UTF-8', pretty_print = True,
            xml_declaration = True)

    def getElementTree(self, validate=True):

        attrs = [
            ('xmlns:xsi', self.xmlSchemaNamespace),
            ("xsi:schemaLocation", self.xmlSchemaLocation),
        ]
        # Allow for no default namespace
        if self.defaultNamespace is not None:
            attrs.append(('xmlns', self.defaultNamespace))
        sio = self._writeToStream(attrs)
        if validate and os.path.exists(self.schemaDir):
            tree = self.validate(sio, self.schemaDir,
                self._getSchemaVersion())
        elif validate:
            import sys
            sys.stderr.write("Warning: unable to validate schema: directory %s missing"
                % self.schemaDir)
            tree = etree.parse(sio)
        else:
            tree = etree.parse(sio)
        return tree

    def xmlFactory(self):
        return self.loadModule(self.version)

    def _getSchemaVersion(self):
        return self._rootObj.get_version() or '1.0'

    def _initFields(self):
        xmlsubs = self.xmlFactory()
        self._rootObj = getattr(xmlsubs, self.ClassFactoryName)()
        self._postinit()

    def _postinit(self):
        xmlsubs = self.xmlFactory()
        if self._rootObj.get_metadata() is None:
            self._rootObj.set_metadata(xmlsubs.metadataTypeSub.factory())
        if self._rootObj.get_dataFields() is None:
            self._rootObj.set_dataFields(xmlsubs.dataFieldsTypeSub.factory())

    def _postprocess(self):
        pass

    def _writeToStream(self, attrs):
        namespacedef = ' '.join('%s="%s"' % a for a in attrs)

        # Write to a temporary file. We are paranoid and want to verify that
        # the output we produce doesn't break lxml
        bsio = StringIO.StringIO()
        self._rootObj.export(bsio, 0, namespace_ = '', name_ = self.RootNode,
            namespacedef_ = namespacedef)
        bsio.seek(0)
        return bsio

class BaseDescriptor(_BaseClass):
    ClassFactoryName = 'descriptorTypeSub'
    RootNode = 'descriptor'

    def getDisplayName(self):
        metadata = self._rootObj.get_metadata()
        return metadata.get_displayName()

    def setDisplayName(self, displayName):
        metadata = self._rootObj.get_metadata()
        metadata.set_displayName(displayName)

    def getRootElement(self):
        metadata = self._rootObj.get_metadata()
        return metadata.get_rootElement()

    def setRootElement(self, rootElement):
        metadata = self._rootObj.get_metadata()
        metadata.set_rootElement(rootElement)

    def getSupportedFiles(self):
        metadata = self._rootObj.get_metadata()
        return metadata.get_supportedFiles().get_file()

    def setSupportedFiles(self, supportedFiles):
        metadata = self._rootObj.get_metadata()
        metadata.get_supportedFiles().set_file(supportedFiles)

    def getDataFields(self):
        """
        @return: the data fields associated with this object
        @rtype: C{list} of C{descriptor_nodes.DataFieldNode}
        """
        return self._rootObj.get_dataFields().get_field()

    def addDataFieldRaw(self, dataField, index=None):
        xmlsubs = self.xmlFactory()
        name = dataField.get_name()

        # Delete the old field if it exists
        self.deleteDataField(name)
        if self._rootObj.dataFields is None:
            self._rootObj.dataFields = xmlsubs.dataFieldsTypeSub.factory()
        if index is None:
            self._rootObj.dataFields.add_field(dataField)
        else:
            self._rootObj.dataFields.field.insert(index, dataField)

    def addDataField(self, name, **kwargs):
        xmlsubs = self.xmlFactory()
        if isinstance(name, xmlsubs.dataFieldTypeSub):
            return self.addDataFieldRaw(name)
        nodeType = kwargs.get('type')
        constraints = kwargs.get('constraints', [])
        descriptions = kwargs.get('descriptions', [])
        help = kwargs.get('help', [])
        if not isinstance(help, list):
            help = [ help ]
        constraintsDescriptions = kwargs.get('constraintsDescriptions', [])
        default = kwargs.get('default')
        df = xmlsubs.dataFieldTypeSub.factory()
        df.name = name
        df.multiple = kwargs.get('multiple', None)
        df.readonly = kwargs.get('readonly')
        if default is not None:
            if not isinstance(default, list):
                if not isinstance(default, (basestring, int)):
                    # values can only be int or string
                    raise errors.InvalidDefaultValue(default)
                # Silently convert a single value into a list
                default = [ str(default) ]
            if not df.multiple and len(default) > 2:
                raise errors.InvalidDefaultValue(default)
            df.default = default
        elif df.readonly:
            # A read-only field only makes sense if it has a default
            # value
            raise errors.MissingDefaultValue()
        if isinstance(nodeType, list) or hasattr(nodeType, 'describedValue'):
            df.set_type(None)
            df.enumeratedType = self.EnumeratedType(nodeType)
            if default is not None:
                properKeys = set(x.key for x in df.enumeratedType.get_describedValue())
                invalidDefaults = set(default) - properKeys
                if invalidDefaults:
                    raise errors.InvalidDefaultValue(", ".join(sorted(invalidDefaults)))
        else:
            df.set_type(nodeType)
            df.enumeratedType = None
        df.descriptions = self.Descriptions(descriptions)
        for h in help:
            h = self.Help(h)
            df.add_help(h)
        if constraints:
            if not isinstance(constraints, list):
                constraints = [ constraints ]
            df.constraints = xmlsubs.constraintsTypeSub.factory()
            df.constraints.fromData(constraints)
        df.required = kwargs.get('required')
        df.allowFileContent = kwargs.get('allowFileContent')
        df.hidden = kwargs.get('hidden')
        df.password = kwargs.get('password')
        df.conditional = kwargs.get('conditional')
        return self.addDataFieldRaw(df, index=kwargs.get('index'))

    def deleteDataField(self, name):
        if self._rootObj.dataFields is None:
            return None
        origFields = self._rootObj.dataFields.field
        matches = [ x for x in origFields if x.get_name() == name ]
        if not matches:
            return None
        self._rootObj.dataFields.set_field(
            [ x for x in origFields if x.get_name() != name ])
        return matches[0]

    def ValueWithDescription(self, key, descriptions):
        ret = self.xmlFactory().describedValueTypeSub.factory()
        ret.key = key
        ret.descriptions = self.Descriptions(descriptions)
        return ret

    def Description(self, value, lang = None):
        ret = self.xmlFactory().descTypeSub.factory(lang = lang,
            valueOf_ = value)
        return ret

    def Descriptions(self, values):
        if values is None:
            return None
        if not isinstance(values, list):
            values = [ values ]
        # Eliminate duplicates
        langMap = {}
        for val in values:
            if isinstance(val, (str, unicode)):
                val = self.Description(val)
            elif isinstance(val, tuple):
                val = self.Description(val[0], val[1])
            langMap[val.get_lang()] = val
        ret = self.xmlFactory().descriptionsTypeSub.factory()
        ret.set_desc([ x[1] for x in sorted(langMap.items()) ])
        return ret

    def EnumeratedType(self, values):
        if hasattr(values, 'describedValue'):
            values = values.describedValue
        ret = self.xmlFactory().enumeratedTypeTypeSub.factory()
        for val in values:
            ret.add_describedValue(val)
        return ret

    def Help(self, h):
        typeClass = self.xmlFactory().helpTypeSub
        if isinstance(h, typeClass):
            return h
        lang = None
        if isinstance(h, tuple):
            if len(h) < 1:
                raise Exception("XXX FIXME")
            href = h[0]
            if len(h) > 1:
                lang = h[1]
        elif isinstance(h, basestring):
            href = h
        else:
            raise Exception("XXX FIXME")
        hval = typeClass.factory(href = href, lang = lang)
        return hval

    def getDataField(self, name):
        fields = [ x for x in self._rootObj.dataFields.get_field()
            if x.name == name ]
        if not fields:
            return None
        return fields[0]

    def getDescriptions(self):
        """
        @return: the description fields associated with this object
        @rtype: C{list} of C{description_nodes.DescriptionNode}
        """
        return self._rootObj.get_metadata().get_descriptions().asDict()

    def addDescription(self, description, lang=None):
        metadata = self._rootObj.get_metadata()
        descriptions = metadata.get_descriptions()
        if descriptions is None:
            dlist = []
        else:
            dlist = descriptions.get_desc()
        d = self.Description(description, lang = lang)
        dlist.append(d)
        # This also eliminates duplicates
        metadata.set_descriptions(self.Descriptions(dlist))

    def Conditional(self, fieldName, fieldValue, operator = "eq"):
        node = self.xmlFactory().conditionalTypeSub.factory(
            fieldName = fieldName, value = fieldValue, operator = operator)
        return node

class DescriptorData(_BaseClass):
    "Class for representing the descriptor data"

    def __init__(self, fromStream = None, validate = False, descriptor = None):
        if descriptor is None:
            raise errors.FactoryDefinitionMissing()

        self._descriptor = descriptor
        self._rootElement = descriptor.getRootElement()
        if self._rootElement is None:
            # Safe default if no default root element is supplied
            self._rootElement = "descriptorData"
        _BaseClass.__init__(self, fromStream = fromStream)

    def _initFields(self):
        self._rootObj = etree.Element(self._rootElement)
        self._fields = []
        self._fieldsMap = {}
        self._postinit()

    def _getSchemaVersion(self):
        return self._rootObj.attrib.get('version', '1.0')

    def parseStream(self, fromStream, validate = False, schemaDir = None):
        if isinstance(fromStream, (str, unicode)):
            func = etree.fromstring
        else:
            func = etree.parse
        self._rootObj = func(fromStream)
        self._postinit()
        self._postprocess()

    @classmethod
    def validate(cls, stream, schemaDir, version):
        tree = etree.parse(stream)
        return tree

    def setId(self, id):
        self._rootObj.attrib['id'] = id

    def _postinit(self):
        pass

    def _postprocess(self):
        if self._rootObj.tag != self._rootElement:
            raise errors.DataValidationError("Expected node %s, got %s"
                % (self._rootElement, self._rootObj.tag))
        for child in self._rootObj:
            nodeName = child.tag
            # Grab the descriptor for this field
            fieldDesc = self._descriptor.getDataField(nodeName)
            if fieldDesc is None:
                # Unsupported field
                continue
            # Disable constraint checking, we will do it at the end
            field = dnodes._DescriptorDataField(child, fieldDesc,
                checkConstraints = False)
            self._fields.append(field)
            self._fieldsMap[nodeName] = field
        self.checkConstraints()

    def getFields(self):
        return [ x for x in self._fields ]

    def addField(self, name, value = None, checkConstraints=True):
        # Do not add the field if it was not defined
        fdesc = self._descriptor.getDataField(name)
        if fdesc is None:
            raise errors.UndefinedFactoryDataField(name)

        elm = etree.SubElement(self._rootObj, name)
        if fdesc.multiple:
            if not isinstance(value, list):
                raise errors.DataValidationError("Expected multi-value")
            for val in value:
                val = self._cleanseValue(fdesc, val)
                subnode = etree.SubElement(elm, 'item')
                subnode.text = val
        else:
            value = self._cleanseValue(fdesc, value)
            elm.text = value

        field = dnodes._DescriptorDataField(elm, fdesc,
                checkConstraints=checkConstraints)
        self._fields.append(field)
        self._fieldsMap[field.getName()] = field

    def getField(self, name):
        if name not in self._fieldsMap:
            return None
        return self._fieldsMap[name].getValue()

    def checkConstraints(self):
        errorList = []

        for field in self._fields:
            try:
                field.checkConstraints()
            except errors.ConstraintsValidationError, e:
                errorList.extend(e.args[0])

        # next, look for missing fields
        missingRequiredFields = [ x
            for x in self._descriptor.getDataFields()
                if x.name not in self._fieldsMap
                    and x.required ]
        # A required field may be missing if:
        # the conditional is eq and the field is missing or the field value is
        # not what the conditional specified
        # the conditional is noteq and the field is present and its value is
        # what the conditional specified
        missingRequiredFields = [ x
            for x in missingRequiredFields
                if self._filterEqConditionals(x) ]

        for field in missingRequiredFields:
            errorList.append("Missing field: '%s'" % field.name)

        if errorList:
            raise errors.ConstraintsValidationError(errorList)

    def _filterEqConditionals(self, field):
        # Filter eq conditionals that are not satisfied
        if field.conditional is None:
            return True
        condFieldName = field.conditional.fieldName
        if condFieldName not in self._fieldsMap:
            return False
        return (self._fieldsMap[condFieldName].getValue() ==
                field.conditional.value)

    def _cleanseValue(self, fieldDescription, value):
        if not isinstance(value, basestring):
            value = str(value)
        return value

    def _writeToStream(self, attrs):
        # Write to a temporary file. We are paranoid and want to verify that
        # the output we produce doesn't break lxml
        bsio = StringIO.StringIO(etree.tostring(self._rootObj))
        bsio.seek(0)
        return bsio


class ConfigurationDescriptor(BaseDescriptor):
    "Class for representing the configuration descriptor definition"


class SystemConfigurationDescriptor(BaseDescriptor):
    """
    Class for representing configuration descriptors for systems.
    """

    RootNode = 'configuration_descriptor'


class FactoryDescriptor(BaseDescriptor):
    """
    Class for representing factory descriptors.
    """

    RootNode = 'factory'

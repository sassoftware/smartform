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
    __slots__ = ['_validate', 'schemaDir', '_rootObj', ]
    version = constants.version
    defaultNamespace = constants.defaultNamespaceList[0]
    xmlSchemaNamespace = constants.xmlSchemaNamespace
    xmlSchemaLocation = constants.xmlSchemaLocation

    schemaDir = "/usr/share/smartform"

    _SchemaName = 'descriptor'

    def __init__(self, fromStream = None, validate = False, schemaDir = None,
            fromNode=None):
        self._initFields()
        self._validate = validate
        if schemaDir:
            self.schemaDir = schemaDir

        if fromStream is not None:
            self.parseStream(fromStream, validate = validate,
                schemaDir = self.schemaDir)
        elif fromNode is not None:
            self.fromNode(fromNode, validate=validate)

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
        self.fromNode(rootObj)

    def fromNode(self, node, validate=False):
        self._rootObj = node
        self._postinit()
        self._postprocess(validate=validate)

    def getId(self):
        return self._rootObj.get_id()

    def setId(self, id):
        self._rootObj.set_id(id)

    id = property(getId, setId)

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

    def toxml(self, validate=True):
        """
        Serialize the current object as an XML string.
        """

        out = StringIO.StringIO()
        self.serialize(out, validate=validate)
        return out.getvalue()

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
            sys.stderr.write("Warning: unable to validate schema: directory %s missing"
                % self.schemaDir)
            tree = etree.parse(sio)
        else:
            tree = etree.parse(sio)
        return tree

    def xmlFactory(self):
        return self.loadModule(self.version)

    def _getSchemaVersion(self):
        return self._rootObj.get_version() or self.__class__.version

    def _initFields(self):
        xmlsubs = self.xmlFactory()
        self._rootObj = getattr(xmlsubs, self.ClassFactoryName)()
        # Default to the current version
        self._rootObj.set_version(self.__class__.version)
        self._postinit()

    def _postinit(self):
        xmlsubs = self.xmlFactory()
        if self._rootObj.get_metadata() is None:
            self._rootObj.set_metadata(xmlsubs.metadataTypeSub.factory())
        if self._rootObj.get_dataFields() is None:
            self._rootObj.set_dataFields(xmlsubs.dataFieldsTypeSub.factory())

    def _postprocess(self, validate=True):
        for df in self.getDataFields():
            self._postprocessField(df)

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
    __slots__ = []
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
        self._postprocessField(dataField)

    def addDataField(self, name, **kwargs):
        xmlsubs = self.xmlFactory()
        if isinstance(name, xmlsubs.dataFieldTypeSub):
            return self.addDataFieldRaw(name)
        nodeType = kwargs.get('type')
        constraints = kwargs.get('constraints', [])
        if constraints:
            if not isinstance(constraints, list):
                constraints = [ constraints ]
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
        if isinstance(nodeType, self.CompoundType):
            df.set_descriptor(nodeType.getValue())
            # One should acess the data field via the descriptor
            # property, in order to get access to methods like
            # getDataField()
            df._descriptor = nodeType.dsc
            df._descriptor.setRootElement(name)
        elif isinstance(nodeType, self.ListType):
            if not nodeType.dsc.getRootElement():
                raise errors.MissingRootElement()
            df.set_listType(self._ListType(nodeType))
            df._descriptor = nodeType.dsc
        elif isinstance(nodeType, list) or hasattr(nodeType, 'describedValue'):
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
            df.constraints = xmlsubs.constraintsTypeSub.factory()
            df.constraints.fromData(constraints)
        section = kwargs.get('section')
        if section:
            df.section = xmlsubs.sectionTypeSub.factory()
            df.section.set_key(section['key'])
            df.section.set_descriptions(self.Descriptions(
                section.get('descriptions', [])))
        df.required = kwargs.get('required')
        df.allowFileContent = kwargs.get('allowFileContent')
        df.hidden = kwargs.get('hidden')
        df.password = kwargs.get('password')
        df.conditional = kwargs.get('conditional')
        return self.addDataFieldRaw(df, index=kwargs.get('index'))

    def _postprocessField(self, df):
        if df.enumeratedType is not None and df.enumeratedType.describedValue:
            df.set_type('enumeratedType')
            df.listType = df.descriptor = None
        else:
            # Make sure we don't introduce contradictory types: zero out
            df.enumeratedType = None
            if df.listType is not None:
                df.set_type('listType')
                df.descriptor = None
                df._descriptor = self.__class__(fromNode=df.listType.descriptor)
            elif df.descriptor is not None:
                df.set_type('compoundType')
                df._descriptor = self.__class__(fromNode=df.descriptor)
                df.descriptor = df._descriptor._rootObj
        df.sanitizeConstraints()
        df.sanitizeHelp()
        df.sanitizeConditionals()

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
        if isinstance(values, dict):
            values = [ (y, x) for x, y in values.iteritems() ]
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

    def _ListType(self, compoundType):
        ret = self.xmlFactory().listTypeTypeSub.factory()
        ret.set_descriptor(compoundType.getValue())
        return ret

    class ListType(object):
        def __init__(self, dsc):
            self.dsc = dsc
        def getValue(self):
            return self.dsc._rootObj

    class CompoundType(object):
        def __init__(self, dsc):
            self.dsc = dsc
        def getValue(self):
            return self.dsc._rootObj

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

    def createDescriptorData(self, callback, name=None):
        """
        Create a DescriptorData object, with answers supplied by the callback

        The callback should be an object implementing the following interface:

        class Callback(object):
            def start(self, descriptor, name=None):
                pass
            def end(self, descriptor):
                pass
            def getValueForField(self, field):
                # Here some values are produced for that field
                return '1'

        If the callback prefers to process the whole descriptor by itself, it
        can return the whole descriptor data, and fields will no longer be
        individually queried for values.
        """
        data = callback.start(self, name=name)
        if data:
            return data
        # Collect all nodes in a graph, to determine the order of
        # operation
        graph = Graph()
        allFields = {}
        deferredFields = {}
        for field in self.getDataFields():
            predecessors = []
            deferredField = deferredFields.pop(field.name, None)
            if field.conditional:
                if field.conditional.operator != 'eq':
                    continue
                condFieldName = field.conditional.fieldName
                if condFieldName in allFields:
                    allFields[condFieldName][1].setdefault(
                        field.conditional.value, {})[field.name] = field
                else:
                    deferredFields.setdefault(field.name, {}).setdefault(
                        field.conditional.value, {})[field.name] = field
                predecessors.append(condFieldName)
            if deferredField is None:
                depFields = {}
            else:
                depFields = deferredField
            allFields[field.name] = (field, depFields)
            graph.add(field.name, predecessors=predecessors)
        assert deferredFields == {}

        trees = graph.toTrees()
        trees.reverse()

        ddata = DescriptorData(descriptor=self)
        while trees:
            node = trees.pop()
            fieldName = node.id
            field, dependents = allFields[fieldName]
            if field.descriptor:
                # Compound type
                assert not dependents
                value = field._descriptor.createDescriptorData(callback,
                    name=fieldName)
            elif field.listType:
                assert not dependents
                raise NotImplementedError()
            else:
                value = callback.getValueForField(field)

            if dependents:
                validDependents = dependents.get(value, {})

                # Skip over all dependents that we don't care about
                # We reverse the list since trees acts like a stack
                trees.extend(x for x in reversed(node.links)
                        if x.id in validDependents)

            if value is None:
                # Don't bother to check yet, checkConstraints() will
                # explode if a required value is missing
                continue
            ddata.addField(field.name, value)

        data = callback.end(self)
        ddata._addMissingRequiredFieldsWithDefault()
        ddata.checkConstraints()
        return ddata

class Callback(object):
    """
    Prototype callback interface
    """
    __slots__ = ['name']

    def start(self, descriptor, name=None):
        self.name = name

    def end(self, descriptor):
        pass

    def getValueForField(self, field):
        raise NotImplementedError()

class GraphNode(object):
    __slots__ = [ 'id', 'links', ]
    def __init__(self, id):
        self.id = id
        self.links = set()

class Graph(object):
    __slots__ = [ '_natural', '_nodes', '_deferred' ]
    def __init__(self):
        self._natural = dict()
        self._nodes = dict()
        self._deferred = dict()

    def add(self, id, predecessors=[]):
        if id not in self._nodes:
            self._natural[id] = len(self._natural)
        # If the node was already referenced, use it
        node = self._nodes.setdefault(id, self._deferred.get(id, GraphNode(id)))
        for predecessor in predecessors:
            if predecessor not in self._nodes and predecessor not in self._deferred:
                self._deferred[predecessor] = GraphNode(predecessor)
            node.links.add(predecessor)

    def get(self, id):
        return self._nodes[id]

    def toTrees(self):
        trees = dict()
        processed = dict()
        # Add all level0 nodes
        for node in self._nodes.values():
            rnode = processed.setdefault(node.id, GraphNode(node.id))
            if not node.links:
                trees[node.id] = rnode
            else:
                for parentId in node.links:
                    parent = processed.setdefault(parentId, GraphNode(parentId))
                    parent.links.add(node.id)
        toOrder = trees.values()
        while toOrder:
            node = toOrder.pop()
            node.links = [ processed[x]
                    for x in sorted(node.links, key=lambda x: self._natural[x]) ]
            toOrder.extend(node.links)
        # Order top-level trees too
        return sorted(trees.values(), key=lambda x: self._natural[x.id])

class DescriptorData(_BaseClass):
    "Class for representing the descriptor data"
    __slots__ = [ '_descriptor', '_rootElement', '_fields', '_fieldsMap', ]

    def __init__(self, fromStream = None, validate = True, descriptor = None,
            rootElement=None):
        if descriptor is None:
            raise errors.FactoryDefinitionMissing()

        self._descriptor = descriptor
        self._rootElement = descriptor.getRootElement()
        if self._rootElement is None:
            # Safe default if no default root element is supplied
            self._rootElement = rootElement or "descriptorData"
        _BaseClass.__init__(self, fromStream = fromStream, validate=validate)

    def _initFields(self):
        self._rootObj = etree.Element(self._rootElement)
        self._rootObj.attrib['version'] = str(self.__class__.version)
        self._fields = []
        self._fieldsMap = {}
        self._postinit()

    def _getSchemaVersion(self):
        return self._rootObj.attrib.get('version', self.__class__.version)

    def parseStream(self, fromStream, validate = False, schemaDir = None):
        if isinstance(fromStream, (str, unicode)):
            self._rootObj = etree.fromstring(fromStream)
        elif isinstance(fromStream, etree._Element):
            self._rootObj = fromStream
        else:
            self._rootObj = etree.parse(fromStream).getroot()
        self._postinit()
        self._postprocess(validate=validate)

    @classmethod
    def validate(cls, stream, schemaDir, version):
        tree = etree.parse(stream)
        return tree

    def setId(self, id):
        self._rootObj.attrib['id'] = id

    def getId(self):
        return self._rootObj.attrib.get('id')

    id = property(getId, setId)

    def _postinit(self):
        pass

    def _postprocess(self, validate=True):
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
            if fieldDesc.multiple or fieldDesc.listType:
                child.attrib['list'] = 'true'
            else:
                child.attrib.pop('list', None)
            if fieldDesc.listType:
                field = dnodes.ListField(nodeDescriptor=fieldDesc)
                childName = fieldDesc._descriptor.getRootElement()
                for csub in child.iterchildren(childName):
                    field.append(DescriptorData(fromStream=csub,
                    descriptor=fieldDesc._descriptor, rootElement=childName))
            elif fieldDesc.descriptor:
                field = DescriptorData(fromStream=child,
                    descriptor=fieldDesc._descriptor, rootElement=nodeName)
            else:
                # Disable constraint checking, we will do it at the end
                field = dnodes._DescriptorDataField(child, fieldDesc,
                    checkConstraints = False)
            self._fields.append(field)
            self._fieldsMap[nodeName] = field
        self._addMissingRequiredFieldsWithDefault()
        if validate:
            self.checkConstraints()

    def _addMissingRequiredFieldsWithDefault(self):
        # Add required fields with a default that might be missing
        for dfield in self._descriptor.getDataFields():
            nodeName = dfield.name
            if nodeName in self._fieldsMap:
                # We already saw this field
                continue
            if not (dfield.required and dfield.default):
                continue
            if dfield.conditional:
                # We don't want to enforce conditionals with defaults just yet
                continue
            child = etree.Element(nodeName)
            if dfield.multiple:
                for v in dfield.default:
                    cv = etree.SubElement(child, "item")
                    cv.text = str(v)
            else:
                child.text = str(dfield.default[0])
            field = dnodes._DescriptorDataField(child, dfield,
                checkConstraints = False)
            self._fields.append(field)
            self._fieldsMap[nodeName] = field

    def getFields(self):
        return [ x for x in self._fields ]

    def addField(self, name, value = None, checkConstraints=True):
        field = self._addField(self._descriptor, self._rootObj, name, value)
        if checkConstraints:
            field.checkConstraints()
        self._fields.append(field)
        self._fieldsMap[name] = field

    def _addField(self, descriptor, parent, name, value):
        # Do not add the field if it was not defined
        fdesc = descriptor.getDataField(name)
        if fdesc is None:
            raise errors.UndefinedFactoryDataField(name)

        elm = etree.SubElement(parent, name)
        field = None
        if fdesc.descriptor:
            subdesc = fdesc._descriptor
            field = self._addCompoundTypeField(subdesc, elm, value)
        elif fdesc.listType:
            elm.attrib['list'] = 'true'
            subdesc = fdesc._descriptor
            subName = subdesc.getRootElement()
            field = dnodes.ListField(nodeDescriptor=fdesc)
            for val in value:
                subelm = etree.SubElement(elm, subName)
                field.append(self._addCompoundTypeField(subdesc, subelm, val))
        elif fdesc.multiple:
            if not isinstance(value, list):
                raise errors.DataValidationError("Expected multi-value")
            elm.attrib['list'] = 'true'
            for val in value:
                val = self._cleanseValue(fdesc, val)
                subnode = etree.SubElement(elm, 'item')
                subnode.text = val
        else:
            value = self._cleanseValue(fdesc, value)
            elm.text = value
        if field is None:
            field = dnodes._DescriptorDataField(elm, fdesc,
                checkConstraints=False)
        return field

    def _addCompoundTypeField(self, descriptor, parent, value):
        if hasattr(value, 'getFields'):
            for f in value.getFields():
                self._addField(descriptor, parent, f.getName(), f.getValue())
        else:
            for k, v in value.items():
                self._addField(descriptor, parent, k, v)
        field = DescriptorData(fromStream=parent,
            descriptor=descriptor, rootElement=parent.tag,
            validate=False)
        return field

    def getField(self, name):
        if name not in self._fieldsMap:
            return None
        fdata = self._fieldsMap[name]
        if hasattr(fdata, 'getValue'):
            return fdata.getValue()
        return fdata

    def checkConstraints(self, raiseException=True):
        errorList = []

        for field in self._fields:
            errorList.extend(field.checkConstraints(raiseException=False))

        errorList.extend(self._checkRequiredFields(
            self._descriptor, self._fieldsMap))

        if errorList and raiseException:
            raise errors.ConstraintsValidationError(errorList)
        return errorList

    @classmethod
    def _checkRequiredFields(cls, descriptor, fieldsMap):
        errorList = []
        # look for missing fields
        missingRequiredFields = [ x
            for x in descriptor.getDataFields()
                if x.name not in fieldsMap
                    and x.required ]
        # A required field may be missing if:
        # * the field has a default
        # * the conditional is eq and the field is missing or the field value is
        # not what the conditional specified
        # * the conditional is noteq and the field is present and its value is
        # what the conditional specified
        missingRequiredFields = [ x
            for x in missingRequiredFields
                if cls._filterEqConditionals(x, fieldsMap) ]

        for field in missingRequiredFields:
            errorList.append("Missing field: '%s'" % field.name)
        return errorList

    @classmethod
    def _filterEqConditionals(cls, field, fieldsMap):
        # Filter eq conditionals that are not satisfied
        if field.conditional is None:
            return True
        condFieldName = field.conditional.fieldName
        if condFieldName not in fieldsMap:
            return False
        switchField = fieldsMap[condFieldName]
        condValue = dnodes._cast(field.conditional.value,
            switchField._nodeDescriptor.type)
        return (switchField.getValue() == condValue)


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
    __slots__ = []


class SystemConfigurationDescriptor(BaseDescriptor):
    """
    Class for representing configuration descriptors for systems.
    """
    __slots__ = []

    RootNode = 'configuration_descriptor'


class FactoryDescriptor(BaseDescriptor):
    """
    Class for representing factory descriptors.
    """
    __slots__ = []

    RootNode = 'factory'

    def getSupportedFiles(self):
        md = self._rootObj.get_metadata()
        return md.get_supportedFiles().get_file()

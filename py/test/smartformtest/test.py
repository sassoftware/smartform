#!/usr/bin/python2.4
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


import testsuite
testsuite.setup()

import os
from StringIO import StringIO

from testrunner import testcase

from smartform import descriptor
from smartform import descriptor_nodes as dnodes
from smartform import descriptor_errors as errors

multiValues = """<values>
      <value>one</value>
      <value>two</value>
      <value>three</value>
    </values>"""

multiValuesSingleValue = "<value>Just one value</value>"

basicXmlDef2 = """<?xml version='1.0' encoding='UTF-8'?>
<factory xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
  <metadata>
    <displayName>metadata display name</displayName>
    <descriptions><desc>metadata description</desc></descriptions>
    <supportedFiles>
      <file>tar</file>
      <file>gzip</file>
    </supportedFiles>
  </metadata>
  <dataFields>
      <field>
        <name>foo</name>
        <descriptions><desc>Field description for foo</desc></descriptions>
        <type>int</type>
      </field>
      <field>
        <name>bar</name>
        <descriptions><desc>Field description for bar</desc></descriptions>
        <type>bool</type>
      </field>
      <field>
        <name>baz</name>
        <descriptions><desc>Field description for baz</desc></descriptions>
        <type>str</type>
        <multiple>true</multiple>
      </field>
  </dataFields>
</factory>"""

class BaseTest(testcase.TestCase):
    def setUp(self):
        testcase.TestCase.setUp(self)
        self.setUpSchemaDir()

    def setUpSchemaDir(self):
        self.schemaDir = ""
        schemaFile = "descriptor-%s.xsd" % descriptor.BaseDescriptor.version
        schemaDir = os.path.join(os.environ['SMARTFORM_PATH'], 'xsd')
        if not os.path.exists(os.path.join(schemaDir, schemaFile)):
            # Not running from a checkout
            schemaDir = descriptor._BaseClass.schemaDir
            assert(os.path.exists(os.path.join(schemaDir, schemaFile)))
        self.schemaDir = schemaDir
        self.mock(descriptor.BaseDescriptor, 'schemaDir', schemaDir)
        self.mock(descriptor.DescriptorData, 'schemaDir', schemaDir)


class FactoryDescriptorTest(BaseTest):
    def testSupportedFiles(self):
        desc = descriptor.FactoryDescriptor()
        desc.parseStream(StringIO(basicXmlDef2))

        self.failUnlessEqual(desc.getSupportedFiles(), ['tar', 'gzip'])

        desc.setSupportedFiles(['george', ])
        self.failUnlessEqual(desc.getSupportedFiles(), ['george'])


class DescriptorTest(BaseTest):
    """Schema validation tests for factory data defintion goes here"""

    def testCreateDescriptor1(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setId("Some-ID")
        dsc.setDisplayName('Cloud Information')
        dsc.addDescription('Configure Super Cloud')

        dsc.addDataField('cloudType', type = 'str',
            descriptions = [ dsc.Description('Cloud Type') ],
            help = [ ('http://url1/en', None), ('http://url1/lol', 'en_LOL')])
        dsc.addDataField('multiField', type = 'str', multiple = True,
            required = True,
            descriptions = [ dsc.Description('Multi Field') ],
            constraints = [
                dict(constraintName = 'legalValues',
                     values = ['Foo', 'Bar', 'Baz']),
            ])

        self.assertXMLEquals(dsc.toxml(), xmlDescriptor1)

        self.failUnlessEqual([ x.helpAsDict
                for x in dsc.getDataFields() ],
            [{None: 'http://url1/en', 'en_LOL': 'http://url1/lol'}, {}])

    def testDeleteDataField(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setId("Some-ID")
        dsc.setDisplayName('Cloud Information')
        dsc.addDescription('Configure Super Cloud')

        dsc.addDataField('field1', type = 'str',
            descriptions = [ dsc.Description('Field 1') ])
        dsc.addDataField('field2', type = 'str',
            descriptions = [ dsc.Description('Field 2') ])
        dsc.addDataField('field3', type = 'str',
            descriptions = [ dsc.Description('Field 3') ])
        # Add field1 again; it will remove the first one and place this
        # one after field3
        dsc.addDataField('field1', type = 'str',
            descriptions = [ dsc.Description('Field 1 modified') ])
        dsc.deleteDataField('field3')

        self.failUnlessEqual(
            [ x.descriptions.asDict() for x in dsc.getDataFields() ],
            [{None: 'Field 2'}, {None: 'Field 1 modified'}])

    def testUseTupleForDescriptions(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setId("Some-ID")
        dsc.setDisplayName('Cloud Information')
        #dsc.addDescription([('msg in lang 1', 'lang1'),
        #    ('msg in lang 2', 'lang2'), 'Default lang'])
        dsc.addDescription("Description in default lang")
        dsc.addDescription("Description in lang 1", "lang1")

        dsc.addDataField('cloudType', type = 'str',
            descriptions = [('field msg in lang 1', 'lang1'),
                ('field msg in lang 2', 'lang2'), 'Default lang'])
        self.assertXMLEquals(dsc.toxml(), """
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" id="Some-ID" version="1.1">
    <metadata>
        <displayName>Cloud Information</displayName>
        <descriptions>
            <desc>Description in default lang</desc>
            <desc lang="lang1">Description in lang 1</desc>
        </descriptions>
    </metadata>
    <dataFields>
        <field>
            <name>cloudType</name>
            <descriptions>
                <desc>Default lang</desc>
                <desc lang="lang1">field msg in lang 1</desc>
                <desc lang="lang2">field msg in lang 2</desc>
            </descriptions>
            <type>str</type>
        </field>
    </dataFields>
</descriptor>
""")

    def testParseDescriptor1(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor1)
        self.failUnlessEqual(dsc.getId(), 'Some-ID')
        self.failUnlessEqual(dsc.getDisplayName(), 'Cloud Information')
        self.failUnlessEqual(dsc.getDescriptions(),
            {None : 'Configure Super Cloud'})
        self.failUnlessEqual([x.name for x in dsc.getDataFields()],
            ['cloudType', 'multiField'])
        self.failUnlessEqual([x.descriptions.asDict() for x in dsc.getDataFields()],
            [{None: 'Cloud Type'}, {None: 'Multi Field'}])
        self.failUnlessEqual([x.required for x in dsc.getDataFields()],
            [None, True])
        self.failUnlessEqual([x.type for x in dsc.getDataFields()],
            ['str', 'str'])
        self.failUnlessEqual([x.multiple for x in dsc.getDataFields()],
            [None, True])
        self.failUnlessEqual([x.presentation() for x in dsc.getDataFields()], [
          [],
          [{'constraintName': 'legalValues', 'values': ['Foo', 'Bar', 'Baz']}],
        ])

    def testSerializeDescriptor1(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor1)
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xmlDescriptor1)

    def testParseDescriptorData1(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor1)
        ddata = descriptor.DescriptorData(fromStream = xmlDescriptorData1,
            descriptor = dsc)

        self.failUnlessEqual(dsc.getId(), 'Some-ID')
        self.failUnlessEqual(
            [(x.getName(), x.getValue()) for x in ddata.getFields()],
            [('cloudType', 'ec2'), ('multiField', ['Foo', 'Baz'])])

    def testSerializeDescriptorData1(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor1)
        ddata = descriptor.DescriptorData(fromStream = xmlDescriptorData1,
            descriptor = dsc)
        sio = StringIO()
        ddata.serialize(sio)
        expXml = xmlDescriptorData1.replace("<multiField>",
           '<multiField list="true">')
        self.assertXMLEquals(sio.getvalue(), expXml)

    def testExtraData(self):
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('foo', type = 'int')
        fDef.addDataField('bar', type = 'int')

        data = """<descriptorData><foo>1</foo><baz>2</baz></descriptorData>"""

        fData = descriptor.DescriptorData(fromStream = data, descriptor = fDef)

    def testParseDescriptor2(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor2)

        self.failUnlessEqual([x.name for x in dsc.getDataFields()],
            ['cloudType', 'multiField'])

        multi = dsc.getDataField('multiField')
        self.failUnlessEqual([ x.key for x in multi.type ],
            ['small', 'medium'])
        self.failUnlessEqual([ x.descriptions.asDict() for x in multi.type ],
            [{None: 'Small value'}, {None: 'Medium value'}])

        dsc.addDataField('lotsaValues',
            descriptions = [dsc.Description("foo")],
            type = [
                dsc.ValueWithDescription('one',
                    descriptions = [dsc.Description("One")]),
                dsc.ValueWithDescription('two',
                    descriptions = [dsc.Description("Two")]),
            ])
        multi = dsc.getDataField('lotsaValues')
        self.failUnlessEqual([ x.key for x in multi.type ],
            ['one', 'two'])
        self.failUnlessEqual([ x.descriptions.asDict() for x in multi.type ],
            [{None: 'One'}, {None: 'Two'}])

        sio = StringIO()
        dsc.serialize(sio)
        newXml = xmlDescriptor2.replace("  </dataFields>",
            "%s\n  </dataFields>" % newDescriptorField)
        self.assertXMLEquals(sio.getvalue(), newXml)

        sio.seek(0)
        dsc = descriptor.ConfigurationDescriptor(fromStream = sio)
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), newXml)

    def testSerializeDescriptor2(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor2)
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xmlDescriptor2)

    def testParseDescriptor3Password(self):
        xml = xmlDescriptor3 % passwordFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

        nLen = len(dsc.getDataFields())

        self.failUnlessEqual([x.name for x in dsc.getDataFields()],
            ['passwordFieldStr', 'passwordFieldInt'])

        self.failUnlessEqual([x.required for x in dsc.getDataFields()],
            [True] * nLen)

        self.failUnlessEqual([x.password for x in dsc.getDataFields()],
            [True] * nLen)

        self.failUnlessEqual([x.hidden for x in dsc.getDataFields()],
            [None] * nLen)

    def testSerializeDescriptor3Password(self):
        xml = xmlDescriptor3 % passwordFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xml)

    def testParseDescriptor3Hidden(self):
        xml = xmlDescriptor3 % hiddenFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

        self.failUnlessEqual(dsc.getRootElement(), 'blahBlah')

        nLen = len(dsc.getDataFields())

        self.failUnlessEqual([x.name for x in dsc.getDataFields()],
            ['hiddenFieldStr', 'hiddenFieldInt'])

        self.failUnlessEqual([x.required for x in dsc.getDataFields()],
            [True, False])

        self.failUnlessEqual([x.password for x in dsc.getDataFields()],
            [None] * nLen)

        self.failUnlessEqual([x.hidden for x in dsc.getDataFields()],
            [True] * nLen)

    def testSerializeDescriptor3Hidden(self):
        xml = xmlDescriptor3 % hiddenFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xml)

    def testParseDescriptorData3Hidden(self):
        xml = xmlDescriptor3 % hiddenFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

        xml = xmlDescriptorData3 % (dsc.getRootElement(), hiddenFields3Data,
            dsc.getRootElement())

        ddata = descriptor.DescriptorData(fromStream = xml,
            descriptor = dsc)

        self.failUnlessEqual(dsc.getId(), 'Some-ID')
        self.failUnlessEqual(
            [(x.getName(), x.getValue()) for x in ddata.getFields()],
            [('hiddenFieldStr', 'abc'), ('hiddenFieldInt', 1)])

        sio = StringIO()
        ddata.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xml)

    def testParseDescriptorData3Password(self):
        xml = xmlDescriptor3 % hiddenFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

        xml = xmlDescriptorData3 % (dsc.getRootElement(), hiddenFields3Data,
            dsc.getRootElement())

        ddata = descriptor.DescriptorData(fromStream = xml,
            descriptor = dsc)

        self.failUnlessEqual(dsc.getId(), 'Some-ID')
        self.failUnlessEqual(
            [(x.getName(), x.getValue()) for x in ddata.getFields()],
            [('hiddenFieldStr', 'abc'), ('hiddenFieldInt', 1)])

    def testParseDescriptorData3Password(self):
        # RBL-3847: we used to send the passwords masked out, not anymore
        xml = xmlDescriptor3 % passwordFields3
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

        xml = xmlDescriptorData3 % (dsc.getRootElement(), passwordFields3Data,
            dsc.getRootElement())

        ddata = descriptor.DescriptorData(fromStream = xml,
            descriptor = dsc)

        self.failUnlessEqual(dsc.getId(), 'Some-ID')
        self.failUnlessEqual(
            [(x.getName(), x.getValue(), type(x.getValue())) for x in ddata.getFields()],
            [
                ('passwordFieldStr', 'Real string', dnodes.ProtectedUnicode),
                ('passwordFieldInt', 42, int)
            ])

        sio = StringIO()
        ddata.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xml)

        # Construct a response
        ddata = descriptor.DescriptorData(descriptor = dsc)
        ddata.setId('Some-ID')
        ddata.addField('passwordFieldStr', 'Real string')
        ddata.addField('passwordFieldInt', 42)

        # The password fields should have been whited out
        sio = StringIO()
        ddata.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xml)

    def testDescriptorDataMultiField(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor2)

        data = """<descriptorData><multiField><item>small</item><item>medium</item></multiField></descriptorData>"""
        ddata = descriptor.DescriptorData(fromStream=data, descriptor=dsc)
        self.failUnlessEqual(ddata.getField('multiField'), ['small', 'medium'])

    def testParseVersion10(self):
        xml = xmlDescriptor2.replace('descriptor-1.1', 'descriptor-1.0')
        dsc = descriptor.ConfigurationDescriptor(fromStream = xml)

    def testCompoundType1(self):
        dsc1 = descriptor.ConfigurationDescriptor()
        dsc1.setId("apache-configuration/process-info")
        dsc1.setRootElement("blabbedy-blah")
        dsc1.setDisplayName('Process Ownership Information')
        dsc1.addDescription('Process Ownership Information')
        dsc1.addDataField("user", type="str", default="apache", required=True,
            descriptions="User")
        dsc1.addDataField("group", type="str", default="apache", required=True,
            descriptions="Group")

        vhost = descriptor.ConfigurationDescriptor()
        vhost.setId("apache-configuration/vhost")
        vhost.setRootElement('vhost')
        vhost.setDisplayName('Virtual Host Configuration')
        vhost.addDescription('Virtual Host Configuration')
        vhost.addDataField('serverName', type="str", required=True,
            descriptions="Virtual Host Name")
        vhost.addDataField('documentRoot', type="str", required=True,
            descriptions="Virtual Host Document Root")

        dsc = descriptor.ConfigurationDescriptor()
        dsc.setRootElement('configuration')
        dsc.setId("apache-configuration")
        dsc.setDisplayName('Apache Configuration')
        dsc.addDescription('Apache Configuration')

        dsc.addDataField('port', type="int",
            required=True, descriptions="Apache Port")
        dsc.addDataField('processInfo', type=dsc.CompoundType(dsc1),
            required=True, descriptions="Process Ownership Information")
        dsc.addDataField('vhosts', type=dsc.ListType(vhost),
            required=True, descriptions="Virtual Hosts",
            constraints=[dict(constraintName='uniqueKey', value="serverName"),
                dict(constraintName="minLength", value=1)])

        sio = StringIO()
        dsc.serialize(sio)

        # Make sure the uniqueKey and minLength constraints got in the
        # proper spot
        sio.seek(0)
        tree = descriptor.etree.parse(sio)
        namespaces = dict(
            dsc="http://www.rpath.com/permanent/descriptor-%s.xsd" % descriptor.constants.version)
        # Select vhosts
        constraints = tree.xpath('/dsc:descriptor/dsc:dataFields/dsc:field[dsc:name="vhosts"]/dsc:constraints',
            namespaces=namespaces)
        self.assertXMLEquals(descriptor.etree.tostring(constraints[0]),
            """\
<constraints xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <uniqueKey>serverName</uniqueKey>
    <minLength>1</minLength>
</constraints>""")

        # Make sure we can load it
        sio.seek(0)
        dsc2 = descriptor.ConfigurationDescriptor(fromStream=sio)
        sio2 = StringIO()
        dsc2.serialize(sio2)
        self.assertXMLEquals(sio.getvalue(), sio2.getvalue())

        dataXml = """\
<configuration version="1.1">
  <port>10</port>
  <processInfo>
    <group>nogroup</group>
    <user>nobody</user>
  </processInfo>
  <vhosts list="true">
    <vhost>
      <serverName>a.example.com</serverName>
      <documentRoot>/a</documentRoot>
    </vhost>
    <vhost>
      <serverName>b.example.com</serverName>
      <documentRoot>/b</documentRoot>
    </vhost>
  </vhosts>
</configuration>"""
        # Take out list=true, serializing DescriptorData should put it
        # back
        ddata = descriptor.DescriptorData(
            fromStream=dataXml.replace(' list="true"', ''),
            descriptor=dsc)
        self.assertEquals(ddata.getField('port'), 10)
        processInfo = ddata.getField('processInfo')
        self.assertEquals(
            (processInfo.getField('user'), processInfo.getField('group')),
            ('nobody', 'nogroup'))
        vhosts = ddata.getField('vhosts')
        self.failUnlessEqual(
            [ (x.getField('serverName'), x.getField('documentRoot'))
                for x in vhosts ],
            [ ('a.example.com', '/a'), ('b.example.com', '/b') ])

        sio2.truncate(0)
        ddata.serialize(sio2)
        self.assertXMLEquals(sio2.getvalue(), dataXml)

        # New descriptor, we set the values by hand
        ddata = descriptor.DescriptorData(descriptor=dsc)
        ddata.addField('port', 10)
        ddata.addField('processInfo', dict(user='nobody', group='nogroup'))
        ddata.addField('vhosts', [
            dict(serverName='a.example.com', documentRoot='/a'),
            dict(serverName='b.example.com', documentRoot='/b'),
        ])

        sio2.truncate(0)
        ddata.serialize(sio2)
        self.assertXMLEquals(sio2.getvalue(), dataXml)

        # New descriptor, with some required fields missing
        ddata = descriptor.DescriptorData(descriptor=dsc)
        ddata.addField('port', 10)
        # This will work, since we have a default for the required field
        ddata.addField('processInfo', dict(user='nobody'))
        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            ddata.addField, 'vhosts', [
                dict(serverName='a.example.com'),
                dict(documentRoot='/b'),
            ])
        self.assertEquals(e.args[0],
            ["Missing field: 'documentRoot'", "Missing field: 'serverName'"])
        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            ddata.checkConstraints)
        self.assertEquals(e.args[0],
            ["Missing field: 'vhosts'",])

    def testCompoundType2(self):
        # RCE-951
        xml = """\
<?xml version="1.0"?>
<configuration_descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1">
  <metadata>
    <displayName>Configuration Descriptor</displayName>
    <rootElement>configuration</rootElement>
    <descriptions>
      <desc>Configuration Descriptor</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>port</name>
      <descriptions>
        <desc lang="en_US">Apache Port</desc>
      </descriptions>
      <type>int</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
    <field>
      <name>processInfo</name>
      <descriptions>
        <desc lang="en_US">Process Ownership Information</desc>
      </descriptions>
      <type>compoundType</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <descriptor version="1.1" id="apache-configuration/process-info">
        <metadata>
          <displayName>Process Ownership Information</displayName>
          <descriptions>
            <desc lang="en_US">Process Ownership Information</desc>
          </descriptions>
        </metadata>
        <dataFields>
          <field>
            <name>user</name>
            <descriptions>
              <desc lang="en_US">User</desc>
            </descriptions>
            <help href="None"/>
            <type>str</type>
            <enumeratedType/>
            <multiple>false</multiple>
            <default>apache</default>
            <constraints>
              <descriptions/>
              <range/>
              <minLength>0</minLength>
            </constraints>
            <required>true</required>
            <allowFileContent>false</allowFileContent>
            <hidden>false</hidden>
            <password>false</password>
            <conditional/>
            <prompt/>
          </field>
          <field>
            <name>group</name>
            <descriptions>
              <desc lang="en_US">Group</desc>
            </descriptions>
            <help href="None"/>
            <type>str</type>
            <enumeratedType/>
            <multiple>false</multiple>
            <default>apache</default>
            <constraints>
              <descriptions/>
              <range/>
              <minLength>0</minLength>
            </constraints>
            <required>true</required>
            <allowFileContent>false</allowFileContent>
            <hidden>false</hidden>
            <password>false</password>
            <conditional/>
            <prompt/>
          </field>
        </dataFields>
      </descriptor>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
    <field>
      <name>vhosts</name>
      <descriptions>
        <desc>Virtual Hosts</desc>
      </descriptions>
      <type>listType</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <listType>
        <descriptor version="1.1" id="apache-configuration/vhost">
          <metadata>
            <displayName>Virtual Host Configuration</displayName>
            <rootElement>vhost</rootElement>
            <descriptions>
              <desc lang="en_US">Virtual Host Configuration</desc>
            </descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>serverName</name>
              <descriptions>
                <desc lang="en_US">Virtual Host Name</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt/>
            </field>
            <field>
              <name>documentRoot</name>
              <descriptions>
                <desc lang="en_US">Virtual Host Document Root</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt/>
            </field>
          </dataFields>
        </descriptor>
      </listType>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <uniqueKey>serverName</uniqueKey>
        <minLength>1</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
  </dataFields>
</configuration_descriptor>
"""

        sanitizedXml = """\
<?xml version="1.0"?>
<configuration_descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1">
  <metadata>
    <displayName>Configuration Descriptor</displayName>
    <rootElement>configuration</rootElement>
    <descriptions>
      <desc>Configuration Descriptor</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>port</name>
      <descriptions>
        <desc lang="en_US">Apache Port</desc>
      </descriptions>
      <type>int</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
    <field>
      <name>processInfo</name>
      <descriptions>
        <desc lang="en_US">Process Ownership Information</desc>
      </descriptions>
      <type>compoundType</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <descriptor version="1.1" id="apache-configuration/process-info">
        <metadata>
          <displayName>Process Ownership Information</displayName>
          <descriptions>
            <desc lang="en_US">Process Ownership Information</desc>
          </descriptions>
        </metadata>
        <dataFields>
          <field>
            <name>user</name>
            <descriptions>
              <desc lang="en_US">User</desc>
            </descriptions>
            <help href="None"/>
            <type>str</type>
            <multiple>false</multiple>
            <default>apache</default>
            <constraints>
              <descriptions/>
              <minLength>0</minLength>
            </constraints>
            <required>true</required>
            <allowFileContent>false</allowFileContent>
            <hidden>false</hidden>
            <password>false</password>
            <prompt/>
          </field>
          <field>
            <name>group</name>
            <descriptions>
              <desc lang="en_US">Group</desc>
            </descriptions>
            <help href="None"/>
            <type>str</type>
            <multiple>false</multiple>
            <default>apache</default>
            <constraints>
              <descriptions/>
              <minLength>0</minLength>
            </constraints>
            <required>true</required>
            <allowFileContent>false</allowFileContent>
            <hidden>false</hidden>
            <password>false</password>
            <prompt/>
          </field>
        </dataFields>
      </descriptor>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
    <field>
      <name>vhosts</name>
      <descriptions>
        <desc>Virtual Hosts</desc>
      </descriptions>
      <type>listType</type>
      <section>
        <key>apache_configurator</key>
      </section>
      <listType>
        <descriptor version="1.1" id="apache-configuration/vhost">
          <metadata>
            <displayName>Virtual Host Configuration</displayName>
            <rootElement>vhost</rootElement>
            <descriptions>
              <desc lang="en_US">Virtual Host Configuration</desc>
            </descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>serverName</name>
              <descriptions>
                <desc lang="en_US">Virtual Host Name</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt/>
            </field>
            <field>
              <name>documentRoot</name>
              <descriptions>
                <desc lang="en_US">Virtual Host Document Root</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt/>
            </field>
          </dataFields>
        </descriptor>
      </listType>
      <multiple>false</multiple>
      <constraints>
        <descriptions/>
        <uniqueKey>serverName</uniqueKey>
        <minLength>1</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt/>
    </field>
  </dataFields>
</configuration_descriptor>
"""
        dsc = descriptor.SystemConfigurationDescriptor(fromStream=xml)
        xml2 = dsc.toxml()
        self.assertXMLEquals(xml2, sanitizedXml)

        # RCE-955
        xml = """\
<configuration id="https://qa3.eng.rpath.com/api/v1/inventory/systems/756/configuration" href="https://qa3.eng.rpath.com/api/v1/inventory/systems/756/configuration">
  <port>8080</port>
  <processInfo/>
  <vhosts>
    <vhost>
      <serverName>a.com</serverName>
      <documentRoot>/srv/a</documentRoot>
    </vhost>
  </vhosts>
</configuration>
"""
        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=dsc)
        xml2 = ddata.toxml()
        self.assertXMLEquals(xml2, xml.replace('<vhosts', '<vhosts list="true"'))

        # Trip the minLength check
        xml = """\
<configuration id="https://qa3.eng.rpath.com/api/v1/inventory/systems/756/configuration" href="https://qa3.eng.rpath.com/api/v1/inventory/systems/756/configuration">
  <port>8080</port>
  <processInfo/>
  <vhosts/>
</configuration>
"""

        err = self.failUnlessRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData, fromStream=xml, descriptor=dsc)
        self.failUnlessEqual(err.args[0],
            ["'Virtual Hosts': fails minimum length check '1' (actual: 0)"])

    def testCompoundType3_conditional(self):
        # A descriptor field being conditional on a boolean field
        xml = """\
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
  <metadata>
    <displayName>FooDescriptor</displayName>
    <rootElement>descriptor_data</rootElement>
    <descriptions>
      <desc>Description</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>imageId</name>
      <descriptions>
        <desc>Image ID</desc>
      </descriptions>
      <type>str</type>
      <default>7</default>
      <required>true</required>
      <hidden>true</hidden>
    </field>
    <field>
      <name>withConfiguration</name>
      <descriptions/>
      <type>bool</type>
      <default>False</default>
      <required>true</required>
    </field>
    <field>
      <name>system_configuration</name>
      <descriptions>
        <desc>System Configuration</desc>
      </descriptions>
      <type>compoundType</type>
      <descriptor version="1.1">
        <metadata>
          <displayName>System Configuration</displayName>
          <descriptions>
            <desc>System Configuration</desc>
          </descriptions>
        </metadata>
        <dataFields>
          <field>
            <name>user</name>
            <descriptions>
              <desc>User</desc>
            </descriptions>
            <type>str</type>
            <required>true</required>
          </field>
          <field>
            <name>group</name>
            <descriptions>
              <desc>Group</desc>
            </descriptions>
            <type>str</type>
            <required>true</required>
          </field>
        </dataFields>
      </descriptor>
      <required>true</required>
      <conditional>
        <fieldName>withConfiguration</fieldName>
        <operator>eq</operator>
        <value>true</value>
      </conditional>
    </field>
  </dataFields>
</descriptor>"""
        descr = descriptor.ConfigurationDescriptor(fromStream=xml)
        xml = """\
<descriptor_data>
  <imageId>123</imageId>
</descriptor_data>
"""
        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=descr)
        self.failUnlessEqual(
            [ (x.getName(), x.getValue()) for x in ddata.getFields() ],
            [ ('imageId', '123'), ('withConfiguration', False), ])

        xml = """\
<descriptor_data>
  <imageId>123</imageId>
  <withConfiguration>true</withConfiguration>
</descriptor_data>
"""
        e = self.assertRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData, fromStream=xml, descriptor=descr)
        self.assertEqual(e.args[0],
            ["Missing field: 'system_configuration'"])

        xml = """\
<descriptor_data>
  <imageId>123</imageId>
  <withConfiguration>true</withConfiguration>
  <system_configuration>
  </system_configuration>
</descriptor_data>
"""
        e = self.assertRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData, fromStream=xml, descriptor=descr)
        self.assertEqual(e.args[0],
            ["Missing field: 'user'", "Missing field: 'group'", ])

        xml = """\
<descriptor_data>
  <imageId>123</imageId>
  <withConfiguration>true</withConfiguration>
  <system_configuration>
    <user>forrest</user>
    <group>greenbow</group>
  </system_configuration>
</descriptor_data>
"""

        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=descr)
        fields = ddata.getFields()
        simpleFields, complexFields = fields[:-1], fields[-1:]
        self.failUnlessEqual(
            [ (x.getName(), x.getValue()) for x in simpleFields ],
            [ ('imageId', '123'), ('withConfiguration', True), ])

        self.failUnlessEqual(
            [
                [(x.getName(), x.getValue()) for x in y.getFields()]
                for y in complexFields ],
            [
                [ ('user', 'forrest'), ('group', 'greenbow') ]
            ])

        # Change the embedded descriptor to add some defaults
        complexField = descr.getDataField('system_configuration')
        for field in complexField._descriptor.getDataFields():
            field.set_default(['apache'])

        xml = """\
<descriptor_data>
  <imageId>123</imageId>
  <withConfiguration>true</withConfiguration>
  <system_configuration>
  </system_configuration>
</descriptor_data>
"""

        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=descr)
        fields = ddata.getFields()
        simpleFields, complexFields = fields[:-1], fields[-1:]
        self.failUnlessEqual(
            [ (x.getName(), x.getValue()) for x in simpleFields ],
            [ ('imageId', '123'), ('withConfiguration', True), ])

        self.failUnlessEqual(
            [
                [(x.getName(), x.getValue()) for x in y.getFields()]
                for y in complexFields ],
            [
                [ ('user', 'apache'), ('group', 'apache') ]
            ])

    def testSections1(self):
        desc1 = descriptor.ConfigurationDescriptor()
        desc1.setDisplayName('Configuration Descriptor')
        desc1.addDescription('Configuration Descriptor')
        desc1.addDataField('motd', type='str', default='Welcome!',
            required=True, descriptions='Message of the day')
        desc1.addDataField('iis_port', type='int', default=80, required=True,
            descriptions='Port for IIS to listen on',
            section={'key': 'middleware', 'descriptions': 'Middleware'},
            prompt='IIS Port')
        desc1.addDataField('sqlserver_port', type='int', default=1234,
            required=True, descriptions='Port for SQLSserver to listen on',
            section={'key': 'middleware', 'descriptions': 'Middleware'},
            prompt='SQLServer Port')

        xml = desc1.toxml()

        desc2 = descriptor.ConfigurationDescriptor()
        desc2.parseStream(StringIO(xml))

        fields = dict((x.get_name(), x) for x in desc2.getDataFields())
        iis_port = fields.get('iis_port').get_section()
        self.failUnlessEqual(iis_port.get_key(), 'middleware')
        self.failUnlessEqual(iis_port.get_descriptions().asDict(),
            {None: 'Middleware'})

        sqlserver_port = fields.get('sqlserver_port').get_section()
        self.failUnlessEqual(sqlserver_port.get_key(), 'middleware')
        self.failUnlessEqual(sqlserver_port.get_descriptions().asDict(),
            {None: 'Middleware'})

        motd = fields.get('motd')
        self.failUnlessEqual(motd.get_section(), None)

    def testDescriptorWithExtraData(self):
        xml = """\
<descriptor xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd">
  <metadata>
    <displayName>postgres_configurator</displayName>
    <descriptions>
      <desc lang="en_US">postgres_configurator</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>postgres_listen_addresses</name>
      <descriptions>
        <desc lang="en_US">PostgreSQL Listen Addresses</desc>
      </descriptions>
      <type>str</type>
      <default>*</default>
      <required>false</required>
      <prompt>
        <desc lang="en_US">PostgreSQL Listen Addresses</desc>
      </prompt>
      <allowFileContent>false</allowFileContent>
      <conditional/>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <hidden>false</hidden>
      <multiple>false</multiple>
      <password>false</password>
      <uid>4D2234B1-1EC7-41B6-93FB-30D8B421C2C6</uid>
    </field>
    <field>
      <name>postgres_port</name>
      <descriptions>
        <desc lang="en_US">Port for PostgreSQL</desc>
      </descriptions>
      <type>str</type>
      <default>5432</default>
      <required>true</required>
      <prompt>
        <desc lang="en_US">Port for PostgreSQL</desc>
      </prompt>
      <allowFileContent>false</allowFileContent>
      <conditional/>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
        <range/>
        <legalValues/>
      </constraints>
      <enumeratedType/>
      <help/>
      <hidden>false</hidden>
      <multiple>false</multiple>
      <password>false</password>
      <uid>6C368FD7-BE46-886E-B390-30D8B422C460</uid>
    </field>
    <field>
      <name>iis_configuration</name>
      <descriptions>
        <desc lang="en_US">IIS Configuration Websites</desc>
      </descriptions>
      <type>listType</type>
      <listType>
        <descriptor>
          <metadata>
            <displayName>IIS Website Configuration</displayName>
            <rootElement>website</rootElement>
            <descriptions>
              <desc lang="en_US">Website Configuration</desc>
            </descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>website_name</name>
              <descriptions>
                <desc lang="en_US">domain for website</desc>
              </descriptions>
              <type>str</type>
              <default>www.testing.com</default>
              <required>true</required>
              <prompt>
                <desc lang="en_US">Host Name for Website</desc>
              </prompt>
              <allowFileContent>false</allowFileContent>
              <conditional/>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
                <range/>
              </constraints>
              <enumeratedType/>
              <help/>
              <hidden>false</hidden>
              <multiple>false</multiple>
              <password>false</password>
              <uid>43C65384-E346-198D-CA5D-6E6CA9F62F1C</uid>
            </field>
            <field>
              <name>port</name>
              <descriptions>
                <desc lang="en_US">Port for Website</desc>
              </descriptions>
              <type>str</type>
              <default>8080</default>
              <required>true</required>
              <prompt>
                <desc lang="en_US">Port for Website</desc>
              </prompt>
              <allowFileContent>false</allowFileContent>
              <conditional/>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
                <range/>
              </constraints>
              <enumeratedType/>
              <help/>
              <hidden>false</hidden>
              <multiple>false</multiple>
              <password>false</password>
              <uid>BD4E10EF-71BA-60C7-8CF0-6E6CA9FC6B73</uid>
            </field>
          </dataFields>
        </descriptor>
      </listType>
      <allowFileContent>false</allowFileContent>
      <conditional/>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
        <range/>
      </constraints>
      <enumeratedType/>
      <help/>
      <hidden>false</hidden>
      <multiple>false</multiple>
      <password>false</password>
      <prompt/>
      <required>false</required>
      <uid>CB6E82BF-CECB-61B6-43AD-6E6CA9F2875A</uid>
    </field>
  </dataFields>
</descriptor>"""

        descr = descriptor.ConfigurationDescriptor(fromStream=xml)
        # Serialize, should drop the additional crap
        retXml = descr.toxml()
        self.assertXMLEquals(retXml, """\
<descriptor xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd">
  <metadata>
    <displayName>postgres_configurator</displayName>
    <descriptions>
      <desc lang="en_US">postgres_configurator</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>postgres_listen_addresses</name>
      <descriptions>
        <desc lang="en_US">PostgreSQL Listen Addresses</desc>
      </descriptions>
      <type>str</type>
      <multiple>false</multiple>
      <default>*</default>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>false</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt>
        <desc lang="en_US">PostgreSQL Listen Addresses</desc>
      </prompt>
    </field>
    <field>
      <name>postgres_port</name>
      <descriptions>
        <desc lang="en_US">Port for PostgreSQL</desc>
      </descriptions>
      <type>str</type>
      <multiple>false</multiple>
      <default>5432</default>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>true</required>
      <allowFileContent>false</allowFileContent>
      <hidden>false</hidden>
      <password>false</password>
      <prompt>
        <desc lang="en_US">Port for PostgreSQL</desc>
      </prompt>
    </field>
    <field>
      <name>iis_configuration</name>
      <descriptions>
        <desc lang="en_US">IIS Configuration Websites</desc>
      </descriptions>
      <type>listType</type>
      <listType>
        <descriptor>
          <metadata>
            <displayName>IIS Website Configuration</displayName>
            <rootElement>website</rootElement>
            <descriptions>
              <desc lang="en_US">Website Configuration</desc>
            </descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>website_name</name>
              <descriptions>
                <desc lang="en_US">domain for website</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <default>www.testing.com</default>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt>
                <desc lang="en_US">Host Name for Website</desc>
              </prompt>
            </field>
            <field>
              <name>port</name>
              <descriptions>
                <desc lang="en_US">Port for Website</desc>
              </descriptions>
              <type>str</type>
              <multiple>false</multiple>
              <default>8080</default>
              <constraints>
                <descriptions/>
                <minLength>0</minLength>
              </constraints>
              <required>true</required>
              <allowFileContent>false</allowFileContent>
              <hidden>false</hidden>
              <password>false</password>
              <prompt>
                <desc lang="en_US">Port for Website</desc>
              </prompt>
            </field>
          </dataFields>
        </descriptor>
      </listType>
      <allowFileContent>false</allowFileContent>
      <constraints>
        <descriptions/>
        <minLength>0</minLength>
      </constraints>
      <required>false</required>
      <hidden>false</hidden>
      <multiple>false</multiple>
      <password>false</password>
      <prompt/>
    </field>
  </dataFields>
</descriptor>""")

    def testListType1(self):
        # RCE-858
        descrXml = """\
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
  <metadata>
    <displayName>Apache HTTPD Configuration Properties</displayName>
    <descriptions>
      <desc>Apache HTTPD Configuration for PORT and VirtualHost</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>vhosts</name>
      <descriptions>
        <desc>Virtual Hosts</desc>
      </descriptions>
      <type>listType</type>
      <listType>
        <descriptor>
          <metadata>
            <displayName>Virtual 2 Host Configuration</displayName>
            <rootElement>vhost</rootElement>
            <descriptions>
              <desc>Virtual Host Configuration</desc>
            </descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>nameVirtualHost</name>
              <descriptions>
                <desc>VirtualHost for website</desc>
              </descriptions>
              <type>str</type>
              <default>*</default>
              <required>false</required>
              <prompt>
                <desc>Virtual Host Name for Website</desc>
              </prompt>
            </field>
            <field>
              <name>port</name>
              <descriptions>
                <desc>Port for Virtual Host</desc>
              </descriptions>
              <type>str</type>
              <default>8080</default>
              <required>true</required>
              <prompt>
                <desc>Port for Virtual Host</desc>
              </prompt>
            </field>
            <field>
              <name>serverName</name>
              <descriptions>
                <desc>Server Name for Virtual Host</desc>
              </descriptions>
              <type>str</type>
              <default>vhost2.example.com</default>
              <required>true</required>
              <prompt>
                <desc>Server Name for Virtual Host</desc>
              </prompt>
            </field>
          </dataFields>
        </descriptor>
      </listType>
    </field>
  </dataFields>
</descriptor>"""

        dataXml = """\
<configuration href="https://dhcp155.eng.rpath.com/api/v1/inventory/systems/711/configuration" id="https://dhcp155.eng.rpath.com/api/v1/inventory/systems/711/configuration">
  <vhosts list="true">
    <vhost>
      <nameVirtualHost>*</nameVirtualHost>
      <port>8080</port>
      <serverName>vhost1.example.com</serverName>
    </vhost>
    <vhost>
      <nameVirtualHost>*</nameVirtualHost>
      <port>8080</port>
      <serverName>vhost2.example.com</serverName>
    </vhost>
  </vhosts>
</configuration>"""

        descr = descriptor.ConfigurationDescriptor(fromStream=descrXml)
        descr.setRootElement('configuration')
        ddata = descriptor.DescriptorData(fromStream=dataXml, descriptor=descr)

    def testListType2(self):
        # RCE-1194

        xml = """
<descriptor>
  <dataFields>
    <field>
      <default>complex_iprop-simple-default</default>
      <descriptions>
        <desc lang="en_US">complex_iprop-simple-description</desc>
      </descriptions>
      <name>complex_iprop-simple-name</name>
      <password>false</password>
      <prompt>
        <desc lang="en_US">complex_iprop-simple-prompte</desc>
      </prompt>
      <required>true</required>
      <type>str</type>
    </field>
    <field>
      <name>complex_iprop-compound</name>
      <descriptions>
        <desc lang="en_US">complex_iprop-compound-description</desc>
      </descriptions>
      <type>compoundType</type>
      <descriptor version="1.1" id="qatest/complex_iprop-compound">
        <metadata>
          <displayName>complex_iprop-compound-displayname</displayName>
          <descriptions><desc>complex_iprop-compound-descr</desc></descriptions>
        </metadata>
        <dataFields>
          <field>
            <name>complex_iprop-compound-field1</name>
            <descriptions><desc>complex_iprop-compound-field1-descr</desc></descriptions>
            <type>str</type>
            <default>complex_iprop-compound-field1-default</default>
            <required>true</required>
          </field>
          <field>
            <name>complex_iprop-compound-field2</name>
            <descriptions><desc>complex_iprop-compound-field2-descr</desc></descriptions>
            <type>str</type>
            <default>complex_iprop-compound-field2-default</default>
            <required>true</required>
          </field>
        </dataFields>
      </descriptor>
      <required>true</required>
    </field>
    <field>
      <name>complex_iprop-list</name>
      <descriptions>
        <desc lang="en_US">complex_iprop-list-descr</desc>
      </descriptions>
      <type>listType</type>
      <listType>
        <descriptor version="1.1" id="qatest/complex_iprop-list">
          <metadata>
            <displayName>complex_iprop-list-displayname</displayName>
            <rootElement>complex_iprop-listitem</rootElement>
            <descriptions><desc>complex_iprop-list-descr</desc></descriptions>
          </metadata>
          <dataFields>
            <field>
              <name>complex_iprop-list-item</name>
              <descriptions><desc>complex_iprop-list-item-descr</desc></descriptions>
              <type>str</type>
              <default>complex_iprop-list-item-descr</default>
              <required>true</required>
            </field>
          </dataFields>
        </descriptor>
      </listType>
      <required>true</required>
    </field>
  </dataFields>
</descriptor>"""

        descr = descriptor.ConfigurationDescriptor(fromStream=xml)
        descr.setRootElement('system_configuration')

        xml = """
        <system_configuration>
            <complex_iprop-compound>
                <complex_iprop-compound-field1>complex_iprop-compound-field1-default</complex_iprop-compound-field1>
                <complex_iprop-compound-field2>complex_iprop-compound-field2-default</complex_iprop-compound-field2>
            </complex_iprop-compound>
            <complex_iprop-list list="true">
                <complex_iprop-listitem>
                    <complex_iprop-list-item>complex_iprop-list-item-descr</complex_iprop-list-item>
                </complex_iprop-listitem>
            </complex_iprop-list>
            <complex_iprop-simple-name>complex_iprop-simple-default</complex_iprop-simple-name>
        </system_configuration>"""

        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=descr)
        ddata.toxml()

    def testCreateDescriptorData_conditional(self):
        # test createDescriptorData with a conditional descriptor
        xml = """\
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
  <metadata>
    <displayName>FooDescriptor</displayName>
    <rootElement>descriptor_data</rootElement>
    <descriptions>
      <desc>Description</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>imageId</name>
      <descriptions>
        <desc>Image ID</desc>
      </descriptions>
      <type>str</type>
      <default>7</default>
      <required>true</required>
      <hidden>true</hidden>
    </field>
    <field>
      <name>withConfiguration</name>
      <descriptions/>
      <type>bool</type>
      <default>False</default>
      <required>true</required>
    </field>
    <field>
      <name>system_configuration</name>
      <descriptions>
        <desc>System Configuration</desc>
      </descriptions>
      <type>compoundType</type>
      <descriptor version="1.1">
        <metadata>
          <displayName>System Configuration</displayName>
          <descriptions>
            <desc>System Configuration</desc>
          </descriptions>
        </metadata>
        <dataFields>
          <field>
            <name>user</name>
            <descriptions>
              <desc>User</desc>
            </descriptions>
            <type>str</type>
            <required>true</required>
          </field>
          <field>
            <name>group</name>
            <descriptions>
              <desc>Group</desc>
            </descriptions>
            <type>str</type>
            <required>true</required>
          </field>
        </dataFields>
      </descriptor>
      <required>true</required>
      <conditional>
        <fieldName>withConfiguration</fieldName>
        <operator>eq</operator>
        <value>true</value>
      </conditional>
    </field>
  </dataFields>
</descriptor>"""
        descr = descriptor.ConfigurationDescriptor(fromStream=xml)

        class CB(object):
            values = {
                None : {
                    'imageId' : '1',
                    'withConfiguration' : 'true',
                },
                'system_configuration' : {
                    'user' : 'apache',
                    'group' : 'nobody',
                }
            }
            def start(slf, descriptor, name=None):
                slf.name = name
            def end(slf, descriptor):
                pass
            def getValueForField(slf, field):
                return slf.values[slf.name][field.name]

        callback = CB()

        ddata = descr.createDescriptorData(callback)
        self.assertXMLEquals(ddata.toxml(), """
<descriptor_data version="1.1">
  <imageId>1</imageId>
  <withConfiguration>true</withConfiguration>
  <system_configuration>
    <user>apache</user>
    <group>nobody</group>
  </system_configuration>
</descriptor_data>
""")

        # No configuration
        callback.values[None]['withConfiguration'] = 'false'
        ddata = descr.createDescriptorData(callback)
        self.assertXMLEquals(ddata.toxml(), """
<descriptor_data version="1.1">
  <imageId>1</imageId>
  <withConfiguration>false</withConfiguration>
</descriptor_data>
""")

class DescriptorConstraintTest(BaseTest):
    def testIntType(self):
        # only a partial def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('foo', type = 'int',
            descriptions = [fDef.Description("foo")])

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = '45')
        self.failUnlessEqual(fData.getField('foo'), 45)

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = '-45')
        self.failUnlessEqual(fData.getField('foo'), -45)


        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 45)
        self.failUnlessEqual(fData.getField('foo'), 45)

        fData = descriptor.DescriptorData(descriptor = fDef)
        self.failUnlessRaises(errors.ConstraintsValidationError,
                              fData.addField, 'foo', value = '45t')

    def testBoolType(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('foo', type = 'bool',
            descriptions = [fDef.Description("foo")])

        fData = descriptor.DescriptorData(descriptor = fDef)
        self.assertRaises(errors.ConstraintsValidationError, fData.addField,
                'foo', value = '45')

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 'True')
        self.failUnlessEqual(fData.getField('foo'), True)

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 1)
        self.failUnlessEqual(fData.getField('foo'), True)

    def testStringType(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('foo', type = 'str',
            descriptions = [fDef.Description("foo")])

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 'True')

    def testCast(self):
        self.failUnlessEqual(dnodes._cast('a', 'str'), 'a')
        self.failUnlessEqual(dnodes._cast(u'a', 'str'), 'a')
        self.failUnlessEqual(dnodes._cast('', 'str'), '')
        self.failUnlessEqual(dnodes._cast(u'', 'str'), '')
        self.failUnlessRaises(errors.DataValidationError,
            dnodes._cast, '\300', 'str')

        self.failUnlessEqual(dnodes._cast('1', 'int'), 1)
        self.failUnlessEqual(dnodes._cast(u'-1', 'int'), -1)
        self.failUnlessRaises(errors.DataValidationError,
            dnodes._cast, u'1t', 'int')

        self.failUnlessEqual(dnodes._cast('1', 'bool'), True)
        self.failUnlessEqual(dnodes._cast(1, 'bool'), True)
        self.failUnlessEqual(dnodes._cast('tRuE', 'bool'), True)
        self.failUnlessEqual(dnodes._cast(0, 'bool'), False)
        self.failUnlessRaises(errors.DataValidationError,
                dnodes._cast, '', 'bool')
        self.failUnlessRaises(errors.DataValidationError,
                dnodes._cast, 'blah', 'bool')

        # Unknown type, should be preserved
        self.failUnlessEqual(dnodes._cast([1, 2, 3], 'XXX'), [1, 2, 3])

    def testEnumeratedType(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('lotsaValues',
            descriptions = [fDef.Description("foo")],
            multiple = True,
            type = fDef.EnumeratedType([
                fDef.ValueWithDescription('one',
                    descriptions = [fDef.Description("One")]),
                fDef.ValueWithDescription('two',
                    descriptions = [fDef.Description("Two")]),
            ]))

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('lotsaValues', value = ['one', 'two'])
        self.failUnlessEqual(fData.getField('lotsaValues'), ['one', 'two'])

        fData = descriptor.DescriptorData(descriptor = fDef)
        e = self.assertRaises(errors.ConstraintsValidationError, fData.addField,
                'lotsaValues', value = ['one', 'Two', 'Three'])
        self.failUnlessEqual(e.args[0],
            ["'foo': invalid value 'Two'", "'foo': invalid value 'Three'"])

        fData = descriptor.DescriptorData(descriptor = fDef)
        e = self.assertRaises(errors.DataValidationError, fData.addField,
                'lotsaValues', value = 'one')
        self.failUnlessEqual(str(e), "Expected multi-value")

    def testEnumeratedType2(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.setDisplayName("display name")
        fDef.setRootElement("newInstance")
        fDef.addDescription("text description")
        fDef.addDataField('enumNoDefault',
            descriptions = [ "foo" ],
            type = fDef.EnumeratedType([
                fDef.ValueWithDescription('one',
                    descriptions = [fDef.Description("One")]),
                fDef.ValueWithDescription('two',
                    descriptions = [fDef.Description("Two")]),
            ]))

        xml = "<newInstance><enumNoDefault/></newInstance>"
        fData = descriptor.DescriptorData(fromStream=xml, descriptor = fDef)
        self.failUnlessEqual(fData.getField("enunNoDefault"), None)

    def testEnumeratedType3(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        fDef.setDisplayName("display name")
        fDef.setRootElement("newInstance")
        fDef.addDescription("text description")
        fDef.addDataField('enumNoDefault',
            descriptions = [ "foo" ],
            required = True,
            type = fDef.EnumeratedType([
                fDef.ValueWithDescription('one',
                    descriptions = [fDef.Description("One")]),
                fDef.ValueWithDescription('two',
                    descriptions = [fDef.Description("Two")]),
            ]))

        xml = "<newInstance><enumNoDefault/></newInstance>"
        err = self.failUnlessRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData, fromStream=xml, descriptor = fDef)
        self.failUnlessEqual(err.args[0], ["'foo': a value is required"])

    def testConstraintsParsing(self):
        # only a partial factory def for the pieces we care about
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setId("Some-ID")
        dsc.setDisplayName('Cloud Information')
        dsc.addDescription('Configure Super Cloud')
        constraints = [
                    dict(constraintName = 'length', value = 10),
                    dict(constraintName = 'regexp', value = '^a'),
        ]
        dsc.addDataField('foo', type = 'str',
            descriptions = [dsc.Description("foo")],
            constraints = constraints
            )
        dsc.addDataField('bar', type = 'str',
            descriptions = ['bar', ('barre', 'fr')],
            )

        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), """
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" id="Some-ID" version="1.1">
    <metadata>
        <displayName>Cloud Information</displayName>
        <descriptions>
            <desc>Configure Super Cloud</desc>
        </descriptions>
    </metadata>
    <dataFields>
        <field>
            <name>foo</name>
            <descriptions>
                <desc>foo</desc>
            </descriptions>
            <type>str</type>
            <constraints>
                <regexp>^a</regexp>
                <length>10</length>
            </constraints>
        </field>
        <field>
            <name>bar</name>
            <descriptions>
                <desc>bar</desc>
                <desc lang="fr">barre</desc>
            </descriptions>
            <type>str</type>
        </field>
    </dataFields>
</descriptor>
""")
        sio.seek(0)
        dsc = descriptor.ConfigurationDescriptor(fromStream = sio)
        exp =  [
                [{'constraintName': 'regexp', 'value': '^a'},
                 {'constraintName': 'length', 'value': 10}],
                [],
            ]
        self.failUnlessEqual(dsc.getDataFields()[0].constraints.presentation(),
            exp[0])
        self.failUnlessEqual(dsc.getDataFields()[1].constraints,
            None)
        self.failUnlessEqual([ x.constraintsPresentation
                for x in dsc.getDataFields() ],
            exp)
        self.failUnlessEqual([ x.helpAsDict
                for x in dsc.getDataFields() ], [{}, {}])

    def testInvalidXML(self):
        data = "<data"
        e = self.failUnlessRaises(descriptor.errors.InvalidXML,
            descriptor.ConfigurationDescriptor, fromStream = data)

    def testConstraints(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        constraints = [
                    dict(constraintName = 'length', value = 10),
                    dict(constraintName = 'regexp', value = '^a'),
        ]
        fDef.addDataField('foo', type = 'str',
            descriptions = [fDef.Description("foo")],
            constraints = constraints
            )

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 'abcdefghij')

        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            fData.addField, 'foo', value = 'bbcdefghijk')
        self.failUnlessEqual(e.args[0],
            ["'foo': 'bbcdefghijk' fails regexp check '^a'",
             "'foo': 'bbcdefghijk' fails length check '10'"])

        # Test missing fields, additional fields, failing fields
        fDef = descriptor.ConfigurationDescriptor()
        fDef.addDataField('foo', type = 'str',
            descriptions = [fDef.Description("foo")],
            constraints = constraints,
            )
        fDef.addDataField('bar', type = 'str',
            descriptions = [fDef.Description("bar")],
            constraints = constraints,
            required = True
            )
        fDef.addDataField('baz', type = 'str',
            descriptions = [fDef.Description("baz")],
            constraints = constraints,
            required = True
            )

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('foo', value = 'abcdefghij')

        # Now remove the field definition
        fDef._rootObj.dataFields.field = [
            x for x in fDef._rootObj.dataFields.field
                if x.name != 'foo' ]

        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            fData.addField, 'baz', value = 'bcdefghijkl')

        self.failUnlessEqual(e.args[0],
            ["'baz': 'bcdefghijkl' fails regexp check '^a'",
             "'baz': 'bcdefghijkl' fails length check '10'",
            ])

        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            fData.checkConstraints)
        self.failUnlessEqual(e.args[0],
            ["Missing field: 'bar'", "Missing field: 'baz'"])

    def testValidateSingleValue(self):
        # No constraints
        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('t', 'int', 'intfield',
            [])
        self.failUnlessEqual(errList,
            ["'intfield': invalid value 't' for type 'int'"])

        # Legal values constraints
        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [dict(constraintName = 'legalValues', values = ['1', 2])])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('3', 'int', 'intfield',
            [dict(constraintName = 'legalValues', values = ['1', 2])])
        self.failUnlessEqual(errList,
            ["'intfield': '3' is not a legal value"])

        errList = dnodes._validateSingleValue('1', 'bool', 'boolfield',
            [dict(constraintName = 'legalValues', values = [True])])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('blah', 'bool', 'boolfield',
            [dict(constraintName = 'legalValues', values = [True])])
        self.failUnlessEqual(errList,
            ["'boolfield': invalid value 'blah' for type 'bool'"])

        # Length constraints
        # They don't apply to ints
        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [dict(constraintName = 'length', value = '12345')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('1', 'str', 'strfield',
            [dict(constraintName = 'length', value = '5')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('123456', 'str', 'strfield',
            [dict(constraintName = 'length', value = '5')])
        self.failUnlessEqual(errList,
            ["'strfield': '123456' fails length check '5'"])

        # Range checks
        # They don't apply to str
        errList = dnodes._validateSingleValue('1', 'str', 'strfield',
            [dict(constraintName = 'range', min = '5')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [dict(constraintName = 'range', min = '1')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [dict(constraintName = 'range', min = '1'),
             dict(constraintName = 'range', min = '2'),
             dict(constraintName = 'range', max = '1'),
             dict(constraintName = 'range', min = '3', max = '-1'),
             dict(constraintName = 'range', max = '-2'),
            ])
        self.failUnlessEqual(errList,
            ["'intfield': '1' fails minimum range check '2'",
             "'intfield': '1' fails minimum range check '3'",
             "'intfield': '1' fails maximum range check '-1'",
             "'intfield': '1' fails maximum range check '-2'",
            ])

        # Regex constraints
        # They don't apply to ints
        errList = dnodes._validateSingleValue('1', 'int', 'intfield',
            [dict(constraintName = 'regexp', value = '^abc')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('1', 'str', 'strfield',
            [dict(constraintName = 'regexp', value = '^1')])
        self.failUnlessEqual(errList, [])

        errList = dnodes._validateSingleValue('2', 'str', 'strfield',
            [dict(constraintName = 'regexp', value = '^1')])
        self.failUnlessEqual(errList,
            ["'strfield': '2' fails regexp check '^1'"])

        # Ensure there is a stable order in which errors are reported
        errList = dnodes._validateSingleValue('2345', 'str', 'strfield',
            [dict(constraintName = 'regexp', value = '^1'),
             dict(constraintName = 'length', value = '3'),
             dict(constraintName = 'legalValues', values = [ '3' ]),
             ])
        self.failUnlessEqual(errList,
            ["'strfield': '2345' fails regexp check '^1'",
             "'strfield': '2345' fails length check '3'",
             "'strfield': '2345' is not a legal value"])

    def testParseDescriptorDataNoMulti(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptor1)
        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData,
            fromStream = xmlDescriptorDataNoMulti1,
            descriptor = dsc)
        self.failUnlessEqual(e.args[0], ["Missing field: 'multiField'"])

    def testEnumeratedBadDefault(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        e = self.failUnlessRaises(errors.InvalidDefaultValue,
          dsc.addDataField, "multi-field",
            required = True,
            multiple = True,
            type = dsc.EnumeratedType(
                dsc.ValueWithDescription(str(x),
                    descriptions = "Description for %s") for x in range(3)),
            default = "aaa")
        self.failUnlessEqual(str(e), "aaa")

    def testEnumeratedMultiDefault(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("multi-field",
            required = True,
            multiple = True,
            type = dsc.EnumeratedType(
                dsc.ValueWithDescription(str(x),
                    descriptions = "Description for %s" % x) for x in range(3)),
            default = ["0", "1"])
        sio = StringIO()
        dsc.serialize(sio)
        sio.seek(0)

        dsc = descriptor.ConfigurationDescriptor(fromStream = sio)
        field = dsc.getDataField('multi-field')
        self.failUnlessEqual(field.getDefault(), ["0", "1"])

    def testSimpleDefault(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("fieldName",
            type = "int", default = 1)

        sio = StringIO()
        dsc.serialize(sio)
        sio.seek(0)

        field = dsc.getDataField('fieldName')
        self.failUnlessEqual(field.getDefault(), 1)

    def testMultiDefault(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("fieldName",
            type = "int", default = 1, multiple = True)

        sio = StringIO()
        dsc.serialize(sio)
        sio.seek(0)

        field = dsc.getDataField('fieldName')
        self.failUnlessEqual(field.getDefault(), [1])

    def testConditional1(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream = xmlDescriptorConditional1)

        dsc.setRootElement("newInstance")
        data = descriptor.DescriptorData(
            fromStream = xmlDescriptorDataConditional1, descriptor = dsc)

    def testConditional2(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.setRootElement("newInstance")
        dsc.addDataField("switchField",
            descriptions = "Conditionals will use this field as a switch",
            type = [
                dsc.ValueWithDescription("val-%s" % x,
                                     descriptions = "Description for %s" % x)
                 for x in range(2) ], default = "val-1", required = True)
        for i in range(2):
            dsc.addDataField("cond-%s" % i,
                type = [
                    dsc.ValueWithDescription("val-%s-%s" % (i, x),
                             descriptions = "Description for %s-%s" % (i, x))
                     for x in range(3) ],
                 default = "val-%s-2" % i, required = True,
                 conditional = dsc.Conditional("switchField", "val-%s" % i))
        sio = StringIO()
        dsc.serialize(sio)
        self.assertXMLEquals(sio.getvalue(), xmlDescriptorConditional2)

        data = descriptor.DescriptorData(
            fromStream = xmlDescriptorDataConditional21, descriptor = dsc)
        # Hmm, arguably this should also explode since we had additional data
        data = descriptor.DescriptorData(
            fromStream = xmlDescriptorDataConditional22, descriptor = dsc)
        err = self.failUnlessRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData,
            fromStream = xmlDescriptorDataConditional23, descriptor = dsc)
        self.failUnlessEqual(err.args[0], ["Missing field: 'cond-0'"])

    def testConditional3(self):
        dsc = descriptor.ConfigurationDescriptor(fromStream=xmlDescriptorConditional3)
        dsc.setRootElement('newInstance')
        descriptor.DescriptorData(fromStream=xmlDescriptorDataConditional3,
            descriptor=dsc)

    def testDuplicateDescriptions(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.addDescription("Test 1")
        dsc.addDescription("Test 2")
        dlist = dsc._rootObj.get_metadata().get_descriptions().get_desc()
        self.failUnlessEqual(
            [(x.get_lang(), x.getValueOf_()) for x in dlist],
            [(None, 'Test 2')])

    def testReadonly(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        self.failUnlessRaises(errors.MissingDefaultValue,
            dsc.addDataField, "readonly-field", type='str', readonly=True)

        dsc.addDataField("readonly-field", type='str', default="mydefault",
            descriptions="read-only field", readonly=True)
        data = descriptor.DescriptorData(descriptor=dsc, fromStream="""\
<descriptorData>
    <readonly-field>mydefault</readonly-field>
</descriptorData>
""")
        self.failUnlessEqual(data.getField('readonly-field'),
            "mydefault")

        # At least for now, empty values are ok
        data = descriptor.DescriptorData(descriptor=dsc, fromStream="""\
<descriptorData/>
""")
        self.failUnlessEqual(data.getField('readonly-field'),
            None) # XXX should be "mydefault"
        data = descriptor.DescriptorData(descriptor=dsc, fromStream="""\
<descriptorData>
    <readonly-field></readonly-field>
</descriptorData>
""")
        self.failUnlessEqual(data.getField('readonly-field'),
            None) # XXX should be "mydefault"

        # This should fail, the read-only value was changed
        e = self.failUnlessRaises(errors.ConstraintsValidationError,
            descriptor.DescriptorData, descriptor=dsc, fromStream="""\
<descriptorData>
    <readonly-field>not the default</readonly-field>
</descriptorData>
""")
        self.failUnlessEqual(e.args[0],
            ["'read-only field': invalid value 'not the default' for read-only field; expected 'mydefault'"])

        # Read-only field with no default
        dsc.addDataField("readonly-field", type='str', default="",
            descriptions="read-only field", readonly=True)
        data = descriptor.DescriptorData(descriptor=dsc, fromStream="""\
<descriptorData>
    <readonly-field>mydefault</readonly-field>
</descriptorData>
""")
        self.failUnlessEqual(data.getField('readonly-field'),
            "mydefault")

    def testRange(self):
        # only a partial factory def for the pieces we care about
        fDef = descriptor.ConfigurationDescriptor()
        constraints = [
                    dict(constraintName = 'range', min=0, max=65535),
        ]

        fDef.addDataField('port', type = 'int',
            descriptions = [fDef.Description("port")],
            constraints = constraints,
            default = 8080,
            )

        fData = descriptor.DescriptorData(descriptor = fDef)
        fData.addField('port', value = 0)

        sio = StringIO()
        fData.serialize(sio)
        sio.seek(0)

        fData = descriptor.DescriptorData(fromStream=sio, descriptor=fDef)
        self.assertEqual(fData.getField('port'), 0)

    def testRangeOnDescriptor(self):
        # Mingle #2117: minValue of 0 should not fail with:
        # '0' is not a # valid value of the atomic type 'xs:positiveInteger'
        fDef = descriptor.ConfigurationDescriptor()
        fDef.setDisplayName('test')
        fDef.setRootElement('descriptor_data')
        fDef.addDescription('Range test')
        constraints = [
                    dict(constraintName = 'range', min=-123456, max=123456),
        ]

        fDef.addDataField('port', type = 'int',
            descriptions = [fDef.Description("port")],
            constraints = constraints,
            default = 8080,
            )

        sio = StringIO()
        fDef.serialize(sio)

    def testRequiredDefault(self):
        # Make sure that one can skip a required data field if it has a
        # default value
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setRootElement("data")
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("reqFieldWithDefault",
            type = "int", default = 42, required=True)
        dsc.addDataField("reqField",
            type = "int", required=True)
        dsc.addDataField('multiField', type = 'str', multiple = True,
            required = True,
            descriptions = [ dsc.Description('Multi Field') ],
            constraints = [
                dict(constraintName = 'legalValues',
                     values = ['Foo', 'Bar', 'Baz']),
            ],
            default = [ 'Baz', 'Foo'], )


        xml = """<data><reqField>10</reqField></data>"""
        ddata = descriptor.DescriptorData(fromStream=xml, descriptor=dsc)
        self.assertEquals(ddata.getField('reqFieldWithDefault'), 42)
        self.assertEquals(ddata.getField('multiField'), ['Baz', 'Foo'])

    def testXmlField(self):
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setRootElement("data")
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("blooper", descriptions="Blooper")

        ddata = descriptor.DescriptorData(descriptor=dsc)
        xml = '<xml attr="1"><a>1</a></xml>'
        ddata.addField('blooper', xml)
        sio = StringIO()
        ddata.serialize(sio)
        sio.seek(0)

        ddata = descriptor.DescriptorData(descriptor=dsc, fromStream=sio)
        self.assertEquals(ddata.getField('blooper'), xml)

        # Test with default data
        dsc = descriptor.ConfigurationDescriptor()
        dsc.setRootElement("data")
        dsc.setDisplayName('test')
        dsc.addDescription("Test")
        dsc.addDataField("blooper", descriptions="Blooper", required=True)

        field = dsc.getDataField("blooper")
        field.set_default([xml])

        # Default values do not show up automatically
        ddata = descriptor.DescriptorData(descriptor=dsc)
        self.assertEquals(ddata.getField('blooper'), None)

xmlDescriptor1 = """<?xml version="1.0" encoding="UTF-8"?>
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" id="Some-ID" version="1.1">
  <metadata>
    <displayName>Cloud Information</displayName>
    <descriptions>
      <desc>Configure Super Cloud</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>cloudType</name>
      <descriptions>
        <desc>Cloud Type</desc>
      </descriptions>
      <help href="http://url1/en"/>
      <help lang="en_LOL" href="http://url1/lol"/>
      <type>str</type>
    </field>
    <field>
      <name>multiField</name>
      <descriptions>
        <desc>Multi Field</desc>
      </descriptions>
      <type>str</type>
      <multiple>true</multiple>
      <constraints>
        <legalValues>
          <item>Foo</item>
          <item>Bar</item>
          <item>Baz</item>
        </legalValues>
      </constraints>
      <required>true</required>
    </field>
  </dataFields>
</descriptor>"""

xmlDescriptorData1 = """<?xml version='1.0' encoding='UTF-8'?>
<descriptorData id="Some-ID" version="1.1">
  <cloudType>ec2</cloudType>
  <multiField>
    <item>Foo</item>
    <item>Baz</item>
  </multiField>
</descriptorData>
"""

xmlDescriptor2 = """<?xml version="1.0" encoding="UTF-8"?>
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" id="Some-ID" version="1.1">
  <metadata>
    <displayName>Cloud Information</displayName>
    <descriptions>
      <desc>Configure Super Cloud</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>cloudType</name>
      <descriptions>
        <desc>Cloud Type</desc>
      </descriptions>
      <type>str</type>
    </field>
    <field>
      <name>multiField</name>
      <descriptions>
        <desc>Multi Field</desc>
      </descriptions>
      <type>enumeratedType</type>
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>Small value</desc>
          </descriptions>
          <key>small</key>
        </describedValue>
        <describedValue>
          <descriptions>
            <desc>Medium value</desc>
          </descriptions>
          <key>medium</key>
        </describedValue>
      </enumeratedType>
      <multiple>true</multiple>
      <required>true</required>
    </field>
  </dataFields>
</descriptor>"""

newDescriptorField = """\
    <field>
      <name>lotsaValues</name>
      <descriptions>
        <desc>foo</desc>
      </descriptions>
      <type>enumeratedType</type>
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>One</desc>
          </descriptions>
          <key>one</key>
        </describedValue>
        <describedValue>
          <descriptions>
            <desc>Two</desc>
          </descriptions>
          <key>two</key>
        </describedValue>
      </enumeratedType>
    </field>"""

xmlDescriptor3 = """<?xml version="1.0" encoding="UTF-8"?>
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" id="Some-ID" version="1.1">
  <metadata>
    <displayName>Cloud Information</displayName>
    <rootElement>blahBlah</rootElement>
    <descriptions>
      <desc>Configure Super Cloud</desc>
    </descriptions>
  </metadata>
  <dataFields>
%s
  </dataFields>
</descriptor>"""

passwordFields3 = """\
    <field>
      <name>passwordFieldStr</name>
      <descriptions>
        <desc>Password String</desc>
      </descriptions>
      <type>str</type>
      <required>true</required>
      <password>true</password>
    </field>
    <field>
      <name>passwordFieldInt</name>
      <descriptions>
        <desc>Password Integer</desc>
      </descriptions>
      <type>int</type>
      <required>true</required>
      <password>true</password>
    </field>"""

hiddenFields3 = """\
    <field>
      <name>hiddenFieldStr</name>
      <descriptions>
        <desc>Hidden String</desc>
      </descriptions>
      <type>str</type>
      <required>true</required>
      <hidden>true</hidden>
    </field>
    <field>
      <name>hiddenFieldInt</name>
      <descriptions>
        <desc>Hidden Integer</desc>
      </descriptions>
      <type>int</type>
      <required>false</required>
      <hidden>true</hidden>
    </field>"""

xmlDescriptorData3 = """<?xml version='1.0' encoding='UTF-8'?>
<%s id="Some-ID" version="1.1">
%s
</%s>"""

passwordFields3Data = """\
  <passwordFieldStr>Real string</passwordFieldStr>
  <passwordFieldInt>42</passwordFieldInt>"""

hiddenFields3Data = """\
  <hiddenFieldStr>abc</hiddenFieldStr>
  <hiddenFieldInt>1</hiddenFieldInt>"""

xmlDescriptorDataNoMulti1 = """<?xml version='1.0' encoding='UTF-8'?>
<descriptorData id="Some-ID" version="1.1">
  <cloudType>ec2</cloudType>
  <multiField>bloop</multiField>
</descriptorData>
"""

xmlDescriptorConditional1 = """<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
  <metadata>
    <displayName>VMware Launch Parameters</displayName>
    <descriptions>
      <desc>VMware Launch Parameters</desc>
    </descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>dataCenter</name>
      <descriptions>
        <desc>Data Center</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/dataCenter.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>Performance ESX</desc>
          </descriptions>
          <key>datacenter-2</key>
        </describedValue>
      </enumeratedType>
      <default>datacenter-2</default>
      <required>true</required>
    </field>
    <field>
      <name>cr-datacenter-2</name>
      <descriptions>
        <desc>Compute Resource</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/computeResource.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>pershing.aus.lab.vignette.com</desc>
          </descriptions>
          <key>domain-s5</key>
        </describedValue>
        <describedValue>
          <descriptions>
            <desc>paveway.aus.lab.vignette.com</desc>
          </descriptions>
          <key>domain-s47</key>
        </describedValue>
      </enumeratedType>
      <default>domain-s5</default>
      <required>true</required>
      <conditional>
        <fieldName>dataCenter</fieldName>
        <operator>eq</operator>
        <value>datacenter-2</value>
      </conditional>
    </field>
    <field>
      <name>dataStore-domain-s5</name>
      <descriptions>
        <desc>Data Store</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/dataStore.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>pershing:storage1 - 439 GiB free</desc>
          </descriptions>
          <key>datastore-11</key>
        </describedValue>
      </enumeratedType>
      <default>datastore-11</default>
      <required>true</required>
      <conditional>
        <fieldName>cr-datacenter-2</fieldName>
        <operator>eq</operator>
        <value>domain-s5</value>
      </conditional>
    </field>
    <field>
      <name>dataStore-domain-s47</name>
      <descriptions>
        <desc>Data Store</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/dataStore.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>paveway:storage1 - 355 GiB free</desc>
          </descriptions>
          <key>datastore-53</key>
        </describedValue>
      </enumeratedType>
      <default>datastore-53</default>
      <required>true</required>
      <conditional>
        <fieldName>cr-datacenter-2</fieldName>
        <operator>eq</operator>
        <value>domain-s47</value>
      </conditional>
    </field>
    <field>
      <name>resourcePool-domain-s5</name>
      <descriptions>
        <desc>Resource Pool</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/resourcePool.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>Resources</desc>
          </descriptions>
          <key>resgroup-7</key>
        </describedValue>
      </enumeratedType>
      <default>resgroup-7</default>
      <required>true</required>
      <conditional>
        <fieldName>cr-datacenter-2</fieldName>
        <operator>eq</operator>
        <value>domain-s5</value>
      </conditional>
    </field>
    <field>
      <name>resourcePool-domain-s47</name>
      <descriptions>
        <desc>Resource Pool</desc>
      </descriptions>
      <help href="https://rbuilder.aus.lab.vignette.com/catalog/clouds/vmware/help/launch/resourcePool.html" />
      <enumeratedType>
        <describedValue>
          <descriptions>
            <desc>Resources</desc>
          </descriptions>
          <key>resgroup-49</key>
        </describedValue>
      </enumeratedType>
      <default>resgroup-49</default>
      <required>true</required>
      <conditional>
        <fieldName>cr-datacenter-2</fieldName>
        <operator>eq</operator>
        <value>domain-s47</value>
      </conditional>
    </field>
  </dataFields>
</descriptor>"""

xmlDescriptorDataConditional1 = """\
<newInstance>
  <cr-datacenter-2>domain-s5</cr-datacenter-2>
  <dataCenter>datacenter-2</dataCenter>
  <dataStore-domain-s5>datastore-11</dataStore-domain-s5>
  <resourcePool-domain-s5>resgroup-7</resourcePool-domain-s5>
</newInstance>
"""

xmlDescriptorConditional2 = """\
<descriptor xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd" version="1.1">
  <metadata>
    <displayName>test</displayName>
    <rootElement>newInstance</rootElement>
    <descriptions><desc>Test</desc></descriptions>
  </metadata>
  <dataFields>
    <field>
      <name>switchField</name>
      <descriptions><desc>Conditionals will use this field as a switch</desc></descriptions>
      <type>enumeratedType</type>
      <enumeratedType>
        <describedValue>
          <descriptions><desc>Description for 0</desc></descriptions>
          <key>val-0</key>
        </describedValue>
        <describedValue>
          <descriptions><desc>Description for 1</desc></descriptions>
          <key>val-1</key>
        </describedValue>
      </enumeratedType>
      <default>val-1</default>
      <required>true</required>
    </field>
    <field>
      <name>cond-0</name>
      <descriptions/>
      <type>enumeratedType</type>
      <enumeratedType>
        <describedValue>
          <descriptions><desc>Description for 0-0</desc></descriptions>
          <key>val-0-0</key>
        </describedValue>
        <describedValue>
          <descriptions><desc>Description for 0-1</desc></descriptions>
          <key>val-0-1</key>
        </describedValue>
        <describedValue>
          <descriptions><desc>Description for 0-2</desc></descriptions>
          <key>val-0-2</key>
        </describedValue>
      </enumeratedType>
      <default>val-0-2</default>
      <required>true</required>
      <conditional>
        <fieldName>switchField</fieldName>
        <operator>eq</operator>
        <value>val-0</value>
      </conditional>
    </field>
    <field>
      <name>cond-1</name>
      <descriptions/>
      <type>enumeratedType</type>
      <enumeratedType>
        <describedValue>
          <descriptions><desc>Description for 1-0</desc></descriptions>
          <key>val-1-0</key>
        </describedValue>
        <describedValue>
          <descriptions><desc>Description for 1-1</desc></descriptions>
          <key>val-1-1</key>
        </describedValue>
        <describedValue>
          <descriptions><desc>Description for 1-2</desc></descriptions>
          <key>val-1-2</key>
        </describedValue>
      </enumeratedType>
      <default>val-1-2</default>
      <required>true</required>
      <conditional>
        <fieldName>switchField</fieldName>
        <operator>eq</operator>
        <value>val-1</value>
      </conditional>
    </field>
  </dataFields>
</descriptor>
"""

xmlDescriptorDataConditional21 = """\
<newInstance>
  <switchField>val-0</switchField>
  <cond-0>val-0-0</cond-0>
</newInstance>
"""

xmlDescriptorDataConditional22= """\
<newInstance>
  <switchField>val-0</switchField>
  <cond-0>val-0-0</cond-0>
  <cond-1>val-1-0</cond-1>
</newInstance>
"""

xmlDescriptorDataConditional23= """\
<newInstance>
  <switchField>val-0</switchField>
  <cond-1>val-1-0</cond-1>
</newInstance>
"""

xmlDescriptorConditional3 = """\
<?xml version='1.0' encoding='UTF-8'?>
<descriptor xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.rpath.com/permanent/descriptor-1.1.xsd" xsi:schemaLocation="http://www.rpath.com/permanent/descriptor-1.1.xsd descriptor-1.1.xsd">
    <metadata>
        <displayName>VMware Launch Parameters</displayName>
        <descriptions>
            <desc>VMware Launch Parameters</desc>
        </descriptions>
    </metadata>
    <dataFields>
        <field>
            <name>imageId</name>
            <descriptions>
                <desc>Image ID</desc>
            </descriptions>
            <type>str</type>
            <constraints>
                <range>
                    <min>1</min>
                    <max>32</max>
                </range>
            </constraints>
            <required>true</required>
            <hidden>true</hidden>
        </field>
        <field>
            <name>instanceName</name>
            <descriptions>
                <desc>Instance Name</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/instanceName.html"/>
            <type>str</type>
            <constraints>
                <length>32</length>
            </constraints>
            <required>true</required>
        </field>
        <field>
            <name>instanceDescription</name>
            <descriptions>
                <desc>Instance Description</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/instanceDescription.html"/>
            <type>str</type>
            <constraints>
                <length>128</length>
            </constraints>
        </field>
        <field>
            <name>dataCenter</name>
            <descriptions>
                <desc>Data Center</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/dataCenter.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>DR-Non-prod-DC2</desc>
                    </descriptions>
                    <key>datacenter-689</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>LISP-Metro-DC</desc>
                    </descriptions>
                    <key>datacenter-2</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>DC-network-designs</desc>
                    </descriptions>
                    <key>datacenter-654</key>
                </describedValue>
            </enumeratedType>
            <default>datacenter-689</default>
            <required>true</required>
        </field>
        <field>
            <name>cr-datacenter-689</name>
            <descriptions>
                <desc>Compute Resource</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/computeResource.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>SVL-DR1</desc>
                    </descriptions>
                    <key>domain-c694</key>
                </describedValue>
            </enumeratedType>
            <default>domain-c694</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-689</value>
            </conditional>
        </field>
        <field>
            <name>cr-datacenter-2</name>
            <descriptions>
                <desc>Compute Resource</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/computeResource.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>LISP-Pod-DC1</desc>
                    </descriptions>
                    <key>domain-c341</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>LISP-Pod-DC2</desc>
                    </descriptions>
                    <key>domain-c343</key>
                </describedValue>
            </enumeratedType>
            <default>domain-c341</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-2</value>
            </conditional>
        </field>
        <field>
            <name>cr-datacenter-654</name>
            <descriptions>
                <desc>Compute Resource</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/computeResource.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>ntlab-server2.cisco.com</desc>
                    </descriptions>
                    <key>domain-s675</key>
                </describedValue>
            </enumeratedType>
            <default>domain-s675</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-654</value>
            </conditional>
        </field>
        <field>
            <name>network-datacenter-689</name>
            <descriptions>
                <desc>Network</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/network.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>N1KV-Control_vl90</desc>
                    </descriptions>
                    <key>network-711</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>N1KV-MGMT_vl91</desc>
                    </descriptions>
                    <key>network-712</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>N1KV-Packet_vl92</desc>
                    </descriptions>
                    <key>network-713</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VM Network</desc>
                    </descriptions>
                    <key>network-698</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Unused_Or_Quarantine_Veth</desc>
                    </descriptions>
                    <key>dvportgroup-727</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>vmw-mgmt-v93</desc>
                    </descriptions>
                    <key>dvportgroup-728</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>dr1_dmz_webserver_vl400</desc>
                    </descriptions>
                    <key>dvportgroup-731</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>vmk-vmkernel-v94</desc>
                    </descriptions>
                    <key>dvportgroup-734</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>n1k-ctrl-v90</desc>
                    </descriptions>
                    <key>dvportgroup-735</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>n1k-mgmt-v91</desc>
                    </descriptions>
                    <key>dvportgroup-736</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>n1k-pkt-v92</desc>
                    </descriptions>
                    <key>dvportgroup-737</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>dr1_VMK_NFS_vl40</desc>
                    </descriptions>
                    <key>dvportgroup-743</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Gen-Client1-vl110</desc>
                    </descriptions>
                    <key>dvportgroup-744</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>svldr1_webserver_vl250</desc>
                    </descriptions>
                    <key>dvportgroup-750</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>svl-dr1-webserver-nonprod-vl200</desc>
                    </descriptions>
                    <key>dvportgroup-784</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>dr1_dmz_webserver_client_vl449</desc>
                    </descriptions>
                    <key>dvportgroup-788</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>svldr1_webserver_client_vl299</desc>
                    </descriptions>
                    <key>dvportgroup-789</key>
                </describedValue>
            </enumeratedType>
            <default>network-711</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-689</value>
            </conditional>
        </field>
        <field>
            <name>network-datacenter-2</name>
            <descriptions>
                <desc>Network</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/network.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>LISP-Client1-v70</desc>
                    </descriptions>
                    <key>network-500</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Unused_Or_Quarantine_Veth</desc>
                    </descriptions>
                    <key>dvportgroup-456</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-MGMT-DC2-v22</desc>
                    </descriptions>
                    <key>dvportgroup-480</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-VMotion-DC2-v23</desc>
                    </descriptions>
                    <key>dvportgroup-481</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-NFS-DC2-v34</desc>
                    </descriptions>
                    <key>dvportgroup-482</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-MGMT-DC1-v93</desc>
                    </descriptions>
                    <key>dvportgroup-483</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-VMotion-DC1-v94</desc>
                    </descriptions>
                    <key>dvportgroup-484</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VMW-NFS-DC1-v12</desc>
                    </descriptions>
                    <key>dvportgroup-485</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>LISP-Client1-v70</desc>
                    </descriptions>
                    <key>dvportgroup-569</key>
                </describedValue>
            </enumeratedType>
            <default>network-500</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-2</value>
            </conditional>
        </field>
        <field>
            <name>network-datacenter-654</name>
            <descriptions>
                <desc>Network</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/network.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>Test-VMs-V100</desc>
                    </descriptions>
                    <key>network-688</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>VM Network</desc>
                    </descriptions>
                    <key>network-680</key>
                </describedValue>
            </enumeratedType>
            <default>network-688</default>
            <required>true</required>
            <conditional>
                <fieldName>dataCenter</fieldName>
                <operator>eq</operator>
                <value>datacenter-654</value>
            </conditional>
        </field>
        <field>
            <name>dataStore-domain-c694</name>
            <descriptions>
                <desc>Data Store</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/dataStore.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>NFS-DATA-01 - 0  bytes free</desc>
                    </descriptions>
                    <key>datastore-741</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>DS_NETWORK_ACE (2) - 212  GiB free</desc>
                    </descriptions>
                    <key>datastore-841</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>datastore1 (2) - 272  GiB free</desc>
                    </descriptions>
                    <key>datastore-703</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>DS_NETWORK_ACE - 0  bytes free</desc>
                    </descriptions>
                    <key>datastore-706</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>DS_NETWORK_ACE (1) - 212  GiB free</desc>
                    </descriptions>
                    <key>datastore-830</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>NFS-DATA-01 (1) - 231  GiB free</desc>
                    </descriptions>
                    <key>datastore-829</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>datastore1 - 272  GiB free</desc>
                    </descriptions>
                    <key>datastore-705</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>datastore1 (1) - 272  GiB free</desc>
                    </descriptions>
                    <key>datastore-758</key>
                </describedValue>
            </enumeratedType>
            <default>datastore-741</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-689</fieldName>
                <operator>eq</operator>
                <value>domain-c694</value>
            </conditional>
        </field>
        <field>
            <name>dataStore-domain-c341</name>
            <descriptions>
                <desc>Data Store</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/dataStore.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>NFS-SNAP-SRC-02 - 162  GiB free</desc>
                    </descriptions>
                    <key>datastore-645</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>NFS-FLEX-01 - 250  GiB free</desc>
                    </descriptions>
                    <key>datastore-563</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>NFS-FLEX-02 - 289  GiB free</desc>
                    </descriptions>
                    <key>datastore-588</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Local - 122  GiB free</desc>
                    </descriptions>
                    <key>datastore-488</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>SAN-VPLEX-00 - 259  GiB free</desc>
                    </descriptions>
                    <key>datastore-605</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>SAN-VPLEX-01 - 259  GiB free</desc>
                    </descriptions>
                    <key>datastore-606</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>SAN-VPLEX-02 - 271  GiB free</desc>
                    </descriptions>
                    <key>datastore-607</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>SAN-VPLEX-03 - 271  GiB free</desc>
                    </descriptions>
                    <key>datastore-608</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>snap-7d4d6769-SAN-SRDF-01 - 260  GiB free</desc>
                    </descriptions>
                    <key>datastore-637</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>snap-12965a56-SAN-SRDF-02 - 260  GiB free</desc>
                    </descriptions>
                    <key>datastore-646</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Storage2 (1) - 122  GiB free</desc>
                    </descriptions>
                    <key>datastore-585</key>
                </describedValue>
            </enumeratedType>
            <default>datastore-645</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-2</fieldName>
                <operator>eq</operator>
                <value>domain-c341</value>
            </conditional>
        </field>
        <field>
            <name>dataStore-domain-s675</name>
            <descriptions>
                <desc>Data Store</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/dataStore.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>datastore1 - 63  GiB free</desc>
                    </descriptions>
                    <key>datastore-678</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>datastore2 - 11  GiB free</desc>
                    </descriptions>
                    <key>datastore-679</key>
                </describedValue>
            </enumeratedType>
            <default>datastore-678</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-654</fieldName>
                <operator>eq</operator>
                <value>domain-s675</value>
            </conditional>
        </field>
        <field>
            <name>resourcePool-domain-c694</name>
            <descriptions>
                <desc>Resource Pool</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/resourcePool.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>non-prod</desc>
                    </descriptions>
                    <key>resgroup-794</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Resources</desc>
                    </descriptions>
                    <key>resgroup-695</key>
                </describedValue>
                <describedValue>
                    <descriptions>
                        <desc>Prod</desc>
                    </descriptions>
                    <key>resgroup-793</key>
                </describedValue>
            </enumeratedType>
            <default>resgroup-793</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-689</fieldName>
                <operator>eq</operator>
                <value>domain-c694</value>
            </conditional>
        </field>
        <field>
            <name>resourcePool-domain-c341</name>
            <descriptions>
                <desc>Resource Pool</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/resourcePool.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>Resources</desc>
                    </descriptions>
                    <key>resgroup-342</key>
                </describedValue>
            </enumeratedType>
            <default>resgroup-342</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-2</fieldName>
                <operator>eq</operator>
                <value>domain-c341</value>
            </conditional>
        </field>
        <field>
            <name>resourcePool-domain-c343</name>
            <descriptions>
                <desc>Resource Pool</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/resourcePool.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>Resources</desc>
                    </descriptions>
                    <key>resgroup-344</key>
                </describedValue>
            </enumeratedType>
            <default>resgroup-344</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-2</fieldName>
                <operator>eq</operator>
                <value>domain-c343</value>
            </conditional>
        </field>
        <field>
            <name>resourcePool-domain-s675</name>
            <descriptions>
                <desc>Resource Pool</desc>
            </descriptions>
            <help href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/help/launch/resourcePool.html"/>
            <enumeratedType>
                <describedValue>
                    <descriptions>
                        <desc>Resources</desc>
                    </descriptions>
                    <key>resgroup-676</key>
                </describedValue>
            </enumeratedType>
            <default>resgroup-676</default>
            <required>true</required>
            <conditional>
                <fieldName>cr-datacenter-654</fieldName>
                <operator>eq</operator>
                <value>domain-s675</value>
            </conditional>
        </field>
    </dataFields>
</descriptor>
"""

xmlDescriptorDataConditional3 = """\
<?xml version="1.0"?>
<newInstance>
  <cr-datacenter-2>domain-c341</cr-datacenter-2>
  <dataCenter>datacenter-2</dataCenter>
  <dataStore-domain-c341>datastore-588</dataStore-domain-c341>
  <description/>
  <descriptor/>
  <history/>
  <id/>
  <image xmlNodeHash="52425d8d813674d7c7ad4aff39eccd1404fc4656">
    <architecture>x86_64</architecture>
    <baseFileName>newappliance-1-x86_64</baseFileName>
    <buildDescription/>
    <buildId>12</buildId>
    <buildName>newappliance-VMware ESX ESX (x86_64)</buildName>
    <cloudAlias>design-vc2</cloudAlias>
    <cloudName>design-vc2.cisco.com</cloudName>
    <cloudType>vmware</cloudType>
    <downloadUrl>https://rpath-bld-001.cisco.com/downloadImage?fileId=15</downloadUrl>
    <id>https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/images/0ac74fef-0fe4-c56a-ab49-c2000dcacb6e</id>
    <imageId>0ac74fef-0fe4-c56a-ab49-c2000dcacb6e</imageId>
    <isDeployed>false</isDeployed>
    <isPrivate_rBuilder>false</isPrivate_rBuilder>
    <is_rBuilderImage>true</is_rBuilderImage>
    <longName>12/newappliance-1-x86_64</longName>
    <productDescription/>
    <productName>widgetappliance</productName>
    <publisher>admin</publisher>
    <role>Product Owner</role>
    <shortName>newappliance-1-x86_64</shortName>
    <description>12/newappliance-1-x86_64</description>
    <isPublic>false</isPublic>
    <libraryId/>
    <location>12/newappliance-1-x86_64</location>
    <myRating>-1</myRating>
    <name>newappliance-VMware ESX ESX (x86_64)</name>
    <ownerId/>
    <productCode/>
    <productCodes/>
    <rating>5</rating>
    <state/>
  </image>
  <imageId>https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/images/0ac74fef-0fe4-c56a-ab49-c2000dcacb6e</imageId>
  <instanceDescription>widget-1</instanceDescription>
  <instanceName>widget-1</instanceName>
  <name/>
  <network-datacenter-2>dvportgroup-569</network-datacenter-2>
  <remoteIp>64.102.35.119</remoteIp>
  <resourcePool-domain-c341>resgroup-342</resourcePool-domain-c341>
  <resultResource/>
  <securityGroups/>
  <system/>
  <target id="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com">
    <activeJobs href="https://rpath-bld-001.cisco.com/catalog/jobs/types/instance-launch/jobs?cloudName=design-vc2.cisco.com&amp;cloudType=vmware&amp;status=Running"/>
    <cloudAlias>design-vc2</cloudAlias>
    <cloudName>design-vc2.cisco.com</cloudName>
    <configuration href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/configuration"/>
    <description>Design VC-2</description>
    <descriptorLaunch href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/descriptor/launch"/>
    <images href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/images"/>
    <instances href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/instances"/>
    <type href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware">vmware</type>
    <userCredentials href="https://rpath-bld-001.cisco.com/catalog/clouds/vmware/instances/design-vc2.cisco.com/users/admin/credentials"/>
    <cloudType>vmware</cloudType>
    <fullDescription>design-vc2 (Design VC-2)</fullDescription>
    <instanceDescription>design-vc2 (design-vc2.cisco.com)</instanceDescription>
    <instanceFullDescription>Design VC-2 (design-vc2.cisco.com)</instanceFullDescription>
    <isCreatable>false</isCreatable>
    <isRemovable>false</isRemovable>
    <isUpdatable>false</isUpdatable>
    <launchEnvironmentRef/>
    <name>Design VC-2</name>
  </target>
</newInstance>
"""

if __name__ == "__main__":
    testsuite.main()

/*
#
# Copyright (c) 2008-2011 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/


package com.rpath.raf.models
{
import com.rpath.xobj.XObjXMLDecoder;
import com.rpath.xobj.XObjXMLEncoder;
import com.verveguy.rest.RESTResource;

import flash.xml.XMLDocument;
import flash.xml.XMLNode;

import mx.collections.ArrayCollection;

[Bindable]
public class Descriptor extends RESTResource
{
    public function Descriptor()
    {
        super();
        
        metadata = new MetadataDescriptor();
        dataFields = new DataFieldsDescriptor();
    }
    
    public var metadata:MetadataDescriptor;
    
    public var dataFields:DataFieldsDescriptor;
    
    public function asXML():XML
    {
        var xmlNode:XMLNode;
        var newXML:XML;
        var myXML:XMLDocument = new XMLDocument();
        var xmlEncoder:XObjXMLEncoder = new XObjXMLEncoder({descriptor:Descriptor}, myXML);
        
        xmlEncoder.encodeNullElements = false;
        
        xmlNode = xmlEncoder.encodeObject(this);
        newXML = new XML(xmlNode.toString());
        
        return newXML;
    }

    public static function fromXML(xml:XML):Descriptor
    {
        // try parsing into a new Descriptor structure...
        var xmlNode:XMLNode = new XMLDocument(xml);
        var xmlDecoder:XObjXMLDecoder = new XObjXMLDecoder({descriptor:Descriptor});
        
        var decode:* = xmlDecoder.decodeXML(xmlNode);
        return decode.root as Descriptor;
    }

    public function toString():String
    {
        // pretty print a version for our descriptor XML display
        XML.prettyIndent = 2;
        XML.prettyPrinting = true;
        
        return asXML().toXMLString();
    }
    
}
}
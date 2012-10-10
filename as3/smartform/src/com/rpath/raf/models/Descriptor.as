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

import flash.events.Event;

import mx.events.CollectionEvent;

[Bindable]
public class Descriptor extends RESTResource
{
    public function Descriptor()
    {
        super();
        
        metadata = new MetadataDescriptor();
        dataFields = new DataFieldsDescriptor();
    }
    
    // alternative construction pattern
    public static function fromXML(xml:XML):Descriptor
    {
        // try parsing into a new Descriptor structure...
        var descriptor:Descriptor = new Descriptor();
        return descriptor.fromXML(xml);
    }

    
    public var metadata:MetadataDescriptor;
    
    private var _dataFields:DataFieldsDescriptor;

    [Bindable(event="dataFieldsChange")]
    public function get dataFields():DataFieldsDescriptor
    {
        return _dataFields;
    }

    public function set dataFields(value:DataFieldsDescriptor):void
    {
        if( _dataFields !== value)
        {
            trackSubcollection(_dataFields, value, handleDataFieldsChanged);
            _dataFields = value;
            
            dispatchEvent(new Event("dataFieldsChange"));
        }
    }

    // OVERRIDE value mapping for simple XML CDATA blocks
    [xobjTransient]
    override public function get value():String
    {
        return _rawXMLString;
    }
    
    private var _rawXMLString:String;
    
    override public function set value(s:String):void
    {
        _rawXMLString = s;
        // load ourselves up
        fromXMLString(_rawXMLString);
    }
    
    [xobjTransient]
    public var version:String;
    
    protected function handleDataFieldsChanged(event:CollectionEvent):void
    {
        dispatchEvent(new Event("dataFieldsChange"));
    }

    public function findFieldByUID(uid:String):FieldDescriptor
    {
        var field:FieldDescriptor;
        var match:Array;
        
        match = dataFields.toArray().filter(
            function find(item:FieldDescriptor, index:int, array:Array):Boolean 
            {
                return item.uid == uid;
            });
        
        if (match.length > 0)
            field = match[0];
            
        return field;
    }
    
    public function findFieldByName(name:String):FieldDescriptor
    {
        var field:FieldDescriptor;
        var match:Array;
        
        match = dataFields.toArray().filter(
            function find(item:FieldDescriptor, index:int, array:Array):Boolean 
            {
                return item.name == name;
            });
        
        if (match.length > 0)
            field = match[0];
        
        return field;
    }
    
    private static const typeMap:Object = {descriptor: Descriptor, conditional:ConditionDescriptor, 'default':String};
    
    public function asXML():XML
    {
        var xml:XML;
        var xmlEncoder:XObjXMLEncoder = new XObjXMLEncoder(typeMap);
        
        // server doesn't like these
        xmlEncoder.encodeNullElements = false;
        
        xml = xmlEncoder.encodeObject(this);
        
        // HACK: Bug in namespace handling in xobj/AS3 XML makes namespaces broken
        // unless we dump to plain string and back again (cleanses things..?????)
        var dupXML:XML = new XML(xml.toXMLString());
        
        return dupXML;
    }

    public function fromXML(xml:XML):Descriptor
    {
        // NOTE: we must pass in a typeMap for the <conditional> tag since we rely
        // on repeated element "fake array" stuff for the conditions...would have
        // to revise smartform XML format to wrap multiple conditions
        var xmlDecoder:XObjXMLDecoder = new XObjXMLDecoder(typeMap);
        var result:Descriptor = this;
        
        try
        {
            var decode:* = xmlDecoder.decodeXMLIntoObject(xml, this);
        }
        catch (e:Error)
        {
            // bad XML
            result = null;
        }
        
        return this;
    }
    
    public function fromXMLString(s:String):Descriptor
    {
        var xml:XML = new XML(s);
        return fromXML(xml);
    }


    public function toString():String
    {
        // pretty print a version for our descriptor XML display
        XML.prettyIndent = 2;
        XML.prettyPrinting = true;
        return asXML().toXMLString();
    }
    
    
    // don't remove, break package creator 
    public var xsi_schemaLocation:String;
    public var xmlns_xsi:String;
    public var xmlns:String;
}
}
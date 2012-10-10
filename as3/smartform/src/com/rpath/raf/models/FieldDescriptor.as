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
import com.rpath.xobj.IXObjReference;
import com.verveguy.rest.RESThref;

import flash.events.Event;
import flash.events.IEventDispatcher;

import mx.collections.ArrayCollection;
import mx.controls.HRule;
import mx.events.CollectionEvent;
import mx.events.PropertyChangeEvent;
import mx.events.PropertyChangeEventKind;
import mx.utils.UIDUtil;

/**
 * 
 * <field>
 <name>container.options.diskAdapter</name>
 <required>true</required>
 <descriptions>
 <desc>Disk driver</desc>
 </descriptions>
 <prompt>
 <desc>Select the disk driver that the VM should use.</desc>
 </prompt>
 
 <enumeratedType>
 
 <describedValue>
 <descriptions>
 <desc>IDE</desc>
 </descriptions>
 <key>ide</key>
 </describedValue>
 
 <describedValue>
 <descriptions>
 <desc>SCSI (LSILogic)</desc>
 </descriptions>
 <key>lsilogic</key>
 </describedValue>
 
 </enumeratedType>
 <default>lsilogic</default>
 </field>
 * 
 */

[Bindable]
public dynamic class FieldDescriptor implements IXObjReference
{
    public function FieldDescriptor()
    {
        super();
        
        descriptions = new Description();
        prompt = new Description();
        constraints = new ConstraintDescriptor();
        enumeratedType = new EnumTypesDescriptor();
        conditional = new ConditionsDescriptor();
        
        // now translate collection change events on our sub properties into 
        // property change events on us...this is to watch the "first" property
        // of our Description elements which is all to make DataGrids work
        // as expected when displaying the description.first property
        watchDescription("descriptions");
        watchDescription("descriptions");
        
        uid = UIDUtil.createUID();
    }
    
    public function elementTypeForElementName(elementName:String):Class
    {
        if (elementName == 'default')
            return String;
        else
            return null;
    }

    // To satisfy IXobjReference
    [xobjTransient]
    public var isByReference:Boolean = false;

/*   
    [xobjTransient]
    THIS CANNOT BE TRANSIENT 
    We rely on being able ot use the UID either side of a transform to/from XML
    in the SmartFormEditor. 
    
    Once the SmartFormEditor no longer uses XML as the metadata carrier (i.e. 
    once it transforms to FieldDescriptors, etc as a model from the start)
    we can make this transient again
*/    
    public var uid:String;
    
    private function watchDescription(propName:String):void
    {
        this[propName].addEventListener(PropertyChangeEvent.PROPERTY_CHANGE, makePropWatcher(propName));
    }
    
    private function makePropWatcher(propName:String):Function
    {
        var localThis:FieldDescriptor = this;
        return function onPropertyChange(event:PropertyChangeEvent):void
        {
            localThis["dispatchEvent"](new PropertyChangeEvent(PropertyChangeEvent.PROPERTY_CHANGE, false, false, 
                PropertyChangeEventKind.UPDATE, propName, null, localThis[propName].first, this));
        }
    }
    
    public var name:String;
    public var required:Boolean;

    /** when type changes, we have to clear out other parts of the descriptor
    */
    
    public function get type():String
    {
        return _type;
    }

    private var _type:String;

    public function set type(value:String):void
    {
        // destroy old constraints, etc.
        constraints = new ConstraintDescriptor();
        enumeratedType = new EnumTypesDescriptor();
        conditional = new ConditionsDescriptor();
        password = false;
        allowFileContent = false;
        multiple = false;
        
        _type = value;
    }

    public var help:RESThref = new RESThref(""); // URL to help
    
    public var descriptions:Description;
    
    public var prompt:Description;
    
    private var _enumeratedType:EnumTypesDescriptor;
    
    public function get enumeratedType():EnumTypesDescriptor
    {
        return _enumeratedType;
    }
    
    public function set enumeratedType(value:EnumTypesDescriptor):void
    {
        if (_enumeratedType)
        {
            _enumeratedType.removeEventListener(CollectionEvent.COLLECTION_CHANGE, handleEnumTypesChanged);
        }
        
        _enumeratedType = value;
        
        if (_enumeratedType)
        {
            _enumeratedType.addEventListener(CollectionEvent.COLLECTION_CHANGE, handleEnumTypesChanged, false, 0, true);
        }
    }
    
    protected function handleEnumTypesChanged(event:CollectionEvent):void
    {
        this.dispatchEvent(new PropertyChangeEvent(PropertyChangeEvent.PROPERTY_CHANGE, false, false, 
            PropertyChangeEventKind.UPDATE, "enumeratedType", enumeratedType, enumeratedType, this));
    }
    
    [ArrayElementType("com.rpath.raf.models.ConditionDescriptor")]
    public var conditional:ConditionsDescriptor;
    
    public var constraints:ConstraintDescriptor;
    
    
    public var allowFileContent:Boolean;
    public var password:Boolean;
    
    public var multiple:Boolean;
    
    public var hidden:Boolean;
    
    /** new ordering and group properties **/
    [xobjTransient]
    public var ordinal:uint;
    
    public var section:SectionDescriptor;
    
    // compoundType and listType have subsdescriptor
    public var descriptor:Descriptor;
    
}
}
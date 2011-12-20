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
import flash.events.IEventDispatcher;

import mx.collections.ArrayCollection;
import mx.controls.HRule;
import mx.events.CollectionEvent;
import mx.events.PropertyChangeEvent;
import mx.events.PropertyChangeEventKind;

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
public dynamic class FieldDescriptor
{
    public function FieldDescriptor()
    {
        super();
        
        this["default"] = null;  // HOW TO DEAL WITH THIS RESERVED WORD COLLISION?
        
        descriptions = new Description();
        prompt = new Description();
        constraints = new ConstraintDescriptor();
        enumeratedType = new EnumTypesDescriptor();
        conditional = [];
        
        // now translate collection change events on our sub properties into 
        // property change events on us...this is to watch the "first" property
        // of our Description elements which is all to make DataGrids work
        // as expected when displaying the description.first property
        watchDescription("descriptions");
        watchDescription("prompt");
    }
    
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
    public var type:String;
    public var help:String; // URL to help
    
    public var descriptions:Description;
    
    public var prompt:Description;
    
    public var enumeratedType:EnumTypesDescriptor;
    
    [ArrayElementType("com.rpath.raf.models.ConditionDescriptor")]
    public var conditional:Array;
    
    public var constraints:ConstraintDescriptor;
    
    
    public var allowFileContent:Boolean;
    public var password:Boolean;
    
    public var multiple:Boolean;
    
    public var hidden:Boolean;
}
}
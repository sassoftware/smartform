/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{
import mx.collections.ArrayCollection;
import mx.controls.HRule;

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
    }
    
    public var name:String;
    public var required:Boolean;
    public var type:String;
    public var help:String; // URL to help
    
    public var descriptions:Description;
    
    public var prompt:Description;
    
    [ElementType("com.rpath.raf.models.EnumDescriptor")]
    public var enumeratedType:ArrayCollection;
    
    [ElementType("com.rpath.raf.models.ConditionDescriptor")]
    public var conditional:ArrayCollection;
    
    public var constraints:ConstraintDescriptor;
    
    
    public var allowFileContent:Boolean;
    public var password:Boolean;
    
    public var multiple:Boolean;
    
    public var hidden:Boolean;
}
}
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

/*
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
*/

[Bindable]
public class EnumDescriptor
{
    public function EnumDescriptor()
    {
        super();
        descriptions = new Description();
    }
    
    public var key:String;
    
    public var descriptions:Description;
    
}
}
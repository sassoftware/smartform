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

[Bindable]
public class MetadataDescriptor
{
    public function MetadataDescriptor()
    {
        super();
        descriptions = new Description();
        descriptions.addItem(new DescriptionEntry());
    }
    
    public var displayName:String;
    
    public var descriptions:Description;

}
}
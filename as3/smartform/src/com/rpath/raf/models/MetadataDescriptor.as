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
    }
    
    public var displayName:String;
    
    public var descriptions:Description;

}
}
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
public class Descriptor
{
    public function Descriptor()
    {
        super();
        
        FieldDescriptor;
    }
    
    public var metadata:MetadataDescriptor;
    
    
    [ElementType("com.rpath.raf.models.FieldDescriptor")]
    public var dataFields:ArrayCollection;
}
}
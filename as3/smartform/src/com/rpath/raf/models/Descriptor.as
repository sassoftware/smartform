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
        
        metadata = new MetadataDescriptor();
        dataFields = new DataFieldsDescriptor();
    }
    
    public var metadata:MetadataDescriptor;
    
    public var dataFields:DataFieldsDescriptor;
}
}
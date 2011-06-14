/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{
import spark.components.supportClasses.Range;

[Bindable]
public class ConstraintDescriptor
{
    public function ConstraintDescriptor()
    {
        super();
    }
    
    public var range:RangeDescriptor;
    public var length:String;  // so we can represent null values
    public var regexp:String;
}
}
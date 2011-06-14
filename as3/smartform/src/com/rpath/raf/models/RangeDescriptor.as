/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{

[Bindable]
public class RangeDescriptor
{
    public function RangeDescriptor()
    {
        super();
    }
    
    public var min:String;  // so we can represent null values
    public var max:String;
}
}
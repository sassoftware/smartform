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
public class ConditionDescriptor
{
    public function ConditionDescriptor()
    {
        super();
    }
    
    public var fieldName:String;
    public var operator:String;
    public var value:String;
}
}
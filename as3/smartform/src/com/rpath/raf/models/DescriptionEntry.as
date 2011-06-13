/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{
import com.rpath.xobj.XObjString;

[Bindable]
public class DescriptionEntry extends XObjString
{
    public function DescriptionEntry()
    {
        super();
    }
    
    public var lang:String;
}
}
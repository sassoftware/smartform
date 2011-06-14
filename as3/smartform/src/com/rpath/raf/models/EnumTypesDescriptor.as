/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{
import com.rpath.xobj.XObjArrayCollection;

public class EnumTypesDescriptor extends XObjArrayCollection
{
    public function EnumTypesDescriptor(source:Array=null, typeMap:*=null)
    {
        super(source, {describedValue: EnumDescriptor});
    }
}
}
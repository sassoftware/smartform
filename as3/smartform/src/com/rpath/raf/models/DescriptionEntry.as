/*
#
# Copyright (c) 2007-2011 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.models
{
import com.rpath.xobj.XObjMetadata;
import com.rpath.xobj.XObjString;

[Bindable]
public class DescriptionEntry extends XObjString
{
    public function DescriptionEntry(lang:String=null, value:String=null)
    {
        super();
        this.lang = lang;
        this.value = value;
        
        // encode lang as attr
        XObjMetadata.addAttribute(this, "lang");
    }
    
    public var lang:String;
}
}
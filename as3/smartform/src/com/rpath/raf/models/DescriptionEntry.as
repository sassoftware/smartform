/*
#
# Copyright (c) 2008-2011 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/


package com.rpath.raf.models
{
import com.rpath.xobj.XObjMetadata;
import com.rpath.xobj.XObjString;

[Bindable]
public class DescriptionEntry extends XObjString
{
    public function DescriptionEntry(lang:String="en_US", value:String=null)
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
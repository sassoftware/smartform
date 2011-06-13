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

public class Description extends XObjArrayCollection
{
    public function Description(source:Array=null)
    {
        super(source, {desc: DescriptionEntry});
    }
    
    public function valueForLang(lang:String):String
    {
        for each (var desc:DescriptionEntry in this)
        {
            if (desc.lang == lang)
                return desc.toString();
        }
        
        return toString(); // go with whatever we've got
    }
    
    override public function toString():String
    {
        if (length > 0)
        {
            return valueForLang("en_US"); // TODO: lookup user locale
        }
        else
        {
            return null;
        }
    }
    
    public function valueOf():Object
    {
        return toString();
    }
}
}
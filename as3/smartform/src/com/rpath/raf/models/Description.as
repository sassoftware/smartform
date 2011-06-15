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
        // make sure we always have one
        addItem(new DescriptionEntry());
    }
    
    public function valueForLang(lang:String):String
    {
        var desc:DescriptionEntry;
        
        if (length == 0)
            return null;
        
        for each (desc in this)
        {
            if (desc.lang == lang)
                return desc.toString();
        }
        
        // TODO: look for a locale one first
        
        // what about english?
        lang = "en_US";
        
        for each (desc in this)
        {
            if (desc.lang == lang)
                return desc.toString();
        }
        
        // just take the first one...
        return this[0].toString();
    }
    
    override public function toString():String
    {
        return valueForLang("en_US"); // TODO: lookup user locale
    }
    
    public function valueOf():Object
    {
        return toString();
    }
    
    [Transient]
    public function get first():String
    {
        return toString();
    }
    
    public function set first(s:String):void
    {
        this[0].value = s;
    }
}
}
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
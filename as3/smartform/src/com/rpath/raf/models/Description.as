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

import flash.events.Event;

import mx.events.CollectionEvent;
import mx.events.PropertyChangeEvent;
import mx.events.PropertyChangeEventKind;

[Bindable]
public class Description extends XObjArrayCollection
{
    public function Description(source:Array=null)
    {
        super(source, {desc: DescriptionEntry});
        
        // we need to maintain our synthetic first property
        addEventListener(CollectionEvent.COLLECTION_CHANGE, onCollectionChange);
        
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
            if (desc && desc.lang == lang)
                return desc.toString();
        }
        
        // TODO: look for a locale one first
        
        // what about english?
        lang = "en_US";
        
        for each (desc in this)
        {
            if (desc && desc.lang == lang)
                return desc.toString();
        }
        
        // just take the first one...
        if (this[0])
            return this[0].toString();
        else
            return "(null)"
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
        return _first;
    }
    
    private var _first:String;
    
    public function set first(s:String):void
    {
        if (_first == s)
            return;
        
        if (length > 0)
        {
            if (this[0] == null)
                this[0] = new DescriptionEntry("en_US", s);
            else
                this[0].value = s;
            _first = s;
        }
    }
    
    
    private function onCollectionChange(event:CollectionEvent):void
    {
        // first may have changed. Signal this
        first = toString();
        
        
        // do we need to send some kind of validation event here?
        
    }

}
}
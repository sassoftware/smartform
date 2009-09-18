/*
#
# Copyright (c) 2009 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any waranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.events
{
    
    import mx.events.DynamicEvent;
    import mx.rpc.Fault;

    [Bindable]
    public class HelpEvent extends DynamicEvent
    {
        public function HelpEvent(type:String, bubbles:Boolean=true, cancelable:Boolean=false)
        {
            super(type, bubbles, cancelable);
        }
        
        public static var SHOW_HELP:String = "showHelp";
        
        public var text:String;

        public var uri:String;
        
        public function get node():XMLList
        {
            return _node;
        }
        
        private var _node:XMLList;

        public function set node(n:XMLList):void
        {
            _node = n;
            
            // do we have an href to the help text?
            if (node.@href.length > 0)
            {
                uri = node.@href.toString();
            }
            else
            {
                // do we have a locale resource ref?
                var val:String;
                val = node.toString();
                if (val.charAt(0) == "@")
                {
                    key = val.replace(/@/g,'');
                }
                else
                {
                    // use the literal value
                    text = val;
                }
            }
        }
        
        
        public function set key(k:String):void
        {
            _key = k;
            // look up the key in the locale bundle if you want....
            // text = ...
        }
        
        private var _key:String;
        
        public function get key():String
        {
            return _key;
        }
        
        public function hasHelp():Boolean
        {
            return ((node && node.length() > 0) || key || (text && text != ""));
        }

        private function handleHelpSuccess(data:String):void
        {
            text = data;
        }
        
        private function handleHelpFailure(fault:Fault):void
        {
            text = "<b>Failed retrieving help text.</b><br/>" + 
                (fault ? fault.faultDetail : "");;
        }

    }
}
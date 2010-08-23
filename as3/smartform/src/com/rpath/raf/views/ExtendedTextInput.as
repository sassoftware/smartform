/*
#
# Copyright (c) 2009 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.views
{
     
    public class ExtendedTextInput extends PromptingTextInput
    {
        override public function set enabled(value:Boolean):void
        {
           super.enabled = value;
           selectStyle();
        }
         
        override public function set editable(value:Boolean):void
        {
           super.editable = value;
           selectStyle();
        }
         
        private function selectStyle():void
        {
           //styleName = (editable && enabled) ? getStyle("enabledStyleName") as String : getStyle("disabledStyleName") as String;
           styleName = (editable && enabled) ? "enabledTI" as String : "nonEnabledTI" as String;
           if (editable && enabled)
           {
               this.setStyle("disabledColor", 0x000000);
           }
           else
           {
               this.setStyle("disabledColor", 0x000000);
           }
        }

    }
}
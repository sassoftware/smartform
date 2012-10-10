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
import com.rpath.raf.controls.AdvancedTextArea;
import com.rpath.raf.util.UIHelper;

import flash.events.Event;
import flash.events.FocusEvent;

import mx.effects.Resize;
import mx.events.FlexEvent;


public class ExtendedTextArea extends AdvancedTextArea
{
    public function ExtendedTextArea()
    {
        super();
    }
    
    /** allowFileContent controls whether a small "from file" button should 
     * be offered to read content from a local file
     */
    [Bindable]
    public var allowFileContent:Boolean;
    
    
    /** override of text property to handle CR/LF consistently across
     * platforms
     */
    
    [Bindable]
    override public function set text(value:String):void
    {
        super.text = UIHelper.processCarriageReturns(value);
    }
    
    override public function get text():String
    {
        return super.text;
    }

}
}
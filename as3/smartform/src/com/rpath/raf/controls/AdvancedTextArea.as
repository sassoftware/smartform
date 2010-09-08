/*
#
# Copyright (c) 2010 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.controls
{
import com.rpath.raf.skins.AdvancedTextAreaSkin;

import flash.events.FocusEvent;

import spark.components.TextArea;

public class AdvancedTextArea extends TextArea
{
    //----------------------------------------------------------------------
    //
    //	Constructor
    //
    //----------------------------------------------------------------------
    
    public function AdvancedTextArea()
    {
        super();
        setStyle("skinClass", com.rpath.raf.skins.AdvancedTextAreaSkin);
    }
    
    //----------------------------------------------------------------------
    //
    //	States
    //
    //----------------------------------------------------------------------
    
    [SkinState("focused")];
    
    //----------------------------------------------------------------------
    //
    //	Properties
    //
    //----------------------------------------------------------------------
    
    private var _promptText:String
    
    [Bindable]
    
    public function get promptText():String
    {
        return _promptText;
    }
    
    public function set promptText(v:String):void
    {
        _promptText = v;
    }
    
    [Bindable]
    public function get prompt():String
    {
        return promptText;
    }
    
    public function set prompt(v:String):void
    {
        promptText = v;
    }
    
    /** autoResize controls the dynamic expand/contract behavior
     * 
     * @default true
     */
    
    [Bindable]
    public var autoResize:Boolean = true;

    //----------------------------------------------------------------------
    //
    //	Variables
    //
    //----------------------------------------------------------------------
    
    protected var focused:Boolean;
    
    //----------------------------------------------------------------------
    //
    //	Overridden Methods
    //
    //----------------------------------------------------------------------
    
    override protected function partAdded(partName:String, instance:Object):void
    {
        super.partAdded(partName, instance);
        
        if (instance == this.textDisplay)
        {
            this.textDisplay.addEventListener(FocusEvent.FOCUS_IN, onFocusInHandler);
            this.textDisplay.addEventListener(FocusEvent.FOCUS_OUT, onFocusOutHandler);
        }
    }
    
    override protected function partRemoved(partName:String, instance:Object):void
    {
        super.partRemoved(partName, instance);
        
        if (instance == this.textDisplay)
        {
            this.textDisplay.removeEventListener(FocusEvent.FOCUS_IN, onFocusInHandler);
            this.textDisplay.removeEventListener(FocusEvent.FOCUS_OUT, onFocusOutHandler);
        }
    }
    
    override protected function getCurrentSkinState():String
    {
        if (focused)
        {
            return "focused";
        }
        else
        {
            return super.getCurrentSkinState();
        }
    }
    
    //----------------------------------------------------------------------
    //
    //	Event Handlers
    //
    //----------------------------------------------------------------------
    
    private function onFocusInHandler(event:FocusEvent):void
    {
        focused = true;
        invalidateSkinState();
    }
    
    private function onFocusOutHandler(event:FocusEvent):void
    {
        focused = false;
        invalidateSkinState();
    }
    
}
}
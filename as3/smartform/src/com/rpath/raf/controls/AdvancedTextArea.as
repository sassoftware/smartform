package com.rpath.raf.controls
{
import flash.events.FocusEvent;

import spark.components.TextArea;
import com.rpath.raf.skins.AdvancedTextInputSkin;

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
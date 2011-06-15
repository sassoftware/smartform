/*

Copyright (c) 2009-2011 rPath, Inc.

This program is distributed under the terms of the MIT License as found 
in a file called LICENSE. If it is not present, the license
is always available at http://www.opensource.org/licenses/mit-license.php.

This program is distributed in the hope that it will be useful, but
without any warranty; without even the implied warranty of merchantability
or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.views
{
import com.rpath.raf.events.HelpEvent;
import com.rpath.raf.util.ErrorTipManager;
import com.rpath.raf.util.IValidationAware;
import com.rpath.raf.util.ValidationHelper;

import mx.containers.FormItem;
import mx.controls.Label;
import mx.events.FlexEvent;
import flash.events.MouseEvent;

[Event(name=HelpEvent.SHOW_HELP, type="com.rpath.raf.events.HelpEvent")]

public class ExtendedFormItem extends FormItem implements IValidationAware
{
    public function ExtendedFormItem()
    {
        super();
        
        this.addEventListener(FlexEvent.CREATION_COMPLETE, onCreationComplete);
        this.setStyle("backgroundAlpha","0");
    }
    
    [Bindable]
    public var helpLink:String;
    
    [Bindable]
    public var helpText:String;
    
    [Bindable]
    public var helpNode:XMLList;
    
    [Bindable]
    public var helpKey:String;
    
    
    public function onCreationComplete(event:FlexEvent):void
    {
        if ((helpNode && helpNode.length() > 0) || helpKey || (helpLink && helpLink != "") || (helpText && helpText != ""))
        {
            var lbl:Label = FormItem(event.currentTarget).itemLabel as Label;
            lbl.selectable = true;
            lbl.enabled = true;
            lbl.setStyle("color", this.getStyle("labelColor"));
            lbl.setStyle("textDecoration", "underline");
            lbl.toolTip = "Click here for more information";
            lbl.useHandCursor = true;
            lbl.buttonMode = true;
            lbl.mouseChildren = false;
            lbl.addEventListener(MouseEvent.CLICK, handleHelp,false,0,true);
        }
    }
    
    
    protected function handleHelp(event:MouseEvent):void
    {
        var evt:HelpEvent = new HelpEvent(HelpEvent.SHOW_HELP, true);
        if (helpText && helpText != "")
            evt.text = helpText;
        if (helpLink && helpLink != "")
            evt.uri = helpLink;
        if (helpKey && helpKey != "")
            evt.key = helpKey;
        dispatchEvent(evt);
    }
    
    //---------------------------------------------- VALIDATION
    
    [Bindable]
    public function set isValid(b:Boolean):void
    {
        _isValid = b;
        // rethrow the validation event so that our whole form can go invalid
        dispatchEvent(new FlexEvent(_isValid ? FlexEvent.VALID : FlexEvent.INVALID));
    }
    
    private var _isValid:Boolean = true;
    
    public function get isValid():Boolean
    {
        return _isValid;
    }
    
    private var _validationHelper:ValidationHelper;
    
    public function get validationHelper():ValidationHelper
    {
        return _validationHelper;
    }
    
    public function set validationHelper(v:ValidationHelper):void
    {
        _validationHelper = v;
    }
    
    public function initializeValidators():void
    {
        // first ensure we have a validation helper to listen
        validationHelper = new ValidationHelper(validators, this);
    }
    
    public var validators:Array;
    
    private var _pendingValidation:Boolean;
    
    public function validate(suppressEvents:Boolean=false):void
    {        
        if (validationHelper)
            validationHelper.validate(suppressEvents);
        else
        {
            _pendingValidation = true;
            invalidateProperties();
        }
    }
    
    // optionally, show errors via this manager
    private var _errorTipManager:ErrorTipManager;
    
    public function get errorTipManager():ErrorTipManager
    {
        return _errorTipManager;
    }
    
    public function set errorTipManager(value:ErrorTipManager):void
    {
        _errorTipManager = value;
        if (_validationHelper)
            _validationHelper.errorTipManager = _errorTipManager;
    }
    
    override protected function commitProperties():void
    {
        if (validationHelper == null)
        {
            initializeValidators();
        }
        
        if (_pendingValidation && validationHelper != null
            && validationHelper.errorTipManager.suppressionCount < 1)
        {
            _pendingValidation = false;
            validationHelper.showErrors();
        }
        
        super.commitProperties();
    }
    
    
    
}
}
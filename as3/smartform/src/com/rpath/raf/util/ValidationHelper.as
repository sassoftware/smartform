/*
#
# Copyright (c) 2008-2010 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.util
{    
import flash.events.Event;
import flash.events.IEventDispatcher;
import flash.utils.Dictionary;

import mx.events.DynamicEvent;
import mx.events.FlexEvent;
import mx.events.ValidationResultEvent;
import mx.validators.Validator;


/** ValidationHelper provides a way to aggregate the checking of multiple
 * Validators to arrive at an "isValid" decision. It offers the ability
 * to maintain the isValid property on a target object, typically a View that
 * contains a form, so that Save buttons, etc can be bound to the isValid
 * property rather than wiring up various event listeners to the underlying
 * validation events.
 * 
 * ValidationHelper accepts an array of Validators as well as the target to
 * inform of isValid changes.
 * 
 * ValidationHelper can also manage the presentation of errorTips.
 * 
 */

[Bindable]
public class ValidationHelper extends LifecycleObject implements IValidationAware
{
    public static const FIND_ERROR_TIP_MANAGER:String = "findErrorTipManager";
    
    public function ValidationHelper(vals:Array=null, 
                                     target:IEventDispatcher=null, 
                                     property:String="isValid", 
                                     newErrorTipManager:ErrorTipManager=null)
    {
        super();
        
        this.property = property;
        this.target = target;
        
        if (!this.errorTipManager)
        {
            if (newErrorTipManager)
                this.errorTipManager = newErrorTipManager;
            else
                errorTipManager = new ErrorTipManager();
        }
        
        errorTipManager.increaseSuppressionCount();
        
        this.errorTipManager = errorTipManager;
        
        // do this last, since it wires up errorTipManager as a side effect
        itemsToValidate = vals;
    }
    
    private var _isValid:Boolean = true;
    
    /** isValid indicates whether this ValidationHelper as a whole is
     * valid. This is also bound to the target.property (if provided)
     */
    public function get isValid():Boolean
    {
        return _isValid;
    }
    
    /**
     * @private
     */
    public function set isValid(value:Boolean):void
    {
        if (_isValid == value)
            return;
        
        _isValid = value;
        
        if (target)
        {
            target[property] = _isValid;
            // propagate a validation changed event through our target view
            // rethrow the validation event so that our whole form can go invalid
            dispatchEvent(new FlexEvent(_isValid ? FlexEvent.VALID : FlexEvent.INVALID));
            target.dispatchEvent(new FlexEvent(_isValid ? FlexEvent.VALID : FlexEvent.INVALID));
        }
    }
    
    /** required for conformance with the IValidationAware protocol
     */
    
    public function get validationHelper():ValidationHelper
    {
        return this;
    }
    
    public function set validationHelper(v:ValidationHelper):void
    {
        // ignore;
    }
    
    private var property:String;
    
    // we use a further helper instance to pop errorTips
    
    public function get errorTipManager():ErrorTipManager
    {
        return _errorTipManager;
    }
    
    private var _errorTipManager:ErrorTipManager;
    
    public function set errorTipManager(value:ErrorTipManager):void
    {
        _errorTipManager = value;
        // now inform it of all our validators
        for (var v:* in _validators)
        {
            _errorTipManager.registerValidator(v as Validator);
        }
    }
    
    public function get target():IEventDispatcher
    {
        return _target;
    }
    
    private var _target:IEventDispatcher;
    
    public function set target(v:IEventDispatcher):void
    {
        if (_target)
        {
            _target.removeEventListener(FIND_ERROR_TIP_MANAGER, handleRequestErrorTipManager);
            _target.removeEventListener(Event.CLOSE, handleTargetRemovedFromStage);
            _target.removeEventListener(FlexEvent.HIDE, handleTargetRemovedFromStage);
            _target.removeEventListener(Event.REMOVED_FROM_STAGE, handleTargetRemovedFromStage);
            _target.removeEventListener(Event.ADDED_TO_STAGE, handleTargetAddedToStage);
            _target.removeEventListener(FlexEvent.UPDATE_COMPLETE, handleTargetUpdateComplete);
        }
        
        _target = v;
        
        if (_target)
        {
            _target[property] = isValid;
            
            // go get our errorTip manager up the visual heirarchy
            findErrorTipManager();
            
            _target.addEventListener(FIND_ERROR_TIP_MANAGER, handleRequestErrorTipManager,false,0,true);
            _target.addEventListener(FlexEvent.UPDATE_COMPLETE, handleTargetUpdateComplete,false,0,true);
            _target.addEventListener(Event.CLOSE, handleTargetRemovedFromStage,false,0,true);
            _target.addEventListener(FlexEvent.HIDE, handleTargetRemovedFromStage,false,0,true);
            _target.addEventListener(Event.REMOVED_FROM_STAGE, handleTargetRemovedFromStage,false,0,true);
            _target.addEventListener(Event.ADDED_TO_STAGE, handleTargetAddedToStage,false,0,true);
        }
    }
    
    private function findErrorTipManager():void
    {
        var findEvent:DynamicEvent = new DynamicEvent(FIND_ERROR_TIP_MANAGER, true, false);
        findEvent.validationHelper = this;
        findEvent.errorTipManager = null;
        target.dispatchEvent(findEvent);
        if (findEvent.errorTipManager)
        {
            errorTipManager = findEvent.errorTipManager;
        }
    }
    
    private function handleRequestErrorTipManager(event:DynamicEvent):void
    {
        if (errorTipManager && !event.errorTipManager)
            event.errorTipManager = errorTipManager;
    }
    
    
    private function handleTargetUpdateComplete(event:Event):void
    {
        // remove all the error tips
        if (event.target == target)
        {
            errorTipManager.decreaseSuppressionCount();
        }
    }
    
    private function handleTargetAddedToStage(event:Event):void
    {
        // add all the error tip intercepts back
        if (event.target == target)
        {
            var vals:Array = itemsToValidate;
            
            // forcibly re-add all validators
            itemsToValidate = vals;
        }
    }
    
    private function handleTargetRemovedFromStage(event:Event):void
    {
        // remove all the error tips
        if (event.target == target)
        {
            reset();
        }
    }
    
    public function removeAllValidators():void
    {
        var v:*;
        
        errorTipManager.reset();
        
        for (v in _others)
        {
            var valAware:IValidationAware = v as IValidationAware;
            if (valAware)
            {
                if (valAware.validationHelper)
                    valAware.validationHelper.removeAllValidators();
                if (valAware.errorTipManager)
                    valAware.errorTipManager.reset();
            }
        }
        
        // and forget all items
        for each (v in itemsToValidate)
        {
            removeItemToValidate(v);
        }
        
    }
    
    public function reset():void
    {
        var v:*;
        
        //errorTipManager.reset();
        
        // cascade the reset
        /*            for (var v:* in _others)
        {
        var valAware:IValidationAware = v as IValidationAware;
        if (valAware)
        {
        if (valAware.validationHelper)
        valAware.validationHelper.reset();
        if (valAware.errorTipManager)
        valAware.errorTipManager.reset();
        }
        }*/
        
        // and forget all items
        for each (v in itemsToValidate)
        {
            suspendItemToValidate(v);
        }
        
    }
    
    private var _itemsToValidate:Dictionary = new Dictionary(true);
    
    // _vals is a partition of actual Validator instances
    private var _validators:Dictionary = new Dictionary(true);
    
    // _others is a partition of non-Validator instances we're also
    // monitoring as part of the total validation set
    private var _others:Dictionary = new Dictionary(true);
    
    public function addItemToValidate(v:IEventDispatcher):void
    {
        if (!v)
            return;
        
        _itemsToValidate[v] = true;
        
        var validator:Validator = v as Validator;
        if (validator)
        {
            _validators[validator] = true;
            setupListeners(validator);
            if (errorTipManager)
                errorTipManager.registerValidator(validator);
        }
        else 
        {
            // we want to share a single errorTipManager
            var vAware:IValidationAware = v as IValidationAware;
            
            if (vAware)
            {
                vAware.errorTipManager = errorTipManager;
            }
            else // must just be a plain old item...
            {
                errorTipManager.addComponentListeners(v);
            }
            
            _others[v] = true;
            setupListeners(v);
        }
    }
    
    /** suspendItemToValidate prevents an item from being actively tracked
     * but does NOT remove it from the overal list of items. This is necessary
     * in the case where scroll bars cause a REMOVED_FROM_STAGE followed by an
     * ADD_TO_STAGE which can fool us into prematurely removing validators
     */
    
    public function suspendItemToValidate(v:*):void
    {
        if (v is IEventDispatcher)
        {
            removeListeners(v);
        }
        
        var validator:Validator = v as Validator;
        var valAware:IValidationAware = v as IValidationAware;
        
        if (validator)
        {
            errorTipManager.unregisterValidator(validator);
        }
        else if (valAware)
        {
            if (valAware.validationHelper)
                valAware.validationHelper.reset();
        }
        else
        {
            errorTipManager.removeComponentListeners(v);
            errorTipManager.hideErrorTip(v);
        }
        
        // clean up our various partitioned validators
        delete _others[v];
        delete _validators[v];
    }
    
    public function removeItemToValidate(v:*):void
    {
        suspendItemToValidate(v);
        // and now also remove it frmo the list entirely
        delete _itemsToValidate[v];
    }
    
    protected function setupListeners(v:IEventDispatcher):void
    {
        v.addEventListener(ValidationResultEvent.VALID, handleItemValidationEvent,false,0,true);
        v.addEventListener(ValidationResultEvent.INVALID, handleItemValidationEvent,false,0,true);
        v.addEventListener(FlexEvent.VALID, handleItemValidationEvent,false,0,true);
        v.addEventListener(FlexEvent.INVALID, handleItemValidationEvent,false,0,true);
        //v.addEventListener("validChanged", handleItemValidationEvent,false,0,true);
    }
    
    protected function removeListeners(v:IEventDispatcher):void
    {
        v.removeEventListener(ValidationResultEvent.VALID, handleItemValidationEvent);
        v.removeEventListener(ValidationResultEvent.INVALID, handleItemValidationEvent);
        v.removeEventListener(FlexEvent.VALID, handleItemValidationEvent);
        v.removeEventListener(FlexEvent.INVALID, handleItemValidationEvent);
        //v.removeEventListener("validChanged", handleItemValidationEvent);
    }
    
    
    public function get itemsToValidate():Array
    {
        return DictionaryUtils.getKeys(_itemsToValidate);
    }
    
    public function set itemsToValidate(vals:Array):void
    {
        var v:*;
        
        removeAllValidators();
        reset();
        for each (v in vals)
        {
            // allow for nested sets
            if (v is Array)
            {
                for each (var v2:* in v)
                {
                    addItemToValidate(v2);
                }
            }
            else
            {
                addItemToValidate(v);
            }
            
        }
        
        // now ensure our own isValid state reflects validity of all 
        // new Validators
        _needsSuppressedValidation = true;
        invalidateProperties();
    }
    
    
    private var _validating:Boolean;
    
    /** checkValidity runs through all validators and checks their state
     *  Note that we handle the events carefully to control whether the
     *  actual UI elements hear the events or not
     */
    
    public function checkValidity(validators:Array, suppressEvents:Boolean=true):Array
    {   
        var result:Array = [];
        
        var n:int = validators.length;
        for (var i:int = 0; i < n; i++)
        {
            var v:Validator = validators[i] as Validator;
            
            if (v && v.enabled && v.source)
            {
                // Validate with event dispatch so that we and our errorTip
                // manager get to hear the events.
                var resultEvent:ValidationResultEvent = v.validate(null, suppressEvents);
                
                _validationStates[v] = (resultEvent.type == ValidationResultEvent.VALID);
                
                if (resultEvent.type != ValidationResultEvent.VALID)
                {
                    result.push(resultEvent);
                }
                
            }
        }   
        
        return result;
    }
    
    // unfortunately, FlexEvent.VALID and ValidationResultEvent.VALID are the
    // same string constant
    
    private var _validationStates:Dictionary = new Dictionary(true);
    
    private function computeValidityFromCache():void
    {
        var newValid:Boolean = true;
        var item:*;
        var items:Array;
        
        items = DictionaryUtils.getKeys(_validationStates);
        
        // recompute validity from the cache
        for each (item in items)
        {
            newValid = newValid && _validationStates[item];
        }
        
        isValid = newValid;
    }
    
    public function handleItemValidationEvent(event:Event):void
    {
        
        // plain FlexEvent is the way a UIComponent reports it's validity
        // typically after setting errorString on itself
        if (event is FlexEvent)
        {
            // make a note of the source of the event since we should
            // check this object directly in computing valid status
            addItemToValidate(event.target as IEventDispatcher);
            
            // and recompute our own validity
            
            _validationStates[event.target] = (event.type == FlexEvent.VALID);
            
            if (!_validating)
            {
                computeValidityFromCache();
            }
        }
            // ValidationResultEvents are sent by Validators to report their
            // assessment of a source items validity. We're inserted in the 
            // middle of this chain
        else if (event is ValidationResultEvent)
        {
            
            _validationStates[event.target] = (event.type == ValidationResultEvent.VALID);
            
            if (!_validating)
            {
                computeValidityFromCache();
            }
        }
    }
    
    
    public function validate(suppressEvents:Boolean=false):void
    {
        if (!_validating)
        {
            _validating = true;
            
            //errorTipManager.suppressErrors = suppressEvents;
            
            var valid:Boolean = false;
            
            var results:Array = checkValidity(DictionaryUtils.getKeys(_validators), suppressEvents);
            
            valid = (results.length == 0);
            
            // now all the "others"
            for (var v:* in _others)
            {
                var valAware:IValidationAware = v as IValidationAware;
                
                if (valAware)
                {
                    valAware.validate(suppressEvents);
                    _validationStates[valAware] = valAware.isValid;
                    valid = valid && valAware.isValid;
                }
                else
                {
                    trace("found non valaware item");
                    // what to do with this? Assume NOT valid
                    _validationStates[v] = false;
                }
            }
            
            _validating = false;
            
            isValid = valid;
        }
    }
    
    
    // ----------------- Convenience FACADE for ErrorTipManager
    
    /** showErrors() performs a validation pass and pops errorTips at the 
     * same time. ErrorTips will remain visible until the errors are cleared
     * or until the hideErrors() method is called.
     */
    
    public function showErrors():void
    {
        // revalidate and throw events so we get errorTips
        //errorTipManager.showAllErrors = true;
        validate(false);
        errorTipManager.showAllErrorTips();
    }
    
    public function hideErrors():void
    {
        errorTipManager.hideAllErrorTips();
        // but still allow new errors to pop
        errorTipManager.decreaseSuppressionCount();
    }
    
    
    public function checkAlso(...args):Boolean
    {
        var t:Boolean = isValid;
        for each (var b:Boolean in args)
        {
            t = t && b;
            if (!t)
                break;
        }
        return t;
    }
    
    private var _needsValidation:Boolean;
    private var _needsSuppressedValidation:Boolean;
    
    override protected function commitProperties():void
    {
        
        if (_needsValidation)
        {
            _needsValidation = false;
            // temporarily disable errors flags
            errorTipManager.increaseSuppressionCount();
            // but validate with error marker dispatch
            validate(false);
            // start showing the problems hereafter
            errorTipManager.decreaseSuppressionCount();
        }
        
        if (_needsSuppressedValidation)
        {
            _needsSuppressedValidation = false;
            
            // temporarily disable errors flags
            errorTipManager.increaseSuppressionCount();
            // validate without error markers
            validate(true);
            // start showing the problems hereafter
            errorTipManager.decreaseSuppressionCount();
        }
        super.commitProperties();
    }
}
}
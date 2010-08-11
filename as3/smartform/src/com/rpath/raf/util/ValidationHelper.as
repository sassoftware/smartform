/*
#
# Copyright (c) 2005-2009 rPath, Inc.
#
# All rights reserved
#
*/

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

package com.rpath.raf.util
{    
    import com.rpath.raf.views.SmartFormItem;
    
    import flash.events.Event;
    import flash.events.IEventDispatcher;
    import flash.events.MouseEvent;
    import flash.utils.Dictionary;
    
    import mx.binding.utils.BindingUtils;
    import mx.binding.utils.ChangeWatcher;
    import mx.core.UIComponent;
    import mx.events.FlexEvent;
    import mx.events.ValidationResultEvent;
    import mx.managers.ToolTipManager;
    import mx.utils.ArrayUtil;
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
    public class ValidationHelper extends LifecycleObject
    {
        
        public function ValidationHelper(vals:Array=null, 
                                         target:IEventDispatcher=null, 
                                         property:String="isValid", 
                                         errorTipManager:ErrorTipManager=null)
        {
            super();
            
            this.property = property;
            this.target = target;
            
            if (!errorTipManager)
            {
                errorTipManager = new ErrorTipManager();
                // start off not displaying anything
                errorTipManager.suppressErrors = true;
            }
            
            this.errorTipManager = errorTipManager;
            
            // do this last, since it wires up errorTipManager as a side effect
            validators = vals;
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
                target.dispatchEvent(new FlexEvent(_isValid ? FlexEvent.VALID : FlexEvent.INVALID));
            }
        }

        private var property:String;
                
        // we use a further helper instance to pop errorTips
        private var _errorTipManager:ErrorTipManager;
        
        public function get errorTipManager():ErrorTipManager
        {
            return _errorTipManager;
        }
        
        public function set errorTipManager(value:ErrorTipManager):void
        {
            _errorTipManager = value;
            // now inform it of all our validators
            for (var v:* in _vals)
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
                _target.removeEventListener(Event.CLOSE, handleTargetRemovedFromStage);
                _target.removeEventListener(FlexEvent.HIDE, handleTargetRemovedFromStage);
                _target.removeEventListener(Event.REMOVED_FROM_STAGE, handleTargetRemovedFromStage);
            }

            _target = v;
            
            if (_target)
            {
                _target[property] = isValid;
                
                _target.addEventListener(Event.CLOSE, handleTargetRemovedFromStage,false,0,true);
                _target.addEventListener(FlexEvent.HIDE, handleTargetRemovedFromStage,false,0,true);
                _target.addEventListener(Event.REMOVED_FROM_STAGE, handleTargetRemovedFromStage,false,0,true);
            }
        }
        
        private function handleTargetRemovedFromStage(event:Event):void
        {
            // remove all the error tips
            if (event.target == target)
            {
                errorTipManager.reset();
            }
        }
        
        private var _validators:Dictionary = new Dictionary(true);
        
        // _vals is a partition of actual Validator instances
        private var _vals:Dictionary = new Dictionary(true);
        
        // _others is a partition of non-Validator instances we're also
        // monitoring as part of the total validation set
        private var _others:Dictionary = new Dictionary(true);
        
        public function addValidator(v:IEventDispatcher):void
        {
            var validator:Validator = v as Validator;
            if (validator)
            {
                _vals[validator] = true;
                setupListeners(validator);
                if (errorTipManager)
                    errorTipManager.registerValidator(validator);
            }
            else 
            {
                // if (v is ValidationHelper) should we do anything extra in nested case?
                _others[v] = true;
                setupListeners(v);
            }
        }
        
        public function removeValidator(v:IEventDispatcher):void
        {
            if (v is IEventDispatcher)
            {
                removeListeners(v);
            }
            
            var validator:Validator = v as Validator;
            if (validator)
            {
                errorTipManager.unregisterValidator(validator);
            }
            
            // clean up our various partitioned validators
            delete _others[v];
            delete _vals[v];
            delete _validators[v];
        }
        
        public function reset():void
        {
            for each (var v:IEventDispatcher in validators)
            {
                removeValidator(v);
            }
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
        
        private function getKeys(map:Dictionary) : Array
        {
            var keys:Array = [];
            
            for (var key:* in map)
            {
                keys.push( key );
            }
            return keys;
        }
        
        public function get validators():Array
        {
            return getKeys(_validators);
        }
        
        public function set validators(vals:Array):void
        {
            var v:*;
            
            reset();
            
            for each (v in vals)
            {
                // allow for nested sets
                if (v is Array)
                {
                    for each (var v2:* in v)
                    {
                        addValidator(v2);
                    }
                }
                else
                {
                    addValidator(v);
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
                
                if (v && v.enabled)
                {
                    // Validate with event dispatch so that we and our errorTip
                    // manager get to hear the events.
                    var resultEvent:ValidationResultEvent = v.validate(null, suppressEvents);
                    
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
            
        public function handleItemValidationEvent(event:Event):void
        {
            // plain FlexEvent is the way a UIComponent reports it's validity
            // typically after setting errorString on itself
            if (event is FlexEvent)
            {
                // make a note of the source of the event since we should
                // check this object directly in computing valid status
                addValidator(event.target as IEventDispatcher);
                
                // and recompute our own validity
                _needsValidation = true;
                invalidateProperties();
            }
            // ValidationResultEvents are sent by Validators to report their
            // assessment of a source items validity. We're inserted in the 
            // middle of this chain
            else if (event is ValidationResultEvent && !_validating)
            {
                var newValid:Boolean = true;
                
                _validationStates[event.target] = (event.type == ValidationResultEvent.VALID);
                
                var validators:Array = getKeys(_validationStates);
                
                //r ecompute validity from the cache
                for each (var v:Validator in validators)
                {
                    newValid = newValid && _validationStates[v];
                }
                
                isValid = newValid;
            }
        }

        
        public function validateNow(suppressEvents:Boolean=false):void
        {
            if (!_validating)
            {
                _validating = true;
                
                var valid:Boolean = false;
                
                var results:Array = checkValidity(getKeys(_vals), suppressEvents);
                
                valid = (results.length == 0);
                
                // now all the "others"
                for (var v:* in _others)
                {
                    if (v is ValidationHelper)
                    {
                        var subhelper:ValidationHelper = v as ValidationHelper;
                        subhelper.validateNow(suppressEvents);
                    }
                    else if (v is SmartFormItem)
                    {
                        var item:SmartFormItem = v as SmartFormItem;
                        item.validate(suppressEvents);
                    }
                    
                    if (v.hasOwnProperty("isValid"))
                    {
                        valid = valid && v["isValid"];
                    }
                    else if (v.hasOwnProperty("valid"))
                    {
                        valid = valid && v["valid"];
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
            validateNow(false);
            errorTipManager.showAllErrorTips();
        }
        
        public function hideErrors():void
        {
            errorTipManager.hideAllErrorTips();
           // but still allow new errors to pop
            errorTipManager.suppressErrors = false;
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
            super.commitProperties();
            
            if (_needsValidation)
            {
                _needsValidation = false;
                // temporarily disable errors flags
                errorTipManager.suppressErrors = false;
                // but validate with error marker dispatch
                validateNow(false);
                // start showing the problems hereafter
                errorTipManager.suppressErrors = false;
            }
            
            if (_needsSuppressedValidation)
            {
                _needsSuppressedValidation = false;

                // temporarily disable errors flags
                errorTipManager.suppressErrors = true;
                // validate without error markers
                validateNow(true);
                // start showing the problems hereafter
                errorTipManager.suppressErrors = false;
            }
        }
    }
}
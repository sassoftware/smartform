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
    import flash.events.IEventDispatcher;
    import flash.events.MouseEvent;
    import flash.utils.Dictionary;
    
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;
    import mx.managers.ToolTipManager;
    import mx.validators.Validator;
    import mx.binding.utils.BindingUtils;
    import mx.binding.utils.ChangeWatcher;
    import mx.utils.ArrayUtil;
    
    
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
    public class ValidationHelper
    {

        /** isValid indicates whether this ValidationHelper as a whole is
        * valid. This is also bound to the target.property (if provided)
        */
        
        public var isValid:Boolean;

        public function ValidationHelper(vals:Array=null, target:*=null, property:String=null, errorTipManager:ErrorTipManager=null)
        {
            super();
            
            this.property = property;
            this.target = target;
            
            this.errorTipManager = errorTipManager;

            // do this last, since it wires up errorTipManager as a side effect
            validators = vals;
        }
        
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


        private var cw:ChangeWatcher;
        private var property:String;
        
        private function bindTargetProperty(targetObj:*, property:*=null):void
        {
            if (_target && cw)
            {
                cw.unwatch();
                cw = null;
            }
            
            _target = targetObj;
            
            if (!property)
                property = "isValid";
            
            if (_target)
                cw = BindingUtils.bindProperty(_target, property, this, ["isValid"], true, true);
        }
        
        public function get target():*
        {
            return _target;
        }
        
        private var _target:*;
        
        public function set target(v:*):void
        {
            bindTargetProperty(v, property);
        }
        
        private var _validators:Dictionary = new Dictionary(true);
        
        // _vals is a partition of actual Validator instances
        private var _vals:Dictionary = new Dictionary(true);
        
        // _others is a partition of non-Validator instances we're also
        // monitoring as part of the total validation set
        private var _others:Dictionary = new Dictionary(true);
        
        
        public function addValidator(v:IEventDispatcher):void
        {
            if (v is Validator)
            {
                _vals[v] = true;
                setupListeners(v);
                if (errorTipManager)
                    errorTipManager.registerValidator(v as Validator);
            }
            else if (v is ValidationHelper)
            {
                // should we do anything extra in nested case?
                _others[v] = true;
                setupListeners(v);
            }
            else
            {
                _others[v] = true;
                setupListeners(v);
            }
            
        }
        
        public function removeValidator(v:IEventDispatcher):void
        {
            if (v is IEventDispatcher)
            {
                v.removeEventListener(ValidationResultEvent.VALID, validateNow);
                v.removeEventListener(ValidationResultEvent.INVALID, validateNow);
            }
            
            errorTipManager.unregisterValidator(v as Validator);
            
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
            v.addEventListener(ValidationResultEvent.VALID, validateNow,false,0,true);
            v.addEventListener(ValidationResultEvent.INVALID, validateNow,false,0,true);
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
            validateNow();
        }
        
        public function get showErrorsImmediately():Boolean
        {
            return _showErrorsImmediately;
        }

        private var _showErrorsImmediately:Boolean = false;

        public function set showErrorsImmediately(value:Boolean):void
        {
            if (_showErrorsImmediately)
            {
                errorTipManager.hideAllErrorTips();
            }
            
            _showErrorsImmediately = value;
            
            if (_showErrorsImmediately)
            {
                errorTipManager.showAllErrorTips();
            }
        }

        
        /**
         *  Shows the tip immediately when the toolTip or errorTip property 
         *  becomes non-null and the mouse is over the target.
         */
        public function showErrorImmediately(target:UIComponent):void
        {
            if (showErrorsImmediately)
            {
                // we have to callLater this to avoid other fields that send events
                // that reset the timers and prevent the errorTip ever showing up.
                target.callLater(showDeferred, [target]);
            }
        }
        
        private function showDeferred(target:UIComponent):void
        {
            var oldShowDelay:Number = ToolTipManager.showDelay;
            ToolTipManager.showDelay = 0;
            if (target.visible)
            {
                // try popping the resulting error flag via the hack 
                // courtesy Adobe bug tracking system
                target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OUT));
                target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OVER));
            }
            ToolTipManager.showDelay = oldShowDelay;
        }
        
        public function clearErrorImmediately(target:UIComponent):void
        {
            target.callLater(clearDeferred, [target]);
        }
        
        private function clearDeferred(target:UIComponent):void
        {
            var oldDelay:Number = ToolTipManager.hideDelay;
            ToolTipManager.hideDelay = 0;
            if (target.visible)
            {
                // clear the errorTip
                try
                {
                    target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OVER));
                    target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OUT));
                }
                catch (e:Error)
                {
                    // sometimes things aren't initialized fully when we try that trick
                }
            }
            ToolTipManager.hideDelay = oldDelay;
        }
        
        
        private var _validating:Boolean;
        
        public function validateNow(...args):void
        {
            if (!_validating)
            {
                _validating = true;
                
                var valid:Boolean = false;
                
                // only pop errorTips if desired
                errorTipManager.showErrorsImmediately = showErrorsImmediately;
                
                var results:Array = Validator.validateAll(getKeys(_vals));
                
                valid = (results.length == 0);
                
                // now all the "others"
                for (var v:* in _others)
                {
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
                
                if (showErrorsImmediately)
                {
                    errorTipManager.showAllErrorTips();
                }
                
                isValid = valid;
            }
        }
        
        public function showErrors():void
        {
            errorTipManager.showAllErrorTips();
        }
        
        public function hideErrors():void
        {
            errorTipManager.hideAllErrorTips();
        }
        
        public function OLDvalidateNow(...args):void
        {
            if (!_validating)
            {
                _validating = true;

                var invalidValidators:Array = [];
                
                var seen:Dictionary = new Dictionary();
                var validationEvent:ValidationResultEvent;
                var v:Validator;
                var vt:Object;
                
                // first test all validators, looking for invalid ones
                for each (v in _vals)
                {
                    if (v.enabled)
                    {
                        vt = v.listener ? v.listener : v.source;
                        if (vt && seen[vt] == undefined)
                        {
                            // careful not to send events!
                            validationEvent = v.validate(null,true);
                            if (validationEvent && validationEvent.type != ValidationResultEvent.VALID)
                            {
                                invalidValidators.push(v);
                                seen[vt] = validationEvent;
                                
                                // send failures right away
                                try
                                {
                                    vt.validationResultHandler(seen[vt]);
                                    showErrorImmediately(vt as UIComponent);
                                }
                                catch (e:Error)
                                {
                                }
                            }
                        }
                    }
                }
                
                // now all the valid validators that we haven't seen invalid 
                // make sure we send a VALID event
                for each (v in _vals)
                {
                    if (v.enabled)
                    {
                        vt = v.listener ? v.listener : v.source;
                        if (vt && seen[vt] == undefined)
                        {
                            seen[vt] = true;
                            try
                            {
                                vt.validationResultHandler(new ValidationResultEvent(ValidationResultEvent.VALID));
                                // make sure we clear any error flag
                                clearErrorImmediately(vt as UIComponent);
                            }
                            catch (e:Error)
                            {
                            }
                        }
                    }
                }
                 
                // are we valid overall?
                var valid:Boolean;
                valid = invalidValidators.length == 0;
                
                // now check the others
                
                for each (var item:* in _others)
                {
                    if (item.hasOwnProperty("isValid"))
                    {
                        valid = valid && item["isValid"];
                    }
                    else if (item.hasOwnProperty("valid"))
                    {
                        valid = valid && item["valid"];
                    }
                    
                }
                
                _validating = false;
                isValid = valid;
            }
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
    
    }
}
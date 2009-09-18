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
    
    import mx.binding.utils.BindingUtils;
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;
    import mx.managers.ToolTipManager;
    import mx.validators.Validator;
    
    [Bindable]
    public class ValidationHelper
    {
        public function ValidationHelper(vals:Array=null, target:*=null, property:String=null)
        {
            if (target && property)
                BindingUtils.bindProperty(target, property, this, ["isValid"]);
            
            validators = vals;
        }

        public var isValid:Boolean;
        
        public function get validators():Array
        {
            return _validators;
        }
        
        private var _validators:Array;
        private var _vals:Array;
        private var _others:Array;
        
        public function set validators(vals:Array):void
        {
            var v:*;
            
            for each (v in _validators)
            {
                if (v is IEventDispatcher)
                {
                    v.removeEventListener(ValidationResultEvent.VALID, validateNow);
                    v.removeEventListener(ValidationResultEvent.INVALID, validateNow);
                }
            }
            
            _validators = vals;
            _vals = [];
            _others = [];
            
            for each (v in _validators)
            {
                if (v is Validator)
                {
                    _vals.push(v);
                    setupListeners(v);
                }
                else if (v is Array)
                {
                    for each (var v2:* in v)
                    {
                        if (v2 is Validator)
                        {
                            _vals.push(v2);
                        }
                        else
                        {
                            _others.push(v2);
                        }
                        setupListeners(v2);
                    }
                }
                else
                {
                    _others.push(v);
                    setupListeners(v);
                }
                
            }

            validateNow();
        }
        
        protected function setupListeners(v:IEventDispatcher):void
        {
            v.addEventListener(ValidationResultEvent.VALID, validateNow);
            v.addEventListener(ValidationResultEvent.INVALID, validateNow);
        }

        /**
         *  @private
         *  Shows the tip immediately when the toolTip or errorTip property 
         *  becomes non-null and the mouse is over the target.
         */
        public function showErrorImmediately(target:UIComponent):void
        {
            // we have to callLater this to avoid other fields that send events
            // that reset the timers and prevent the errorTip ever showing up.
            target.callLater(showDeferred, [target]);
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
            var oldDelay:Number = ToolTipManager.hideDelay;
            ToolTipManager.hideDelay = 0;
            if (target.visible)
            {
                // clear the errorTip
                target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OVER));
                target.dispatchEvent(new MouseEvent(MouseEvent.MOUSE_OUT));
            }
            ToolTipManager.hideDelay = oldDelay;
        }
        
        
        private var _validating:Boolean;
        
        public function validateNow(...args):void
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
/*
#
# Copyright (c) 2009-2010 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

/*
    Based on an example for Flex 3 posted at:
    Blog entry: http://flexdevtips.blogspot.com/2009/08/always-showing-error-tips-validators.html -->

 */


package com.rpath.raf.util
{
    import flash.display.DisplayObject;
    import flash.display.DisplayObjectContainer;
    import flash.events.Event;
    import flash.events.IEventDispatcher;
    import flash.geom.Point;
    import flash.geom.Rectangle;
    import flash.utils.Dictionary;
    import flash.utils.clearTimeout;
    import flash.utils.setTimeout;
    
    import mx.controls.ToolTip;
    import mx.core.IChildList;
    import mx.core.IInvalidating;
    import mx.core.IToolTip;
    import mx.core.UIComponent;
    import mx.events.FlexEvent;
    import mx.events.MoveEvent;
    import mx.events.ResizeEvent;
    import mx.events.ScrollEvent;
    import mx.events.ToolTipEvent;
    import mx.events.ValidationResultEvent;
    import mx.managers.SystemManager;
    import mx.managers.ToolTipManager;
    import mx.styles.IStyleClient;
    import mx.validators.Validator;
    
    
    /**
     * This class makes the error ToolTip shown up all the time instead of 
     * just when the mouse is over the target component.
     * It is designed to work with a Validator control, but you can manually use this class
     * by calling the showErrorTip() and hideErrorTip() functions too.
     * <br>
     * When the showErrorTip(target:Object, error:String) function is called, if the error String is null and
     * the target is a UIComponent then the UIComponent.errorString property is used in the error tip.
     * <br>
     * Here are some more resources on the issue:<br>
     * <li><a href="http://bugs.adobe.com/jira/browse/SDK-11256">Adobe Bug Tracker</a></li>
     * <li><a href="http://aralbalkan.com/1125">Aral Balkan - Better form validation in Flex</a></li>
     * <li><a href="http://blog.flexmonkeypatches.com/2007/09/17/using-the-flex-tooltip-manager-to-create-error-tooltips-and-position-them/">Creating Error Tooltips</a></li>
     * 
     * @author Chris Callendar
     * @date August 5th, 2009
     * 
     * Extensively modified by Brett Adam to support Flex 4 among other changes.
     * Now used in conjunction with the smartform/ValidationHelper classes.
     * 
     */
    [Bindable]
    public class ErrorTipManager
    {
        
        public function ErrorTipManager():void
        {
            super();
        }
        
        
        // maps the target components to the error IToolTip components
        private var errorTips:Dictionary = new Dictionary(true); 
        // maps the validators to a boolean indicating whether the toolTipShown event listener has been
        // added to the validator source property.
        private var validators:Dictionary = new Dictionary(true);
        // maps the popUps to an Array of validators
        private var popUps:Dictionary = new Dictionary(true);
        // maps the parent containers to an Array of validator source components
        private var containersToTargets:Dictionary = new Dictionary(true);
        
        /** suppressErrors allows you to control whether validation events pop
        * errors message as they occur or not
        */
        private function get suppressErrors():Boolean
        {
            return _suppressErrors;
        }
        
        private var _suppressErrors:Boolean = true;
        public var suppressionCount:int = 0;  // start off suppressed
        
        private function set suppressErrors(b:Boolean):void
        {
            _suppressErrors = b;
        }
        
        public function increaseSuppressionCount():void
        {
            suppressionCount++;
            suppressErrors = true;
        }
        
        public function decreaseSuppressionCount():void
        {
            suppressionCount--;
            if (suppressionCount <= 0)
            {
                suppressionCount = 0;
                suppressErrors = false;
            }
        }
        
        /** showAllErrors controls whether all errors should be shown
        * and scrolling should reveal errors, etc.
        */
        private var _showAllErrors:Boolean = false;

        public function get showAllErrors():Boolean
        {
            return _showAllErrors;
        }

        public function set showAllErrors(value:Boolean):void
        {
            _showAllErrors = value;
            if (showAllErrors)
            {
                suppressErrors = false;
            }
        }
        
        /**
         * Adds "invalid" and "valid" event listeners which show and hide the error tooltips.
         */
        public function registerValidator(validator:Validator):void {
            validator.addEventListener(ValidationResultEvent.VALID, validValidationHandler, false, 0, true);
            validator.addEventListener(ValidationResultEvent.INVALID, invalidValidationHandler, false, 0, true);
            validators[validator] = false;
            
            // Also listen for when the real mouse over error tooltip is shown 
            addValidatorSourceListeners(validator);
            
            // do we already have errorTips for this validators source or listener?
            // if so, show them (resume/scroll back into view case)
            unhideErrorTip(validator.source);
            unhideErrorTip(validator.listener);
        }
        
        /**
         * Removes the "invalid" and "valid" event listeners from the validator.
         * Also removes the error tip.
         */
        public function unregisterValidator(validator:Validator):void {
            if (!validator)
                return;
            
            validator.removeEventListener(ValidationResultEvent.VALID, validValidationHandler);
            validator.removeEventListener(ValidationResultEvent.INVALID, invalidValidationHandler);
            // make sure our error tooltip is hidden
            hideErrorTip(validator.source);
            hideErrorTip(validator.listener);
            // stop listening for events on the validator's source
            removeValidatorSourceListeners(validator);
        }
        
        /** removes all validators and listeners. Cleanup
        */
        
        public function reset():void
        {
            // remove all errorTips
            removeAllErrorTips();

            // unregister all validators
            for (var v:* in validators)
            {
                var validator:Validator = v as Validator;

                unregisterValidator(validator);
                // make sure our error tooltip is actually removed
                removeErrorTip(validator.source);
                removeErrorTip(validator.listener);
            }
            
        }
        
        
        /**
         * Registers the validator (see registerValidator), and adds MOVE and RESIZE listeners
         * on the popUp component to keep the error tip positioned properly.
         * It can also hide all existing error tips which is a good idea when showing a popUp
         * because the error tips will appear on top of the popUp window.
         * @param validator the validator to register
         * @param popUp the popUp component which will have move and resize listeners added to
         * @param hideExistingErrorTips if true then all existing error tips will be hidden
         */
        public function registerValidatorOnPopUp(validator:Validator, popUp:UIComponent, 
                                                        hideExistingErrorTips:Boolean = false):void {
            // hide all existing error tips to prevent them from being on top of the popUp
            if (hideExistingErrorTips) {
                hideAllErrorTips();
            }
            registerValidator(validator);
            if (popUps[popUp] == null) {
                popUps[popUp] = [];
                // add move/resize listeners on the popUp to keep the error tip positioned properly
                popUp.addEventListener(MoveEvent.MOVE, targetMoved, false, 0, true);
                popUp.addEventListener(ResizeEvent.RESIZE, targetMoved, false, 0, true);
            }
            var validators:Array = (popUps[popUp] as Array);
            if (validators.indexOf(validator) == -1) { 
                validators.push(validator);
            }
        }
        
        /**
         * Unregisters all the validators that are associated with the given popup.
         * Also removes the MOVE and RESIZE listeners on the popUp.
         * It can also re-validate all existing validators which will show the error tips if necessary. 
         * @param popUp the popUp component which will have move and resize listeners added to
         * @param validateExistingErrorTips if true then all other validators will be validated
         */
        public function unregisterPopUpValidators(popUp:UIComponent, validateExistingErrorTips:Boolean = false):void {
            if (popUps[popUp] != null) {
                var validators:Array = (popUps[popUp] as Array);
                for each (var validator:Validator in validators) {
                    unregisterValidator(validator);
                }
                delete popUps[popUp];
                // remove the move/resize listeners on the popUp
                popUp.removeEventListener(MoveEvent.MOVE, targetMoved);
                popUp.removeEventListener(ResizeEvent.RESIZE, targetMoved);
            }
            // show any error tips that were showing before the popUp was shown
            if (validateExistingErrorTips) {
                validateAll();
            }
        }
        
        /**
         * Adds the ToolTipEvent.TOOL_TIP_SHOW event listener on the validator's source
         * only if it hasn't already been added.
         */
        private function addValidatorSourceListeners(validator:Validator):void {
            // make sure the listeners have been added
            if (validator) {
                var alreadyAdded:Boolean = validators[validator];
                if (!alreadyAdded)
                {
                    validators[validator] = true;
                    addComponentListeners(validator.source);
                    if (validator.source != validator.listener)
                        addComponentListeners(validator.listener);
                }
            }
        }
        
        private var listened:Dictionary = new Dictionary(true);
        
        public function addComponentListeners(source:*):void
        {
            var ed:IEventDispatcher = (source as IEventDispatcher);
            if (ed && !listened[ed])
            {
                listened[ed] = true;
                // need to listener for when the real tooltip gets shown 
                // we'll hide it if is an error tooltip since we are already showing it 
                ed.addEventListener(ToolTipEvent.TOOL_TIP_SHOWN, toolTipShown, false, 0, true);
                // also need to listen for move and resize events to keep the error tip positioned correctly
                ed.addEventListener(MoveEvent.MOVE, targetMoved, false, 0, true);
                ed.addEventListener(ResizeEvent.RESIZE, targetMoved, false, 0, true);
                ed.addEventListener(FlexEvent.HIDE, targetHidden, false, 0, true);
                ed.addEventListener(FlexEvent.REMOVE, targetRemoved, false, 0, true);
                ed.addEventListener(Event.REMOVED_FROM_STAGE, targetRemoved, false, 0, true);
                ed.addEventListener(FlexEvent.VALID, validHandler, false, 0, true);
                ed.addEventListener(FlexEvent.INVALID, invalidHandler, false, 0, true);
                
                // listen for scroll events on the parent containers
                if (source is DisplayObject) {
                    var obj:DisplayObject = (source as DisplayObject);
                    var parent:DisplayObjectContainer = obj.parent;
                    while (parent) {
                        
                        //TODO: add in code here to auto discover that we're in a 
                        // POPUP window and add the required event listeners 
                        // to handle the popup moving around the screen (user drag)
                        
                        if (parent is DisplayObjectContainer) {
                            parent.addEventListener(ScrollEvent.SCROLL, parentContainerScrolled, false, 0, true);
                            parent.addEventListener(MoveEvent.MOVE, parentContainerMoved, false, 0, true);
                            if (!(containersToTargets[parent] is Array)) {
                                containersToTargets[parent] = [];
                            }
                            var array:Array = (containersToTargets[parent] as Array);
                            if (array.indexOf(obj) == -1) {
                                array.push(obj);
                            }
                        }
                        parent = parent.parent;
                    }
                }
            }            
        }
        
        
        /**
         * Removes the event listeners that were added to the validator's source.
         */
        private function removeValidatorSourceListeners(validator:Validator):void {
            if (validator && (validators[validator] == true)) {
                removeComponentListeners(validator.source);
                removeComponentListeners(validator.listener);
                delete validators[validator];
            }
        }
        
        public function removeComponentListeners(source:*):void
        {
            var ed:IEventDispatcher = (source as IEventDispatcher);
            if (ed && listened[ed])
            {
                delete listened[ed];
                ed.removeEventListener(ToolTipEvent.TOOL_TIP_SHOWN, toolTipShown);
                ed.removeEventListener(MoveEvent.MOVE, targetMoved);
                ed.removeEventListener(ResizeEvent.RESIZE, targetMoved);
                ed.removeEventListener(FlexEvent.HIDE, targetHidden);
                ed.removeEventListener(FlexEvent.REMOVE, targetRemoved);
                ed.removeEventListener(Event.REMOVED_FROM_STAGE, targetRemoved);
                ed.removeEventListener(FlexEvent.VALID, validHandler);
                ed.removeEventListener(FlexEvent.INVALID, invalidHandler);
                
                if (source is DisplayObject) {
                    var obj:DisplayObject = (source as DisplayObject);
                    var parent:DisplayObjectContainer = obj.parent;
                    while (parent) {
                        if (parent is DisplayObjectContainer) {
                            parent.removeEventListener(ScrollEvent.SCROLL, parentContainerScrolled);
                            parent.removeEventListener(MoveEvent.MOVE, parentContainerMoved);
                            if (containersToTargets[parent] is Array) {
                                var array:Array = (containersToTargets[parent] as Array);
                                var index:int = array.indexOf(obj);
                                if (index != -1) {
                                    array.splice(index, 1);
                                    containersToTargets[parent] = array;
                                }
                            }
                        }
                        parent = parent.parent;
                    }
                }
            }
        }
        
        /**
         * Called when the validator fires the valid event.
         * Hides the error tooltip if it is visible.
         */
        public function validValidationHandler(event:ValidationResultEvent):void {
            // the target component is valid, so hide the error tooltip
            var validator:Validator = Validator(event.target); 
/*            removeErrorTip(validator.source);
*/            // ensure that the source listeners were added 
            addValidatorSourceListeners(validator);
        }
        
        /**
         * Called when the validator fires an invalid event.
         * Shows the error tooltip with the ValidatorResultEvent.message as the error String.
         */
        public function invalidValidationHandler(event:ValidationResultEvent):void {
            // the target component is invalid, so show the error tooltip 
            var validator:Validator = Validator(event.target); 
/*            
            // always create the errorTip
            createErrorTip(validator.source, event.message);
            
            // only show if requested
            if (!suppressErrors)
                showErrorTip(validator.source, event.message);
            
*/            // ensure that the source listeners were added 
            addValidatorSourceListeners(validator);
        }

        /**
         * Called when the validator fires the valid event.
         * Hides the error tooltip if it is visible.
         */
        public function validHandler(event:FlexEvent):void {
            // the target component is valid, so hide the error tooltip
            removeErrorTip(event.target);
        }
        
        /**
         * Called when the validator fires an invalid event.
         * Shows the error tooltip with the ValidatorResultEvent.message as the error String.
         */
        public function invalidHandler(event:FlexEvent):void {
            // the target component is invalid, so show the error tooltip 
            
            // always create the errorTip
            createErrorTip(event.target, event.target.errorString);
            
            // only show if requested
            if (!suppressErrors)
                showErrorTip(event.target, event.target.errorString);
        }

        
        // TODO: make this also work for Spark viewport scrolling which DO NOT
        // appear to dispatch SCROLL events. Instead, we need to listen for 
        // PropertChange events on the verticalScrollPosition and horizontalScrollPosition
        // properties and react accordingly. <sigh>
        
        private function parentContainerScrolled(event:ScrollEvent):void {
            var parent:DisplayObjectContainer = (event.target as DisplayObjectContainer);
            if (parent && (containersToTargets[parent] is Array)) {
                var targets:Array = (containersToTargets[parent] as Array);
                if (targets && (targets.length > 0)) {
                    // need to wait a fraction of a second for the scroll event to be finished
                    // and the each targets position to be updated
                    var id:uint = setTimeout(function():void {
                        clearTimeout(id);
                        for each (var target:DisplayObject in targets) {
                            // make sure the source target is actually visible (not scrolled out of the view)
                            var pt:Point = target.localToGlobal(new Point());
                            pt = parent.globalToLocal(pt);
                            if ((pt.x < 0) || (pt.y < 0) || 
                                ((pt.x + target.width) > parent.width) || 
                                ((pt.y + target.height) > parent.height)) {
                                // the source component isn't fully visible, so hide the error tip 
                                hideErrorTip(target);
                            } else {
                                // re-position the error tip, also will make it visible if it was hidden
                                updateErrorTipPosition(target, showAllErrors);
                            }
                        }
                    }, 50);
                }
            }
        }
        
        private function parentContainerMoved(event:MoveEvent):void 
        {
            var parent:DisplayObjectContainer = (event.target as DisplayObjectContainer);
            
            // move all errors tips that are related to objects parented by this parent
            // TODO: how to figure out which ones?
            
            // for now, just move everything
            for (var target:* in errorTips)
            {
                positionErrorTip(errorTips[target], target);
            }
            
        }
            
        /**
         * When a target is hidden, then make sure the error tip is hidden too.
         */
        private function targetHidden(event:FlexEvent):void {
            var target:DisplayObject = (event.target as DisplayObject);
            hideErrorTip(target, true);
        }
        
        /**
         * When a target is removed, then make sure the error tip is hidden too.
         */
        private function targetRemoved(event:Event):void {
            var target:DisplayObject = (event.target as DisplayObject);
            removeErrorTip(target, true);
        }
        
        /**
         * When the target component moves or is resized we need to keep the 
         * error tip in the correct position.
         */
        private function targetMoved(event:Event):void {
            var target:DisplayObject = (event.target as DisplayObject);
            // check if the target is actually a popUp, in which case we get the real
            // target from the validator source
            if (popUps[target] != null) {
                var validators:Array = (popUps[target] as Array);
                for each (var validator:Validator in validators) { 
                    var source:DisplayObject = (validator.source as DisplayObject);
                    handleTargetMoved(source);
                }
            } else {
                handleTargetMoved(target);
            }
        }
        
        private function handleTargetMoved(target:DisplayObject):void {
            if (target is UIComponent) {
                // need to wait for move/resize to finish
                UIComponent(target).callLater(updateErrorTipPosition, [ target, showAllErrors ]);
            } else {
                updateErrorTipPosition(target, showAllErrors);
            }
        }
        
        /**
         * Moves the error tip for the given target.
         * It can also make it visible if the error tip exists but is hidden. 
         */
        public function updateErrorTipPosition(target:Object, makeVisible:Boolean = false):void {
            var errorTip:IToolTip = getErrorTip(target);
            if (errorTip) {
                if (makeVisible && !errorTip.visible) {
                    errorTip.visible = true;
                }
                positionErrorTip(errorTip, target as DisplayObject);
            }
        }
        
        /**
         * This gets called when the mouse hovers over the target component 
         * and a tooltip is shown - either a normal tooltip or an error tooltip.
         * If the tooltip is an error tooltip and our error tooltip is already showing
         * then we hide this new tooltip immediately.
         */
        private function toolTipShown(event:ToolTipEvent):void {
            // hide our error tip until this tooltip is hidden
            var style:Object = ToolTip(event.toolTip).styleName;
            var errorTip:IToolTip = getErrorTip(event.target);
            if ((style == "errorTip")) //&& (errorTip != null))
            {
                // register the target for later cleanup
                addComponentListeners(event.target);
                
                // hide this tooltip, ours is already displaying (or is about to display)
                event.toolTip.visible = false;
                event.toolTip.width = 0;
                event.toolTip.height = 0;
                event.currentTarget.dispatchEvent(new ToolTipEvent(ToolTipEvent.TOOL_TIP_HIDE, false, false, event.toolTip));
            }
        }
        
        /**
         * Gets the cached IToolTip object for the given target.
         */
        public function getErrorTip(target:Object):IToolTip {
            return (target ? errorTips[target] as IToolTip : null);
        }
        
        /**
         * Determines if the error tooltip exists and if it is visible.
         */
        public function isErrorTipVisible(target:Object):Boolean {
            var errorTip:IToolTip = getErrorTip(target);
            return (errorTip && errorTip.visible);
        }
        
        /**
         * Creates the error IToolTip object if one doesn't already exist for the given target.
         * If the error tooltip already exists then the error string is updated on the existing tooltip.
         * The tooltip will not be shown if the error (or errorString) is blank. 
         * @param target the target component (usually a UIComponent)
         * @param error the optional error String, if null and the target is a UIComponent then 
         *  the target.errorString property is used.
         */
        public function createErrorTip(target:Object, error:String = null):IToolTip {
            var errorTip:IToolTip = null;
            var position:Point;
            
            // always listen for subsequent lifecycle changes
            addComponentListeners(target);
            
            if (target) {
                // use the errorString property on the target
                if (!error && (target is UIComponent)) {
                    error = (target as UIComponent).errorString;
                }
                errorTip = getErrorTip(target);
                if (!errorTip) {
                    if ((error != null) && (error.length > 0)) {
                        position = getErrorTipPosition(target as DisplayObject);
                        errorTip = ToolTipManager.createToolTip(error, position.x, position.y);
                        errorTips[target] = errorTip;
                        
                        sizeErrorTip(errorTip);
                        // update the position (handles the tooltip going offscreen)
                        positionErrorTip(errorTip, target as DisplayObject);
                        
                        // set the styles to match the real error tooltip 
                        var tt:ToolTip = ToolTip(errorTip);
                        tt.styleName = "errorTip";
                        
                        errorTip.visible = showAllErrors;
                    } 
                } else if (error && (error != errorTip.text)) {
                    // update the error tooltip text
                    errorTip.text = error;
                    // update the position too
                    //position = getErrorTipPosition(target as DisplayObject);
                    //errorTip.move(position.x, position.y);
                    positionErrorTip(errorTip, target as DisplayObject);
                }
            }
            return errorTip;
        }
        
        /**
         * Gets the position for the tooltip in global coordinates.
         */
        private function getErrorTipPosition(target:DisplayObject):Point {
            // position the error tip to be in the exact same position as the real error tooltip
            var pt:Point = new Point();
            if (target) {
                // need to get the position of the target in global coordinates 
                var global:Point = target.localToGlobal(new Point(0, 0));
                // position on the right side of the target
                pt.x = global.x + target.width + 4;
                pt.y = global.y - 1;
            } 
            return pt;
        }
        
        /**
         * Gets the position for the error tip. 
         * Copied from ToolTipManagerImpl.positionTip()
         */
        private function positionErrorTip(errorTip:IToolTip, target:DisplayObject, bringInFront:Boolean = true):void {
            if (!errorTip || !target) {
                return;
            }
            var x:Number;
            var y:Number;
            
            var screenWidth:Number = errorTip.screen.width;
            var screenHeight:Number = errorTip.screen.height;
            var upperLeft:Point = new Point(0, 0);
            upperLeft = target.localToGlobal(upperLeft);
            upperLeft = errorTip.root.globalToLocal(upperLeft);
            var targetGlobalBounds:Rectangle = new Rectangle(upperLeft.x, upperLeft.y, target.width, target.height);
            x = targetGlobalBounds.right + 4;
            y = targetGlobalBounds.top - 1;
            var above:Boolean = false;
            
            // If there's no room to the right of the control, put it above or below, 
            // with the left edge of the error tip aligned with the left edge of the target.
            if (x + errorTip.width > screenWidth) {
                var newWidth:Number = NaN;
                var oldWidth:Number = NaN;
                x = targetGlobalBounds.left - 2;
                
                // If the error tip would be too wide for the stage, reduce the maximum width to fit onstage. 
                // Note that we have to reassign the text in order to get the tip to relayout after changing 
                // the border style and maxWidth.
                if (x + errorTip.width + 4 > screenWidth) {
                    newWidth = screenWidth - x - 4;
                    oldWidth = errorTip.maxWidth;
                    setMaxWidth(errorTip, newWidth);
                    if (errorTip is IStyleClient) {
                        IStyleClient(errorTip).setStyle("borderStyle", "errorTipAbove");
                    }
                    errorTip["text"] = errorTip["text"];
                    setMaxWidth(errorTip, oldWidth);
                } else {
                    // Even if the error tip will fit onstage, we still need to change the border style 
                    // and get the error tip to relayout.
                    if (errorTip is IStyleClient) {
                        IStyleClient(errorTip).setStyle("borderStyle", "errorTipAbove");
                    }
                    errorTip["text"] = errorTip["text"];
                }
                
                if (errorTip.height + 2 < targetGlobalBounds.top) {
                    // There's room to put it above the control.
                    above = true;    // wait for the errorTip to be sized before setting y
                } else {
                    // No room above, put it below the control.
                    y = targetGlobalBounds.bottom + 2;
                    setMaxWidth(errorTip, newWidth);
                    if (errorTip is IStyleClient) {
                        IStyleClient(errorTip).setStyle("borderStyle", "errorTipBelow");
                    }
                    errorTip["text"] = errorTip["text"];
                    setMaxWidth(errorTip, oldWidth);
                }
            } else {
                if (errorTip is IStyleClient) {
                    IStyleClient(errorTip).clearStyle("borderStyle");
                }
            }
            
            // Since the border style of the error tip may have changed, we have to force a remeasurement and change 
            // its size. This is because objects in the toolTips layer don't undergo normal measurement and layout.
            sizeErrorTip(errorTip);
            
            // need to do this after the error tip has been sized since the height might have changed
            if (above) {
                y = targetGlobalBounds.top - (errorTip.height + 2);
            }
            
            errorTip.move(x, y);
            
            // move this error tip on top of other error tips
            if (bringInFront) {
                bringToFront(errorTip);
            }
        }
        
        private function setMaxWidth(errorTip:IToolTip, width:Number):void {
            if (!isNaN(width) && (errorTip is UIComponent)) {
                (errorTip as UIComponent).maxWidth = width;
            }
        }
        
        /**
         * Moves the given error tip in front of any other error tips.
         */
        public function bringToFront(errorTip:IToolTip):void {
            var parent:IChildList = (errorTip.parent as IChildList);
            if (parent is SystemManager) {
                parent = (parent as SystemManager).rawChildren;
            }
            var index:int = parent.getChildIndex(errorTip as DisplayObject);
            var children:int = parent.numChildren;
            if (index < (children - 1)) {
                parent.setChildIndex(errorTip as DisplayObject, children - 1);
            }
        }
        
        /**
         * Copied from ToolTipManagerImpl.sizeTip()
         * Objects added to the SystemManager's ToolTip layer don't get automatically measured or sized, 
         * so ToolTipManager has to measure it and set its size.
         */
        private function sizeErrorTip(errorTip:IToolTip):void {
            // Force measure() to be called on the tooltip.  Otherwise, its measured size will be 0.
            if (errorTip is IInvalidating) {
                IInvalidating(errorTip).validateNow();
            }
            errorTip.setActualSize(errorTip.getExplicitOrMeasuredWidth(),
                errorTip.getExplicitOrMeasuredHeight());
        }
        
        /**
         * Creates the error tooltip if it doesn't already exist, and makes it visible.
         */
        public function showErrorTip(target:Object, error:String = null):void {
            var errorTip:IToolTip = createErrorTip(target, error);
            if (errorTip) {
                errorTip.visible = true;
            }
        }

        public function unhideErrorTip(target:Object):void {
            var errorTip:IToolTip = getErrorTip(target);
            if (errorTip) {
                errorTip.visible = true;
            }
        }
        
        /**
         * Hides the existing error tooltip for the target if one exists.
         */ 
        public function hideErrorTip(target:Object, clearErrorString:Boolean = false):void {
            var errorTip:IToolTip = getErrorTip(target);
            if (errorTip) {
                errorTip.visible = false;
            }
            // clear the errorString property to remove the red border around the target control
            if (clearErrorString && target && target.hasOwnProperty("errorString")) {
                target.errorString = "";
            }
        }
        
        /**
         * Hides the error tooltip for the target AND removes it from the
         * ToolTipManager (by calling ToolTipManager.destroyToolTip).
         */
        public function removeErrorTip(target:Object, clearErrorString:Boolean = false):void {
            var errorTip:IToolTip = getErrorTip(target);
            if (errorTip) {
                errorTip.visible = false;
                ToolTipManager.destroyToolTip(errorTip);
                delete errorTips[target];
            }
            // clear the errorString property to remove the red border around the target control
            if (clearErrorString && target && target.hasOwnProperty("errorString")) {
                target.errorString = "";
            }
        } 
        
        /**
         * Removes all the error tips.
         */
        public function removeAllErrorTips():void {
            //showAllErrors = false;
            var keys:Array = DictionaryUtils.getKeys(errorTips);
            for each (var target:Object in keys) 
            {
                removeErrorTip(target, false);
            }
        }

        
        /**
         * Hides all the error tips.
         */
        public function hideAllErrorTips():void {
            showAllErrors = false;
            var keys:Array = DictionaryUtils.getKeys(errorTips);
            for each (var target:Object in keys) 
            {
                hideErrorTip(target, false);
            }
        }
        
        /**
         * Shows all the error tips - doesn't check to see if an error string is set!
         */
        public function showAllErrorTips():void {
            showAllErrors = true;
            var keys:Array = DictionaryUtils.getKeys(errorTips);
            for each (var target:Object in keys) 
            {
                showErrorTip(target);
            }
        }
        
        /**
         * Calls validate() on all the validators.
         */
        public function validateAll():void {
            // need to validator to figure out which error tips should be shown
            for (var validator:Object in validators)
            {
                validator.validate();
            }
        }
        
    }
}
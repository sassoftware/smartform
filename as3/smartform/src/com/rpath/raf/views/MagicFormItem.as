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


package com.rpath.raf.views
{
    import mx.containers.Canvas;
    import mx.core.IVisualElement;
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;
    
    import spark.components.BorderContainer;
    import spark.components.Group;
    import mx.events.FlexEvent;

    public class MagicFormItem extends Group
    {
        
        public function MagicFormItem()
        {
            super();

            // force height computation
            minHeight = 0;
        }
        
        private var _validChanged:Boolean;
        
        [Bindable]
        public function set isValid(v:Boolean):void
        {
            _isValid = v;
            _validChanged = true;
            dispatchEvent(new FlexEvent(_isValid ? FlexEvent.VALID : FlexEvent.INVALID));
        }
        
        private var _isValid:Boolean;
        
        public function get isValid():Boolean
        {
            return _isValid;
        }
        
        /** we need to override validationResultHandler in order to propagate
        * the validation events from Validators down to the actual UI elements
        * so they can change state, etc.
        */
        
        public override function validationResultHandler(event:ValidationResultEvent):void
        {
            isValid = (event.type == ValidationResultEvent.VALID);
            // let our specific input control mark itself appropriately
            try
            {
                if (this.getElementAt(0) is UIComponent)
                {
                    (this.getElementAt(0) as UIComponent).validationResultHandler(event);
                }
            }
            catch (e:RangeError)
            {
                // no children yet. Ignore
            }
            
            // propagate events beyond ourselves
            super.validationResultHandler(event);
        }
        
        private var _selectedIndex:int;
        
        public function get selectedIndex():int
        {
            return _selectedIndex;
        }

        public function set selectedIndex( value:int ):void
        {
            _selectedIndex = value;
        }

    }
}
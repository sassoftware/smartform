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
    import mx.collections.ArrayCollection;
    import mx.core.IVisualElement;
    import mx.core.UIComponent;
    import mx.events.ToolTipEvent;
    import mx.events.ValidationResultEvent;
    
    import spark.components.Group;

    public class CompoundInputItem extends Group
    {
        public function CompoundInputItem()
        {
            super();

            // force initial setting of validation styles
            _validChanged = true;
        }

        [Bindable]
        public var inputFields:Array;

        private var _validChanged:Boolean;
        
        [Bindable]
        public function set isValid(v:Boolean):void
        {
            _isValid = v;
            _validChanged = true;
            invalidateProperties();
        }
        
        private var _isValid:Boolean;
        
        public function get isValid():Boolean
        {
            return _isValid;
        }
        
        public override function validationResultHandler(event:ValidationResultEvent):void
        {
            isValid = (event.type == ValidationResultEvent.VALID);
            // let our specific input control mark itself appropriately
            try
            {
                for each (var elem:UIComponent in inputFields)
                {
                    elem.validationResultHandler(event);
                }
            }
            catch (e:Error)
            {
                // ignore??
            }
            
            // propagate events beyond ourselves
            super.validationResultHandler(event);
        }
        
        
        override protected function commitProperties():void
        {
            super.commitProperties();
            
            if (_validChanged)
            {
                _validChanged = false;
                //setStylesFromValidStatus();
            }
            
        }
    }
}
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
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;

    /**
     *  On error, change the backgroundAlpha to this value
     *
     *  @default 0.25
     */
    [Style(name="errorBackgroundAlpha", type="Number", format="Length", inherit="yes")]

    public class MagicFormItem extends Canvas
    {
        
        public function MagicFormItem()
        {
            super();
            this.setStyle("errorBackgroundAlpha", "0.25");
            
            // force initial setting of validation styles
            _validChanged = true;
        }
        
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
                if (this.getChildAt(0) is UIComponent)
                {
                    (this.getChildAt(0) as UIComponent).validationResultHandler(event);
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
    
        /** enabled override
        * We do this to prevent the Canvas that is our parent type
        * from dimming the whole box. Rather, we want the items within
        * the box to respond to the enabled flag directly
        */
        
        [Bindable]
        public override function set enabled(v:Boolean):void
        {
            _itemEnabled = v;
        }
    
        private var _itemEnabled:Boolean = true;
        
        public override function get enabled():Boolean
        {
            return _itemEnabled;
        }

        
        override public function createComponentsFromDescriptors(recurse:Boolean = true ):void
        {
            if ( childDescriptors.length == 0 )
                return; // no children specified
            
            // remove current children
            if ( selectedIndex != -1 && childDescriptors[selectedIndex] )
            {
                createComponentFromDescriptor( childDescriptors[ selectedIndex ], recurse );
            }
            
            validateNow();
        }

        public override function setFocus():void
        {
            super.setFocus();
            for each (var item:* in getChildren())
            {
                if (item is UIComponent)
                {
                    (item as UIComponent).setFocus();
                    break;
                }
            }
        }

        private var _origBackgroundColor:Number;
        private var _origBackgroundColorChanged:Boolean;
        private var _origBackgroundAlpha:Number;
        private var _origBackgroundAlphaChanged:Boolean;
        
        private function setStylesFromValidStatus():void
        {
            var item:UIComponent;

            try
            {
                item = this.getChildAt(0) as UIComponent;
                // 
                if (_isValid)
                {
                    if (item)
                    {
                        if (_origBackgroundAlphaChanged)
                            item.setStyle("backgroundAlpha", _origBackgroundAlpha);
                        if (_origBackgroundColorChanged)
                            item.setStyle("backgroundColor", _origBackgroundColor);
                    
                        _origBackgroundAlphaChanged = false;
                        _origBackgroundColorChanged = false;
                    }
                }
                else
                {
                    if (item)
                    {
                        var errorAlpha:Number = this.getStyle("errorBackgroundAlpha");
                        
                        if (!isNaN(errorAlpha))
                        {
                            _origBackgroundAlpha = item.getStyle("backgroundAlpha");
                            if (!isNaN(errorAlpha))
                            {
                                item.setStyle("backgroundAlpha", errorAlpha);
                                _origBackgroundAlphaChanged = true;
                            }
                        }
    
                        _origBackgroundColor = item.getStyle("backgroundColor");
                        item.setStyle("backgroundColor", getStyle("errorColor"));
                        _origBackgroundColorChanged = true;
                    }
                }
            }
            catch (e:RangeError)
            {
                // if the children haven't been initialized yet
            }
        }
        
        override protected function commitProperties():void
        {
            super.commitProperties();

            if (_validChanged)
            {
                _validChanged = false;
                setStylesFromValidStatus();
            }
            
        }
    }
}
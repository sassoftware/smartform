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
    import com.rpath.raf.util.UIHelper;
    
    import flash.events.Event;
    import flash.events.FocusEvent;
    
    import mx.effects.Resize;
    import mx.events.FlexEvent;
    
     
    public class ExtendedTextArea extends PromptingTextArea
    {
        public function ExtendedTextArea()
        {
            super();
            addEventListener(FlexEvent.INITIALIZE, onInitialize);
            //addEventListener(MouseEvent.ROLL_OVER, onRollOver);
            //addEventListener(MouseEvent.ROLL_OUT, onRollOut);
            addEventListener(Event.CHANGE, onChange);
            addEventListener(FocusEvent.FOCUS_IN, onFocusIn);
            addEventListener(FocusEvent.FOCUS_OUT, onFocusOut);
            
            resizeAreaEffect.duration = 250;
            resizeAreaEffect.target = this;
            setStyle("resizeEffect", resizeAreaEffect);
        }
        
        public var resizeAreaEffect:Resize = new Resize();
        
        /** allowFileContent controls whether a small "from file" button should 
        * be offered to read content from a local file
        */
        [Bindable]
        public var allowFileContent:Boolean;
        
        
        /** autoResize controls the dynamic expand/contract behavior
        * 
        * @default true
        */
        
        [Bindable]
        public var autoResize:Boolean = true;
        
        public function onInitialize(event:Event):void
        {
            //explicitHeight = unexpandedHeight();
        }
        
        private var _lastHeight:int;
        
        public function onFocusOut(event:Event):void
        {
            if (!autoResize)
                return;

            explicitHeight = _lastHeight;
        }
        
        private function unexpandedHeight():int
        {
            var newHeight:int;
            newHeight = (explicitHeight > measuredMinHeight) ? explicitHeight : measuredMinHeight;
            newHeight = (newHeight > maxHeight) ? maxHeight : (newHeight < minHeight) ? minHeight : newHeight;
            return newHeight;
        }

        private function expandedHeight():int
        {
            var newHeight:int;
            newHeight = (height + 10 > measuredMinHeight) ? height + 10 : measuredMinHeight;
            newHeight = (newHeight > maxHeight) ? maxHeight : (newHeight < minHeight) ? minHeight : newHeight;
            return newHeight;
        }

        
        public function onFocusIn(event:Event):void
        {
            if (!autoResize)
                return;
                
            _lastHeight = unexpandedHeight();
            explicitHeight = expandedHeight();
        }

        public function onChange(event:Event):void
        { 
            if (!autoResize)
                return;
               
            if (text == null || text == "")
            {
                explicitHeight = unexpandedHeight();
            }
            else 
            {
                explicitHeight = expandedHeight();
            }
        }

        protected override function measure():void
        {
            super.measure();
        }
        
        /** override of text property to handle CR/LF consistently across
        * platforms
        */
        
        [Bindable]
        override public function set text(value:String):void
        {
            super.text = UIHelper.processCarriageReturns(value);
        }
        
        override public function get text():String
        {
            return super.text;
        }
        
        [Bindable]
        override public function set enabled(value:Boolean):void
        {
           super.enabled = value;
           selectStyle();
        }
        
        override public function get enabled():Boolean
        {
            return super.enabled;
        }
        
         
        [Bindable]
        override public function set editable(value:Boolean):void
        {
           super.editable = value;
           selectStyle();
        }

        override public function get editable():Boolean
        {
            return super.editable;
        }

        
        private function selectStyle():void
        {
           //styleName = (editable && enabled) ? getStyle("enabledStyleName") as String : getStyle("disabledStyleName") as String;
           styleName = (editable && enabled) ? "enabledTI" as String : "nonEnabledTI" as String;
        }
    }
}
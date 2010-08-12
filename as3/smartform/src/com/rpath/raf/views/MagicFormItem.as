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
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;
    
    import spark.components.Group;

    public class MagicFormItem extends Group
    {
        
        public function MagicFormItem()
        {
            super();

            // force height computation
            minHeight = 0;
        }
       
        /** we need to override validationResultHandler in order to propagate
        * the validation events from Validators down to the actual UI elements
        * so they can change state, etc.
        */
        
        public override function validationResultHandler(event:ValidationResultEvent):void
        {
            // let our specific input control mark itself appropriately
            var child:UIComponent;
            var numElements:int = numElements;
            
            for (var i:int = 0; i < numElements; i++)
            {
                child = getElementAt(i) as UIComponent;
                if (child)
                {
                    child.validationResultHandler(event);
                }
            }
            
            super.validationResultHandler(event);
        }


    }
}
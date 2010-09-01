/*
#
# Copyright (c) 2009 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.views
{
    import mx.core.UIComponent;
    import mx.events.ValidationResultEvent;
    
    import spark.components.Group;

    public class CompoundInputItem extends Group
    {
        public function CompoundInputItem()
        {
            super();
            
            // force height computation
            minHeight = 0;
        }

        [Bindable]
        public var inputFields:Array;

        public override function validationResultHandler(event:ValidationResultEvent):void
        {
            // let our specific input controls mark themselves appropriately
            for each (var elem:UIComponent in inputFields)
            {
                elem.validationResultHandler(event);
            }
            
            // propagate events beyond ourselves
            super.validationResultHandler(event);
        }

    }
}
/*
#
# Copyright (c) 2008-2010 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/


package com.rpath.raf.util
{
    import flash.utils.Dictionary;
    
    import mx.collections.ArrayCollection;
    import spark.components.Application;
    import mx.core.FlexGlobals;
    import mx.core.IFlexDisplayObject;
    import mx.formatters.NumberBaseRoundType;
    import mx.formatters.NumberFormatter;
    import mx.managers.PopUpManager;
    import mx.managers.PopUpManagerChildList;
    
    public class UIHelper
    {

        public static function checkBooleans(...args):Boolean
        {
            for each (var b:* in args)
            {
                if (b is Array || b is ArrayCollection)
                {
                    for each (var c:* in b)
                    {
                        // allow for nested arrays
                        checkBooleans(c);
                    }
                }
                else
                {
                    if (!b)
                        return false;
                }
            }
            return true;
        }
    
        public static function checkOneOf(...args):Boolean
        {
            for each (var b:* in args)
            {
                if (b)
                    return true;
            }
            return false;
        }
        
        public static function formattedDate(unixTimestamp:Number):String
        {
            if (isNaN(unixTimestamp))
                return "";
            
            var date:Date = new Date(unixTimestamp * 1000);
            /*
             * Note that we add 1 to month b/c January is 0 in Flex
             */ 
            return padLeft(date.getMonth() +1) + "/" + padLeft(date.getDate()) + 
                "/" + padLeft(date.getFullYear()) + " " + padLeft(date.getHours()) + 
                ":" + padLeft(date.getMinutes()) + ":" + padLeft(date.getSeconds());
        }
        
        public static function padLeft(number:Number):String
        {
            var strNum:String = number.toString();
            if (number.toString().length == 1)
                strNum = "0" + strNum;
                
            return strNum;
        }
        
        /**
         * Replace \r\n with \n, replace \r with \n
         */
        public static function processCarriageReturns(value:String):String
        {
            if (!value)
                return value;
                
            var cr:String = String.fromCharCode(13);
            var crRegex:RegExp = new RegExp(cr, "gm");

            var crnl:String = String.fromCharCode(13, 10);
            var crnlRegex:RegExp = new RegExp(crnl, "gm");
                
            // process CRNL first
            value = value.replace(crnlRegex, '\n');
            
            // process CR
            value = value.replace(crRegex, '\n');
            
            return value;
        }

        private static var popupModelMap:Dictionary = new Dictionary(true);
        private static var popupOwnerMap:Dictionary = new Dictionary(true);
        
        public static function createPopup(clazz:Class):*
        {
            var popup:Object = PopUpManager.createPopUp(FlexGlobals.topLevelApplication as Application,
                clazz, false, PopUpManagerChildList.APPLICATION) as clazz;
            return popup as IFlexDisplayObject;
        }

        public static function createSingletonPopupForModel(clazz:Class, model:Object, owner:Object=null):*
        {
            var popup:Object;
            
            popup = popupForModel(model);
            if (popup == null)
            {
                popup = PopUpManager.createPopUp(FlexGlobals.topLevelApplication as Application,
                    clazz, false, PopUpManagerChildList.APPLICATION) as clazz;
                
                popupModelMap[model] = popup;
                
                if (owner)
                {
                    popupOwnerMap[popup] = owner;
                }
            }
            
            return popup as IFlexDisplayObject;
        }

        public static function popupForModel(model:Object):*
        {
            return popupModelMap[model];
        }

        public static function removePopupForModel(model:Object):void
        {
            var popup:IFlexDisplayObject = popupModelMap[model];
            if (popup)
            {
                delete popupModelMap[model];
                delete popupOwnerMap[popup];
            }
            
        }

        public static function removePopupsForOwner(owner:Object):void
        {
            for (var popup:* in popupOwnerMap)
            {
                if (popupOwnerMap[popup] === owner)
                {
                    delete popupOwnerMap[popup];
                    // scan the model map too
                    for (var model:* in popupModelMap)
                    {
                        if (popupModelMap[model] === popup)
                        {
                            delete popupModelMap[model];
                        }
                    }
                }
            }
        }

        public static function popupsForOwner(owner:Object):Array
        {
            var result:Array = [];
            for (var popup:* in popupOwnerMap)
            {
                if (popupOwnerMap[popup] === owner)
                {
                    result.push(popup);
                }
            }
            
            return result;
        }

        public static function closePopupsForOwner(owner:Object):void
        {
            for each (var popup:* in UIHelper.popupsForOwner(owner))
            {
                PopUpManager.removePopUp(popup);
            }
            
            removePopupsForOwner(owner);
        }
        
        // make bytes human readable
        public static function humanReadableSize(bytes:int, precision:int=1):String
        {
            var s:String = bytes + ' bytes';
            
            var nf:NumberFormatter = new NumberFormatter();
            nf.precision = precision;
            nf.useThousandsSeparator = true;
            nf.useNegativeSign = true;
            nf.rounding = NumberBaseRoundType.NEAREST;
        
            if (bytes > 1073741824)
            {
                s = nf.format((bytes / 1073741824.0)) + ' GB' + ' (' + (s) + ')';
            }
            else if (bytes > 1048576)
            {
                s = nf.format((bytes / 1048576.0)) + ' MB' + ' (' + (s) + ')';
            }
            else if (bytes > 1024)
            {
                s = nf.format((bytes / 1024.0)) + ' KB' + ' (' + (s) + ')';
            }
            
            return s;
        }
    }
}
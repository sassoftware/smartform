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
    import mx.resources.ResourceManager;
    
    public class DescriptorUtil
    {

    public static function localeDescString(node:XMLList, ns:Namespace):String
    {
        var desc:XMLList;
        var localeChain:Array = ResourceManager.getInstance().localeChain;
        var foundIt:Boolean;
        
        for each (var locale:String in localeChain)
        {
            desc = node..ns::desc.(attribute('lang') == locale);
            
            if (desc.length() > 0)
            {
                foundIt = true;
                break;
            }
        }
        
        if (!foundIt)
        {
            // go with the unlang'd entry
            desc = node..ns::desc.(attribute('lang') == undefined);
        }
                        
        return desc.toString();
    }


    public static function localHelpHref(node:XMLList, ns:Namespace):String
    {
        return localHelpNode(node, ns).@ns::href.toString();
    }
    
    public static function localHelpNode(node:XMLList, ns:Namespace):XMLList
    {
        var help:XMLList;
        var localeChain:Array = ResourceManager.getInstance().localeChain;
        var foundIt:Boolean;
        
        for each (var locale:String in localeChain)
        {
            help = node.(attribute('lang') == locale);
            if (help.length() > 0)
            {
                foundIt = true;
                break;
            }
        }
        
        if (!foundIt)
        {
            // go with the unlang'd entry
            help = node.(attribute('lang') == undefined);
        }
        
        return help;
    }
    
        
    }
}
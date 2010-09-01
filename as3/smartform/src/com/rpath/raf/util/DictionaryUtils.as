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

public class DictionaryUtils
{
    public function DictionaryUtils()
    {
    }
    
    
    public static function getKeys(map:Dictionary) : Array
    {
        var keys:Array = [];
        
        for (var key:* in map)
        {
            keys.push( key );
        }
        return keys;
    }
}
}
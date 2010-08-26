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
package com.rpath.raf.util
{
    /** Interface to ease the pain of handling various validation
    * patterns in ValidationHelper and ErrorTipManager
    */
    
    public interface IValidationAware
    {
        function get errorTipManager():ErrorTipManager;
        function set errorTipManager(v:ErrorTipManager):void;
        
        function get isValid():Boolean;
        function set isValid(v:Boolean):void;
        
        function get validationHelper():ValidationHelper;
        function set validationHelper(v:ValidationHelper):void;
        
        function validate(suppressEvent:Boolean=false):void;
    }
}
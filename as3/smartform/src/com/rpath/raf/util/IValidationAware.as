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
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

package com.rpath.raf.validators
{
import mx.validators.ValidationResult;
import mx.validators.Validator;

public class BooleanValidator extends Validator
{
    public function BooleanValidator()
    {
        super();
    }
    
    override protected function doValidation(value:Object):Array
    {
        var results:Array = [];
        
        var result:ValidationResult = validateTrue(value);
        if (result)
            results.push(result);
        
        return results;
    }
    
    [Bindable]
    public var valueIsFalseError:String = "The value must be true";
    
    private function validateTrue(value:Object):ValidationResult
    {
        var val:Boolean = (value != null) ? Boolean(value) : false;
        
        if (!val)
        {
            return new ValidationResult(true, "", "valueIsFalse",
                valueIsFalseError);                 
        }
        
        return null;
    }
}
}
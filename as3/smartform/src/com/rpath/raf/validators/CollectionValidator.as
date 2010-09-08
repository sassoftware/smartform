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
import mx.collections.ICollectionView;
import mx.validators.ValidationResult;
import mx.validators.Validator;

public class CollectionValidator extends Validator
{
    public function CollectionValidator()
    {
        super();
    }
    
    override protected function doValidation(value:Object):Array
    {
        var results:Array = [];
        
        var result:ValidationResult = validateCollection(value);
        if (result)
            results.push(result);
        
        return results;
    }
    
    [Bindable]
    public var collectionIsEmptyError:String = "The collection cannot be empty";
    
    private function validateCollection(value:Object):ValidationResult
    {
        var valArray:Array = (value as Array);
        var valCollectionView:ICollectionView = (value as ICollectionView);
        
        if (valArray)
        {
            if (valArray.length == 0)
            {
                return new ValidationResult(true, "", "collectionIsEmpty",
                    collectionIsEmptyError);       
            }
        }
        
        if (valCollectionView)
        {
            if (valCollectionView.length == 0)
            {
                return new ValidationResult(true, "", "collectionIsEmpty",
                    collectionIsEmptyError);       
            }
        }
        
        if (required)
        {
            if (!valArray && !valCollectionView)
            {
                return new ValidationResult(true, "", "requiredField",
                    requiredFieldError);                 
            }
        }
        
        return null;
    }
}
}
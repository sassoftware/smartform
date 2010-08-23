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

    [Bindable]
    public class UniqueElementValidator extends Validator
    {
        // Constructor.
        public function UniqueElementValidator() {
            super();
        }

        // Define Array for the return value of doValidation().
        private var results:Array;

        // Array or Collection to check against
        private var _dataProvider : *;

        // Property to use for comparison. Setting this overrides any 
        // comparisonFunction previously set
        public override function set property (value : String) : void
        {
            super.property = value;
            comparisonFunction = compareProperties;
        }
        
        public override function get property () : String
        {
            return super.property;
        }
                
        // Function to use for comparison
        public var comparisonFunction : Function;

        // Define mismatch error messsage
        private var _nonUniqueEntryError : String = "Passwords do not match";

        public function set dataProvider (value : *) : void
        {
            _dataProvider = value;
        }

        public function get dataProvider ():*
        {
            return _dataProvider;
        }
        
        public function set nonUniqueEntryError (s : String) : void 
       {
            _nonUniqueEntryError = s;
        }

        public function get nonUniqueEntryError ():String
        {
            return _nonUniqueEntryError;
        }
        
        private function compareProperties(object:*):Boolean
        {
            try
            {
                for each (var item:* in dataProvider)
                {
                    // ignore ourselves. Needed for edit case
                    if (object === item)
                        continue;
                    
                    if (object[property] == item[property])
                        return false;
                }
            }
            catch (e:Error)
            {
                // any error means bogus properties, data, etc. Thus, we're unique
                // within the parameters given. Sorry!
            }
            return true;
        }
        
        // Define the doValidation() method.
        override protected function doValidation(value:Object):Array
        {
            results = [];
            results = super.doValidation(value);

            // Return if there are errors.
            if (results.length > 0)
                return results;

            // do we have a func or a property to test?
            if (comparisonFunction != null)
            {
                if (!comparisonFunction(source))
                {
                    results.push(new ValidationResult(true, null, "Nonunique", nonUniqueEntryError));
                }
            }
            
            return results;
        }
        
    }
}
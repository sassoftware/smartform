package com.rpath.raf.validators
{
    import mx.validators.ValidationResult;
    import mx.validators.Validator;

    public class StringMatchValidator extends Validator {

        // Define Array for the return value of doValidation().
        private var results:Array;

        // Define compare string
        private var _matches : String = "";

        // Define mismatch error messsage
        private var _mismatchError : String = "Passwords do not match";

        // Constructor.
        public function StringMatchValidator() {
            super();
        }

        public function set matches (s : String) : void {
            _matches = s;
        }

        public function set mismatchError (s : String) : void {
            _mismatchError = s;
        }

        // Define the doValidation() method.
        override protected function doValidation(value:Object):Array {
            var s1: String = _matches;
            var s2: String = source.text;

            results = [];
            results = super.doValidation(value);

            // Return if there are errors.
            if (results.length > 0)
                return results;

            if(s1 == s2)
            {
                return results;
            }
            else
            {
                results.push(new ValidationResult(true, null, "Mismatch", _mismatchError));
                return results;
            }
        }
    }
}
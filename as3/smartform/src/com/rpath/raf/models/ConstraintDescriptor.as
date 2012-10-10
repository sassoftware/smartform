/*
#
# Copyright (c) 2008-2011 rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
*/

package com.rpath.raf.models
{
import spark.components.supportClasses.Range;

[Bindable]
public class ConstraintDescriptor
{
    public function ConstraintDescriptor()
    {
        super();
        
        descriptions = new Description();
        range = new RangeDescriptor();
    }
    
    public var descriptions:Description;
    public var range:RangeDescriptor;
    public var length:String;  // so we can represent null values
    public var regexp:String;
    
    public var uniqueKey:String;
    public var minLength:int;
}
}
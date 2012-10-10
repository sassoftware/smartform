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
import mx.collections.ArrayCollection;


[Bindable]
public class SectionDescriptor
{
    public function SectionDescriptor()
    {
        super();
        descriptions = new Description();
    }
    
    public var key:String;
    
    public var descriptions:Description;
}
}
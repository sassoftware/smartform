/*
#
# Copyright (c) 2009-2012 rPath, Inc.
#
# All rights reserved
#
*/

/*
#
# Copy of RAFButton
#
*/
package com.rpath.raf.controls
{
import com.rpath.raf.skins.SmartFormButtonSkin;

import spark.components.Button;

public class SmartFormButton extends Button
{
    public function SmartFormButton()
    {
        super();
        useHandCursor = this.enabled;
        buttonMode = this.enabled;
        setStyle("skinClass",SmartFormButtonSkin);

    }
    
    public var data:*;
}
}
/*
#
# Copyright (c) 2005-2010 rPath, Inc.
#
# All rights reserved
#
*/

package com.rpath.raf.controls
{

import com.rpath.raf.skins.SmartFormIconButtonSkin;

import flash.events.MouseEvent;
import flash.events.TimerEvent;
import flash.utils.Timer;

import mx.events.FlexEvent;

import spark.components.Button;

//[Event("iconChanged")]

/** IconButton is meant to supercede ClickableImage
 */

public class SmartFormIconButton extends Button
{
    public function SmartFormIconButton()
    {
        super();
        useHandCursor = true;
        buttonMode = true;
        setStyle("skinClass",SmartFormIconButtonSkin);
    }
    
    private var _icon:Class;
    
    /// taking out the source property for now.
    /// force using icon, iconOver, iconDown
    
    
    //adding "source" alias to icon property, since
    //legacy ClickableImages are bitmapImages with source
    //properties
//    [Bindable("iconChanged")]
//    public function get source():Class
//    {
//        return icon;
//    }
//    
//    public function set source(value:Class):void
//    {
//        icon = value;
//    }
    
//    [Bindable("iconChanged")]
    [Bindable]
    public function get icon():Class
    {
        return _icon;
    }
    
    public function set icon(value:Class):void
    {
        if(_icon == value) return;
        
        _icon = value;
        //dispatchEvent(new FlexEvent("iconChanged"));
    }
    
    [Bindable]
    public function get iconOver():Class
    {
        if (_iconOver)
            return _iconOver;
        else
            return _icon;
    }
    
    public function set iconOver(value:Class):void
    {
        _iconOver = value;
    }
    
    [Bindable]
    public function get iconDown():Class
    {
        if (_iconDown)
            return _iconDown;
        else
            return _icon;
    }
    
    public function set iconDown(value:Class):void
    {
        _iconDown = value;
    }
    
    
    private var _iconOver:Class;
    
    private var _iconDown:Class;
    
    [Bindable]
    public var blinkInterval:int = 1000; // ms
    
    public var keepEnabled:Boolean = false;
    
    private var blinkTimer:Timer;
    
    [Bindable]
    public function get blink():Boolean
    {
        return _blink;
    }
    
    private var _blink:Boolean;
    
    public function set blink(value:Boolean):void
    {
        _blink = value;
        if (_blink)
        {
            if (!blinkTimer)
                setupBlinkTimer();
            
            // do first blink right away
            handleBlink(null);
            
            blinkTimer.start();
        }
        else
        {
            if (blinkTimer)
                blinkTimer.stop();
            visible = true;
        }
    }
    
    private function setupBlinkTimer():void
    {
        blinkTimer = new Timer(blinkInterval , 0);
        blinkTimer.addEventListener(TimerEvent.TIMER , handleBlink,false,0,true);
    }
    
    private function handleBlink(event:TimerEvent):void
    {
        if (includeInLayout)
            visible = !visible;
    }
    
    override protected function updateDisplayList(w:Number, h:Number):void
    {
        super.updateDisplayList(w,h);
        if(enabled) {
            useHandCursor = true;
        } else {
            useHandCursor = false;
        }
    }
    
}
}
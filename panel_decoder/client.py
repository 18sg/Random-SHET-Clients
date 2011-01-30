#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

class Client(ShetClient):
	
	root = "/lounge/panel/"
	raw_root = "/lounge/arduino/"
	
	def __init__(self, *args, **kwargs):
		
		ShetClient.__init__(self, *args, **kwargs)
		
		self.watch_event(self.raw_root + "btn_pressed", self.on_btn_pressed)
		self.watch_event(self.raw_root + "btn_mode_changed", self.on_mode_changed)
		
		self.pressed_evt = self.add_event("pressed")
		self.mode_changed_evt = self.add_event("mode_changed")
		self.add_action("set_mode", self.set_mode)
		
		self.add_action("set_led", self.set_led)
		self.add_action("set_led_instant", self.set_led_instant)
		
		print "Started..."
	
	
	def decode_mode(self, encoded):
		return encoded & 0b11, encoded >> 2
	def encode_mode(self, mode_type, mode):
		return mode_type | (mode << 2)
	
	
	def on_mode_changed(self, encoded):
		self.mode_changed_evt(*self.decode_mode(encoded))
	
	
	@make_sync
	def set_mode(self, mode_type, mode):
		yield self.call(self.raw_root + "set_btn_mode", self.encode_mode(mode_type, mode))
	
	
	def decode_buttons(self, encoded):
		mode_e          = encoded >> 7
		buttons_e       = encoded & 0b11111
		hold_e          = (encoded >> 5) & 0b1
		middle_switch_e = (encoded >> 6) & 0b1
		return (self.decode_mode(mode_e)
		       ,(filter((lambda n: bool((encoded>>n) & 0b1)),
		                range(5)),
		         bool(hold_e),
		         bool(middle_switch_e)))
	
	
	def on_btn_pressed(self, encoded):
		mode, buttons = self.decode_buttons(encoded)
		self.pressed_evt(mode, buttons)
	
	
	def encode_led(self, r,g,b):
		return ( (r>>3) << 0
		        |(g>>3) << 5
		        |(b>>3) << 10)
	
	
	@make_sync
	def set_led(self, r, g, b):
		yield self.call(self.raw_root + "set_rgbled", self.encode_led(r,g,b))
	
	@make_sync
	def set_led_instant(self, r, g, b):
		yield self.call(self.raw_root + "set_rgbled_instant", self.encode_led(r,g,b))



if __name__ == "__main__":
	Client().run()

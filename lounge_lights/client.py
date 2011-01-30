#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

class Client(ShetClient):
	
	root = "/lounge/lights/"
	raw_root = "/lounge/arduino/"
	
	def __init__(self, *args, **kwargs):
		
		ShetClient.__init__(self, *args, **kwargs)
		
		# Aliases
		self.add_property("lounge", self.get_lounge, self.set_lounge)
		self.add_property("kitchen", self.get_kitchen, self.set_kitchen)
		
		self.add_action("toggle", self.toggle)
		self.add_action("on", self.on)
		self.add_action("off", self.off)
		self.add_action("mood", self.mood)
		
		print "Started..."
	
	def set_lounge(self, state):
		self.set(self.raw_root + "light_lounge", state)
	def set_kitchen(self, state):
		self.set(self.raw_root + "light_kitchen", state)
	def get_lounge(self):
		return self.get(self.raw_root + "light_lounge")
	def get_kitchen(self):
		return self.get(self.raw_root + "light_kitchen")
	
	def toggle(self):
		return self.call(self.raw_root + "light_toggle")
	def on(self):
		self.set(self.raw_root + "light_kitchen", 1)
		self.set(self.raw_root + "light_lounge", 1)
	def off(self):
		self.set(self.raw_root + "light_kitchen", 0)
		self.set(self.raw_root + "light_lounge", 0)
	def mood(self):
		self.set(self.raw_root + "light_kitchen", 0)
		self.set(self.raw_root + "light_lounge", 1)



if __name__ == "__main__":
	Client().run()

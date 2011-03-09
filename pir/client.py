#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

DEFAULT_DELAY = 30

class Client(ShetClient):
	
	root = "/house/power"
	
	lights = [
		"/jonathan/arduino/bogvo",
		"/tom/servo",
		"/karl/arduino/light_hall",
		"/karl/arduino/light_landing",
		"/lounge/arduino/light_kitchen",
		"/lounge/arduino/light_lounge",
	]
	
	def __init__(self, pir_event, pres_property, delay_property, *args, **kwargs):
		
		ShetClient.__init__(self, *args, **kwargs)
		
		self.pir_event      = pir_event
		self.pres_property  = pres_property
		self.delay_property = delay_property
		
		self.watch_event(pir_event, self.pir_fired)
		self.add_property(pres_property,  self.get_presence, self.set_presence)
		self.add_property(delay_property, self.get_delay,    self.set_delay)
		
		self.timeout_delay = DEFAULT_DELAY
		
		# DelayedCall object for timeout
		self.timeout = None
		
		self.presence = False
		
		print "Started..."
	
	
	def pir_fired(self):
		if self.timeout is not None:
			self.timeout.cancel()
		else:
			# Newly present
			# (Done externally to fire the on-property-set event)
			self.set(self.pres_property, True)
		
		self.timeout = reactor.callLater(self.timeout_delay, self.timeout_expired)
	
	
	def timeout_expired(self):
		self.timeout = None
		
		# (Done externally to fire the on-property-set event)
		if self.get_presence():
			self.set(self.pres_property, False)
	
	
	def get_presence(self):
		return self.presence
	
	def set_presence(self, presence):
		self.presence = presence
	
	
	def get_delay(self):
		return self.timeout_delay
	
	def set_delay(self, timeout_delay):
		self.timeout_delay = timeout_delay



if __name__ == "__main__":
	Client(*sys.argv[1:]).run()

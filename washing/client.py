#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

class Client(ShetClient):
	
	root = "/lounge/washing_machine/"
	raw_root = "/lounge/arduino/"
	washing_mode = (1, 3)
	notify_panel_duration = 10
	
	def __init__(self, *args, **kwargs):
		
		ShetClient.__init__(self, *args, **kwargs)
		
		# Aliases
		self.add_property("state", self.get_washing, self.set_washing)
		
		self.finished_evt = self.add_event("finished")
		self.finished_notification_evt = self.add_event("finished_notification")
		self.started_evt = self.add_event("started")
		
		self.watch_event(self.raw_root + "washing_finished", self.finished_evt)
		self.watch_event(self.raw_root + "washing_finished", self.notify_on_finish)
		
		self.watch_event(self.raw_root + "washing_started", self.on_start)
		
		self.watch_event("/lounge/panel/mode_changed", self.mode_changed)
		
		self.go_back_timer = None
		
		print "Started..."
	
	
	def notify_on_finish(self, runtime):
		self.finished_notification_evt(
			"Washing finished in %d mins, %d secs."%(runtime/60, runtime%60))
	
	
	def get_washing(self):
		return self.call(self.raw_root + "get_washing_state")
	def set_washing(self, v):
		pass
	
	def mode_changed(self, *mode):
		if mode != self.washing_mode and self.go_back_timer is not None:
			self.go_back_timer.cancel()
			self.go_back_timer = None
	
	@make_sync
	def on_start(self):
		# Show the panel for getting notifications for a short period when the
		# washing starts
		self.started_evt()
		self.go_back_timer = reactor.callLater(self.notify_panel_duration,
		                                       self.on_start_expired,
		                                       (yield self.get("/lounge/panel/mode")))
		self.set("/lounge/panel/mode", self.washing_mode)
	
	def on_start_expired(self, last_mode):
		self.set("/lounge/panel/mode", last_mode)
		self.go_back_timer = None



if __name__ == "__main__":
	Client().run()

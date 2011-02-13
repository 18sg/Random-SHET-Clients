#!/usr/bin/python

import os, os.path, sys

from twisted.internet       import reactor
from twisted.internet.defer import Deferred

from shet.client import ShetClient
from shet.sync   import make_sync

from festival import FestivalProcessProtocol


MAX_QUEUE_LENGTH = 5


class Client(ShetClient):
	
	def __init__(self, root, mpd = None, *args, **kwargs):
		self.root = root
		self.mpd = mpd if mpd.endswith("/") else mpd + "/"
		ShetClient.__init__(self, *args, **kwargs)
		
		self.add_action("voices", self.get_voices)
		self.add_action("say_now", self.say_now)
		self.add_action("say", self.say)
		
		self.say_queue = []
		
		print "Started..."
	
	
	def start_festival(self):
		festival = FestivalProcessProtocol()
		cmd = ["festival", "--pipe"]
		reactor.spawnProcess(festival, cmd[0], cmd)
		
		return festival
	
	
	def get_voices(self):
		festival = self.start_festival()
		return festival.get_voices()
	
	
	def say_now(self, *args):
		festival = self.start_festival()
		print "Speaking:", args
		return festival.say_text(*args)
	
	
	@make_sync
	def pause_music(self):
		playing = False
		
		if (self.mpd):
			playing = (yield self.get(self.mpd + "playing"))
			(yield self.set(self.mpd + "playing", False))
		
		yield playing
	
	
	@make_sync
	def unpause_music(self, state):
		if (self.mpd):
			(yield self.set(self.mpd + "playing", state))
	
	
	@make_sync
	def process_say_queue(self):
		playing = (yield self.pause_music())
		
		# Say stuff on the queue
		while len(self.say_queue):
			d = self.say_queue[0]
			
			try:
				(yield self.say_now(*d.to_speek))
				d.callback(d.to_speek[0])
			except Exception, e:
				d.errback(e)
			
			# Element has been processed
			self.say_queue.pop(0)
		
		# Unpause the music (if needed)
		yield self.unpause_music(playing)
	
	
	def say(self, *args):
		if len(self.say_queue) >= MAX_QUEUE_LENGTH:
			raise Exception("Say-Queue Full!")
		
		d = Deferred()
		d.to_speek = args
		
		self.say_queue.append(d)
		
		# If the say_queue was empty, start the queue processor again
		if self.say_queue == [d]:
			self.process_say_queue()
		
		return d
	


if __name__ == "__main__":
	Client(*sys.argv[1:]).run()

#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

from festival import FestivalProcessProtocol

class Client(ShetClient):
	
	def __init__(self, root, *args, **kwargs):
		self.root = root
		ShetClient.__init__(self, *args, **kwargs)
		
		self.add_action("voices", self.get_voices)
		self.add_action("say", self.say_text)
		
		print "Started..."
	
	
	def start_festival(self):
		festival = FestivalProcessProtocol()
		cmd = ["festival", "--pipe"]
		reactor.spawnProcess(festival, cmd[0], cmd)
		
		return festival
	
	
	def get_voices(self):
		festival = self.start_festival()
		return festival.get_voices()
	
	
	def say_text(self, *args):
		festival = self.start_festival()
		print "Speaking:", args
		return festival.say_text(*args)
	


if __name__ == "__main__":
	Client(sys.argv[1]).run()

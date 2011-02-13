#!/usr/bin/python

import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

class Client(ShetClient):
	
	def __init__(self, root, configfile, *args, **kwargs):
		self.root = root
		ShetClient.__init__(self, *args, **kwargs)
		
		bindings = filter(None, open(configfile, "r").read().strip().split("\n"))
		
		for uri, binding in map((lambda s: s.split(" ", 1)), map(str.strip, bindings)):
			self.add_action(uri, self.get_binding(binding))
		
		print "Started..."
	
	def get_binding(self, bindings):
		def press():
			ret_val = 0
			for binding in map(str.strip, bindings.split(";")):
				print "xdotool %s"%binding
				ret_val |= os.system("xdotool %s"%binding)
			return ret_val
		
		return press


if __name__ == "__main__":
	Client(*sys.argv[1:3]).run()

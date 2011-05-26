from lirc_raw import LircProtocolFactory
from shet.client import ShetClient
from functools import partial
from shet.path import join
from twisted.internet import reactor
import sys


class LircToShet(LircProtocolFactory):
	
	def __init__(self, root, remote):
		self.shet = ShetClient()
		self.shet.root = root
		self.shet.install()
		self.remote = remote
		self.events = {}
		
	
	def on_connect(self):
		self.list(self.remote).addCallback(self.recv_keys)
	
	def recv_keys(self, keys):
		self.shet.reset()
		for key in keys:
			code, name = key.split()
			
			self.shet.add_action(join("send", name), partial(self.send, name))
			
			on_command = self.shet.add_event(join("on_command", name))
			on_first_command = self.shet.add_event(join("on_first_command", name))
			self.events[name] = (on_command, on_first_command)
	
	def on_command(self, seq, code, remote):
		if remote == self.remote:
			self.events[code][0](seq)
	
	def on_first_command(self, code, remote):
		if remote == self.remote:
			self.events[code][1]()
	
	def send(self, name):
		return self.send_once(self.remote, name)


if __name__ == "__main__":
	LircToShet(sys.argv[1], sys.argv[2]).connect()
	reactor.run()

from shet.client import ShetClient, shet_action
from twisted.internet import reactor

class Backdoor(ShetClient):
	root = "/lounge/backdoor"
	
	def __init__(self):
		ShetClient.__init__(self)
		self.watch_event("/lounge/arduino/backdoor_opened", self.opened)
		self.watch_event("/lounge/panel/pressed", self.clear)
		self.open = False
	
	def opened(self):
		if not self.open:
			def save_mode(mode):
				self.old_mode = mode
			self.get("/lounge/panel/mode").addCallback(save_mode)
			self.tick()
		self.open = True
	
	def clear(self, *args):
		self.open = False
	
	def tick(self):
		self.set_light()
		reactor.callLater(0.2, self.tock)
	
	def tock(self):
		self.clear_light()
		if self.open:
			reactor.callLater(0.8, self.tick)
		else:
			self.set("/lounge/panel/mode", self.old_mode)
	
	def set_light(self):
		self.call("/lounge/panel/set_led_instant", 255, 0, 0)
	
	def clear_light(self):
		self.call("/lounge/panel/set_led_instant", 0, 0, 255)
		self.set_unused_mode()
	
	def set_unused_mode(self):
		self.set("/lounge/panel/mode", [3, 0])
				

if __name__ == "__main__":
	Backdoor().run()

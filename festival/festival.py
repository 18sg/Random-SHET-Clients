from twisted.internet.protocol import ProcessProtocol
from twisted.internet.defer    import Deferred

MAX_REQUESTS = 5


class FloodException(Exception):
	pass


class FestivalProcessProtocol(ProcessProtocol):
	
	def __init__(self):
		self.buf = ""
		self.request = None
	
	
	def outReceived(self, data):
		self.buf += data
	
	
	def errReceived(self, data):
		self.request.errback(data)
		self.request = None
		
	
	def outConnectionLost(self):
		data, _ , self.buf = self.buf.partition("\n")
		self.handle_data(data, self.request)
	
	
	def handle_data(self, data, d):
		d.callback(d.decode(data))
	
	
	def get_voices(self):
		self.transport.write("(print (voice.list))\n")
		self.transport.closeStdin()
		d = Deferred()
		
		def decode(data):
			return data.strip("()").split(" ")
		
		d.decode = decode
		
		self.request = d
		return d
	
	
	def say_text(self, text, voice = None):
		if voice is not None:
			self.transport.write("(voice_%s)\n"%str(voice))
		
		self.transport.write('(SayText "%s")\n'%(str(text).replace('"','')))
		
		self.transport.closeStdin()
		d = Deferred()
		
		def decode(data):
			# Output is irrellevent
			return
		
		d.decode = decode
		
		self.request = d
		return d

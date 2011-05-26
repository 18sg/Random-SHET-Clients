from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ReconnectingClientFactory, ClientFactory, Protocol


class LircProtocol(LineReceiver):
	
	delimiter = '\n'
	
	def __init__(self):
		self.in_return = False
		self.pending_commands = {}
	
	def connectionMade(self):
		print "connected"
		self.factory.resetDelay()
		self.factory.client = self
		self.factory.on_connect()
	
	def connectionLost(self, reason):
		print "disconnected"
		self.factory.client = None
	
	def lineReceived(self, line):
		if line == "BEGIN":
			self.in_return = True
			self.return_lines = []
		elif line == "END":
			self.in_return = False
			self.on_return(self.return_lines)
		else:
			if self.in_return:
				self.return_lines.append(line)
			else:
				raw, seq, code, remote = line.split()
				seq = int(seq)
				
				self.factory.on_command(seq, code, remote)
				if seq == 0:
					self.factory.on_first_command(code, remote)
	
	def on_return(self, lines):
		command = lines.pop(0)
		succes = lines.pop(0)
		
		if lines:
			assert(lines[0] == "DATA")
			assert(len(lines) == int(lines[1]) + 2)
			data = lines[2:]
		else:
			data = None
		
		d = self.pending_commands[command]
		del self.pending_commands[command]
		
		if succes == "SUCCESS":
			d.callback(data)
		else:
			d.errback(data)
	
	def send_command(self, command):
		command_str = ' '.join(command)
		self.sendLine(command_str)
		d = Deferred()
		self.pending_commands[command_str] = d
		return d


class LircProtocolFactory(ReconnectingClientFactory):
	protocol = LircProtocol
	
	def send_once(self, remote, button, repeat=None):
		command = ["SEND_ONCE", remote, button]
		if repeat is not None:
			command.append(str(repeat))
		return self.client.send_command(command)
	
	def list(self, remote):
		command = ["LIST", remote]
		return self.client.send_command(command)
	
	def on_command(self, seq, code, remote):
		pass
	
	def on_first_command(self, code, remote):
		pass
	
	def on_connect(self):
		pass
	
	def connect(self):
		reactor.connectUNIX("/var/run/lirc/lircd", self)


if __name__ == "__main__":
	LircProtocolFactory().connect()
	reactor.run()

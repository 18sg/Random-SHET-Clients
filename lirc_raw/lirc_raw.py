from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ReconnectingClientFactory

class LircProtocol(LineReceiver):
	
	def __init__(self):
		print "init"
	
	def LineReceived(self, line):
		print line

class LircProtocolFactory(ReconnectingClientFactory):
	protocol = LircProtocol

if __name__ == "__main__":
	f = LircProtocolFactory()
	reactor.connectUNIX("/var/run/lirc/lircd", f)
	reactor.run()



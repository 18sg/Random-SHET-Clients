#!/usr/bin/python
import os, os.path, sys

from twisted.internet import reactor

from shet.client import ShetClient
from shet.sync   import make_sync

import smtplib
from email.mime.text import MIMEText


class Client(ShetClient):
	
	sender = "shet@18sg.net"
	names = ["house","james","jonathan","karl","matt","tom"]
	
	def __init__(self, *args, **kwargs):
		
		ShetClient.__init__(self, *args, **kwargs)
		
		for name in self.names:
			self.add_action("/%s/email"%name, self.make_email_action(name))
		
		print "Started..."
	
	
	def make_email_action(self, name):
		to = "%s@18sg.net"%name
		
		def send_email(message):
			print "Emailing %s: %s"%(to, message)
			msg = MIMEText(message)
			msg['Subject'] = "SHET: %s"%(message[:100])
			msg['From'] = self.sender
			msg['To'] = to
			srv = smtplib.SMTP('smtp1.bethere.co.uk')
			srv.sendmail(self.sender, to, msg.as_string())
			srv.quit()
		
		return send_email
	


if __name__ == "__main__":
	Client().run()


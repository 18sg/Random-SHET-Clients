from shet.client import ShetClient
import xml.etree.ElementTree as et
import requests
from twisted.internet.task import LoopingCall

class Line:
		def __init__(self, statusID, statusDes):
			self.statusID = statusID
			self.statusDes = statusDes

		def getStatusID(self):
			return self.statusID

		def setStatusID(self, statusID):
			self.statusID = statusID

		def getStatusDes(self):
			return self.statusDes

		def setStatusDes(self, statusDes):
			self.statusDes = statusDes

class Underground(ShetClient):
	root = "/underground/"
	raw_root = "/underground/"

	def __init__(self, *args, **kwargs):
		ShetClient.__init__(self, *args, **kwargs)

		self.update_url = "http://cloud.tfl.gov.uk/TrackerNet/LineStatus"
		self.lines = {}
		self.update_time = 30 #TfL asks for 30 seconds between requests

		self.updater = LoopingCall(self.updateStatus)
		self.updater.start(self.update_time)

		print("Started")

	def updateStatus(self):
		r = requests.get(self.update_url)

		root = et.fromstring(r.content)
		for child in root:
			if child[1].get('Name') not in self.lines:
				self.lines[child[1].get('Name')] = Line(child[2].get('ID'), child[2].get('Description'))
				self.add_property(child[1].get('Name') + "/status_id", self.lines[child[1].get('Name')].getStatusID, self.lines[child[1].get('Name')].setStatusID)
				self.add_property(child[1].get('Name') + "/status_des", self.lines[child[1].get('Name')].getStatusDes, self.lines[child[1].get('Name')].setStatusDes)
			else:
				self.lines[child[1].get('Name')].setStatusID(child[2].get('ID'))
				self.lines[child[1].get('Name')].setStatusDes(child[2].get('Description'))

Underground().run()
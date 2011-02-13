#!/usr/bin/python

from shet.client import ShetClient
from shet.sync   import make_sync

MPD_SERVER = "/shelf/mpd"


class Client(ShetClient):
	
	root = "shelf"
	
	def __init__(self, *args, **kwargs):
		ShetClient.__init__(self, *args, **kwargs)
		
		self.add_action("load_playlist", self.load_playlist)
	
	@make_sync
	def load_playlist(self, playlist):
		yield self.set(MPD_SERVER + "/playlist", open(playlist,"r").read().strip().split("\n"))
		yield self.call(MPD_SERVER + "/play")


if __name__ == "__main__":
	Client().run()

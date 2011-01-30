#!/usr/bin/python

from shet.client import ShetClient
from shet.sync   import make_sync

MPD_SERVER = "/shelf/mpd"


class Client(ShetClient):
	
	root = "shelf"
	
	def __init__(self, *args, **kwargs):
		ShetClient.__init__(self, *args, **kwargs)
		
		self.add_action("copy_playlist_from", self.copy_playlist)
	
	
	@make_sync
	def copy_playlist(self, people):
		# To later be expanded...
		if type(people) is not list:
			people = [people]
		
		for person in people[:1]:
			user_mpd = "/%s/mpd"%(person)
			user_prefix = "%s/"%person.title()
			
			self.call("%s/get_playlist"%MPD_SERVER,user_mpd, user_prefix)
			
			time = (yield self.get("%s/current_pos"%user_mpd))
			self.set("%s/current_pos"%MPD_SERVER, time)


if __name__ == "__main__":
	Client().run()

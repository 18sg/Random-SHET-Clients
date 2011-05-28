#!/usr/bin/python

# Simple Alsa Mixer SHET client. Currently only treats outputs sensibly.
# Usage:
#   python client.py /path/to/use/ [MixerName:DisplayName ...]
# If a list of MixerName:DisplayName pairs are provided, only these mixers will
# be shown under the names given.

DEFAULT_VOLUME_INCREMENT = 3

import sys
import alsaaudio

from shet.client import ShetClient
from shet.sync   import make_sync

class MixerControl(object):
	
	def __init__(self, mixer_name):
		self.mixer = alsaaudio.Mixer(mixer_name)
	
	def get_mute(self):
		return self.mixer.getmute()[0]
	def set_mute(self, state):
		self.mixer.setmute(state)
	
	def mute_toggle(self):
		self.set_mute(not self.get_mute())
	
	def get_vol(self):
		return self.mixer.getvolume()[0]
	def set_vol(self, volume):
		self.mixer.setvolume(volume)
	
	def vol_inc(self, amount = DEFAULT_VOLUME_INCREMENT):
		self.set_vol(min(self.get_vol() + amount, 100))
	def vol_dec(self, amount = DEFAULT_VOLUME_INCREMENT):
		self.set_vol(max(self.get_vol() - amount, 0))



class Client(ShetClient):
	
	def __init__(self, root, device_names, *args, **kwargs):
		self.root = root
		ShetClient.__init__(self, *args, **kwargs)
		
		# Turn the user's mixer list and the system mixer list into (mixer-name,
		# display-name) pairs.
		user_mixers = map((lambda s: s.split(":",1)), device_names)
		sys_mixers = map(lambda m: (m, str(m).replace(" ", "_")), alsaaudio.mixers())
		
		for mixer_name, name in user_mixers or sys_mixers:
			mixer = MixerControl(mixer_name)
			self.add_property("%s/volume"%name, mixer.get_vol, mixer.set_vol)
			self.add_property("%s/mute"%name, mixer.get_mute, mixer.set_mute)
			
			self.add_action("%s/mute_toggle"%name, mixer.mute_toggle)
			self.add_action("%s/vol_inc"%name, mixer.vol_inc)
			self.add_action("%s/vol_dec"%name, mixer.vol_dec)
		
		print "Started..."



if __name__ == "__main__":
	Client(sys.argv[1], sys.argv[2:]).run()

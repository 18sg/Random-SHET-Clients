#!/usr/bin/python2

import eiscp
from shet.client import ShetClient, shet_action


class Onkyo(ShetClient):
	def __init__(self, args):
		self.receiver = eiscp.eISCP(args.ip)

		ShetClient.__init__(self)

		self.add_action('/onkyo/volUp', self.volume_up)
		self.add_action('/onkyo/volDown', self.volume_down)
		self.add_action('/onkyo/mute', self.mute)
		self.add_action('/onkyo/on', self.on)
		self.add_action('/onkyo/standby', self.standby)

	def volume_up(self):
		self.receiver.command('master-volume level-up')

	def volume_down(self):
		self.receiver.command('master-volume level-down')

	def mute(self):
		self.receiver.command('audio-muting toggle')

	def on(self):
		self.receiver.command('system-power on')

	def standby(self):
		self.receiver.command('system-power standby')


def get_args():
	import argparse
	parser = argparse.ArgumentParser(description="Control of onkyo audio recievers.")
	parser.add_argument("ip", help="The IP address of your reciever")
	return parser.parse_args()

if __name__ == "__main__":
	Onkyo(get_args()).run()
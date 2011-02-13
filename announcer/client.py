#!/usr/bin/python

import os, os.path, sys

from twisted.internet       import reactor
from twisted.internet.defer import Deferred

from shet.client import ShetClient
from shet.sync   import make_sync


WASHING_FINISHED_NOTIFICATION = "/lounge/washing_machine/finished_notification"
WASHING_STATE = "/lounge/washing_machine/state"


class Client(ShetClient):
	
	def __init__(self, root, tts, *args, **kwargs):
		self.root = root if root.endswith("/") else root + "/"
		self.tts  = tts  if tts.endswith("/")  else tts + "/"
		ShetClient.__init__(self, *args, **kwargs)
		
		self.add_action("washing_reminder_booked", self.wasing_reminder_booked)
		self.add_action("washing_reminder_removed", self.wasing_reminder_removed)
		self.add_action("all_washing_bookings", self.all_washing_bookings)
		
		self.irc_announce = "addressed"
		self.add_property("irc_announcements",
		                  self.get_irc_announcements,
		                  self.set_irc_announcements)
		
		self.watch_event("/irc/on_say", self.irc_announce_all)
		self.watch_event("/irc/on_action", self.irc_announce_all_action)
		self.watch_event("/shelf/irc/on_address", self.irc_announce_addressed)
		
		print "Started..."
	
	
	def say(self, *args):
		return self.call(self.tts + "say", *args)
	
	
	def wasing_reminder_booked(self, people):
		if type(people) is not list:
			people = [people]
		
		# Can only book reminders one at a time atm...
		if len(people) == 1:
			self.say("Reminder booked for %s."%people[0])
	
	
	def wasing_reminder_removed(self, people):
		if type(people) is not list:
			people = [people]
		
		# Can only book reminders one at a time atm...
		if len(people) == 1:
			self.say("Reminder cancelled for %s."%people[0])
	
	
	@make_sync
	def all_washing_bookings(self):
		binds = (yield self.call("/bind/ls"))
		
		# Generate runtime message
		runtime_sec = (yield self.get(WASHING_STATE))
		runtime_prefix = " and the washing machine has been running for "
		if runtime_sec == 0:
			runtime = ""
		elif runtime_sec < 60:
			runtime = "%s%d seconds"%(runtime_prefix, runtime_sec)
		else:
			hrs = runtime_sec / (60*60)
			mins = (runtime_sec - (hrs * 60 * 60)) / 60
			runtime = runtime_prefix
			if hrs > 0:
				runtime += "%d hour%s"%(hrs, "s" if hrs > 1 else "")
			
			if hrs > 0 and mins > 0:
				runtime += " and "
			
			if mins > 0:
				runtime += "%d minute%s"%(mins, "s" if mins > 1 else "")
		
		# Get a list of people with reminders booked
		people = []
		for bind, bind_type in binds:
			event, action = bind
			if bind_type == "once" and event == WASHING_FINISHED_NOTIFICATION:
				people.append(action.split("/",2)[1])
		
		if len(people) == 0:
			yield self.say("No reminders have been booked%s."%runtime)
		else:
			# Format the list
			reminders = ", ".join(people[:-1])
			if len(people) > 1:
				reminders += " and "
			reminders += people[-1]
			
			prefix = "" if len(people) > 1 else "A "
			joiner = "s have" if len(people) > 1 else " has"
			
			yield self.say("%sReminder%s been booked by %s %s."%(prefix, joiner, reminders, runtime))
	
	
	def set_irc_announcements(self, value):
		self.irc_announce = value
		self.say("Read %s."%value)
	
	
	def get_irc_announcements(self):
		return self.irc_announce
	
	
	def irc_announce_all(self, user, message):
		if self.irc_announce == "all":
			return self.say("%s said %s"%(user, message))
	
	def irc_announce_all_action(self, user, message):
		if self.irc_announce == "all":
			return self.say("%s %s"%(user, message))
	
	def irc_announce_addressed(self, user, message):
		print "all", user, message
		if self.irc_announce == "addressed":
			return self.say("%s said %s"%(user, message))
	
	




if __name__ == "__main__":
	Client(*sys.argv[1:]).run()

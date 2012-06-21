fs = require "q-fs"
Q = require "q"
exec = require("child_process").exec
shet = require("shet-client").connect()

# Filter a list of items (in a promise) by a function which returns promises
# containing booleans.
q_filter = (l, f) ->
	l
	.then (items) ->
		for item in items
			do (item) ->
				f(item).then (flag) -> [item, flag]
	.all()
	.then (items) ->
		item for [item, flag] in items when flag

# Get the command line of a process given it;s pid.
get_cmd_line = (pid) ->
	fs.read("/proc/#{pid}/cmdline").then (line) -> line.toString()

# Does a process have a command line starting with mplayer?
is_mplayer = (pid) ->
	get_cmd_line(pid)
	.then (cmdline) ->
		cmdline.match /^mplayer/
	.fail () ->
		false

# A list of all pids on the system.
get_processes = ->
	fs.list("/proc")
	.then (files) ->
		for file in files when file.match /^\d+$/
			parseInt(file)

# Get the pid of the first mplayer process.
get_mplayer_pid = ->
	q_filter(get_processes(), is_mplayer)
	.then (pids) ->
		if pids.length
			pids[0]
		else
			Q.reject("No mplayer process running.")

# Get the playing mp3 or flac file from an mplayer process.
now_playing = (pid) ->
	fs.list("/proc/#{pid}/fd")
	.then (fds) ->
		fs.readLink("/proc/#{pid}/fd/#{fd}") for fd in fds
	.all()
	.then (files) ->
		(f for f in files when f.match /\.(flac|mp3|m4a)$/i)[0]

# Get the file currently playing in mplayer, caching the pid across calls.
last_pid = null
mplayer_now_playing = ->
	# get the pid, store it, and return the current file.
	get_pid = ->
		get_mplayer_pid()
		.then (pid) ->
			last_pid = pid
			now_playing pid
	
	if last_pid == null
		get_pid()
	else
		is_mplayer(last_pid)
		.then (flag) ->
			if flag
				now_playing last_pid
			else
				get_pid()

# Given the spewage from ffprobe parsed as jsom, return a nicely-formatted
# "artist - title" string.
format_info = (info) ->
	tags = info.format.tags
	title = tags.title ? tags.TITLE
	artist = tags.artist ? tags.ARTIST
	"#{artist} - #{title}"

# Get media info from a given file.
get_info_raw = (file) ->
	Q.ncall(exec, this, "ffprobe -v quiet -show_format -print_format json \"#{file}\"")
	.spread (stdout, stderr) ->
		JSON.parse stdout

# Get the media info of a file, while caching the last value.
last_file = null
last_info = null
get_info = (file) ->
	if last_file == file
		last_info
	else
		get_info_raw(file).then (info) ->
			last_file = file
			last_info = info
			info


# Setup the shet interface.
path = process.argv[2]
fifo = process.argv[3]

shet.add_action "#{path}/next", -> fs.write(fifo, "pt_step 1\n")
shet.add_action "#{path}/prev", -> fs.write(fifo, "pt_step -1\n")
shet.add_action "#{path}/toggle", -> fs.write(fifo, "pause\n")
shet.add_action "#{path}/seek", (time) -> fs.write(fifo, "seek #{time}\n")
shet.add_action "#{path}/now_playing", ->
	mplayer_now_playing()
	.then(get_info)
	.then(format_info)

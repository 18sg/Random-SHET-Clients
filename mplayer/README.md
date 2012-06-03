SHET Mplayer Interface
======================

This client allows control of a running mplayer process from SHET.

For some reason I decided to write the while thing using asynchronous APIs, so the code is unnecessarily hairy.

Dependencies
------------

- node
- coffeescript `# npm install -g coffee-script`
- shet-client `$ npm install shet-client`
- q `$ npm install q`
- q-fs `$ npm install q-fs`

Usage
-----

```
$ coffee mplayer.coffee SHET_PATH MPLAYER_FIFO
```

- `SHET_PATH`

	The SHET directory in which `next`, `prev`, `toggle`, `seek`, and `now_playing`
	actions will be added.

- `MPLAYER_FIFO`

	The fifo write mplayer commands to. Put a line like this in `~/.mplayer/config`:
	
	```
	input=file=/home/foo/.mplayer/fifo
	```
	
	, and make the fifo:
	
	```
	$ mkfifo /home/foo/.mplayer/fifo
	```

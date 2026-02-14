## Python Plex Client

Ideal for playing media on a Raspberry Pi 3 via composite, also works over HDMI or on any x86_64.

The [official pi client](https://github.com/plexinc/plex-media-player) has been deprecated and [RasPlex](https://github.com/RasPlex/RasPlex) is no longer supported.

### Setup

We want to run without window manager (runlevel 3) so start from a Raspbian "Lite" image or disable LXDE.

`$ sudo apt install mplayer`

Note: omxplayer can be used on Raspbian Buster and earlier for improved performance.

`$ pip3 install -r requirements.txt`


`$ cp .env.example .env`

* Set the Plex host and account token. To retrieve the token, you can clone the python-plexapi repository and run the [plex-gettoken.py](https://github.com/pushingkarmaorg/python-plexapi/blob/master/tools/plex-gettoken.py) script.

* Also set desired output resolution to use for transcoding. In my case, I am wanting 640x480 output for a CRT TV.

Run using: `$ python3 client.py`

### Playback

Uses mplayer keybindings:

 * q to stop, space to pause
 * 1-2 brightness
 * 3-4 contrast
 * 5-6 hue
 * 7-8 saturation
 * 9-0 volume
 * <-> previous/next when playing an album

### What it doesn't do

* Seeking: doesn't seem to be supported by the stream url, not going to fix this, it makes it more like the actual live TV experience
* We could seek if we mounted the share with smbclient and played the file directly
* But perhaps we don't want to expose the seek functionality 

### What it can do

* Add PageUp/PageDown support to curses-menu by applying patch
* Then install modified package:

`pip install -e curses-menu`

### What it will do

* Additional library types
* Show durations
* Stream URLs may expire by the time they are used... (refactor menu)
* Event on return to menu/screensaver? Use function instead of command
* Screen edge cutoff 5 chars
* Thumbnails

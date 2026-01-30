#!/usr/bin/python3

from plexapi.server import PlexServer
from cursesmenu import CursesMenu
from cursesmenu.items import CommandItem, FunctionItem, MenuItem, SubmenuItem
from dotenv import load_dotenv
import os

load_dotenv()

baseurl = os.getenv('PLEX_BASEURL')
token = os.getenv('PLEX_TOKEN')
videoResolution = os.getenv('PLEX_VIDEO_RESOLUTION', '1920x1080')
plex = PlexServer(baseurl, token)

# Menu library sections
menu = CursesMenu("Plex Client", "Choose Library")
libraries = plex.library.sections()
for library in libraries:
  print(library.title)

  if library.TYPE != 'movie':
    continue

  submenu = CursesMenu(library.title)
  movies = plex.library.section(library.title)
  for video in movies.search():
    print(video.title)

    item = MenuItem(video.title)
    movie = plex.library.section(library.title).get(video.title)
    for obj in movie.media:
      for part in obj.parts:
        file_url = baseurl + movie.key
        stream_url = movie.getStreamURL(videoResolution=videoResolution)
        command_item = CommandItem(
          video.title,
          "mplayer -really-quiet -nolirc \"" + stream_url + "\"",
        )
        submenu.items.append(command_item)

  submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
  menu.items.append(submenu_item)
  print('')

os.system('cls||clear')
menu.show()

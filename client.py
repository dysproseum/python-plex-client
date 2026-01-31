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
  print(f"TYPE: {library.TYPE}")

  if library.TYPE == 'movie':
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
            "mplayer -really-quiet -nolirc -fs \"" + stream_url + "\"",
          )
          submenu.items.append(command_item)
  
    # end movie for loop
    submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
    menu.items.append(submenu_item)
    print('')

  if library.TYPE == 'show':
    submenu = CursesMenu(library.title)
    shows = plex.library.section(library.title)
    for show in shows.search():
      print(show.title)
      # make menu item for show itself containing seasons
      show_menu = CursesMenu(show.title)
      seasons = show.seasons()
      for season in seasons:
        print(f"- Season {season.index}")
        # then each season is also a submenu
        season_menu = CursesMenu(f"Season {season.index}")
        episodes = season.episodes()
        for episode in episodes:
          for obj in episode.media:
            file_url = baseurl + episode.key
            stream_url = episode.getStreamURL(videoResolution=videoResolution)
            command_item = CommandItem(
              episode.title,
              "mplayer -really-quiet -nolirc -fs \"" + stream_url + "\"",
            )
            season_menu.items.append(command_item)

        season_item = SubmenuItem(f"Season {season.index}", submenu=season_menu, menu=show_menu)
        show_menu.items.append(season_item)

      show_item = SubmenuItem(show.title, submenu=show_menu, menu=submenu)
      submenu.items.append(show_item)

    submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
    menu.items.append(submenu_item)

  if library.TYPE == 'artist':
    continue

os.system('cls||clear')
menu.show()

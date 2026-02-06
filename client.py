#!/usr/bin/python3

from plexapi.server import PlexServer
from cursesmenu import CursesMenu
from cursesmenu.items import CommandItem, FunctionItem, MenuItem, SubmenuItem
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
baseurl = os.getenv('PLEX_BASEURL')
token = os.getenv('PLEX_TOKEN')
videoResolution = os.getenv('PLEX_VIDEO_RESOLUTION', '1920x1080')
plex = PlexServer(baseurl, token)

menu_title = "Plex Client"
menu_subtitle = "Choose Library"
vo = None

# Callback to start player.
def launch_player(stream_url):
  command = f"mplayer -really-quiet -nolirc -framedrop"
  global vo
  if vo == "aa":
    command += " -vo aa -monitorpixelaspect 0.5"
  elif vo == "caca":
    command += " -vo caca"
  else:
    command += " -fs"
  command += f" \"{stream_url}\""
  print(command)
  subprocess.call(command, shell=True)

# Main menu.
menu = CursesMenu(menu_title, menu_subtitle)
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
          function_item = FunctionItem(
            video.title,
            launch_player,
            [stream_url]
          )
          submenu.items.append(function_item)
    submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
    menu.items.append(submenu_item)
    print('')

  if library.TYPE == 'show':
    submenu = CursesMenu(library.title)
    shows = plex.library.section(library.title)
    for show in shows.search():
      print(show.title)

      # Make menu item for show itself containing seasons
      show_menu = CursesMenu(show.title)
      seasons = show.seasons()
      for season in seasons:
        print(f"- Season {season.index}")

        # Then each season is also a submenu
        season_menu = CursesMenu(f"Season {season.index}")
        episodes = season.episodes()
        for episode in episodes:
          for obj in episode.media:
            file_url = baseurl + episode.key
            stream_url = episode.getStreamURL(videoResolution=videoResolution)
            function_item = FunctionItem(
              episode.title,
              launch_player,
              [stream_url]
            )
            season_menu.items.append(function_item)

        season_item = SubmenuItem(f"Season {season.index}", submenu=season_menu, menu=show_menu)
        show_menu.items.append(season_item)

      show_item = SubmenuItem(show.title, submenu=show_menu, menu=submenu)
      submenu.items.append(show_item)

    submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
    menu.items.append(submenu_item)
    print('')

  if library.TYPE == 'artist':
    submenu = CursesMenu(library.title)

    music = plex.library.section(library.title)
    albums = music.albums()
    # don't have first album yet to get its artist
    # just walk through albums. ignore filter by artist for now.
    for album in albums:
      artist = album.artist()
      title = f"{artist.title} - {album.title} ({album.year})"
      print(title)
      album_menu = CursesMenu(title)

      url_array = []
      for track in album.tracks():
        for obj in track.media:
          stream_url = track.getStreamURL()
          command_item = CommandItem(
            track.title,
            "mplayer -nolirc -fs \"" + stream_url + "\"",
          )
          album_menu.items.append(command_item)
          url_array.append(stream_url)

      # Additional items to play all
      quoted_params = [f'"{url}"' for url in url_array]
      flat_params = (' ').join(quoted_params)
      play_all_item = CommandItem(
        ">> Play Album >>",
        f"mplayer -nolirc -fs {flat_params}",
      )
      album_menu.items.append(play_all_item)
      shuffle_all_item = CommandItem(
        ">> Shuffle Album >>",
        f"mplayer -nolirc -fs -shuffle {flat_params}",
      )
      album_menu.items.append(shuffle_all_item)
      album_item = SubmenuItem(title, submenu=album_menu, menu=submenu)
      submenu.items.append(album_item)

    submenu_item = SubmenuItem(library.title, submenu=submenu, menu=menu)
    menu.items.append(submenu_item)

# Menu item to set video output filter.
def set_video_output(menu):
  global vo
  if vo == None:
    vo = "aa"
  elif vo == "aa":
    vo = "caca"
  else:
    vo = None

  global vo_item
  vo_item.text = f">> Video Output Filter ({vo})"
  menu.refresh_screen()

vo_item = FunctionItem(
  ">> Video Output Filter (None)",
  set_video_output,
  [menu]
)
menu.items.append(vo_item)

# Start.
os.system('cls||clear')
menu.show()

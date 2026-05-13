#!/usr/bin/python3

from pick import pick
from dotenv import load_dotenv
import os
import subprocess
from smb.SMBConnection import SMBConnection
import smb.smb_structs

load_dotenv()
localpcname = os.getenv('SMB_LOCAL_HOSTNAME', 'localhost')
remotepcname = os.getenv('SMB_REMOTE_HOSTNAME', 'remote')
address = os.getenv('SMB_ADDRESS', '127.0.0.1')
port = os.getenv('SMB_PORT', 445)
username = os.getenv('SMB_USERNAME', 'guest')
password = os.getenv('SMB_PASSWORD', '')
domain = os.getenv('SMB_DOMAIN', 'workgroup')
KEY_ESCAPE = 27
QUIT_KEYS = (KEY_ESCAPE, ord("q"))

os.system('cls||clear')

def list_smb_path(share, path):
  try:
    return conn.listPath(share, path)
  except smb.smb_structs.OperationFailure as ex:
    for msg in ex.smb_messages:
      if hasattr(msg, 'status'):
        # SMB2 messages expose status directly
        code = msg.status
      elif hasattr(msg, 'status') and hasattr(msg.status, 'internal_value'):
        # SMB1 messages expose status internally
        code = msg.status.internal_value

      # Map common NTSTATUS codes to POSIX errors
      if code == 0x00000000:
        print("The operation completed successfully")
      elif code == 0xC0000001:
        print("The requested operation was unsuccessful")
      elif code == 0xC000000F:
        print("No such entry (ENOENT)")
      elif code == 0xC0000022:
        print("Permission denied (EPERM)")
      elif code == 0xC0000035:
        print("Already exists (EEXIST)")
      elif code == 0xC000007F:
        print("No space left on device (ENOSPC)")
      elif code == 0xC00000CC:
        print("The specified share cannot be found on the remote server")
      else:
        print(f"Unknown error code: {code}")

vo=None
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
  command += f" \"smb://{username}:{password}@{address}/{selected_share}{stream_url}\""
  print(command)
  try:
    subprocess.call(command, shell=True)
  except KeyboardInterrupt as ex:
    print("Caught Ctrl-C in player")

def select_smb_share():
  # List shares
  shares = conn.listShares()
  share_names = []
  folder_names = []
  for share in shares:
    if not share.isSpecial and share.name not in ['NETLOGON', 'SYSVOL']:
      share_names.append(share.name)
      folder_names.append(f"📁 {share.name}")

  title = f"SMB {remotepcname} - Please select a share:"
  try:
    option, index = pick(folder_names, title, indicator='➜', quit_keys=QUIT_KEYS)
  except KeyboardInterrupt as ex:
    exit(1)

  # Detect quit
  if (index == -1):
    print(option)
    conn.close()
    exit(0)
  return [share_names[index], index]

# Initialize connection
conn = SMBConnection(username, password, localpcname, remotepcname, domain=domain, use_ntlm_v2=True, is_direct_tcp=True)

# Connect to server IP
conn.connect(address, port)

file_list = []
while not file_list:
  # Choose share
  option, index = select_smb_share()
  selected_share = option
  selected_path = '/'
  # List path
  file_list = list_smb_path(selected_share, selected_path)

while True:
  # Sort first by filename then put directories at the top
  file_list.sort(key=lambda x: x.filename)
  file_list.sort(key=lambda x: x.isDirectory, reverse=True)

  # Iterate through results to print filenames
  filename_list = []
  for item in file_list:
    if item.isDirectory:
      filename_list.append(f"📁 {item.filename}")
    else:
      filename_list.append(item.filename)

  title = f"SMB {selected_share}: {selected_path}"
  try:
    option, index = pick(filename_list, title, indicator='‣', quit_keys=QUIT_KEYS)
  except KeyboardInterrupt as ex:
    exit(1)
  # Detect quit
  if (index == -1):
    conn.close()
    exit(0)

  # Navigation
  if file_list[index].isDirectory:
    if file_list[index].filename == ".":
      selected_path = selected_path
    elif file_list[index].filename == "..":
      index = selected_path.rfind('/')
      if index != -1:
        selected_path = selected_path[:index]
      if selected_path == '':
        selected_path = '/'
    else:
      selected_path = f"{selected_path}/{file_list[index].filename}"
  else:
    # @todo keep default_index after playback
    print(f"Selected path: {selected_path}")
    print(f"Selected file: {file_list[index].filename}")
    launch_player(f"{selected_path}/{file_list[index].filename}")

  # List contents of the root directory ('/')
  if selected_path[0:2] == "//":
    selected_path = selected_path[1:]

  file_list = list_smb_path(selected_share, selected_path)


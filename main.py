import os
import qbittorrentapi
from qbittorrentapi import Client, TorrentStates
import time
import json

def killClient(qbt_client):
  # os.system('cmd /c "taskkill /im qbittorrent.exe"')
  qbt_client.app_shutdown()

def startClient():
  os.system('cmd /c "start qtshortcut.lnk"')

def displayClientInfo(qbt_client):
  print(f'qBittorrent: {qbt_client.app.version}')
  print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
  for k,v in qbt_client.app.build_info.items(): print(f'{k}: {v}')

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(
    host='localhost',
    port=8080,
    username='admin',
    password='adminadmin',
)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
  qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
  print(e)

print("got client")

# Determine if we're in a bad connection state
# This is when there are others in the swarm yet no progress is being made.
numBadTorrents = 0
numGoodTorrents = 0
now = int(time.time())
for torrent in qbt_client.torrents_info():
  # check if torrent is downloading
  if torrent.state_enum.is_downloading:
    swarmCount = torrent.num_complete + torrent.num_incomplete + torrent.num_seeds + torrent.num_leechs
    lastChunkDownloadedSecondsAgo = now - torrent.last_activity
    print(f'last chunk was DL {lastChunkDownloadedSecondsAgo} seconds ago. DL speed is {torrent.dlspeed}. Swarm count {swarmCount}')

    if swarmCount >= 0 and torrent.dlspeed <= 200 and lastChunkDownloadedSecondsAgo > 60*10:
      print(f'{torrent.name} {torrent.hash} is downloading but is BAD!')
      numBadTorrents += 1
    else:
      print(f'{torrent.name} {torrent.hash} is downloading and is GOOD!')
      numGoodTorrents += 1
  else:
    print(f'{torrent.name} {torrent.hash} is not being counted')

print(f'good {numGoodTorrents} bad {numBadTorrents}')
if numBadTorrents > 0 and numGoodTorrents == 0:
  print("commencing reboot")
  killClient(qbt_client)
  time.sleep(10)
  startClient()

print("done")


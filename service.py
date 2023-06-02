from lib.Plugin import *
from lib.StoreSQLite import Store
import xbmcgui




Monitor				= xbmc.Monitor()
Player				= xbmc.Player()

Addon_DatabaseFile	= getAddonDatabaseFile()
Database			= Store(Addon_DatabaseFile)



if __name__ == '__main__':
	while not Monitor.abortRequested():
		# Sleep/wait for abort for 10 seconds
		if Monitor.waitForAbort(1):
			# Abort was requested while waiting. We should exit
			break


		if Player.isPlaying():
			InfoTag			= Player.getVideoInfoTag()
			getVideoInfo	= InfoTag.getDirectors()


			if 0 < len(getVideoInfo) and 1 < len(getVideoInfo):
				AddonName	= getAddonInfo('name')
				VideoCheck	= getVideoInfo[0]
				VideoID		= getVideoInfo[1]


				if AddonName == VideoCheck and VideoID !='':
					FileCurrent	= Player.getPlayingFile()

					TimeCurrent	= int(Player.getTime())
					TimeTotal	= int(Player.getTotalTime())

					TimePercent	= TimeCurrent / TimeTotal * 100
					TimePercent	= int(TimePercent)


					if TimePercent >= 80:	isWatched = '1'
					else:					isWatched = '0'


					Database.Update('Video', 'Video_ID', int(VideoID), {'Watched':isWatched, 'WatchDate':'DateTimeNow'})

from lib.Plugin import *
from lib.StoreSQLite import Store
import xbmc
import xbmcgui
import xbmcplugin


Monitor				= xbmc.Monitor()
Player				= xbmc.Player()
Playlist			= xbmc.PlayList(xbmc.PLAYLIST_VIDEO)


Addon_DatabaseFile	= getAddonDatabaseFile()
Database			= Store(Addon_DatabaseFile)


if __name__ == '__main__':
	while not Monitor.abortRequested():
		# Sleep/wait for abort for 10 seconds
		if Monitor.waitForAbort(1):
			# Abort was requested while waiting. We should exit
			break


		if Player.isPlayingVideo():
			#Log('is playing .. ')
			InfoTag			= Player.getVideoInfoTag()
			FileCurrent		= Player.getPlayingFile()
			AddonName		= getAddonInfo('name')


			getVideoTitle	= InfoTag.getTitle()
			getAddonName	= InfoTag.getWritingCredits()
			getVideoID		= InfoTag.getPlotOutline()


			if getAddonName == AddonName and getVideoID != '':
				#Log('video from addon .. ')


				TimeCurrent	= int(Player.getTime())
				TimeTotal	= int(Player.getTotalTime())

				TimePercent	= TimeCurrent / TimeTotal * 100
				TimePercent	= int(TimePercent)


				if TimePercent >= 80:
					Watched		= '1'
					WatchInfo	= 'Folge wurde geguckt'
				else:
					Watched		= None
					WatchInfo	= 'Folge ungeguckt'


				#blub = f'{TimeCurrent} / {TimeTotal} = {TimePercent} : {WatchInfo}'
				#Log(blub)


				LI = xbmcgui.ListItem(getVideoTitle)
				LI.setPath(FileCurrent)
				LI.setInfo('video', {'title'		: getVideoTitle})
				LI.setInfo('video', {'credits'		: getAddonName})
				LI.setInfo('video', {'plotoutline'	: getVideoID})
				LI.setInfo('video', {'genre'		: WatchInfo})
				Player.updateInfoTag(LI)


				Database.Update(
					'Video',
					'Video_ID',
					int(getVideoID),
					{
					'Watched'	:Watched,
					'WatchDate'	:'DateTimeNow'
					}
					)


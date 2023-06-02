from lib.StoreSQLite	import Store
from lib.Plugin			import *
from lib.GUI_Menu		import *
from lib.GUI_Option		import *
from lib.GUI_Other		import *
from lib.GUI_SQLCommand	import *
import xbmc
import xbmcgui
import xbmcplugin


# -----


PAGE_NAME		= SystemPage().get('PAGE_NAME', 	None)
PAGE_ID			= SystemPage().get('PAGE_ID',   	None)
PAGE_SUBID		= SystemPage().get('PAGE_SUBID',	None)


if PAGE_NAME is not None:	PAGE_NAME	= PAGE_NAME[0]
if PAGE_ID is not None:		PAGE_ID		= PAGE_ID[0]
if PAGE_SUBID is not None:	PAGE_SUBID	= PAGE_SUBID[0]


# -----


Addon_DatabaseFile	= getAddonDatabaseFile()
Database			= Store(Addon_DatabaseFile)


Player				= xbmc.Player()
Playlist			= xbmc.PlayList(xbmc.PLAYLIST_VIDEO)


# -----


if not Player.isPlaying():
	Playlist.clear()


# -----



if PAGE_NAME is None:
	SetPageTitle(getLang(10001))


	openPlaylist_By_UserInput(Database)
	openPlaylist_By_Addon()
	xbmcplugin.endOfDirectory(SystemID())


	#xbmcplugin.setContent(SystemID(), 'videos')
	#xbmc.executebuiltin('Container.SetViewMode(55)')
	#xbmc.executebuiltin('Container.NextViewMode')


	#files 	songs 	artists 	albums
	#movies 	tvshows 	episodes 	musicvideos
	#videos 	images 	games 	–


else:
	if PAGE_NAME == 'PlaylistAdd':
		SetPageTitle(getLang(11002))
		openMenu_Manager('Add',		PAGE_ID,	PAGE_SUBID,	Database)


	if PAGE_NAME == 'PlaylistEdit':
		SetPageTitle(getLang(11004))
		openMenu_Manager('Edit',	PAGE_ID,	PAGE_SUBID,	Database)


	if PAGE_NAME == 'PlaylistDelete':
		openMenu_Manager('Delete',	PAGE_ID,	PAGE_SUBID,	Database)


	if PAGE_NAME == 'Settings':
		openAddonSetttings()


	if PAGE_NAME == 'PlayPlaylist':
		openMenu_Playlist_Play(Database, PAGE_ID)

from lib.Plugin			import *
from lib.GUI_Menu		import *
from lib.GUI_Option		import *
from lib.GUI_SQLCommand	import *
import os
from itertools import islice, chain
from functools import partial
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs


# -----


def setListItem(Name, Poster='DefaultAddon', Icon='', Pager=[], Plot='', isFolder=True, PlayCounter=None):
	if Icon == '':
		Icon = Poster


	Poster	= getImage_CustomPath(Poster)
	Icon	= getImage_CustomPath(Icon)
	LI		= xbmcgui.ListItem(Name)


	if type(Pager) is str:
		URL		= Pager
	else:
		URL		= SetPager(Pager)
		LI.setArt({'poster'	: Poster})
		LI.setArt({'thumb'	: Icon})


	if PlayCounter is not None:
		LI.setInfo('video', {'playcount': PlayCounter})


	LI.setInfo('video',	{'plot'		: Plot})
	LI.setInfo('video',	{'title'	: Name})


	xbmcplugin.addDirectoryItem(
		handle		= SystemID(),
		url			= URL,
		listitem	= LI,
		isFolder	= isFolder
		)
	return LI


# -----


def getSerie_ListOverview(Data):
	if Data is None:
		return

	Count	= len(Data)
	Title	= ''
	Plot	= ''
	List	= []
	Break	= 0
	Stop	= 4


	if Count is None:
		return


	for Info in Data:
		InfoName	= Info['Serie_Name']
		StopCount	= Count - Stop
		Break		+= 1


		if InfoName is None:					InfoName = getLang(24201)
		if Break > Stop and StopCount != 1:		InfoName = getLang(24202, {'COUNT_SERIE':str(StopCount)})
		if Break > (Stop+1):					continue


		List.append(InfoName)


	List	= ('\n- '.join(List))
	List	= {'Count':str(Count), 'List':'- ' + List}
	return List


# -----


def setVideo_Update(Option, Database, PAGE_SUBID):
	OptionSupport = ['Playlist_EPP', 'Series_EPP', 'Series_Add', 'Series_Update', 'Series_Delete']


	if Option not in OptionSupport:
		return


	# Case: Playlist edit > select Series > delete Serie-Entry
	if Option == 'Series_Delete':
		Database.Delete('Video', 'Serie_ID', int(PAGE_SUBID))
		return



	# Nr.1 -- get PlaylistID as reference from Series
	if Option == 'Series_Add' or Option == 'Playlist_EPP':
		PlaylistID	= PAGE_SUBID
	else:
		getSerie	= Database.FetchOne(getSQLCommand_Serie_BySerieID(PAGE_SUBID))
		PlaylistID	= getSerie['Playlist_ID']
		PlaylistID	= str(PlaylistID)



	getPlaylist	= Database.FetchOne(getSQLCommand_Playlist_ByPlaylistID(PlaylistID))
	PlaylistEPP	= getPlaylist['Playlist_EPP']



	# Nr.2 -- get Series for looping the Path
	getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(PlaylistID))


	SerieData	= []
	for Serie in getSerie:
		SerieID		= Serie['Serie_ID']
		SeriePath	= Serie['Serie_Path']
		SerieEPP	= Serie['Serie_EPP']


		# Case: Playlist edit > select Series > edit path
		if Option == 'Series_Update':
			Database.Delete('Video', 'Serie_ID', int(SerieID))


		SerieVideos	= getVideo_PathOfSerie(SeriePath, SerieID)
		SerieData.append(
			{
			'ID'	: SerieID,
			'EPP'	: SerieEPP,
			'File'	: SerieVideos,
			}
			)


	VideoData	= getVideo_FileAsIter(SerieData)
	VideoData	= partial(getVideo_FileAsBlock, VideoData, PlaylistEPP)
	VideoData	= iter(VideoData, [])
	VideoData	= enumerate(VideoData)


	for VideoOrderMain, VideoBlock in VideoData:
		VideoBlock	= enumerate(VideoBlock)


		for VideoOrderSub, VideoInfo in VideoBlock:
			VideoPath	= VideoInfo['Path']
			SerieID		= VideoInfo['SerieID']
			VideoName	= os.path.basename(VideoPath)


			# Case: Playlist edit > Add Serie|Edit EPP > get exists videos
			if Option == 'Series_Add' or Option == 'Series_EPP' or Option == 'Playlist_EPP':
				# check if video in table existing/found
				SQLWHERE	= {
							"Video_Name='" + VideoName + "'",
							"Video_Path='" + VideoPath + "'",
							"Playlist_ID='" + str(PlaylistID) + "'",
							"Serie_ID='" + str(SerieID) + "'",
							}
				SQLWHERE	= sorted(SQLWHERE)
				SQLWHERE	= (' AND '.join(SQLWHERE))
				VideoInfo	= Database.FetchOne("SELECT * FROM Video WHERE " + SQLWHERE)


			# --


			# Series_Update
			if Option == 'Series_Update':
				Database.Insert(
					'Video',
					{
					'Video_Name'		: VideoName,
					'Video_Path'		: VideoPath,
					'Video_Order_Main'	: str(VideoOrderMain),
					'Video_Order_Sub'	: str(VideoOrderSub),
					'Playlist_ID'		: PlaylistID,
					'Serie_ID'			: str(SerieID)
					}
					)
			# Series_Update


			# --


			# Series_Add
			if Option == 'Series_Add':
				if VideoInfo is None:
					Database.Insert(
						'Video',
						{
						'Video_Name'		: VideoName,
						'Video_Path'		: VideoPath,
						'Video_Order_Main'	: str(VideoOrderMain),
						'Video_Order_Sub'	: str(VideoOrderSub),
						'Playlist_ID'		: PlaylistID,
						'Serie_ID'			: str(SerieID)
						}
						)
			# Series_Add


			# --


			# Series_EPP
			if Option == 'Series_EPP' or Option == 'Playlist_EPP':
				if VideoInfo is not None:
					Database.Update(
						'Video',
						'Video_ID',
						int(VideoInfo['Video_ID']),
						{
						'Video_Order_Main'	: str(VideoOrderMain),
						'Video_Order_Sub'	: str(VideoOrderSub)
						}
						)
			# Series_EPP


# -----


def getVideo_FileAsBlock(iterators, amount):
	return list(islice(
		chain.from_iterable(
			islice(iterator, amount)
			for amount, iterator in iterators
			),
		amount
		))


def getVideo_FileAsIter(Data):
	return [
		(nData['EPP'], iter(nData['File']))
		for nData in Data
		]


def getVideo_PathOfSerie(Path, SerieID):
	VideoTypes	= xbmc.getSupportedMedia('video')
	Data		= []
	Path		= xbmcvfs.validatePath(Path)	# set Windows-Like C:\blabla\ to C:/blabla/


	for osPath, osSubdirs, osFiles in os.walk(Path):
		for FileName in sorted(osFiles):
			getFileExt	= os.path.splitext(FileName)[-1].lower()


			# Ignore not Supported-Video-Extension
			if not getFileExt in VideoTypes:
				continue


			FilePath	= os.path.join(osPath, FileName)
			FilePath	= FilePath.encode('utf8', 'surrogateescape').decode('utf8')
			Data.append({'Path':FilePath, 'SerieID':SerieID})
	return Data


# ----


def getVideo_NameOfSerie(Path):
	Path		= xbmcvfs.validatePath(Path)	# set Windows-Like C:\blabla\ to C:/blabla/
	Path		= os.path.normpath(Path)
	Path		= Path.split(os.sep)
	Name		= Path[-1]						# get Last-Last Entry (Folder: blabla/bla/)
	SeasonLang	= ['Staffel', 'Season']


	# check if Season in Name
	# if true: make name like 'Series - Season X'
	if any(n.lower() in Name.lower() for n in SeasonLang) is True:
		Name	= Path[-2] + ' - ' + Name


	return Name


# -----


def getImage_CustomPath(Path):
	RePath		= xbmcvfs.validatePath(Path)	# set Windows-Like C:\blabla\ to C:/blabla/
	RePath		= RePath.split('.')


	if len(RePath) == 2:
		PosterTypes	= xbmc.getSupportedMedia('picture')
		Ext			= RePath[-1]


		if Ext in PosterTypes:
			return Path

	else:
		return Path + '.png'


# -----


def getImage_PlaylistIcon(Path, Default):
	Setting	= getAddonSetting('PlaylistOverviewIcon')


	if Setting == 'true':	return Path
	else:					return 'DefaultVideoPlaylists'
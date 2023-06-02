from lib.Plugin			import *
from lib.GUI_Menu		import *
from lib.GUI_Other		import *
from lib.GUI_SQLCommand	import *
import xbmcgui


# -----


def openOption_Playlist_Delete(Database):
	getPlaylist	= Database.FetchAll(getSQLCommand_Playlist_Overview())
	Dialog		= xbmcgui.Dialog()
	Data_Select	= []
	Data_List	= []
	ID			= 0


	for Playlist in getPlaylist:
		Data_Select.append(
			Playlist['Playlist_Name']
			)
		Data_List.append(
			{
			'ID'			: ID,
			'Playlist_ID'	: Playlist['Playlist_ID'],
			'Playlist_Name'	: Playlist['Playlist_Name']
			}
			)
		ID += 1


	# open Select-Dialog
	Select		= Dialog.select(
		heading	= getLang(13001),
		list	= Data_Select
		)


	# if dialog ..
	if Select >= 0:
		for List in Data_List:
			# check select-id = Playlist_ID
			if Select == List['ID']:
				Database.Delete('Playlist',	'Playlist_ID',	List['Playlist_ID'])
				Database.Delete('Serie',	'Playlist_ID',	List['Playlist_ID'])
				Database.Delete('Video',	'Playlist_ID',	List['Playlist_ID'])

		# Feedback to User
		Dialog.ok('Kodi', getLang(13002))


# -----


def openOption_Playlist_ReName(Database, PlaylistID):
	getInfo			= Database.FetchOne(getSQLCommand_Playlist_ByPlaylistID(PlaylistID))
	Name			= getInfo['Playlist_Name']
	Dialog			= xbmcgui.Dialog()
	Input			= Dialog.input(
		heading		= getLang(21101),
		defaultt	= Name,
		type		= xbmcgui.INPUT_ALPHANUM #standard keyboard
		)


	# 'cancel'
	if Name is None and Input == '':
		Dialog.ok('Kodi', getLang(21102))
		return 'Cancel'


	# 'cancel' or clear input
	if Name is not None and Input == '':
		return 'TakeStoreValue'


	if Input != '':
		Database.Update('Playlist', 'Playlist_ID', int(PlaylistID), {'Playlist_Name' : Input})
		return 'Update'


# -----


def openOption_Playlist_EPP(Database, PlaylistID):
	getInfo			= Database.FetchOne(getSQLCommand_Playlist_ByPlaylistID(PlaylistID))
	EPP				= getInfo['Playlist_EPP']
	SettingEPP		= getAddonSetting('EpisodePerDayByPlaylist')
	Input			= openOption_EPP(EPP, SettingEPP)


	if Input != '':
		Database.Update('Playlist', 'Playlist_ID', int(PlaylistID), {'Playlist_EPP' : str(Input)})


# -----


def openOption_Playlist_Poster(Database, PlaylistID):
	getInfo			= Database.FetchOne(getSQLCommand_Playlist_ByPlaylistID(PlaylistID))
	Dialog			= xbmcgui.Dialog()
	UserFolder		= getAddonSetting('PathToSeries')
	UserPoster		= getInfo['Playlist_Poster']
	Select			= 0


	if UserPoster is not None:
		Select			= Dialog.contextmenu(
							[
							getLang(22102),
							getLang(22103)
							]
							)


	if Select == -1:
		return


	if Select == 0:
		# Select Folder for Entry
		InputFolder		= Dialog.browseSingle(
			type		= 2, #ShowAndGetImage
			heading		= getLang(22101),
			shares		= 'pictures',
			defaultt	= UserFolder,
			useThumbs	= True
			)

	if Select == 1:
		Database.Update('Playlist', 'Playlist_ID', int(PlaylistID), {'Playlist_Poster' : None})
		return


	# 'cancel'
	if UserFolder == InputFolder:
		return


	# 'cancel'
	if  InputFolder == '':
		return


	Database.Update('Playlist', 'Playlist_ID', int(PlaylistID), {'Playlist_Poster' : InputFolder})


# -----


def openOption_Serie_Add(Database, PlaylistID):
	Dialog			= xbmcgui.Dialog()
	UserFolder		= getAddonSetting('PathToSeries')


	# Select Folder for Entry
	InputFolder		= Dialog.browseSingle(
		type		= 0, #ShowAndGetDirectory
		heading		= getLang(24103),
		shares		= 'video',
		defaultt	= UserFolder
		)


	# 'cancel'
	if UserFolder == InputFolder:
		return


	# Name for Serie
	Named		= getVideo_NameOfSerie(InputFolder)
	InputName	= Dialog.input(
		heading	= getLang(24104),
		defaultt= Named,
		type	= xbmcgui.INPUT_ALPHANUM
		)


	# 'cancel'
	if InputName == '':
		return


	getLastID	= Database.FetchOne("SELECT * FROM Serie ORDER BY Serie_Order DESC")


	if getLastID is None:	OrderNr	= 0
	else:					OrderNr = getLastID['Serie_Order'] + 1


	Database.Insert(
		'Serie',
		{
		'Playlist_ID'			:PlaylistID,
		'Serie_Order'			:OrderNr,
		'Serie_EPP'	:getAddonSetting('EpisodePerDayBySerie'),
		'Serie_Name'			:InputName,
		'Serie_Path'			:InputFolder,
		}
		)


# -----


def openOption_Serie_Edit(Type, Database, PAGE_SUBID):
	Dialog			= xbmcgui.Dialog()
	UserFolder		= getAddonSetting('PathToSeries')
	Select			= Dialog.contextmenu(
						[
						getLang(24107),
						getLang(24108),
						getLang(24109),
						getLang(24110),
						getLang(24111),
						getLang(24112),
						]
						)
	getSerieInfo	= Database.FetchOne(getSQLCommand_Serie_BySerieID(PAGE_SUBID))


	# set Order -1
	if Select == 0:
		openOption_MoveItem(Database, 'MoveUp', getSerieInfo)


	# set Order +1
	if Select == 1:
		openOption_MoveItem(Database, 'MoveDown', getSerieInfo)


	# Edit Name of Entry
	if Select == 2:
		InputName		= Dialog.input(
			heading		= getLang(24104),
			defaultt	= getSerieInfo['Serie_Name'],
			type		= xbmcgui.INPUT_ALPHANUM
			)


		if InputName != '':
			Database.Update('Serie', 'Serie_ID', int(PAGE_SUBID), {'Serie_Name':InputName})
		return 'Series_ReName'


	# Edit Path of Series
	if Select == 3:
		SeriePath		= getSerieInfo['Serie_Path']


		InputFolder		= Dialog.browseSingle(
			type		= 0, #ShowAndGetDirectory
			heading		= getLang(24103),
			shares		= 'video',
			defaultt	= SeriePath
			)


		if SeriePath != '':
			UserFolder	= SeriePath


		if UserFolder != InputFolder:
			Named		= getVideo_NameOfSerie(InputFolder)
			InputName	= Dialog.input(
				heading	= getLang(24104),
				defaultt= Named,
				type	= xbmcgui.INPUT_ALPHANUM
				)


			if InputName != '':
				Database.Update('Serie', 'Serie_ID', int(PAGE_SUBID), {'Serie_Path' :InputFolder, 'Serie_Name' :InputName})
		return 'Series_Path'


	# Edit EPP
	if Select == 4:
		SerieEPP		= getSerieInfo['Serie_EPP']
		SettingEPP		= getAddonSetting('EpisodePerDayBySerie')
		Input			= openOption_EPP(SerieEPP, SettingEPP)


		if Input != '':
			Database.Update('Serie', 'Serie_ID', int(PAGE_SUBID), {'Serie_EPP' : str(Input)})
		return 'Series_EPP'


	# Delete Entry
	if Select == 5:
		Database.Delete('Serie', 'Serie_ID', int(PAGE_SUBID))
		Database.Delete('Video', 'Serie_ID', int(PAGE_SUBID))
		return 'Series_Delete'


# -----


def openOption_EPP(EPP, Setting):
	if EPP == '' or EPP is None:
		EPP = Setting


	getEPP			= EPP - 1
	Dialog			= xbmcgui.Dialog()
	Input			= Dialog.select(
		heading		= getLang(23101),
		list		= [str(i).zfill(1) for i in range(1,100)],
		preselect	= getEPP
		)
	Input			= Input + 1


	if Input == 0:
		Input = EPP


	return Input


# -----


def openOption_MoveItem(Database, Option, Data):
	SelectID	= Data['Serie_ID']
	SelectOrder	= Data['Serie_Order']


	if Option == 'MoveUp':	SelectNew	= SelectOrder - 1
	else:					SelectNew	= SelectOrder + 1


	if Option == 'MoveUp':
		# item is already on top
		if SelectOrder == 0:
			return

	getNext		= Database.FetchOne("SELECT * FROM Serie WHERE Serie_Order='" + str(SelectNew) + "'")


	if Option == 'MoveDown':
		# serie is already on bottom
		if getNext is None:
			return


	NextID		= getNext['Serie_ID']
	NextOrder	= getNext['Serie_Order']


	Database.Update('Serie', 'Serie_ID',	int(SelectID),	{'Serie_Order':str(SelectNew)})
	Database.Update('Serie', 'Serie_ID',	int(NextID),	{'Serie_Order':str(SelectOrder)})

from lib.Plugin			import *
from lib.GUI_Option		import *
from lib.GUI_Other		import *
from lib.GUI_SQLCommand	import *
import os
import textwrap
import xbmcgui
import xbmcplugin


# -----


def openPlaylist_By_UserInput(Database):
	# get Playlists with Status=1
	getPlaylist = Database.FetchAll(getSQLCommand_Playlist_Overview())


	for Playlist in getPlaylist:
		ID			= Playlist['Playlist_ID']
		Name		= Playlist['Playlist_Name']
		Poster		= Playlist['Playlist_Poster']


		if Poster is None:
			Poster	= 'DefaultVideoPlaylists'


		getUnWatch	= Database.FetchOne(getSQLCommand_Video_UnWatched(ID))


		if getUnWatch is None:
			PlayCurrent		= getLang(12005)
			Name			= f'{Name} [I]({PlayCurrent})[/I]'

		else:
			OrderMain		= getUnWatch['Video_Order_Main']
			getVideo		= Database.FetchAll(getSQLCommand_Video_CurrentDay(ID, OrderMain, 'UnWatch'))
			CurrentDay		= str(OrderMain + 1)
			CurrentVideo	= len(getVideo)
			LangReplace		= {
				'DAY'			:CurrentDay,
				'EPISODE'		:CurrentVideo,
				}
			if CurrentVideo == 1:	PlayCurrent	= getLang(12003, LangReplace)
			else:					PlayCurrent	= getLang(12004, LangReplace)


		getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(ID))
		Serie_Info	= getSerie_ListOverview(getSerie)
		Serie_Plot	= Serie_Info['List']


		LI = setListItem(
			Name	= Name,
			Poster	= Poster,
			Icon	= getImage_PlaylistIcon(Poster, 'DefaultVideoPlaylists'),
			Pager	=	{
						'PAGE_NAME'	: 'PlayPlaylist',
						'PAGE_ID'	: ID
						},
			Plot	= getLang(12001) + '\n' + PlayCurrent + '\n\n' + getLang(12006) + '\n' + Serie_Plot,
			isFolder= True
			)
	#xbmcplugin.setResolvedUrl(
	#	handle		= SystemID(),
	#	succeeded	= True,
	#	listitem	= LI
	#	)


# -----


def openPlaylist_By_Addon():
	Data = []
	Data.append(
		{
		'Name'	:getLang(11002),
		'Icon'	:'DefaultAddSource',
		'Page'	:'PlaylistAdd',
		'Plot'	:getLang(11003),
		}
		)
	Data.append(
		{
		'Name'	:getLang(11004),
		'Icon'	:'DefaultAddonContextItem',
		'Page'	:'PlaylistEdit',
		'Plot'	:getLang(11005),
		}
		)
	Data.append(
		{
		'Name'	:getLang(11006),
		'Icon'	:'DefaultIconError',
		'Page'	:'PlaylistDelete',
		'Plot'	:getLang(11007),
		}
		)
	Data.append(
		{
		'Name'	:getLang(11008),
		'Icon'	:'DefaultAddonProgram',
		'Page'	:'Settings',
		'Plot'	:getLang(11009),
		}
		)
	for Playlist in Data:
		LI = setListItem(
			Name	= Playlist['Name'],
			Poster	= Playlist['Icon'],
			Pager	= {'PAGE_NAME': Playlist['Page']},
			Plot	= Playlist['Plot'],
			isFolder= True
			)
	xbmcplugin.setResolvedUrl(
		handle		= SystemID(),
		succeeded	= True,
		listitem	= LI
		)


# -----


def openMenu_Manager(Type, PAGE_ID, PAGE_SUBID, Database):
	Dialog		= xbmcgui.Dialog()
	TypeSupport = ['Add', 'Edit', 'Delete']


	if Type not in TypeSupport:
		return


	# Menu Playlist: Add
	if Type == 'Add':
		if PAGE_SUBID is None:
			# Check Table with Entry
			getPlaylist	= Database.FetchOne(getSQLCommand_Playlist_Add())


			# Check Table with Entry
			if getPlaylist is None:
				PAGE_SUBID = Database.Insert(	# No Entry = insert Entry
					'Playlist',
					{
					'Playlist_Status'	:'0',
					'Playlist_EPP'		:getAddonSetting('EpisodePerDayByPlaylist')
					}
					)
			else:
				PAGE_SUBID = getPlaylist['Playlist_ID']


			getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(PAGE_SUBID))


			openMenu_Playlist_Edit(Type, getPlaylist, getSerie, PAGE_SUBID)
	# Menu Playlist: Add



	# Menu Playlist: Edit
	if Type == 'Edit':
		if PAGE_SUBID is None:
			openMenu_Playlist_Overview(Database)

		else:
			if PAGE_ID is None:
				getPlaylist		= Database.FetchOne(getSQLCommand_Playlist_ByPlaylistID(PAGE_SUBID))
				getSerie		= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(PAGE_SUBID))

				openMenu_Playlist_Edit(Type, getPlaylist, getSerie, PAGE_SUBID)
	# Playlist: Edit



	# Menu Playlist: Delete
	if Type == 'Delete':
		openOption_Playlist_Delete(Database)
	# Menu Playlist: Delete



	# Edit Elements
	if Type == 'Add' or Type == 'Edit':
		if PAGE_ID == 'Playlist_ReName':
			openOption_Playlist_ReName(Database, PAGE_SUBID)


		# --


		if PAGE_ID == 'Playlist_EPP':
			openOption_Playlist_EPP(Database, PAGE_SUBID)
			setVideo_Update('Playlist_EPP', Database, PAGE_SUBID)


		# --


		if PAGE_ID == 'Playlist_Poster':
			openOption_Playlist_Poster(Database, PAGE_SUBID)


		# --


		if PAGE_ID == 'Series_Overview':
			openMenu_Series_Overview(Type, Database, PAGE_SUBID)


		# --


		if PAGE_ID == 'Series_Add':
			openOption_Serie_Add	(				Database, PAGE_SUBID)
			setVideo_Update			('Series_Add',	Database, PAGE_SUBID)


		# --


		if PAGE_ID == 'Series_Option':
			Option = openOption_Serie_Edit(Type, Database, PAGE_SUBID)

			# Update Videos only by edit Path|EPP|Delete
			if Option == 'Series_Path':			setVideo_Update('Series_Update',	Database, PAGE_SUBID)
			if Option == 'Series_EPP':			setVideo_Update('Series_EPP',		Database, PAGE_SUBID)
			if Option == 'Series_Delete':		setVideo_Update('Series_Delete',	Database, PAGE_SUBID)


		# --


		if Type == 'Add' and PAGE_ID == 'Playlist_SAVE':
			getPlaylist	= Database.FetchOne(getSQLCommand_Playlist_Add())
			Name		= getPlaylist['Playlist_Name']


			if Name is None:
				Dialog.ok('Kodi', getLang(26102))

			else:
				Database.Update('Playlist', 'Playlist_ID', int(PAGE_SUBID), {'Playlist_Status':'1', 'Playlist_Date_Create':'DateTimeNow'})

				# Feedback to User
				Dialog.ok('Kodi', getLang(26101))


		# --


		#if Type == 'Edit' and PAGE_ID == 'Videos_Overview_Simple':
		if PAGE_ID == 'Videos_Overview_Simple':
			openMenu_Playlist_Videos(Type, Database, PAGE_SUBID)
	# Edit Elements


# -----


def openMenu_Playlist_Edit(Type, Data_SQL_Add, Data_SQL_Serie, PAGE_SUBID):
	Name_Var		= ''
	Name_Title		= getLang(21003)
	Name_Plot		= getLang(21006)

	Poster_Var		= ''
	Poster_Icon		= 'DefaultPicture'
	Poster_Title	= getLang(22003)
	Poster_Plot		= getLang(22006)

	EPP_Var			= ''
	EPP_Title		= getLang(23003)
	EPP_Plot		= getLang(23006)


	if Data_SQL_Add is not None:
		Name_Var		= Data_SQL_Add['Playlist_Name']
		Poster_Var		= Data_SQL_Add['Playlist_Poster']
		EPP_Var			= Data_SQL_Add['Playlist_EPP']

		if Name_Var is not None:
			Name_Title		= Name_Var
			Name_Plot		= Name_Var

		if Poster_Var is not None:
			Poster_Icon		= Poster_Var
			Poster_Title	= getLang(22104)
			Poster_Plot		= ('\n'.join(textwrap.wrap(Poster_Var, 32)))

		if EPP_Var is not None:
			EPP_Title		= str(EPP_Var)
			EPP_Plot		= str(EPP_Var)
		else:
			EPP_Plot		= getAddonSetting('EpisodePerDayByPlaylist')

	# --


	Serie_Info	= getSerie_ListOverview(Data_SQL_Serie)
	Serie_Title	= Serie_Info['Count']
	Serie_Plot	= Serie_Info['List']


	# --


	if Type == 'Add':	TypePage	='PlaylistAdd'
	else:				TypePage	='PlaylistEdit'


	Data = []
	Data.append(
		{
		'Name'		: getLang(21001),
		#'Name'		: getLang(21001) + '    [COLOR yellow](' + getLang(21002) + ' ' + Name_Title + ')[/COLOR]',
		'Poster'	: 'DefaultAddonLanguage',
		'Page'		: TypePage,
		'ID'		: 'Playlist_ReName',
		'Plot'		: getLang(21004) + '\n\n' + getLang(21005) + '\n' + Name_Plot,
		}
		)
	Data.append(
		{
   		'Name'		: getLang(22001),
		#'Name'		: getLang(22001) + '    [COLOR yellow](' + getLang(22002) + ' ' + Poster_Title + ')[/COLOR]',
		'Poster'	: Poster_Icon,
		'Icon'		: 'DefaultPicture',
		'Page'		: TypePage,
		'ID'		: 'Playlist_Poster',
		'Plot'		: getLang(22004) + '\n\n' + getLang(22005) + '\n' + Poster_Plot,
		}
		)
	Data.append(
		{
      	'Name'		: getLang(23001),
		#'Name'		: getLang(23001) + '    [COLOR yellow](' + getLang(23002) + ' ' + EPP_Title + ')[/COLOR]',
		'Poster'	: 'DefaultAddonAudioDecoder',
		'Page'		: TypePage,
		'ID'		: 'Playlist_EPP',
		'Plot'		: getLang(23004) + '\n\n' + getLang(23005) + '\n' + EPP_Plot,
		}
		)
	Data.append(
		{
      	'Name'		: getLang(24001),
		#'Name'		: getLang(24001) + '    [COLOR yellow](' + getLang(24002) + ' ' + Serie_Title + ')[/COLOR]',
		'Poster'	: 'DefaultInProgressShows',
		'Page'		:  TypePage,
		'ID'		: 'Series_Overview',
		'Plot'		: getLang(24003) + '\n\n' + getLang(24004) + '\n' + Serie_Plot,
		}
		)
	Data.append(
		{
      	'Name'		: getLang(25001),
		'Poster'	: 'DefaultVideoPlaylists',
		'Page'		: TypePage,
		'ID'		: 'Videos_Overview_Simple',
		'Plot'		: getLang(25002),
		}
		)
	if Type == 'Add':
		Data.append(
			{
			'Name'		: getLang(26001),
			'Poster'	: 'DefaultAddSource',
			'Page'		: TypePage,
			'ID'		: 'Playlist_SAVE',
			'Plot'		: getLang(26002),
			}
			)
	for OptionItem in Data:
		if 'Icon' not in OptionItem:	Icon = OptionItem['Poster']
		else:							Icon = OptionItem['Icon']


		LI = setListItem(
			Name	= OptionItem['Name'],
			Poster	= OptionItem['Poster'],
			Icon	= Icon,
			Pager	=	{
						'PAGE_NAME'		: OptionItem['Page'],
						'PAGE_ID'		: OptionItem['ID'],
						'PAGE_SUBID'	: PAGE_SUBID
						},
			Plot	= OptionItem['Plot'],
			isFolder= True
			)
	xbmcplugin.setResolvedUrl(
		handle		= SystemID(),
		succeeded	= True,
		listitem	= LI
		)
	xbmcplugin.endOfDirectory(SystemID())


# -----


def openMenu_Playlist_Overview(Database):
	getPlaylist		= Database.FetchAll(getSQLCommand_Playlist_Overview())


	if len(getPlaylist) == 0:
		return


	for Playlist in getPlaylist:
		ID			= Playlist['Playlist_ID']
		Name		= Playlist['Playlist_Name']
		Poster		= Playlist['Playlist_Poster']


		if Poster is None:
			Poster	= 'DefaultVideoPlaylists'


		getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(ID))
		Serie_Info	= getSerie_ListOverview(getSerie)
		Serie_Plot	= Serie_Info['List']


		LI = setListItem(
			Name	= Name,
			Poster	= Poster,
			Icon	= getImage_PlaylistIcon(Poster, 'DefaultAddonContextItem'),
			Pager	=	{
						'PAGE_NAME'	: 'PlaylistEdit',
						'PAGE_SUBID': ID
						},
			Plot	= getLang(27001) + '\n\n' + getLang(27002) + '\n' + Serie_Plot,
			isFolder= True
			)
	xbmcplugin.setResolvedUrl(
		handle		= SystemID(),
		succeeded	= True,
		listitem	= LI
		)
	xbmcplugin.endOfDirectory(SystemID())


# -----


def openMenu_Series_Overview(Type, Database, PlaylistID):
	if Type == 'Add':	PAGE	= 'PlaylistAdd'
	if Type == 'Edit':	PAGE	= 'PlaylistEdit'


	LI = setListItem(
		Name	= getLang(24101),
		Poster	= 'DefaultAddSource',
		Pager	=	{
					'PAGE_NAME'	: PAGE,
					'PAGE_ID'	: 'Series_Add',
					'PAGE_SUBID': PlaylistID
					},
		Plot	= getLang(24102),
		isFolder= True
		)
	getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(PlaylistID))


	for Serie in getSerie:
		SerieID		= Serie['Serie_ID']
		SerieName	= Serie['Serie_Name']
		SeriePath	= Serie['Serie_Path']
		SeriePath	= ('\n'.join(textwrap.wrap(SeriePath, 32)))
		SerieEPP	= str(Serie['Serie_EPP'])


		if SerieName is None:
			SerieName	= getLang(24115)


		VideoCount	= Database.FetchOne("SELECT COUNT(*) AS Counter FROM Video WHERE Playlist_ID='" + str(PlaylistID) + "' AND Serie_ID='" + str(SerieID) + "'")
		VideoCount	= VideoCount['Counter']


		if VideoCount == 1:
			SerieName	= SerieName + '    ' + getLang(24113, {'EPISODE_COUNT':str(VideoCount)})
		else:
			SerieName	= SerieName + '    ' + getLang(24114, {'EPISODE_COUNT':str(VideoCount)})


		LI = setListItem(
			Name	= SerieName,
			Poster	= 'DefaultInProgressShows',
			Pager	=	{
						'PAGE_NAME'	: PAGE,
						'PAGE_ID'	: 'Series_Option',
						'PAGE_SUBID': SerieID
						},
			Plot	= getLang(24105) + '\n' + SerieEPP + '\n\n' + getLang(24106) + '\n' + SeriePath,
			isFolder= True
			)
	xbmcplugin.setResolvedUrl(
		handle		= SystemID(),
		succeeded	= True,
		listitem	= LI
		)
	xbmcplugin.endOfDirectory(SystemID())


# -----


def openMenu_Playlist_Videos(Type, Database, PAGE_SUBID):
	if Type != 'Add' and Type != 'Edit':
		return

	SetPageTitle(getLang(25104), 'ContentAsSerie')

	xbmcplugin.setContent(SystemID(), 'episodes')
	"""
	files
	songs 	artists 	albums
	movies 	tvshows 	episodes
	musicvideos
	videos 	images 	games
	–
	"""

	Dialog			= xbmcgui.Dialog()
	getVideoMain	= Database.FetchAll(
		"""
		SELECT
			Video_Order_Main
		FROM
			Video
		WHERE
			Video.Playlist_ID='""" + PAGE_SUBID + """'
		GROUP By
			Video_Order_Main
		ORDER BY
			Video_Order_Main ASC
		"""
		)


	# no videos found
	if len(getVideoMain) == 0:
		getSerie	= Database.FetchAll(getSQLCommand_Serie_ByPlaylistID(PAGE_SUBID))


		if len(getSerie) == 0:	Name = getLang(25105)
		else:					Name = getLang(25106)


		LI = setListItem(
			Name	= Name,
			Poster	= 'DefaultIconError',
			Pager	=	{
						'PAGE_NAME'		: 'PlaylistEdit',
						'PAGE_ID'		: 'Videos_Overview_Simple',
						'PAGE_SUBID'	: PAGE_SUBID
						},
			#Plot	= '',
			isFolder= True
			)
		xbmcplugin.setResolvedUrl(
			handle		= SystemID(),
			succeeded	= True,
			listitem	= LI
			)
		xbmcplugin.endOfDirectory(SystemID())
		return


	for mVideo in getVideoMain:
		mOrderMain	= mVideo['Video_Order_Main']
		mOrderName	= mOrderMain + 1
		#mOrderName	= ('{:03}'.format(mOrderMain))


		getCount	=Database.FetchOne(
			"""
			SELECT
				(SELECT COUNT(*) FROM Video WHERE Playlist_ID='""" + str(PAGE_SUBID) + """' AND Video_Order_Main='""" + str(mOrderMain) + """' AND Watched='1')
				AS CountWatch,
				(SELECT COUNT(*) FROM Video WHERE Playlist_ID='""" + str(PAGE_SUBID) + """' AND Video_Order_Main='""" + str(mOrderMain) + """')
				AS CountEntry
			"""
			)


		if getCount['CountWatch'] == getCount['CountEntry']:
			mWatched	= 1
		else:
			mWatched	= 0


		if getCount['CountEntry'] == 1:
			EntryName	= str(getCount['CountEntry']) + ' ' + getLang(25102)
		else:
			EntryName	= str(getCount['CountEntry']) + ' ' + getLang(25103)


		LI = setListItem(
			Name		= '[COLOR yellow][B][I]' + getLang(25101) + ' ' + str(mOrderName) + '[/I][/B]    (' + EntryName + ')[/COLOR]',
			Poster		= 'DefaultYear',
			Pager		=	{
							'PAGE_NAME'		: 'PlaylistEdit',
							'PAGE_ID'		: 'Videos_Overview_Simple',
							'PAGE_SUBID'	: PAGE_SUBID
							},
			Plot		= '',
			isFolder	= True,
			PlayCounter	= mWatched
			)
		getVideoSub	= Database.FetchAll(getSQLCommand_Video_CurrentDay(PAGE_SUBID, mOrderMain))


		for sVideo in getVideoSub:
			sWatched	= sVideo['Watched']
			sVideoName	= sVideo['Video_Name']
			sVideoPath	= sVideo['Video_Path']


			if sWatched is None:
				sWatched	= 0


			LI = setListItem(
				Name		= sVideoName,
				Pager		= sVideoPath,
				isFolder	= False,
				PlayCounter	= sWatched
				)

	xbmcplugin.setResolvedUrl(
		handle		= SystemID(),
		succeeded	= True,
		listitem	= LI
		)
	xbmcplugin.endOfDirectory(SystemID())


# -----


def openMenu_Playlist_Play(Database, PlaylistID):
	getLastUnWatch	= Database.FetchOne(getSQLCommand_Video_UnWatched(PlaylistID))


	if getLastUnWatch is None:
		Dialog		= xbmcgui.Dialog()
		Dialog.ok('Kodi', getLang(12007))
		return


	Database.Update('Playlist', 'Playlist_ID', int(PlaylistID), {'Playlist_Date_LastAccess':'DateTimeNow'})


	getLastUnWatch	= getLastUnWatch['Video_Order_Main']
	getLastUnWatch	= str(getLastUnWatch)
	getVideo		= Database.FetchAll(getSQLCommand_Video_CurrentDay(PlaylistID, getLastUnWatch, 'UnWatch'))


	Player			= xbmc.Player()
	Playlist		= xbmc.PlayList(xbmc.PLAYLIST_VIDEO)


	for Video in getVideo:
		Video_ID	= Video['Video_ID']
		Video_Name	= Video['Video_Name']
		Video_Path	= Video['Video_Path']
		Video_OM	= Video['Video_Order_Main']


		LI			= xbmcgui.ListItem(Video_Name)
		LI.setInfo('video', {'title'	: Video_Name})
		#LI.setInfo('video', {'director'	: [getAddonInfo('name'), Video_ID]}) # to get video_id at playing
		#LI.setInfo('video', {'genre'	: 'test'}) # to get video_id at playing


		LI.setInfo('video', {'credits'		: getAddonInfo('name')})	# to referer to this addon to playlist
		LI.setInfo('video', {'plotoutline'	: Video_ID})				# to get video_id to playlist


		Playlist.add(
			url			= Video_Path,
			listitem	= LI
			)
	Player.play(Playlist, LI, False)

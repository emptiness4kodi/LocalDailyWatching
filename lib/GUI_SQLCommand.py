from lib.Plugin			import *
from lib.GUI_Menu		import *
from lib.GUI_Option		import *
from lib.GUI_Other		import *

# -----


def getSQLCommand_Playlist_Overview():
	Sorts	= getAddonSetting('PlaylistOverviewSort')

	if Sorts == '0':	Sorts = 'Playlist_Name ASC'
	if Sorts == '1':	Sorts = 'Playlist_Date_LastAccess DESC'
	if Sorts == '2':	Sorts = 'Playlist_Date_Create ASC'


	return "SELECT * FROM Playlist WHERE Playlist_Status='1' ORDER By " + Sorts


# -----


def getSQLCommand_Playlist_Add():
	return "SELECT * FROM Playlist WHERE Playlist_Status='0'"


# -----


def getSQLCommand_Playlist_ByPlaylistID(PlaylistID):
	return "SELECT * FROM Playlist WHERE Playlist_ID='" + str(PlaylistID) + "'"


# -----


def getSQLCommand_Video_UnWatched(PlaylistID):
	return "SELECT * FROM Video WHERE Playlist_ID='" + str(PlaylistID) + "' AND Watched is NULL ORDER By Video_Order_Main ASC"


# -----


def getSQLCommand_Video_CurrentDay(PlaylistID, OrderMain, Option='List'):
	if Option == 'UnWatch':	Option = 'AND Video.Watched is NULL'
	if Option == 'List':	Option = ''


	return """
			SELECT
				*
			FROM
				Video
			LEFT JOIN
				Serie
				ON Serie.Serie_ID = Video.Serie_ID
			WHERE
				Video.Playlist_ID='""" + str(PlaylistID) + """'
				AND
				Video.Video_Order_Main='""" + str(OrderMain) + """'
				""" + Option + """
			ORDER By
				Video.Video_Order_Main ASC,
				Serie.Serie_Order ASC,
				Video.Video_Order_Sub ASC
			"""


# -----


def getSQLCommand_Serie_ByPlaylistID(PlaylistID):
	return "SELECT * FROM Serie WHERE Playlist_ID='" + str(PlaylistID) + "' ORDER BY Serie_Order ASC"


# -----


def getSQLCommand_Serie_BySerieID(SerieID):
	return "SELECT * FROM Serie WHERE Serie_ID='" + str(SerieID) + "'"
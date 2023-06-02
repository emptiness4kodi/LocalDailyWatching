from lib.Plugin import *
import sqlite3
import xbmcgui
import xbmcvfs
import datetime


class Store():
	def __init__(self, Pathfile):
		try:
			con				= sqlite3.connect(Pathfile)
			con.row_factory	= sqlite3.Row
			cur				= con.cursor()

			self.__con		= con
			self.__cur		= cur

		except sqlite3.Error as SQLiteError:
			Log('SQL-Error: ' + (' '.join(SQLiteError.args)))
		#con.close()



		Check	= self.__StructurCheck()
		Log		= self.__StructurUpdate(Check)



	# -----


	def __query(self, Command, Parameter=()):
		try:
			Statement = self.__cur.execute(Command, Parameter)

		except sqlite3.Error as SQLiteError:
			Log('SQL-Error: ' + (' '.join(SQLiteError.args)))

		else:
			return Statement


	# -----



	def FetchOne(self, Command):
		Statement = self.__query(Command)
		return Statement.fetchone()


	# -----


	def FetchAll(self, Command):
		Statement = self.__query(Command)
		return Statement.fetchall()


	# -----


	def Insert(self, TableName, ColumnList=[]):
		nVar	= []
		for n in ColumnList:
			nVar.append('?')

		Divider		= ', '
		ColumnName	= Divider.join(ColumnList.keys())	# Column, Column, ..
		ColumnValue	= list(ColumnList.values())			# [Value, Value, ..]
		ColumnVar	= Divider.join(nVar)				# ?, ?, ..

		Command		= "INSERT INTO " + str(TableName) + " (" + ColumnName + ") VALUES (" + ColumnVar + ")"


		try:
			self.__query(Command, ColumnValue)
			self.__con.commit()

		except sqlite3.Error as SQLiteError:
			Log('SQL-Error: ' + (' '.join(SQLiteError.args)))

		else:
			#if self.__cur.lastrowid is None:
			#	Log(getLang(41001) + ' ' + Command + " // " + str(ColumnValue))
			#else:
			#	Log(getLang(41002) + ' ' + Command + " // " + str(ColumnValue))

			return self.__cur.lastrowid


	# -----


	def Update(self, TableName, WhereColumn, WhereID, ColumnList=[]):
		Data	= []
		for Columns in ColumnList.items():
			if Columns[1] == 'DateTimeNow':	Data.append(Columns[0] + "=datetime('now')")
			elif Columns[1] == None:		Data.append(Columns[0] + "=NULL")
			else:							Data.append(Columns[0] + '="' + Columns[1] + '"')


		Divider		= ', '
		ColumnName	= Divider.join(Data)	# Column='Value', Column='Value', ..
		Command		= "UPDATE " + str(TableName) + " SET " + ColumnName + " WHERE " + str(WhereColumn) + "='" + str(WhereID) + "'"


		try:
			self.__query(Command)
			self.__con.commit()

		except sqlite3.Error as SQLiteError:
			Log('SQL-Error: ' + (' '.join(SQLiteError.args)))

		#else:
			#if self.__cur.rowcount == 0:
			#	Log(getLang(42001) + ' ' + Command)
			#else:
			#	Log(getLang(42002) + ' ' + Command)


	# -----


	def Delete(self, TableName, WhereColumn, WhereID):
		Command		= "DELETE FROM " + str(TableName) + " WHERE " + str(WhereColumn) + "='" + str(WhereID) + "'"


		try:
			self.__query(Command)
			self.__con.commit()

		except sqlite3.Error as SQLiteError:
			Log('SQL-Error: ' + (' '.join(SQLiteError.args)))


	# -----


	def __StructurBuild(self):
		List	= []
		Data	= []
		List.append(
			{
			'Table'	:'Playlist',
			'SQL'	:
					"""
					CREATE TABLE "Playlist" (
						"Playlist_ID"	INTEGER,
						"Playlist_Name"	TEXT,
						"Playlist_Poster"	TEXT,
						"Playlist_EPP"	INTEGER,
						"Playlist_Status"	INTEGER,
						"Playlist_Date_Create"	TEXT,
						"Playlist_Date_LastAccess"	TEXT,
						PRIMARY KEY("Playlist_ID" AUTOINCREMENT)
					)
					"""
			}
			)
		List.append(
			{
			'Table'	:'Serie',
			'SQL'	:
					"""
					CREATE TABLE "Serie" (
						"Serie_ID"	INTEGER,
						"Playlist_ID"	INTEGER,
						"Serie_Order"	INTEGER,
						"Serie_EPP"	INTEGER,
						"Serie_Name"	TEXT,
						"Serie_Path"	TEXT,
						PRIMARY KEY("Serie_ID" AUTOINCREMENT)
					)
					"""
			}
			)
		List.append(
			{
			'Table'	:'Video',
			'SQL'	:
					"""
					CREATE TABLE "Video" (
						"Video_ID"	INTEGER,
						"Playlist_ID"	INTEGER,
						"Serie_ID"	INTEGER,
						"Video_Order_Main"	INTEGER,
						"Video_Order_Sub"	INTEGER,
						"Watched"	INTEGER,
						"WatchDate"	TEXT,
						"Video_Name"	TEXT,
						"Video_Path"	TEXT,
						PRIMARY KEY("Video_ID" AUTOINCREMENT)
					)
					"""
			}
			)

		for Command in List:
			Table	= Command['Table']
			SQL		= Command['SQL']

			SQL		= SQL.strip()
			SQL		= SQL.replace("\t\t\t\t\t", "")

			Data.append({'Table':Table, 'SQL':SQL})
		return Data


	# -----


	def __StructurCheck(self):
		Command	= self.__StructurBuild()
		CheckUp	= []


		for Item in Command:
			Table	= Item['Table']
			SQL		= Item['SQL']
			Shema	= self.FetchOne("SELECT sql FROM sqlite_master WHERE tbl_name = '" + Table + "'")


			if Shema is None:
				CheckUp.append({'Table':Table, 'Shema_Addon':SQL, 'Shema_DB':''})
				continue


			if SQL != Shema['sql']:
				CheckUp.append({'Table':Table, 'Shema_Addon':SQL, 'Shema_DB':Shema['sql']})


		if len(CheckUp) == 0:
			return True
		else:
			return CheckUp


	# -----


	def __StructurUpdate(self, Data):
		if Data is True:
			return True


		TimeCurrent	= datetime.datetime.now()
		TimeCurrent	= TimeCurrent.strftime("%Y-%m-%d_%H-%M-%S")


		StoreFile	= getAddonInfo('path') + '/store.db'
		Store_Old	= getAddonInfo('path') + '/store_old_' + TimeCurrent + '.db'


		getFile		= xbmcvfs.File(StoreFile)
		FileSize	= getFile.size()
		getFile.close()


		if FileSize > 0:
			CopySQLFile	= xbmcvfs.rename(StoreFile, Store_Old)

			#Log('CopySQLFile')
			#Log(CopySQLFile)


			con				= sqlite3.connect(StoreFile)
			con.row_factory	= sqlite3.Row
			cur				= con.cursor()

			self.__con		= con
			self.__cur		= cur


			Dialog = xbmcgui.Dialog()
			Dialog.ok('Kodi', getLang(43001))


		for Command in self.__StructurBuild():
			Table	= Command['Table']
			SQL		= Command['SQL']
			self.__query(SQL)
		return
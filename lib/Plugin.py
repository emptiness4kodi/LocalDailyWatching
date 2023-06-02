import sys
import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs
import xbmc
import xbmcplugin
import xbmcaddon


# ----


def Log(Text):
	xbmc.log("LOG-INFO\n" + str(Text), xbmc.LOGINFO)
	#xbmc.log("LOG-INFO\t\t" + str(Text), xbmc.LOGINFO)


# ----


def SystemURL():
	return sys.argv[0]


# ----


def SystemID():
	return int(sys.argv[1])


# ----


def SystemPage():
	Page = sys.argv[2][1:]
	Page = urllib.parse.urlparse(Page).path
	Page = urllib.parse.parse_qs(Page)
	return Page


# ----


def SetPager(query):
	return SystemURL() + '?' + urllib.parse.urlencode(query)


# ----


def SetPageTitle(Name, Type=''):
	if Type == '':	Type = getAddonInfo('name') + ' / '
	else:			Type = ''
	xbmcplugin.setPluginCategory(SystemID(), Type + Name)


# ----


def getAddon():
	Addon	= xbmcaddon.Addon()
	return Addon


# ----


def getAddonInfo(Name):
	Addon	= getAddon()
	Addon	= Addon.getAddonInfo(Name)
	return Addon


# ----


def getAddonDatabaseFile():
	return getAddonInfo('path') + 'store.db'


# ----


def getAddonSetting(Name):
	Addon	= getAddon()
	Addon	= Addon.getSetting(Name)
	return Addon


# ----


def openAddonSetttings():
	Addon	= getAddon()
	Addon.openSettings()


# ----


def getLang(ID, Replace=None):
	LangString = getAddon().getLocalizedString(ID)
	LangString = getLangColorSkin(LangString)


	if type(Replace) is dict:
		for itemKey, itemValue in Replace.items():
			LangString = LangString.replace(f'[{itemKey}]', itemValue)


	return LangString





def getLangColorSkin(LangString):
	import json
	import re


	getSkin		= xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue", "params":{"setting":"lookandfeel.skin"},"id":1}')
	getSkin		= json.loads(getSkin)
	getSkin		= getSkin['result']['value']

	Default		= 'skin.estuary'


	if getSkin == Default:
		ReString	= LangString
	else:
		ReString	= re.sub('\[COLOR button_focus\](.*)\[/COLOR\]', '\\1', LangString)

	return ReString

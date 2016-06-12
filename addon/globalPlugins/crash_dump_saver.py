#crash_dump_saver: Main plugin code.
#copyright Derek Riemer 2016.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import datetime
import re
import os
import shutil
import tempfile
import globalPluginHandler
import api
import gui
import config
import wx

def confDialog(evt):
	cs = CrashSettings(gui.mainFrame)
	gui.mainFrame.prePopup()
	cs.Show()
	gui.mainFrame.postPopup()

class CrashSettings(gui.SettingsDialog):
	#Translators: Title of the settings dialog.
	title = _("Crash settings.")

	def makeSettings(self, settingsSizer):
		self.folderName = config.conf["crashSaver"]["dir"]
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		#Translators: Label that appears next to the current directory display.
		sizer.Add(wx.StaticText(self, wx.ID_ANY, label = _("Current Directory")))
		self.edit = item = wx.TextCtrl(self, size=(500, 100))
		item.SetValue(self.folderName)
		sizer.Add(item)
		settingsSizer.Add(sizer)
		#Translators: A button that brings up a dialog to pick a folder.
		dirButton = wx.Button(self, wx.ID_ANY, label=_("Pick a Folder"))
		dirButton.Bind(wx.EVT_BUTTON, self.onDirButtonAction)
		settingsSizer.Add(dirButton)
	
	def onDirButtonAction(self, evt):
		self.Hide()
		dirDialog = wx.DirDialog(self, style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST, defaultPath = self.folderName)
		dirDialog.Center()
		result = dirDialog.ShowModal()
		self.edit.Value = dirDialog.Path
		self.Show()
	
	def postInit(self):
		self.edit.SetFocus()
	
	def onOk(self, evt):
		config.conf["crashSaver"]["dir"] = self.edit.Value
		self.Destroy()

def crashDialog():
	#Translators: Title of a dialog shown at startup of NVDA.
	dialog = wx.Dialog(gui.mainFrame, wx.ID_OK, title=_("NVDA Crashed!"), size = (500,500))
	dialog.Center()
	mainSizer = wx.BoxSizer(wx.VERTICAL)
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	#Translators: Message NVDA presents for crashes.
	sizer.Add(wx.StaticText(dialog, wx.ID_ANY, _("Type what you were doing whenn NVDA crashed")))
	text = wx.TextCtrl(dialog, wx.ID_ANY,  style=wx.TE_MULTILINE)
	sizer.Add(text)
	mainSizer.Add(sizer)
	sizer = wx.BoxSizer(wx.HORIZONTAL)
	ok = wx.Button(dialog, wx.ID_OK)
	sizer.Add(ok)
	mainSizer.Add(sizer)
	mainSizer.Fit(dialog)
	gui.mainFrame.prePopup()
	dialog.ShowModal()
	gui.mainFrame.postPopup()
	result = text.Value
	dialog.Destroy()
	return result

def saveCrash():
	message = crashDialog()
	timestamp = datetime.datetime.now().strftime("%a %d %B %Y %H-%M-%S") #colons aren't allowed in file names.
	msg = message.split(" ", 5)
	#Some characters like : aren't file safe. Just remove them.
	mst = (msg[:-1] if len(msg) > 5 else msg) #It's a list and we need a string.
	msg = " ".join(msg)
	msg = re.sub(r"[^a-zA-Z0-9_ -]", "", msg)
	folderName = timestamp + " "+msg
	userDir = config.conf["crashSaver"]["dir"]
	
	#translators: the plural word for crash in your language.
	crashDir = os.path.join(userDir, _("crashes"))
	if not os.path.exists(crashDir):
		os.mkdir(crashDir)
	crashDir = os.path.join(crashDir, folderName)
	os.mkdir(crashDir)
	temp = tempfile.gettempdir()
	try:
		shutil.move(os.path.join(temp, "nvda_crash.dmp"), crashDir) #No need to check existance. See above.
	except Exception as e:
		gui.messageBox("check the log please")
		raise e
	with open(os.path.join(crashDir, "message.txt"), "w") as messageFile:
		messageFile.write(message)
	gui.messageBox(crashDir, "the NVDA crash is in this directory.")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		config.conf.spec["crashSaver"] = {
			"dir" : "string(default={})".format(os.path.expanduser("~"))
		}
		temp = tempfile.gettempdir()
		if os.path.exists(os.path.join(temp, "nvda_crash.dmp")):
			wx.CallAfter(saveCrash) #call after NVDA is ready to pop up gui stuff.
		prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
		#Translators: Message for setting the Crash saver preferences.
		item = prefsMenu.Append(wx.ID_ANY, _("Crash Saver Settings ..."))
		prefsMenu.Parent.Bind(wx.EVT_MENU, confDialog, item)
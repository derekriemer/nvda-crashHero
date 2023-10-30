#crash_dump_saver: Main plugin code.
#copyright Derek Riemer 2016-2023.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import datetime
import re
import os
import shutil
import tempfile
import globalPluginHandler
import api
from scriptHandler import script
import gui
import config
import wx
import sys
from gui import guiHelper

def confDialog(evt):
	gui.mainFrame._popupSettingsDialog(CrashSettings)

class CrashSettingsPanel(gui.settingsDialogs.SettingsPanel):
	#Translators: Title of the settings dialog.
	title = _("Crash Hero")

	def makeSettings(self, settingsSizer):
		self.folderName = config.conf["crashSaver"]["directory"]
		self.crashDirectory = guiHelper.PathSelectionHelper(self, "Browse", "Choose your crash selection Directory")
		self.crashDirectory.pathControl.Value = self.folderName

	def onSave(self):
		curProfile = config.conf.profiles[-1].name
		config.conf.manualActivateProfile(None)
		if os.path.exists(self.crashDirectory.pathControl.Value):
			config.conf["crashSaver"]["directory"] = self.crashDirectory.pathControl.Value
		else:
			gui.messageBox(_("That folder doesn't exist. Enter a valid folder name."))
		config.conf.manualActivateProfile(curProfile)

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
	userFriendlyTimestamp = datetime.datetime.now().strftime("%a %d %B %Y %H:%M:%S")
	msg = message.split(" ", 5)
	msg = " ".join(msg)
	#sanatize files.
	msg = re.sub(r"[^a-zA-Z0-9_ -]", "", msg)
	folderName = timestamp + " "+msg
	userDir = config.conf["crashSaver"]["directory"]
	
	#translators: the plural word for crash in your language.
	crashDir = os.path.join(userDir, _("crashes"))
	if not os.path.exists(crashDir):
		os.mkdir(crashDir)
	crashDir = os.path.join(crashDir, folderName)
	os.mkdir(crashDir)
	temp = tempfile.gettempdir()
	try:
		shutil.move(os.path.join(temp, "nvda_crash.dmp"), crashDir) #No need to check existance. See above.
		shutil.move(os.path.join(temp, "nvda-old.log"), crashDir) #No need to check existance. See above.
	except Exception as e:
		gui.messageBox("check the log please")
		raise e
	with open(os.path.join(crashDir, "message.txt"), "w") as messageFile:
		messageFile.write("The crash occured at {0}\n".format(userFriendlyTimestamp))
		messageFile.write("User supplied message:\n\n")
		messageFile.write(message)
	gui.messageBox(crashDir, "the NVDA crash is in this directory.")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		config.conf.spec["crashSaver"] = {
			"directory" : "string(default=\"{}\")".format(os.path.expanduser("~"))
		}
		config.conf.BASE_ONLY_SECTIONS.add("crashSaver")
		temp = tempfile.gettempdir()
		if os.path.exists(os.path.join(temp, "nvda_crash.dmp")):
			wx.CallAfter(saveCrash) #call after NVDA is ready to pop up gui stuff.
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CrashSettingsPanel)

	def terminate(self):
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(CrashSettingsPanel)
		except IndexError:
			pass

	# Intentionally untranslated. We don't need to care about translation this developer only feature.
	@script(description="fakes a crash of NVDA on purpose", category="Crash Hero")
	def script_crash(self, gesture):
		# Does not actually crash NVDA. I'm not publishing code that actually does that.
		d=open(os.path.join(tempfile.gettempdir(), "nvda_crash.dmp"), "w")
		d.write("This is a test file.")
		d.close()
		#Import late to prevent perf hit in 99% of cases.
		import core
		core.restart()

#-*- coding:utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

import addonHandler
from logHandler import log
try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	log.warning("Unable to initialise translations. This may be because the addon is running from NVDA scratchpad.")

import os
_addonDir = os.path.join(os.path.dirname(__file__), "..", "..")
if isinstance(_addonDir, bytes):
	_addonDir = _addonDir.decode("mbcs")
_curAddon = addonHandler.Addon(_addonDir)
_addonName = _curAddon.manifest['name']
_addonSummary = _curAddon.manifest['summary']

import globalPluginHandler
import synthDriverHandler
from threading import Thread
from time import sleep
from tones import beep
import gui
import config
from .settings import UnmuteSettingsPanel


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Implementation global commands of NVDA add-on"""
	scriptCategory = str(_addonSummary)

	def __init__(self, *args, **kwargs):
		"""Initializing initial configuration values ​​and other fields"""
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		confspec = {
			"max": "boolean(default=true)",
			"volume": "integer(default=90,min=0,max=100)",
			"minlevel": "integer(default=20,min=0,max=100)",
			"reinit": "boolean(default=true)",
			"retries": "integer(default=0,min=0,max=10000000)"
		}
		config.conf.spec[_addonName] = confspec
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(UnmuteSettingsPanel)
		Thread(target=self.unmuteAudio).start()
		if config.conf[_addonName]['reinit']:
			Thread(target=self.resetSynth).start()

	def terminate(self, *args, **kwargs):
		"""This will be called when NVDA is finished with this global plugin"""
		super().terminate(*args, **kwargs)
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(UnmuteSettingsPanel)
		except IndexError:
			log.warning("Can't remove %s Settings panel from NVDA settings dialogs", _addonSummary)

	def unmuteAudio(self) -> None:
		"""Turns on Windows sound if it is muted or low."""
		from ctypes import cast, POINTER
		from comtypes import CLSCTX_ALL
		from .pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
		devices = AudioUtilities.GetSpeakers()
		interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
		volume = cast(interface, POINTER(IAudioEndpointVolume))
		if volume.GetMute():
			volume.SetMute(False, None)
		if volume.GetMasterVolumeLevelScalar()*100 < config.conf[_addonName]['minlevel']:
			if config.conf[_addonName]['max']:
				volume.SetMasterVolumeLevelScalar(1.0, None)
			else:
				volume.SetMasterVolumeLevelScalar(float(config.conf[_addonName]['volume'])/100, None)

	def resetSynth(self) -> None:
		"""If the synthesizer is not initialized - repeat attempts to initialize it."""
		if not synthDriverHandler.getSynth():
			synthDriverHandler.initialize()
			i = 0
			while not synthDriverHandler.getSynth() and i<=config.conf[_addonName]['retries']:
				synthDriverHandler.setSynth(config.conf['speech']['synth'])
				sleep(1)
				if config.conf[_addonName]['retries']!=0:
					i+=1
			else:
				self.audioEnabledSound()

	def audioEnabledSound(self) -> None:
		"""The signal when the audio is successfully turned on and the synthesizer is enabled."""
		for p,t,s in [(300,100,0.1),(500,80,0.1),(700,60,0.1)]:
			beep(p, t)
			sleep(s)

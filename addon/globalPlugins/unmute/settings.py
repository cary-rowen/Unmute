#settings.py
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

import gui
from gui import guiHelper, nvdaControls
import wx
import config
from . import _addonName, _addonSummary


class UnmuteSettingsPanel(gui.SettingsPanel):
	"""Add-on settings panel object"""
	title = _addonSummary

	def __init__(self, parent):
		"""Initializing the add-on settings panel object"""
		super(UnmuteSettingsPanel, self).__init__(parent)

	def makeSettings(self, sizer: wx._core.BoxSizer):
		"""Populate the panel with settings controls.
		@param sizer: The sizer to which to add the settings controls.
		@type sizer: wx._core.BoxSizer
		"""
		# Translators: Help message for a dialog.
		helpLabel = wx.StaticText(self, label=_("Select the initial sound system settings that will be set when NVDA starts:"), style=wx.ALIGN_LEFT)
		helpLabel.Wrap(helpLabel.GetSize()[0])
		sizer.Add(helpLabel, flag=wx.EXPAND)
		soundSizer = wx.BoxSizer(wx.VERTICAL)
		maxVolumeSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: A setting in addon settings dialog.
		self._maxVolumeChk = wx.CheckBox(self, label=_("Set the &maximum volume of the Windows system audio when starting NVDA"))
		maxVolumeSizer.Add(self._maxVolumeChk)
		soundSizer.Add(maxVolumeSizer, flag=wx.EXPAND)
		self._maxVolumeChk.SetValue(config.conf[_addonName]['max'])

		customVolumeSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: A setting in addon settings dialog.
		self._customVolumeSlider = guiHelper.LabeledControlHelper(self, _("Set custom volume level:"), nvdaControls.EnhancedInputSlider,
			value=config.conf[_addonName]['volume'], minValue=0, maxValue=100, size=(250, -1)).control
		customVolumeSizer.Add(self._customVolumeSlider, flag=wx.EXPAND)
		soundSizer.Add(customVolumeSizer, flag=wx.EXPAND)
		self._maxVolumeChk.Bind(wx.EVT_CHECKBOX, lambda evt, s1=soundSizer, s2=customVolumeSizer: s1.Show(s2, show=not evt.IsChecked()) and s1.Layout())

		sizer.Add(soundSizer, flag=wx.EXPAND)

	def postInit(self):
		"""Set system focus to source language selection dropdown list."""
		self._maxVolumeChk.SetFocus()

	def onSave(self):
		"""Update Configuration when clicking OK."""
		config.conf[_addonName]['max'] = self._maxVolumeChk.GetValue()
		config.conf[_addonName]['volume'] = self._customVolumeSlider.GetValue()
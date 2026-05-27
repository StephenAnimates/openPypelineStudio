"""
File: UIObjects.py
Description: Singleton class for managing Maya UI instances and dock controls.
             
Original Framework: openPipeline by Kickstand
License: Common Public License 1.0 (CPL-1.0)
"""

import singleton as singleton

class UIObjects(singleton.singleton):
	
	def __init__(self):
		self.window = []
		self.dockControl = []
	
	def addWindow(self, window=None):
		if window not in self.window:
			self.window.append(window)
	
	def addDockControl(self, dockCtrl=None):
		if dockCtrl not in self.dockControl:
			self.dockControl.append(dockCtrl)
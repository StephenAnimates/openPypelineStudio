import singleton as singleton
import maya.cmds as cmds

class UIObjects(singleton.singleton):
	
	def __init__(self):
		self.window = []
		self.dockControl = []
	
	def addWindow(self, window=None):
		addWin = 1
		if(len(self.window) == 0):
			self.window.append(window)
		else:
			for win in self.window:
				if (win == window): addWin = None
			if addWin:
				self.window.append(window)
		self.updateTextField()
	
	def addDockControl(self, dockCtrl=None):
		addDoc = 1
		if(len(self.dockControl) == 0):
			self.dockControl.append(dockCtrl)
		else:
			for doc in self.dockControl:
				if(doc == dockCtrl): addDoc=0
			if addDoc:
				self.dockControl.append(dockCtrl)
		self.updateTextField()
				
	def updateTextField(self):
		if cmds.workspaceControl('DiagnosticUIManager', exists=1) or cmds.window('DiagnosticUIManager', q=True, ex=True):

			textFieldString = '---window objects---\n\n'
			for obj in self.window:
			    if cmds.window(obj, q=True, ex=True): textFieldString += obj + '\n'
			textFieldString += '\n---dockable objects---\n\n'
			for obj in self.dockControl:
			    if cmds.workspaceControl(obj, q=1, exists=1): textFieldString += obj + '\n'
			cmds.scrollField('diagnosticUI_UIObjects_scrollField', edit=1, text=textFieldString)
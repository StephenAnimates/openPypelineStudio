def renameAsset(folderPath, newName, oldName=''):
	
	import os
		
	isTopLevel = 0
	
	error=''
	
	if oldName == '': # the first call, top level
		isTopLevel = 1
		split = os.path.split(folderPath)
		oldName = os.path.basename(split[0])
		newDirPath = folderPath.replace(oldName, newName)
		if os.path.isdir(newDirPath):
			error += 'An asset with this name already exists.'
		
		
	if error == '':		
		for root, dirs, files in os.walk(folderPath):
			for filename in files:
				print(f'renaming {filename}')
				newFileName = filename.replace(oldName, newName)
				os.rename(os.path.join(root, filename), os.path.join(root, newFileName))
			for dirname in dirs:
				print(dirname)
				nextFolderPath = os.path.join(folderPath, dirname)
				renameAsset(nextFolderPath, newName, oldName)
				print(f'renaming {dirname}')
				newDirName = dirname.replace(oldName, newName)
				os.rename(os.path.join(root, dirname), os.path.join(root, newDirName))
		
		
		if isTopLevel: # rename the top level
			newDirPath = folderPath.replace(oldName, newName)
			os.rename(folderPath, newDirPath)
			
	else:
		print(error)
			
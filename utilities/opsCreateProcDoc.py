import fnmatch
import os
import re
import datetime

#returns a list of all MEL files under the given folder
def getMelFiles(folder):
    return [os.path.join(folder, filename).replace("\\", "/") for filename in os.listdir(folder) if fnmatch.fnmatch ( filename, '*.mel' )]

#returns whether the given folder is a valid openPypeline folder (contains "openPypeline.mel" file and "openpypeline" folder)
def isValidOpFolder(folder):
    return os.path.exists(folder) and os.path.exists(os.path.join(folder, "openpypeline"))

#returns a dictionary of all the scripts and their comments
#keys = script filenames (string), data = procedures and info for that file (dictionary)
def getAllComments(scriptPath):
    allComments = {}
    if (isValidOpFolder(scriptPath)):
        opPath = os.path.join(scriptPath, "openpypeline")
        scriptFiles = [os.path.join(scriptPath, "openPypeline.mel")]
        scriptFiles.extend(getMelFiles(opPath))
        for script in scriptFiles:
            allComments[os.path.basename(script)] = getComments(script)
    else:
        print(f"{scriptPath} is not a valid openpypeline script path.  Please manually set the script path at the bottom of the opsCreateProcDoc.py file.")
    return allComments

#returns a dictionary of all procedures and their info for the given script file
#keys = procedure names (string), data = comments (string)
def getComments(filename):
    p = re.compile('//#+')
    p2 = re.compile('//')
    p3 = re.compile('[ ]*//[ ]*[Nn][Aa][Mm][Ee][ ]*:')
    try:
        with open(filename, "r") as f:
            comments = {}
            currProc=""
            currComments=""
            write = 0
            for line in f.readlines():
                if (write):
                    m = p3.match(line)
                    if (m):
                        currProc = line[m.end():(len(line)-1)]
                    elif p2.match(line) and not (p.match(line)):
                        currComments += line[2:len(line)]
                if (p.match(line)):
                    if (write):
                        comments[currProc] = currComments
                        currComments=""
                        write = 0
                    else:
                        write = 1
            return comments
    except IOError:
        print(f"Warning: {filename} could not be opened for reading!")


#given a dictionary of all relevant info, writes the info to the given html file in a readable format
def htmlWriter(comments, filename):
    files = comments.keys()
    try:
        with open(filename, 'w') as f:
            f.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN""http://www.w3.org/TR/html4/loose.dtd">\n<html>\n<head>\n<title>openPypeline Studio for Maya Procedure Overview</title>\n<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">\n</head>\n<body>\n')
            f.write(f'<a name="top"><h1>openPypeline Studio for Maya Procedure Documentation ({datetime.date.today().strftime("%b. %d, %Y")})</h1></a>\n')
            
            for script in files:
                f.write(f'<a href="#{script}">{script}<a><br>\n')
                
            for script in files:
                f.write(f'<a name="{script}"><h2>{script}</h2></a>\n')
                procDictionary = comments[script]
                for proc in procDictionary.keys():
                    f.write(f'<h4>{proc}</h4>\n')
                    f.write(re.sub("\n","<br>",(procDictionary[proc])))
                    
                f.write('<a href="#top">back to top</a>\n')
                
            f.write('<br><br><br><i>This file was created by the opsCreateProcDoc.py script.</i>\n')
            f.write('</body>\n</html>\n')
    except IOError:
        print(f"{filename} could not be opened/created for writing. Please make sure the script path you specified contains an 'openpypeline' folder.")

#given the maya scriptPath and an html filename, retrieves the openPypeline procedure info and writes it to the html file
def openPypelineCreateProcDoc(scriptPath, htmlFile):
    htmlWriter(getAllComments(scriptPath),htmlFile)
               
if __name__ == "__main__":
    #edit the path and filename below before using this script:
    #the maya script path that contains your openPypeline.mel file and openpypeline folder:
    scriptPath = "[insert path here]"
    htmlFile = os.path.join(scriptPath, "openpypeline", "openPypelineProcedures.html").replace("\\", "/")
    openPypelineCreateProcDoc(scriptPath, htmlFile)

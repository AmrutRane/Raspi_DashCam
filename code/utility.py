# get base directory based on this file.
def getBaseDirectory():
    mypath = os.path.abspath(__file__)  # Find the full path of this python script
    baseDir = os.path.dirname(mypath)  # get the path location only (excluding script name)
    
    return baseDir;

# pass file name along with extension.
# ex: name = "dashcam.log"
def buildFilePath(name):
    baseDir = getBaseDirectory()
    baseFileName = os.path.splitext(os.path.basename(mypath))[0]
    filePath = os.path.join(baseDir, name)

    return filePath;

import picamera
import os
import psutil
import serial
#import pynmea2
import pathlib
import time
import json
import itertools
import RPi.GPIO as GPIO
from picamera import Color
import datetime as dt

absolute_path = str(pathlib.Path(__file__).parent.absolute()) + "/"
Folder_Root = "/home/pi/DashCam/"
Videos_Folder = "Videos/"

if not os.path.exists(Videos_Folder):
    os.makedirs(Videos_Folder)
    print('Created Video Folder')

def Clear_Space():
    
    i = 0
    Files_Deleted = 0
    while i < cnf_Max_Files:
        del_file_path = Folder_Root + Videos_Folder + "Video%05d.h264" % i
        i = i + 1
        if os.path.exists(del_file_path):
            #print('Deleting some files to create space on the drive, please wait ...')
            os.remove(del_file_path)
            print( 'Deleted file ' + del_file_path ) 
            Files_Deleted = Files_Deleted + 1
        if(Files_Deleted >= cnf_Delete_Files):
            break
    

def Check_Space():
    #print('Checking Space...')
    if(psutil.disk_usage(".").percent > cnf_Space_Limit):
        Clear_Space()

def Get_file_number(file_name):
    fullNameLen = len(file_name)
    st = fullNameLen - 10
    en = fullNameLen - 5
    return int(file_name[st:en])

def WriteFileNumberToConfigFile(file_name):
    iNum = Get_file_number(file_name)

    if os.path.exists(absolute_path + 'Config_DashCam.json'):
        try:
            with open(absolute_path + 'Config_DashCam.json', 'r') as f:
                ConfigFile = json.load(f)
        except(IOError, ValueError):
            ConfigFile = cnf_file_number

        ConfigFile['File_Number'] = iNum  # or whatever

        with open(absolute_path + 'Config_DashCam.json', 'w') as f:
            json.dump(ConfigFile, f)

#Function that actually start recording based on either default or config file parameter values        
def StartRecording():


    with picamera.PiCamera() as camera:
        camera.resolution = (cnf_ResolutionX,cnf_ResolutionY)
        camera.framerate = cnf_Framerate
        camera.annotate_background = picamera.Color('black')
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for file_name in camera.record_sequence(Folder_Root + Videos_Folder + "Video%05d.h264" % i for i in range(cnf_file_number, cnf_Max_Files)):
            print('Recording to %s' % file_name)
            camera.wait_recording(cnf_Duration*60)
            start = dt.datetime.now()
            while (dt.datetime.now() - start).seconds < 30:
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.wait_recording(0.2)
            
            WriteFileNumberToConfigFile(file_name)
            Check_Space()

    print('Obtaining Video File Number')

    #Note :- If Json confic file exist then read from it and assign to variables.   
if os.path.isfile(absolute_path + 'Config_DashCam.json'):
    f = open(absolute_path + 'Config_DashCam.json','r')
    Config_DashCam = json.load(f)
    cnf_file_number = Config_DashCam['File_Number']

    #Note :- Config file number is the last successful file. Next file should start with new number to avoid overriding last file.
    cnf_file_number = cnf_file_number +1 

    cnf_Duration = Config_DashCam['Duration_In_Minutes']
    cnf_Max_Files = Config_DashCam['Max_Files']
    cnf_Space_Limit = Config_DashCam['Space_Limit_In_Percentage']
    cnf_Delete_Files = Config_DashCam['Delete_Files']
    cnf_ResolutionX = Config_DashCam['ResolutionX']
    cnf_ResolutionY = Config_DashCam['ResolutionY']
    cnf_Framerate = Config_DashCam['Framerate']

    file_name = Folder_Root + Videos_Folder + "Video" + str(cnf_file_number).zfill(5) + "." + "h264"
    print(file_name)

    StartRecording()
#Note :- If Json canfic file does not exist then create one with default variables values and start recording with it.
else:
    print("Config file not found, creating one with default values, please wait...")

    cnf_file_number = 1
    cnf_Duration = 1
    cnf_Max_Files = 99999
    cnf_Space_Limit = 80
    cnf_Delete_Files = 10
    cnf_ResolutionX = 1920
    cnf_ResolutionY = 1000
    cnf_Framerate = 30

    Config_DashCam = {}
    Config_DashCam['File_Number'] =  cnf_file_number
    Config_DashCam['Duration_In_Minutes'] =  cnf_Duration
    Config_DashCam['Max_Files'] =  cnf_Max_Files
    Config_DashCam['Space_Limit_In_Percentage'] =  cnf_Space_Limit
    Config_DashCam['Delete_Files'] =  cnf_Delete_Files
    Config_DashCam['ResolutionX'] =  cnf_ResolutionX
    Config_DashCam['ResolutionY'] =  cnf_ResolutionY
    Config_DashCam['Framerate'] =  cnf_Framerate

    with open(absolute_path + 'Config_DashCam.json', 'w') as f:
            json.dump(Config_DashCam,f)
            print('Config file created')

    file_name = Folder_Root + Videos_Folder + "Video" + str(cnf_file_number).zfill(5) + "." + "h264"
    print(file_name)

    StartRecording()




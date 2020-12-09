import picamera
import os
import psutil
import serial
#import pynmea2
import time
import json
import itertools
import RPi.GPIO as GPIO
from picamera import Color

DURATION = 1
MAX_FILES = 99999
SPACE_LIMIT = 15
DELETE_FILES = 10
File_Number = 1

Folder_Root = "/home/pi/DashCam/"
Videos_Folder = "Videos/"

if not os.path.exists(Videos_Folder):
    os.makedirs(Videos_Folder)
    print('Created Video Folder')

def Clear_Space():
    
    i = 0
    Files_Deleted = 0
    while i < MAX_FILES:
        del_file_path = Folder_Root + Videos_Folder + "Video%05d.h264" % i
        i = i + 1
        if os.path.exists(del_file_path):
            print('Max file count reached. Deleting some files, please wait ...')
            os.remove(del_file_path)
            print('Deleted file ' + del_file_path ) 
            Files_Deleted = Files_Deleted + 1
        if(Files_Deleted >= DELETE_FILES):
            break
    
    
    
def Check_Space():
    print('Checking Space...')
    if(psutil.disk_usage(".").percent > SPACE_LIMIT):
        Clear_Space()

def Get_file_number(fullPath):
    fullNameLen = len(file_name)
    st = fullNameLen - 10
    en = fullNameLen - 5
    return int(file_name[st:en])

#Check_Space()  

def WriteFileNumberToConfigFile(file_name):
    iNum = Get_file_number(file_number)

    if os.path.exists('Config_DashCam.json'):
        try:
            with open('Config_DashCam.json', 'r') as f:
                ConfigFile = json.load(f)
        except(IOError, ValueError):
            ConfigFile = File_Number

        ConfigFile['number'] = iNum  # or whatever

        with open('Config_DashCam.json', 'w') as f:
            json.dump(ConfigFile, f)
        
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1000)
    camera.framerate = 30

    print('Obtaining Video File Number')

    if os.path.isfile(Folder_Root + 'Config_DashCam.json'):
        f = open('Config_DashCam.json','r')
        Config_DashCam = json.load(f)
        file_number = Config_DashCam['File_Number']['number']
        print('File Number is : ')
        print(file_number)
        file_name = Folder_Root + Videos_Folder + "Video" + str(file_number).zfill(5) + "." + "h264"
        print(file_name)
    else:
        print("Config file not found, creating one.")
        File_Number = 1
        Config_DashCam = {}
        Config_DashCam['File_Number'] = { 'number' : File_Number }
        with open('Config_DashCam.json', 'w') as f:
            json.dump(Config_DashCam,f)
            print('Config file created')
    
#     print('Searching files ...')
# 
#     for i in range(1, MAX_FILES):
#         file_number = i
#         file_name = Folder_Root + Videos_Folder + "Video" + str(i).zfill(5) + "." + "h264"
#         exists = os.path.isfile(file_name)
#                 
#         if not exists:
#             print ('Search complete')
#             break

    for file_name in camera.record_sequence(Folder_Root + Videos_Folder + "Video%05d.h264" % i for i in range(file_number, MAX_FILES)):
       print('Recording to %s' % file_name)
       camera.wait_recording(DURATION*5)
    
       WriteFileNumberToConfigFile(file_name)

       if(psutil.disk_usage(".").percent > SPACE_LIMIT):
           print('Warning : Low space!')
           Clear_Space()


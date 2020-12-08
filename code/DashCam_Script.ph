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
        
#Check_Space()  


        
if not os.path.exists(Videos_Folder):
    os.makedirs(Videos_Folder)
    print('Created Video Folder')
             
        
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1000)
    camera.framerate = 30

    print('Obtaining Video File Number')

    if os.path.isfile(Folder_Root + 'Config_DashCam.json'):
        f = open('Config_DashCam.json','r')
        Config_DashCam = json.load(f)
        file_number1 = Config_DashCam['filenumber']
        print('File Number is : ')
        print(file_number1)
        file_name = Folder_Root + Videos_Folder + "Video" + str(file_number1).zfill(5) + "." + "h264"
        print(file_name)
    
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

    for file_name in camera.record_sequence(Folder_Root + Videos_Folder + "Video%05d.h264" % i for i in range(file_number1, MAX_FILES)):
            
       print(file_number1)
       print('Recording to %s' % file_name)
       camera.wait_recording(DURATION*5)
       if(psutil.disk_usage(".").percent > SPACE_LIMIT):
           print('Warning : Low space!')
           Clear_Space()

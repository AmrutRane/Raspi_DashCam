# Import libraries
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
import subprocess

#Global Variable declaration

absolute_path = str(pathlib.Path(__file__).parent.absolute()) + "/"
Folder_Root = "/home/pi/dashcam/"
Videos_Folder = "videos/"

SWITCH_PIN = 3
POWER_PIN = 27

file_number = 0
port = "/dev/serial0"
timeout = 0.5
#serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)
# GPIO.setup(POWER_PIN, GPIO.OUT)
# GPIO.output(POWER_PIN, GPIO.LOW)

# GPIO.setup(LED_PIN, GPIO.OUT)
# GPIO.output(LED_PIN, GPIO.LOW)

# Create root folder ("dashcam")
if not os.path.exists(Folder_Root):
    os.makedirs(Folder_Root)
    print('dashcam folder created')

# Create videos folder.
if not os.path.exists(Videos_Folder):
    os.makedirs(Videos_Folder)
    print('videos folder created')

# Function to delete files (per number from Json config file) if disk space is more than threshold (from condig file)
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

# Function to check available disk space. If disk space is above threshold mentioned in the Json config file then call clear_space
def Check_Space():
    #print('Checking Space...')
    if(psutil.disk_usage(".").percent > cnf_Space_Limit):
        Clear_Space()

# Function to extract file number for file name.
def Get_file_number(file_name):
    fullNameLen = len(file_name)
    st = fullNameLen - 10
    en = fullNameLen - 5
    return int(file_name[st:en])

# Function to write last successful video file number in Json config file.
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
# Execution Steps are 
# 1 Set values from Json config
# 2 Start recoding with a loop for max number of files.
# 3 Format file name and start recording
# 4 Print annotate having date time 
# 5 Stop Recording
# 6 Write last successful recorded file number to Jason config file.
# 7 Start recording with the next file number / Name
# 8 In between, if Shutdown switch is pressed and hold for 5 seconds, then shut down Raspi safely/softly

def StartRecording():

    cntr = 0
    with picamera.PiCamera() as camera:
        camera.resolution = (cnf_ResolutionX,cnf_ResolutionY)
        camera.framerate = cnf_Framerate
        
        file_number=cnf_file_number 
 
        while file_number < cnf_Max_Files:
               
            file_name = Folder_Root + Videos_Folder + "video%05d.h264" % file_number
            print('Recording to %s' % file_name)
            cntr = 0
            timeout = time.time() + cnf_Duration
            camera.start_recording(file_name, quality = cnf_Quality)
            start = dt.datetime.now()
        
            while (dt.datetime.now() - start).seconds < cnf_Duration:
                camera.annotate_background = Color('black')
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %a %H:%M:%S')
                camera.wait_recording(0.1)
                start_time  = time.time()
                shutdown = False
                
                if GPIO.input(cnf_GPIOPINNUMBER) == False:
                        time.sleep(1)
                        cntr = cntr +1
                        start_time = time.time()
                        print(cntr)
                        
                        if cntr > cnf_PiShutdownDelay:
                            shutdown = True
                            print('Shutting down...')
                            camera.stop_recording()
                            WriteFileNumberToConfigFile(file_name)
                            time.sleep(3)
                            os.system("sudo shutdown -h now")
                            #subprocess.call("/sbin/shutdown -h now", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    cntr = 0                               
               
            Check_Space()
            WriteFileNumberToConfigFile(file_name)
            Check_Space()
            time.sleep(0.02)
        
            file_number = file_number +1
        
            camera.stop_recording()

    #Note :- If Json confic file exist then read from it and assign to variables.   
if os.path.isfile(absolute_path + 'Config_DashCam.json'):
    f = open(absolute_path + 'Config_DashCam.json','r')
    Config_DashCam = json.load(f)
    cnf_file_number = Config_DashCam['File_Number']

    #Note :- Config file number is the last successful file. Next file should start with new number to avoid overriding last file.
    cnf_file_number = cnf_file_number +1 

    cnf_Duration = Config_DashCam['Duration_In_Minutes']
    cnf_Duration = cnf_Duration * 60 # Config value * 60 seconds
    cnf_Max_Files = Config_DashCam['Max_Files']
    cnf_Space_Limit = Config_DashCam['Space_Limit_In_Percentage']
    cnf_Delete_Files = Config_DashCam['Delete_Files']
    cnf_ResolutionX = Config_DashCam['ResolutionX']
    cnf_ResolutionY = Config_DashCam['ResolutionY']
    cnf_Framerate = Config_DashCam['Framerate']
    cnf_Quality = Config_DashCam['Quality']
    cnf_PiStartTimeDelay = Config_DashCam['PiStartTimeDelay']
    cnf_PiShutdownDelay = Config_DashCam['PiShutdownDelay']
    cnf_GPIOPINNUMBER = Config_DashCam['GPIOPINNUMBER']
    SWITCH_PIN = cnf_GPIOPINNUMBER
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
    cnf_Quality = 20
    cnf_PiStartTimeDelay = 2
    cnf_PiShutdownDelay = 5
    cnf_GPIOPINNUMBER = 3

    Config_DashCam = {}
    Config_DashCam['File_Number'] =  cnf_file_number
    Config_DashCam['Duration_In_Minutes'] =  cnf_Duration
    Config_DashCam['Max_Files'] =  cnf_Max_Files
    Config_DashCam['Space_Limit_In_Percentage'] =  cnf_Space_Limit
    Config_DashCam['Delete_Files'] =  cnf_Delete_Files
    Config_DashCam['ResolutionX'] =  cnf_ResolutionX
    Config_DashCam['ResolutionY'] =  cnf_ResolutionY
    Config_DashCam['Framerate'] =  cnf_Framerate
    Config_DashCam['Quality'] =  cnf_Quality
    Config_DashCam['PiStartTimeDelay'] = cnf_PiStartTimeDelay
    Config_DashCam['PiShutdownDelay'] = cnf_PiShutdownDelay
    Config_DashCam['GPIOPINNUMBER'] =cnf_GPIOPINNUMBER
    SWITCH_PIN = cnf_GPIOPINNUMBER
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    with open(absolute_path + 'Config_DashCam.json', 'w') as f:
            json.dump(Config_DashCam,f)
            print('Config file created')

    file_name = Folder_Root + Videos_Folder + "Video" + str(cnf_file_number).zfill(5) + "." + "h264"
    print(file_name)

    StartRecording()




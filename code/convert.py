
import os

START_INDEX = 2106
END_INDEX =2108
Folder_Root = "/home/pi/DashCam/"

print("Starting conversion...")
if START_INDEX > END_INDEX:
	print("Error! Check index values")
else:
	if not os.path.exists(Folder_Root + "output/"):
		os.makedirs(Folder_Root + "output/")
		print("Created output folder.")

	i=START_INDEX
	while(i <= END_INDEX):
		input_file =  Folder_Root + "Videos/Video%05d.h264" % i
		output_file = Folder_Root + "output/video%05d.mp4" % i
		i = i + 1

		if os.path.exists(input_file):
			print("Converting: " + input_file)
			conversion_command = "MP4Box -add " + input_file + " " + output_file
			print(conversion_command)
			os.system(conversion_command)
	print("Conversion complete.")
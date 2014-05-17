# -*- coding: utf-8 -*-
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
import commands
import sys
import os

# Connects to the current device, returning a MonkeyDevice object
devices = commands.getoutput('../platform-tools/adb devices').strip().split('\n')[1:]
if len(devices) == 0:
	MonkeyRunner.alert("Select device to connect.", "No devices found", "Exit")
	sys.exit(1) 

# Select Any One Device And Ask User's Choice. Select Actual Device To Execute
device = None
choice = MonkeyRunner.choice('select device', devices, 'Choice')
device = devices[choice].split('\t')[0]

if device is None:
	MonkeyRunner.alert("Select device to connect.", "No 192.devices found", "Exit")
	sys.exit(1) 

path = 'monkey/screen_shot'
files = os.listdir(path)
for f in files:
	os.remove(path + '/' + f)

device = MonkeyRunner.waitForConnection(5, device)
size = (device.getProperty('display.width'), device.getProperty('display.height'))
size = map(int, size)
print size[0], size[1]

shot_count = 0
mode = MonkeyRunner.choice('mode?', ['sub', 'full'], 'Choice')
if mode == 0:
	rect = [0, 0, size[1], size[0]]
	while True:
		rect = MonkeyRunner.input('rect:x, y, w, h', `rect[0]`+','+`rect[1]`+','+`rect[2]`+','+`rect[3]`, 'input rect', 'ok', 'cancel').split(',')
		rect = map(int, rect)
		shot = device.takeSnapshot().getSubImage((rect[0], rect[1], rect[2], rect[3]))
		shot.writeToFile(path+'/shot_'+`rect[0]`+'_'+`rect[1]`+'_'+`rect[2]`+'_'+`rect[3]`+'_'+`shot_count` + '.png','png')
		shot_count += 1
else:
	while True:
		choice = MonkeyRunner.choice('take a shot?', ['yes', 'no', 'end'], 'Choice')
		if  choice == 0:
			device.takeSnapshot().writeToFile(path + '/shot_' + `shot_count` + '.png','png')
			shot_count += 1
		elif choice == 2:
			sys.exit(1) 

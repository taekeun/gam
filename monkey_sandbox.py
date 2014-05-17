# -*- coding: utf-8 -*-
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from com.android.monkeyrunner.easy import EasyMonkeyDevice, By
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
for i, d in enumerate(devices):
	if d.find('192') >= 0:
		device = d.split('\t')[0]
		break

if device is None:
	MonkeyRunner.alert("Select device to connect.", "No 192.devices found", "Exit")
	sys.exit(1) 

device = MonkeyRunner.waitForConnection(5, device)
if not device:
   raise Exception('Cannot connect to device')

easyDevice = EasyMonkeyDevice(device)

hv = device.getHierarchyViewer()

while True:
	windowName = hv.getFocusedWindowName()
	print windowName	

	# rootView = easyDevice.getRootView()
	print easyDevice.getViewIdList()
	# if MonkeyRunner.choice('continue?', ['Yes', 'No'], 'Choice') == 1 : break
	break

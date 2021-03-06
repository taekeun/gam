# -*- coding: utf-8 -*-
# Game Auto helper using MonkeyRunner

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage
import commands
import sys
from datetime import datetime
import subprocess
import glob


class Gam:
    def __init__(self, name, device_name, path):
        self.name = name
        self.path = path

        self.refs = {}
        self.refs_key_ordered = []
        self.start_time = datetime.now()
        self.turn_start_time = self.start_time
        self.print_msg('hello ' + name)

        self.get_device(device_name)

    def get_device(self, device_name):
        # Connects to the current device, returning a MonkeyDevice object
        devices = commands.getoutput('../platform-tools/adb devices').strip().split('\n')[1:]
        if len(devices) == 0: self.exit("No devices found")
        self.print_msg(str(devices))

        # Select Any One Device And Ask User's Choice. Select Actual Device To Execute
        device = None
        if len(devices) > 1:
            for i, d in enumerate(devices):
                if d.find(device_name) >= 0:
                    device = d
                    break
            # choice = MonkeyRunner.choice('select device', devices, 'Choice')
            # device = devices[choice]
            if device is None: self.exit("No " + device_name + " devices found")
        else:
            device = devices[0]
        device = device.split('\t')[0]
        self.is_geny = device.split('.')[0].find('192') >= 0

        self.device = MonkeyRunner.waitForConnection(5, device)
        try:
            self.width = self.device.getProperty('display.width')
            self.height = self.device.getProperty('display.height')
            if not self.width:
                self.exit('fail device.getProperty("display.width")')
            self.print_msg(`self.width` + "," + `self.height`)
            # TODO 자바 SocketException 잡기
        except:
            print "retry get_device"
            self.get_device(device_name)

    def set_stages(self, **enums):
        self.stages = self.enum(enums)
        return self.stages

    def enum(self, enums):
        return type('Enum', (), enums)

    def set_ref(self, stage, acceptance):
        # if self.is_geny:
        #     path = self.path + 'images/'
        # else:
        #     path = self.path + 'images_p/'
        path = self.path + 'images/'
        file_name = glob.glob(path + stage + '-*.png')[0]
        position = tuple(map(int, file_name.split('-')[1].replace('.png', '').split('_')))
        self.refs[stage] = (position, acceptance, MonkeyRunner.loadImageFromFile(file_name))
        self.refs_key_ordered.append(stage)

    # print 'set reference stage:' + stage +', position:' + str(position) + ', file:' + file_name

    def check_stage(self, shot, stage):
        sub = shot.getSubImage(self.refs[stage][0])
        return sub.sameAs(self.refs[stage][2], self.refs[stage][1])

    def current_stage(self, shot=None):
        if shot is None: shot = self.take_snapshot()

        for stage in self.refs_key_ordered[:]:
            if self.check_stage(shot, stage): return stage
        return 'fail:current_stage'

    def turn_end(self, msg):
        self.debug(self.elapsed_time_str() + '|' + str(msg))
        self.turn_start_time = datetime.now()

    def take_snapshot(self):
        try:
            shot = self.device.takeSnapshot()
            return shot
        except:
            print 'ERROR]fail to take_snapshot : ' + sys.exc_info()[0]

    def screen_shot(self, is_save=False):
        try:
            shot = self.take_snapshot()
            if is_save and shot: self.save_file(shot, 'current_shot')
            return shot
        except:
            print 'ERROR]fail to screen_shot : ' + sys.exc_info()[0]

    def save_file(self, image, name):
        image.writeToFile(self.get_file_path(name), 'png')

    def get_file_path(self, name):
        return self.path + name + '.png'

    # actions
    def touch(self, x, y, msg=None):
        if msg: self.print_running(msg)
        self.device.touch(x, y, MonkeyDevice.DOWN_AND_UP)
        MonkeyRunner.sleep(1.0)

    def back(self, msg=None):
        if msg:
            print msg
        self.device.press('KEYCODE_BACK', MonkeyDevice.DOWN_AND_UP)

    # appeptance
    def compare_debug(self, ref, shot, acceptance):
        self.save_file(ref, 'ref')
        self.save_file(shot, 'shot')
        if shot.sameAs(ref, acceptance):
            print 'pass compare:' + `acceptance`
        else:
            print 'fail compare:' + `acceptance`
            subprocess.call(["/usr/local/bin/compare", get_file_path('ref'), get_file_path('shot'), get_file_path('cmp')])

    def find_acceptance(self, message, ref, shot):
        acceptance = 1.0
        while acceptance > 0.0:
            if shot.sameAs(ref, acceptance):
                print message + ' acceptance: ' + `acceptance`
                break
            acceptance -= 0.1
        if acceptance < 0.1:
            print message + ' fail to find acceptance'
        self.compare_debug(ref, shot, acceptance)

    # utils
    def battery_level(self):
        return int(self.device.shell('cat /sys/class/power_supply/battery/capacity'))

    def print_msg(self, msg):
        msg = self.time_to_s(datetime.now()) + '|' + msg
        print msg
        return msg

    def print_running(self, msg):
        print self.time_to_s(datetime.now()) + '|' + self.elapsed_time_str() + ' ' + str(msg)

    # sys.stdout.write(self.time_to_s(datetime.now()) + '|' + self.elapsed_time_str() + ' ' + str(msg) + '\r')
    # sys.stdout.flush()
    # sys.stdout.write('\n')

    def exit(self, msg=''):
        self.print_msg(msg)
        sys.exit(1)

    def time_to_s(self, time):
        return time.strftime("%m-%d %H:%M:%S");

    def elapsed_time_str(self):
        return str(datetime.now() - self.turn_start_time).split('.')[0]

    def debug(self, msg):
        log_file = open('monkey/log.txt', 'a')
        # sys.stdout.write('\n')
        msg = self.print_msg(self.name + '|' + msg)
        log_file.write(msg + '\n')
        log_file.close()

    def sleep(self, sec):
        MonkeyRunner.sleep(sec)

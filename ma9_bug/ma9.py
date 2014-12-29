# -*- coding: utf-8 -*-
#
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage
from datetime import datetime
import commands
import sys
import os
import subprocess
import time

sys.path.insert(0, 'monkey')
from gam import Gam


count = {'B': 0}
no_bat = False
no_ticket_sleep = 60.0 * 10.0
restart_mode = False


def add_battle():
    count['B'] += 1
    gam.turn_end(count)


def get_used_bat():
    return count['B']


def run_battle():
    global restart_mode

    msg = "battle:"
    is_played = False
    bug_set = False
    while True:
        gam.sleep(1)
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)

        if stage is Stages.H:
            if bug_set:
                gam.touch(1500, 500, msg + '배틀')
            else:
                gam.touch(300, 1000, msg + '친구')
        elif stage is Stages.F_I:
            gam.touch(800, 200, msg + '카톡친구')
        elif stage is Stages.F_K:
            if bug_set:
                gam.touch(70, 70, msg + '뒤로')
                gam.sleep(3)
            else:
                gam.device.drag((800, 900), (800, 400), 0.1, 10)
                gam.sleep(1)
                gam.device.drag((800, 900), (800, 400), 0.1, 10)
                gam.sleep(3)
                # gam.touch(1600, 900, msg + '라인업')
                gam.touch(1600, 800, msg + '라인업') #2번째
                # gam.touch(1600, 600, msg + '라인업') #3번째
                # gam.touch(1600, 500, msg + '라인업') #4번째
        elif stage is Stages.B_R:
            bug_set = False
            is_played = True
            gam.touch(1500, 1000, msg + '경기준비')
        elif stage is Stages.B_S:
            gam.touch(1500, 1000, msg + '경기시작')
        elif stage is Stages.OP_L:
            bug_set = True
            gam.touch(100, 950, msg + '뒤로')
        elif stage is Stages.P:
            gam.sleep(1)
        elif stage is Stages.B_E:
            is_played = False
            add_battle()
            gam.touch(900, 950, msg + '배틀 종료:홈으로')
        elif stage is Stages.B_LE:
            gam.touch(1500, 200, msg + '배틀 리그 종료')
        elif stage is Stages.A_NB:
            gam.touch(800, 850, msg + '배트 부족')
            no_bat = True
            gam.debug("no bat. sleep 10min")
            gam.sleep(10 * 60)
        elif stage is Stages.A_OK or stage is Stages.A_OK2:
            gam.touch(1000, 800, msg + 'Alert:OK')
        elif stage is Stages.MI_R:
            gam.touch(1200, 850, msg + '미션 보상 받기')
        elif stage is Stages.MI:
            gam.touch(1700, 1000, msg + '미션:모두받기')
        elif stage is Stages.MI_I:
            gam.touch(800, 850, msg + '미션:확인')
            gam.sleep(1)
            gam.touch(60, 60, msg + '미션:뒤로')
            gam.sleep(3)
        else:
            if is_played:
                gam.touch(1300, 800, msg + 'else')
            gam.debug('fail to find stage:' + stage)

mode = {'single': False, 'battle': False}

if len(sys.argv) is 1:
    sys.argv.append(2)

if len(sys.argv) < 2:
    print 'usage: ./monkeyrunner monkey/star_level_up.py [index]'
    print 'options'
    print '-r # restart'
    gam.exit()
device_index = sys.argv[1]

if len(sys.argv) == 3 and sys.argv[2] == '-r':
    restart_mode = True

mode['battle'] = True

gam = Gam('ma9ma9', '192.168.56.10' + str(device_index), 'monkey/ma9_bug/')

Stages = gam.set_stages(H='home',
                        B='battle', B_R='battle_rank', B_H='battle_history', B_S='battle_start', B_E='battle_end', B_LE='battle_lend',
                        OP_L='opponent_lineup',
                        P='play',
                        F_I='friend_invite', F_K='friend_kakao',
                        A_NB='alert_nobat', A_OK='alert_ok', A_OK2='alert_ok2',
                        MI='mission', MI_R='mission_r', MI_I='mission_item')

gam.set_ref(Stages.H, 0.9)
gam.set_ref(Stages.B, 0.9)
gam.set_ref(Stages.B_R, 0.9)
gam.set_ref(Stages.B_H, 0.8)
gam.set_ref(Stages.B_S, 0.8)
gam.set_ref(Stages.B_E, 0.9)
gam.set_ref(Stages.B_LE, 0.9)
gam.set_ref(Stages.OP_L, 0.9)
gam.set_ref(Stages.P, 0.9)
gam.set_ref(Stages.F_I, 0.8)
gam.set_ref(Stages.F_K, 0.8)
gam.set_ref(Stages.A_NB, 0.9)
gam.set_ref(Stages.A_OK, 0.9)
gam.set_ref(Stages.A_OK2, 0.9)
gam.set_ref(Stages.MI, 0.9)
gam.set_ref(Stages.MI_R, 0.7)
gam.set_ref(Stages.MI_I, 0.8)

# shot = gam.take_snapshot()
# stage = Stages.A_OK2
# ref = gam.refs[stage]
# gam.find_acceptance(stage, ref[2], shot.getSubImage(ref[0]))
# # run_battle()
# gam.exit()

while True:
    if no_bat:
        gam.debug("no bat")
        no_bat = False
    if mode['battle']:
        run_battle()


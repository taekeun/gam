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

gam = Gam('star', '192', 'monkey/star/')

count = {'Q': 0, 'R': [0, 0], 'D': [0, 0]}
no_coin = [False, False]
no_ticket_sleep = 60.0 * 20.0


def add_quest():
    count['Q'] += 1
    gam.turn_end(count)


def add_raid(is_succ):
    set_count(is_succ, 'R')


def add_daily(is_succ):
    set_count(is_succ, 'D')


def set_count(is_succ, key):
    if (is_succ):
        count[key][0] += 1
    else:
        count[key][1] += 1
    gam.turn_end(count)


def get_used_sinbal():
    return count['Q'] + sum(count['D']);


Stages = gam.set_stages(
    H='home', H_AD='home_ad', H_ADA='home_ada', H_A='home_a',
    M='map', M_A='map_a', R='raid', R_A='raid_a', R_R='raid_r',
    Q='quest', Q_F='quest_f', Q_B='quest_bag', Q_N='quest_n', Q_A='quest_a',
    MI='migung', MI_A='migung_a', A='arena', A_A='arena_a',
    P='play', P_A='play_a', P_R='play_r', P_RB='play_daily_boss', P_AUTO='play_auto',
    B='bag', B_L='bag_l', B_D='bag_detail', B_S='bag_s', B_SP='bag_sp', B_P1='bag_p1', B_P2='bag_p2',
    BO='bonus', D='daily')

gam.set_ref(Stages.H, 0.8)
gam.set_ref(Stages.H_AD, 0.9)
# gam.set_ref(Stages.H_ADA, 0.9)
gam.set_ref(Stages.H_A, 0.4)
gam.set_ref(Stages.M, 0.9)
gam.set_ref(Stages.M_A, 0.4)
gam.set_ref(Stages.R, 0.8)
gam.set_ref(Stages.R_A, 0.4)
gam.set_ref(Stages.R_R, 0.9)
gam.set_ref(Stages.P, 0.9)
gam.set_ref(Stages.P_A, 0.4)
gam.set_ref(Stages.P_R, 0.9)
gam.set_ref(Stages.P_RB, 0.9)
gam.set_ref(Stages.P_AUTO, 0.9)
gam.set_ref(Stages.Q, 0.9)
gam.set_ref(Stages.Q_N, 0.9)
gam.set_ref(Stages.Q_F, 0.9)
gam.set_ref(Stages.Q_B, 0.9)
gam.set_ref(Stages.A, 0.9)
gam.set_ref(Stages.A_A, 0.4)
gam.set_ref(Stages.MI, 0.9)
gam.set_ref(Stages.MI_A, 0.4)
gam.set_ref(Stages.B, 0.9)
# gam.set_ref(Stages.B_L2, 0.6)
gam.set_ref(Stages.B_L, 0.6)
gam.set_ref(Stages.B_D, 0.9)
gam.set_ref(Stages.B_S, 0.9)
gam.set_ref(Stages.B_SP, 0.9)
gam.set_ref(Stages.B_P1, 0.4)
gam.set_ref(Stages.B_P2, 0.4)
gam.set_ref(Stages.BO, 0.9)
gam.set_ref(Stages.D, 0.8)


def check_bonus():
    gam.touch(990, 970, '출석 보너스')
    MonkeyRunner.sleep(2.0)
    gam.touch(968, 720, '확인')


def empty_bag():
    print '정리 시작'
    line = 0
    max_line = 3
    fail_count = 0
    while True:
        shot = gam.take_snapshot()
        stage = gam.current_stage(shot)
        if fail_count > 10: break

        if stage is Stages.B:
            if not gam.check_stage(shot, Stages.B_L):
                gam.touch(1600, 940, '장비창 이동')
                MonkeyRunner.sleep(3.0)
                continue
            if line > max_line: break
# -10,516,650:A, -11,117,467:B/P, -6,408,193:S, -5,863,090:N, -2,941,172:SSS, -27,357:SS, -1:C
            raw_pixel_int = shot.getRawPixelInt(290 + 190 * line, 1770)
            print line
            if -6000000 > raw_pixel_int or -10000 < raw_pixel_int:
                gam.touch(1770, 290 - 10 + 190 * (max_line - line), '장비창:' + `line`)
            line += 1
        elif stage is Stages.B_D:
            gam.touch(1309, 987, '판매')
        elif stage is Stages.B_S:
            gam.touch(794, 730, '등급판매')
        elif stage is Stages.B_SP:
            if gam.check_stage(shot, Stages.B_P1) or gam.check_stage(shot, Stages.B_P2):
                gam.touch(1180, 730, '물약 판매')
            else:
                gam.touch(794, 730, '취소')
            gam.touch(1767, 111, '장비창 나가기')
        else:
            fail_count += 1
            print '장비 정리 화면 인식 실패:' + `fail_count`
    print '정리 끝'
    gam.back()


def check_home(stage, msg):
    if stage is Stages.H:
        gam.touch(1850, 800, msg + ':레이드 초대 취소')
        return 1
    elif stage is Stages.H_AD:
        gam.touch(761, 975, msg + ':광고 취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(1180, 720, msg + ':광고 팝업 취소')
        return 2
    # elif stage is Stages.H_ADA:
    # gam.touch(1085, 720, msg+':광고 팝업 취소')
    elif stage is Stages.H_A:
        gam.touch(707, 725, msg + ':취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(783, 720, msg + ':레이드 초대 거절 확인')
        return 3
    else:
        return 0


def run_quest(is_infinity):
    dm = 'Quest:'
    is_played = False
    while True:
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        if stage is Stages.Q:
            if is_played is True:
                is_played = False
                add_quest()
                if not is_infinity: break
            gam.touch(1431, 352, dm + '퀘스트 선택')
        elif stage is Stages.Q_N:
            no_coin[0] = True
            gam.touch(1051, 756, dm + '신발 부족 확인')
            if not is_infinity:
                break
            elif no_coin[0]:
                no_coin[0] = False
                print 'no sinbal sleep' + `no_ticket_sleep / 60` + 'min'
                MonkeyRunner.sleep(no_ticket_sleep)
        elif stage is Stages.Q_F:
            gam.touch(1474, 227, dm + '친구 선택')
            gam.touch(1088, 994, dm + '입장 하기')
            MonkeyRunner.sleep(1.0)
            gam.touch(1088, 720, dm + '입장 하기-친구 없을시')
        elif stage is Stages.Q_B:
            gam.touch(786, 725, dm + '가방 정리')
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.B:
            empty_bag()
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.P:
            if is_played:
                gam.touch(900, 80, dm + '동료 호출')
            else:
                MonkeyRunner.sleep(30)
                is_played = True
        elif stage is Stages.P_R:
            gam.touch(1088, 994, dm + '모험 보상')
        elif stage is Stages.BO:
            check_bonus()
        else:
            gam.touch(1088, 994, dm + '동료맞이')
            gam.touch(1306, 994, dm + '탐험 성공/실패 : 확인, 동료맞이')


def run_raid(is_infinity):
    mode = 'Raid:'
    is_played = False
    is_succ = False

    while True:
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        msg = mode + stage

        home_checked = check_home(stage, msg)
        if home_checked > 0:
            if home_checked is 1:
                if is_played is True:
                    is_played = False
                    add_raid(is_succ)
                    if not is_infinity: break
                else:
                    gam.touch(270, 970, msg + '가방정리')
                    empty_bag()

                gam.touch(1789, 912, msg + ':모험하기')
        elif stage is Stages.M:
            # 데스 크라운
            gam.device.drag((900, 5), (900, 970), 0.1, 10)
            gam.device.drag((1630, 300), (0, 300), 0.1, 10)
            gam.touch(150, 854, msg + '데스 크라운')
        elif stage is Stages.M_A:
            no_coin[1] = True
            gam.touch(1051, 756, msg + ':티켓 부족 확인')
            if not is_infinity:
                gam.back()
                MonkeyRunner.sleep(1.0)
                break
            elif no_coin[1]:
                no_coin[1] = False
                print 'no ticket sleep' + `no_ticket_sleep / 60` + 'min'
                MonkeyRunner.sleep(no_ticket_sleep)
        elif stage is Stages.P:
            is_played = True
            MonkeyRunner.sleep(10.0)
        elif stage is Stages.P_A:
            gam.touch(1131, 85, msg + ':동료 호출')
        elif stage is Stages.R:
            gam.touch(1700, 975, msg + ':레이드 시작')
        elif stage is Stages.R_A:
            gam.touch(1360, 765, msg + ':시작 확인')
        elif stage is Stages.BO:
            check_bonus()
        elif stage is Stages.R_R:
            is_succ = True
            gam.debug(msg + ':성공')
        else:
            gam.touch(1789, 5, mode + ':탐험실패')
            gam.debug('fail to find stage:' + stage)


def run_daily(is_infinity):
    mode = 'daily:'
    is_played = False
    is_succ = False
    daily_points = [(653, 350), (870, 350), (1088, 350), (1088, 600), (1306, 600), (1523, 600), (653, 600)]

    while True:
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        msg = mode + stage

        if stage is Stages.M:
            gam.device.drag((10, 0), (10, 970), 0.1, 10)  # 세로 맵 이동
            gam.device.drag((1774, 660), (0, 660), 0.1, 10)
            gam.touch(533, 550, msg + ':요일 특별 던전')
        elif stage is Stages.D:
            if is_played is True:
                is_played = False
                add_daily(is_succ)
                if not is_infinity: break
            p = daily_points[time.localtime().tm_wday]
            gam.touch(p[0], p[1], msg + '요일 던전 선택')
        elif stage is Stages.Q_N:
            no_coin[0] = True
            gam.touch(1051, 756, msg + '신발 부족 확인')
            if not is_infinity:
                break
        elif stage is Stages.Q_F:
            gam.touch(1474, 227, msg + '친구 선택')
            gam.touch(1088, 994, msg + '입장 하기')
            MonkeyRunner.sleep(1.0)
            gam.touch(1088, 720, msg + '입장 하기-친구 없을시')
        elif stage is Stages.Q_B:
            gam.touch(786, 725, dm + '가방 정리')
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.B:
            empty_bag()
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.P:
            if gam.check_stage(shot, Stages.P_RB):
                gam.touch(1131, 85, msg + '동료 호출')
            is_played = True
        elif stage is Stages.R_R:
            is_succ = True
            gam.debug(msg + ':성공')
        else:
            gam.debug(msg + ':인식실패:' + stage)
            gam.touch(1789, 5, msg + ':탐험실패')
            gam.touch(1306, 994, msg + '탐험 성공/실패 : 확인, 동료맞이')

# shot = gam.take_snapshot()
# stage = Stages.Q
# ref = gam.refs[stage]
# gam.find_acceptance(stage, ref[2], shot.getSubImage(ref[0]))
# empty_bag()
# gam.exit()

modes = ['QR', 'Quest', 'Raid', 'Migung']
if len(sys.argv) is 1:
    sys.argv.append(modes[0])

if len(sys.argv) is not 2 or not sys.argv[1] in modes:
    print 'usage: ./monkeyrunner monkey/star/star.py [mode]'
    print 'mode: QR, Quest, Raid, Migung'
    gam.exit()
mode = sys.argv[1]

print 'start'
gam.debug('start:' + mode)

if mode == 'QR':
    while True:
        if no_coin[0] and no_coin[1]:
            print 'no sinbal, ticket sleep ' + `no_ticket_sleep / 60` + 'min'
            MonkeyRunner.sleep(no_ticket_sleep)
        no_coin[0] = False
        no_coin[1] = False
        for i in range(1): run_raid(False)

        gam.touch(707, 725, 'QR:취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(783, 720, 'QR:레이드 초대 거절 확인')
        MonkeyRunner.sleep(1.0)
        gam.touch(1789, 912, 'QR:모험하기')

        # 1D : 1Q
        if get_used_sinbal() % 2 is 0:
            run_daily(False)
        else:
            # gam.touch(572, 943, 'QR:전설선택')
            gam.device.drag((900, 970), (900, 0), 0.1, 10)  # 맵 이동
            gam.device.drag((0, 660), (1630, 660), 0.1, 10)
            gam.touch(400, 540, 'QR:사막지대')
            # gam.device.drag((900, 0), (900, 970), 0.1, 10) #맵 이동
            # gam.device.drag((1630, 660), (0, 660), 0.1, 10)
            # gam.touch(455, 811, 'QR:존의호박밭')

            for i in range(1): run_quest(False)

        gam.back()  # Map
        MonkeyRunner.sleep(1.0)
        gam.back()  # Home
        MonkeyRunner.sleep(1.0)
elif mode == 'Quest':  # 퀘스트, 사막지대 최적화
    run_quest(True)
elif mode == 'Raid':  # 레이드
    while True:
        run_raid(True)
elif mode == 'Migung':  # 미궁
    msg = '미궁:'
    is_played = False
    while True:
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        if stage is Stages.MI or Stages.A:
            if is_played is True:
                is_played = False
                add_raid(False)
            gam.touch(1632, 950, msg + '미궁도전')
        elif stage is Stages.P:
            is_played = True

        gam.touch(1088, 782, msg + '미궁도전확인')
        gam.touch(1131, 85, msg + '미궁안')
        gam.touch(979, 1025, msg + '점수확인')

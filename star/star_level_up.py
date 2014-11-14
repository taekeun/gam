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


count = {'Q': 0, 'R': [0, 0], 'D': [0, 0], 'A': [0, 0]}
no_coin = [False, False]
no_ticket_sleep = 60.0 * 10.0


def add_quest():
    count['Q'] += 1
    gam.turn_end(count)


def set_count(is_succ, key):
    if (is_succ):
        count[key][0] += 1
    else:
        count[key][1] += 1
    gam.turn_end(count)


def get_used_sinbal():
    return count['Q'] + sum(count['D']);


def drag_to_top_right():
    dragTo(True, True, False, False)


def drag_to_bottom_right():
    dragTo(False, True, True, False)


def drag_to_bottom_left():
    dragTo(False, False, True, True)


def dragTo(t, r, b, l):
    if t:
        gam.device.drag((900, 5), (900, 970), 0.1, 10)
    elif b:
        gam.device.drag((900, 970), (900, 5), 0.1, 10)

    if r:
        gam.device.drag((1630, 300), (5, 300), 0.1, 10)
    elif l:
        gam.device.drag((5, 5), (1630, 5), 0.1, 10)

def drag_by_direction(direction):
    if direction is 'rt':
        dragTo(True, True, False, False)
    elif direction is 'rb':
        dragTo(False, True, True, False)
    elif direction is 'lb':
        dragTo(False, False, True, True)
    elif direction is 'lt':
        dragTo(True, False, False, True)


def check_bonus():
    gam.touch(1000, 850, '뉴비 출석 보너스')
    gam.touch(990, 970, '출석 보너스')
    MonkeyRunner.sleep(3.0)
    gam.touch(1000, 720, '확인')


def check_auto(shot):
    if gam.check_stage(shot, Stages.P_AUTO):
        gam.touch(200, 1000, 'auto 켜기')


def check_boss_hp_and_use_scroll(shot):
    if gam.check_stage(shot, Stages.B_HP):
        gam.print_msg("low boss hp")
        gam.touch(1550, 1000, 'scroll 1')
        gam.touch(1700, 1000, 'scroll 2')
        gam.touch(1850, 1000, 'scroll 3')


def empty_bag(is_all=False):
    print '정리 시작'
    line = 3
    # max_line = 3
    fail_count = 0
    while True:
        shot = gam.take_snapshot()
        stage = gam.current_stage(shot)
        if fail_count > 10: break

        if stage is Stages.B:
            if line < 0: break
            # -10,516,650:A, -11,117,467:B/P, -6,408,193:S, -5,863,090:N, -2,941,172:SSS, -27,357:SS, -1:C
            raw_pixel_int = shot.getRawPixelInt(290 + 190 * line, 1770)
            if -6000000 > raw_pixel_int or -10000 < raw_pixel_int:
                gam.touch(1770, 290 - 10 + 190 * (3 - line), '장비창:' + `line`)
            line -= 1
        elif stage is Stages.B_D:
            gam.touch(1309, 987, '판매')
        elif stage is Stages.B_S:
            gam.touch(794, 730, '등급판매')
        elif stage is Stages.B_SP:
            if gam.check_stage(shot, Stages.B_P0):# or gam.check_stage(shot, Stages.B_P2):
                gam.touch(1180, 730, '물약 판매')
            else:
                gam.touch(794, 730, '취소')
            gam.touch(1767, 111, '장비창 나가기')
        else:
            fail_count += 1
            print '장비 정리 화면 인식 실패:' + `fail_count`
    print '정리 끝'
    gam.back()
    MonkeyRunner.sleep(1.0)


def check_home(stage, msg):
    if stage is Stages.H:
        gam.touch(1850, 800, msg + ':레이드 초대 취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(707, 725, msg + ':취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(783, 720, msg + ':레이드 초대 거절 확인')
        return 1
    elif stage is Stages.H_AD:
        gam.touch(761, 975, msg + ':광고 취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(1180, 720, msg + ':광고 팝업 취소')
        return 2
    # elif stage is Stages.H_ADA:
    # gam.touch(1085, 720, msg+':광고 팝업 취소')
    elif stage is Stages.H_AD2:
        gam.touch(1000, 950, msg + '광고2 취소')
    elif stage is Stages.H_A:
        gam.touch(707, 725, msg + ':취소')
        MonkeyRunner.sleep(1.0)
        gam.touch(783, 720, msg + ':레이드 초대 거절 확인')
        return 3
    else:
        return 0


def is_quest(stage):
    return stage is Stages.Q or stage is Stages.Q_C or stage is Stages.Q_BO


def go_to_quest(last_quest, msg=""):
    quests = [
        {'no':1, 'name':'놀우드', 'point':(800, 850), 'di':'rt', 'sq':7},
        {'no':2, 'name':'쓰러진 골렘', 'point':(700, 420), 'di':'rt', 'sq':8},
        {'no':3, 'name':'요정폭포', 'point':(1500, 500), 'di':'rt', 'sq':9},

        {'no':4, 'name':'옐로우 월', 'point':(700, 420), 'di':'lb', 'sq':8},
        {'no':5, 'name':'사막지대', 'point':(400, 520), 'di':'lb', 'sq':9},
        {'no':6, 'name':'모래폭풍의 언덕', 'point':(300, 420), 'di':'lb', 'sq':9},
        {'no':7, 'name':'추락자의 유적', 'point':(400, 200), 'di':'lb', 'sq':9},

        {'no':8, 'name':'상아이빨 호수', 'point':(1300, 750), 'di':'lb', 'sq':9},
        {'no':9, 'name':'잊혀진 유적', 'point':(600, 650), 'di':'rb', 'sq':9},
        {'no':10, 'name':'그림자 강', 'point':(1000, 750), 'di':'rb', 'sq':9},
        {'no':11, 'name':'안개 지대', 'point':(1000, 620), 'di':'rb', 'sq':9},
        {'no':12, 'name':'돌보지 않는 탑', 'point':(1000, 400), 'di':'rb', 'sq':9},

        {'no':13, 'name':'검은 바위산 입구', 'point':(1100, 700), 'di':'lt', 'sq':9},
        {'no':14, 'name':'메아리 무덤', 'point':(900, 650), 'di':'lt', 'sq':9},
        {'no':15, 'name':'망자의 산길', 'point':(700, 540), 'di':'lt', 'sq':9},
        {'no':16, 'name':'검은 성채 가는 길', 'point':(800, 300), 'di':'lt', 'sq':9},
        {'no':17, 'name':'검은 성채', 'point':(1200, 300), 'di':'lt', 'sq':9},

        {'no':18, 'name':'존의 호박밭', 'point':(500, 800), 'di':'rt', 'sq':9},
        {'no':19, 'name':'성의 입구', 'point':(1200, 300), 'di':'lb`', 'sq':9},
        {'no':20, 'name':'랜딩 가든', 'point':(1400, 400), 'di':'lb', 'sq':9},
        {'no':21, 'name':'안개 낀 성벽', 'point':(1700, 380), 'di':'lb', 'sq':9},
        {'no':22, 'name':'성채', 'point':(1500, 250), 'di':'lb', 'sq':9},
    ]

    if last_quest is None:
        index = len(quests) -1
    else:
        index = last_quest['no']
        if index >= len(quests):
            return None
    while True:
        q = quests[index]
        drag_by_direction(q['di'])
        gam.touch(q['point'][0], q['point'][1], msg + '퀘스트 선택 ' + `index` + q['name'])
        gam.sleep(1.0)

        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        if stage is not Stages.M:
            gam.print_msg(msg + '퀘스트 선택 완료: ' + `index` + q['name'])
            return q
        if index < 0:
            gam.print_msg(msg + '퀘스트 선택 실패: ' + stage)
            return None
        index -= 1


def go_to_sub_quest(last_sub_quest, msg=""):
    f = 400
    s = 600
    fp = 215
    sp = 248
    points = [(f,s),(f+fp,s),(f+fp,s-sp),(f+fp*2,s-sp),(f+fp*3,s-sp),(f+fp*3,s), (f+fp*4,s), (f+fp*5,s),(f+fp*5,s-sp)]
    if last_sub_quest is None:
        index = len(points)
    else:
        index = last_sub_quest + 1
        if index >= len(points):
            index = len(points)

    while True:
        p = points[index - 1]
        gam.touch(p[0], p[1], msg + '서브 퀘스트 선택 ' + `index`)
        gam.sleep(1.0)

        shot = gam.screen_shot()
        stage = gam.current_stage(shot)
        if gam.check_stage(shot, Stages.Q_CA):
            gam.touch(1000, 700, msg+'닫힌퀘 경고 닫기')
        elif not is_quest(stage):
            gam.print_msg(msg + '서브 퀘스트 선택 완료: ' + stage)
            return index
        if index < 0:
            gam.print_msg(msg + '서브 퀘스트 선택 실패: ' + stage)
            return None
        index -= 1

def run_levelup():
    # 맵 > 퀘스트
    # 퀘 클리어

    msg = "LevelUp:"
    is_played = False
    cur_quest = None
    cur_sub_quest = None
    while True:
        shot = gam.screen_shot()
        stage = gam.current_stage(shot)

        if check_home(stage, 'QA:') > 0:
            gam.touch(1789, 912, msg + '모험하기')
        elif stage is Stages.M:
            cur_quest = go_to_quest(cur_quest, msg)
            if cur_quest is None:
                gam.back()
        elif is_quest(stage):
            if is_played:
                is_played = False
                add_quest()
                if cur_sub_quest is not None and cur_quest is not None and cur_sub_quest >= cur_quest['sq']:
                    cur_sub_quest = 3
                    gam.back(msg + cur_quest['name'] + " 완료")
                    continue
            cur_sub_quest = go_to_sub_quest(cur_sub_quest, msg)
        elif stage is Stages.Q_N:
            no_coin[0] = True
            gam.touch(1051, 756, msg + '신발 부족 확인')
            if no_coin[0]:
                no_coin[0] = False
                print 'no ticket sleep' + `no_ticket_sleep / 60` + 'min'
                MonkeyRunner.sleep(no_ticket_sleep)
        elif stage is Stages.Q_F:
            gam.touch(1474, 227, msg + '친구 선택')
            gam.touch(1088, 994, msg + '입장 하기')
            MonkeyRunner.sleep(1.0)
            gam.touch(1088, 720, msg + '입장 하기-친구 없을시')
        elif stage is Stages.Q_B:
            gam.touch(786, 725, msg + '가방 정리')
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.B:
            empty_bag()
            MonkeyRunner.sleep(3.0)
        elif stage is Stages.P:
            check_auto(shot)
            if not is_played:
                is_played = True
                gam.touch(900, 80, msg + '동료 호출')
                MonkeyRunner.sleep(10.0)
            MonkeyRunner.sleep(1.0)
        elif stage is Stages.P_R:
            gam.touch(1088, 994, msg + '모험 보상')
        elif stage is Stages.BO or stage is Stages.BO_A or stage is Stages.BO_N or stage is Stages.BO_N_A:
            check_bonus()
        elif stage is Stages.C_N:
            gam.touch(1088, 994, msg + '동료맞이')
        elif stage is Stages.B_SP: #동료 빈자리
            gam.touch(1180, 730, '동료 만땅 진행')
        elif stage is Stages.Q_FA: #퀘 실패
            gam.touch(1200, 1000, '모험 실패 확인')
            if cur_sub_quest is not None and cur_sub_quest >  3:
                cur_sub_quest = 3
        else:
            gam.touch(1306, 850, msg + '탐험 성공/실패 : 확인')
            gam.debug('fail to find stage:' + stage)


if len(sys.argv) is 1:
    sys.argv.append(2)

if len(sys.argv) is not 2:
    print 'usage: ./monkeyrunner monkey/star_level_up.py [index]'
    gam.exit()
device_index = sys.argv[1]

gam = Gam('star_lv', '192.168.56.10' + str(device_index), 'monkey/star/')


Stages = gam.set_stages(
    H='home', H_AD='home_ad', H_AD2='home_ad2', H_ADA='home_ada', H_A='home_a',
    M='map', M_A='map_a', R='raid', R_A='raid_a', R_R='raid_r',
    Q='quest', Q_C='quest_close', Q_BO='quest_boss', Q_F='quest_f', Q_B='quest_bag', Q_N='quest_n', Q_A='quest_a', Q_FA='quest_fail',
    MI='migung', MI_A='migung_a', A='arena', A_A='arena_a', A_R='arena_r', A_N='arena_n',
    P='play', P_A='play_a', P_R='play_r', P_RB='play_daily_boss', P_AUTO='play_auto',
    B='bag', B_L='bag_l', B_D='bag_detail', B_S='bag_s', B_SP='bag_sp', B_P0='bag_p0',
    BO='bonus', BO_A='bonus_a', BO_N='bonus_new', BO_N_A='bonus_new_a', D='daily', B_HP='boss_hp', Q_CA='quest_close_a',
    C_N='colleague_n')

gam.set_ref(Stages.H, 0.8)
gam.set_ref(Stages.H_AD, 0.9)
gam.set_ref(Stages.H_AD2, 0.9)
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
gam.set_ref(Stages.Q_C, 0.9)
gam.set_ref(Stages.Q_BO, 0.9)
gam.set_ref(Stages.Q_N, 0.9)
gam.set_ref(Stages.Q_F, 0.9)
gam.set_ref(Stages.Q_B, 0.9)
gam.set_ref(Stages.Q_FA, 0.9)
gam.set_ref(Stages.A, 0.9)
gam.set_ref(Stages.A_A, 0.4)
gam.set_ref(Stages.A_R, 0.9)
gam.set_ref(Stages.MI, 0.9)
gam.set_ref(Stages.MI_A, 0.4)
gam.set_ref(Stages.B, 0.9)
# gam.set_ref(Stages.B_L2, 0.6)
gam.set_ref(Stages.B_L, 0.6)
gam.set_ref(Stages.B_D, 0.9)
gam.set_ref(Stages.B_S, 0.9)
gam.set_ref(Stages.B_SP, 0.9)
gam.set_ref(Stages.B_P0, 0.4)
gam.set_ref(Stages.BO, 0.9)
gam.set_ref(Stages.BO_A, 0.3)
gam.set_ref(Stages.BO_N, 0.8)
gam.set_ref(Stages.BO_N_A, 0.3)
gam.set_ref(Stages.D, 0.8)
gam.set_ref(Stages.C_N, 0.8)
# custom check only
gam.set_ref(Stages.A_N, 0.9)
gam.set_ref(Stages.B_HP, 0.9)
gam.set_ref(Stages.Q_CA, 0.9)


# shot = gam.take_snapshot()
# stage = Stages.BO_N
# ref = gam.refs[stage]
# gam.find_acceptance(stage, ref[2], shot.getSubImage(ref[0]))
# empty_bag()

run_levelup()
gam.exit()

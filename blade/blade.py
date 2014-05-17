# -*- coding: utf-8 -*-
#
# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage
from datetime import datetime
import commands
import sys
import os
import subprocess
sys.path.insert(0, 'monkey')
from gam import Gam

print sys.argv
gam = Gam('blade', 'LG', 'monkey/blade/')
count = {'succ':0, 'fail':0}
def add_play(is_success):
	if is_success:
		count['succ'] += 1
	else:
		count['fail'] += 1
	gam.turn_end(count)

Stages = gam.set_stages(H='home', H_A='home_a', M='map', M_A='map_a', 
	M_3='map_3', M_4='map_4', M_5='map_5', M_6='map_6',
	M_AC='map_ac', P='play', P_A='play_auto', Q_F='quest_fail', 
	Q_R="quest_r", Q_RC="quest_rc", Q_RE="quest_re")

gam.set_ref(Stages.H, (60, 1710, 90, 140), 0.9)
gam.set_ref(Stages.H_A, (60, 1710, 90, 140), 0.9)
gam.set_ref(Stages.M, (50, 1750, 100, 100), 0.9)
gam.set_ref(Stages.M_A, (50, 1750, 100, 100), 0.9)
gam.set_ref(Stages.M_AC, (270, 700, 90, 150), 0.9)
gam.set_ref(Stages.M_3, (810, 100, 50, 280), 0.9)
gam.set_ref(Stages.M_4, (810, 100, 50, 280), 0.9)
gam.set_ref(Stages.M_5, (810, 100, 50, 280), 0.9)
gam.set_ref(Stages.M_6, (810, 100, 50, 280), 0.9)
gam.set_ref(Stages.P, (60, 900, 120, 120), 0.9)
gam.set_ref(Stages.P_A, (5, 850, 40, 230), 0.5)
gam.set_ref(Stages.Q_F, (180, 650, 100, 200), 0.9)
gam.set_ref(Stages.Q_R, (430, 820, 250, 280), 0.9)
gam.set_ref(Stages.Q_RC, (110, 1050, 100, 300), 0.9)
gam.set_ref(Stages.Q_RE, (50, 1700, 70, 130), 0.9)

def current_map(shot):
	if gam.check_stage(shot, Stages.M_3): return Stages.M_3
	if gam.check_stage(shot, Stages.M_4): return Stages.M_4
	if gam.check_stage(shot, Stages.M_5): return Stages.M_5
	if gam.check_stage(shot, Stages.M_6): return Stages.M_6
	gam.print_msg('실패 : current_map')
	return ''

#TODO
#	무한던전, 난투, 1:1 돌기
#	가방 정리
#	장애물 극복 하기
sleep = 60.0 * 10.0 #잠금 제한시간 30분
def run_quest(is_infinity):
	mode = 'Quest:'
	is_played = False
	is_success = False
	while True:
		shot = gam.screen_shot()
		stage = gam.current_stage(shot)
		msg = mode+stage
		if stage is Stages.H:
			gam.touch(1780, 980, msg+'전투')
		elif stage is Stages.H_A:
			gam.touch(782, 694, msg+'장비 강화 취소')
		elif stage is Stages.M:
			if is_played is True:
				is_played = False
				add_play(is_success)
				is_success = False
				if not is_infinity: break
			# if current_map(shot) is Stages.M_3:
				# gam.touch(1190, 609, msg+'28')
				# gam.touch(1447, 564, msg+'29')
			# else:
				# gam.touch(73, 542, msg+'move to before map')
			# map 4
			# touch(1436, 172, msg+'31')
			# gam.touch(1611, 287, msg+'32')
			# gam.touch(1620, 530, msg+'33')
			# gam.touch(1414, 560, msg+'34')
			# gam.touch(999, 489, msg+'36')
			gam.touch(795, 424, msg+'37')
			# gam.touch(644, 635, msg+'38') NO!
			# gam.touch(825, 795, msg+'39')

		elif stage is Stages.M_A:
			gam.touch(1370, 815, msg+'전투시작')
		elif stage is Stages.M_AC:
			gam.touch(789, 759, msg+'영혼검 부족')
			print gam.time_to_s(datetime.now()) + ' no ticket. Sleep ' + `sleep/60` + 'min'
			gam.device.press('KEYCODE_POWER', MonkeyDevice.DOWN_AND_UP)
			MonkeyRunner.sleep(sleep)
			gam.device.wake()
		elif stage is Stages.P:
			is_played = True
			gam.touch(955, 965, msg+'자동')
		elif stage is Stages.P_A:
			gam.touch(1398, 929, msg+'스킬1')
			gam.touch(1424, 713, msg+'스킬2')
			gam.touch(1605, 612, msg+'스킬3')
		elif stage is Stages.Q_R:
			gam.touch(1512, 544, msg+'보상 선택')
		elif stage is Stages.Q_RC:
			gam.touch(1201, 917, msg+'보상 선택')
		elif stage is Stages.Q_RE:
			is_success = True
			gam.touch(1762, 1008, msg+'나가기')
		elif stage is Stages.Q_F:
			gam.touch(755, 873, msg+'포기')
		else:
			gam.print_msg('stage 찾기 실패')

# shot = gam.device.takeSnapshot()
# ref = gam.refs[Stages.M_3]
# gam.find_acceptance(Stages.M_3, ref[2], shot.getSubImage(ref[0]))

modes = ['Quest']
mode = MonkeyRunner.choice('mode?', modes, 'Choice')
print 'start'
gam.debug('start:' + modes[mode])

if mode == 0: #퀘스트, 레이드
	while True:
		run_quest(True)

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
count = {'Q':[0,0], 'F':[0,0], 'FA':[0]}
no_coin = 0 
IS_PLAYING = False

Stages = gam.set_stages(H='home', H_A='home_a', M='map', M_A='map_a', 
	M_3='map_3', M_4='map_4', M_5='map_5', M_6='map_6',
	M_AC='map_ac', P='play', P_A='play_auto', Q_F='quest_fail', 
	Q_R="quest_r", Q_RC="quest_rc", Q_RE="quest_re", 
	F='fight', F_N='fight_n', F_F='fight_f', F_P='fight_p', F_R='fight_r', F_RG='fight_rg', F_RC='fight_rc',
	FA='fighta', FA_E='fighta_e',
	B='bag', B_A='bag_a', B_S='bag_s', B_SS='bag_ss', B_SF='bag_sf')

Points = {
	'전투':[1780, 980],
	'장비 강화 취소':[782, 694]
}

gam.set_ref(Stages.H, 0.9)
gam.set_ref(Stages.H_A, 0.9)
gam.set_ref(Stages.M, 0.9)
gam.set_ref(Stages.M_A, 0.9)
gam.set_ref(Stages.M_AC, 0.9)
gam.set_ref(Stages.M_3, 0.9)
gam.set_ref(Stages.M_4, 0.9)
gam.set_ref(Stages.M_5, 0.9)
gam.set_ref(Stages.M_6, 0.9)
gam.set_ref(Stages.P, 0.9)
gam.set_ref(Stages.P_A, 0.5)
gam.set_ref(Stages.Q_F, 0.9)
gam.set_ref(Stages.Q_R, 0.9)
gam.set_ref(Stages.Q_RC, 0.9)
gam.set_ref(Stages.Q_RE, 0.9)
gam.set_ref(Stages.F, 0.9)
gam.set_ref(Stages.F_N, 0.9)
gam.set_ref(Stages.F_P, 0.9)
gam.set_ref(Stages.F_F, 0.9)
gam.set_ref(Stages.FA, 0.9)
gam.set_ref(Stages.FA_E, 0.9)
gam.set_ref(Stages.F_R, 0.9)
gam.set_ref(Stages.F_RG, 0.9)
gam.set_ref(Stages.F_RC, 0.9)
gam.set_ref(Stages.B, 0.9)
gam.set_ref(Stages.B_A, 0.9)
gam.set_ref(Stages.B_S, 0.9)
gam.set_ref(Stages.B_SS, 0.9)
gam.set_ref(Stages.B_SF, 0.9)


def add_count(is_success, count_item):
	if is_success:
		count_item[0] += 1
	else:
		count_item[1] += 1
	gam.turn_end(count)

def current_map(shot):
	if gam.check_stage(shot, Stages.M_3): return Stages.M_3
	if gam.check_stage(shot, Stages.M_4): return Stages.M_4
	if gam.check_stage(shot, Stages.M_5): return Stages.M_5
	if gam.check_stage(shot, Stages.M_6): return Stages.M_6
	gam.print_msg('실패 : current_map')
	return ''

sleep = 60.0 * 10.0 #잠금 제한시간 30분
def sleep_phone(msg='no ticket'):
	print gam.time_to_s(datetime.now()) + ' ' + msg + '. Sleep ' + `sleep/60` + 'min'
	gam.device.press('KEYCODE_POWER', MonkeyDevice.DOWN_AND_UP)
	MonkeyRunner.sleep(sleep)
	gam.device.wake()

def is_low_battery():
	battery_level = gam.battery_level()
	if battery_level <= 50:
		sleep_phone('low battery:' + `battery_level`)

def use_skill(is_played, msg):
	global IS_PLAYING
	if not is_played:
		gam.print_msg('플레이중:스킬 사용')

	IS_PLAYING = True
	gam.touch(1398, 929)
	gam.touch(1424, 713)
	gam.touch(1605, 612)

def go_battle():
	stage = gam.current_stage()
	if stage is Stages.H:
		gam.touch(1780, 980, '전투')
	MonkeyRunner.sleep(1.0)

def exit_mode(msg):
	gam.touch(100, 1000, msg+' 나가기')

def empty_bag():
	print '가방 정리 시작'
	while True:
		shot = gam.screen_shot(not IS_PLAYING)
		stage = gam.current_stage(shot)
		msg = stage + ':'

		if stage is Stages.B:
			gam.touch(1775, 890, msg+'전체팔기')
		elif stage is Stages.B_S:
			gam.touch(970, 770, msg+'팔기')
		elif stage is Stages.B_SS:
			gam.touch(970, 750, msg+'판매성공')
			break
		elif stage is Stages.B_SF:
			gam.touch(970, 750, msg+'판매실패')
			break
		else:
			gam.print_msg('가방정리:stage 찾기 실패')
	exit_mode(msg+'가방')

def mode_reward(message):
	print message + '보상 받기'
	fail_count = 0
	while True:
		shot = gam.screen_shot()
		stage = gam.current_stage(shot)
		msg = message + ':' + stage + ':'

		if gam.check_stage(shot, Stages.F_R):
			fail_count = 0
			gam.touch(1765, 700, msg+'보상 입장')
		elif stage is Stages.F_RG:
			fail_count = 0
			gam.touch(960, 920, msg+'보상 돌리기')
		elif stage is Stages.F_RC:
			gam.touch(1000, 910, msg+'보상 받기')
			break
		else:
			if fail_count >= 10: break
			gam.print_msg('보상받기:stage 찾기 실패' + `fail_count`)
			fail_count += 1

def mode_no_ticket(msg):
	gam.touch(1304, 357, msg+'티켓부족')
	global no_coin 
	no_coin += 1

#TODO
#	무한던전, 난투, 1:1 돌기
#	가방 정리
#	장애물 극복 하기
def run_quest(is_infinity):
	global no_coin 
	global IS_PLAYING
	mode = 'Quest:'
	is_played = False
	is_success = False
	IS_PLAYING = False
	while True:
		shot = gam.screen_shot(not IS_PLAYING)
		IS_PLAYING = False
		stage = gam.current_stage(shot)
		msg = mode+stage+':'
		if stage is Stages.H:
			is_low_battery()
			go_battle()
		elif stage is Stages.H_A:
			gam.touch(782, 694, msg+'장비 강화 취소')
		elif stage is Stages.M:
			if is_played is True:
				is_played = False
				add_count(is_success, count['Q'])
				is_success = False
				# if not is_infinity: break
			# map 3
			# gam.touch(1190, 609, msg+'28')
			# gam.touch(1447, 564, msg+'29')
			# map 4
			# touch(1436, 172, msg+'31')
			# gam.touch(1611, 287, msg+'32')
			# gam.touch(1620, 530, msg+'33')
			# gam.touch(1414, 560, msg+'34')
			# gam.touch(999, 489, msg+'36')
			# gam.touch(795, 424, msg+'37')
			# gam.touch(73, 542, msg+'move to before map')
			# gam.touch(644, 635, msg+'38') NO!
			# gam.touch(825, 795, msg+'39')
			# M_5
			# gam.touch(1652, 242, msg+'41')
			# gam.touch(1304, 260, msg+'44')
			# if current_map(shot) is Stages.M_5:
				# gam.touch(906, 314, msg+'46')
			# else:
				# gam.touch(73, 542, msg+'move to before map')
			# M_6
			gam.touch(1245, 355, msg+'53')
			# gam.touch(1050, 430, msg+'54')
			# gam.touch(455, 615, msg+'56')

			# if current_map(shot) is Stages.M_3:
				#touch(episode)
			# else:
				# gam.touch(73, 542, msg+'move to before map')
		elif stage is Stages.M_A:
			if (no_coin >= 1) and (not is_infinity) :
				gam.touch(1595, 240, msg+'창 닫기')
				break
			else:
				gam.touch(1370, 815, msg+'전투시작')
		elif stage is Stages.M_AC:
			gam.touch(789, 759, msg+'영혼검 부족')
			no_coin += 1
			# sleep_phone()
		elif stage is Stages.P:
			gam.touch(955, 965, msg+'자동')
		elif stage is Stages.P_A:
			use_skill(is_played, msg)
			is_played = True
		elif stage is Stages.Q_R:
			gam.touch(1512, 544, msg+'보상 선택')
		elif stage is Stages.Q_RC:
			gam.touch(1201, 917, msg+'보상 선택')
		elif stage is Stages.Q_RE:
			is_success = True
			gam.touch(1762, 1008, msg+'나가기')
		elif stage is Stages.Q_F:
			gam.touch(755, 873, msg+'포기')
		elif stage is Stages.F:
			exit_mode(msg+'stage')
		elif stage is Stages.B_A:
			gam.touch(980, 760, msg+'가방 풀')
			empty_bag()
		elif stage is Stages.B:
			empty_bag()
		else:
			gam.print_msg(msg + 'stage 찾기 실패' + stage)

def run_1vs1(is_infinity):
	global IS_PLAYING
	mode = '1vs1'
	is_played = False
	is_success = False
	while True:
		shot = gam.screen_shot(not IS_PLAYING)
		IS_PLAYING = False
		stage = gam.current_stage(shot)
		msg = mode+stage+':'
		is_low_battery()
		if stage is Stages.F:
			if gam.check_stage(shot, Stages.F_R):
				mode_reward('1:1')
			else:
				if is_played is True:
					is_played = False
					add_count(is_success, count['F'])
					is_success = False
					# if not is_infinity: break
				gam.touch(1700, 950, msg+'1:1입장')
		elif stage is Stages.F_N:
			mode_no_ticket(msg)
			if not is_infinity:
				exit_mode(msg+'1:1')
		elif stage is Stages.F_P:
			use_skill(is_played, msg)
			is_played = True
		elif stage is Stages.F_F:
			gam.touch(1715, 975, msg+'패배:나가기')
		elif stage is Stages.H or stage is Stages.M:
			break
		else:
			gam.print_msg('stage 찾기 실패')
			gam.touch(1410, 965, msg+'승리:나가기 시도')

def run_NvsN(is_infinity):
	global IS_PLAYING
	not_found_count = 0
	mode = 'NvsN'
	is_played = False
	while True:
		shot = gam.screen_shot(not IS_PLAYING)
		IS_PLAYING = False
		stage = gam.current_stage(shot)
		msg = mode+stage+':'
		is_low_battery()
		if stage is Stages.FA:
			not_found_count = 0
			if gam.check_stage(shot, Stages.F_R):
				mode_reward('난투장')
			else:
				if is_played is True:
					is_played = False
					add_count(True, count['FA'])
					if not is_infinity:
						exit_mode(msg+'난투장')
				gam.touch(1700, 950, msg+'난투장 입장')
		elif stage is Stages.F_N:
			not_found_count = 0
			mode_no_ticket(msg)
			if not is_infinity: 
				exit_mode(msg+'난투장')
		elif stage is Stages.F_P:
			not_found_count = 0
			use_skill(is_played, msg)
			is_played = True
		elif stage is Stages.FA_E:
			not_found_count = 0
			gam.touch(1700, 1000, msg+'난투 종료')
		elif stage is Stages.H or stage is Stages.M:
			break
		else:
			not_found_count += 1
			gam.print_msg(msg + 'stage 찾기 실패' + stage)
			if not_found_count >= 5:
				gam.touch(960, 640, '혹시 접속 끊김?')
			elif not_found_count >= 15:
				break

# shot = gam.device.takeSnapshot()
# ref = gam.refs[Stages.FA]
# gam.find_acceptance(Stages.FA, ref[2], shot.getSubImage(ref[0]))

# run_NvsN(False)
# mode_reward('test')
# gam.exit()

modes = ['All', 'Quest']
if len(sys.argv) is 1:
	sys.argv.append(modes[0])

if len(sys.argv) is not 2 or not sys.argv[1] in modes:
	print 'usage: ./monkeyrunner monkey/blade/blade.py [mode]'
	print 'mode: All, Quest'
	gam.exit()
mode = sys.argv[1]

print 'start'
gam.debug('start:' + mode)

if mode == 'All': #퀘스트, 레이드
	while True:
		is_low_battery()
		if no_coin >= 2: #난투장은 1회만 참여한다.
			sleep_phone('no ticket(' + `no_coin` + ')')
		no_coin = 0

		run_quest(False)
		gam.touch(1800, 1000, '1:1대결')
		run_1vs1(False)
		go_battle()
		gam.touch(1600, 1000, '난투장')
		run_NvsN(False)
		# no_coin += 1
elif mode == 'Quest':
	while True:
		is_low_battery()
		if no_coin >= 1:
			sleep_phone('no ticket(' + `no_coin` + ')')
		no_coin = 0

		run_quest(False)

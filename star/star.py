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

gam = Gam('star', '192', 'monkey/star/')

count = {'sinbal':0, 'ticket':0}
no_coin = [False, False]

def add_sinbal():
	count['sinbal'] += 1
	gam.turn_end(count)

def add_ticket():
	count['ticket'] += 1
	gam.turn_end(count)

Stages = gam.set_stages(H='home', H_A='home_a', M='map', M_A='map_a', R='raid', 
R_A='raid_a', Q='quest', Q_F='quest_f', Q_B='quest_bag', Q_N='quest_n', Q_A='quest_a', MI='migung', MI_A='migung_a', 
A='arena', A_A='arena_a', P='play', P_A='play_a', P_R='play_r', B='bag', B_L='bag_l', B_D='bag_detail', B_S='bag_s')

gam.set_ref(Stages.H, (20, 1620, 180, 170), 0.8)
gam.set_ref(Stages.H_A, (20, 1620, 180, 170), 0.4)
gam.set_ref(Stages.M, (100,1400,80,250), 0.9)
gam.set_ref(Stages.M_A, (100,1400,80,250), 0.4)
gam.set_ref(Stages.R, (85,1500,175,145), 0.8)
gam.set_ref(Stages.R_A, (85,1500,175,145), 0.4)
gam.set_ref(Stages.P, (35,20,85,95), 0.9)
gam.set_ref(Stages.P_A, (35,20,85,95), 0.4)
gam.set_ref(Stages.P_R, (920,780,80,250), 0.9)
gam.set_ref(Stages.Q, (650,740,150,120), 0.9)
gam.set_ref(Stages.Q_N, (530,730,200,350), 0.9)
gam.set_ref(Stages.Q_F, (970,800,80,250), 0.9)
gam.set_ref(Stages.Q_B, (300,550,100,300), 0.9)
gam.set_ref(Stages.A, (100,1300,80,250), 0.9)
gam.set_ref(Stages.A_A, (100,1300,80,250), 0.4)
gam.set_ref(Stages.MI, (100,1300,80,250), 0.9)
gam.set_ref(Stages.MI_A, (100,1300,80,250), 0.4)
gam.set_ref(Stages.B, (100,1570,80,140), 0.9)
gam.set_ref(Stages.B_L, (100,1230,80,120), 0.6)
gam.set_ref(Stages.B_D, (50,1550,90,100), 0.9)
gam.set_ref(Stages.B_S, (300,530,100,350), 0.9)

def empty_bag():
	print '정리 시작'
	line = 3
	current_line = 3
	fail_count = 0
	while True:
		shot = gam.take_snapshot()
		stage = gam.current_stage(shot)
		if fail_count > 10: break

		if stage is Stages.B:
			if not gam.check_stage(shot, Stages.B_L): 
				gam.touch(1470, 940, '장비창 이동')
				continue 
			if current_line is -1: break
# -15035905:A, -14364067:B/P, -6408193:S, -5863090:N, -2941172:SSS, -27357:SS, -1:C
			l = line - current_line
			raw_pixel_int = shot.getRawPixelInt(290 + 190 * l, 1652)
			if -10000000 > raw_pixel_int or -10000 < raw_pixel_int:
				l = current_line
				gam.touch(1652, 290-10 + 190 * l, '장비창:' + `l`)
			current_line -= 1
		elif stage is Stages.B_D:
			gam.touch(1203, 987, '판매')
		elif stage is Stages.B_S:
			gam.touch(730, 730, '등급판매')
		else:
			fail_count += 1
			print '장비 정리 화면 인식 실패:' + `fail_count`
	print '정리 끝'
	gam.back()

# shot = gam.take_snapshot()
# ref = gam.refs[Stages.Q_N]
# gam.find_acceptance(Stages.Q_N, ref[2], shot.getSubImage(ref[0]))
# empty_bag()
# gam.exit()

#TODO
# 물약 판매 처리
# 신발 티켓 부족시 쉬기
#  각각 부족시 시간 기록하고, 둘다 부족시 작은시간 만큼 쉰다.
def run_quest(is_infinity):
	dm = 'Quest:'
	is_played = False
	while True:
		shot = gam.screen_shot()
		stage = gam.current_stage(shot)
		if stage is Stages.Q:
			if is_played is True:
				is_played = False
				add_sinbal()
				if not is_infinity: break
			gam.touch(1315, 352, dm+'퀘스트 선택')
		elif stage is Stages.Q_N:
			no_coin[0] = True
			gam.touch(966, 756, dm+'신발 부족 확인')
			if not is_infinity: break
		elif stage is Stages.Q_F:
			gam.touch(1355, 227, dm+'친구 선택')
			gam.touch(1000, 994, dm+'입장 하기')
		elif stage is Stages.Q_B:
			gam.touch(723, 725, dm+'가방 정리')
			MonkeyRunner.sleep(3.0)
		elif stage is Stages.B:
			empty_bag()
			MonkeyRunner.sleep(3.0)
		elif stage is Stages.P:
			gam.touch(1040, 85, dm+'동료 호출')
			is_played = True
		elif stage is Stages.P_R:
			gam.touch(1000, 994, dm+'모험 보상')
		else:
			gam.touch(1000, 994, dm+'동료맞이')
			gam.touch(1200, 994, dm+'탐험 성공/실패 : 확인, 동료맞이')

def run_raid(is_infinity):
	mode = 'Raid:'
	is_played = False
	while True:
		shot = gam.screen_shot()
		stage = gam.current_stage(shot)
		msg = mode+stage
		if stage is Stages.H:
			if is_played is True:
				is_played = False
				add_ticket()
				if not is_infinity: break
			gam.touch(1700, 800, msg+':레이드 초대')
			gam.touch(1644, 912, msg+':모험하기')
		elif stage is Stages.H_A:
			gam.touch(650, 725, msg+':취소')
			gam.touch(720, 720, msg+':레이드 초대 거절 확인')
		elif stage is Stages.M:
			#블랙 마운틴
		   	# device.drag((900, 5), (900, 970), 0.1, 10)
		   	# device.drag((0, 300), (1630, 300), 0.1, 10)
		   	# touch(1247, 422, mode+stage+':블랙 마운틴')
		   	gam.touch(572, 943, msg+':전설선택')
		   	gam.device.drag((900, 0), (900, 970), 0.1, 10) #맵 이동
		   	gam.device.drag((1630, 660), (0, 660), 0.1, 10)
		   	# if count['ticket'] % 4 == 3:
		   	if False:
			   	gam.touch(1283, 330, msg+':진데스 크라운')
			   	gam.debug(msg+':진데스 크라운')
			else:
			   	# touch(1132, 453, mode+stage+':데스 크라운')
			   	gam.touch(155, 855, msg+':데스 크라운')
		elif stage is Stages.M_A:
			no_coin[1] = True
			gam.touch(966, 756, msg+':티켓 부족 확인')
			if not is_infinity: 
				gam.back()
				MonkeyRunner.sleep(1.0)
				break
		elif stage is Stages.P:
			is_played = True
		elif stage is Stages.P_A:
			gam.touch(1040, 85, msg+':동료 호출')
		elif stage is Stages.R:
		   	gam.touch(1640, 975, msg+':레이드 시작')
		elif stage is Stages.R_A:
		   	gam.touch(1250, 765, msg+':시작 확인')
		else:
			gam.touch(1644, 5, mode+':탐험실패')

modes = ['QR', 'Quest', 'Raid', 'Migung']
mode = MonkeyRunner.choice('mode?', modes, 'Choice')
print 'start'
gam.debug('start:' + modes[mode])

if mode == 0: #퀘스트, 레이드
	while True:
		if no_coin[0] and no_coin[1]:
			print 'no sinbal, ticket sleep 10 min'
			MonkeyRunner.sleep(60.0*10.0)
		no_coin[0] = False
		no_coin[1] = False
		for i in range(1): run_raid(False)

		gam.touch(650, 725, 'QR:취소')
		gam.touch(1644, 912, 'QR:모험하기')

	   	gam.touch(572, 943, 'QR:전설선택')
	   	gam.device.drag((900, 970), (900, 0), 0.1, 10) #맵 이동
	   	gam.device.drag((0, 660), (1630, 660), 0.1, 10)
	   	gam.touch(400, 540, 'QR:사막지대')
	   	# gam.device.drag((900, 0), (900, 970), 0.1, 10) #맵 이동
	   	# gam.device.drag((1630, 660), (0, 660), 0.1, 10)
	   	# gam.touch(455, 811, 'QR:존의호박밭')

		for i in range(1): run_quest(False)

		gam.back()
		MonkeyRunner.sleep(1.0)
		gam.back()
		MonkeyRunner.sleep(1.0)
elif mode == 1: #퀘스트, 사막지대 최적화
	run_quest(True)
elif mode == 2: #레이드
	while True:
		run_raid(True)
elif mode == 3: #미궁
	msg = '미궁:'
	is_played = False
	while True:
		shot = gam.screen_shot()
		stage = gam.current_stage(shot)
		if stage is Stages.MI or Stages.A:
			if is_played is True:
				is_played = False
				add_ticket()
			gam.touch(1500, 950, msg+'미궁도전')
		elif stage is Stages.P: 
			is_played = True

		gam.touch(1000, 782, msg+'미궁도전확인')
		gam.touch(1040, 85, msg+'미궁안')
		gam.touch(900, 1025, msg+'점수확인')
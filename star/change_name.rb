File.open('names', 'r') do |f|
	while line = f.gets
		# puts line
		name = line.split(',')[0]
		p = line.split(',')[1].split('_').map {|i| i.to_i }
		puts name + ' : ' + 
			p[0].to_s + ',' + 
			(p[1] * 1920 / 1794).to_s + ',' + 
			p[2].to_s + ',' + 
			(p[3] * 1920 / 1794).to_s
	end
end

arena_a : 100,1391,80,267
arena : 100,1391,80,267
bag : 100,1680,80,149
bag_detail : 50,1658,90,107
bag_l : 100,1316,80,128
bag_l2 : 100,1316,80,64
bag_p2 : 780,1027,130,171
bag_s : 300,567,100,374
bag_sp : 300,567,100,374
daily : 880,642,100,374
home : 20,1733,180,181
home_a : 20,1733,180,181
map : 100,1498,80,267
migung : 100,1391,80,267
migung_a : 100,1391,80,267
play : 35,21,85,101
play_a : 35,21,85,101
play_r : 920,834,80,267
quest : 650,791,150,128
quest_f : 970,856,80,267
quest_bag : 300,588,100,321
raid : 85,1605,175,155
raid_a : 85,1605,175,155
play_daily_boss : 1050,1337,10,107
home_ad : 65,963,90,374
home_ada : 300,374,400,1177
quest_n : 530,781,200,374

bag_p1 : 780,1027,130,171
bonus : 970,749,80,428
map_a : 100,1498,80,267












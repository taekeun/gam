require 'time'
require 'json'

#TODO
# Twitter DM 보내기
# 모니터 시작 이후의 로그만 수집하기

class Game
	attr_accessor :is_check, :count, :updated, :elapsed, :time_limit, :warning_count
	def initialize(name, time_limit)
		@is_check = false
		@updated = Time.now
		@elapsed = 0
		@time_limit = time_limit
		@warning_count = 0
		@name = name
	end

	def update(updated, elapsed, count)
		@updated = updated
		@elapsed = elapsed.hour * 60 * 60 + elapsed.min * 60 + elapsed.sec
		@count = count
		reset_warning_count
	end

	def reset_warning_count
		if @warning_count > 0
			puts "#{Time.now} !OK! #{@name} back!"
		end
		@warning_count = 0
	end
end

games = {'blade'=>Game.new('blade', 60*13), 'star'=>Game.new('star', 60*25)}
while true
	games.each do |name, game|
		game.is_check = false
	end
	f = File.open('log.txt', 'r')
	lines = f.readlines[-100..-1]
	lines.reverse.each do |line|
		logs = line.split('|')
		next unless logs.size == 4
		game = games[logs[1]]
		next if game.is_check

		game.is_check = true
		time = 	Time.parse('2014-'+logs[0])
		next if game.updated >= time

		game.update(time, Time.parse(logs[2]), JSON.parse(logs[3].gsub(/[']/, '"')))

		puts line
	end
	f.close

	games.each do |name, game|
		elapsed = (Time.now - game.updated).to_i
		if elapsed > game.time_limit and game.warning_count < 3
			puts "#{Time.now} !WARNING! #{name} no updated #{elapsed.to_i / 60} min"
			game.warning_count += 1
		end
	end
	sleep(60 * 1)
end

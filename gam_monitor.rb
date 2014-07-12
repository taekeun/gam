require 'time'
require 'json'
require 'twitter'

# @taekeun
twitter = Twitter::REST::Client.new do |config|
  config.consumer_key = 'D3EI02n2IpUgCg84qJkEudo9i'
  config.consumer_secret = 'jHjW0sEx8PwNxkAZ742h9mWjpjT5tyjq6GVBxmvdjaAbFRptxS'
  config.access_token = '546968795-Gn1wweBSBaQOTbvqn88h7CSknHZf6NQ8e19ppxx4'
  config.access_token_secret = 'HeYaybXmOOuSFybwsONxKyA2ND6I81coQ2Xzb2r8L4Uk0'
end

def twitter_direct_message(twitter, message)
	twitter.create_direct_message('taekeun', message)
end

def twitter_update(twitter, message)
	# twitter.update(message)
end

#TODO
# Twitter DM 보내기

class Game
	attr_accessor :is_check, :count, :updated, :elapsed, :time_limit, :warning_count
	def initialize(name, time_limit)
		@is_check = false
		@updated = Time.now
		@elapsed = 0
		@time_limit = time_limit
		@warning_count = 1
		@name = name
	end

	def update(updated, elapsed, count)
		@updated = updated
		@elapsed = elapsed.hour * 60 * 60 + elapsed.min * 60 + elapsed.sec
		@count = count
		return reset_warning_count
	end

	def reset_warning_count
		if @warning_count > 0
			@warning_count = 0
			message = "#{Time.now.strftime("%m/%d %H:%M")} !OK! #{@name} 복귀! #{@count}"
			puts message
			return message
		else 
			return false
		end
	end
end
puts 'Start Gam Monitor'
games = {'blade'=>Game.new('blade', 60*15), 'star'=>Game.new('star', 60*30)}
while true
	games.each do |name, game|
		game.is_check = false
	end
	f = File.open('log.txt', 'r')
	lines = f.readlines[-50..-1]
	if lines.nil?
		sleep(60 * 1)
		next
	end
	lines.reverse.each do |line|
		logs = line.split('|')
		next unless logs.size == 4
		game = games[logs[1]]
		next if game.is_check

		game.is_check = true
		time = 	Time.parse('2014-'+logs[0])
		next if game.updated >= time

		puts line
		twitter_update(twitter, line)
		message = game.update(time, Time.parse(logs[2]), JSON.parse(logs[3].gsub(/[']/, '"')))
		twitter_direct_message(twitter, message) if message
	end
	f.close

	games.each do |name, game|
		elapsed = (Time.now - game.updated).to_i
		if elapsed > game.time_limit and game.warning_count < 1
			message = "#{Time.now.strftime("%m/%d %H:%M")} !경고! #{name} 진행 없음 #{elapsed.to_i / 60}분:#{game.count}"
			puts message
			twitter_direct_message(twitter, message)
			game.warning_count += 1
		end
	end
	sleep(60 * 1)
end

require 'time'
require 'json'
require 'twitter'


class Notifier
  def initialize
    @dm_sender = Twitter::REST::Client.new do |config|
      config.consumer_key = 'D3EI02n2IpUgCg84qJkEudo9i'
      config.consumer_secret = 'jHjW0sEx8PwNxkAZ742h9mWjpjT5tyjq6GVBxmvdjaAbFRptxS'
      config.access_token = '546968795-Gn1wweBSBaQOTbvqn88h7CSknHZf6NQ8e19ppxx4'
      config.access_token_secret = 'HeYaybXmOOuSFybwsONxKyA2ND6I81coQ2Xzb2r8L4Uk0'
    end

    @gam_monitor = Twitter::REST::Client.new do |config|
      config.consumer_key = 'e6ay8euOVcbPrtJvoB8Ye2oGa'
      config.consumer_secret = 'Lh8EsMpTuErlI04Ufdr6awyqjUuNKpdGd9Rvpe83pRDwWVGZai'
      config.access_token = '2726119297-wKx5iwvVN3sTHFz97Ygj2qAsTAZz2FH9s0BCiCo'
      config.access_token_secret = 'LSVJESUu7L0JlO8Z0M5pdS2UobMnyP0CYqBlG06ctWIiH'
    end
  end

  def alert(message)
    puts message
    @dm_sender.create_direct_message('taekeun', message)
    update_status(message)
  end

  def update_status(message)
    puts message
    @gam_monitor.update(message)
  end
end

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
    reset_warning_count
	end

	def reset_warning_count
		if @warning_count > 0
			@warning_count = 0
			message = "#{Time.now.strftime("%m/%d %H:%M")} !OK! #{@name} 복귀! #{@count}"
		else
      false
		end
	end
end

no_process_warn_cnt = 0
def check_process(name)
  `ps aux | grep #{name}` != ''
end

puts 'Start Gam Monitor'
games = {'blade'=>Game.new('blade', 60*15), 'star'=>Game.new('star', 60*25), 'star_lv'=>Game.new('star_lv', 60*25)}

notifier = Notifier.new

while true
  if check_process('star.p[y]')
    # if no_process_warn_cnt > 0
      # message = "#{Time.now.strftime("%m/%d %H:%M")} 복귀 'star.py'"
      # notifier.alert(message)
    # end
    no_process_warn_cnt = 0
  elsif no_process_warn_cnt < 3
    message = "#{Time.now.strftime("%m/%d %H:%M")} !경고! 비정상 종료 'star.py'"
    notifier.alert(message)
    no_process_warn_cnt += 1
  end

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
		next if game.nil? or game.is_check

		game.is_check = true
		time = 	Time.parse('2014-'+logs[0])
		next if game.updated >= time

    notifier.update_status(line)
		message = game.update(time, Time.parse(logs[2]), JSON.parse(logs[3].gsub(/[']/, '"')))
    notifier.alert(message) if message
	end
	f.close

	games.each do |name, game|
		elapsed = (Time.now - game.updated).to_i
		if elapsed > game.time_limit and game.warning_count < 1
			message = "#{Time.now.strftime("%m/%d %H:%M")} !경고! #{name} 진행 없음 #{elapsed.to_i / 60}분:#{game.count}"
      notifier.alert(message)
			game.warning_count += 1
		end
	end
	sleep(60 * 1)
end

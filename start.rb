# encoding: UTF-8

require 'pty'

device_index = 2
if ARGV.size > 0
  device_index = ARGV[0]
end

if device_index.to_i < 2
  puts "device_index #{device_index} < 2"
  exit
end

@pid = nil
@cmd = "monkeyrunner monkey/star/star_level_up.py #{device_index}"

def is_running(pid)
  return false if pid.nil?
  begin
    Process.getpgid pid
    true
  rescue Errno::ESRCH
    false
  end
end

Dir.chdir('/Users/bran/Development/android-sdk-macosx/tools')

while true
  unless is_running @pid
    unless @pid.nil?
      puts '비정상 종료 탐지.'
      sleep(10)
    end
    begin
      puts '[starter] starting ' + @cmd
      PTY.spawn(@cmd) do |stdin, stdout, pid|
        puts @pid = pid
        stdin.each { |line| print line }
      end
    rescue Interrupt => e
      puts '[starter] Terminating....'
      Process.kill(9, @pid)
      exit
    rescue Exception => e
      puts '[starter] !!! Exception occur !!!'
      puts e.message
      puts e.backtrace.join("\n")
      puts e
    end
  end
end

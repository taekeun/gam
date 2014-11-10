# encoding: UTF-8

require 'pty'

@pid = nil
@cmd = 'monkeyrunner monkey/star/star_level_up.py'

def is_running(pid)
  return false if pid.nil?

  begin
    Process.getpgid pid
    return true
  rescue Errno::ESRCH
    return false
  end
end

Dir.chdir('/Users/bran/Development/android-sdk-macosx/tools')

while true
  unless is_running @pid
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

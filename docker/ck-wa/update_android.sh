#!/usr/bin/expect -f

spawn android update sdk -a -s --no-ui --filter tools,platform-tools,build-tools-23.0.3,android-19

expect "y/n "
send "y\r"

set timeout 3600
expect eof

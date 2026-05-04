#!/bin/bash
cd /home/vm-ssh/gartner
nohup python3 app.py > server.log 2>&1 &
sleep 2
echo "Server started. PID: $(pgrep -f 'python3 app.py')"
tail -n 10 server.log

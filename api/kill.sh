kill -9 `ps aux | grep server.py | grep -v grep | awk '{print $2}'`

kill $(cat script.pid)
rm script.pid
python3 control.py stop

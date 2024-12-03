if [ ! -f ./script.pid ]; then
    python3 main.py >/dev/null &
    echo $! > script.pid
    echo "Started"
else
    echo "Already running. Stopping..."
    ./stopDetach.sh
    python3 main.py >/dev/null &
    echo $! > script.pid
    echo "Started"
fi




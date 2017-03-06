#!/bin/bash

SLEEP=1
SSH_SERVER="smi-ca1"
SSH_USER="mrakitin"

check_tunnel() {
    ps -ef | grep 'ssh -fN' | grep $USER | grep -v grep
}

kill_tunnel() {
    tunnel_status=$(check_tunnel)
    if [ ! -z "$tunnel_status" ]; then
        pid=$(echo $tunnel_status | awk '{print $2}')
        echo "Running tunnel found. Killing pid=${pid}..."
        kill $pid
        sleep $SLEEP
    fi
}

if [ "$1" == "kill" ]; then
    echo "tunnel status:" $(check_tunnel)
    kill_tunnel
    echo "tunnel status:" $(check_tunnel)
    exit 0
fi

tunnel_status=$(check_tunnel)
echo "tunnel status:" $tunnel_status
if [ -z "$tunnel_status" ]; then
    ssh -fN -o ExitOnForwardFailure=yes ${SSH_SERVER} 2>/dev/null
    sleep $SLEEP
    echo "tunnel status:" $(check_tunnel)
fi

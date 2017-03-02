#!/bin/bash

SLEEP=1
SSH_SERVER="chx-srv1"
SSH_USER="mrakitin"
MOUNT_DIR="/XF11ID/data/"

check_mount() {
    mount | grep 'ssh'
}

check_tunnel() {
    ps -ef | grep 'ssh -fN' | grep $USER | grep -v grep
}

check_sshfs() {
    ps -ef | grep 'sshfs' | grep $USER | grep -v grep
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

kill_sshfs() {
    sshfs_status=$(check_sshfs)
    if [ ! -z "$sshfs_status" ]; then
        pid=$(echo $sshfs_status | awk '{print $2}')
        echo "Running sshfs  found. Killing pid=${pid}..."
        kill $pid
        sleep $SLEEP
    fi
}


if [ "$1" == "kill" ]; then
    echo "tunnel status:" $(check_tunnel)
    echo "sshfs status :" $(check_sshfs)
    echo "mount status :" $(check_mount)
    kill_tunnel
    kill_sshfs
    echo "tunnel status:" $(check_tunnel)
    echo "sshfs status :" $(check_sshfs)
    echo "mount status :" $(check_mount)
    exit 0
fi

tunnel_status=$(check_tunnel)
echo "tunnel status:" $tunnel_status
if [ -z "$tunnel_status" ]; then
    ssh -fN -o ExitOnForwardFailure=yes $SERVER 2>/dev/null
    sleep $SLEEP
    echo "tunnel status:" $(check_tunnel)
fi

sshfs_status=$(check_sshfs)
mount_status=$(check_mount)
echo "sshfs status :" $sshfs_status
echo "mount status :" $mount_status
if [ -z "$mount_status" ]; then
    sshfs ${SSH_USER}@${SSH_SERVER}:${MOUNT_DIR} ${MOUNT_DIR}
    sleep $SLEEP
    echo "sshfs status :" $(check_sshfs)
    echo "mount status :" $(check_mount)
fi


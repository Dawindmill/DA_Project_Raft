#!/bin/sh

# check get two arguments
if [ $# -eq 1 ] 
then
    echo "total peers need to launch => $2"
else
    echo "invalid argument => need one args -> total number of peers "
    exit 1
fi

for i in $(seq $1)
do
    python3 raft_single.py peer$i $1 &
    echo "launching peer_$i done"
done

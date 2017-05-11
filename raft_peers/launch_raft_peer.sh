#!/bin/sh

# check get two arguments
if [ $# -eq 2 ] 
then
    echo "host => $1, total peers need to launch => $2"
else
    echo "invalid argument => need two args first is the host ip and second is the total number of peers "
    exit 1
fi

for i in $(seq $2)
do
    echo "lauching peer_$i"
    python3 raft_single.py $1 peer$i $2
done

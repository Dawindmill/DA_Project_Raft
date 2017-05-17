This Raft program is implemented by following Raft paper (https://raft.github.io/)

Folder: raft_peer

raft_single.py is the main file which starts the Raft program.

Pre-requisite:

To run this program, you need to install jsonpickle.

Simply run: 'pip install jsonpickle' or 'pip3 install jsonpickle'

This program should be run with Python3, it is not compatible with Python2

The 'raft_peer.ini' file be included in the same folder, you should modify
the peer names, ports and timeouts in the 'raft_peer.ini' file before
start the raft program and make sure all the peers get the same one.


How to run:

use the command:

'python3 raft_sinlge peername peernum [-v]'

-v is optional flag for connecting to our game to visualize the Raft algorithm in gameplay.

peername should be in the raft_peer.ini file
the total number of peers should not exceed the number of peer names in raft_peer.ini file.

Example run:

'python3 raft_single peer1 3' -> this will launch a peer and he will assume there are 3 peers
in total in this Raft system.

'python3 raft_single peer2 3' -> peer2 join the above system

'python3 raft_single peer3 3' -> peer3 join the above system

Raft run with visualization/game:

'python3 raft_single peer1 3 -v ' -> this will launch a peer and he will assume there are 3 peers
in total in this Raft system and visualization game is started before running peers

'python3 raft_single peer2 3 -v' -> peer2 join the above system

'python3 raft_single peer3 3 -v' -> peer3 join the above system

launch_raft_peer.sh could be used to automatically start peers

Example:

'sh launch_raft_peer.sh 3' -> will launch 3 peers, and their name is peer1, peer2 and peer3

The CLI tester -> User.py


In side the folder 'RaftPeer.py' is the core file which contains all the logics of Raft with the
help of other classes.

Its responsibility is to send, receive, and processing the PRCs, we use JSON as our message
passing protocol for simplicity.

TimeoutCounter is the random timeout class, which will start election or sending append entreis.

The state of the peer is stored in class 'RaftPeerState', all other class are used to forming the
RPCs JSON needed to be sent according to current 'RaftPeerState' and the current state of the
Raft system. Log is stored as list of instances of LogData (LogData.py) class.

You could start User.py by by running

'python3 User.py 3' -> 3 indicates that there are three peers in the system, and their names are
peer1, peer2 and peer3, User.py needs 'raft_peer.ini' for working correctly.

Some commands you can execute in User.py through keyboard:

['x', 'add', '100'] => this command will send request_command to leader and ask to add x to 100

PS: User.py might take some time to find leader, so you should wait for it stops printing messages
and hit enter to enter the above sample command.


Folder: Visualization

game.py is the main file which starts the game program for visualizing Raft in gameplay

How to run:

Pre-requisite:

To run this program, you need to install pygame.

Simply run: 'pip install pygame' or 'pip3 install pygame'

This program should be run with Python3, it is not compatible with Python2

The port used in visualizatio could be modified in constant.py (GAME_HOST, GAME_PORT) and make sure
the host ip and port are in the 'raft_peer.ini' file for every peers.

Example run:

'python3 game.py'

Folder: raft_peers/logs

This folder will contain all the logs of each started peers, so make sure you have folder named
'logs' in the same folder for Raft program

You could use key 's' to stop monster attacking villager and click the villager to kill him/her
for showing Raft properties.

For sample RPCs used in this Raft system, you could check out the markdown file README.MD.

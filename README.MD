# Distributed Algorithm Project - Raft Implementation

## Team Members:
- Regina Zhang - 646179
- Bingfeng Liu - 639187 
- Jimmy Chiang - 822373
- Wen-Pin Wu - 871702 

## Milestones

- Raft Leader Election
- Raft Game
- Bridging Raft and Game
- Report
- Snapshot Algorithm based on Raft Leader Election

## Current Game Screenshot

![Image of Game Screenshot](./current_game_screenshot.png)

## RPCs Examples in Raft

RPC Message Type | Example JSON format | Description
---------------- | ------------------- | -----------
request_vote_reply | {"msg_type": 'request_vote_reply', 'send_to': ['localhost', 10002], 'send_from': ['localhost', 10001], 'sender_term': 5, 'vote_granted': True} | Used to reply the candidate’s vote requesting.
request_vote | {"last_log_index": 1, "last_log_term": 2, "msg_type": "request_vote", "peer_id": "peer2", "send_from": ["localhost", 10002], "send_to": ["localhost", 10001], "sender_term": 5} | Used for candidate to broadcast to request vote
append_entries_leader ( no entries) | {"leader_commit_index": -1, "msg_type": "append_entries_leader", "new_entries": [], "peer_id": "peer2", "prev_log_index": 1, "prev_log_term": 2, "send_from": ["localhost", 10002], "send_to": ["localhost", 10001], "sender_term": 5} | Used for leader to send out its heartbeat or appendEntries
append_entries_leader (with entries)|{"leader_commit_index": -1, "msg_type": "append_entries_leader", "new_entries": [{"py/object": "LogData.LogData", "log_applied": false, "log_index": 1, "log_term": 2, "majority_count": 0, "request_command_action_list": ["x", "add", "100"], "request_user_addr_port_tuple": null}, {"py/object": "LogData.LogData", "log_applied": false, "log_index": 2, "log_term": 5, "majority_count": 1, "request_command_action_list": ["x", "add", "100"], "request_user_addr_port_tuple": ["127.0.0.1", 59182]}], "peer_id": "peer2", "prev_log_index": 0, "prev_log_term": 1, "send_from": ["localhost", 10002], "send_to": ["localhost", 10001], "sender_term": 5} | This is an example appendEntries which included the logs.
append_entries_follower_reply | {'log_index_start': -1, 'log_index_end': -1, 'send_from': ['localhost', 10001], 'send_to': ['localhost', 10002], 'sender_term': 5, 'append_entries_result': False, 'msg_type': 'append_entries_follower_reply'} | Used to reply the leader’s append_entries_leader message.
request_command | {"msg_type": "request_command", "request_command_list": [], "send_to": ["127.0.0.1", 20001], "send_from": ["127.0.0.1", 59162]} | Used by user to request performing certain commands in the system.
request_command (learn_skill) | {"msg_type": "request_command", "request_command_list": ["armour", "learn_skill", true], "send_from": ["127.0.0.1", 59894], "send_to": ["127.0.0.1", 20002]} | One example of user sending commands to add skill variable in the Log of each peer
request_command_reply | {'msg_type': 'request_command_reply', 'command_result': 'not_leader', 'send_from': ('127.0.0.1', 20001), 'send_to': ['127.0.0.1', 59162]} | Used to reply to the user about the result of the command. If received the empty command_list in request_command JSON the command result will be either ‘not_leader’ or ‘is_leader’ to inform the user whether it connected to the leader or not.

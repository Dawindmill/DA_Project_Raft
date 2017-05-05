implement Koln Village based on Raft algorithm


	Wen-Pin Wu - 871702

The University of Melbourne Melbourne, Australia 



Title + Author Information + Abstract + Keywords + Introduction Section (2 pages)


Abstract (not finish yet!!)

Social media is of great significance in modern society and the analysis of Twitter data has shown an increasing trend towards supporting different research efforts, from understanding society to marketing and analysis of organizations. The ubiquity of Twitter with over 2.9million Tweeters in Australia alone means that it can be used for many (potentially unforeseen) activities. In this paper we consider how it can be used for estimation of crowd sizes. This is useful for calculating public event attendance as well as for potential safety concerns. In order to establish the relationship between social media usage and crowd sizes we focus on a range of sporting events, where attendances are known. From this we create a prediction model that can be used to estimate unknown crowd sizes based on social media use alone. We show how it is possible to benchmark the accuracy of the crowd size estimation by introducing other information. Finally, we apply the prediction model to estimate the attendance at the Melbourne marathon event where unknown numbers of attendees were present. 

Keywords – Koln Village, Raft, Distributed algorithm, Consensus algorithm
Keywords – Cloud, big data, social media, crowd estimation. 



Introduction

A distributed algorithm, such as Ricart and Agrawala’s algorithm [2] or Maekawa’s voting algorithm [3], is an algorithm run on the separated components for communicate with different processes. Leader election, consensus, spanning tree generation, mutual exclusion, and resource allocation are the traditional issues solved by distributed algorithms
This essay focus on leader election and consensus algorithm, which is the process of agreeing on one result among a group of participants. Needless to say, when it cones to error dandling, this problem becomes extremely difficult.
In this project, there are two parts: the raft algorithm part and software implementation part. In the raft algorithm part, we systematically implement leader election, consensus and snapshot, meanwhile, our system has reliable failure detecter for handling unpredicted errors. Not to mention, we evaluate the performance when it comes to how many processes exist in the same time. For the software implementation part, we select python for our main language and implement Koln Village from front-end to back-end for demonstrating our algorithm to users. 
Koln Village is XX game 


Background Survey (4 pages)

Consensus algorithms 
Consensus is the process of agreeing on one result among a group of participants. This problem becomes difficult when the participants or their communication medium may experience failures. [4]


The Paxos algorithm

The algorithm runs in a message-passing model with asynchrony and less than n/2 crash failures. As always, we want to get agreement, validity, and termination. The Paxos algorithm itself is mostly concerned with guaranteeing agreement and validity while allowing for the possibility of termination if there is a long enough interval in which no process restarts the protocol.

Processes are classified as proposers, accepters, and learners. The idea is that a proposer attempts to ratify a proposed decision value by collecting acceptances from a majority of the accepters, and this ratification is observed by the learners. Agreement is enforced by guaranteeing that only one proposal can get the votes of a majority of accepters, and validity follows from only allowing input values to be proposed. The tricky part is ensuring that we don't get deadlock when there are more than two proposals or when some of the processes fail. The intuition behind how this works is that any proposer can effectively restart the protocol by issuing a new proposal, and there is a procedure to release accepters from their old votes if we can prove that the old votes were for a value that won't be getting a majority any time soon.

To organize this vote-release process, we attach a distinct proposal number to each proposal. The safety properties of the algorithm don't depend on anything but the proposal numbers being distinct, but since higher numbers override lower numbers, to make progress we'll need them to increase over time. The simplest way to do this in practice is to make the proposal number be a timestamp plus the proposer's id to break ties. We could also have the proposer poll the other processes for the most recent proposal number they've seen and add 1 to it.

The revoting mechanism now works like this: before taking a vote, a proposer tests the waters by sending a prepare(n) message to all accepters where n is the proposal number. An accepter responds to this with a promise never to accept any proposal with a number less than n (so that old proposals don't suddenly get ratified) together with the highest-numbered proposal that the accepter has accepted (so that the proposer can substitute this value for its own, in case the previous value was in fact ratified). If the proposer receives a response from a majority of the accepters, the proposer then does a second phase of voting where it sends an accept(n, v) to all accepters and wins if receives a majority of votes.

So for each proposal, the algorithm proceeds as follows:

The proposer sends a message prepare(n) to all accepters. (Sending to only a majority of the accepters is enough, assuming they will all respond.)
Each accepter compares n to the highest-numbered proposal for which it has responded to a prepare message. If n is greater, it responds with ack(n, v, nv) where v is the highest-numbered proposal it has accepted and nv is the number of that proposal (or ⊥, 0 if there is no such proposal). (An optimization at this point is to allow the accepter to send back nack(higher number) to let the proposer know that it's doomed and should back off and try again—this keeps a confused proposer who thinks it's the future from locking up the protocol until 2037.)
The proposer waits (possibly forever) to receive ack from a majority of accepters. If any ack contained a value, it sets v to the most recent (in proposal number ordering) value that it received. It then sends accept(n, v) to all accepters (or just a majority). You should think of accept as a command ("Accept!") rather than acquiescence ("I accept")—the accepters still need to choose whether to accept or not.
Upon receiving accept(n, v), an accepter accepts v unless it has already received prepare(n') for some n' > n. If a majority of acceptors accept the value of a given proposal, that value becomes the decision value of the protocol.
Note that acceptance is a purely local phenomenon; additional messages are needed to detect which if any proposals have been accepted by a majority of accepters. Typically this involves a fourth round, where accepters send accepted(n, v) to all learners (often just the original proposer).

There is no requirement that only a single proposal is sent out (indeed, if proposers can fail we will need to send out more to jump-start the protocol). The protocol guarantees agreement and validity no matter how many proposers there are and no matter how often they start.

The Raft algorithm

Raft is a consensus algorithm for managing a replicated log. It produces a result equivalent to (multi-)Paxos, and it is as efficient as Paxos, but its structure is different from Paxos; this makes Raft more understandable than Paxos and also provides a better foundation for build- ing practical systems. In order to enhance understandabil- ity, Raft separates the key elements of consensus, such as leader election, log replication, and safety, and it enforces a stronger degree of coherency to reduce the number of states that must be considered. Results from a user study demonstrate that Raft is easier for students to learn than Paxos. Raft also includes a new mechanism for changing the cluster membership, which uses overlapping majori- ties to guarantee safety. 
Byzantine Fault Tolerant Raft [6]
We propose a Byzantine Fault Tolerant variant of the Raft consensus algorithm, BFTRaft, inspired by the original Raft[1] algorithm and the Practical Byzantine Fault Tolerance algorithm[2]. BFT Raft maintains the safety, fault tolerance, and liveness properties of Raft in the presence of Byzantine faults, while also aiming towards to Raft’s goal of simplicity and understandability. We have implemented a proof-of-concept of this algorithm in the Haskell programming language. 


ideal of implementation 
why you think that we need to do this game 


Implementation Details (7 pages)








Discussions and Future Directions and Application Domains (3 pages)




References (1 page) (Approximately 10 papers are acceptable).


[1] In Search of an Understandable Consensus Algorithm. Stanford University 
USA 2014

[2] Maekawa, M.,Oldehoeft, A.,Oldehoeft, R.(1987). Operating Systems: Advanced Concept.Benjamin/Cummings Publishing Company, Inc.

[3] ^M. Maekawa, "A √N algorithm for mutual exclusion in decentralized systems”, ACM Transactions in Computer Systems, vol. 3., no. 2., pp. 145-159, 1985.

[4] Pease, Marshall; Shostak, Robert; Lamport, Leslie (April 1980). "Reaching Agreement in the Presence of Faults". Journal of the Association for Computing Machinery. 27 (2): 228–234. Retrieved 2007-02-02.

[5] Lynch, Nancy (1996). Distributed Algorithms. San Francisco, CA: Morgan Kaufmann Publishers. ISBN 978-1-55860-348-6.

[6] Copeland, Christopher and Zhong, Hongxia. Tangaroa: a Byzantine Fault Tolerant Raft: Stanford, 2015.

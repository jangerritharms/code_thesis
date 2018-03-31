# Towards a tamper-proof collective memory

The goal of pairwise auditing is to provide a data exchange and verfication
mechanism with proven manipulation resistance on a couple of attacks. While
the detection of attacks is possible with the TrustChain technology, there is
no mechanism to make sure that manipulators are detected and banned. 

## Components

- **Agent**: An agent is the main entity that can attempt interactions. Agents have
  a personal hashchain which contains all their interactions of the past. Additionally
  they keep track of other interactions, together with their personal transactions
  this amounts to their private information set. Agents are identifiable by a public
  key, which we assume to be live-long.
  
  * PersonalChain
  * PrivateData
  * PublicKey

- **Network**: A network consists of all agents known to the dataset. 

  * Agents

- **PairwiseAuditing**: A mechanism for data verification and exchange. Two nodes
  exchange their personal chain and private data and verify that their personal
  chains are complete. If so, they become a wittness for the current status of 
  the other agent's chain and publish an.

- **Accusation**: When finding a node that has double-spend, an accusation 
  mechanism spreads the public key of the accused agent to other agents such 
  that they can 

## Attacks

- **Double-spending**: In a double-spending attack an agent can reuse resources
  by publishing two similar requests to two different agents without telling 
  them about the other. It is equivalent to withholding the end of the personal
  chain of the attacking agent or creating a fork of the agent's personal chain.
  Our multichain architecture makes such forks detectable to nodes that know
  about both transactions and can see the same previous hash in both transaction
  blocks.

- **Self-promotion**: In a self-promotion attack an agent withholds data about
  other agents which have a high ranking in order to achieve a higher ranking 
  in the eyes of the other agent. Honest reporting of their private data can
  however be enforced by requiring agents to first send a hash of their complete
  private data before receiving any data from the other agent. Then, agents 
  cannot send a subset of their private data. 

- **Block-withholding**: A simple block-withholding attack of personal blocks
  can simply be detected through checking the completeness of a chain. Not sending
  the full chain will be seen as a manipulation attempt.

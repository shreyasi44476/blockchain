from wallet import Wallet
from node import Node
from blockchain import Transaction


# =========================================================
# CREATE WALLETS
# =========================================================

alice = Wallet()
bob = Wallet()
charlie = Wallet()


# =========================================================
# CREATE NODES
# =========================================================

nodeA = Node("Node A", alice.address)
nodeB = Node("Node B", bob.address)
nodeC = Node("Node C", charlie.address)


# =========================================================
# CONNECT NODES
# =========================================================

nodeA.connect_peer(nodeB)
nodeA.connect_peer(nodeC)

nodeB.connect_peer(nodeA)
nodeB.connect_peer(nodeC)

nodeC.connect_peer(nodeA)
nodeC.connect_peer(nodeB)


# =========================================================
# CREATE TRANSACTION
# =========================================================

transaction = Transaction(
    alice.address,
    bob.address,
    10
)

transaction.sign(alice)


# =========================================================
# ADD TRANSACTION TO NODE A
# =========================================================

nodeA.broadcast_transaction(
    transaction,
    alice
)


# =========================================================
# MINE BLOCK ON NODE A
# =========================================================

print("\nNode A mining...")

nodeA.blockchain.mine_pending_transactions(
    charlie.address
)


# Get Block 1
block1 = nodeA.blockchain.chain[-1]


# Broadcast Block 1
nodeA.broadcast_block(block1)


# =========================================================
# SHOW CHAIN LENGTHS
# =========================================================

print("\nBefore synchronization:")

print(
    "Node A:",
    len(nodeA.blockchain.chain)
)

print(
    "Node B:",
    len(nodeB.blockchain.chain)
)

print(
    "Node C:",
    len(nodeC.blockchain.chain)
)


# =========================================================
# SYNCHRONIZE
# =========================================================

print("\nSynchronizing nodes...")

nodeB.synchronize()
nodeC.synchronize()


# =========================================================
# SHOW FINAL LENGTHS
# =========================================================

print("\nAfter synchronization:")

print(
    "Node A:",
    len(nodeA.blockchain.chain)
)

print(
    "Node B:",
    len(nodeB.blockchain.chain)
)

print(
    "Node C:",
    len(nodeC.blockchain.chain)
)


# =========================================================
# VALIDATE
# =========================================================

print("\nBlockchain validity:")

print(
    "Node A:",
    nodeA.blockchain.is_chain_valid()
)

print(
    "Node B:",
    nodeB.blockchain.is_chain_valid()
)

print(
    "Node C:",
    nodeC.blockchain.is_chain_valid()
)
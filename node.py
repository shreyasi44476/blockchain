from blockchain import Blockchain, Block


class Node:

    def __init__(self, name, address):

        self.name = name

        self.blockchain = Blockchain(
            address
        )

        self.peers = []

    # =====================================================
    # CONNECT PEER
    # =====================================================

    def connect_peer(self, peer):

        self.peers.append(peer)

    # =====================================================
    # BROADCAST TRANSACTION
    # =====================================================

    def broadcast_transaction(
        self,
        transaction,
        wallet
    ):

        # Add transaction to this node
        added = self.blockchain.add_transaction(
            transaction,
            wallet
        )

        if not added:
            return

        # Send transaction to connected peers
        for peer in self.peers:

            if not peer.has_transaction(
                transaction
            ):

                peer.blockchain.pending_transactions.append(
                    transaction
                )

                print(
                    transaction,
                    "broadcasted from",
                    self.name,
                    "to",
                    peer.name
                )

    # =====================================================
    # CHECK IF TRANSACTION ALREADY EXISTS
    # =====================================================

    def has_transaction(
        self,
        transaction
    ):

        for existing in (
            self.blockchain.pending_transactions
        ):

            if (
                existing.sender
                == transaction.sender
                and
                existing.receiver
                == transaction.receiver
                and
                existing.amount
                == transaction.amount
            ):

                return True

        return False

    # =====================================================
    # BROADCAST BLOCK
    # =====================================================

    def broadcast_block(
        self,
        block
    ):

        for peer in self.peers:

            # Check whether this is the next block
            if len(
                peer.blockchain.chain
            ) == block.index:

                # Create a separate copy of the block
                new_block = Block(
                    block.index,
                    block.data,
                    block.previous_hash
                )

                # Copy the original block's values
                new_block.timestamp = (
                    block.timestamp
                )

                new_block.nonce = (
                    block.nonce
                )

                new_block.difficulty = (
                    block.difficulty
                )

                new_block.hash = (
                    block.hash
                )

                # Add copied block to peer's blockchain
                peer.blockchain.chain.append(
                    new_block
                )

                # Remove transactions that are now mined
                peer.blockchain.pending_transactions = []

                print(
                    "Block",
                    block.index,
                    "broadcasted from",
                    self.name,
                    "to",
                    peer.name
                )

    # =====================================================
    # REPLACE CHAIN
    # =====================================================

    def replace_chain(
        self,
        new_chain
    ):

        # New chain must be longer
        if len(new_chain) <= len(
            self.blockchain.chain
        ):

            print(
                self.name,
                ": Chain is not longer."
            )

            return False

        # Save old chain
        old_chain = self.blockchain.chain

        # Temporarily use new chain
        self.blockchain.chain = new_chain

        # Validate new chain
        if not self.blockchain.is_chain_valid():

            # Restore old chain
            self.blockchain.chain = old_chain

            print(
                self.name,
                ": Received chain is invalid."
            )

            return False

        print(
            self.name,
            ": Chain replaced successfully."
        )

        return True

    # =====================================================
    # SYNCHRONIZE BLOCKCHAIN
    # =====================================================

    def synchronize(self):

        for peer in self.peers:

            # Check whether peer has a longer chain
            if len(
                peer.blockchain.chain
            ) > len(
                self.blockchain.chain
            ):

                print(
                    self.name,
                    "checking chain from",
                    peer.name
                )

                # Copy peer's chain
                self.replace_chain(
                    peer.blockchain.chain.copy()
                )
import hashlib
import json
from time import time


# =========================================================
# TRANSACTION
# =========================================================

class Transaction:

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = None

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "signature": str(self.signature)
        }

    def sign(self, wallet):

        message = (
            str(self.sender)
            + str(self.receiver)
            + str(self.amount)
        )

        self.signature = wallet.sign(message)

    def verify_signature(self, wallet):

        if self.signature is None:
            return False

        message = (
            str(self.sender)
            + str(self.receiver)
            + str(self.amount)
        )

        return wallet.verify(
            message,
            self.signature
        )

    def __str__(self):

        return (
            f"{self.sender} -> "
            f"{self.receiver}: "
            f"{self.amount}"
        )


# =========================================================
# BLOCK
# =========================================================

class Block:

    def __init__(
        self,
        index,
        data,
        previous_hash
    ):

        self.index = index
        self.timestamp = time()
        self.data = data
        self.previous_hash = previous_hash

        self.nonce = 0

        # Difficulty of this block
        self.difficulty = 0

        self.hash = self.calculate_hash()

    def calculate_hash(self):

        transaction_data = []

        if isinstance(self.data, list):

            for transaction in self.data:

                if isinstance(
                    transaction,
                    Transaction
                ):

                    transaction_data.append(
                        transaction.to_dict()
                    )

                else:

                    transaction_data.append(
                        transaction
                    )

        else:

            transaction_data = self.data

        block_data = (
            str(self.index)
            + str(self.timestamp)
            + json.dumps(
                transaction_data,
                sort_keys=True
            )
            + str(self.previous_hash)
            + str(self.nonce)
            + str(self.difficulty)
        )

        return hashlib.sha256(
            block_data.encode()
        ).hexdigest()

    def mine_block(self, difficulty):

        # Store difficulty before calculating hashes
        self.difficulty = difficulty

        target = "0" * difficulty

        attempts = 0

        while self.hash[:difficulty] != target:

            self.nonce += 1
            attempts += 1

            self.hash = self.calculate_hash()

            if attempts % 1000000 == 0:

                print(
                    "Attempts:",
                    attempts
                )

        print("Block mined!")
        print("Attempts:", attempts)
        print("Nonce:", self.nonce)
        print("Difficulty:", self.difficulty)
        print("Hash:", self.hash)


# =========================================================
# BLOCKCHAIN
# =========================================================

class Blockchain:

    def __init__(self, owner_address):

        self.chain = [
            self.create_genesis_block()
        ]

        self.difficulty = 4

        self.pending_transactions = []

        self.balances = {
            owner_address: 100
        }

        self.mining_reward = 10

    # -----------------------------------------------------
    # GENESIS BLOCK
    # -----------------------------------------------------

    def create_genesis_block(self):

     genesis = Block(
        0,
        "Genesis Block",
        "0"
    )

    # Every node must have the exact same genesis timestamp
     genesis.timestamp = 0

    # Genesis block does not require mining
     genesis.difficulty = 0
     genesis.nonce = 0

    # Recalculate hash after setting fixed values
     genesis.hash = genesis.calculate_hash()

     return genesis
    # -----------------------------------------------------
    # LATEST BLOCK
    # -----------------------------------------------------

    def get_latest_block(self):

        return self.chain[-1]

    # -----------------------------------------------------
    # ADD TRANSACTION
    # -----------------------------------------------------

    def add_transaction(
        self,
        transaction,
        wallet
    ):

        if not transaction.verify_signature(
            wallet
        ):

            print(
                "Invalid transaction."
                " Transaction rejected."
            )

            return False

        sender_balance = self.balances.get(
            transaction.sender,
            0
        )

        if sender_balance < transaction.amount:

            print(
                "Insufficient balance."
                " Transaction rejected."
            )

            return False

        self.pending_transactions.append(
            transaction
        )

        print(
            "Transaction added successfully."
        )

        return True

    # -----------------------------------------------------
    # PROCESS TRANSACTION
    # -----------------------------------------------------

    def process_transaction(
        self,
        transaction
    ):

        sender = transaction.sender
        receiver = transaction.receiver
        amount = transaction.amount

        sender_balance = self.balances.get(
            sender,
            0
        )

        if sender_balance < amount:

            print(
                "Insufficient balance."
            )

            return False

        self.balances[sender] = (
            sender_balance - amount
        )

        self.balances[receiver] = (
            self.balances.get(
                receiver,
                0
            )
            + amount
        )

        return True

    # -----------------------------------------------------
    # MINE PENDING TRANSACTIONS
    # -----------------------------------------------------

    def mine_pending_transactions(
        self,
        miner_address
    ):

        if len(
            self.pending_transactions
        ) == 0:

            print(
                "No pending transactions to mine."
            )

            return

        new_block = Block(
            len(self.chain),
            self.pending_transactions.copy(),
            self.get_latest_block().hash
        )

        new_block.mine_block(
            self.difficulty
        )

        self.chain.append(
            new_block
        )

        # Process transactions
        for transaction in (
            self.pending_transactions
        ):

            self.process_transaction(
                transaction
            )

        # Mining reward
        self.balances[miner_address] = (
            self.balances.get(
                miner_address,
                0
            )
            + self.mining_reward
        )

        # Clear pending transactions
        self.pending_transactions = []

    # -----------------------------------------------------
    # VALIDATE BLOCKCHAIN
    # -----------------------------------------------------

    def is_chain_valid(self):

        for i in range(
            1,
            len(self.chain)
        ):

            current = self.chain[i]

            previous = self.chain[i - 1]

            # Check hash
            if current.hash != (
                current.calculate_hash()
            ):

                return False

            # Check previous hash
            if current.previous_hash != (
                previous.hash
            ):

                return False

            # Check Proof of Work
            if current.hash[
                :current.difficulty
            ] != (
                "0" * current.difficulty
            ):

                return False

        return True

    # -----------------------------------------------------
    # CALCULATE CHAIN WORK
    # -----------------------------------------------------

    def get_chain_work(self):

        work = 0

        for block in self.chain:

            if block.index == 0:
                continue

            work += 16 ** block.difficulty

        return work
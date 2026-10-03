import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            'index': 1,
            'timestamp': 0,
            'transactions': [],
            'nonce': 0,
            'previous_hash': '0' * 64
        }
        self.chain.append(genesis)

    @staticmethod
    def hash(block):
        # block_string = json.dumps(block,  sort_keys=True).encode()   wersja z sort_keys=True
        block_string = json.dumps(block).encode() # wersja bez sort_keys=True
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': transactions,
            'nonce': 0,
            'previous_hash': self.hash(self.last_block)
        }
        self.chain.append(block)
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block['previous_hash'] != self.hash(previous_block):
                return False(f"Invalid previous hash for Block: {current_block['index']}")

            if self.hash(current_block) != self.hash(current_block):
                return False

        return True


if __name__ == '__main__':
    bc = blockchain = Blockchain()
    bc.add_block(["Alice -> Bob: 5"])
    bc.add_block(["Bob -> Carol: 2"])
    bc.add_block(["Carol -> Dave: 1"])
    for block in bc.chain:
        print(json.dumps(block, indent=2,ensure_ascii=False))
        print("Hash:", bc.hash(block))
        print("-" * 70)

    print("Is blockchain valid?", bc.is_chain_valid())

    bc.chain[1]['transactions'] = ["Alice -> Bob: 10"]
    print("Is blockchain valid after change?", bc.is_chain_valid())

    bc.chain[1]['transactions'] = ["Alice -> Bob: 5"]
    print("Is blockchain valid after reverting change?", bc.is_chain_valid())

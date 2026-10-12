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
    def hash(block, sort_keys=True):
        block_string = json.dumps(block, sort_keys=sort_keys).encode()
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
                return False, f"Błąd integralności! Niezgodność między blokiem {previous_block['index']} a {current_block['index']} (pierwszy niepoprawny blok: {current_block['index']})"

        return True, "Łańcuch jest poprawny (Brak błędów)"


if __name__ == '__main__':
    print("=== ZADANIE 2.2: Tworzenie łańcucha ===")
    bc = Blockchain()
    bc.add_block(["Alice -> Bob: 5"])
    bc.add_block(["Bob -> Carol: 2"])
    bc.add_block(["Carol -> Dave: 1"])

    for block in bc.chain:
        print(json.dumps(block, indent=2, ensure_ascii=False))
        print("Hash:", bc.hash(block))
        print("-" * 70)

    print("\n=== ZADANIE 2.2 : Test sort_keys=True vs False ===")
    b1_a = {'index': 1, 'timestamp': 0, 'transactions': [], 'nonce': 0, 'previous_hash': '0'*64}
    b1_b = {'previous_hash': '0'*64, 'nonce': 0, 'transactions': [], 'timestamp': 0, 'index': 1}
    
    print("Z sort_keys=True:")
    print("  Słownik A:", bc.hash(b1_a, sort_keys=True))
    print("  Słownik B:", bc.hash(b1_b, sort_keys=True))
    print("Bez sort_keys (sort_keys=False):")
    print("  Słownik A:", bc.hash(b1_a, sort_keys=False))
    print("  Słownik B:", bc.hash(b1_b, sort_keys=False))

    print("\n=== ZADANIE 2.3: Weryfikacja integralności ===")
    print("1. Stan początkowy:", bc.is_chain_valid())

    bc.chain[1]['transactions'][0] = "Alice -> Bob: 500"
    print("2. Po manipulacji w bloku nr 2:", bc.is_chain_valid())

    for i in range(2, len(bc.chain)):
        bc.chain[i]['previous_hash'] = bc.hash(bc.chain[i - 1])
    print("3. Po przeliczeniu previous_hash przez atakującego:", bc.is_chain_valid())

    bc.chain[-1]['transactions'][0] = "Carol -> Dave: 9999"
    print("4. Po modyfikacji ostatniego bloku:", bc.is_chain_valid())
import hashlib
import json
import copy
import matplotlib.pyplot as plt
from time import time


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.current_transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def new_transaction(self, sender, recipient, amount):
        if amount <= 0:
            raise ValueError("Kwota musi być liczbą dodatnią")
        if not sender or not recipient:
            raise ValueError("Nadawca i odbiorca muszą być niepustymi ciągami znaków")
        if sender == recipient:
            raise ValueError("Nadawca i odbiorca nie mogą być sobie równi")
            
        if sender != "0" and self.get_balance(sender) < amount:
            raise ValueError(f"Brak wystarczających środków na adresie {sender}!")

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1
        
    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.get('transactions', []):
                if tx['recipient'] == address:
                    balance += tx['amount']
                if tx['sender'] == address:
                    balance -= tx['amount']
                    
        for tx in self.current_transactions:
            if tx['recipient'] == address:
                balance += tx['amount']
            if tx['sender'] == address:
                balance -= tx['amount']
        return balance

    def proof_of_work(self, block):
        block['nonce'] = 0
        computed_hash = self.hash(block)
        while not computed_hash.startswith('0' * self.difficulty):
            block['nonce'] += 1
            computed_hash = self.hash(block)
        return computed_hash

    def mine(self, miner_address):
        reward = {"sender": "0", "recipient": miner_address, "amount": 1}
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': [reward] + self.current_transactions,
            'nonce': 0,
            'previous_hash': self.hash(self.last_block)
        }
        self.proof_of_work(block)
        self.current_transactions = []
        self.chain.append(block)
        return block

    def simulate_attack(self, modified_chain, start_index):
        start_time = time()
        for i in range(start_index, len(modified_chain)):
            previous_block = modified_chain[i - 1]
            block_to_remine = modified_chain[i]
            
            block_to_remine['previous_hash'] = self.hash(previous_block)
            self.proof_of_work(block_to_remine)
            
        return time() - start_time

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

    def is_chain_valid(self, chain):
        if chain[0] != self.chain[0]:
            return False, "Błąd integralności! Niepoprawny blok początkowy"
        for i in range(1, len(chain)):
            previous, block = chain[i-1], chain[i]
            if block['previous_hash'] != self.hash(previous):
                return False, f"Błąd integralności! Niepoprawny previous_hash w bloku {block['index']}"
            if not self.hash(block).startswith('0' * self.difficulty):
                return False, f"Błąd integralności! Niepoprawny hash w bloku {block['index']}"
        return True, "Łańcuch jest poprawny"

# LAB 2 
if __name__ == '__main__':
    print("=== ZADANIE 2.1: Implementacja transakcji i wydobywania ===")
    bc_init = Blockchain(difficulty=3)
    bc_init.new_transaction("0", "Alice", 10)
    bc_init.new_transaction("Alice", "Bob", 5)
    bc_init.mine("Miner_1")
    bc_init.new_transaction("Bob", "Carol", 2)
    bc_init.mine("Miner_1")
    bc_init.new_transaction("Carol", "Dave", 1)
    bc_init.mine("Miner_1")
    for block in bc_init.chain:
        print(json.dumps(block, indent=2, ensure_ascii=False))
        print("Hash:", bc_init.hash(block))
        print("-" * 50)
    print("\n")


    print("=== ZADANIE 2.2: Badanie wpływu trudności ===")
    difficulties = []
    avg_times = []
    total_hashes = 0
    total_time = 0

    for difficulty in range(1, 7):
        bc = Blockchain(difficulty=difficulty)
        bc.new_transaction("0", "Alice", 100)
        
        block_count = 2 if difficulty == 6 else 5
        nonces = []
        mining_times = []

        for _ in range(block_count):
            start = time()
            block = bc.mine(miner_address="Miner1")
            mining_times.append(time() - start)
            nonces.append(block['nonce'])

        avg_time = sum(mining_times) / len(mining_times)
        difficulties.append(difficulty)
        avg_times.append(avg_time)
        
        total_hashes += sum(nonces)
        total_time += sum(mining_times)

        print(f"d={difficulty}: średni nonce={sum(nonces)/len(nonces):.2f}, "
              f"średni czas={avg_time:.4f} s, poprawny={bc.is_chain_valid(bc.chain)[0]}")
        
    hashrate = total_hashes / total_time if total_time > 0 else 0
    print(f"\n=> Szacowana wydajność Twojego komputera: {hashrate:.2f} H/s")
    
    btc_hashes_per_block = (600 * 10**18) * 600 
    years_to_mine = (btc_hashes_per_block / hashrate) / (3600 * 24 * 365) if hashrate > 0 else 0
    print(f"=> Szacowany czas wydobycia bloku BTC (solo): {years_to_mine:.2e} lat")

    print("\n[!] ZAMKNIJ OKNO Z WYKRESEM, ABY KONTYNUOWAĆ SKRYPT...")
    plt.figure(figsize=(8,5))
    plt.plot(difficulties, avg_times, marker='o', linestyle='-', color='b')
    plt.yscale('log')
    plt.xlabel('Trudność (d)')
    plt.ylabel('Średni czas wydobycia [s]')
    plt.title('Wpływ trudności na czas wydobycia (skala logarytmiczna)')
    plt.grid(True, which="both", ls="--")
    plt.show()


    print("\n=== ZADANIE 2.3: Atak na integralność łańcucha ===")
    bc_attack = Blockchain(difficulty=4)
    bc_attack.new_transaction("0", "Alice", 1000) 
    for _ in range(5):
        bc_attack.new_transaction("Alice", "Bob", 10) 
        bc_attack.mine("Miner_A")
        
    hacked_chain = copy.deepcopy(bc_attack.chain)
    
    hacked_chain[1]['transactions'][1]['amount'] = 9999
    
    is_valid_before = bc_attack.is_chain_valid(hacked_chain)[0]
    print(f"Czy łańcuch jest poprawny po ręcznej zmianie kwoty? {is_valid_before}")

    print("Symulacja ataku (d=4)...")
    time_attack_4 = bc_attack.simulate_attack(hacked_chain, start_index=1)
    print(f"Czas przeliczania całego łańcucha (d=4): {time_attack_4:.4f} s")
    print(f"Czy łańcuch jest poprawny po ataku? {bc_attack.is_chain_valid(hacked_chain)[0]}")

    print("\nSymulacja ataku dla trudności d=5...")
    bc_attack.difficulty = 5
    hacked_chain_5 = copy.deepcopy(bc_attack.chain)
    hacked_chain_5[1]['transactions'][1]['amount'] = 9999
    time_attack_5 = bc_attack.simulate_attack(hacked_chain_5, start_index=1)
    print(f"Czas przeliczania całego łańcucha (d=5): {time_attack_5:.4f} s")


    print("\n=== ZADANIE 2.4: Walidacja transakcji ===")
    bc_val = Blockchain(difficulty=2) 
    bc_val.new_transaction("0", "Dave", 100)
    bc_val.mine("Miner_B")
    print(f"Saldo Dave'a: {bc_val.get_balance('Dave')}")
    
    print("Test: Próba transakcji na kwotę ujemną...")
    try:
        bc_val.new_transaction("Dave", "Eve", -20)
    except ValueError as e:
        print(f" -> Złapano wyjątek: {e}")
        
    print("Test: Próba przesłania do samego siebie...")
    try:
        bc_val.new_transaction("Dave", "Dave", 10)
    except ValueError as e:
        print(f" -> Złapano wyjątek: {e}")
        
    print("Test: Próba wydania zbyt dużych środków...")
    try:
        bc_val.new_transaction("Dave", "Eve", 500)
    except ValueError as e:
        print(f" -> Złapano wyjątek: {e}")
        
    print("Test: Poprawna transakcja Dave -> Eve (50)...")
    bc_val.new_transaction("Dave", "Eve", 50)
    bc_val.mine("Miner_B")
    print(f"Saldo Dave'a po operacji: {bc_val.get_balance('Dave')}")
    print(f"Saldo Eve po operacji: {bc_val.get_balance('Eve')}")
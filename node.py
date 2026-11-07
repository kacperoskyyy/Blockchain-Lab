from argparse import ArgumentParser
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchainlab2 import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace("-", "")

blockchain = Blockchain(difficulty=4)

#info o łanuchu
@app.get("/chain")
def full_chain():
    return jsonify({"chain": blockchain.chain, "length": len(blockchain.chain)}), 200


#zwrotka oczekjącychc transakcji
@app.get("/transactions/pending")
def pending_transactions():
    return jsonify({"pending_transactions": blockchain.current_transactions}), 200


#konkretny blok po indeksie 
@app.get("/block/<int:index>")
def get_block(index):
    if 0 < index <= len(blockchain.chain):
        return jsonify(blockchain.chain[index - 1]), 200
    else:
        return jsonify({"error": "Blok nie zostal znaleziony"}), 404


#nowa transakcja
@app.post("/transactions/new")
def new_transaction():
    values = request.get_json(silent=True) or {}
    required = ["sender", "recipient", "amount"]
    
    if not all(k in values for k in required):
        return jsonify({"error": "Brak wymaganych pol: sender, recipient, amount"}), 400

    sender = values["sender"]
    recipient = values["recipient"]
    amount = values["amount"]

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Kwota (amount) musi byc liczba dodatnia!"}), 400
    
    if not isinstance(sender, str) or not isinstance(recipient, str):
        return jsonify({"error": "Sender i recipient musza byc tekstami!"}), 400
        
    if not sender.strip() or not recipient.strip():
        return jsonify({"error": "Sender i recipient nie moga byc puste!"}), 400
        
    if sender == recipient:
        return jsonify({"error": "Sender i recipient nie moga byc tacy sami!"}), 400

    try:
        index = blockchain.new_transaction(sender, recipient, amount)
        return jsonify({"message": f"Transakcja zostanie dodana do bloku {index}"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

#pow zarabianie
@app.post("/mine")
def mine():
    block = blockchain.mine(node_identifier)
    return jsonify({
        "message": "Wydobyto nowy blok",
        "block": block,
        "hash": blockchain.hash(block),
    }), 200

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", default=5000, type=int)
    args = parser.parse_args()
    print(f"Adres sendera: {node_identifier}")
    app.run(host="127.0.0.1", port=args.port)
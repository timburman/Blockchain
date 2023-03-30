# Building the blockchain, Importing flask, hashlib, timedate, json
"""
1. Datetime helps us to know when the block was mined and it also helps us in completeing the POW
2. Requests helps us to call the flask functions within the cli and collect the JSON data and use it for various purposes
3. Urlparse helps us to devide the url into different parts like 'http','google.com','port:2000',etc.
4. Flask makes the webapp backend applications like the server end of the website, in this we are using it to call the functions in the blockchain

"""


from crypt import methods
from sqlite3 import Timestamp
from urllib import response
from flask import jsonify, Flask, request
import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urllib.parse import urlparse

# This part we will Build block chain.

class Blockchain:

    def __init__(self):
        self.chain = [];
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()


    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'transactions': self.transactions,
                'previous_hash': previous_hash,}
        
        self.transactions = []
        self.chain.append(block)
        return block


    def get_previous_block(self):
        return self.chain[-1]

    
    def pow(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof == False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            
            else:
                new_proof += 1
        
        return new_proof

    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    

    def chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            new_proof = block['proof']
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1

        return True


    def addtransactions(self, sender, receiver, amount):
        self.transactions.append({'Sender': sender,
                                'Receiver': receiver,
                                'Amount': amount})
        
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1;


    def addnode(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for nodes in network:
            response = requests.get(f'http://{nodes}/chain_display')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                
        if longest_chain:
            self.chain = longest_chain
            return True
                
        return False
# Webapp using Flask

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a address for the nodes ":5000"

node_address = str(uuid4()).replace('-','')

# Creating a Blockchain

blockchain = Blockchain()

#mining a Block
@app.route('/mine_block', methods = ["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.pow(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    blockchain.addtransactions(sender = node_address, receiver = 'timberman', amount = 1)
    response = {'message': 'One blockmined, the block is added to the chain.',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200



# Get blockchain displayed on postman
@app.route('/chain_display', methods = ["GET"])
def chain_display():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200

# Check the validity of the Blockchain
@app.route('/is_valid', methods = ["GET"])
def is_valid():
    valid = blockchain.chain_valid(blockchain.chain)

    if valid:
        response = {'message': 'The chain is valid'}
    else:
        response = {'messgae: The chain is not valid'}
        replace_chain()
    
    return response , 200

# Adding the transaction to the blockchain
@app.route('/add_transactions', methods = ["POST"])
def add_transaction():
    json_file = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json_file for key in transaction_keys):
        return "Some elements of the transactions is missing", 400
    
    index = blockchain.addtransactions(json_file['sender'],json_file['receiver'],json_file['amount'])
    response = {'message': f'Transaction is added Block{index}'}
    return jsonify(response), 201

# Decentralizing the blockchain
@app.route('/connect_node', methods = ["POST"])
def connect_node():
    json_file = request.get_json()
    nodes = json_file.get('nodes')

    if nodes is None:
        return "The json file is empty", 400
    
    for node in nodes:
        blockchain.addnode(node)
    
    response = {'message': 'All the nodes are connected, The list of nodes are:',
                'total_nodes': list(blockchain.nodes)}
    
    return response, 201


# Replace the chains with the longest chains
@app.route('/replace_chain', methods = ["GET"])
def replace_chain():
    chain_replaced = blockchain.replace_chain()

    if chain_replaced:
        response = {'message': 'The node had different chains, then the chain is replaced',
                    'new chain': blockchain.chain()}
    else:
        response = {'message ':'the chain is the largest one',
                    'actual chain': blockchain.chain()}
    
    return response , 200
    

# Running the app
app.run(host= '127.0.0.1', port=5001)   

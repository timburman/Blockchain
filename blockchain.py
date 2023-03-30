# Building the blockchain, Importing flask, hashlib, timedate, json

from crypt import methods
from sqlite3 import Timestamp
from urllib import response
from flask import jsonify, Flask
import datetime
import hashlib
import json

# This part we will Build block chain.

class Blockchain:

    def __init__(self):
        self.chain = [];
        self.create_block(proof = 1, previous_hash = '0')


    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                'timestamp': str(datetime.datetime.now()),
                'proof': proof,
                'previous_hash': previous_hash,}
        
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



# Webapp using Flask

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    response = {'message': 'One blockmined, the block is added to the chain.',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    
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
    
    return response , 200



# Running the app
app.run(host= '127.0.0.1', port=5000)   

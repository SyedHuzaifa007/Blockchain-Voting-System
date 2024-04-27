from flask import Flask, render_template, request
from web3 import Web3
import json

app = Flask(__name__)

# Connect to Ethereum node
web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

# Load contract ABI
with open('Voting.json') as f:
    contract_abi = json.load(f)['abi']

# Contract address
contract_address = "0x123456789..."  # Replace with actual contract address

# Contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    candidate_id = request.form['candidate_id']
    # Call smart contract function to cast vote
    contract.functions.vote(candidate_id).transact({'from': web3.eth.accounts[0]})
    return "Vote cast successfully!"

if __name__ == '__main__':
    app.run(debug=True)

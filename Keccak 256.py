import binascii
from Crypto.Hash import keccak

previous_proof = 1
proof = 1
check_proof = False

while check_proof == False:
    hash_operation = keccak.new(data = str(proof**2 - previous_proof**2).encode(), digest_bits=256).hexdigest()
    print(hash_operation)
    if hash_operation[:4] == '0000':
        check_proof = True
            
    else:
        proof += 1

print(hash_operation)
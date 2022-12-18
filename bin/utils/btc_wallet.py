#!/usr/bin/env python3

import binascii
import hashlib

import base58
import ecdsa


ecdsaPrivateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
print(f"ECDSA Private Key: {ecdsaPrivateKey.to_string().hex()}")

ecdsaPublicKey = f"04{ecdsaPrivateKey.get_verifying_key().to_string().hex()}"
print(f"ECDSA Public Key: {ecdsaPublicKey}")

hash256FromECDSAPublicKey = hashlib.sha256(binascii.unhexlify(ecdsaPublicKey)).hexdigest()
print(f"SHA256(ECDSA Public Key): {hash256FromECDSAPublicKey}")

ripemd160FromHash256 = hashlib.new("ripemd160", binascii.unhexlify(hash256FromECDSAPublicKey))
print(f"RIPEMD160(SHA256(ECDSA Public Key)): {ripemd160FromHash256.hexdigest()}")

perpendNetworkByte = f"00{ripemd160FromHash256.hexdigest()}"
print(f"Prepend Network Byte to RIPEMD160(SHA256(ECDSA Public Key)): {perpendNetworkByte}")

_hash = perpendNetworkByte
for i in range(1,3):
    _hash = hashlib.sha256(binascii.unhexlify(_hash)).hexdigest()
    print(f"\t|____>SHA256 # {i} : {_hash}")
print(f"Checksum(first 4 bytes: {_hash[:8]}")
print(f"Append Checksum to RIPEMD160(SHA256(ECDSA Public Key)): {perpendNetworkByte + _hash[:8]}")

bitcoinAddress = base58.b58encode(binascii.unhexlify(perpendNetworkByte + _hash[:8]))
print(f"Bitcoin Public Address: {bitcoinAddress.decode('utf8')}")

### CONVERT FORMAT WIF "Wallet import format"
private_key_hex = '80' + ecdsaPrivateKey.to_string().hex()
first_sha256 = hashlib.sha256(binascii.unhexlify(private_key_hex)).hexdigest()
second_sha256 = hashlib.sha256(binascii.unhexlify(first_sha256)).hexdigest()
print(f"Private Key WIF: {base58.b58encode(binascii.unhexlify(private_key_hex + second_sha256)).decode('utf8')}")

# Adapt to Litecoin
# https://github.com/weex/addrgen/blob/master/addrgen.py
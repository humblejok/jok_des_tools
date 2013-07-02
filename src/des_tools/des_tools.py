'''
Created on Jul 2, 2013

@author: sdejonckheere

pyDes must be installed (pip install pydes)
'''
from pyDes import des, PAD_NORMAL, CBC
import binary
from binary import ror, set_odd_parity
import codecs

#
# Generate the CBC checksum.
# It has no use by itself: it is part of a key conversion process.
#
def des_cbc_checksum(str_key, bytes_key, bytes_IV):
    padded_data = bytearray(((len(str_key)+7)/ 8)*8)
    for index in range(0,len(str_key)):
        padded_data[index] = str_key[index]
    # CBC encryption of the key
    cypher = des(str(bytes_key),CBC,str(bytes_IV), pad=None, padmode=PAD_NORMAL)
    key = cypher.encrypt(str_key)
    key = binary.to_bytes(key)
    
    checksum = bytearray(8)
    start_at = len(key) - 8
    for index in range(0,8):
        checksum[index] = key[start_at + index]
    return checksum

#
# Convert a DES string key as 2 effective bytes arrays (simple case: 8 bytes key)
# Inspired from: http://web.mit.edu/macdev/Development/MITKerberos/MITKerberosLib/DESLib/Documentation/api.html
# TODO: May not be Pythonic enough as it is a straightforward adaptation of Java code
# TODO: Has to be tested
#
def des_string_to_2keys(str_key):
    key1 = bytearray(8)
    key2 = bytearray(8)
    for index in range(0,len(str_key)):
        # This is not mandatory as Python seems to handle unsigned bytes by default
        b_val = ord(str_key[index]) & 0xff
        # Doing some bit shifting, please refer to the URL above
        if (index % 32) < 16:
            if (index % 16) < 8:
                key1[index % 8] ^= (b_val<<1)
            else:
                key2[index % 8] ^= (b_val<<1)
        else:
            b_val = ((b_val << 4) & 0xf0) | (ror(b_val,4) & 0x0f)
            b_val = ((b_val << 2) & 0xcc) | (ror(b_val,2) & 0x33)
            b_val = ((b_val << 1) & 0xaa) | (ror(b_val,1) & 0x55)
            if (index % 16) < 8:
                key1[7-(index % 8)] ^= b_val
            else:
                key2[7-(index % 8)] ^= b_val
        if len(str_key)<=8:
            for index in range(0,8):
                key2[index] = key1[index]
        # Getting odd parity
        key1 = set_odd_parity(key1)
        # Computing CBC checksum (generating key)
        key1 = des_cbc_checksum(str_key, key1, key1)
        # Getting odd parity
        key1 = set_odd_parity(key1)
        
        # Getting odd parity
        key2 = set_odd_parity(key2)
        # Computing CBC checksum (generating key)
        key2 = des_cbc_checksum(str_key, key2, key2)
        # Getting odd parity
        key2 = set_odd_parity(key2)
        
        return key1.extend(key2).extend(key1)
        
#
# Convert a DES string key as a bytes array
# Inspired from: http://web.mit.edu/macdev/Development/MITKerberos/MITKerberosLib/DESLib/Documentation/api.html
# TODO: May not be Pythonic enough as it is a straightforward adaptation of Java code
#
def des_string_to_key(str_key):
    # Result variable
    key = bytearray(8)
    # Doing some bit shifting, please refer to the URL above
    for index in range(0,len(str_key)):
        # This is not mandatory as Python seems to handle unsigned bytes by default
        b_val = ord(str_key[index]) & 0xff
        if (index % 16) < 8:
            key[index % 8] = key[index % 8] ^ (b_val<<1)
        else:
            b_val = ((b_val << 4) & 0xf0) | (ror(b_val,4) & 0x0f)
            b_val = ((b_val << 2) & 0xcc) | (ror(b_val,2) & 0x33)
            b_val = ((b_val << 1) & 0xaa) | (ror(b_val,1) & 0x55)
            key[7- (index % 8)] ^= b_val;
        index = index + 1
    # Getting odd parity
    key = set_odd_parity(key)
    # Computing CBC checksum (generating key)
    key = des_cbc_checksum(str_key, key, key)
    # Getting odd parity
    key = set_odd_parity(key)
    return key


#
# Sample example: Bloomberg FTP (Data License) file decipher
#
BLOOMBERG_PADDING = "\0\0\0\0\0\0\0\0"

def decipher_bloomberg_file(key_as_str, in_filename, out_filename):
    # Instanciate the DES decryptor
    decrypt = des(str(des_string_to_key(key_as_str)),CBC,BLOOMBERG_PADDING, pad=None, padmode=PAD_NORMAL)
    in_file = open(in_filename,'rb')
    uubuffer = in_file.read()
    in_file.close()
    out_file = open(out_filename,'wb')
    uudecode = codecs.getdecoder('uu')
    payload, size = uudecode(uubuffer)
    out_file.write(decrypt.decrypt(payload))
    out_file.close()
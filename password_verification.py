"""
Slightly modified from source: https://www.vitoshacademy.com/hashing-passwords-in-python/
"""
import hashlib, binascii, os
 
def hash_pw(plaintext_password):
    """ Hash a password for storing. """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac(
        'sha512', 
        plaintext_password.encode('utf-8'),
        salt, 100000
    )
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def check_pw(hashed_password, plaintext_password):
    """ Verify a hashed password against the plaintext one."""
    salt = hashed_password[:64]
    hashed_password = hashed_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        'sha512', 
        plaintext_password.encode('utf-8'), 
        salt.encode('ascii'), 
        100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == hashed_password


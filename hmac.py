import hmac
import hashlib
from sound import tonality

if __name__=="__main__":
    secret=tonality()
    secret = str(secret)

    # Encode secret 
    byte_secret = secret.encode('utf-8')

    # Create the HMAC object and get the hexadecimal digest
    h = hashlib.new('sha256')
    h.update(byte_secret)
    signature = h.hexdigest()

    print(f"Digest is: {signature}")

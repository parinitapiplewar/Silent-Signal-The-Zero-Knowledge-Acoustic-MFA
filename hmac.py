import hmac
import sound


message=sound.tonality()
secret_key = "the secret key"
message = str(message)

# Encode key and message to bytes
byte_key = secret_key.encode('utf-8')
byte_message = message.encode('utf-8')

# Create the HMAC object and get the hexadecimal digest
h = hmac.new(byte_key, byte_message, hmac.hashlib.sha256)
signature = h.hexdigest()

print(f"HMAC signature: {signature}")


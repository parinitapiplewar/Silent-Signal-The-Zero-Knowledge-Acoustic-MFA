import hmac
import hashlib

SECRET_KEY=b"silent_signal_key"

def generate_hmac(challenge):
    return hmac.new(SECRET_KEY,str(challenge).encode(),hashlib.sha256).hexdigest()
def verify_hmac(challenge,reveived):
    expected=generate_hmac(challenge)
    return hmac.compare_digest(expected,reveived)

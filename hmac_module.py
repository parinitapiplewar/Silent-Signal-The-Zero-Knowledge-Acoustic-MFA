import hmac
import hashlib

SECRET_KEY=b"vibe_signal_key"

def generate_hmac(challenge):
    """
    hmac generator """
    return hmac.new(SECRET_KEY,str(challenge).encode(),hashlib.sha256).hexdigest()
def verify_hmac(challenge,reveived):
    """
    hmac verifier function """
    expected=generate_hmac(challenge)
    return hmac.compare_digest(expected,reveived)

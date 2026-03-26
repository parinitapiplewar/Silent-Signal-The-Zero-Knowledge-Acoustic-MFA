import hmac, hashlib

KEY = b"ultra_secret"

def generate(challenge):
    return hmac.new(KEY, challenge.encode(), hashlib.sha256).hexdigest()[:8]

def verify(challenge, response):
    expected = generate(challenge)
    match = sum(a == b for a, b in zip(expected, response)) / len(expected)
    return match > 0.75
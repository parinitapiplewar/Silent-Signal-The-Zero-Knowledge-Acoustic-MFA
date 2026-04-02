import secrets

def generate_challenge():
    return secrets.token_urlsafe(8)

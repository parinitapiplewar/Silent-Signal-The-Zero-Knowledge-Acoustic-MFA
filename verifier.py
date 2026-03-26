from tx import send
from rx import receive
from crypto import verify
import secrets, time

challenge = secrets.token_urlsafe(6)

print("[VERIFIER] Challenge:", challenge)

time.sleep(2)
send(challenge)

time.sleep(3)
response = receive()

if response and verify(challenge, response):
    print("AUTHENTICATED")
else:
    print("REJECTED")
from rx import receive
from tx import send
from crypto import generate
import time

print("[RESPONDER] Waiting...")

challenge = receive()

if challenge:
    response = generate(challenge)
    print("[RESPONDER] Response:", response)

    time.sleep(1)
    send(response)
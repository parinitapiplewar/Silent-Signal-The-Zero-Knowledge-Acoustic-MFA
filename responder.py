from detector import receive_signal
from sound import send_signal
from hmac_module import generate_hmac
import time

print("\n[RESPONDER] Waiting for challenge...")

# Step 1: receive challenge
challenge = receive_signal()

if challenge:
    challenge = challenge.strip()

print(f"[RESPONDER] Challenge received: {challenge}")

# Step 2: compute response
response_full = generate_hmac(challenge)
response = response_full[:8]   # truncate for reliability

print(f"[RESPONDER] Sending response: {response}")

time.sleep(1)

# Step 3: send response
send_signal(response)
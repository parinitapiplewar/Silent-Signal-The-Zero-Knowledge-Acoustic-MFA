from sound import send_signal
from detector import receive_signal
from hmac_module import verify_hmac
from challenge import generate_challenge
import time

print("\n[VERIFIER] Starting system...")

# Step 1: generate challenge
challenge = generate_challenge()
print(f"[VERIFIER] Challenge: {challenge}")

time.sleep(1)

# Step 2: send challenge
print("[VERIFIER] Sending challenge...")
send_signal(challenge)

time.sleep(1)

# Step 3: receive response
print("[VERIFIER] Waiting for response...")
received = receive_signal()

if received:
    received = received.strip()

print(f"[VERIFIER] Received: {received}")

# Step 4: verify
print("[VERIFIER] Verifying...")

if verify_hmac(challenge, received):
    print("\n AUTHENTICATED")
else:
    print("\n REJECTED")
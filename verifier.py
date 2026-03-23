from sound import send_signal
from detector import receive_signal
from hmac_module import verify_hmac
from challenge import generate_challenge
import time

print("[VERIFIER] Generating challenge...")
challenge = generate_challenge()

print(f"[VERIFIER] Challenge: {challenge}")

# Step 1: send challenge
print("[VERIFIER] Sending challenge...")
send_signal(challenge)

time.sleep(1)

# Step 2: receive response
print("[VERIFIER] Waiting for response...")
received = receive_signal()

# Step 3: verify
print("[VERIFIER] Verifying...")

if verify_hmac(challenge, received):
    print("AUTHENTICATED")
else:
    print("REJECTED")
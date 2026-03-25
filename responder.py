from detector import receive_signal
from sound import send_signal
from hmac_module import generate_hmac
import time

print("[RESPONDER] Waiting for challenge...")

#Step 1: Receive challenge
challenge=receive_signal()
print(f"[RESPONDER] Received challenge: {challenge}")

#Step 2: calculate response
response=generate_hmac(challenge)[:8]
print("[RESPONDER] Sending response...")

time.sleep(1)


#Step 3: send response
send_signal(response)
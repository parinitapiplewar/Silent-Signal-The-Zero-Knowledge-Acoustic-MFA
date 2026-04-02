from sound import send_signal, encode_data
from detector import receive_signal
from hmac_module import verify_hmac
from challenge import generate_challenge
import time

def run_verifier():
    print("[VERIFIER] Verifier started")
    print("[VERIFIER] Generating challenge...")
    challenge = generate_challenge()
    
    # Step 1: send challenge
    print("Challenge sent")
    send_signal(challenge)
    
    time.sleep(1)
    
    # Step 2: receive response
    print("[VERIFIER] Waiting for response...")
    received, _, _, _ = receive_signal(duration=60)
    
    if not received:
        print("[VERIFIER] Timeout or signal not detected")
        print("Verification failure")
        return {"status": "failed", "challenge": challenge, "binary_sent": encode_data(challenge)}
        
    received=received.strip()
    print("Response received")
    
    # Step 3: verify
    print("[VERIFIER] Verifying...")
    
    if verify_hmac(challenge, received):
        print("Verification success")
        return {"status": "success", "challenge": challenge, "binary_sent": encode_data(challenge)}
    else:
        print("Verification failure")
        return {"status": "failed", "challenge": challenge, "binary_sent": encode_data(challenge)}
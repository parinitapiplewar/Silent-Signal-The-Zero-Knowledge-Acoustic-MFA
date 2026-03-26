from detector import receive_signal
from sound import send_signal, encode_data
from hmac_module import generate_hmac
import time

def run_responder():
    print("[RESPONDER] Responder started")
    print("[RESPONDER] Waiting for challenge...")

    #Step 1: Receive challenge
    challenge=receive_signal(duration=3)
    if not challenge:
        print("[RESPONDER] Timeout/No signal")
        print("Verification failure")
        return {"status": "failed", "received_binary": "", "decoded_challenge": "", "hmac": ""}
        
    print(f"[RESPONDER] Received challenge: {challenge}")

    #Step 2: calculate response
    try:
        response=generate_hmac(challenge)[:8]
    except Exception as e:
        print(f"[RESPONDER] Error generating HMAC: {e}")
        print("Verification failure")
        return {"status": "failed", "received_binary": encode_data(challenge), "decoded_challenge": challenge, "hmac": ""}
        
    print("[RESPONDER] Sending response...")

    time.sleep(1)

    #Step 3: send response
    send_signal(response)
    print("Response sent")
    print("Verification success")
    return {"status": "success", "received_binary": encode_data(challenge), "decoded_challenge": challenge, "hmac": response}
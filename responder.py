from detector import receive_signal
from sound import send_signal
from hmac_module import generate_hmac
import time

def run_responder():
    print("[RESPONDER] Responder started")
    print("[RESPONDER] Listening for signal...")

    #Step 1: Receive challenge
    challenge, received_binary, detected_freqs, detected_bits = receive_signal(duration=60)
    
    if not challenge or len(challenge.strip()) == 0:
        print("[RESPONDER] Timeout/No signal")
        print("Verification failure")
        return {
            "status": "failed", 
            "received_binary": received_binary if received_binary else "None", 
            "decoded_challenge": challenge if challenge else "None", 
            "hmac": "None",
            "detected_freqs": detected_freqs,
            "detected_bits": detected_bits
        }
        
    print("[RESPONDER] Signal detected")
    print(f"[RESPONDER] Binary reconstructed: {received_binary}")
    print(f"[RESPONDER] Decoded challenge: {challenge}")

    #Step 2: calculate response
    try:
        response=generate_hmac(challenge)[:8]
        print("[RESPONDER] HMAC generated")
    except Exception as e:
        print(f"[RESPONDER] Error generating HMAC: {e}")
        print("Verification failure")
        return {
            "status": "failed", 
            "received_binary": received_binary, 
            "decoded_challenge": challenge, 
            "hmac": "None",
            "detected_freqs": detected_freqs,
            "detected_bits": detected_bits
        }
        
    print("[RESPONDER] Sending response...")

    time.sleep(1)

    #Step 3: send response
    send_signal(response)
    print("Response sent")
    print("Verification success")
    return {
        "status": "success", 
        "received_binary": received_binary, 
        "decoded_challenge": challenge, 
        "hmac": response,
        "detected_freqs": detected_freqs,
        "detected_bits": detected_bits
    }
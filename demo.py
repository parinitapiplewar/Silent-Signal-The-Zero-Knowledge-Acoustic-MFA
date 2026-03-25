from sound import send_signal
from detector import receive_signal
from hmac_module import generate_hmac, verify_hmac
from challenge import generate_challenge
import time

def demo():
    print("\n==============================")
    print("   SILENT SIGNAL DEMO SYSTEM  ")
    print("==============================\n")

    # Step 1: Generate Challenge
    print("[STEP 1] Generating Challenge...")
    challenge = generate_challenge()
    print(f"[INFO] Challenge: {challenge}")

    time.sleep(1)

    # Step 2: Generate Response (Simulated responder)
    print("\n[STEP 2] Computing Secure Response (HMAC)...")
    
    # IMPORTANT: shorten for stability
    full_hmac = generate_hmac(challenge)
    response = full_hmac[:8]   # send only first 8 chars

    print(f"[INFO] HMAC (truncated): {response}")

    time.sleep(1)

    # Step 3: Send Signal
    print("\n[STEP 3] Transmitting via Ultrasonic Channel...")
    send_signal(response)

    
    # Step 4: Receive Signal
    print("\n[STEP 4] Receiving Signal...")
    received = receive_signal()

    if received:
        received = received.strip()

    print(f"[INFO] Received: {received}")

    # Step 5: Verification
    print("\n[STEP 5] Verifying Authentication...")

    expected = response  # since we truncated
    print(f"[DEBUG] Expected: {expected}")

    if received == expected:
        print("\n✅ AUTHENTICATION SUCCESSFUL")
    else:
        print("\n❌ AUTHENTICATION FAILED")

    print("\n==============================\n")


if __name__ == "__main__":
    demo()
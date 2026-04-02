from flask import Flask, render_template, jsonify, request
# from verifier import run_verifier  # Stop using verifier.py audio logic
# from responder import run_responder # Stop using responder.py audio logic
from challenge import generate_challenge
from hmac_module import verify_hmac
import threading
import uuid
import time

app = Flask(__name__)

# Dictionary to store async job status
# job_id -> {status, challenge, email, start_time}
jobs = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/verifier')
def index():
    return render_template('index.html')

@app.route('/responder')
def mobile():
    return render_template('mobile_interface.html')

@app.route('/start_verification', methods=['POST'])
def start_verification():
    # PC verifier calls this
    data = request.json
    email = data.get('email', 'unknown')
    print(f"Verification started for {email}")
    
    job_id = str(uuid.uuid4())
    challenge = generate_challenge()
    
    # Initialize job state
    jobs[job_id] = {
        "status": "running",
        "challenge": challenge,
        "email": email,
        "start_time": time.time()
    }
    
    # Return challenge to PC so it can play the sound
    return jsonify({
        "job_id": job_id,
        "challenge": challenge
    })

@app.route('/mobile_verify', methods=['POST'])
def mobile_verify():
    # Mobile phone calls this after hearing and decoding the sound
    data = request.json
    email = data.get('email')
    received_hmac = data.get('hmac')
    
    if not email or not received_hmac:
        return jsonify({"status": "error", "message": "Missing email or HMAC"}), 400

    print(f"Mobile verification received for {email}")
    
    # Find the active job for this email
    target_job_id = None
    for jid, job in jobs.items():
        if job.get('email') == email and job.get('status') == 'running':
            target_job_id = jid
            break
            
    if not target_job_id:
        return jsonify({"status": "error", "message": "No active job found for email"}), 404
        
    challenge = jobs[target_job_id]['challenge']
    
    # Server-side HMAC verification
    if verify_hmac(challenge, received_hmac):
        jobs[target_job_id]['status'] = 'success'
        jobs[target_job_id]['hmac_verified'] = True
        print(f"Verification SUCCESS for {email}")
        return jsonify({"status": "success"})
    else:
        jobs[target_job_id]['status'] = 'failed'
        print(f"Verification FAILED (HMAC mismatch) for {email}")
        return jsonify({"status": "failed", "message": "HMAC mismatch"})

@app.route('/mobile_verify_start', methods=['POST'])
def mobile_verify_start():
    # This was previously used to start run_responder(). 
    # Now mobile starts its own listener in JS.
    # Just return success.
    return jsonify({"status": "ready"})

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"status": "error", "result": "not found"})
    
    # Provide necessary fields for PC UI to show progress/result
    response = {
        "status": job['status'],
        "challenge": job['challenge'],
        "binary_sent": "".join(format(ord(c), '08b') for c in job['challenge'])
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

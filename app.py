from flask import Flask, render_template, jsonify, request
from verifier import run_verifier
from responder import run_responder
import threading
import uuid
import time

app = Flask(__name__)

# Dictionary to store async job status
jobs = {}

def async_task(job_id, func):
    try:
        result = func()
        if isinstance(result, dict):
            jobs[job_id] = result
        else:
            jobs[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": "error", "result": str(e)}

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
    print("Verification started")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running"}
    
    # Execute immediately in a non-blocking thread without calling .join()
    t = threading.Thread(target=async_task, args=(job_id, run_verifier))
    t.start()
    
    return jsonify({"job_id": job_id})

@app.route('/mobile_verify_start', methods=['POST'])
def mobile_verify_start():
    print("Responder verification started")
    
    # Execute synchronously to guarantee the responder has completed processing
    result = run_responder()
    
    if isinstance(result, dict):
        return jsonify(result)
    else:
        return jsonify({"status": result})

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"status": "error", "result": "not found"})
    return jsonify(job)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

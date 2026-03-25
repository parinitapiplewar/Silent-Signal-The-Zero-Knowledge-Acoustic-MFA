from flask import Flask, render_template, jsonify, request
from verifier import run_verifier

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_verification', methods=['POST'])
def start_verification():
    print("Verification started")
    result = run_verifier()
    return jsonify({"status": result})

if __name__ == '__main__':
    app.run(debug=True)

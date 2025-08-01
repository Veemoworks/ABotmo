from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify(status="ok"), 200

def run_flask():
    app.run(host='0.0.0.0', port=8004)
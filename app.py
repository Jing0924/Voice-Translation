from flask import Flask, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        # 执行real-time-translate.py脚本
        result = subprocess.run(['python3', 'real-time-translate.py'], capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        output = str(e)
    return jsonify(output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
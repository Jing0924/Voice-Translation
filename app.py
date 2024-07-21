from flask import Flask, jsonify, request, send_from_directory
import subprocess

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        data = request.get_json()  # 獲取請求中的JSON數據
        language = data.get('language')  # 獲取選擇的語言

        # 根據選擇的語言執行不同的腳本
        if language == 'all':
            result = subprocess.run(['python3', 'real-time-translate-all.py'], capture_output=True, text=True)
        elif language == 'en':
            result = subprocess.run(['python3', 'real-time-translate-en.py'], capture_output=True, text=True)
        elif language == 'ja':
            result = subprocess.run(['python3', 'real-time-translate-ja.py'], capture_output=True, text=True)
        elif language == 'ko':
            result = subprocess.run(['python3', 'real-time-translate-ko.py'], capture_output=True, text=True)
        output = result.stdout
    except Exception as e:
        output = str(e)
    
    return jsonify(output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

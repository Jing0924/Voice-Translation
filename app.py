from flask import Flask, jsonify, send_from_directory  # 匯入 Flask 框架，jsonify 和 send_from_directory 函數
import subprocess                                     # 匯入 subprocess 模組，用於執行子進程
import os                                             # 匯入操作系統模組

app = Flask(__name__)                                 # 創建 Flask 應用實例

@app.route('/')                                       # 設置根路由
def serve_index():
    return send_from_directory('static', 'index.html') # 返回靜態文件夾中的 index.html 文件

@app.route('/run-script', methods=['POST'])           # 設置 /run-script 路由，接受 POST 請求
def run_script():
    try:
        # 執行 real-time-translate.py 腳本
        result = subprocess.run(['python3', 'real-time-translate.py'], capture_output=True, text=True) # 執行腳本並捕獲輸出
        output = result.stdout                          # 獲取腳本的標準輸出
    except Exception as e:                              # 捕獲異常
        output = str(e)                                 # 將異常轉換為字符串
    return jsonify(output=output)                       # 將輸出以 JSON 格式返回

if __name__ == '__main__':                              # 檢查是否以主程序運行
    app.run(debug=True, port=5001)                      # 啟動 Flask 應用，啟用 debug 模式，設置埠號為 5001
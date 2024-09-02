from flask import Flask, jsonify, request

app = Flask(__name__)

# 測試 API：回應一個簡單的 JSON 物件
@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

# 取得數據的 API
@app.route('/api/data', methods=['GET'])
def get_data():
    sample_data = {
        "name": "ChatGPT",
        "type": "AI",
        "language": "Python"
    }
    return jsonify(sample_data)

# 接收 POST 請求的 API
@app.route('/api/post', methods=['POST'])
def post_data():
    data = request.json  # 取得 POST 請求中的 JSON 數據
    return jsonify({"received_data": data})

if __name__ == '__main__':
    app.run(debug=True)

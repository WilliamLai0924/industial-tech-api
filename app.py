import os

from flask import Flask, jsonify, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)

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

# Line Bot API 與 Webhook Handler 設置
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # 確認請求來自 LINE
    signature = request.headers['X-Line-Signature']

    # 獲取請求主體
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))  # 回覆相同的訊息

if __name__ == '__main__':
    app.run()

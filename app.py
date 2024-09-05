import os
import io
import evalue_plan

from flask import Flask, abort, jsonify, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FileMessage

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

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_id = event.message.id
    file_name = event.message.file_name

    if file_name.endswith('.xlsx'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='收到! 正在幫您整理~'))
        
         # 取得文件內容
        message_content = line_bot_api.get_message_content(message_id)
        file_bytes = io.BytesIO(message_content.content)
        
        try:
            data = evalue_plan.get_excel_data(file_bytes)
            filter_df = evalue_plan.filter_valid_data(data)
            dates = evalue_plan.get_dateTimes(filter_df)
            if len(dates) > 0:
                for date in dates:
                    date = str(date).split(' ')[0]
                    reply = f"{date}："
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
                    # 回傳處理後的數據
                    plans_dict = evalue_plan.get_sameday_plan(filter_df, date)
                    for k, v in plans_dict.items():
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=k + ":"))
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=v))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="尚未安排未來行程!請在確認文件內容!"))

        except Exception as e:
            reply = f"讀取 Excel 文件時發生錯誤：{str(e)}"
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    else:
        reply = "請上傳 .xlsx 檔案格式的文件。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == '__main__':
    app.run()

import os
import io
import evalue_plan
import requests
import json
import pandas as pd

from datetime import datetime
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
        TextSendMessage(text= event.message.text))  # 回覆相同的訊息

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_id = event.message.id
    file_name = event.message.file_name
    if file_name.endswith('.xlsx'):
         # 取得文件內容
        message_content = line_bot_api.get_message_content(message_id)
        file_bytes = io.BytesIO(message_content.content) 
        try:            
            messages = []
            data = evalue_plan.get_excel_data(file_bytes)
            messages.append(str(len(data)))
            filter_df = evalue_plan.filter_valid_data(data)   
            dates = evalue_plan.get_dateTimes(filter_df)
            if len(dates) > 0:
                # messages.append(len(data))
                # messages.append(data)
                # 將 DataFrame 中的 Timestamp 列轉換為字符串格式
                # dates['日期'] = dates['日期'].apply(lambda x: x.strftime('%Y-%m-%d'))
                # date_df = date_df.where(pd.notnull(date_df), None)
                # date_df = date_df.applymap(lambda x: None if pd.isna(x) else x)
                # data = {
                #     'EvalueList':date_df.values.tolist(),
                #     'Date':datetime.now().strftime("%Y-%m-%d")
                # }
                # json_data = json.dumps(data, ensure_ascii=False)
                # # 設置請求標頭
                # headers = {
                #     "Content-Type": "application/json"
                # }
                # # 發送 POST 請求
                # plan = requests.post('http://yuapp.runasp.net/api/PlanArrange', headers=headers, data=json_data)
                
                # for iplan in plan:
                #     messages.append(iplan)
                for date in dates:
                    date = str(date).split(' ')[0]

                    date_df = filter_df[filter_df['日期'] == date]
                    # line_bot_api.push_message(
                    #     event.source.user_id,  # 使用者的 LINE user ID
                    #     [
                    #         TextSendMessage(text="這是第 6 則訊息"),
                    #         TextSendMessage(text="這是第 7 則訊息"),
                    #         TextSendMessage(text=str(date_df['日期']))
                    #     ]
                    # )

                    # # 將 DataFrame 中的 Timestamp 列轉換為字符串格式
                    # date_df['日期'] = date_df['日期'].apply(lambda x: x.strftime('%Y-%m-%d'))
                    date_df = date_df.where(pd.notnull(date_df), None)
                    date_df = date_df.applymap(lambda x: None if pd.isna(x) else x)
                    data = {
                        'EvalueList':date_df.values.tolist(),
                    }
                    json_data = json.dumps(data, ensure_ascii=False)

                    line_bot_api.push_message(
                            event.source.user_id,
                            [
                                TextSendMessage(text=json_data)
                            ]
                    )

                    # 設置請求標頭
                    headers = {
                        "Content-Type": "application/json"
                    }
                    # 發送 POST 請求
                    plan = requests.post('http://yuapp.runasp.net/api/PlanArrange', headers=headers, data=json_data)
                    
                    for iplan in plan:
                        line_bot_api.push_message(
                            event.source.user_id,
                            [
                                TextSendMessage(text=iplan)
                            ]
                        )
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="尚未安排未來行程!請在確認文件內容!"))

        except Exception as e:
            # reply = "讀取 Excel 文件時發生錯誤：" + str(e)
            # messages.append(reply)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(e)))

    else:
        reply = "請上傳 .xlsx 檔案格式的文件。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == '__main__':
    app.run(debug=True)

import pandas as pd
from datetime import datetime

def get_excel_data(file_bytes):
    try:
        df = pd.read_excel(file_bytes, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"讀取 Excel 文件時發生錯誤：{str(e)}")
    
    result = df.copy()
    return result

def filter_valid_data(data : pd.DataFrame):
   return data[data['人員一'].notnull() &
                data['人員二'].notnull() &
                data['日期'].notnull()  &
                data['時間'].notnull()  &
                data['電話'].notnull()  &
                (data['聯絡情形'].notnull() | data['聯絡人'].notnull() ) &
                data['雇主名稱'].notnull() &
                data['郵遞區號'].notnull() &
                data['地址'].notnull() &
                (data['印尼'].notnull()  | data['泰國'].notnull()  | data['越南'].notnull() | data['菲律賓'].notnull()) &
                (data['通譯一'].notnull()  | data['通譯二'].notnull() | data['通譯三'].notnull())]

def get_sameday_plan(data: pd.DataFrame, dateTime):
    result = {}
    names = data['人員二'].unique()
    ec = 0
    for name in names:
        employee={}
        try:
            employee = data[data['人員二'] == name]
            employee.loc[:, '時間2'] = employee['時間'].apply(extract_start_time)
            times = employee.sort_values(by='時間')['時間'].unique()
            ec += 1
            contens = []
            placeCount = 1
            for time in times:
                titles = []
                contacts = []
                forContents = []
                translators = []
                places = employee[employee['時間'] == time]
                ec += 1
                for i, place in places.iterrows():
                    foreigners = []
                    translatorContent = ""
                    titles.append(f'第{placeCount}間')
                    placeCount += 1
                    # if place['印尼'] > 0:
                    #     foreigners.append('印尼出席人數'+ str(int(place['印尼'])) +'位')
                    #     ec += 1
                    # if place['泰國'] > 0:
                    #     foreigners.append('泰國出席人數'+ str(int(place['泰國'])) +'位')
                    #     ec += 1
                    # if place['越南'] > 0:
                    #     foreigners.append('越南出席人數'+ str(int(place['越南'])) +'位')
                    #     ec += 1
                    # if place['菲律賓'] > 0:
                    #     foreigners.append('菲律賓出席人數'+ str(int(place['菲律賓'])) +'位')
                    #     ec += 1
                    # if pd.isna(place['通譯一']) == False:
                    #     translatorContent += place['通譯一']
                    #     ec += 1
                    # if pd.isna(place['通譯二']) == False :
                    #     translatorContent += ', '+ (place['通譯二'])
                    #     ec += 1
                    # if pd.isna(place['通譯三']) == False:
                    #     translatorContent += ', '+ (place['通譯三'])
                    #     ec += 1
                    translators.append(translatorContent)
                    forContents.append(place['雇主名稱'] + ':\n' + "/".join(foreigners))
                    contacts.append(place['聯絡人'] if len(place) == 1 else  place['雇主名稱'] + "-" + place['聯絡人'])
                ec += 1
                tap = "" if len(places) == 1 else '*宣導可以多間公司同時進行，但拍照請雇主及外國人分開拍攝，如方便可採不同背景做拍攝，感謝~~~'
                ec += 1
                content = '輔導人員:'+ "/".join(set(s['人員一'] for i, s in places.iterrows())) +'\n'+ '工作人員:'+ "/".join(set(s['人員二'] for i, s in places.iterrows())) +'\n'+ "及".join(titles)+':'+time +'\n'+"/".join(set(s['電話'] for i, s in places.iterrows()))+'\n'+"/".join(set(f"{s['雇主名稱']}\n{s['郵遞區號']}{s['地址']}\n(https://www.google.com/maps/search/?api=1&query={s['雇主名稱']})" for i, s in places.iterrows()))+'\n'+"\n".join(set(forContents))+'翻譯:' + "/".join(set(translators))+"" if len(places['聯絡情形']) == 1 else "/".join(set(s['聯絡情形'] for i, s in places.iterrows()))+'\n'+ '聯絡窗口:'+'\n'+"\n".join(contacts)+'\n'+ tap
                ec += 1
                contens.append(content)
            
            if name not in result:
                result[name] = []
            ec += 1
            result[name].append(str(dateTime).split(' ')[0] +
                        "\n".join(set(contens)) +
                        "\n".join([
                            '貼心提醒',
                            '1. 輔導記錄照片請盡量採橫式拍攝，並留意清晰度。',
                            '2. 請協助篩選呈現效果好，適合刊登新聞的照片（如取鏡畫質佳、主題明確、未過度揭露移工面容資訊等），8張海報都需要。'
                        ]))
            ec += 1
        except Exception as e:
            raise Exception(str(ec) + str(employee))
        
    if ec >= 47:
        e = 0
        
    return result

def get_dateTimes(data: pd.DataFrame):
    dates = data[data['日期'] > datetime.now()]
    dates = dates.sort_values(by='日期')
    return dates['日期'].unique().tolist()

def get_dateTimes2(data: pd.DataFrame):
    dates = data[data['日期'] > datetime.now()]
    dates = dates.sort_values(by='日期')
    return dates

def extract_start_time(time_range):
    start_time_str = time_range.split('-')[0]
    return datetime.strptime(start_time_str, "%H:%M")

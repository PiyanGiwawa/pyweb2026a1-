import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
import random

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入石詠澤的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於詠澤</a><hr>"
    link += "<a href=/welcome?u=詠澤&dep=靜宜資管>GET傳值</a><hr>"   
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>" 
    link += "<a href=/math>數學運算</a><hr>" 
    link += "<a href=/math2>次方與根號計算</a><hr>" 
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序，取前4名)</a><br>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    return link

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form["keyword"]

        db = firestore.client()
        collection_ref = db.collection("靜宜資管2026a")

        docs = collection_ref.get()

        result = ""

        for doc in docs:
            user = doc.to_dict()
            if keyword in user["name"]:
                result += f"{user['name']}老師的研究室在 {user['lab']}<br>"

        if result == "":
            result = "查無資料"

        return result + "<br><a href=/search>返回</a>"

    return """
    <h2>查詢老師研究室</h2>
    <form method="post">
        請輸入老師姓名：
        <input type="text" name="keyword">
        <input type="submit" value="查詢">
    </form>
    <a href="/">回首頁</a>
    """

@app.route("/today")
def today():
    now = datetime.now()
    year  = str(now.year)   # 取得年份 
    month = str(now.month)  # 取得月份 
    day   = str(now.day)    # 取得日期 
    now = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime = now)

@app.route("/about")
def about():
    return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = int(request.form["x"])
        opt = request.form["opt"]
        y = int(request.form["y"])      
        result = "您輸入的是：" + str(x) + opt + str(y)
        
        if (opt == "/" and y == 0):
            result += "，除數不能為0"
        else:
            match opt:
                case "+":
                    r = x + y
                case "-":
                    r = x - y
                case "*":
                    r = x * y
                case "/":
                    r = x / y  # 修正：之前誤寫為 x - y
                case _:
                    return "未知運算符號"
            result += "=" + str(r)  + "<br><a href=/>返回首頁</a>"          
        return result
    else:
        return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)



@app.route("/math2", methods=["GET", "POST"])
def math2():
    result = None
    if request.method == "POST":
        # 取得使用者輸入
        x = int(request.form.get("x"))
        opt = request.form.get("opt")
        y = int(request.form.get("y"))

        # 你的核心邏輯
        match opt:
            case "∧":
                result = x ** y
            case "√":
                if y != 0:
                    result = x ** (1/y)
                else:
                    result = "數學上不存在「0 次方根」"
            case _:
                result = "請輸入∧(次方)或√(根號)"
    return render_template("math2.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)

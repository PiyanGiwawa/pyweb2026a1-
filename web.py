import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
import random

app = Flask(__name__)

# ================== 首頁 ==================
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
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/search>查詢老師研究室</a><hr>"
    link += "<a href=/movies>即將上映電影</a><hr>"
    link += "<a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"

    return link

@app.route("/movie")
def movie():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 




# ================== 電影爬蟲 ==================
@app.route("/movies")
def movies():
    url = "https://www.atmovies.com.tw/movie/next/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"

    soup = BeautifulSoup(res.text, "html.parser")

    items = soup.select("ul.filmListAllX li a")  # ✔ 改這裡

    R = "<h2>即將上映電影</h2>"
    R += '<a href="/">🏠 回首頁</a><hr>'

    if not items:
        return "❌ 沒抓到資料（網站可能改版或被擋）"

    for a in items:
        name = a.text.strip()
        link = "https://www.atmovies.com.tw" + a.get("href")

        R += f'<a href="{link}" target="_blank">{name}</a><br><br>'

    return R

# ================== Firestore 查詢 ==================
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

# ================== 日期 ==================
@app.route("/today")
def today():
    now = datetime.now()
    now_str = f"{now.year}年{now.month}月{now.day}日"
    return render_template("today.html", datetime=now_str)

# ================== 關於 ==================
@app.route("/about")
def about():
    return render_template("mis2a.html")

# ================== GET ==================
@app.route("/welcome")
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name=x, dep=y)

# ================== POST ==================
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        return f"您輸入的帳號是：{user}; 密碼為：{pwd}"
    return render_template("account.html")

# ================== 數學 ==================
@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = int(request.form["x"])
        opt = request.form["opt"]
        y = int(request.form["y"])

        if opt == "/" and y == 0:
            return "除數不能為0"

        match opt:
            case "+": r = x + y
            case "-": r = x - y
            case "*": r = x * y
            case "/": r = x / y
            case _: return "未知運算符號"

        return f"{x}{opt}{y}={r}<br><a href=/>返回首頁</a>"

    return render_template("math.html")

# ================== 擲茭 ==================
@app.route('/cup')
def cup():
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        if x1 != x2:
            msg = "聖筊"
        elif x1 == 0:
            msg = "笑筊"
        else:
            msg = "陰筊"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

# ================== 次方根號 ==================
@app.route("/math2", methods=["GET", "POST"])
def math2():
    result = None
    if request.method == "POST":
        x = int(request.form.get("x"))
        opt = request.form.get("opt")
        y = int(request.form.get("y"))

        match opt:
            case "∧":
                result = x ** y
            case "√":
                result = x ** (1/y) if y != 0 else "錯誤"
            case _:
                result = "錯誤"

    return render_template("math2.html", result=result)

# ================== 主程式 ==================
if __name__ == "__main__":
    app.run(debug=True)
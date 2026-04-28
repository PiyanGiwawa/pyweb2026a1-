@app.route("/movie2")
def movie2():
    import requests
    from bs4 import BeautifulSoup
    import os
    import json
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Firebase（支援本地 + Vercel）
    if not firebase_admin._apps:
        if os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
        else:
            firebase_config = os.getenv('FIREBASE_CONFIG')
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred)

    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"

    sp = BeautifulSoup(Data.text, "html.parser")
    updateDate = sp.find("div", class_="smaller09").text.replace("更新時間:", "")
    result = sp.select(".filmListAllX li")
    info = ""

    db = firestore.client()   # ✔ 移出 for（效能較好）

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")

        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")

        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        showDate = show[0:10]

        if "片長" in show:
            show = show.replace("片長：", "")
            show = show.replace("分", "")

            showDate = show[0:10]
            showLength = show[13:].replace(" ", "")

        else:
            showLength = "尚無片長資訊"

        info += movie_id + "\n" + picture + "\n" + title + "\n" + hyperlink + "\n" + showDate + "\n" + showLength + "\n\n"

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": updateDate
        }

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)

    info += updateDate + "\n\n"

    return "資料寫入完成<br>更新時間：" + updateDate
from flask import Flask, request, render_template, redirect
from math import floor
import string
import pymongo
import strgen
try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str
import base64
from bson import ObjectId

app = Flask(__name__)
host = 'http://localhost:5000/'
dbpool = pymongo.MongoClient("127.0.0.1", 27017)
db = dbpool.keydb
web_url = db.web_url

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('url') == '':
            return render_template('home.html')
        else:
            original_url = str_encode(request.form.get('url'))
            if urlparse(original_url).scheme == '':
                url = 'http://' + original_url
            else:
                url = original_url
            key = strgen.StringGenerator(r"[\d\w]{8}").render()
            web_url.insert_one({"key": key, "url": base64.urlsafe_b64encode(url)})
            return render_template('home.html', short_url=host + key)
    return render_template('home.html')


@app.route('/<short_url>')
def redirect_short_url(short_url):
    res = web_url.find({"key": short_url})
    for r in res:
        url = base64.urlsafe_b64decode(r["url"])
    if url == "":
        url = host    # fallback if no URL is found
    return redirect(url)


if __name__ == '__main__':
    app.run(debug=True)

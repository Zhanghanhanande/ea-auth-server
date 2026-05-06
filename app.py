from flask import Flask, request, redirect, session
import sqlite3, time, datetime

app = Flask(__name__)
app.secret_key = "123456"

USERNAME = "admin"
PASSWORD = "123456"

DB = "auth.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["u"] == USERNAME and request.form["p"] == PASSWORD:
            session["ok"] = True
            return redirect("/")
        return "登录失败"

    return """
    <h3>登录</h3>
    <form method=post>
    <input name=u placeholder=账号><br>
    <input name=p type=password placeholder=密码><br>
    <button>登录</button>
    </form>
    """

@app.before_request
def check():
    if request.path in ["/login", "/"]:
        return
    if not session.get("ok"):
        return redirect("/login")

@app.route("/")
def home():
    return "<h1>测试成功</h1>"

@app.route("/auth")
def auth():
    acc = request.args.get("account")
    srv = request.args.get("server")

    conn = db()
    row = conn.execute(
        "SELECT * FROM licenses WHERE account=? AND server=?",
        (acc, srv)
    ).fetchone()

    if not row:
        return "DENY"

    if row["enabled"] == 0:
        return "DENY"

    if row["expiry"] < time.time():
        return "DENY"

    return "OK"

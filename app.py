
from flask import Flask, request, redirect, session
import sqlite3, time, datetime, os

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
    if request.path == "/login":
        return
    if not session.get("ok"):
        return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def home():
    conn = db()

    # 新增授权
    if request.method == "POST":
        account = request.form["account"]
        server = request.form["server"]
        days = int(request.form["days"])

        expiry = int(time.time()) + days * 86400

        conn.execute(
            "INSERT INTO licenses VALUES (?, ?, ?, ?)",
            (account, server, expiry, 1),
        )
        conn.commit()

    keyword = request.args.get("kw", "")

    if keyword:
        rows = conn.execute(
            "SELECT * FROM licenses WHERE account LIKE ?",
            ("%" + keyword + "%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM licenses").fetchall()

    html = """
    <h2>EA授权管理</h2>

    <form method="post">
        账号: <input name="account">
        服务器: <input name="server">
        天数: <input name="days" value="30">
        <button>新增授权</button>
    </form>

    <br>
    <form>
        搜索账号: <input name="kw">
        <button>搜索</button>
    </form>
    <hr>
    """

    for r in rows:
        expiry_time = datetime.datetime.fromtimestamp(r["expiry"])
        expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M")

        status = "启用" if r["enabled"] else "禁用"

        html += f"<p>{r['account']} | {r['server']} | {expiry_str} | {status}</p>"

    return html
@app.route("/add", methods=["POST"])
def add():
    acc = request.form["account"]
    srv = request.form["server"]
    days = int(request.form["days"])

    expiry = int(time.time()) + days*86400

    conn = db()
    conn.execute(
        "INSERT OR REPLACE INTO licenses VALUES (?,?,?,1)",
        (acc, srv, expiry)
    )
    conn.commit()

    return redirect("/")

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

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


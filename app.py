def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        account TEXT,
        server TEXT,
        expiry INTEGER,
        enabled INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()
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

# 登录页
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["u"] == USERNAME and request.form["p"] == PASSWORD:
            session["ok"] = True
            return redirect("/admin")
        return "登录失败"

    return """
    <h3>登录</h3>
    <form method=post>
    <input name=u placeholder=账号><br>
    <input name=p type=password placeholder=密码><br>
    <button>登录</button>
    </form>
    """

# 登录检查
@app.before_request
def check():
    if request.path in ["/login", "/auth"]:
        return
    if not session.get("ok"):
        return redirect("/login")

# 后台页面（核心）
@app.route("/admin", methods=["GET","POST"])
def admin():
    conn = db()

    # 添加数据
    if request.method == "POST":
        account = request.form["account"]
        server = request.form["server"]
        days = int(request.form["days"])

        expiry = int(time.time()) + days * 86400

        conn.execute(
            "INSERT INTO licenses (account, server, expiry, enabled) VALUES (?, ?, ?, 1)",
            (account, server, expiry)
        )
        conn.commit()

    # 查询所有数据
    rows = conn.execute("SELECT * FROM licenses").fetchall()

    html = "<h2>后台管理</h2>"

    html += """
    <h3>添加授权</h3>
    <form method=post>
    账号: <input name=account><br>
    服务器: <input name=server><br>
    天数: <input name=days><br>
    <button>添加</button>
    </form>
    <hr>
    """

    # 显示列表
    html += "<h3>授权列表</h3>"

    for r in rows:
        t = datetime.datetime.fromtimestamp(r["expiry"]).strftime("%Y-%m-%d %H:%M")
        html += f"<p>{r['account']} | {r['server']} | 到期:{t} | 状态:{r['enabled']}</p>"

    return html

# 授权接口（你原来的功能）
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

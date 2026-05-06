from flask import Flask, request, redirect, session, jsonify
import sqlite3, time, datetime, os

app = Flask(__name__)
app.secret_key = "123456"

DB = "auth.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT,
        server TEXT,
        expiry INTEGER,
        enabled INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

USERNAME = "admin"
PASSWORD = "123456"

# ─── 登录页 ───────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        if request.form["u"] == USERNAME and request.form["p"] == PASSWORD:
            session["ok"] = True
            return redirect("/admin")
        error = "账号或密码错误"
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EA 授权管理系统</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0a0a0f;
    --surface: #111118;
    --border: #1e1e2e;
    --accent: #7c6af7;
    --accent2: #f76a8a;
    --text: #e8e8f0;
    --muted: #5a5a72;
    --success: #4ade80;
    --danger: #f87171;
  }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }}
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 60% 40% at 20% 20%, rgba(124,106,247,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 50% 50% at 80% 80%, rgba(247,106,138,0.08) 0%, transparent 60%);
    pointer-events: none;
  }}
  .grid-bg {{
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(124,106,247,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(124,106,247,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
  }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 48px 44px;
    width: 380px;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 0 1px rgba(124,106,247,0.1), 0 32px 64px rgba(0,0,0,0.4);
    animation: rise 0.5s cubic-bezier(0.16,1,0.3,1) both;
  }}
  @keyframes rise {{
    from {{ opacity:0; transform: translateY(24px); }}
    to   {{ opacity:1; transform: translateY(0); }}
  }}
  .logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 32px;
  }}
  .logo-icon {{
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }}
  .logo-text {{ font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }}
  h2 {{ font-size: 26px; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }}
  .subtitle {{ color: var(--muted); font-size: 14px; margin-bottom: 32px; }}
  label {{ display: block; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }}
  input {{
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    margin-bottom: 20px;
  }}
  input:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(124,106,247,0.15);
  }}
  button {{
    width: 100%;
    background: linear-gradient(135deg, var(--accent), #9b8df9);
    border: none;
    border-radius: 10px;
    padding: 13px;
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.15s;
    letter-spacing: 0.02em;
    margin-top: 4px;
  }}
  button:hover {{ opacity: 0.88; transform: translateY(-1px); }}
  button:active {{ transform: translateY(0); }}
  .error {{
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: var(--danger);
    margin-bottom: 20px;
  }}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="card">
  <div class="logo">
    <div class="logo-icon">⚡</div>
    <span class="logo-text">EA AUTH</span>
  </div>
  <h2>后台登录</h2>
  <p class="subtitle">授权管理系统 · 管理员入口</p>
  {'<div class="error">⚠ ' + error + '</div>' if error else ''}
  <form method="post">
    <label>账号</label>
    <input name="u" placeholder="输入管理员账号" autocomplete="off">
    <label>密码</label>
    <input name="p" type="password" placeholder="输入密码">
    <button type="submit">登 录 →</button>
  </form>
</div>
</body>
</html>"""

@app.before_request
def check():
    if request.path in ["/login", "/auth"]:
        return
    if not session.get("ok"):
        return redirect("/login")

@app.route("/")
def home():
    return redirect("/admin")

# ─── 删除授权 ──────────────────────────────────────────────────────────────────
@app.route("/delete/<int:lid>", methods=["POST"])
def delete(lid):
    conn = db()
    conn.execute("DELETE FROM licenses WHERE id=?", (lid,))
    conn.commit()
    return redirect("/admin")

# ─── 切换启用/禁用 ─────────────────────────────────────────────────────────────
@app.route("/toggle/<int:lid>", methods=["POST"])
def toggle(lid):
    conn = db()
    row = conn.execute("SELECT enabled FROM licenses WHERE id=?", (lid,)).fetchone()
    if row:
        new_state = 0 if row["enabled"] == 1 else 1
        conn.execute("UPDATE licenses SET enabled=? WHERE id=?", (new_state, lid))
        conn.commit()
    return redirect("/admin")

# ─── 后台管理页 ────────────────────────────────────────────────────────────────
@app.route("/admin", methods=["GET", "POST"])
def admin():
    conn = db()
    msg = ""
    if request.method == "POST":
        account = request.form["account"].strip()
        server  = request.form["server"].strip()
        days    = int(request.form["days"])
        expiry  = int(time.time()) + days * 86400
        conn.execute(
            "INSERT INTO licenses (account, server, expiry, enabled) VALUES (?, ?, ?, 1)",
            (account, server, expiry)
        )
        conn.commit()
        msg = "授权添加成功"

    rows = conn.execute("SELECT * FROM licenses ORDER BY id DESC").fetchall()
    now  = int(time.time())

    # 统计
    total   = len(rows)
    active  = sum(1 for r in rows if r["enabled"] == 1 and r["expiry"] > now)
    expired = sum(1 for r in rows if r["expiry"] <= now)
    disabled= sum(1 for r in rows if r["enabled"] == 0)

    # 构建授权行HTML
    rows_html = ""
    for r in rows:
        exp_dt   = datetime.datetime.fromtimestamp(r["expiry"]).strftime("%Y-%m-%d %H:%M")
        remaining= r["expiry"] - now
        rem_days = remaining // 86400
        is_exp   = remaining <= 0
        is_dis   = r["enabled"] == 0

        if is_exp:
            badge = '<span class="badge badge-expired">已到期</span>'
            row_cls = "row-expired"
        elif is_dis:
            badge = '<span class="badge badge-disabled">已禁用</span>'
            row_cls = "row-disabled"
        else:
            badge = f'<span class="badge badge-active">有效 · {rem_days}天</span>'
            row_cls = ""

        toggle_label = "启用" if is_dis else "禁用"
        toggle_cls   = "btn-enable" if is_dis else "btn-disable"

        rows_html += f"""
        <tr class="{row_cls}">
          <td><span class="mono">#{r['id']}</span></td>
          <td><span class="mono acct">{r['account']}</span></td>
          <td><span class="mono srv">{r['server']}</span></td>
          <td><span class="mono">{exp_dt}</span></td>
          <td>{badge}</td>
          <td>
            <div class="actions">
              <form method="post" action="/toggle/{r['id']}" style="display:inline">
                <button type="submit" class="btn-sm {toggle_cls}">{toggle_label}</button>
              </form>
              <form method="post" action="/delete/{r['id']}" style="display:inline"
                    onsubmit="return confirm('确认删除账号 {r['account']} 的授权？')">
                <button type="submit" class="btn-sm btn-del">删除</button>
              </form>
            </div>
          </td>
        </tr>"""

    if not rows_html:
        rows_html = '<tr><td colspan="6" class="empty">暂无授权数据</td></tr>'

    msg_html = f'<div class="toast" id="toast">✓ {msg}</div>' if msg else ""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EA 授权管理后台</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #16161f;
    --border: #1e1e2e;
    --accent: #7c6af7;
    --accent2: #f76a8a;
    --text: #e8e8f0;
    --muted: #5a5a72;
    --success: #4ade80;
    --warning: #facc15;
    --danger: #f87171;
  }}
  html {{ scrollbar-width: thin; scrollbar-color: var(--border) var(--bg); }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
  }}
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 50% 30% at 5% 5%, rgba(124,106,247,0.1) 0%, transparent 60%),
      radial-gradient(ellipse 40% 40% at 95% 10%, rgba(247,106,138,0.06) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
  }}

  /* ── Layout ── */
  .layout {{ display: flex; min-height: 100vh; position: relative; z-index: 1; }}
  .sidebar {{
    width: 220px; flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 28px 20px;
    display: flex; flex-direction: column;
    position: sticky; top: 0; height: 100vh;
  }}
  .main {{ flex: 1; padding: 36px 40px; overflow-x: hidden; }}

  /* ── Sidebar ── */
  .logo {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 36px; padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }}
  .logo-icon {{
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }}
  .logo-text {{ font-size: 16px; font-weight: 800; letter-spacing: -0.3px; }}
  .nav-label {{
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 10px; padding-left: 8px;
  }}
  .nav-item {{
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 8px;
    font-size: 14px; font-weight: 600;
    color: var(--muted); cursor: pointer;
    transition: all 0.15s;
    text-decoration: none;
  }}
  .nav-item.active, .nav-item:hover {{
    background: rgba(124,106,247,0.12);
    color: var(--accent);
  }}
  .sidebar-footer {{
    margin-top: auto; padding-top: 20px;
    border-top: 1px solid var(--border);
  }}
  .logout {{
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 8px;
    font-size: 13px; font-weight: 600;
    color: var(--muted); text-decoration: none;
    transition: all 0.15s;
  }}
  .logout:hover {{ color: var(--danger); background: rgba(248,113,113,0.08); }}

  /* ── Header ── */
  .page-header {{ margin-bottom: 32px; }}
  .page-title {{ font-size: 30px; font-weight: 800; letter-spacing: -1px; margin-bottom: 4px; }}
  .page-sub {{ color: var(--muted); font-size: 14px; }}

  /* ── Stats ── */
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
  .stat {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }}
  .stat:hover {{ border-color: var(--accent); }}
  .stat::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
  }}
  .stat:nth-child(1)::before {{ background: linear-gradient(90deg, var(--accent), var(--accent2)); }}
  .stat:nth-child(2)::before {{ background: var(--success); }}
  .stat:nth-child(3)::before {{ background: var(--danger); }}
  .stat:nth-child(4)::before {{ background: var(--muted); }}
  .stat-val {{ font-size: 32px; font-weight: 800; letter-spacing: -1px; font-family: 'JetBrains Mono', monospace; }}
  .stat-label {{ font-size: 12px; color: var(--muted); margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }}

  /* ── Panel ── */
  .panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 24px;
  }}
  .panel-header {{
    padding: 18px 24px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }}
  .panel-title {{ font-size: 15px; font-weight: 700; }}
  .panel-body {{ padding: 24px; }}

  /* ── Form ── */
  .form-grid {{ display: grid; grid-template-columns: 1fr 1fr 120px auto; gap: 12px; align-items: end; }}
  .form-group label {{
    display: block; font-size: 11px; font-weight: 700;
    letter-spacing: 0.08em; color: var(--muted);
    text-transform: uppercase; margin-bottom: 8px;
  }}
  input[type=text], input[type=number] {{
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 10px 14px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }}
  input:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(124,106,247,0.15);
  }}
  .btn-primary {{
    background: linear-gradient(135deg, var(--accent), #9b8df9);
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 14px; font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    transition: opacity 0.2s, transform 0.15s;
    height: 40px;
  }}
  .btn-primary:hover {{ opacity: 0.88; transform: translateY(-1px); }}

  /* ── Table ── */
  table {{ width: 100%; border-collapse: collapse; }}
  thead tr {{ border-bottom: 1px solid var(--border); }}
  th {{
    padding: 10px 16px;
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); text-align: left;
  }}
  td {{
    padding: 14px 16px;
    font-size: 13px;
    border-bottom: 1px solid rgba(30,30,46,0.6);
    vertical-align: middle;
  }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(124,106,247,0.04); }}
  .row-expired td {{ opacity: 0.5; }}
  .row-disabled td {{ opacity: 0.6; }}
  .mono {{ font-family: 'JetBrains Mono', monospace; }}
  .acct {{ color: var(--accent); font-weight: 500; }}
  .srv  {{ color: #a0a0c0; }}
  .empty {{ text-align: center; color: var(--muted); padding: 40px !important; font-size: 14px; }}

  /* ── Badges ── */
  .badge {{
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.04em;
  }}
  .badge-active  {{ background: rgba(74,222,128,0.12); color: var(--success); border: 1px solid rgba(74,222,128,0.25); }}
  .badge-expired {{ background: rgba(248,113,113,0.12); color: var(--danger);  border: 1px solid rgba(248,113,113,0.25); }}
  .badge-disabled{{ background: rgba(90,90,114,0.2);   color: var(--muted);   border: 1px solid rgba(90,90,114,0.3); }}

  /* ── Action Buttons ── */
  .actions {{ display: flex; gap: 8px; }}
  .btn-sm {{
    padding: 5px 12px; border-radius: 6px;
    font-size: 12px; font-weight: 700;
    cursor: pointer; border: 1px solid;
    font-family: 'Syne', sans-serif;
    transition: all 0.15s;
  }}
  .btn-disable {{
    background: rgba(250,204,21,0.08);
    border-color: rgba(250,204,21,0.25);
    color: var(--warning);
  }}
  .btn-disable:hover {{ background: rgba(250,204,21,0.18); }}
  .btn-enable {{
    background: rgba(74,222,128,0.08);
    border-color: rgba(74,222,128,0.25);
    color: var(--success);
  }}
  .btn-enable:hover {{ background: rgba(74,222,128,0.18); }}
  .btn-del {{
    background: rgba(248,113,113,0.08);
    border-color: rgba(248,113,113,0.25);
    color: var(--danger);
  }}
  .btn-del:hover {{ background: rgba(248,113,113,0.18); }}

  /* ── Toast ── */
  .toast {{
    position: fixed; top: 24px; right: 24px;
    background: rgba(74,222,128,0.15);
    border: 1px solid rgba(74,222,128,0.35);
    color: var(--success);
    padding: 12px 20px; border-radius: 10px;
    font-size: 14px; font-weight: 600;
    z-index: 999;
    animation: slideIn 0.3s ease, fadeOut 0.4s ease 2.5s forwards;
  }}
  @keyframes slideIn {{
    from {{ opacity:0; transform: translateX(20px); }}
    to   {{ opacity:1; transform: translateX(0); }}
  }}
  @keyframes fadeOut {{
    to {{ opacity:0; transform: translateX(20px); }}
  }}

  /* ── Responsive ── */
  @media (max-width: 900px) {{
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    .form-grid {{ grid-template-columns: 1fr 1fr; }}
    .sidebar {{ display: none; }}
    .main {{ padding: 20px; }}
  }}
</style>
</head>
<body>
{msg_html}
<div class="layout">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <span class="logo-text">EA AUTH</span>
    </div>
    <div class="nav-label">菜单</div>
    <a class="nav-item active" href="/admin">
      <span>🔑</span> 授权管理
    </a>
    <div class="sidebar-footer">
      <a class="logout" href="/logout">
        <span>↩</span> 退出登录
      </a>
    </div>
  </aside>

  <!-- Main -->
  <main class="main">
    <div class="page-header">
      <h1 class="page-title">授权管理</h1>
      <p class="page-sub">管理 EA 账号授权 · 共 {total} 条记录</p>
    </div>

    <!-- Stats -->
    <div class="stats">
      <div class="stat">
        <div class="stat-val">{total}</div>
        <div class="stat-label">全部授权</div>
      </div>
      <div class="stat">
        <div class="stat-val">{active}</div>
        <div class="stat-label">有效授权</div>
      </div>
      <div class="stat">
        <div class="stat-val">{expired}</div>
        <div class="stat-label">已到期</div>
      </div>
      <div class="stat">
        <div class="stat-val">{disabled}</div>
        <div class="stat-label">已禁用</div>
      </div>
    </div>

    <!-- Add Form -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">➕ 添加授权</span>
      </div>
      <div class="panel-body">
        <form method="post">
          <div class="form-grid">
            <div class="form-group">
              <label>MT5 账号</label>
              <input type="text" name="account" placeholder="如：277656369" required>
            </div>
            <div class="form-group">
              <label>服务器</label>
              <input type="text" name="server" placeholder="如：Exness-MT5Trial5" required>
            </div>
            <div class="form-group">
              <label>授权天数</label>
              <input type="number" name="days" placeholder="30" min="1" required>
            </div>
            <div class="form-group">
              <label>&nbsp;</label>
              <button type="submit" class="btn-primary">添加 →</button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Table -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">📋 授权列表</span>
        <span style="font-size:12px;color:var(--muted);">共 {total} 条</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>账号</th>
            <th>服务器</th>
            <th>到期时间</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
  </main>
</div>
</body>
</html>"""

# ─── 退出登录 ──────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ─── 授权验证接口（EA调用）────────────────────────────────────────────────────
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

if __name__ == "__main__":
    app.run(debug=True)

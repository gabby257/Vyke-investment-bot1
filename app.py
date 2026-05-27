from flask import Flask, render_template_string, redirect, request, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
PASSWORD = "admin123"

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

HTML = """
<h1>Admin Dashboard</h1>

<h3>Total Users: {{users}}</h3>

<h2>Add Balance</h2>
<form method="POST" action="/add_balance">
<input name="user_id" placeholder="User ID"/>
<input name="amount" placeholder="Amount"/>
<button>Add Balance</button>
</form>

<h2>Withdrawals</h2>
{% for w in withdrawals %}
<div style="border:1px solid red; padding:10px; margin:10px;">
<p>ID: {{w[0]}}</p>
<p>User: {{w[1]}}</p>
<p>Amount: ₦{{w[2]}}</p>
<p>Status: {{w[3]}}</p>

{% if w[3] == "pending" %}
<form method="POST" action="/approve/{{w[0]}}">
<button>Approve</button>
</form>

<form method="POST" action="/reject/{{w[0]}}">
<button>Reject</button>
</form>
{% endif %}
</div>
{% endfor %}
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["admin"] = True
            return redirect("/dashboard")
    return "<form method='post'><input name='password'><button>Login</button></form>"

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    withdrawals = cursor.execute("SELECT * FROM withdrawals").fetchall()

    return render_template_string(HTML, users=users, withdrawals=withdrawals)

@app.route("/add_balance", methods=["POST"])
def add_balance():
    uid = int(request.form["user_id"])
    amt = float(request.form["amount"])

    cursor.execute("UPDATE balances SET amount = amount + ? WHERE user_id=?", (amt, uid))
    conn.commit()

    return redirect("/dashboard")

@app.route("/approve/<int:id>", methods=["POST"])
def approve(id):
    row = cursor.execute("SELECT user_id, amount FROM withdrawals WHERE id=?", (id,)).fetchone()

    if row:
        uid, amt = row
        current = cursor.execute("SELECT amount FROM balances WHERE user_id=?", (uid,)).fetchone()[0]

        if current >= amt:
            cursor.execute("UPDATE balances SET amount = amount - ? WHERE user_id=?", (amt, uid))

        cursor.execute("UPDATE withdrawals SET status='approved' WHERE id=?", (id,))
        conn.commit()

    return redirect("/dashboard")

@app.route("/reject/<int:id>", methods=["POST"])
def reject(id):
    cursor.execute("UPDATE withdrawals SET status='rejected' WHERE id=?", (id,))
    conn.commit()

    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


def get_db():
    return sqlite3.connect("database.db")


# ================= HOME =================

@app.route("/")
def home():

    if "user" in session:
        return redirect("/items")

    return redirect("/login")


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        user = request.form["user"]
        password = request.form["password"]

        db = get_db()

        db.execute(
            "INSERT INTO users (user,password) VALUES (?,?)",
            (user, password)
        )

        db.commit()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = request.form["user"]
        password = request.form["password"]

        db = get_db()

        cur = db.execute(
            "SELECT * FROM users WHERE user=? AND password=?",
            (user, password)
        )

        data = cur.fetchone()

        if data:
            session["user"] = user
            return redirect("/items")

    return render_template("login.html")


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ================= ITEMS =================

@app.route("/items")
def items():

    if "user" not in session:
        return redirect("/login")

    db = get_db()

    cur = db.execute("SELECT * FROM items")

    data = cur.fetchall()

    return render_template("items.html", data=data)


# ================= ADD =================

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]

    db = get_db()

    db.execute(
        "INSERT INTO items(name) VALUES (?)",
        (name,)
    )

    db.commit()

    return redirect("/items")


# ================= DELETE =================

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/login")

    db = get_db()

    db.execute(
        "DELETE FROM items WHERE id=?",
        (id,)
    )

    db.commit()

    return redirect("/items")


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


def get_db():
    return sqlite3.connect("database.db")


@app.route("/")
def home():
    if "user" in session:
        return "Hello " + session["user"]
    return redirect("/login")


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
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "123"


# ================= UPLOAD =================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DB =================

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
        db.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/api/register", methods=["POST"])
def api_register():

    data = request.json

    user = data["user"]
    password = data["password"]

    db = get_db()

    db.execute(
        "INSERT INTO users(user,password) VALUES (?,?)",
        (user, password)
    )

    db.commit()
    db.close()

    return {
        "status": "ok",
        "message": "registered"
    }
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

        db.close()

        if data:
            session["user"] = user
            return redirect("/items")

    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():

    data = request.json

    user = data["user"]
    password = data["password"]

    db = get_db()

    cur = db.execute(
        "SELECT * FROM users WHERE user=? AND password=?",
        (user, password)
    )

    r = cur.fetchone()

    db.close()

    if not r:
        return {
            "status": "fail"
        }

    return {
        "status": "ok",
        "user": r[1]
    }


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

    db.close()

    return render_template("items.html", data=data)


# ================= ADD =================

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]

    file = request.files.get("image")

    filename = ""

    if file and file.filename != "":

        filename = file.filename

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(path)

    db = get_db()

    db.execute(
        "INSERT INTO items(name,image,user) VALUES (?,?,?)",
        (name, filename, session["user"])
    )

    db.commit()
    db.close()

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
    db.close()

    return redirect("/items")


# ================= EDIT =================

@app.route("/edit/<int:id>")
def edit(id):

    if "user" not in session:
        return redirect("/login")

    db = get_db()

    cur = db.execute(
        "SELECT * FROM items WHERE id=?",
        (id,)
    )

    data = cur.fetchone()

    db.close()

    return render_template(
        "edit.html",
        item=data
    )


# ================= UPDATE =================

@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]

    db = get_db()

    db.execute(
        "UPDATE items SET name=? WHERE id=?",
        (name, id)
    )

    db.commit()
    db.close()

    return redirect("/items")


# ================= SEARCH =================

@app.route("/search", methods=["POST"])
def search():

    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]

    db = get_db()

    cur = db.execute(
        "SELECT * FROM items WHERE name LIKE ?",
        ("%" + name + "%",)
    )

    data = cur.fetchall()

    db.close()

    return render_template(
        "items.html",
        data=data
    )

@app.route("/api/items")
def api_items():

    db = get_db()

    cur = db.execute(
        "SELECT * FROM items"
    )

    rows = cur.fetchall()

    db.close()

    data = []

    for r in rows:

        data.append({
            "id": r[0],
            "name": r[1],
            "image": r[2],
            "user": r[3]
        })

    return {
        "items": data
    }
@app.route("/api/items/<int:id>")
def api_item(id):

    db = get_db()

    cur = db.execute(
        "SELECT * FROM items WHERE id=?",
        (id,)
    )

    r = cur.fetchone()

    db.close()

    if not r:
        return {"error": "not found"}

    return {
        "id": r[0],
        "name": r[1],
        "image": r[2],
        "user": r[3]
    }
@app.route("/api/items", methods=["GET"])
def api_get_items():

    db = get_db()

    cur = db.execute(
        "SELECT * FROM items"
    )

    rows = cur.fetchall()

    db.close()

    data = []

    for r in rows:

        data.append({
            "id": r[0],
            "name": r[1],
            "image": r[2],
            "user": r[3]
        })

    return {
        "items": data
    }
@app.route("/api/items", methods=["POST"])
def api_add():

    name = request.form["name"]

    db = get_db()

    db.execute(
        "INSERT INTO items(name) VALUES (?)",
        (name,)
    )

    db.commit()
    db.close()

    return {
        "status": "ok"
    }
@app.route("/api/items/<int:id>", methods=["DELETE"])
def api_delete(id):

    db = get_db()

    db.execute(
        "DELETE FROM items WHERE id=?",
        (id,)
    )

    db.commit()
    db.close()

    return {
        "status": "deleted"
    }

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
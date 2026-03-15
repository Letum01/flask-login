from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        return "Hello " + user
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
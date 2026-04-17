from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ==============================
# HOME (LOGIN PAGE)
# ==============================
@app.route("/")
def home():
    return render_template("login.html")


# ==============================
# SIGNUP
# ==============================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("blog.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


# ==============================
# LOGIN
# ==============================
@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        session["user"] = username
        return redirect("/dashboard")

    return "Invalid Login"


# ==============================
# DASHBOARD
# ==============================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"])


# ==============================
# CREATE BLOG PAGE
# ==============================
@app.route("/create_blog")
def create_blog():

    if "user" not in session:
        return redirect("/")

    return render_template("create_blog.html")


# ==============================
# SAVE BLOG
# ==============================
@app.route("/save_blog", methods=["POST"])
def save_blog():

    if "user" not in session:
        return redirect("/")

    title = request.form["title"]
    content = request.form["content"]

    file = request.files.get("image")

    filename = ""
    if file and file.filename != "":
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO blogs (title, content, image, author) VALUES (?, ?, ?, ?)",
        (title, content, filename, session["user"])
    )

    conn.commit()
    conn.close()

    return redirect("/blogs")


# ==============================
# VIEW BLOGS (WITH SEARCH)
# ==============================
@app.route("/blogs")
def blogs():

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    # 🔍 search value lena
    search = request.args.get("search")

    if search:
        cursor.execute(
            "SELECT * FROM blogs WHERE title LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cursor.execute("SELECT * FROM blogs")

    blogs = cursor.fetchall()

    conn.close()

    return render_template("blogs.html", blogs=blogs)

# ==============================
# DELETE BLOG
# ==============================
@app.route("/delete_blog/<int:id>")
def delete_blog(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    # 🔐 check owner
    cursor.execute("SELECT author FROM blogs WHERE id=?", (id,))
    blog = cursor.fetchone()

    if blog and blog[0] == session["user"]:
        cursor.execute("DELETE FROM blogs WHERE id=?", (id,))
        conn.commit()

    conn.close()

    return redirect("/blogs")


# ==============================
# EDIT BLOG PAGE
# ==============================
@app.route("/edit_blog/<int:id>")
def edit_blog(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM blogs WHERE id=?", (id,))
    blog = cursor.fetchone()

    conn.close()

    # 🔐 owner check
    if blog and blog[4] == session["user"]:
        return render_template("edit_blog.html", blog=blog)

    return "Unauthorized Access"


# ==============================
# UPDATE BLOG
# ==============================

@app.route("/update_blog/<int:id>", methods=["POST"])
def update_blog(id):

    if "user" not in session:
        return redirect("/")

    title = request.form["title"]
    content = request.form["content"]

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    # 🔐 owner check
    cursor.execute("SELECT author FROM blogs WHERE id=?", (id,))
    blog = cursor.fetchone()

    if blog and blog[0] == session["user"]:
        cursor.execute(
            "UPDATE blogs SET title=?, content=? WHERE id=?",
            (title, content, id)
        )
        conn.commit()

    conn.close()

    return redirect("/blogs")

# ==============================
# MY BLOGS
# ==============================
@app.route("/my_blogs")
def my_blogs():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM blogs WHERE author=?",
        (session["user"],)
    )

    blogs = cursor.fetchall()

    conn.close()

    return render_template("my_blogs.html", blogs=blogs)


# ==============================
# IMAGE ROUTE (IMPORTANT 🔥)
# ==============================
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


# ==============================
# LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    database = app.config.get("DATABASE", "tasks.db")
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]

    if title.strip():
        conn = get_db()

        conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )

        conn.commit()
        conn.close()

    return redirect("/")


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_db()

    conn.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_db()

    if request.method == "POST":

        title = request.form.get("title", "").strip()

        if title:
            conn.execute(
                "UPDATE tasks SET title = ? WHERE id = ?",
                (title, task_id)
            )

            conn.commit()

        conn.close()

        return redirect("/")

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", task=task)


@app.route("/health")
def health():
    return {"status": "ok"}


# Initialize the database when the application starts.
# This is required when running with Gunicorn on Render.
init_db()


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("water.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_ml INTEGER,
            day TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_goals (
            day TEXT PRIMARY KEY,
            goal_ml INTEGER
        )
    """)

    conn.commit()
    conn.close()


create_table()


# Home page
@app.route("/")
def home():

    today = str(date.today())

    conn = get_db()

    records = conn.execute(
        "SELECT * FROM water_intake WHERE day = ? ORDER BY id DESC",
        (today,)
    ).fetchall()

    result = conn.execute(
        "SELECT goal_ml FROM daily_goals WHERE day = ?",
        (today,)
    ).fetchone()

    goal = result["goal_ml"] if result else 2000

    total = sum(record["amount_ml"] for record in records)

    conn.close()

    progress = min((total / goal) * 100, 100)

    remaining = max(goal - total, 0)

    return render_template(
        "index.html",
        total=total,
        progress=progress,
        remaining=remaining,
        goal=goal,
        records=records
    )


# Set custom daily goal
@app.route("/set_goal", methods=["POST"])
def set_goal():

    try:
        goal = int(request.form["goal"])

        if 100 <= goal <= 10000:

            conn = get_db()

            conn.execute("""
                INSERT OR REPLACE INTO daily_goals
                (day, goal_ml)
                VALUES (?, ?)
            """, (str(date.today()), goal))

            conn.commit()
            conn.close()

    except (ValueError, KeyError):
        pass

    return redirect("/")


# Add water intake
@app.route("/add", methods=["POST"])
def add():

    try:
        amount = int(request.form["amount"])

        if 1 <= amount <= 5000:

            conn = get_db()

            conn.execute(
                "INSERT INTO water_intake (amount_ml, day) VALUES (?, ?)",
                (amount, str(date.today()))
            )

            conn.commit()
            conn.close()

    except (ValueError, KeyError):
        pass

    return redirect("/")


# Reset today's water records
@app.route("/reset", methods=["POST"])
def reset():

    conn = get_db()

    conn.execute(
        "DELETE FROM water_intake WHERE day = ?",
        (str(date.today()),)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

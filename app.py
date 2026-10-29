
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "phishaware.db"

SCENARIOS = [
    {
        "id": 1,
        "sender": "security@example.invalid",
        "subject": "Urgent: Verify your account immediately",
        "body": (
            "This training example uses urgent language "
            "to pressure the reader into acting quickly."
        ),
        "answer": "phishing",
        "reason": (
            "Urgency and pressure to verify an account are "
            "warning signs. Check through the official website."
        ),
    },
    {
        "id": 2,
        "sender": "updates@example.invalid",
        "subject": "Your weekly learning summary",
        "body": (
            "Your weekly training summary is ready. "
            "Open the training portal using your saved bookmark."
        ),
        "answer": "legitimate",
        "reason": (
            "This example recommends a known, bookmarked portal "
            "and does not ask for sensitive information."
        ),
    },
    {
        "id": 3,
        "sender": "payroll@example.invalid",
        "subject": "Unexpected payroll document",
        "body": (
            "An unexpected document request can be suspicious. "
            "Verify it with your payroll team through a known channel."
        ),
        "answer": "phishing",
        "reason": (
            "Unexpected document requests deserve verification. "
            "Sender details and context matter; the subject alone "
            "cannot prove a message is malicious."
        ),
    },
]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


@app.get("/")
def index():
    return render_template("index.html", scenarios=SCENARIOS)


@app.post("/submit")
def submit():
    score = 0
    feedback = []

    for scenario in SCENARIOS:
        choice = request.form.get(
            f"answer_{scenario['id']}", ""
        ).lower()

        correct = choice == scenario["answer"]

        if correct:
            score += 1

        feedback.append({
            "subject": scenario["subject"],
            "correct": correct,
            "selected": choice or "not answered",
            "answer": scenario["answer"],
            "reason": scenario["reason"],
        })

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO attempts (score, total, created_at)
            VALUES (?, ?, ?)
            """,
            (
                score,
                len(SCENARIOS),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    return render_template(
        "result.html",
        score=score,
        total=len(SCENARIOS),
        percentage=round(score / len(SCENARIOS) * 100),
        feedback=feedback,
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)

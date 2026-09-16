"""Data access helpers for quizzes, questions, and attempts."""
from datetime import datetime, timezone

from .db import get_db


def create_quiz(title, questions):
    """Create a quiz with its questions.

    questions: list of dicts, each with keys "text", "choices" (list of 4
    strings), and "correct_index" (0-3).
    Returns the new quiz's id.
    """
    db = get_db()
    cur = db.execute("INSERT INTO quiz (title) VALUES (?)", (title,))
    quiz_id = cur.lastrowid
    for q in questions:
        choices = q["choices"]
        db.execute(
            """INSERT INTO question
                   (quiz_id, text, choice_a, choice_b, choice_c, choice_d, correct_index)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (quiz_id, q["text"], choices[0], choices[1], choices[2], choices[3], q["correct_index"]),
        )
    db.commit()
    return quiz_id


def get_quiz(quiz_id):
    db = get_db()
    return db.execute("SELECT * FROM quiz WHERE id = ?", (quiz_id,)).fetchone()


def get_questions(quiz_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM question WHERE quiz_id = ? ORDER BY id", (quiz_id,)
    ).fetchall()


def list_quizzes_with_avg():
    """List all quizzes with attempt count and average score percentage."""
    db = get_db()
    return db.execute(
        """
        SELECT q.id AS id,
               q.title AS title,
               COUNT(a.id) AS attempt_count,
               AVG(CASE WHEN a.total > 0 THEN (a.score * 100.0 / a.total) END) AS avg_percentage
        FROM quiz q
        LEFT JOIN attempt a ON a.quiz_id = q.id
        GROUP BY q.id
        ORDER BY q.id
        """
    ).fetchall()


def record_attempt(quiz_id, score, total):
    db = get_db()
    taken_at = datetime.now(timezone.utc).isoformat()
    db.execute(
        "INSERT INTO attempt (quiz_id, score, total, taken_at) VALUES (?, ?, ?, ?)",
        (quiz_id, score, total, taken_at),
    )
    db.commit()


def score_submission(quiz_id, answers):
    """Score a quiz submission.

    answers: dict mapping question id -> selected choice index (int).
    Returns a dict with score, total, percentage, and a per-question
    breakdown of correctness.
    """
    questions = get_questions(quiz_id)
    total = len(questions)
    score = 0
    per_question = []
    for q in questions:
        qid = q["id"]
        selected = answers.get(qid)
        correct_index = q["correct_index"]
        is_correct = selected is not None and selected == correct_index
        if is_correct:
            score += 1
        per_question.append(
            {
                "question_id": qid,
                "text": q["text"],
                "choices": [q["choice_a"], q["choice_b"], q["choice_c"], q["choice_d"]],
                "selected_index": selected,
                "correct_index": correct_index,
                "is_correct": is_correct,
            }
        )
    percentage = (score / total * 100.0) if total else 0.0
    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "per_question": per_question,
    }

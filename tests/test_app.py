"""Unit tests for the Online Quiz Platform, using Flask's test client."""
import pytest

from app import create_app
from app.db import get_db


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app):
    return app.test_client()


def create_sample_quiz(client, title="Sample Quiz", n=2):
    """Create a quiz with n questions, each with correct answer = choice A (index 0)."""
    data = {
        "title": title,
        "q_text": [f"Question {i + 1}?" for i in range(n)],
        "choice_0": ["A"] * n,
        "choice_1": ["B"] * n,
        "choice_2": ["C"] * n,
        "choice_3": ["D"] * n,
        "correct": ["0"] * n,
    }
    return client.post("/quizzes/new", data=data)


def get_quiz_and_questions(app, title):
    with app.app_context():
        db = get_db()
        quiz = db.execute("SELECT * FROM quiz WHERE title = ?", (title,)).fetchone()
        questions = db.execute(
            "SELECT * FROM question WHERE quiz_id = ? ORDER BY id", (quiz["id"],)
        ).fetchall()
        return quiz["id"], [q["id"] for q in questions]


def test_create_quiz_persists_title_and_questions(client, app):
    resp = create_sample_quiz(client, title="My Quiz", n=3)

    assert resp.status_code == 302  # redirected to the take-quiz page

    with app.app_context():
        db = get_db()
        quiz = db.execute("SELECT * FROM quiz WHERE title = ?", ("My Quiz",)).fetchone()
        assert quiz is not None
        questions = db.execute(
            "SELECT * FROM question WHERE quiz_id = ?", (quiz["id"],)
        ).fetchall()
        assert len(questions) == 3


def test_take_quiz_and_get_correct_score(client, app):
    create_sample_quiz(client, title="Score Quiz", n=4)
    quiz_id, qids = get_quiz_and_questions(app, "Score Quiz")

    # Every correct answer is choice A (index 0).
    answer_data = {f"answer_{qid}": "0" for qid in qids}
    resp = client.post(f"/quizzes/{quiz_id}/take", data=answer_data)

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "4 / 4" in html
    assert "100.0%" in html


def test_per_question_correctness_is_accurate(client, app):
    create_sample_quiz(client, title="Mix Quiz", n=3)
    quiz_id, qids = get_quiz_and_questions(app, "Mix Quiz")

    # First question correct (0), the other two wrong (1).
    answer_data = {
        f"answer_{qids[0]}": "0",
        f"answer_{qids[1]}": "1",
        f"answer_{qids[2]}": "1",
    }
    resp = client.post(f"/quizzes/{quiz_id}/take", data=answer_data)
    assert resp.status_code == 200
    assert "1 / 3" in resp.get_data(as_text=True)

    with app.app_context():
        from app import models

        result = models.score_submission(
            quiz_id, {qids[0]: 0, qids[1]: 1, qids[2]: 1}
        )
    assert result["score"] == 1
    assert result["per_question"][0]["is_correct"] is True
    assert result["per_question"][1]["is_correct"] is False
    assert result["per_question"][2]["is_correct"] is False


def test_average_score_computed_across_multiple_attempts(client, app):
    create_sample_quiz(client, title="Avg Quiz", n=2)
    quiz_id, qids = get_quiz_and_questions(app, "Avg Quiz")

    # Attempt 1: both correct -> 100%
    client.post(
        f"/quizzes/{quiz_id}/take",
        data={f"answer_{qids[0]}": "0", f"answer_{qids[1]}": "0"},
    )
    # Attempt 2: one correct, one wrong -> 50%
    client.post(
        f"/quizzes/{quiz_id}/take",
        data={f"answer_{qids[0]}": "0", f"answer_{qids[1]}": "1"},
    )

    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    # Average of 100% and 50% is 75.0%
    assert "75.0%" in html


def test_invalid_submission_is_rejected(client, app):
    create_sample_quiz(client, title="Invalid Quiz", n=2)
    quiz_id, qids = get_quiz_and_questions(app, "Invalid Quiz")

    # Missing an answer for the second question.
    resp = client.post(f"/quizzes/{quiz_id}/take", data={f"answer_{qids[0]}": "0"})
    assert resp.status_code == 400

    with app.app_context():
        db = get_db()
        count = db.execute(
            "SELECT COUNT(*) AS c FROM attempt WHERE quiz_id = ?", (quiz_id,)
        ).fetchone()["c"]
    assert count == 0

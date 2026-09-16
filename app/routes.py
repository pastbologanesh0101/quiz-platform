"""HTTP routes for the Online Quiz Platform."""
from flask import Blueprint, abort, redirect, render_template, request, url_for

from . import models

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    quizzes = models.list_quizzes_with_avg()
    return render_template("index.html", quizzes=quizzes)


@bp.route("/quizzes/new", methods=["GET", "POST"])
def new_quiz():
    if request.method == "GET":
        return render_template("quiz_form.html", errors=None)

    title = request.form.get("title", "").strip()
    q_texts = request.form.getlist("q_text")
    choice_0 = request.form.getlist("choice_0")
    choice_1 = request.form.getlist("choice_1")
    choice_2 = request.form.getlist("choice_2")
    choice_3 = request.form.getlist("choice_3")
    corrects = request.form.getlist("correct")

    errors = []
    if not title:
        errors.append("A quiz title is required.")
    if not q_texts:
        errors.append("At least one question is required.")

    lengths = {len(q_texts), len(choice_0), len(choice_1), len(choice_2), len(choice_3), len(corrects)}
    if len(lengths) > 1:
        errors.append("Question fields are inconsistent; each question needs 4 choices and a correct answer.")

    questions = []
    if not errors:
        for i in range(len(q_texts)):
            text = q_texts[i].strip()
            choices = [
                choice_0[i].strip(),
                choice_1[i].strip(),
                choice_2[i].strip(),
                choice_3[i].strip(),
            ]
            try:
                correct_index = int(corrects[i])
            except (ValueError, IndexError):
                correct_index = -1

            if not text or any(not c for c in choices) or correct_index not in (0, 1, 2, 3):
                errors.append(f"Question {i + 1} is invalid: needs text, 4 non-empty choices, and a correct answer.")
                continue

            questions.append({"text": text, "choices": choices, "correct_index": correct_index})

    if errors:
        return render_template("quiz_form.html", errors=errors), 400

    quiz_id = models.create_quiz(title, questions)
    return redirect(url_for("main.take_quiz", quiz_id=quiz_id))


@bp.route("/quizzes/<int:quiz_id>/take", methods=["GET", "POST"])
def take_quiz(quiz_id):
    quiz = models.get_quiz(quiz_id)
    if quiz is None:
        abort(404)
    questions = models.get_questions(quiz_id)

    if request.method == "GET":
        return render_template("quiz_take.html", quiz=quiz, questions=questions, error=None)

    answers = {}
    for q in questions:
        raw = request.form.get(f"answer_{q['id']}")
        if raw is None or raw == "":
            return (
                render_template(
                    "quiz_take.html",
                    quiz=quiz,
                    questions=questions,
                    error="Please answer every question before submitting.",
                ),
                400,
            )
        try:
            selected = int(raw)
        except ValueError:
            selected = None

        if selected not in (0, 1, 2, 3):
            return (
                render_template(
                    "quiz_take.html",
                    quiz=quiz,
                    questions=questions,
                    error="Invalid answer submitted.",
                ),
                400,
            )
        answers[q["id"]] = selected

    result = models.score_submission(quiz_id, answers)
    models.record_attempt(quiz_id, result["score"], result["total"])
    return render_template("quiz_result.html", quiz=quiz, result=result)

# Online Quiz Platform

A small, self-contained Flask + SQLite web app for creating and taking
multiple-choice quizzes, with automatic scoring and attempt history.

## Features

- Create a quiz with any number of questions, each with 4 answer choices
  and one correct answer.
- Take a quiz: answer every question and submit in a single request.
- Get an instant scored result: correct count, percentage, and a
  per-question right/wrong breakdown with the correct answer shown for
  anything you missed.
- Home page lists every quiz along with the number of attempts and the
  **average score** across all attempts.
- Ships with a seeded "General Knowledge" quiz (10 questions) so there's
  something to try immediately.

## Tech

- Flask (app factory pattern via `create_app()`)
- SQLite (raw `sqlite3`, no ORM)
- Server-rendered Jinja2 templates + plain CSS (no JS framework, no build step)

## Project layout

```
app/
  __init__.py     # create_app() factory
  db.py           # schema + connection helper
  models.py       # quiz / question / attempt data access
  seed.py         # seeds the sample quiz on first run
  routes.py       # all HTTP routes
  templates/      # Jinja2 templates
  static/         # style.css
tests/
  test_app.py     # unit tests using Flask's test client
run.py            # dev server entrypoint
```

## Running it

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python run.py
```

Then open http://127.0.0.1:5000/ in your browser. On first run this
creates `instance/quiz.db` (SQLite file) seeded with a General Knowledge
quiz.

## Example usage

1. Visit `/` to see the list of quizzes (title, attempt count, average score).
2. Click "Take quiz" on **General Knowledge**, answer all 10 questions, and
   submit — you'll immediately see your score (e.g. `8 / 10 (80.0%)`) plus
   which questions you got right or wrong.
3. Click "+ New Quiz" to build your own quiz: give it a title, add one or
   more questions (text, 4 choices, and which one is correct), then submit
   to create it.
4. Take your new quiz a few times with different answers and check the
   home page — the average score column updates to reflect all attempts.

## Running the tests

```bash
pip install -r requirements.txt
python -m pytest
```

Tests use `create_app(testing=True)`, which points the app at an
in-memory SQLite database, so no files are touched and no dev server is
needed. Covered scenarios:

- Creating a quiz persists its title and all of its questions.
- Taking a quiz and answering everything correctly yields a 100% score.
- Per-question correctness (right/wrong) is reported accurately.
- The average score across multiple attempts is computed correctly.
- An incomplete/invalid submission is rejected (HTTP 400) and does not
  record an attempt.

## CI

`.github/workflows/tests.yml` runs the test suite on every push and pull
request against Python 3.11 and 3.12.

## License

MIT — see [LICENSE](LICENSE).

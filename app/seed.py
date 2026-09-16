"""Seed a sample general-knowledge quiz on first run."""

GENERAL_KNOWLEDGE_QUESTIONS = [
    {
        "text": "What is the capital of France?",
        "choices": ["Paris", "London", "Berlin", "Madrid"],
        "correct_index": 0,
    },
    {
        "text": "Which planet is known as the Red Planet?",
        "choices": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_index": 1,
    },
    {
        "text": "What is the largest ocean on Earth?",
        "choices": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "correct_index": 3,
    },
    {
        "text": "Who wrote the play 'Romeo and Juliet'?",
        "choices": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "correct_index": 1,
    },
    {
        "text": "What is the chemical symbol for gold?",
        "choices": ["Go", "Gd", "Au", "Ag"],
        "correct_index": 2,
    },
    {
        "text": "How many continents are there on Earth?",
        "choices": ["5", "6", "7", "8"],
        "correct_index": 2,
    },
    {
        "text": "What is the smallest prime number?",
        "choices": ["0", "1", "2", "3"],
        "correct_index": 2,
    },
    {
        "text": "Which country is home to the kangaroo?",
        "choices": ["South Africa", "Australia", "Brazil", "India"],
        "correct_index": 1,
    },
    {
        "text": "What gas do plants primarily absorb from the atmosphere?",
        "choices": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
        "correct_index": 2,
    },
    {
        "text": "In which year did the first man land on the Moon?",
        "choices": ["1965", "1969", "1972", "1959"],
        "correct_index": 1,
    },
]


def seed_if_empty(conn):
    """Insert the sample quiz if the database has no quizzes yet."""
    count = conn.execute("SELECT COUNT(*) AS c FROM quiz").fetchone()["c"]
    if count > 0:
        return

    cur = conn.execute("INSERT INTO quiz (title) VALUES (?)", ("General Knowledge",))
    quiz_id = cur.lastrowid
    for q in GENERAL_KNOWLEDGE_QUESTIONS:
        choices = q["choices"]
        conn.execute(
            """INSERT INTO question
                   (quiz_id, text, choice_a, choice_b, choice_c, choice_d, correct_index)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (quiz_id, q["text"], choices[0], choices[1], choices[2], choices[3], q["correct_index"]),
        )
    conn.commit()

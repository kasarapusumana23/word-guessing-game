from flask import Flask, render_template, request, session, redirect, url_for
import random
import os

app = Flask(__name__)
app.secret_key = "secret123"

# 📁 Base path (for files)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 Load words
def load_words():
    words = []
    with open(os.path.join(BASE_DIR, "words.txt"), "r") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                words.append(parts[1])
    return words

words = load_words()

# 🔹 Start game
def start_game():
    word = random.choice(words)
    session["word"] = word
    session["guessed"] = ["_"] * len(word)
    session["attempts"] = 6
    session["score"] = 0
    session["used"] = []

# 🔹 Save score
def save_score(score):
    with open(os.path.join(BASE_DIR, "scores.txt"), "a") as f:
        f.write(str(score) + "\n")

# 🔹 Get leaderboard
def get_top_scores():
    try:
        with open(os.path.join(BASE_DIR, "scores.txt"), "r") as f:
            scores = [int(line.strip()) for line in f if line.strip().isdigit()]
        scores.sort(reverse=True)
        return scores[:5]
    except:
        return []

# 🔹 MAIN ROUTE (VERY IMPORTANT)
@app.route("/", methods=["GET", "POST"])
def index():
    if "word" not in session:
        start_game()

    message = ""

    if request.method == "POST":
        guess = request.form.get("guess", "").lower()

        # 🔁 Restart
        if guess == "restart":
            start_game()
            return redirect(url_for("index"))

        # 💡 Hint
        elif guess == "hint":
            hidden = [i for i in range(len(session["word"])) if session["guessed"][i] == "_"]
            if hidden:
                idx = random.choice(hidden)
                letter = session["word"][idx]

                for i in range(len(session["word"])):
                    if session["word"][i] == letter:
                        session["guessed"][i] = letter

                session["score"] -= 2
                message = f"Hint: {letter}"

        # 🔁 Already guessed
        elif guess in session["used"]:
            message = "Already guessed!"

        # ✅ Valid input
        elif len(guess) == 1 and guess.isalpha():
            session["used"].append(guess)

            if guess in session["word"]:
                for i in range(len(session["word"])):
                    if session["word"][i] == guess:
                        session["guessed"][i] = guess

                session["score"] += 2
                message = "Correct!"
            else:
                session["attempts"] -= 1
                session["score"] -= 1
                message = "Wrong!"

        else:
            message = "Invalid input"

    # 🎯 Win/Lose
    win = "_" not in session["guessed"]
    lose = session["attempts"] == 0

    # 🏆 Save score
    if win or lose:
        save_score(session["score"])

    return render_template(
        "index.html",
        word=" ".join(session["guessed"]),
        attempts=session["attempts"],
        score=session["score"],
        used=session["used"],
        message=message,
        win=win,
        lose=lose,
        real_word=session["word"],
        top_scores=get_top_scores()
    )

# 🔹 Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

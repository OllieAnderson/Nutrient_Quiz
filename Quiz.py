
import csv
import random
from pathlib import Path


# File locations
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_DIR / "Database.csv"


def load_questions():
    """Import questions from CSV."""

    questions = []

    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "Answer", "Question", "Group_1", "Group_2", "Notes"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "The CSV must contain these columns: "
                "Answer, Question, Group_1, Group_2, Notes"
            )

        for row in reader:
            group1 = [
                group.strip()
                for group in (row["Group_1"] or "").split(";")
                if group.strip()
            ]

            group2 = [
                group.strip()
                for group in (row["Group_2"] or "").split(";")
                if group.strip()
            ]

            questions.append({
                "Answer": row["Answer"].strip(),
                "Question": row["Question"].strip(),
                "Group_1": group1,
                "Group_2": group2,
                "Notes": row["Notes"].strip()
            })

    return questions


questions = load_questions()


def clear_console():
    """Clear the terminal screen."""
    import os
    os.system("cls" if os.name == "nt" else "clear")


def select_categories(categories, title):
    """Allow selection of multiple categories."""

    categories = sorted(categories)

    while True:
        clear_console()

        print(f"=== {title} ===")
        print("Enter one or more numbers separated by commas.")
        print("A. All")
        print()

        for number, category in enumerate(categories, start=1):
            print(f"{number}. {category}")

        print("\nQ. Quit")

        choice = input("\nYour selection: ").strip().lower()

        if choice == "q":
            return None

        if choice == "a":
            return set(categories)

        try:
            selections = [
                int(number.strip())
                for number in choice.split(",")
            ]
        except ValueError:
            print("\nInvalid selection.")
            input("Press Enter to try again...")
            continue

        if (
            not selections
            or len(selections) != len(set(selections))
            or any(number < 1 or number > len(categories)
                   for number in selections)
        ):
            print("\nInvalid selection.")
            input("Press Enter to try again...")
            continue

        return {
            categories[number - 1]
            for number in selections
        }


def select_questions(questions):
    """Two-stage selection of Group_1 and Group_2."""

    # First selection: Group_1
    group1_categories = {
        group
        for question in questions
        for group in question["Group_1"]
    }

    selected_group1 = select_categories(
        group1_categories,
        "Select Group_1"
    )

    if selected_group1 is None:
        return None

    # Filter questions using Group_1.
    group1_questions = [
        question
        for question in questions
        if any(
            group in selected_group1
            for group in question["Group_1"]
        )
    ]

    if len(group1_questions) < 4:
        print("\nFewer than four questions match Group_1.")
        input("Press Enter to restart...")
        return select_questions(questions)

    # Second selection: Group_2
    group2_categories = {
        group
        for question in group1_questions
        for group in question["Group_2"]
    }

    selected_group2 = select_categories(
        group2_categories,
        "Select Group_2"
    )

    if selected_group2 is None:
        return None

    # Filter questions using Group_2.
    selected_questions = [
        question
        for question in group1_questions
        if any(
            group in selected_group2
            for group in question["Group_2"]
        )
    ]

    if len(selected_questions) < 4:
        print("\nFewer than four questions match both selections.")
        input("Press Enter to restart...")
        return select_questions(questions)

    return selected_questions


def ask_question(question, quiz_questions):
    """Ask one multiple-choice question."""

    clear_console()

    # Choose three incorrect answers.
    other_questions = [
        item for item in quiz_questions
        if item["Answer"] != question["Answer"]
    ]

    wrong_answers = random.sample(other_questions, 3)

    options = wrong_answers + [question]
    random.shuffle(options)

    print(question["Question"])
    print()

    for number, option in enumerate(options, start=1):
        print(f"{number}. {option['Answer']}")

    while True:
        answer = input("\nYour answer (1-4, or q to quit): ")
        answer = answer.strip().lower()

        if answer == "q":
            return None

        if answer in ("1", "2", "3", "4"):
            break

        print("Please enter 1, 2, 3, 4, or q.")

    selected = options[int(answer) - 1]

    clear_console()

    if selected["Answer"] == question["Answer"]:
        print("Correct!")
        correct = True
    else:
        print(f"Not quite. The answer is {question['Answer']}.")
        correct = False

    print(f"Group_1: {', '.join(question['Group_1']) or 'None'}")
    print(f"Group_2: {', '.join(question['Group_2']) or 'None'}")
    print(f"Note: {question['Notes']}")

    return correct


def run_quiz():
    """Run the quiz."""

    if len(questions) < 4:
        print("The database needs at least four questions.")
        return

    selected_questions = select_questions(questions)

    if selected_questions is None:
        print("Quiz cancelled.")
        return

    score = 0
    questions_asked = 0

    available_questions = selected_questions.copy()

    clear_console()

    print("=== Quiz ===")
    print(f"Questions selected: {len(selected_questions)}")
    print("Correctly answered questions will be removed.")
    print("Enter q at any question to finish.")

    while available_questions:
        question = random.choice(available_questions)

        result = ask_question(question, selected_questions)

        if result is None:
            break

        questions_asked += 1

        if result:
            score += 1
            available_questions.remove(question)

            print(f"Correct! {len(available_questions)} remaining.")
        else:
            print(f"\n{len(available_questions)} questions remaining.")

        print(f"Score: {score}/{questions_asked}")

        input("\nPress Enter to continue...")
        clear_console()

    clear_console()

    print("=== Quiz Finished ===")
    print(f"Correct answers: {score}/{questions_asked}")

    if questions_asked:
        percentage = score / questions_asked * 100
        print(f"Accuracy: {percentage:.1f}%")

    if not available_questions:
        print("\nCongratulations! You answered every question correctly.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    run_quiz()

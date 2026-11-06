import json
import os

from generator import generate_lesson
from evaluator import evaluate_lesson
from memory import update_memory, get_memory_context


TOPIC = "Introduction to RAG"
MAX_RETRIES = 2

OUTPUT_DIR = "outputs"
FINAL_LESSON_FILE = os.path.join(
    OUTPUT_DIR, "final_lesson.md"
)
REJECTION_LOG_FILE = os.path.join(
    OUTPUT_DIR, "rejection_log.json"
)
REJECTED_LESSON_FILE = os.path.join(
    OUTPUT_DIR, "rejected_lesson.md"
)


def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def run_agent():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n===================================")
    print(" SELF-EVALUATING AI LESSON AGENT")
    print("===================================")

    print(f"\nTopic: {TOPIC}")
    print("Starting lesson generation...\n")

    feedback = []
    rejection_log = []
    lesson = None

    memory_context = get_memory_context()

    for attempt in range(1, MAX_RETRIES + 2):

        print(f"\n--- Attempt {attempt} ---")

        # STEP 1: GENERATE
        print("Generating lesson...")

        lesson = generate_lesson(
            topic=TOPIC,
            feedback=feedback,
            memory_context=memory_context
        )

        # STEP 2: EVALUATE
        print("Evaluating lesson...")

        evaluation = evaluate_lesson(lesson)

        result = evaluation["overall_result"]

        print("\nEvaluation results:")

        for check in [
            "accuracy",
            "beginner_friendly",
            "examples",
            "jargon_explanation",
            "completeness",
            "teaching_flow"
        ]:
            print(f"{check}: {evaluation[check]}")

        print(f"\nOverall result: {result}")

        # STEP 3: SAVE MEMORY
        changes = (
            "Initial lesson generation."
            if attempt == 1
            else "Regenerated using previous evaluator feedback."
        )

        update_memory(
            topic=TOPIC,
            attempt=attempt,
            evaluation=evaluation,
            changes=changes
        )

        # STEP 4: HANDLE PASS
        if result == "PASS":

            with open(
                FINAL_LESSON_FILE,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(lesson)

            if os.path.exists(REJECTED_LESSON_FILE):
                os.remove(REJECTED_LESSON_FILE)

            save_json(rejection_log, REJECTION_LOG_FILE)

            print("\n===================================")
            print(" SUCCESS: LESSON APPROVED!")
            print("===================================")

            print(f"Final lesson: {FINAL_LESSON_FILE}")
            print(f"Rejection log: {REJECTION_LOG_FILE}")

            return True

        # STEP 5: HANDLE FAILURE
        print("\nLesson rejected.")

        failure_record = {
            "attempt": attempt,
            "result": "FAIL",
            "failed_checks": [
                check
                for check in [
                    "accuracy",
                    "beginner_friendly",
                    "examples",
                    "jargon_explanation",
                    "completeness",
                    "teaching_flow"
                ]
                if evaluation[check] == "FAIL"
            ],
            "feedback": evaluation["feedback"],
            "changes_on_next_retry": (
                "Regenerate the lesson using the feedback."
                if attempt <= MAX_RETRIES
                else "No retries remaining."
            )
        }

        rejection_log.append(failure_record)

        save_json(rejection_log, REJECTION_LOG_FILE)

        feedback = evaluation["feedback"]

        if attempt <= MAX_RETRIES:
            print("\nFeedback for regeneration:")

            for item in feedback:
                print(f"- {item}")

            print("\nPreparing next attempt...")

    # STEP 6: MAXIMUM RETRIES REACHED
    with open(
        REJECTED_LESSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(lesson or "No lesson was generated.")

    if os.path.exists(FINAL_LESSON_FILE):
        os.remove(FINAL_LESSON_FILE)

    save_json(rejection_log, REJECTION_LOG_FILE)

    print("\n===================================")
    print(" LESSON REJECTED")
    print(" Maximum retries reached.")
    print("===================================")

    print(f"Rejection log: {REJECTION_LOG_FILE}")
    print(f"Rejected lesson: {REJECTED_LESSON_FILE}")

    return False


if __name__ == "__main__":
    run_agent()

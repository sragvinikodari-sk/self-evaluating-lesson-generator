
import json
import os
from datetime import datetime, timezone

MEMORY_DIR = "memory"
MEMORY_FILE = os.path.join(
    MEMORY_DIR, "evaluation_history.json"
)


def load_memory():
    """Load previous evaluation history."""

    os.makedirs(MEMORY_DIR, exist_ok=True)

    if not os.path.exists(MEMORY_FILE):
        return {
            "total_runs": 0,
            "common_failures": [],
            "successful_improvements": [],
            "history": []
        }

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        raise ValueError(
            "Memory file could not be read. "
            "Check evaluation_history.json."
        )


def save_memory(memory):
    """Save memory permanently between program runs."""

    os.makedirs(MEMORY_DIR, exist_ok=True)

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)


def update_memory(topic, attempt, evaluation, changes=""):
    """Remember evaluation failures and improvements."""

    memory = load_memory()

    memory["total_runs"] += 1

    failed_checks = [
        check
        for check in [
            "accuracy",
            "beginner_friendly",
            "examples",
            "jargon_explanation",
            "completeness",
            "teaching_flow"
        ]
        if evaluation.get(check) == "FAIL"
    ]

    for failure in failed_checks:
        if failure not in memory["common_failures"]:
            memory["common_failures"].append(failure)

    if evaluation.get("overall_result") == "PASS":
        if changes:
            memory["successful_improvements"].append(changes)

    record = {
        "topic": topic,
        "attempt": attempt,
        "date": datetime.now(timezone.utc).isoformat(),
        "failed_checks": failed_checks,
        "feedback": evaluation.get("feedback", []),
        "changes": changes,
        "result": evaluation.get("overall_result", "FAIL")
    }

    memory["history"].append(record)

    save_memory(memory)

    return memory


def get_memory_context():
    """Prepare useful previous learning for the generator."""

    memory = load_memory()

    if not memory["history"]:
        return "No previous evaluation history. This is the first run."

    context = {
        "previous_failures": memory["common_failures"],
        "successful_improvements": memory[
            "successful_improvements"
        ],
        "recent_history": memory["history"][-5:]
    }

    return json.dumps(context, indent=2)

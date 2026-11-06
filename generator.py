
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def generate_lesson(topic, feedback=None, memory_context=None):

    feedback = feedback or []
    memory_context = memory_context or ""

    prompt = f"""
You are an expert AI educational content creator.

Your task is to teach a beginner about the following topic:

TOPIC: {topic}

TARGET LEARNER:
An Indian student who has completed 12th grade.
The student has no previous knowledge of this topic.
Use simple English and short sentences.

LESSON REQUIREMENTS:

1. Explain what the topic means.
2. Explain why it is important.
3. Explain how it works step by step.
4. Include a simple real-life example.
5. Explain important technical words.
6. Include advantages and limitations.
7. Compare it with related concepts where useful.
8. Include a short summary.
9. Add five practice questions with answers.

For RAG, make sure to explain:
- Retrieval-Augmented Generation
- Large Language Models (LLMs)
- Documents and knowledge sources
- Embeddings
- Vector databases
- Retrieval
- Context
- Generation

ACCURACY RULES:
- Do not invent technical facts.
- Explain concepts correctly.
- Do not leave technical terms unexplained.
- Use clear and beginner-friendly examples.

PREVIOUS EVALUATOR FEEDBACK:
{feedback}

PAST LEARNING FROM MEMORY:
{memory_context}

Improve the lesson using the feedback.
Do not repeat previous mistakes.

Return a complete standalone lesson in Markdown.
Do not include your internal reasoning.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError("The AI returned an empty lesson.")

    return response.text

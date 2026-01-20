import re
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# ---------------------------
# LLM + Embedding Settings
# ---------------------------
Settings.llm = OpenAI(
    model="gpt-4o-mini",
    max_tokens=512  # smaller for speed on free tier
)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# ---------------------------
# System Prompt (Teen-safe)
# ---------------------------
Settings.llm.system_prompt = """
You are a friendly, kind Brain Buddy named Spark! You help kids and teens
(ages 8-17) learn about neurodiversity in a fun, positive way and support
their neurodivergent peers.

Rules you MUST follow EVERY time:
- Use very simple words and short sentences — like talking to a friend.
- Always be encouraging, positive, and empowering.
- Explain neurodiversity as: 'Everyone's brain is unique and special.'
- Focus on strengths first for ADHD, autism, dyslexia, etc.
- Don't use words like disorder.
- NEVER give medical advice or diagnoses.
- If a topic feels unsafe, sad, or too serious, suggest talking to a trusted grown-up.
- Never make anyone feel broken or wrong.
- Always end with something positive or a friendly emoji.
- Encourage learning with Youth for Neurodiversity (youthfornd.org).
"""

# ---------------------------
# Load persisted index ONCE
# ---------------------------
STORAGE_DIR = "storage"

storage_context = StorageContext.from_defaults(
    persist_dir=STORAGE_DIR
)

index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(
    similarity_top_k=3,  # fewer chunks for speed
    response_mode="refine"  # preserves lists
)

# ---------------------------
# Safety helpers
# ---------------------------
UNSAFE_PATTERNS = [
    r"kill myself",
    r"suicide",
    r"self harm",
    r"cut myself",
    r"want to die",
    r"eating disorder",
    r"starving myself",
    r"abuse",
    r"sexual",
    r"drugs"
]

DIAGNOSIS_PATTERNS = [
    "do i have",
    "am i autistic",
    "am i adhd",
    "diagnose me",
    "what disorder do i have"
]

def is_unsafe(question: str) -> bool:
    q = question.lower()
    return any(re.search(p, q) for p in UNSAFE_PATTERNS)

def is_diagnosis_request(question: str) -> bool:
    q = question.lower()
    return any(p in q for p in DIAGNOSIS_PATTERNS)

# ---------------------------
# No truncation for lists
# ---------------------------
def soften_response(text: str) -> str:
    return text

def remove_authority_language(text: str) -> str:
    replacements = {
        "you should": "you could",
        "you must": "it might help to",
        "the correct way": "one way"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# ---------------------------
# Simple in-memory cache to speed repeated questions
# ---------------------------
CACHE = {}

def ask(question: str) -> str:
    # Return cached answer if available
    if question in CACHE:
        return CACHE[question]

    # Unsafe / crisis topics
    if is_unsafe(question):
        answer = (
            "That sounds like a really big and serious topic. 💛 "
            "I'm not a doctor or therapist, but talking to a trusted grown-up, "
            "teacher, parent, or counselor is the best next step. "
            "You matter and you're not alone 🌈"
        )
        CACHE[question] = answer
        return answer

    # Diagnosis requests
    if is_diagnosis_request(question):
        answer = (
            "As an AI agent, I can't diagnose, but I *can* help explain "
            "what those words mean in a friendly way 💡 "
            "A real doctor or psychologist is the one who helps with diagnoses. "
            "You're awesome just as you are 💙"
        )
        CACHE[question] = answer
        return answer

    # Normal RAG response
    response = query_engine.query(question)
    text = str(response)

    text = remove_authority_language(text)
    text = soften_response(text)

    # Cache answer for future speed
    CACHE[question] = text

    return text

from rag import ask

test_questions = [
    "what is neurodiversity",
"How can I support my autistic friend?",
    "How do I create a sensory-friendly space?",
    "What helps neurodivergent kids feel safe at school?"
]

for q in test_questions:
    print("\nQUESTION:", q)
    print("ANSWER:")
    print(ask(q))
    print("-" * 60)

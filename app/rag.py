import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "dsa_knowledge"

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not configured")

groq_client = Groq(api_key=api_key)
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_or_create_collection(COLLECTION_NAME)


def retrieve(question: str, top_k: int = 3) -> str:
    document_count = collection.count()
    if document_count == 0:
        raise RuntimeError(
            "The DSA knowledge collection is empty. Run `python app/ingest.py` first."
        )

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, document_count),
    )

    retrieved_docs = results.get("documents", [[]])[0]
    context = " ".join(retrieved_docs)
    return context


def generate_answer(question: str, context: str) -> str:
    prompt = f"""Use only the context below to answer the question.
If the context does not contain the answer, say "I don't know".

Context:
{context}

Question:
{question}"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{
            "role": "system",
            "content": "You are an interview preparation assistant. Answer only from the provided context. If the context does not contain the answer, say: I don't know."
        }, 
        {
            "role": "user",
            "content": prompt
        }],
        temperature=0,
    )

    return response.choices[0].message.content or "I don't know"


def ask(question: str) -> str:
    context = retrieve(question)
    answer = generate_answer(question, context)
    return answer


if __name__ == "__main__":
    question = "What is a Queue traversal in a binary tree?"
    answer = ask(question)
    print(f"Question: {question}\nAnswer: {answer}")

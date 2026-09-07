from pathlib import Path

import chromadb
from dotenv import load_dotenv 

load_dotenv()

collection_name = "dsa_knowledge"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dsa.txt"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_or_create_collection(collection_name)

def load_text_file(file_path: str | Path) -> str:
    """
    Load the content of a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the text file.
    """
    return Path(file_path).read_text(encoding="utf-8")


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20):

    words = text.split()
    print("words")
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def ingest_data(file_path: str | Path, chunk_size: int = 100, overlap: int = 20):
    """
    Ingest data from a text file into the Chroma collection.

    Args:
        file_path (str): The path to the text file.
        chunk_size (int): The size of each chunk.
        overlap (int): The overlap between chunks.
    """
    file_path = Path(file_path)
    text = load_text_file(file_path)
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    collection.upsert(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {
                "source": str(file_path),
                "topic": "Data Structures and Algorithms",
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
    )


if __name__ == "__main__":
    ingest_data(DATA_FILE, chunk_size=100, overlap=20)

# print(f"Total chunks created: {len(chunks)}")

# for chunk in chunks[:3]:  # Print the first 3 chunks for verification
#     print(f"Chunk: {chunk}\n")

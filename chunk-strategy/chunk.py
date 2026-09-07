from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dsa.txt"

def load_text_from_file(file_path: str | Path) -> str:
    """
    Load the content of a text file.

    Args:
        file_path (str | Path): The path to the text file.

    Returns:
        str: The content of the text file.
    """
    return Path(file_path).read_text(encoding="utf-8")

def chunk_text(text: str, chunk_size: int = 100, chunk_overlap:int = 20) -> list[str]:
    """
    Splits the input text into chunks of specified size with overlap.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of overlapping characters between chunks.

    Returns:
        list[str]: A list of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)

text = load_text_from_file(DATA_FILE) 

chunks = chunk_text(text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}\n")
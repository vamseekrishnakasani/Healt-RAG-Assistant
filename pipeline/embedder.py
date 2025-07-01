# health_rag/pipeline/embedder.py

import json
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/combined_health_data.json")
VECTORSTORE_PATH = os.path.join(BASE_DIR, "../vectorstore")

def embed_combined_data():
    # Load JSON data
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to LangChain Documents
    documents = []
    for item in data:
        title = item.get("title", "")
        content = item.get("content", "")
        metadata = {
            "url": item.get("url", ""),
            "source": item.get("source", ""),
            "category": item.get("category", "")
        }
        full_text = f"{title}\n\n{content}"
        documents.append(Document(page_content=full_text, metadata=metadata))

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Embedding model
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create FAISS vectorstore
    vectorstore = FAISS.from_documents(chunks, embedder)

    # Save vectorstore
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"Vectorstore saved at: {VECTORSTORE_PATH}")

if __name__ == "__main__":
    embed_combined_data()
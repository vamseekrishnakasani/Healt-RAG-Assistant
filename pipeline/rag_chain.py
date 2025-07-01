"""
Local RAG pipeline using FAISS, HuggingFaceEmbeddings, and LlamaCpp.
Includes proper log suppression, hallucination-resistant prompt, and cleaned-up output.
"""

import os
import sys
import warnings
import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pipeline.llm import load_local_llm

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, '..'))

# Suppress native stderr logs from LlamaCpp and other C++ libraries
def suppress_native_logs():
    try:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 2)  # Only stderr
    except Exception:
        pass

suppress_native_logs()

# Suppress Python warnings and reduce log noise from key libraries
warnings.filterwarnings("ignore")
for name in ["langchain", "langchain_community", "transformers", "urllib3"]:
    logging.getLogger(name).setLevel(logging.CRITICAL)

# Set up model and vectorstore configuration paths
VECTORSTORE_PATH = os.path.join(base_dir, "../vectorstore")
GGUF_MODEL_PATH = os.path.join(base_dir, "../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")

# Strict prompt for medical assistant grounded only on provided context
prompt_template = PromptTemplate.from_template("""
You are a trusted and professional **health assistant**. Your job is to answer only questions related to health or medicine, using only the provided context.

Use the examples below as a guide to your behavior:
- Q: hi  
  A: Hello! 👋 I'm your Health Assistant. Feel free to ask me anything about health or medicine.
- Q: what's the weather like in New York?  
  A: I'm only able to answer health-related questions.
- Q: Who is the president of the US?  
  A: I'm only able to answer health-related questions.
- Q: What are the symptoms of diabetes?  
  A: [A factual answer, based strictly on the context.]

If the answer is not clearly found in the context, respond with:
"I don't know based on the provided sources."

### Context:
{context}

### Question:
{question}

### Answer:
""")

# Load vectorstore and embedding model for document retrieval
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Load local LLM (Misral or compatible GGUF model) with limited tokens and context
llm = load_local_llm(GGUF_MODEL_PATH)

# Construct the Retrieval-Augmented Generation QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# Inference function that handles question processing and structured output
def run_query(question: str):
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    if question.strip().lower() in greetings:
        return {
            "question": question,
            "response": "Hello! 👋 I'm your Health Assistant. You can ask me anything related to medical topics or healthcare.",
            "sources": []
        }
    result = qa_chain.invoke({"query": question})
    
    # Extract context from source documents
    source_docs = result["source_documents"]
    sources = list({doc.metadata.get("source", "unknown") for doc in source_docs})

    response = result["result"].strip()

    return {
        "question": question,
        "response": response,
        "sources": sources
    }
# CLI entry point for local testing and debugging
if __name__ == "__main__":
    output = run_query("what is the weather like in New York City today?")
    print(f"\nQuestion: {output['question']}\n")
    print("Response:")
    print(output["response"])
    print("\nSources:")
    for src in output["sources"]:
        print(f" - {src}")
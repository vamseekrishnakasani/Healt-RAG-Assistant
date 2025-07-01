


# Health RAG Assistant

A **locally hosted RAG (Retrieval-Augmented Generation) system** that answers medical questions using grounded and curated health-related documents. The assistant uses **FAISS**, **HuggingFace embeddings**, and a local **Mistral GGUF model** (via `llama-cpp`) to provide secure, hallucination-resistant responses. This project is designed for **offline, privacy-conscious use cases** where accurate medical information is critical.

---

## Project Structure

```
health_rag/
├── backend/
│   └── main.py               # FastAPI server that exposes the `/query` endpoint
├── pipeline/
│   ├── rag_chain.py          # Core RAG logic: embedding retrieval + LLM inference
│   ├── llm.py                # Loads the local Mistral or TinyLlama GGUF model
│   └── query_interface.py    # Interface logic (currently minimal)
├── streamlit_app/
│   └── fronted_ui.py         # Chat-based web interface using Streamlit
├── vectorstore/
│   └── (FAISS index)         # Contains pre-embedded chunks of health documents
├── models/
│   └── mistral-7b*.gguf      # Local quantized GGUF model (e.g., Mistral 7B Q4_K_M)
└── Readme.md                 # Project documentation
```

---

## 🚀 Features

- **Chat Interface** — Responsive chat UI (mobile-ready) that mimics WhatsApp-style assistant layout.
- **Contextual Responses** — Uses document retrieval to provide answers grounded in source material.
- **Local LLM Inference** — Runs Mistral (or other GGUF models) locally using llama-cpp for privacy.
- **Health-Specific Prompting** — Carefully designed prompts ensure assistant only responds when contextually grounded.
- **Use Case** — Acts as a clinical assistant with fact-based, hallucination-free answers.

---

## How It Works

1. **User asks a medical question** via the Streamlit UI.
2. The backend (`main.py`) sends the question to the `run_query()` function in `rag_chain.py`.
3. `rag_chain.py`:
   - Retrieves the top 3 relevant document chunks from the FAISS vectorstore.
   - Feeds the context + question into the prompt template.
   - Calls `load_local_llm()` to generate a grounded response using the local model.
4. Returns structured output with:
   - Answer
   - Sources used
5. The frontend displays the chat, including loading animation, sources, and user/assistant messages.

---

## Prompt Template

The model uses a **hallucination-resistant medical prompt** like:

```
You are a professional medical assistant. Your job is to answer **only** if the answer exists clearly in the given context. Do **not** guess, create, or assume any facts.

If the answer cannot be confidently found from the context, respond with:
"I don't know based on the provided sources."

### Context:
{context}

### Question:
{question}

### Answer (in a short paragraph, no bullet points):
```

---

## How to Run the App

1. **Set up the environment:**
   ```bash
   python3.10 -m venv rag_venv
   source rag_venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start the backend API:**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Run the Streamlit UI:**
   ```bash
   streamlit run streamlit_app/fronted_ui.py
   ```

4. **Ask Questions!**

---

## Notes

- All embeddings are generated using: `all-MiniLM-L6-v2`.
- Sources are always shown to increase user trust.
- Query interface (optional) can be used to modularize interaction logic.

---

## Frontend UI Highlights

- Fully responsive chat window.
- User messages on right; assistant on left.
- Mobile-friendly input box floats above keyboard on typing.
- Shows spinning animation (`...`) before response.

---

## Example Output

```
Q: What are the symptoms of ionizing radiation?

Answer:
The symptoms include nausea, fatigue, vomiting, and hair loss. Severe exposure can lead to internal damage and is often fatal.

Sources:
- Mayo Clinic
- WHO
```

---

## Future Enhancements

-  Streaming token output (simulate real-time typing).
-  Few-shot prompting for better greetings and context switching.
-  PDF upload for custom health documents.
-  Multi-language support.

---

## Author

Developed by **Vamsee Krishna Kasani**  
---
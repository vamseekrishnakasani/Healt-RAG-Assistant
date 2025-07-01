from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pipeline.rag_chain import run_query  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or just Streamlit domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def get_answer(request: Request):
    body = await request.json()
    result = run_query(body["question"])

    return {
        "question": body["question"],
        "response": result["response"],
        "sources": result["sources"]
    }
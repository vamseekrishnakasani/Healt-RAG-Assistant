from langchain_community.llms import LlamaCpp

def load_local_llm(model_path: str, temperature: float = 0.1, max_tokens: int = 1024, n_ctx: int = 4096, n_threads: int = 4):
    return LlamaCpp(
        model_path=model_path,
        temperature=temperature,
        max_tokens=max_tokens,
        n_ctx=n_ctx,
        n_threads=n_threads,
        top_p=0.95,
        repeat_penalty=1.1,
        stop=["\n\n", "\nSources:", "Answer:", "Context:"],
        verbose=False
    )

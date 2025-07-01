import streamlit as st
import requests

st.set_page_config(page_title="Health RAG Assistant", layout="centered")

# Custom CSS for clean and responsive styling
st.markdown("""
    <style>
    .main {
        background: #f7f9fb;
        font-family: 'Segoe UI', sans-serif;
        padding: 2rem;
        padding-bottom: 5rem;
    }
    .title {
        text-align: center;
        font-size: 2.75rem;
        font-weight: bold;
        background: linear-gradient(to right, #27ae60, #2980b9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -1rem;
    }
    .response-box {
        background-color: #f0f0f0;
        color: #111;
        padding: 1.25rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-top: 1rem;
    }
    .sources {
        font-size: 0.9rem;
        color: #333;
        margin-top: 0.5rem;
    }
    .custom-chat-input {
        margin-bottom: 2rem;
        padding: 0.75rem 1rem;
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        background-color: #f9f9f9;
        color: #000;
    }
    @media screen and (max-width: 768px) {
        .title {
            font-size: 2rem;
        }
        .main {
            padding: 1rem;
            padding-bottom: 6rem;
        }
        .response-box, .sources {
            font-size: 1rem;
        }
        input[type="text"] {
            font-size: 1rem;
            width: 100%;
            box-sizing: border-box;
        }
        .stChatInputContainer {
            position: fixed !important;
            bottom: calc(env(keyboard-inset-height, 0) + 1rem);
            width: 100%;
            max-width: 100vw;
            background-color: #ffffff;
            padding: 0.75rem 1rem;
            z-index: 9999;
            box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.1);
            transition: bottom 0.3s ease;
            box-sizing: border-box;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Health RAG Assistant</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("### Ask a medical question:")

user_input = st.chat_input("Type your question here...", key="chat_input")

if user_input:
    # Show user message immediately
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    # Show placeholder for assistant response
    st.session_state.chat_history.append({"role": "assistant", "text": "Typing...", "sources": []})
    
    with st.spinner("Analyzing..."):
        res = requests.post("http://localhost:8000/query", json={"question": user_input})
        if res.ok:
            data = res.json()
            st.session_state.chat_history[-1] = {"role": "assistant", "text": data['response'], "sources": data["sources"]}
        else:
            st.error("Something went wrong.")

# Apply custom styling to chat input box (injected separately to control spacing)
st.markdown("""
    <style>
    .stChatInputContainer {
        margin-bottom: 2rem !important;
        background-color: #ffffff;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'''
            <div style="text-align: right; background-color: #dff9fb; color: #000; padding: 0.75rem 1rem; border-radius: 0.5rem; margin: 0.5rem 0 0.5rem auto; max-width: 75%;">
                {msg["text"]}
            </div>
        ''', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'''
            <div style="text-align: left; background-color: #f1f2f6; color: #000; padding: 0.75rem 1rem; border-radius: 0.5rem; margin: 0.5rem auto 0.5rem 0; max-width: 75%;">
                {msg["text"]}
            </div>
        ''', unsafe_allow_html=True)
        if msg.get("sources"):
            st.markdown(f'''
                <div class="sources" style="text-align: left; padding-left: 1rem; max-width: 75%;">
                    <strong>Sources:</strong><br>
                    {''.join(f'- {src}<br>' for src in msg["sources"])}
                </div>
            ''', unsafe_allow_html=True)
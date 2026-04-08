import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

st.secrets["GEMINI_API_KEY"]

# ---------------- Setup ---------------- #
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")

st.set_page_config(page_title="Chat with History")

# ---------------- Session State ---------------- #
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []  # [("user", text), ("assistant", text)]

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None


# ---------------- Helper ---------------- #
def truncate(text, n=50):
    return text if len(text) <= n else text[:n] + "..."


# ---------------- Sidebar ---------------- #
st.sidebar.title("🧠 Chat History")

# Reset button
if st.sidebar.button("🔄 New Chat"):
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    st.session_state.selected_index = None
    st.rerun()

# Convert messages → pairs (Flat list → Paired list, [(Q1, A1), (Q2, A2), ...])
chat_pairs = [
    (st.session_state.messages[i], st.session_state.messages[i + 1])
    for i in range(0, len(st.session_state.messages), 2)
    if i + 1 < len(st.session_state.messages)
]

# Sidebar clickable chats
# Converts your chat history into:
    # Short previews (sidebar)
    # Clickable items
if chat_pairs:
    for idx, ((_, user_msg), (_, bot_msg)) in enumerate(chat_pairs):

        preview = truncate(user_msg, 40)

        if st.sidebar.button(f"💬 {preview}", key=f"chat_{idx}"):
            st.session_state.selected_index = idx
else:
    st.sidebar.write("No chats yet")

# Toggle full history
show_all = st.sidebar.checkbox("Show Full Chat")


# ---------------- Main Page ---------------- #
st.title("💬 Gemini Chatbot")

user_input = st.text_input("Ask something:")

if st.button("Send") and user_input:

    response = st.session_state.chat.send_message(user_input)

    # Store messages
    st.session_state.messages.append(("user", user_input))
    st.session_state.messages.append(("assistant", response.text))

    # Reset selection
    st.session_state.selected_index = None

    st.subheader("Response")
    st.write(response.text)


# ---------------- Selected Chat ---------------- #
if st.session_state.selected_index is not None:
    st.subheader("📜 Selected Chat")

    user_msg, bot_msg = chat_pairs[st.session_state.selected_index]

    st.chat_message("user").write(user_msg[1])
    st.chat_message("assistant").write(bot_msg[1])


# ---------------- Full Chat ---------------- #
if show_all:
    st.subheader("📜 Full Conversation")

    for role, text in st.session_state.messages:
        st.chat_message(role).write(text)
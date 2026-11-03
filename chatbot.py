import streamlit as st 
import json 
import os
import uuid
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model 
from langchain_core.messages import (AIMessage,SystemMessage,HumanMessage)
load_dotenv()
st.set_page_config(page_title="AI Chatbot",page_icon="🤖",layout="wide")
st.title("🤖 AI Chatbot")  
CHAT_FILE = "chat_history.json" 
SYSTEM_PROMPT = (
    "You are a helpful AI assistant. "
    "Answer questions clearly, accurately "
    "and in simple language."
)
def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}
    return {} 
def save_chats():
    with open(CHAT_FILE, "w", encoding="utf-8") as file:
        json.dump(st.session_state.chats,file,indent=4,ensure_ascii=False)
if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_chat = chat_id
    save_chats()
if not st.session_state.chats:
    create_new_chat()
if ("active_chat" not in st.session_state or st.session_state.active_chat not in st.session_state.chats):
    st.session_state.active_chat = next(
        iter(st.session_state.chats)
    )
model = init_chat_model("openai/gpt-oss-120b",model_provider="groq",temperature=0)
with st.sidebar:
    st.header("💬 Chat History")
    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()
    st.divider()
    for chat_id, chat in list(st.session_state.chats.items()):
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"💬 {chat['title']}",key=f"chat_{chat_id}",use_container_width=True):
                st.session_state.active_chat = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.active_chat == chat_id:
                    if st.session_state.chats:
                        st.session_state.active_chat = next(
                            iter(st.session_state.chats)
                        )
                    else:
                        create_new_chat()
                save_chats()
                st.rerun()
active_chat = st.session_state.chats[st.session_state.active_chat]
messages = active_chat["messages"]
for message in messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
prompt = st.chat_input("Your message...")
if prompt:
    messages.append({
        "role": "user",
        "content": prompt
    })
    if active_chat["title"] == "New Chat":
        active_chat["title"] = prompt[:30]
    save_chats()
    with st.chat_message("user"):
        st.write(prompt)
    conversation = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]
    for message in messages:
        if message["role"] == "user":
            conversation.append(
                HumanMessage(content=message["content"])
            )
        elif message["role"] == "assistant":
            conversation.append(
                AIMessage(content=message["content"])
            ) 
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = model.invoke(conversation)
                answer = response.content
                st.write(answer)
                messages.append({ 
                    "role": "assistant",
                    "content": answer
                })
                save_chats() 
            except Exception as e:
                st.error(f"Error: {e}") 
                messages.pop() 
                save_chats() 
    st.rerun() 
import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# ===== 載入 API 金鑰 =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

genai.configure(api_key=API_KEY)

# ===== 頁面設定 =====
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ===== 初始化狀態 =====
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # {"主題名稱": [{"user": ..., "bot": ...}, ...]}
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None

# ===== 自動生成主題函式 =====
def generate_topic(prompt):
    topic_model = genai.GenerativeModel("models/gemini-1.5-flash")
    topic_chat = topic_model.start_chat()
    response = topic_chat.send_message(f"請用不超過10個中文字為以下內容取一個簡短主題：\n{prompt}")
    return response.text.strip().split("\n")[0]

# ===== 側邊欄功能 =====
st.sidebar.title("📂 對話主題")

# 顯示已有的聊天主題
if st.session_state.chat_sessions:
    selected_topic = st.sidebar.radio(
        "選擇主題",
        list(st.session_state.chat_sessions.keys()),
        index=list(st.session_state.chat_sessions.keys()).index(st.session_state.current_topic)
        if st.session_state.current_topic in st.session_state.chat_sessions else 0
    )
    st.session_state.current_topic = selected_topic
else:
    st.sidebar.info("尚未有主題紀錄")

if st.sidebar.button("🧹 清除所有主題"):
    st.session_state.chat_sessions.clear()
    st.session_state.current_topic = None

# ===== 聊天機器人區塊 =====
st.title("🤖 Gemini 聊天機器人")
st.markdown("請輸入任何問題，Gemini 將會回應你。")

# 使用者輸入問題區域
user_input = st.text_area("✏️ 你想問 Gemini 什麼？", height=100)

if st.button("🚀 送出"):
    if user_input.strip() == "":
        st.warning("請輸入問題後再送出。")
    elif len(user_input) > 1000:
        st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
    else:
        with st.spinner("Gemini 正在生成回應..."):
            try:
                # 呼叫 Gemini 回應
                model = genai.GenerativeModel("models/gemini-2.0-flash")
                response = model.generate_content(user_input)
                reply = response.text.strip()

                # 自動產生主題（不超過10個字）
                title = generate_topic(user_input)

                # 確保主題不重複
                counter = 1
                original_title = title
                while title in st.session_state.chat_sessions:
                    title = f"{original_title}_{counter}"
                    counter += 1

                # 儲存對話紀錄
                if st.session_state.current_topic is None:
                    st.session_state.current_topic = title
                    st.session_state.chat_sessions[title] = []

                st.session_state.chat_sessions[st.session_state.current_topic].append({
                    "user_input": user_input,
                    "response": reply
                })

            except Exception as e:
                st.error(f"❌ 發生錯誤：{e}")

# ===== 顯示選擇主題的對話紀錄 =====
if st.session_state.current_topic:
    st.markdown(f"### 💬 主題：{st.session_state.current_topic}")
    for item in st.session_state.chat_sessions[st.session_state.current_topic]:
        st.markdown(f"**👤 你：** {item['user_input']}")
        st.markdown(f"**🤖 Gemini：** {item['response']}")
        st.markdown("---")

import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# ====== 載入 API Key ======
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# ====== 頁面設定 ======
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ====== 初始化狀態 ======
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}  # {"主題名稱": [{"user": ..., "bot": ...}, ...]}
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# ====== 自動生成主題函式 ======
def generate_topic(prompt):
    topic_model = genai.GenerativeModel("models/gemini-1.5-flash")  # 可改回你常用的
    topic_chat = topic_model.start_chat()
    response = topic_chat.send_message(f"請為以下提問產生一個簡短明確的主題，不超過8個字：\n「{prompt}」")
    return response.text.strip().replace("\n", "")

# ===== 側邊欄功能 =====
st.sidebar.title("📂 對話主題")

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
    st.session_state.chat = model.start_chat(history=[])

# ====== 主頁區塊 ======
st.title("🤖 Gemini 聊天機器人")
st.markdown("請輸入任何問題，Gemini 將會回應你。")

# ====== 輸入欄位 ======
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("你想問什麼？", placeholder="請輸入問題...", key="chat_input")
    submitted = st.form_submit_button("🚀 送出")

# ====== 處理使用者輸入 ======
if submitted and user_input:
    with st.spinner("Gemini 正在思考中..."):
        try:
            response = st.session_state.chat.send_message(user_input)
            answer = response.text.strip()

            # 如果是第一次對話，生成主題
            if st.session_state.current_topic is None:
                topic = generate_topic(user_input)
                # 確保主題不重複
                counter = 1
                original_topic = topic
                while topic in st.session_state.chat_sessions:
                    topic = f"{original_topic}_{counter}"
                    counter += 1

                st.session_state.current_topic = topic
                st.session_state.chat_sessions[topic] = []

            # 儲存對話內容
            st.session_state.chat_sessions[st.session_state.current_topic].append({
                "user": user_input,
                "bot": answer
            })

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")

# ====== 顯示聊天紀錄 ======
if st.session_state.current_topic:
    st.markdown(f"### 💬 主題：{st.session_state.current_topic}")
    for item in st.session_state.chat_sessions[st.session_state.current_topic]:
        st.markdown(f"**👤 你：** {item['user']}")
        st.markdown(f"**🤖 Gemini：** {item['bot']}")
        st.markdown("---")

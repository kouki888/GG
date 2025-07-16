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
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# ===== 側邊欄功能 =====
with st.sidebar:
    st.header("🗂️ 對話主題")
    for idx, conv in enumerate(st.session_state.conversations):
        if st.button(conv["title"], key=f"title_{idx}"):
            st.session_state.selected_index = idx

    if st.button("🧹 清除所有對話"):
        st.session_state.conversations = []
        st.session_state.selected_index = None

# ===== 主畫面區塊 =====
st.title("🤖 Gemini Chatbot")
st.markdown("請輸入任何問題，並按 Enter 或點擊送出，Gemini 將會回應你。")

# ====== 輸入區塊 ======
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("你想問什麼？", placeholder="請輸入問題...", key="chat_input")
    submitted = st.form_submit_button("🚀 送出")

# ====== 呼叫 Gemini 回應 ======
if submitted and user_input:
    with st.spinner("Gemini 正在思考中..."):
        try:
            # 回答內容
            response = model.generate_content(user_input)
            answer = response.text.strip()

            # 自動產生對話主題
            title_prompt = f"請用不超過10個中文字為以下內容取一個主題：\n{user_input}"
            title_response = model.generate_content(title_prompt)
            title = title_response.text.strip().split("\n")[0][:10]

            # 加入對話紀錄
            st.session_state.conversations.append({
                "title": title,
                "user": user_input,
                "bot": answer
            })
            st.session_state.selected_index = len(st.session_state.conversations) - 1

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")

# ====== 顯示選定對話內容 ======
if st.session_state.selected_index is not None:
    conv = st.session_state.conversations[st.session_state.selected_index]
    st.markdown("### 💬 對話內容")
    st.markdown(f"**📝 主題：** {conv['title']}")
    st.markdown(f"**👤 你：** {conv['user']}")
    st.markdown(f"**🤖 Gemini：** {conv['bot']}")

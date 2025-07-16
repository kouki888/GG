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
model = genai.GenerativeModel("models/gemini-2.0-pro")

# ====== 頁面設定 ======
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ====== 聊天紀錄狀態 ======
if "history" not in st.session_state:
    st.session_state.history = []

# ====== 標題區塊 ======
st.title("🤖 Gemini Chatbot")
st.markdown("請輸入任何問題，並按 Enter 或點擊送出，Gemini 將會回應你。")

# ====== 輸入欄位 ======
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("你想問什麼？", placeholder="請輸入問題...", key="chat_input")
    submitted = st.form_submit_button("🚀 送出")

# ====== 呼叫 Gemini ======
if submitted and user_input:
    with st.spinner("Gemini 正在思考中..."):
        try:
            response = model.generate_content(user_input)
            answer = response.text.strip()

            # 儲存對話紀錄
            st.session_state.history.append({
                "user": user_input,
                "bot": answer
            })

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")

# ====== 顯示聊天紀錄 ======
if st.session_state.history:
    st.markdown("### 💬 對話紀錄")
    for item in reversed(st.session_state.history):
        st.markdown(f"**👤 你：** {item['user']}")
        st.markdown(f"**🤖 Gemini：** {item['bot']}")
        st.markdown("---")

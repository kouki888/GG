import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# 頁面設定
st.set_page_config(page_title="Gemini 聊天室", layout="wide")
st.title("🤖 Gemini AI 聊天室")

# 初始化狀態
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "remember_api" not in st.session_state:
    st.session_state.remember_api = False
if "chat" not in st.session_state:
    st.session_state.chat = None  # Gemini 的 chat 物件

# ---------------- 🔐 API 金鑰輸入區 ----------------
with st.sidebar:
    st.markdown("## 🔐 API 設定")
    st.markdown("## 限gemini-1.5-flash")
    
    remember_api_checkbox = st.checkbox("記住 API 金鑰", value=st.session_state.remember_api)

    # 檢查是否從勾選變為取消，若是則清空 API 金鑰
    if not remember_api_checkbox and st.session_state.remember_api:
        st.session_state.api_key = ""

    # 更新勾選狀態
    st.session_state.remember_api = remember_api_checkbox

    # 根據勾選狀態與 API 金鑰顯示或輸入
    if st.session_state.remember_api and st.session_state.api_key:
        api_key_input = st.session_state.api_key
    else:
        api_key_input = st.text_input("請輸入 Gemini API 金鑰", type="password")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# ====== 頁面設定 ======
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ===== 側邊欄選單 =====
app_mode = st.sidebar.selectbox("選擇功能模式", ["🤖 Gemini 聊天機器人"])

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

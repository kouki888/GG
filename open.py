import streamlit as st
import pandas as pd
import chardet
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io

# ===== 載入 API 金鑰 =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ API 金鑰未設定，請確認 .env 檔案或環境變數")
    st.stop()

genai.configure(api_key=API_KEY)

# ===== 頁面設定 =====
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

# ===== 側邊欄選單 =====
app_mode = st.sidebar.selectbox("選擇功能模式", ["🤖 Gemini 聊天機器人"])

# ===== Gemini 聊天機器人 =====
if app_mode == "🤖 Gemini 聊天機器人":
    st.title("🤖 Gemini Chatbot")
    st.markdown("請輸入任何問題，Gemini 將會回應你。")

    # ====== 初始化聊天狀態 ======
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None

    # ====== 回應設定 ======
    language = st.selectbox("🌐 回應語言", ["自動判斷", "中文", "英文"])
    style = st.selectbox("🧠 回答風格", ["一般", "簡潔", "詳細"])
    model_option = st.selectbox("⚙️ 模型版本", ["models/gemini-2.0-flash", "models/gemini-1.5-pro"])

    # ====== 使用者輸入問題 ======
    # ===== 表單：輸入框 + 按 Enter 送出 =====
    with st.form("question_form", clear_on_submit=True):
        user_input = st.text_input("✏️ 你想問 Gemini 什麼？", placeholder="請輸入問題並按 Enter...", key="user_input")
        submitted = st.form_submit_button("🚀 送出")  # 使用者可以按 Enter 或按按鈕送出

    if submitted:
        if user_input.strip() == "":
            st.warning("請輸入問題後再送出。")
        elif len(user_input) > 1000:
            st.warning("⚠️ 輸入過長，請簡化你的問題（最多 1000 字元）。")
        else:
            with st.spinner("Gemini 正在生成回應..."):
                try:
                    # 建立模型
                    model = genai.GenerativeModel(model_option)

                    # 加入語言與風格提示
                    prompt = user_input
                    if language == "英文":
                        prompt = f"Please answer in English: {user_input}"
                    elif language == "中文":
                        prompt = f"請用中文回答：{user_input}"

                    if style == "簡潔":
                        prompt += "\n請簡要回答。"
                    elif style == "詳細":
                        prompt += "\n請詳細解釋。"

                    # 回應內容
                    response = model.generate_content(prompt)
                    reply = response.text.strip()

                    # 自動產生主題（限制 10 字內）
                    title_prompt = f"請用不超過10個中文字為以下內容取一個簡短主題：\n{user_input}"
                    title_resp = model.generate_content(title_prompt)
                    title = title_resp.text.strip().split("\n")[0]

                    # 加入對話紀錄
                    st.session_state.chat_history.append({
                        "title": title,
                        "user_input": user_input,
                        "response": reply
                    })
                    st.session_state.selected_chat = len(st.session_state.chat_history) - 1

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")

    # ====== 側邊欄：聊天主題清單 ======
    with st.sidebar:
        st.markdown("---")
        st.header("🗂️ 聊天紀錄")

        for idx, chat in enumerate(st.session_state.chat_history):
            if st.button(chat["title"], key=f"chat_{idx}"):
                st.session_state.selected_chat = idx

        if st.button("🧹 清除所有聊天紀錄"):
            st.session_state.chat_history = []
            st.session_state.selected_chat = None

    # ====== 主畫面：顯示選定對話 ======
    if st.session_state.selected_chat is not None:
        chat = st.session_state.chat_history[st.session_state.selected_chat]
        st.subheader("👤 使用者問題")
        st.info(chat["user_input"])
        st.subheader("🤖 Gemini 回應")
        st.success(chat["response"])

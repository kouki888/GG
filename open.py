import streamlit as st
import openai
from io import StringIO
import os

# 這裡要加入您的 OpenAI API 密鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始設置
if 'history' not in st.session_state:
    st.session_state.history = []

# 頁面設置
st.set_page_config(page_title="GPT 聊天機器人", page_icon="🤖")

# 標題
st.title("GPT 聊天機器人")

# 顯示對話歷史
st.subheader("對話歷史")
for message in st.session_state.history:
    st.markdown(f"**{message['role']}**: {message['content']}")

# 用戶輸入框
user_input = st.text_input("請輸入您的問題或指令:")

# 語言選擇
language = st.selectbox("選擇回應語言", ["中文", "英文"])

# 發送按鈕
if st.button("送出"):
    if user_input:
        # 設定提示語和語言選擇
        prompt = user_input
        if language == "英文":
            prompt = f"Translate the following to English: {user_input}"

        # 發送 API 請求給 GPT
        try:
            response = openai.Completion.create(
                model="text-davinci-003",  # 或其他適用的模型
                prompt=prompt,
                max_tokens=150
            )
            message = response.choices[0].text.strip()

            # 更新對話歷史
            st.session_state.history.append({"role": "User", "content": user_input})
            st.session_state.history.append({"role": "GPT", "content": message})

            # 顯示回應
            st.write(f"**GPT**: {message}")
        except Exception as e:
            st.error(f"發生錯誤: {e}")

# 功能選單：檔案上傳功能
uploaded_file = st.file_uploader("上傳檔案", type=["txt", "csv"])

if uploaded_file:
    # 顯示檔案內容
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.text(stringio.read())

# 設置選項：調整回答風格
response_style = st.selectbox("選擇回答風格", ["簡潔", "詳細"])

# 顯示當前設置
st.markdown(f"**當前設置**: 回應語言 - {language}, 回應風格 - {response_style}")

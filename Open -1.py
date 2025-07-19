import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai

# ============================================
# 頁面基本設定
# ============================================
st.set_page_config(page_title="Gemini 聊天室", layout="wide")
st.title("🤖 Gemini AI 聊天室")

# ============================================
# Session State 初始化
# ============================================
_default_state = {
    "api_key": "",
    "remember_api": False,
    "conversations": {},  # {topic_id: {"title": str, "history": list[dict]}}
    "topic_ids": [],      # 保持主題的順序
    "current_topic": "new",  # 預設為新對話
}
for k, v in _default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
# Sidebar ── API Key 區塊
# ============================================
with st.sidebar:
    st.markdown("## 🔐 API 設定 ")

    # 記住 API Key 的勾選框
    st.session_state.remember_api = st.checkbox(
        "記住 API 金鑰", value=st.session_state.remember_api
    )

    # API Key 輸入或顯示
    if st.session_state.remember_api and st.session_state.api_key:
        api_key_input = st.session_state.api_key
        st.success("✅ 已使用儲存的 API Key")
    else:
        api_key_input = st.text_input("請輸入 Gemini API 金鑰", type="password")

    # 只有在輸入值變動時才寫回 session_state
    if api_key_input and api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input

# ============================================
# 驗證並初始化 Gemini 模型
# ============================================
if st.session_state.api_key:
    try:
        genai.configure(api_key=st.session_state.api_key)
        MODEL_NAME = "models/gemini-2.0-flash"
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.error(f"❌ 初始化 Gemini 失敗：{e}")
        st.stop()
else:
    st.info("⚠️ 請在左側輸入 API 金鑰後開始使用。")
    st.stop()

# ============================================
# Sidebar ── 主題列表
# ============================================
with st.sidebar:
    st.markdown("---")
    st.markdown("## 💡 主題列表")

    topic_options = ["new"] + st.session_state.topic_ids
    topic_labels = ["🆕 新對話"] + [st.session_state.conversations[tid]["title"] for tid in st.session_state.topic_ids]

    selected_topic_id = st.radio(
        "選擇主題以查看或開始對話：",
        options=topic_options,
        index=0 if st.session_state.current_topic == "new" else topic_options.index(st.session_state.current_topic),
        format_func=lambda tid: "🆕 新對話" if tid == "new" else st.session_state.conversations[tid]["title"],
        key="topic_selector",
    )
    st.session_state.current_topic = selected_topic_id

# ============================================
# 主要輸入區
# ============================================
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("你想問什麼？", placeholder="請輸入問題...")
    submitted = st.form_submit_button("🚀 送出")

if submitted and user_input:
    with st.spinner("Gemini 正在思考中..."):
        try:
            response = model.generate_content(user_input)
            answer = response.text.strip()
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            st.stop()

    if st.session_state.current_topic == "new":
        # 建立新主題
        topic_title = user_input if len(user_input) <= 10 else user_input[:10] + "..."
        topic_id = f"topic_{len(st.session_state.topic_ids) + 1}"

        st.session_state.conversations[topic_id] = {
            "title": topic_title,
            "history": [{"user": user_input, "bot": answer}],
        }
        st.session_state.topic_ids.append(topic_id)
        st.session_state.current_topic = topic_id
    else:
        # 使用現有主題
        st.session_state.conversations[st.session_state.current_topic]["history"].append({
            "user": user_input,
            "bot": answer
        })

# ============================================
# 對話紀錄顯示區
# ============================================
if st.session_state.current_topic != "new":
    conv = st.session_state.conversations[st.session_state.current_topic]

    for msg in reversed(conv["history"]):
        st.markdown(f"**👤 你：** {msg['user']}")
        st.markdown(f"**🤖 Gemini：** {msg['bot']}")
        st.markdown("---")

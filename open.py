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
    "conversations": {},        # {topic_id: {"title": str, "history": list[dict]}}
    "topic_ids": [],            # 主題順序
    "current_topic": "new",     # 預設為新對話
}
for k, v in _default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
# Sidebar ── API Key 區塊
# ============================================
with st.sidebar:
    st.markdown("## 🔐 API 設定 ")

    st.session_state.remember_api = st.checkbox("記住 API 金鑰", value=st.session_state.remember_api)

    if st.session_state.remember_api and st.session_state.api_key:
        api_key_input = st.session_state.api_key
        st.success("✅ 已使用儲存的 API Key")
    else:
        api_key_input = st.text_input("請輸入 Gemini API 金鑰", type="password")

    if api_key_input and api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input

# ============================================
# 驗證並初始化 Gemini 模型
# ============================================
if st.session_state.api_key:
    try:
        genai.configure(api_key=st.session_state.api_key)
        MODEL_NAME = "models/gemini-2.0"
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.error(f"❌ 初始化 Gemini 失敗：{e}")
        st.stop()
else:
    st.info("⚠️ 請在左側輸入 API 金鑰後開始使用。")
    st.stop()

# ============================================
# Sidebar ── 聊天主題清單（按鈕版）
# ============================================
with st.sidebar:
    st.markdown("---")
    st.header("🗂️ 聊天紀錄")

    if st.button("🆕 新對話", key="new_btn"):
        st.session_state.current_topic = "new"

    for tid in st.session_state.topic_ids:
        title = st.session_state.conversations[tid]["title"]
        label = f"✔️ {title}" if tid == st.session_state.current_topic else title
        if st.button(label, key=f"topic_btn_{tid}"):
            st.session_state.current_topic = tid

    st.markdown("---")
    if st.button("🧹 清除所有聊天紀錄"):
        st.session_state.conversations = {}
        st.session_state.topic_ids = []
        st.session_state.current_topic = "new"

# ============================================
# 使用者輸入區塊
# ============================================
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_input("你想問什麼？", placeholder="請輸入問題...")
    submitted = st.form_submit_button("🚀 送出")

if submitted and user_input:
    is_new = st.session_state.current_topic == "new"

    if is_new:
        # ==== 先加暫時主題 ====
        topic_id = f"topic_{len(st.session_state.topic_ids) + 1}"
        st.session_state.conversations[topic_id] = {
            "title": "（產生主題中...）",
            "history": [{"user": user_input, "bot": "⏳ 回覆生成中..."}],
        }
        st.session_state.topic_ids.append(topic_id)
        st.session_state.current_topic = topic_id
    else:
        st.session_state.conversations[st.session_state.current_topic]["history"].append({
            "user": user_input,
            "bot": "⏳ 回覆生成中..."
        })

    # === Gemini 回覆內容與主題生成 ===
    with st.spinner("Gemini 正在思考中..."):
        try:
            response = model.generate_content(user_input)
            answer = response.text.strip()

            # 產生主題名稱（如果是新主題）
            if is_new:
                title_prompt = f"請為以下這句話產生一個簡短主題：「{user_input}」"
                title_response = model.generate_content(title_prompt)
                topic_title = title_response.text.strip().replace("主題：", "").replace("\n", "")
                st.session_state.conversations[topic_id]["title"] = topic_title

        except Exception as e:
            answer = f"⚠️ 發生錯誤：{e}"
            if is_new:
                st.session_state.conversations[topic_id]["title"] = "錯誤主題"

    # === 更新對話內容 ===
    st.session_state.conversations[st.session_state.current_topic]["history"][-1]["bot"] = answer

# ============================================
# 對話紀錄顯示區
# ============================================
if st.session_state.current_topic != "new":
    conv = st.session_state.conversations[st.session_state.current_topic]

    for msg in reversed(conv["history"]):
        st.markdown(f"**👤 你：** {msg['user']}")
        st.markdown(f"**🤖 Gemini：** {msg['bot']}")
        st.markdown("---")

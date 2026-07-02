import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import WarshipAgent

st.set_page_config(
    page_title="해군 함정 조회 에이전트",
    page_icon="🚢",
    layout="centered",
)

st.title("🚢 대한민국 해군 함정 조회")
st.caption("함번·함명·함종으로 현역 및 건조 중 함정을 조회합니다. (퇴역함 제외)")

# 에이전트 및 대화 기록 초기화
if "agent" not in st.session_state:
    st.session_state.agent = WarshipAgent()
if "history" not in st.session_state:
    st.session_state.history = []
if "pending" not in st.session_state:
    st.session_state.pending = ""

# 한글 IME 버그 우회: keydown에서 isComposing 체크하는 JS 주입
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', () => {
  const fix = () => {
    const inputs = document.querySelectorAll('input[type=text], textarea');
    inputs.forEach(el => {
      if (el.dataset.imeFix) return;
      el.dataset.imeFix = '1';
      let composing = false;
      el.addEventListener('compositionstart', () => composing = true);
      el.addEventListener('compositionend', () => composing = false);
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' && composing) e.stopImmediatePropagation();
      }, true);
    });
  };
  fix();
  new MutationObserver(fix).observe(document.body, {childList: true, subtree: true});
});
</script>
""", unsafe_allow_html=True)

# 대화 기록 출력
for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar="🚢" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# 입력 폼 (버튼 클릭으로만 제출 → IME 버그 우회)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            label="질문",
            placeholder="예: 전차상륙함 목록 알려줘 / DDG-997 함선명이 뭐야?",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("전송", use_container_width=True)

if submitted and user_input.strip():
    prompt = user_input.strip()

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🚢"):
        with st.spinner("조회 중..."):
            api_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.history
            ]
            reply = st.session_state.agent.chat(prompt, api_history or None)
        st.markdown(reply)

    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.rerun()

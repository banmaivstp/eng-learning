import streamlit as st
from config import client
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple
from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

st.set_page_config(page_title="Edu-Stay AI", page_icon="⚡", layout="centered")

# ============================================================
# M0 — DESIGN SYSTEM: Dark Mode + Glassmorphism + Neon Accent
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Be+Vietnam+Pro:wght@300;400;500;600;700&display=swap');

/* ── ROOT TOKENS ── */
:root {
    --bg:           #0D0D0D;
    --surface:      rgba(255,255,255,0.04);
    --surface-hover:rgba(255,255,255,0.08);
    --border:       rgba(0,245,212,0.15);
    --border-hover: rgba(0,245,212,0.4);
    --teal:         #00F5D4;
    --blue:         #00BBFF;
    --red:          #FF4560;
    --text:         #F0F0F0;
    --text-muted:   #888;
    --radius:       16px;
    --radius-sm:    10px;
}

/* ── GLOBAL RESET ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(13,13,13,0.95) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── GLASS CARD ── */
.glass-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(12px);
    transition: border-color 0.2s, background 0.2s;
}
.glass-card:hover {
    border-color: var(--border-hover);
    background: var(--surface-hover);
}

/* ── METRIC BADGE ── */
.metric-badge {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 16px;
    text-align: center;
}
.metric-badge .value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--teal);
    display: block;
    line-height: 1.1;
}
.metric-badge .label {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── NEON BUTTON ── */
.stButton > button {
    background: linear-gradient(90deg, var(--teal), var(--blue)) !important;
    color: #000 !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── SECONDARY BUTTON (Đăng xuất) ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--red) !important;
    color: var(--red) !important;
}

/* ── TEXT INPUT ── */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 2px rgba(0,245,212,0.15) !important;
}
.stTextInput label { color: var(--text-muted) !important; font-size: 0.85rem !important; }

/* ── RADIO BUTTONS ── */
.stRadio label { color: var(--text) !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: var(--text) !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── STATUS/SPINNER ── */
[data-testid="stStatus"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── ALERT BOXES ── */
.stSuccess {
    background: rgba(0,245,212,0.08) !important;
    border: 1px solid rgba(0,245,212,0.3) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--teal) !important;
}
.stError {
    background: rgba(255,69,96,0.08) !important;
    border: 1px solid rgba(255,69,96,0.3) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--red) !important;
}
.stInfo {
    background: rgba(0,187,255,0.08) !important;
    border: 1px solid rgba(0,187,255,0.2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--blue) !important;
}

/* ── TYPOGRAPHY ── */
h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: var(--text) !important;
}
h1 { font-size: 1.8rem !important; letter-spacing: -0.02em; }
h2 { font-size: 1.3rem !important; }
p, li, span { color: var(--text) !important; }

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 20px 0 !important;
}

/* ── NEON GLOW TITLE ── */
.neon-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--teal), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.subtitle {
    color: var(--text-muted);
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* ── LOGIN SCREEN ── */
.login-container {
    max-width: 420px;
    margin: 80px auto 0;
    text-align: center;
}
.login-logo {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, var(--teal), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.login-tagline {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 40px;
}

/* ── SIDEBAR PROFILE ── */
.sidebar-name {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
    margin-bottom: 2px;
}
.sidebar-email {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 16px;
}
.sidebar-divider {
    border-top: 1px solid var(--border);
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# ROUTING
# ============================================================
if "auth" not in st.session_state:
    render_login_screen()
else:
    render_sidebar_profile()

    # Header
    st.markdown('<div class="neon-title">⚡ Edu-Stay AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Trợ lý AI Biên soạn Quiz Nghe hiểu · Powered by Groq LPU</div>', unsafe_allow_html=True)

    # Input card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    url_input = st.text_input(
        "🔗 Dán link bài học Apple Podcast tại đây:",
        value="https://podcasts.apple.com/vn/podcast/how-to-end-a-conversation-politely-in-english-sound/id1820739470?i=1000760146111",
        placeholder="https://podcasts.apple.com/..."
    )
    st.button("🚀 Bắt đầu Biên soạn câu hỏi (Groq LPU)", key="btn_start")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("btn_start"):
        if not client:
            st.error("⚠️ Hệ thống chưa kết nối được Cloud AI của Groq. Vui lòng check Secrets!")
        else:
            with st.status("🤖 AI đang bóc băng âm thanh và làm đề...", expanded=True) as status:
                audio_url = get_audio_url_from_apple(url_input)
                if not audio_url:
                    st.error("Không bóc được file âm thanh gốc. Thử lại link khác.")
                    st.stop()

                transcript_text = transcribe_audio_with_whisper(audio_url)
                st.session_state['groq_transcript'] = transcript_text

                quiz_data = generate_quiz_from_transcript(transcript_text)
                st.session_state['groq_quiz_data'] = quiz_data

                status.update(label="✅ AI đã xử lý xong bài tập!", state="complete")

    # Quiz area
    if 'groq_quiz_data' in st.session_state:
        with st.expander("📝 Xem toàn bộ Transcript"):
            st.write(st.session_state['groq_transcript'])

        st.markdown("---")
        st.subheader("✍️ Trả lời 10 câu hỏi trắc nghiệm:")
        user_answers = {}

        for item in st.session_state['groq_quiz_data']:
            st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Câu {item['id']}: {item['question']}**")
            options_list = [f"{k}: {v}" for k, v in item['options'].items()]
            user_choice = st.radio("Chọn:", options_list, key=f"q_{item['id']}", label_visibility="collapsed")
            user_answers[item['id']] = user_choice[0]
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("💯 Nộp bài & Xem kết quả"):
            score = 0
            for item in st.session_state['groq_quiz_data']:
                q_id = item['id']
                if user_answers[q_id] == item['correct']:
                    score += 1
                    st.success(f"✅ Câu {q_id}: Chính xác! (Đáp án: {item['correct']})")
                else:
                    st.error(f"❌ Câu {q_id}: Sai rồi. Bạn chọn {user_answers[q_id]} — Đáp án đúng: {item['correct']}")
                st.info(f"💡 Giải thích: {item['explain']}")

            st.markdown("---")
            st.markdown(
                f'<div class="metric-badge"><span class="value">{score}/10</span>'
                f'<span class="label">Kết quả làm bài</span></div>',
                unsafe_allow_html=True
            )

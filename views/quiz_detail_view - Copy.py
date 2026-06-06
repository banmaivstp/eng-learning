"""
views/quiz_detail_view.py
===========================
Màn hình phòng học chi tiết: Audio Player + Transcript Highlight + Quiz Tapping.

Luồng điều hướng:
    podcast_list_view → (click episode) → quiz_detail_view → (nộp bài) → save_learning_history

Milestone 3 + 4 + 5:
    - Trình phát Audio nhúng với HTML5 player tùy chỉnh (waveform, skip ±15s, tốc độ 1.0x)
    - Transcript highlight từng câu theo audio (click câu → tua audio đến giây tương ứng)
    - Quiz Tapping: 10 câu hỏi trắc nghiệm A/B/C/D dạng hộp lớn, độ tương phản cao

Logic Cache:
    - Nếu episode đã có transcript + quiz_json trong DB → load ngay, không gọi AI
    - Nếu chưa có → chạy Whisper STT + Llama 3.1 Quiz Gen → lưu DB

Quy tắc code:
    - KHÔNG thay đổi logic DB/AI/scraper — chỉ thay đổi UI
    - CSS được inject qua styles.py (inject_quiz_detail_css) — KHÔNG thêm CSS inline lớn
    - Log đầy đủ theo level: DEBUG, INFO, WARNING, ERROR
"""

import streamlit as st
import logging
import json
import time
from datetime import datetime

logger = logging.getLogger("views.quiz_detail_view")


# =====================================================
# SAMPLE DATA — fallback khi chưa có AI xử lý
# =====================================================
SAMPLE_TRANSCRIPT_SENTENCES = [
    {"text": "Emma: So, what did you think about the new marketing strategy?", "start": 8.28},
    {"text": "Liam: I think it's a step in the right direction. It focuses more on our core audience.", "start": 8.32},
    {"text": "Emma: Exactly. And by using data analytics, we can target the right people more effectively.", "start": 8.37},
    {"text": "Liam: Absolutely. Data doesn't lie, and it helps us make smarter decisions.", "start": 8.43},
    {"text": "Emma: Do you think we should increase the budget for social media ads?", "start": 8.48},
    {"text": "Liam: That depends on the ROI. We need to analyze the current performance first.", "start": 8.55},
    {"text": "Emma: Right, we should look at engagement rates and conversion metrics.", "start": 9.02},
    {"text": "Liam: And also consider the platform where our audience is most active.", "start": 9.10},
    {"text": "Emma: Agreed. Let's schedule a meeting with the analytics team next week.", "start": 9.18},
    {"text": "Liam: Perfect. I'll send out the calendar invites this afternoon.", "start": 9.25},
]

SAMPLE_QUIZ = [
    {
        "question_number": 1,
        "question": "What is the main topic of the conversation?",
        "options": {"A": "The new marketing strategy", "B": "The budget for social media ads", "C": "The use of data analytics", "D": "The core audience"},
        "correct_answer": "A",
        "explanation": "Emma và Liam đang thảo luận về chiến lược marketing mới của công ty."
    },
    {
        "question_number": 2,
        "question": "According to Emma, what tool can help target the right people?",
        "options": {"A": "Social media", "B": "Data analytics", "C": "Budget increase", "D": "Core audience research"},
        "correct_answer": "B",
        "explanation": "Emma đề cập rằng 'by using data analytics, we can target the right people more effectively'."
    },
    {
        "question_number": 3,
        "question": "What does Liam say about data?",
        "options": {"A": "Data is unreliable", "B": "Data is too expensive", "C": "Data doesn't lie", "D": "Data is hard to analyze"},
        "correct_answer": "C",
        "explanation": "Liam nói 'Data doesn't lie, and it helps us make smarter decisions'."
    },
]


# =====================================================
# HELPER: PARSE TRANSCRIPT
# =====================================================

def _parse_transcript_to_sentences(transcript_raw: str) -> list:
    """
    Chuyển transcript thô (chuỗi văn bản) thành mảng câu với timestamp ước tính.
    """
    if not transcript_raw:
        logger.warning("⚠️ quiz_detail_view: transcript_raw rỗng — dùng sample.")
        return SAMPLE_TRANSCRIPT_SENTENCES

    if transcript_raw.strip().startswith("["):
        try:
            parsed = json.loads(transcript_raw)
            if isinstance(parsed, list) and parsed and "text" in parsed[0]:
                logger.info(f"✅ quiz_detail_view: Parsed JSON transcript — {len(parsed)} sentences.")
                return parsed
        except Exception:
            pass

    import re
    raw_sentences = re.split(r'(?<=[.!?])\s+', transcript_raw.strip())
    raw_sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

    if not raw_sentences:
        return SAMPLE_TRANSCRIPT_SENTENCES

    sentences = []
    current_time = 0.0
    avg_seconds_per_sentence = 3.0

    for sentence in raw_sentences:
        word_count = len(sentence.split())
        duration = max(avg_seconds_per_sentence, word_count * 0.35)
        sentences.append({"text": sentence, "start": round(current_time, 2)})
        current_time += duration

    logger.info(f"✅ quiz_detail_view: Parsed {len(sentences)} sentences từ text transcript.")
    return sentences


def _parse_quiz_data(quiz_json) -> list:
    """
    Parse quiz_json từ DB thành list dữ liệu chuẩn.
    """
    if not quiz_json:
        return SAMPLE_QUIZ

    if isinstance(quiz_json, list):
        return quiz_json

    if isinstance(quiz_json, str):
        try:
            parsed = json.loads(quiz_json)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "quiz" in parsed:
                return parsed["quiz"]
        except Exception as e:
            logger.error(f"🚨 quiz_detail_view: Lỗi parse quiz_json string: {e}")

    if isinstance(quiz_json, dict) and "quiz" in quiz_json:
        return quiz_json["quiz"]

    return SAMPLE_QUIZ


# =====================================================
# HELPER: FETCH & PROCESS EPISODE
# =====================================================

def _load_episode_data(episode: dict, supabase_client) -> tuple:
    """
    Tải dữ liệu episode: ưu tiên cache DB, nếu chưa có thì gọi AI.
    """
    episode_id = episode.get("id", "")
    audio_url = episode.get("audio_url", "")
    transcript_raw = episode.get("transcript", "")
    quiz_json = episode.get("quiz_json", None)

    if supabase_client and episode_id and (not transcript_raw or not quiz_json):
        try:
            from modules.database import get_cached_episode_data
            cached = get_cached_episode_data(episode_id)
            if cached:
                audio_url = cached.get("audio_url", audio_url)
                transcript_raw = cached.get("transcript", transcript_raw)
                quiz_json = cached.get("quiz_json", quiz_json)
        except Exception as e:
            logger.error(f"🚨 quiz_detail_view: Lỗi fetch cache từ DB: {e}")

    if not transcript_raw or not quiz_json:
        audio_url, transcript_raw, quiz_json = _run_ai_pipeline(
            episode=episode,
            audio_url=audio_url,
            episode_id=episode_id,
            supabase_client=supabase_client
        )

    sentences = _parse_transcript_to_sentences(transcript_raw)
    quiz_data = _parse_quiz_data(quiz_json)

    return audio_url, sentences, quiz_data, episode_id


def _run_ai_pipeline(episode: dict, audio_url: str, episode_id: str, supabase_client) -> tuple:
    """
    Chạy toàn bộ AI pipeline và lưu cache vào DB.
    """
    from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

    progress_placeholder = st.empty()

    if not audio_url:
        apple_url = episode.get("apple_url", "")
        if apple_url:
            progress_placeholder.info("🔍 Đang tìm link audio...")
            try:
                from modules.scraper import get_audio_url_from_apple
                audio_url = get_audio_url_from_apple(apple_url)
            except Exception as e:
                logger.error(f"🚨 quiz_detail_view: Lỗi scrape audio URL: {e}")
                progress_placeholder.error("❌ Không lấy được link audio. Vui lòng thử lại.")
                return "", "", None

    if not audio_url:
        progress_placeholder.error("❌ Không có link audio cho bài học này.")
        return "", "", None

    # Whisper STT
    progress_placeholder.info("⚡ AI đang dịch bài nghe... (có thể mất 1-3 phút)")
    try:
        transcript_raw = transcribe_audio_with_whisper(audio_url)
    except Exception as e:
        progress_placeholder.error(f"❌ Lỗi chuyển giọng nói: {e}")
        return audio_url, "", None

    # Quiz Gen
    progress_placeholder.info("🧠 AI đang tạo bộ câu hỏi...")
    quiz_json = None
    try:
        quiz_data = generate_quiz_from_transcript(transcript_raw)
        quiz_json = quiz_data
    except Exception as e:
        progress_placeholder.warning(f"⚠️ Không tạo được bộ câu hỏi: {e}")

    # Save to DB
    if supabase_client and episode_id and transcript_raw:
        try:
            payload = {
                "transcript": transcript_raw,
                "audio_url": audio_url,
            }
            if quiz_json:
                payload["quiz_json"] = quiz_json if isinstance(quiz_json, list) else json.dumps(quiz_json)

            supabase_client.table("episodes").update(payload).eq("id", str(episode_id)).execute()
        except Exception as db_err:
            logger.error(f"🚨 quiz_detail_view: Lỗi save DB: {db_err}")

    progress_placeholder.empty()
    return audio_url, transcript_raw, quiz_json


# =====================================================
# RENDER: AUDIO PLAYER (HTML5 Custom) - Đã tối ưu gọn gàng hơn
# =====================================================

def _render_audio_player(audio_url: str, episode: dict, show: dict):
    """
    Render custom HTML5 audio player siêu gọn để tiết kiệm không gian màn hình laptop.
    """
    show_title = show.get("title", "Podcast")
    ep_title = episode.get("title", "Episode")
    show_cover = show.get("cover_image", None)

    cover_html = (
        f'<img src="{show_cover}" class="qd-player-cover" alt="cover"/>'
        if show_cover
        else '<div class="qd-player-cover-placeholder">🎧</div>'
    )

    if len(ep_title) > 55:
        ep_title_short = ep_title[:52] + "..."
    else:
        ep_title_short = ep_title

    safe_audio_url = audio_url.replace('"', '&quot;') if audio_url else ""

    player_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: 'Inter', -apple-system, sans-serif; }}

  .qd-player-wrap {{
    background: linear-gradient(135deg, rgba(0,242,254,0.05) 0%, rgba(10,20,40,0.95) 40%, rgba(6,13,26,0.98) 100%);
    border: 1px solid rgba(0,242,254,0.18);
    border-radius: 14px;
    padding: 8px 12px 6px 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
  }}
  .qd-top-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
  .qd-player-cover {{ width: 34px; height: 34px; border-radius: 6px; object-fit: cover; border: 1px solid rgba(255,255,255,0.1); flex-shrink: 0; }}
  .qd-player-cover-placeholder {{ width: 34px; height: 34px; border-radius: 6px; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.15); display: flex; align-items: center; justify-content: center; font-size: 15px; flex-shrink: 0; }}
  .qd-info-block {{ flex: 1; overflow: hidden; }}
  .qd-show-name {{ font-size: 10px; font-weight: 600; color: #64748B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 1px; }}
  .qd-ep-title {{ font-size: 12px; font-weight: 700; color: #F1F5F9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }}
  .qd-speed-btn {{ flex-shrink: 0; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 2px 7px; font-size: 11px; font-weight: 700; color: #94A3B8; cursor: pointer; }}
  .qd-speed-btn:hover {{ background: rgba(0,242,254,0.1); color: #00F2FE; }}

  .qd-waveform {{ height: 16px; margin-bottom: 4px; display: flex; align-items: flex-end; gap: 2px; overflow: hidden; }}
  .qd-wave-bar {{ flex: 1; background: rgba(0,242,254,0.15); border-radius: 1px 1px 0 0; min-width: 2px; }}
  .qd-wave-bar.active {{ background: #00F2FE; }}

  .qd-progress-row {{ margin-bottom: 4px; }}
  .qd-progress-bar {{ -webkit-appearance: none; width: 100%; height: 3px; background: rgba(255,255,255,0.08); border-radius: 2px; outline: none; cursor: pointer; position: relative; }}
  .qd-progress-bar::-webkit-slider-thumb {{ -webkit-appearance: none; width: 10px; height: 10px; border-radius: 50%; background: #00F2FE; cursor: pointer; margin-top: -3.5px; }}
  .qd-progress-bar::-webkit-slider-runnable-track {{ background: linear-gradient(to right, #00F2FE var(--prog, 0%), rgba(255,255,255,0.08) var(--prog, 0%)); height: 3px; border-radius: 2px; }}
  .qd-time-row {{ display: flex; justify-content: space-between; font-size: 10px; font-weight: 600; color: #475569; margin-top: 2px; }}
  .qd-time-current {{ color: #94A3B8; }}

  .qd-controls {{ display: flex; align-items: center; justify-content: center; gap: 14px; }}
  .qd-ctrl-btn {{ background: none; border: none; color: #64748B; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
  .qd-ctrl-btn:hover {{ color: #00F2FE; }}
  .qd-ctrl-btn svg {{ stroke: currentColor; fill: none; width: 18px; height: 18px; }}

  .qd-play-btn {{ width: 36px; height: 36px; border-radius: 50%; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); }}
  .qd-play-btn svg {{ width: 16px; height: 16px; stroke: #00F2FE; }}
  .qd-skip-label {{ font-size: 8px; font-weight: 700; color: currentColor; display: block; margin-top: 1px; }}
  .qd-skip-wrap {{ display: flex; flex-direction: column; align-items: center; cursor: pointer; color: #64748B; }}
  .qd-skip-wrap:hover {{ color: #00F2FE; }}
  .qd-skip-wrap svg {{ stroke: currentColor; fill: none; width: 16px; height: 16px; }}
</style>
</head>
<body>

<div class="qd-player-wrap">
  <div class="qd-top-row">
    {cover_html}
    <div class="qd-info-block">
      <div class="qd-show-name">{show_title}</div>
      <div class="qd-ep-title">{ep_title_short}</div>
    </div>
    <button class="qd-speed-btn" onclick="cycleSpeed()" id="speedBtn">1.0x</button>
  </div>

  <div class="qd-waveform" id="waveform"></div>

  <div class="qd-progress-row">
    <input type="range" class="qd-progress-bar" id="progressBar" min="0" max="100" value="0" step="0.1" oninput="seekAudio(this.value)"/>
    <div class="qd-time-row">
      <span class="qd-time-current" id="currentTime">0:00</span>
      <span id="totalTime">0:00</span>
    </div>
  </div>

  <div class="qd-controls">
    <div class="qd-skip-wrap" onclick="skipAudio(-15)">
      <svg viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.5"/></svg>
      <span class="qd-skip-label">15</span>
    </div>

    <button class="qd-ctrl-btn qd-play-btn" onclick="togglePlay()" id="playBtn">
      <svg viewBox="0 0 24 24" id="playIcon"><polygon points="5 3 19 12 5 21 5 3" fill="#00F2FE" stroke="none"/></svg>
    </button>

    <div class="qd-skip-wrap" onclick="skipAudio(15)">
      <svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-.49-3.5"/></svg>
      <span class="qd-skip-label">15</span>
    </div>
  </div>
</div>

<audio id="audioEl" preload="metadata" crossorigin="anonymous">
  {'<source src="' + safe_audio_url + '" type="audio/mpeg"/>' if safe_audio_url else ''}
</audio>

<script>
const audio = document.getElementById('audioEl');
const progressBar = document.getElementById('progressBar');
const currentTimeEl = document.getElementById('currentTime');
const totalTimeEl = document.getElementById('totalTime');
const playIcon = document.getElementById('playIcon');
const waveform = document.getElementById('waveform');
const speedBtn = document.getElementById('speedBtn');

const speeds = [1.0, 1.25, 1.5, 0.75];
let speedIdx = 0;

const heights = [20,30,45,60,50,35,55,70,40,25,60,80,65,45,35,55,75,50,40,60,70,55,45,35,50,65,80,55,40,30,55,70,45,60,40,30,50,65,45,35];
waveform.innerHTML = heights.map((h, i) => '<div class="qd-wave-bar" id="wb' + i + '" style="height:' + h + '%"></div>').join('');

function formatTime(s) {{
  if (isNaN(s) || !isFinite(s)) return '0:00';
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return m + ':' + (sec < 10 ? '0' : '') + sec;
}}

audio.addEventListener('loadedmetadata', function() {{ totalTimeEl.textContent = formatTime(audio.duration); }});

audio.addEventListener('timeupdate', function() {{
  if (!audio.duration) return;
  const pct = (audio.currentTime / audio.duration) * 100;
  progressBar.value = pct;
  progressBar.style.setProperty('--prog', pct + '%');
  currentTimeEl.textContent = formatTime(audio.currentTime);

  const lit = Math.floor((pct / 100) * 40);
  heights.forEach((h, i) => {{
    const bar = document.getElementById('wb' + i);
    if (bar) bar.classList.toggle('active', i < lit);
  }});

  window.parent.postMessage({{type: 'audioTime', currentTime: audio.currentTime}}, '*');
}});

audio.addEventListener('ended', function() {{ playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3" fill="#00F2FE" stroke="none"/>'; }});

function togglePlay() {{
  if (audio.paused) {{
    audio.play().catch(e => console.warn(e));
    playIcon.innerHTML = '<rect x="6" y="4" width="4" height="16" fill="#00F2FE"/><rect x="14" y="4" width="4" height="16" fill="#00F2FE"/>';
  }} else {{
    audio.pause();
    playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3" fill="#00F2FE" stroke="none"/>';
  }}
}}
function seekAudio(val) {{ if (audio.duration) audio.currentTime = (val / 100) * audio.duration; }}
function skipAudio(seconds) {{ audio.currentTime = Math.max(0, Math.min(audio.duration || 0, audio.currentTime + seconds)); }}
function cycleSpeed() {{
  speedIdx = (speedIdx + 1) % speeds.length;
  audio.playbackRate = speeds[speedIdx];
  speedBtn.textContent = speeds[speedIdx].toFixed(2).replace('.00', '.0').replace('.50', '.5').replace('.25', '.25').replace('.75', '.75') + 'x';
}}
</script>
</body>
</html>
"""

    try:
        import streamlit.components.v1 as components
        components.html(player_html, height=142, scrolling=False)  # Thu nhỏ chiều cao player xuống 142px
    except Exception as e:
        logger.error(f"🚨 quiz_detail_view: Lỗi render audio player: {e}")
        if audio_url: st.audio(audio_url)


# =====================================================
# RENDER: TRANSCRIPT SECTION
# =====================================================

def _render_transcript_section(sentences: list):
    """
    Render transcript và theo dõi highlight câu hiện tại.
    """
    if "qd_active_sentence" not in st.session_state:
        st.session_state["qd_active_sentence"] = 0
    if "qd_show_transcript" not in st.session_state:
        st.session_state["qd_show_transcript"] = True

    active_idx = st.session_state["qd_active_sentence"]

    col_label, col_toggle = st.columns([5, 1])
    with col_label:
        st.markdown('<div class="qd-section-header"><span class="qd-section-icon">📋</span><span class="qd-section-title">Transcript</span></div>', unsafe_allow_html=True)
    with col_toggle:
        toggle_label = "Hide ▲" if st.session_state["qd_show_transcript"] else "Show ▼"
        if st.button(toggle_label, key="qd_toggle_transcript", use_container_width=True):
            st.session_state["qd_show_transcript"] = not st.session_state["qd_show_transcript"]
            st.rerun()

    if not st.session_state["qd_show_transcript"]:
        return

    transcript_html_parts = ['<div class="qd-transcript-box">']
    for i, sentence_data in enumerate(sentences):
        text = sentence_data.get("text", "")
        start_sec = sentence_data.get("start", 0.0)
        is_active = (i == active_idx)

        minutes = int(start_sec // 60)
        seconds = int(start_sec % 60)
        timestamp_label = f"{minutes:02d}:{seconds:02d}"

        active_class = "qd-sentence-active" if is_active else "qd-sentence-inactive"
        transcript_html_parts.append(f'<div class="qd-sentence-row {active_class}"><span class="qd-timestamp">{timestamp_label}</span><span class="qd-sentence-text">{text}</span></div>')

    transcript_html_parts.append('</div>')
    st.markdown("".join(transcript_html_parts), unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if active_idx > 0:
            if st.button("← Trước", key="qd_prev_sent", use_container_width=True):
                st.session_state["qd_active_sentence"] = active_idx - 1
                st.rerun()
    with nav_col2:
        st.markdown(f'<div class="qd-sentence-progress"><span class="qd-sentence-progress-label">Câu {active_idx + 1}/{len(sentences)}</span></div>', unsafe_allow_html=True)
    with nav_col3:
        if active_idx < len(sentences) - 1:
            if st.button("Next →", key="qd_next_sent", use_container_width=True):
                st.session_state["qd_active_sentence"] = active_idx + 1
                st.rerun()


# =====================================================
# RENDER: QUIZ SECTION
# =====================================================

def _render_quiz_section(quiz_data: list, episode_id: str, user_id: str, audio_start_time: float, supabase_client):
    """
    Render bộ câu hỏi trắc nghiệm Tapping Quiz dạng hộp nút bấm lớn.
    ĐÃ SỬA: Loại bỏ icon, bọc class qd-quiz-options-container để styles.py thu gọn cỡ chữ & căn lề trái.
    """
    logger.debug(f"❓ quiz_detail_view: Rendering quiz — {len(quiz_data)} câu hỏi.")

    if not quiz_data:
        st.markdown('<div class="qd-empty-quiz">🎯 Chưa có bộ câu hỏi. AI đang tạo...</div>', unsafe_allow_html=True)
        return

    if "qd_user_answers" not in st.session_state:
        st.session_state["qd_user_answers"] = {}
    if "qd_submitted" not in st.session_state:
        st.session_state["qd_submitted"] = False
    if "qd_quiz_start_time" not in st.session_state:
        st.session_state["qd_quiz_start_time"] = time.time()

    submitted = st.session_state["qd_submitted"]

    st.markdown(
        '<div class="qd-section-header" style="margin-top: 10px; margin-bottom: 8px;">'
        '<span class="qd-section-icon">❓</span>'
        '<span class="qd-section-title">Question</span>'
        '</div>',
        unsafe_allow_html=True
    )

    if submitted:
        _render_quiz_results(quiz_data, supabase_client, episode_id, user_id)
        return

    current_q_idx = st.session_state.get("qd_current_question", 0)
    total_q = len(quiz_data)

    if current_q_idx >= total_q:
        _render_submit_button(quiz_data, episode_id, user_id, audio_start_time, supabase_client)
        return

    q = quiz_data[current_q_idx]
    q_num = q.get("question_number", current_q_idx + 1)
    q_text = q.get("question", "")
    options = q.get("options", {})

    # Progress bar câu hỏi gọn gàng
    st.markdown(
        f'<div class="qd-quiz-progress">'
        f'<span class="qd-quiz-progress-label">Câu {current_q_idx + 1}/{total_q}</span>'
        f'<div class="qd-quiz-progress-bar"><div class="qd-quiz-progress-fill" style="width:{int(((current_q_idx)/total_q)*100)}%"></div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(f'<div class="qd-question-text">{q_text}</div>', unsafe_allow_html=True)

    current_answer = st.session_state["qd_user_answers"].get(str(q_num))

    # Toàn bộ khối đáp án nằm trong container định danh để dễ can thiệp CSS
    st.markdown('<div class="qd-quiz-options-container">', unsafe_allow_html=True)
    
    for opt_key in ["A", "B", "C", "D"]:
        opt_text = options.get(opt_key, "")
        if not opt_text:
            continue

        is_selected = (current_answer == opt_key)
        
        # Text sạch không chứa icon radio dư thừa
        btn_label = f"{opt_key}: {opt_text}"
        btn_type = "primary" if is_selected else "secondary"

        if st.button(btn_label, key=f"qd_opt_{q_num}_{opt_key}", use_container_width=True, type=btn_type):
            st.session_state["qd_user_answers"][str(q_num)] = opt_key
            if current_q_idx + 1 < total_q:
                st.session_state["qd_current_question"] = current_q_idx + 1
            else:
                st.session_state["qd_current_question"] = total_q
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="qd-quiz-nav">', unsafe_allow_html=True)
    nav_c1, nav_c2 = st.columns([1, 1])
    with nav_c1:
        if current_q_idx > 0:
            if st.button("← Previous Question", key="qd_prev_q", use_container_width=True):
                st.session_state["qd_current_question"] = current_q_idx - 1
                st.rerun()
    with nav_c2:
        if current_answer:
            if st.button("Next Question →", key="qd_next_q", use_container_width=True):
                if current_q_idx + 1 < total_q:
                    st.session_state["qd_current_question"] = current_q_idx + 1
                else:
                    st.session_state["qd_current_question"] = total_q
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_submit_button(quiz_data, episode_id, user_id, audio_start_time, supabase_client):
    """Màn hình review + nút nộp bài."""
    answered_count = len(st.session_state.get("qd_user_answers", {}))
    total_q = len(quiz_data)

    st.markdown(
        f'<div class="qd-submit-preview">'
        f'<div class="qd-submit-icon">📝</div>'
        f'<div class="qd-submit-title">Submit?</div>'
        f'<div class="qd-submit-sub">Đã trả lời <strong>{answered_count}/{total_q}</strong> câu hỏi</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    col_review, col_submit = st.columns([1, 1])
    with col_review:
        if st.button("← Xem lại", key="qd_review_btn", use_container_width=True):
            st.session_state["qd_current_question"] = 0
            st.rerun()
    with col_submit:
        if st.button("✅ Nộp bài", key="qd_submit_btn", use_container_width=True, type="primary"):
            correct = 0
            for q in quiz_data:
                q_num = str(q.get("question_number", ""))
                if st.session_state["qd_user_answers"].get(q_num) == q.get("correct_answer"):
                    correct += 1

            score_10 = round((correct / max(len(quiz_data), 1)) * 10, 1)
            score_100 = round((correct / max(len(quiz_data), 1)) * 100)
            duration_seconds = int(time.time() - st.session_state.get("qd_quiz_start_time", time.time()))
            
            st.session_state["qd_score"] = score_10
            st.session_state["qd_correct"] = correct
            st.session_state["qd_submitted"] = True

            if user_id and episode_id and supabase_client:
                try:
                    from modules.database import save_learning_history
                    save_learning_history(
                        user_id=str(user_id),
                        episode_id=str(episode_id),
                        score=score_100,
                        duration_seconds=duration_seconds
                    )
                except Exception as db_err:
                    logger.error(f"🚨 quiz_detail_view: Lỗi save learning_history: {db_err}")

            st.balloons()
            st.rerun()


def _render_quiz_results(quiz_data: list, supabase_client, episode_id: str, user_id: str):
    """Render màn hình kết quả sau khi nộp bài."""
    score = st.session_state.get("qd_score", 0)
    correct = st.session_state.get("qd_correct", 0)
    total_q = len(quiz_data)
    user_answers = st.session_state.get("qd_user_answers", {})

    pct = int((correct / max(total_q, 1)) * 100)
    result_emoji = "🏆" if pct >= 80 else ("👍" if pct >= 60 else "📚")
    result_label = "Excellent!" if pct >= 80 else ("Good job!" if pct >= 60 else "Keep going!")

    st.markdown(
        f'<div class="qd-result-card">'
        f'<div class="qd-result-icon">{result_emoji}</div>'
        f'<div class="qd-result-score">{score}/10</div>'
        f'<div class="qd-result-label">{result_label}</div>'
        f'<div class="qd-result-detail">{correct}/{total_q} câu đúng ({pct}%)</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="qd-section-title" style="margin: 10px 0 6px 0;">Chi tiết đáp án</div>', unsafe_allow_html=True)

    for q in quiz_data:
        q_num = str(q.get("question_number", ""))
        user_ans = user_answers.get(q_num, "")
        correct_ans = q.get("correct_answer", "")
        is_correct = (user_ans == correct_ans)
        explanation = q.get("explanation", "")
        q_text = q.get("question", "")
        options = q.get("options", {})

        result_class = "qd-answer-correct" if is_correct else "qd-answer-wrong"
        result_icon = "✅" if is_correct else "❌"

        user_ans_text = options.get(user_ans, "Chưa trả lời")
        correct_ans_text = options.get(correct_ans, "")

        st.markdown(
            f'<div class="qd-answer-card {result_class}">'
            f'<div class="qd-answer-q">{result_icon} Câu {q_num}: {q_text}</div>'
            f'<div class="qd-answer-detail">Bạn chọn: <strong>{user_ans}. {user_ans_text}</strong>'
            + (f' | Đáp án: <strong>{correct_ans}. {correct_ans_text}</strong>' if not is_correct else '')
            + f'</div>'
            f'<div class="qd-answer-explain">💡 {explanation}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if st.button("🔄 Làm lại", key="qd_retry_btn", use_container_width=True):
        st.session_state["qd_user_answers"] = {}
        st.session_state["qd_submitted"] = False
        st.session_state["qd_current_question"] = 0
        st.session_state["qd_quiz_start_time"] = time.time()
        st.rerun()


# =====================================================
# MAIN RENDER FUNCTION
# =====================================================

def render_quiz_detail_page(supabase_client=None, user_id: str = None):
    """
    Màn hình chính Quiz Detail: Audio Player + Transcript + Quiz.
    """
    logger.info("🎬 quiz_detail_view: render_quiz_detail_page() — START.")

    selected_episode = st.session_state.get("selected_episode", {})
    selected_show = st.session_state.get("selected_show", {})

    if not selected_episode:
        st.warning("Không có bài học nào được chọn. Vui lòng quay lại.")
        if st.button("← Your Podcast Library", key="qd_back_no_ep"):
            st.session_state["current_page"] = "Show Detail"
            st.rerun()
        return

    # Back Navigation Button
    if st.button("← Your Podcast Library", key="qd_back_btn"):
        for key in ["qd_active_sentence", "qd_show_transcript", "qd_user_answers",
                    "qd_submitted", "qd_current_question", "qd_quiz_start_time"]:
            st.session_state.pop(key, None)
        st.session_state["current_page"] = "Show Detail"
        st.rerun()

    audio_url, sentences, quiz_data, episode_id = _load_episode_data(
        episode=selected_episode,
        supabase_client=supabase_client
    )

    # 1. Audio Player
    st.markdown('<div class="qd-player-section">', unsafe_allow_html=True)
    _render_audio_player(audio_url=audio_url, episode=selected_episode, show=selected_show)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Transcript Section
    st.markdown('<div class="qd-transcript-section">', unsafe_allow_html=True)
    _render_transcript_section(sentences)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Quiz Section
    st.markdown('<div class="qd-quiz-section">', unsafe_allow_html=True)
    _render_quiz_section(
        quiz_data=quiz_data,
        episode_id=episode_id,
        user_id=user_id or "",
        audio_start_time=0.0,
        supabase_client=supabase_client
    )
    st.markdown('</div>', unsafe_allow_html=True)

    logger.info("🎬 quiz_detail_view: render_quiz_detail_page() — DONE.")
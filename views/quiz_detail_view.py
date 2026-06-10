"""
views/quiz_detail_view.py
===========================
TẦNG GIAO DIỆN (VIEW) — Màn hình phòng học chi tiết.
Audio Player + Transcript Highlight + Quiz Tapping.

Luồng điều hướng:
    podcast_list_view → (click episode) → quiz_detail_view → (nộp bài) → save_learning_history

Milestone 3 + 4 + 5:
    - Trình phát Audio nhúng với HTML5 player tùy chỉnh (waveform, skip ±15s, tốc độ 1.0x)
    - Transcript highlight từng câu theo audio (click câu → tua audio đến giây tương ứng)
    - Quiz Tapping: 10 câu hỏi trắc nghiệm A/B/C/D dạng hộp lớn, độ tương phản cao

Logic Cache:
    - Nếu episode đã có transcript + quiz_json trong DB → load ngay, không gọi AI
    - Nếu chưa có → chạy Whisper STT + Llama 3.1 Quiz Gen → lưu DB

FIX v20260610 — Audio bị reset sau mỗi st.rerun():
    - Dùng @st.fragment để tách biệt audio player khỏi quiz/transcript
    - Fragment player chỉ execute lại khi được trigger từ chính nó
    - Fragment quiz/transcript re-run độc lập, không đụng đến fragment player

FIX v20260610.2 — Click đáp án bị mất button hoặc click 2 lần:
    - Sử dụng callback functions thay vì xử lý trực tiếp trong st.button
    - Thêm episode_id vào key của mọi button để tránh conflict
    - Dùng st.rerun() sau callback để force fragment refresh
"""

import streamlit as st
import logging
import json
import time
from datetime import datetime

# TẦNG STYLE: Import CSS độc lập của màn hình này
from views.quiz_detail_css import inject_quiz_detail_css

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
# HELPER: FETCH SHOW INFO (đảm bảo luôn có cover + title)
# =====================================================

def _load_show_info(episode: dict, supabase_client) -> dict:
    """
    Đảm bảo selected_show trong session_state có đủ title + cover_image.
    """
    current_show = st.session_state.get("selected_show") or {}

    has_title = bool(current_show.get("title") or current_show.get("show_title"))
    has_cover = bool(
        current_show.get("cover_image") or current_show.get("cover")
        or current_show.get("image") or current_show.get("show_image")
    )
    if has_title and has_cover:
        return current_show

    episode_id = episode.get("id", "")
    if not episode_id:
        return current_show

    cache_key = f"qd_show_info_{episode_id}"
    if st.session_state.get(cache_key):
        return st.session_state[cache_key]

    from modules.database import get_show_by_episode_id
    show_from_db = get_show_by_episode_id(supabase_client, episode_id)

    if show_from_db:
        enriched = {**current_show, **show_from_db}

        old_has_cover = has_cover
        new_has_cover = bool(show_from_db.get("cover_image"))
        if not old_has_cover and new_has_cover:
            st.session_state.pop(f"qd_player_html_{episode_id}", None)
            logger.info("🧹 quiz_detail_view: Cleared stale player cache — sẽ rebuild với cover mới")

        st.session_state[cache_key] = enriched
        st.session_state["selected_show"] = enriched
        return enriched

    return current_show


def _load_episode_data(episode: dict, supabase_client) -> tuple:
    """
    Tải dữ liệu episode: ưu tiên cache DB, nếu chưa có thì gọi AI.
    """
    episode_id = episode.get("id", "")
    audio_url = episode.get("audio_url", "")
    transcript_raw = episode.get("transcript", "")
    quiz_json = episode.get("quiz_json", None)

    session_audio_key = f"qd_audio_url_{episode_id}"
    if episode_id and st.session_state.get(session_audio_key):
        audio_url = st.session_state[session_audio_key]
        logger.debug(f"🔊 quiz_detail_view: audio_url từ session cache (episode={episode_id})")

    if supabase_client and episode_id and (not transcript_raw or not quiz_json):
        try:
            from modules.database import get_cached_episode_data
            cached = get_cached_episode_data(episode_id)
            if cached:
                if not st.session_state.get(session_audio_key):
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

    if episode_id and audio_url and not st.session_state.get(session_audio_key):
        st.session_state[session_audio_key] = audio_url
        logger.debug(f"💾 quiz_detail_view: Đã cache audio_url vào session (episode={episode_id})")

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

    progress_placeholder.info("⚡ AI đang dịch bài nghe... (có thể mất 1-3 phút)")
    try:
        transcript_raw = transcribe_audio_with_whisper(audio_url)
    except Exception as e:
        progress_placeholder.error(f"❌ Lỗi chuyển giọng nói: {e}")
        return audio_url, "", None

    progress_placeholder.info("🧠 AI đang tạo bộ câu hỏi...")
    quiz_json = None
    try:
        quiz_data = generate_quiz_from_transcript(transcript_raw)
        quiz_json = quiz_data
    except Exception as e:
        progress_placeholder.warning(f"⚠️ Không tạo được bộ câu hỏi: {e}")

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
# HELPER: BUILD PLAYER HTML
# =====================================================

def _build_player_html(audio_url: str, episode: dict, show: dict) -> str:
    """
    Tạo chuỗi HTML cho custom audio player.
    """
    show_title = show.get("title", "") or show.get("show_title", "") or "Podcast"
    ep_title = episode.get("title", "") or "Episode"
    show_cover = (
        show.get("cover_image")
        or show.get("cover")
        or show.get("image")
        or show.get("show_image")
        or None
    )

    cover_html = (
        f'<img src="{show_cover}" class="qd-player-cover" alt="cover"/>'
        if show_cover
        else '<div class="qd-player-cover-placeholder">🎧</div>'
    )

    if len(ep_title) > 60:
        ep_title_short = ep_title[:57] + "..."
    else:
        ep_title_short = ep_title

    import html as _html
    show_title_safe = _html.escape(show_title)
    ep_title_safe = _html.escape(ep_title_short)
    safe_audio_url = audio_url.replace('"', '&quot;') if audio_url else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden;}}

  .qd-player-wrap {{
    background: linear-gradient(135deg, rgba(0,242,254,0.05) 0%, rgba(10,20,40,0.95) 40%, rgba(6,13,26,0.98) 100%);
    border: 1px solid rgba(0,242,254,0.18);
    border-radius: 14px;
    padding: 8px 12px 6px 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
  }}
  .qd-top-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }}
  .qd-player-cover {{ width: 44px; height: 44px; border-radius: 8px; object-fit: cover; border: 1px solid rgba(255,255,255,0.12); flex-shrink: 0; }}
  .qd-player-cover-placeholder {{ width: 44px; height: 44px; border-radius: 8px; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.15); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
  .qd-info-block {{ flex: 1; overflow: hidden; display: flex; flex-direction: column; justify-content: center; gap: 2px; }}
  .qd-show-name {{ font-size: 11px; font-weight: 600; color: #64748B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.01em; }}
  .qd-ep-title {{ font-size: 13px; font-weight: 700; color: #F1F5F9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3; }}
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
      <div class="qd-show-name">{show_title_safe}</div>
      <div class="qd-ep-title">{ep_title_safe}</div>
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
</html>"""


# =====================================================
# CALLBACK FUNCTIONS FOR QUIZ
# =====================================================

def _on_answer_click(q_num: str, opt_key: str, current_idx: int, total_q: int):
    """Callback khi click đáp án"""
    logger.debug(f"📝 Answer clicked: Q{q_num} -> {opt_key}")
    st.session_state["qd_user_answers"][q_num] = opt_key
    if current_idx + 1 < total_q:
        st.session_state["qd_current_question"] = current_idx + 1
        logger.debug(f"➡️ Moving to question {current_idx + 2}")
    else:
        st.session_state["qd_current_question"] = total_q
        logger.debug(f"🏁 Reached last question, ready for submit")


def _on_prev_question(current_idx: int):
    """Callback khi click Previous Question"""
    if current_idx > 0:
        st.session_state["qd_current_question"] = current_idx - 1
        logger.debug(f"⬅️ Previous question: {current_idx - 1 + 1}")


def _on_next_question(current_idx: int, total_q: int):
    """Callback khi click Next Question"""
    if current_idx + 1 < total_q:
        st.session_state["qd_current_question"] = current_idx + 1
        logger.debug(f"➡️ Next question: {current_idx + 2}")
    else:
        st.session_state["qd_current_question"] = total_q
        logger.debug(f"🏁 Reached last question")


def _on_review():
    """Callback khi click Review"""
    st.session_state["qd_current_question"] = 0
    logger.debug("🔄 Review: back to first question")


def _on_submit(quiz_data: list, episode_id: str, user_id: str, supabase_client):
    """Callback khi click Submit"""
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
            logger.info(f"✅ Learning history saved: user={user_id}, episode={episode_id}, score={score_100}")
        except Exception as db_err:
            logger.error(f"🚨 quiz_detail_view: Lỗi save learning_history: {db_err}")

    st.balloons()


def _on_retry():
    """Callback khi click Làm lại"""
    st.session_state["qd_user_answers"] = {}
    st.session_state["qd_submitted"] = False
    st.session_state["qd_current_question"] = 0
    st.session_state["qd_quiz_start_time"] = time.time()
    logger.debug("🔄 Retry quiz: reset all states")


# =====================================================
# FRAGMENT 1: AUDIO PLAYER
# =====================================================

@st.fragment
def _render_audio_player(audio_url: str, episode: dict, show: dict):
    """
    Render custom HTML5 audio player — bọc trong @st.fragment riêng.
    """
    _episode = st.session_state.get("selected_episode") or episode or {}
    _show = st.session_state.get("selected_show") or show or {}
    _audio_url = (
        st.session_state.get(f"qd_audio_url_{_episode.get('id', '')}")
        or audio_url
        or _episode.get("audio_url", "")
    )

    episode_id = _episode.get("id", "unknown")
    cache_key = f"qd_player_html_{episode_id}"

    if cache_key not in st.session_state:
        logger.debug(f"🎵 quiz_detail_view: Building player...")
        player_html = _build_player_html(audio_url=_audio_url, episode=_episode, show=_show)
        st.session_state[cache_key] = player_html
    else:
        player_html = st.session_state[cache_key]

    try:
        st.iframe(player_html, height=150)
    except Exception as e:
        logger.error(f"🚨 quiz_detail_view: Lỗi render audio player: {e}")
        if _audio_url:
            st.audio(_audio_url)


# =====================================================
# FRAGMENT 2: TRANSCRIPT SECTION
# =====================================================

@st.fragment
def _render_transcript_section(sentences: list):
    """
    Render transcript và theo dõi highlight câu hiện tại.
    """
    if "qd_active_sentence" not in st.session_state:
        st.session_state["qd_active_sentence"] = 0
    if "qd_show_transcript" not in st.session_state:
        st.session_state["qd_show_transcript"] = False

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
        transcript_html_parts.append(
            f'<div class="qd-sentence-row {active_class}">'
            f'<span class="qd-timestamp">{timestamp_label}</span>'
            f'<span class="qd-sentence-text">{text}</span>'
            f'</div>'
        )

    transcript_html_parts.append('</div>')
    st.markdown("".join(transcript_html_parts), unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if active_idx > 0:
            if st.button("← Trước", key="qd_prev_sent", use_container_width=True):
                st.session_state["qd_active_sentence"] = active_idx - 1
                st.rerun()
    with nav_col2:
        st.markdown(
            f'<div class="qd-sentence-progress">'
            f'<span class="qd-sentence-progress-label">Câu {active_idx + 1}/{len(sentences)}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with nav_col3:
        if active_idx < len(sentences) - 1:
            if st.button("Next →", key="qd_next_sent", use_container_width=True):
                st.session_state["qd_active_sentence"] = active_idx + 1
                st.rerun()


# =====================================================
# FRAGMENT 3: QUIZ SECTION (FIXED with callbacks)
# =====================================================

@st.fragment
def _render_quiz_section(quiz_data: list, episode_id: str, user_id: str, supabase_client):
    """
    Render bộ câu hỏi trắc nghiệm.
    FIX: Sử dụng callback functions để xử lý click, tránh mất button.
    """
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

    if submitted:
        _render_quiz_results(quiz_data, episode_id, user_id, supabase_client)
        return

    current_q_idx = st.session_state.get("qd_current_question", 0)
    total_q = len(quiz_data)

    if current_q_idx >= total_q:
        _render_submit_button(quiz_data, episode_id, user_id, supabase_client)
        return

    q = quiz_data[current_q_idx]
    q_num = str(q.get("question_number", current_q_idx + 1))
    q_text = q.get("question", "")
    options = q.get("options", {})

    st.markdown(
        '<div class="qd-section-header" style="margin-top: 10px; margin-bottom: 8px;">'
        '<span class="qd-section-icon">❓</span>'
        '<span class="qd-section-title">Question</span>'
        f'<span class="qd-quiz-progress-label">(Câu {current_q_idx + 1}/{total_q})</span>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="qd-quiz-progress">'
        f'<div class="qd-quiz-progress-bar">'
        f'<div class="qd-quiz-progress-fill" style="width:{int(((current_q_idx)/total_q)*100)}%"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(f'<div class="qd-question-text">{q_text}</div>', unsafe_allow_html=True)

    current_answer = st.session_state["qd_user_answers"].get(q_num)

    st.markdown('<div class="qd-quiz-options-container">', unsafe_allow_html=True)

    # Render 4 đáp án A, B, C, D
    for opt_key in ["A", "B", "C", "D"]:
        opt_text = options.get(opt_key, "")
        if not opt_text:
            continue

        is_selected = (current_answer == opt_key)
        btn_label = f"{opt_key}: {opt_text}"
        btn_type = "primary" if is_selected else "secondary"

        # Tạo unique key cho mỗi button
        button_key = f"qd_opt_{episode_id}_{q_num}_{opt_key}"
        
        st.button(
            btn_label, 
            key=button_key, 
            use_container_width=True, 
            type=btn_type,
            on_click=_on_answer_click,
            args=(q_num, opt_key, current_q_idx, total_q)
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="qd-quiz-nav">', unsafe_allow_html=True)
    nav_c1, nav_c2 = st.columns([1, 1])
    with nav_c1:
        if current_q_idx > 0:
            st.button(
                "← Previous Question", 
                key=f"qd_prev_q_{episode_id}", 
                use_container_width=True,
                on_click=_on_prev_question,
                args=(current_q_idx,)
            )
    with nav_c2:
        if current_answer:
            st.button(
                "Next Question →", 
                key=f"qd_next_q_{episode_id}", 
                use_container_width=True,
                on_click=_on_next_question,
                args=(current_q_idx, total_q)
            )
    st.markdown('</div>', unsafe_allow_html=True)


def _render_submit_button(quiz_data: list, episode_id: str, user_id: str, supabase_client):
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
        st.button(
            "← Review", 
            key=f"qd_review_btn_{episode_id}", 
            use_container_width=True,
            on_click=_on_review
        )
    with col_submit:
        st.button(
            "✅ Submit", 
            key=f"qd_submit_btn_{episode_id}", 
            use_container_width=True, 
            type="primary",
            on_click=_on_submit,
            args=(quiz_data, episode_id, user_id, supabase_client)
        )


def _render_quiz_results(quiz_data: list, episode_id: str, user_id: str, supabase_client):
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

    st.button(
        "🔄 Làm lại", 
        key=f"qd_retry_btn_{episode_id}", 
        use_container_width=True,
        on_click=_on_retry
    )


# =====================================================
# FRAGMENT 4: INTERACTIVE SECTION (Transcript + Quiz)
# =====================================================

@st.fragment
def _render_interactive_section(sentences: list, quiz_data: list, episode_id: str, user_id: str, supabase_client):
    """
    Fragment độc lập chứa Transcript + Quiz.
    """
    st.markdown('<div class="qd-transcript-section">', unsafe_allow_html=True)
    _render_transcript_section(sentences)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="qd-quiz-section">', unsafe_allow_html=True)
    _render_quiz_section(
        quiz_data=quiz_data,
        episode_id=episode_id,
        user_id=user_id or "",
        supabase_client=supabase_client
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# MAIN RENDER FUNCTION
# =====================================================

def render_quiz_detail_page(supabase_client=None, user_id: str = None):
    """
    Màn hình chính Quiz Detail: Audio Player + Transcript + Quiz.
    """
    logger.info("🎬 quiz_detail_view: render_quiz_detail_page() — START.")

    inject_quiz_detail_css()

    selected_episode = st.session_state.get("selected_episode", {})
    selected_show = st.session_state.get("selected_show", {})

    if not selected_episode:
        st.warning("Không có bài học nào được chọn. Vui lòng quay lại.")
        if st.button("← Your Podcast Library", key="qd_back_no_ep"):
            st.session_state["current_page"] = "Show Detail"
            st.rerun()
        return

    current_episode_id = selected_episode.get("id", "")

    # Guard: episode_id thay đổi → xóa cache player cũ
    last_rendered_ep = st.session_state.get("qd_last_rendered_episode_id")
    if last_rendered_ep and last_rendered_ep != current_episode_id:
        st.session_state.pop(f"qd_player_html_{last_rendered_ep}", None)
        st.session_state.pop(f"qd_audio_url_{last_rendered_ep}", None)
        logger.info(f"🧹 quiz_detail_view: Cleared stale player cache (old_ep={last_rendered_ep})")

    st.session_state["qd_last_rendered_episode_id"] = current_episode_id

    # Back Navigation Button
    if st.button("← Your Podcast Library", key="qd_back_btn"):
        st.session_state.pop(f"qd_player_html_{current_episode_id}", None)
        st.session_state.pop(f"qd_audio_url_{current_episode_id}", None)
        for key in [
            "qd_active_sentence", "qd_show_transcript", "qd_user_answers",
            "qd_submitted", "qd_current_question", "qd_quiz_start_time",
            "qd_last_rendered_episode_id"
        ]:
            st.session_state.pop(key, None)
        st.session_state["current_page"] = "Show Detail"
        st.rerun()

    # Load data
    audio_url, sentences, quiz_data, episode_id = _load_episode_data(
        episode=selected_episode,
        supabase_client=supabase_client
    )

    # Đảm bảo show info
    selected_show = _load_show_info(episode=selected_episode, supabase_client=supabase_client)

    # 1. Audio Player — Fragment riêng
    st.markdown('<div class="qd-player-section">', unsafe_allow_html=True)
    _render_audio_player(audio_url=audio_url, episode=selected_episode, show=selected_show)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Interactive Section (Transcript + Quiz) — Fragment riêng
    _render_interactive_section(
        sentences=sentences,
        quiz_data=quiz_data,
        episode_id=episode_id,
        user_id=user_id,
        supabase_client=supabase_client
    )

    logger.info("🎬 quiz_detail_view: render_quiz_detail_page() — DONE.")
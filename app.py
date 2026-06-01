import streamlit as st
import time
import jwt
from config import client, supabase
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.database import save_learning_history

# Thiết lập cấu hình nền tảng trang
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM ---
st.markdown("""
<style>
    .stApp {
        background-color: #0D0D0D !important;
        color: #E0E0E0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }
    .correct-card {
        background: rgba(46, 204, 113, 0.08) !important;
        border: 1px solid #2ecc71 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }
    .incorrect-card {
        background: rgba(231, 76, 60, 0.08) !important;
        border: 1px solid #e74c3c !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }
    .explain-box {
        background: rgba(0, 242, 254, 0.04) !important;
        border-left: 4px solid #00F2FE !important;
        padding: 14px 18px !important;
        border-radius: 4px 12px 12px 4px !important;
        margin-top: 15px !important;
    }
    .neon-text-teal { color: #00F2FE !important; font-weight: 700; }
    .neon-text-green { color: #2ecc71 !important; font-weight: 700; }
    .neon-text-red { color: #e74c3c !important; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    render_login_screen()
else:
    render_sidebar_profile()
    
    # --- KHU VỰC TEST KẾT NỐI SUPABASE TRÊN SIDEBAR ---
    st.sidebar.write("---")
    st.sidebar.markdown("⚙️ **Trạng thái hệ thống:**")
    if supabase:
        try:
            # Gọi bảng ngắn gọn và chuẩn hóa theo config mới (đã ép public schema)
            supabase.table("profiles").select("id").limit(1).execute()
            st.sidebar.success("✅ Supabase: Đang kết nối")
        except Exception as test_e:
            st.sidebar.error(f"❌ Supabase Lỗi: {test_e}")
    else:
        st.sidebar.error("❌ Supabase: Chưa cấu hình")
        
    if 'page' not in st.session_state: st.session_state['page'] = 'list'
    if 'current_episode' not in st.session_state: st.session_state['current_episode'] = None
    if 'submitted_quiz' not in st.session_state: st.session_state['submitted_quiz'] = False

    # GIAO DIỆN 1: DANH SÁCH BÀI HỌC PODCAST
    if st.session_state['page'] == 'list':
        st.title("⚡ Khóa học nghe hiểu tiếng Anh qua Podcast")
        input_show_url = st.text_input("Dán đường dẫn Apple Podcast của Show tổng tại đây:")
        
        if st.button("🔍 Quét danh sách bài học"):
            if input_show_url:
                with st.spinner("Đang đồng bộ hóa dữ liệu từ RSS Feed..."):
                    # Import hàm tại đây để tránh lỗi vòng lặp import chéo giữa các modules
                    from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript
                    
                    show_data = get_episode_list_from_show(input_show_url)
                    if show_data:
                        try:
                            # 1. Thử ghi nhận thông tin kênh Podcast vào bảng `shows` (Cú pháp ngắn gọn sạch sẽ)
                            try:
                                show_db = supabase.table("shows").upsert({
                                    "apple_show_url": input_show_url.strip(),
                                    "title": show_data.get('show_title', 'Podcast Show'),
                                    "cover_image": show_data.get('show_image', '')
                                }, on_conflict="apple_show_url").execute()
                            except Exception as show_err:
                                raise Exception(f"Lỗi ghi dữ liệu vào bảng 'shows': {show_err}")
                            
                            if not show_db.data:
                                raise Exception("Không thể nhận phản hồi dữ liệu trả về từ bảng 'shows'.")
                                
                            show_id = show_db.data[0]["id"]
                            st.session_state['db_show_id'] = show_id
                            
                            # 2. Thử ghi nhận danh sách tập vào bảng `episodes`
                            processed_episodes = []
                            for ep in show_data['episodes']:
                                try:
                                    ep_db = supabase.table("episodes").upsert({
                                        "show_id": show_id,
                                        "title": ep["title"],
                                        "audio_url": ep["apple_url"]
                                    }, on_conflict="show_id,title").execute()
                                    
                                    
                                except Exception as ep_err:
                                    raise Exception(f"Lỗi ghi dữ liệu vào bảng 'episodes': {ep_err}")
                                
                                if ep_db.data:
                                    processed_episodes.append({
                                        "id": ep_db.data[0]["id"], 
                                        "title": ep["title"],
                                        "apple_url": ep["apple_url"],
                                        "image": ep.get("image", show_data.get('show_image', ''))
                                    })
                                    
                            st.session_state['podcast_episodes'] = processed_episodes
                            st.session_state['podcast_show_title'] = show_data['show_title']
                            st.success(f"Đã nạp thành công: {show_data['show_title']}")
                        except Exception as e:
                            st.error(f"💥 {e}")
            
        if 'podcast_episodes' in st.session_state:
            st.write("---")
            st.subheader(f"📚 Danh sách bài học: {st.session_state['podcast_show_title']}")
            for index, ep in enumerate(st.session_state['podcast_episodes']):
                with st.container():
                    st.markdown(f'<div class="glass-card"><h4>Bài {len(st.session_state["podcast_episodes"]) - index}: {ep["title"]}</h4></div>', unsafe_allow_html=True)
                    if st.button("🎧 Bắt đầu học bài này", key=f"btn_ep_{index}"):
                        st.session_state['current_episode'] = ep
                        st.session_state['submitted_quiz'] = False
                        st.session_state['page'] = 'detail'
                        st.rerun()

    # GIAO DIỆN 2: CHI TIẾT BÀI TẬP VÀ TRẮC NGHIỆM ĐIỂM SỐ
    elif st.session_state['page'] == 'detail' and st.session_state['current_episode']:
        from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript
        current_ep = st.session_state['current_episode']
        
        if st.button("⬅️ Quay lại danh sách tập"):
            st.session_state['page'] = 'list'
            st.session_state['current_episode'] = None
            st.rerun()
            
        st.title(current_ep['title'])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if current_ep.get('image'): st.image(current_ep['image'], use_container_width=True)
        with col2:
            st.markdown("**Trình nghe nhạc học tập:**")
            real_audio_url = get_audio_url_from_apple(current_ep['apple_url'])
            if real_audio_url: st.audio(real_audio_url)
                
        # Đồng bộ và sinh đề trắc nghiệm
        if 'last_processed_url' not in st.session_state or st.session_state['last_processed_url'] != current_ep['apple_url']:
            if real_audio_url:
                with st.spinner("AI đang chuyển âm thanh thành văn bản..."):
                    transcript = transcribe_audio_with_whisper(real_audio_url)
                    st.session_state['current_transcript'] = transcript
                with st.spinner("AI đang tạo 10 câu hỏi trắc nghiệm..."):
                    quiz_data = generate_quiz_from_transcript(transcript)
                    st.session_state['groq_quiz_data'] = quiz_data
                    
                    try:
                        # Cập nhật thông tin transcript và quiz vào bảng episodes bằng tên gọn
                        supabase.table("episodes").update({
                            "audio_url": real_audio_url,
                            "transcript": transcript,
                            "quiz_json": {"quiz": quiz_data}
                        }).eq("id", current_ep["id"]).execute()
                    except Exception:
                        pass
                        
                st.session_state['last_processed_url'] = current_ep['apple_url']
                st.session_state['quiz_start_time'] = time.time()
                st.session_state['submitted_quiz'] = False
                
        if 'current_transcript' in st.session_state:
            with st.expander("👁️ Xem chi tiết toàn bộ bài đọc"):
                st.write(st.session_state['current_transcript'])
                
        st.write("---")
        st.subheader("🎯 Bài tập trắc nghiệm kiểm tra nghe hiểu")
        
        if 'groq_quiz_data' in st.session_state and st.session_state['groq_quiz_data']:
            user_answers = {}
            for item in st.session_state['groq_quiz_data']:
                q_id = item['question_number']
                options_list = [f"{k}: {v}" for k, v in item['options'].items()]
                
                card_class = "glass-card"
                if st.session_state['submitted_quiz']:
                    saved_ans = st.session_state.get(f"user_ans_stored_{q_id}", "")
                    card_class = "correct-card" if saved_ans == item['correct_answer'] else "incorrect-card"
                
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                st.markdown(f"<span class='neon-text-teal'>**Câu {q_id}: {item['question']}**</span>", unsafe_allow_html=True)
                
                user_choice = st.radio("Chọn đáp án:", options_list, key=f"q_{q_id}", label_visibility="collapsed", disabled=st.session_state['submitted_quiz'])
                user_answers[q_id] = user_choice[0] if user_choice else ""
                
                if st.session_state['submitted_quiz']:
                    saved_ans = st.session_state.get(f"user_ans_stored_{q_id}", "")
                    if saved_ans == item['correct_answer']:
                        st.markdown(f"🏅 **Kết quả:** <span class='neon-text-green'>Chính xác! (Bạn chọn: {saved_ans})</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"💥 **Kết quả:** <span class='neon-text-red'>Chưa chính xác! (Bạn chọn: {saved_ans} — Đúng: {item['correct_answer']})</span>", unsafe_allow_html=True)
                    st.markdown(f'<div class="explain-box"><strong>💡 AI Giải thích:</strong><br/>{item["explanation"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            if not st.session_state['submitted_quiz']:
                if st.button("💯 Nộp bài và xem kết quả"):
                    start_time = st.session_state.get('quiz_start_time', time.time())
                    duration_seconds = int(time.time() - start_time)
                    
                    score = 0
                    for item in st.session_state['groq_quiz_data']:
                        q_id = item['question_number']
                        st.session_state[f"user_ans_stored_{q_id}"] = user_answers[q_id]
                        if user_answers[q_id] == item['correct_answer']: score += 1
                    
                    st.session_state['last_score'] = score
                    
                    try:
                        auth_data = st.session_state.get("auth", {})
                        token_data = auth_data.get("token", {})
                        id_token = token_data.get("id_token") if isinstance(token_data, dict) else auth_data.get("id_token")
                        
                        if id_token:
                            user_profile = jwt.decode(id_token, options={"verify_signature": False})
                            user_id = user_profile.get("sub")
                            
                            if user_id and current_ep.get("id"):
                                # Đồng bộ truyền đúng UUID (current_ep["id"]) thay vì dùng text cũ
                                save_learning_history(
                                    user_id=user_id, 
                                    episode_id=current_ep["id"], 
                                    score=score, 
                                    duration_seconds=duration_seconds
                                )
                    except Exception as db_err:
                        st.error(f"💥 Lỗi lưu trữ lịch sử làm bài: {db_err}")
                        
                    st.session_state['submitted_quiz'] = True
                    st.rerun()
            else:
                total_q = len(st.session_state['groq_quiz_data'])
                score = st.session_state.get('last_score', 0)
                st.markdown(f'<div style="background: rgba(0, 242, 254, 0.1); padding: 20px; border-radius: 12px; border: 1px dashed #00F2FE; text-align: center; margin-top: 20px;"><span style="font-size: 20px; font-weight: 700; color: #00F2FE;">📊 BÁO CÁO KẾT QUẢ BÀI LÀM</span><br/><span style="font-size: 32px; font-weight: 800; color: #ffffff;">{score} / {total_q}</span> Câu đúng</div>', unsafe_allow_html=True)
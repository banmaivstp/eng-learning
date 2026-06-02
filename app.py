import streamlit as st
import time
import pandas as pd
import logging
from config import client, supabase
from modules.auth import render_login_screen, render_sidebar_profile, get_logged_in_user_id
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.database import (
    save_learning_history, 
    get_cached_episode_data,
    get_user_analytics,
    evaluate_user_badges
)
from views.styles import inject_global_css

# Khởi tạo Logger định danh cho luồng điều phối chính app
logger = logging.getLogger("app_main")

# Cấu hình thiết lập nền tảng ứng dụng
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM NÂNG CẤP & FIX MỜ CHỮ DI ĐỘNG ---
inject_global_css()

if "auth" not in st.session_state:
    logger.debug("🔒 Anonymous user context detected. Presenting secure portal.")
    render_login_screen()
else:
    render_sidebar_profile()
    
    # --- TRÍCH XUẤT THÔNG TIN ĐỊNH DANH QUA LOGIC ARCHITECTURE MỚI ---
    user_id = get_logged_in_user_id()

    # Kiểm tra liên kết dữ liệu hệ thống
    st.sidebar.write("---")
    st.sidebar.markdown("⚙️ **Kết nối hệ thống:**")
    if supabase:
        try:
            # SỬA LỖI: Đổi tên bảng "profiles" -> "users_profile" để khớp cấu trúc DB thực tế
            supabase.table("users_profile").select("id").limit(1).execute()
            st.sidebar.success("✅ Supabase: Sẵn sàng")
            logger.debug("Supabase connection check passed.")
        except Exception as test_e:
            logger.error(f"🚨 Active Supabase link check encountered an issue: {test_e}")
            st.sidebar.error(f"❌ Supabase lỗi: {test_e}")
    else:
        st.sidebar.error("❌ Supabase: Chưa liên kết")
        
    if 'page' not in st.session_state: st.session_state['page'] = 'list'
    if 'current_episode' not in st.session_state: st.session_state['current_episode'] = None
    if 'submitted_quiz' not in st.session_state: st.session_state['submitted_quiz'] = False

    # GIAO DIỆN CHÍNH 1: DASHBOARD TIẾN ĐỘ & DANH SÁCH BÀI HỌC PODCAST
    if st.session_state['page'] == 'list':
        st.title("⚡ Edu-Stay AI Learning Platform")
        
        if user_id:
            logger.debug(f"Loading analytics dashboard view for user: {user_id}")
            stats = get_user_analytics(user_id)
            badges = evaluate_user_badges(stats)
            
            # Khối 1: Hộp Streak Box rực cháy nổi bật nhất trên cùng
            st.markdown(f"""
            <div class="streak-box-container">
                <span style="font-size: 15px; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.95; font-weight:600;">Chuỗi ngày học liên tiếp hiện tại</span>
                <h1 style="margin: 6px 0 2px 0; color: #FFFFFF; font-size: 40px; font-weight: 800; text-shadow: 0 4px 12px rgba(0,0,0,0.15);">🔥 {stats['current_streak']} Ngày học liên tiếp</h1>
                <span style="font-size: 13px; opacity: 0.85;">Kỷ lục chuỗi dài nhất của bạn: {stats['longest_streak']} ngày</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Khối 2: Số liệu Metrics trực quan tổng quan
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric(label="📊 Tổng bài đã học", value=f"{stats['total_episodes']} bài")
            with m_col2:
                st.metric(label="⏱️ Tổng thời gian", value=f"{stats['total_minutes']} phút")
            with m_col3:
                st.metric(label="🎯 Điểm số TB", value=f"{stats['avg_score']}/10")
            with m_col4:
                st.metric(label="📈 Điểm mới nhất", value=f"{stats['latest_score']}/10")
                
            # Khối 3: Tiến độ mục tiêu học trong tuần
            st.write("")
            weekly_goal = 3
            progress_pct = min(int((stats['total_episodes'] / weekly_goal) * 100), 100)
            st.markdown(f"🎯 **Tiến độ hoàn thành mục tiêu tuần:** Đã đạt {stats['total_episodes']}/{weekly_goal} bài học ({progress_pct}%)")
            st.progress(progress_pct / 100)
            
            # Khối 4: Biểu đồ và Badge thành tích
            g_col1, g_col2 = st.columns([5, 4])
            with g_col1:
                st.markdown("📊 **Thời gian nghe hiểu theo ngày trong tuần (phút):**")
                chart_df = pd.DataFrame({
                    "Thời gian (phút)": stats["weekly_data"]
                }, index=["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"])
                st.bar_chart(chart_df, color="#00F2FE")
                
            with g_col2:
                st.markdown("🏅 **Danh hiệu đạt được (Badges):**")
                if badges:
                    for b in badges:
                        st.markdown(f"""
                        <div class="badge-item-card">
                            <span style="font-size: 28px;">{b['icon']}</span>
                            <div>
                                <div style="font-weight: 700; color: #FFD700; font-size:14px; letter-spacing:0.3px;">{b['name']}</div>
                                <div style="font-size: 11px; color: #B5B5B5; line-height:1.2;">{b['desc']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("Hoàn thành bài tập trắc nghiệm nghe hiểu để thu thập các danh hiệu vinh danh tại đây!")
            
            st.markdown("---")
            
        # KHU VỰC NHẬP LINK SHOW PODCAST ĐỂ CÀO DỮ LIỆU
        st.subheader("📻 Khám phá bài nghe mới từ Show")
        input_show_url = st.text_input("Nhập đường dẫn Apple Podcast của Show tổng tại đây:", value="https://podcasts.apple.com/vn/podcast/5-minute-english-talk/id1820739470")
        
        if st.button("🔍 Quét danh sách tập"):
            if input_show_url:
                logger.info(f"🕵️ Bắt đầu cào thông tin Show từ URL: {input_show_url}")
                with st.spinner("Hệ thống đang trích xuất thông tin và đồng bộ danh mục bài học từ RSS..."):
                    show_data = get_episode_list_from_show(input_show_url)
                    if show_data:
                        try:
                            # 1. Thêm hoặc cập nhật dữ liệu kênh vào bảng shows
                            show_db = supabase.table("shows").upsert({
                                "apple_show_url": input_show_url.strip(),
                                "title": show_data.get('show_title', 'Podcast Show'),
                                "cover_image": show_data.get('show_image', '')
                            }, on_conflict="apple_show_url").execute()
                            
                            if not show_db.data:
                                raise Exception("Không thể nhận phản hồi lưu trữ từ bảng 'shows'.")
                                
                            show_id = show_db.data[0]["id"]
                            st.session_state['db_show_id'] = show_id
                            
                            # 2. Thêm hoặc cập nhật danh sách bài học vào bảng episodes
                            processed_episodes = []
                            for ep in show_data['episodes']:
                                ep_db = supabase.table("episodes").upsert({
                                    "show_id": show_id,
                                    "title": ep["title"],
                                    "audio_url": ep["apple_url"]
                                }, on_conflict="show_id,title").execute()
                                
                                if ep_db.data:
                                    processed_episodes.append({
                                        "id": ep_db.data[0]["id"], 
                                        "title": ep["title"],
                                        "apple_url": ep["apple_url"],
                                        "image": ep.get("image", show_data.get('show_image', ''))
                                    })
                                    
                            st.session_state['podcast_episodes'] = processed_episodes
                            st.session_state['podcast_show_title'] = show_data['show_title']
                            logger.info(f"Đồng bộ hoàn tất thành công {len(processed_episodes)} tập bài nghe vào Database.")
                            st.success(f"Đã đồng bộ thành công kênh: {show_data['show_title']}")
                        except Exception as e:
                            logger.error(f"💥 Lỗi đồng bộ hóa dữ liệu từ RSS: {str(e)}")
                            st.error(f"💥 Lỗi hệ thống: {e}")
            
        if 'podcast_episodes' in st.session_state:
            st.write("---")
            st.subheader(f"📚 Danh mục bài nghe: {st.session_state['podcast_show_title']}")
            for idx, ep in enumerate(st.session_state['podcast_episodes']):
                with st.container():
                    st.markdown(f'<div class="glass-card"><h4>Bài {len(st.session_state["podcast_episodes"]) - idx}: {ep["title"]}</h4></div>', unsafe_allow_html=True)
                    if st.button("🎧 Vào phòng học nghe", key=f"btn_ep_{idx}"):
                        st.session_state['current_episode'] = ep
                        st.session_state['submitted_quiz'] = False
                        st.session_state['page'] = 'detail'
                        logger.info(f"🔄 Học viên chọn mở tập bài nghe: '{ep['title']}' (ID: {ep['id']})")
                        st.rerun()

    # GIAO DIỆN CHÍNH 2: TRANG CHI TIẾT BÀI NGHE & LÀM BÀI TRẮC NGHIỆM AI QUIZ
    elif st.session_state['page'] == 'detail' and st.session_state['current_episode']:
        from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript
        current_ep = st.session_state['current_episode']
        
        if st.button("⬅️ Quay lại Dashboard Trang chủ"):
            st.session_state['page'] = 'list'
            st.session_state['current_episode'] = None
            st.rerun()
            
        st.title(current_ep['title'])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if current_ep.get('image'): st.image(current_ep['image'], use_container_width=True)
        with col2:
            st.markdown("**Trình phát Audio Nhúng (Embedded Player):**")
            
            cached_data = get_cached_episode_data(current_ep['id'])
            if cached_data and cached_data.get("audio_url"):
                real_audio_url = cached_data["audio_url"]
            else:
                real_audio_url = get_audio_url_from_apple(current_ep['apple_url'])
                
            if real_audio_url: 
                st.audio(real_audio_url)
                
        # Xử lý tạo và đồng bộ dữ liệu Quiz + Transcript
        if 'last_processed_url' not in st.session_state or st.session_state['last_processed_url'] != current_ep['apple_url']:
            logger.info(f"🚀 Điều phối xử lý dữ liệu cho bài học: {current_ep['title']}")
            
            if cached_data:
                st.session_state['current_transcript'] = cached_data["transcript"]
                quiz_obj = cached_data["quiz_json"]
                
                if isinstance(quiz_obj, dict) and "quiz" in quiz_obj:
                    st.session_state['groq_quiz_data'] = quiz_obj["quiz"]
                else:
                    st.session_state['groq_quiz_data'] = quiz_obj
                st.toast("⚡ Loaded from database cache (< 1s)", icon="🚀")
                logger.debug("Successfully loaded quiz data from database cache.")
            else:
                if real_audio_url:
                    with st.spinner("AI đang thực hiện chuyển giọng nói âm thanh thành văn bản văn bản..."):
                        transcript = transcribe_audio_with_whisper(real_audio_url)
                        st.session_state['current_transcript'] = transcript
                    
                    with st.spinner("AI đang thiết lập biên soạn bộ đề 10 câu trắc nghiệm..."):
                        quiz_data = generate_quiz_from_transcript(transcript)
                        st.session_state['groq_quiz_data'] = quiz_data
                    
                    try:
                        supabase.table("episodes").update({
                            "audio_url": real_audio_url,
                            "transcript": transcript,
                            "quiz_json": {"quiz": quiz_data}
                        }).eq("id", current_ep["id"]).execute()
                        logger.info("✅ Đã lưu cache dữ liệu mới (Transcript & Quiz) vào DB thành công.")
                    except Exception as ce:
                        logger.error(f"🚨 LỖI LƯU CACHE: Không thể lưu dữ liệu ngược lại DB: {ce}")
                            
            st.session_state['last_processed_url'] = current_ep['apple_url']
            st.session_state['quiz_start_time'] = time.time()
            st.session_state['submitted_quiz'] = False
                
        if 'current_transcript' in st.session_state:
            with st.expander("👁️ Xem chi tiết toàn bộ Transcript bài nghe"):
                st.write(st.session_state['current_transcript'])
                
        st.write("---")
        st.subheader("🎯 Bài tập kiểm tra năng lực nghe hiểu")
        
        if 'groq_quiz_data' in st.session_state and st.session_state['groq_quiz_data']:
            user_answers = {}
            for item in st.session_state['groq_quiz_data']:
                q_id = item['question_number']
                options_list = [f"{k}: {v}" for k, v in item['options'].items()]
                
                card_style_class = "glass-card"
                if st.session_state['submitted_quiz']:
                    saved_ans = st.session_state.get(f"stored_ans_{q_id}", "")
                    card_style_class = "correct-card" if saved_ans == item['correct_answer'] else "incorrect-card"
                
                st.markdown(f'<div class="{card_style_class}">', unsafe_allow_html=True)
                st.markdown(f"<span class='neon-text-teal'>**Câu {q_id}: {item['question']}**</span>", unsafe_allow_html=True)
                
                user_choice = st.radio("Chọn một đáp án:", options_list, key=f"radio_q_{q_id}", label_visibility="collapsed", disabled=st.session_state['submitted_quiz'])
                user_answers[q_id] = user_choice[0] if user_choice else ""
                
                if st.session_state['submitted_quiz']:
                    saved_ans = st.session_state.get(f"stored_ans_{q_id}", "")
                    if saved_ans == item['correct_answer']:
                        st.markdown(f"🏅 **Kết quả:** <span class='neon-text-green'>Chính xác! (Đáp án bạn chọn: {saved_ans})</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"💥 **Kết quả:** <span class='neon-text-red'>Chưa chính xác! (Bạn đã chọn: {saved_ans} — Đáp án đúng: {item['correct_answer']})</span>", unsafe_allow_html=True)
                    st.markdown(f'<div class="explain-box"><strong>💡 Giải thích chi tiết bằng tiếng Việt:</strong><br/>{item["explanation"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            if not st.session_state['submitted_quiz']:
                if st.button("💯 Nộp bài và lưu lịch sử tiến độ"):
                    start_time = st.session_state.get('quiz_start_time', time.time())
                    duration_seconds = int(time.time() - start_time)
                    
                    score = 0
                    for item in st.session_state['groq_quiz_data']:
                        q_id = item['question_number']
                        st.session_state[f"stored_ans_{q_id}"] = user_answers[q_id]
                        if user_answers[q_id] == item['correct_answer']: 
                            score += 1
                    
                    st.session_state['last_score'] = score
                    
                    try:
                        if user_id and current_ep.get("id"):
                            logger.info(f"Submitting user quiz results. User: {user_id}, Score: {score}/{len(st.session_state['groq_quiz_data'])}")
                            save_learning_history(
                                user_id=str(user_id), \
                                episode_id=str(current_ep["id"]), \
                                score=score, \
                                duration_seconds=duration_seconds
                            )
                    except Exception as app_err:
                        logger.error(f"💥 LỖI LUỒNG SUBMIT KHI LƯU LỊCH SỬ: {str(app_err)}")
                        
                    st.session_state['submitted_quiz'] = True
                    st.rerun()
            else:
                total_q = len(st.session_state['groq_quiz_data'])
                score = st.session_state.get('last_score', 0)
                st.markdown(f'<div style="background: rgba(0, 242, 254, 0.1); padding: 20px; border-radius: 12px; border: 1px dashed #00F2FE; text-align: center; margin-top: 20px;"><span style="font-size: 18px; font-weight: 700; color: #00F2FE;">📊 TỔNG HỢP KẾT QUẢ BÀI LÀM KIỂM TRA</span><br/><span style="font-size: 34px; font-weight: 800; color: #ffffff;">{score} / {total_q}</span> Câu trả lời đúng</div>', unsafe_allow_html=True)
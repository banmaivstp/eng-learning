import streamlit as st
from config import client
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

# Thiết lập cấu hình nền tảng trang
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM (ĐỒNG BỘ M0, M2 & NÂNG CẤP M4 GAMIFIED UI) ---
st.markdown("""
<style>
    /* 1. Thiết lập giao diện Dark Mode toàn ứng dụng */
    .stApp {
        background-color: #0D0D0D !important;
        color: #E0E0E0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 2. Cấu trúc thẻ Glassmorphic Card tiêu chuẩn */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }

    /* 3. Thẻ Card khi trả lời CHÍNH XÁC (Highlight Xanh) */
    .correct-card {
        background: rgba(46, 204, 113, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid #2ecc71 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }

    /* 4. Thẻ Card khi trả lời SAI (Highlight Đỏ) */
    .incorrect-card {
        background: rgba(231, 76, 60, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid #e74c3c !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
    }
    
    /* 5. Khung hộp giải thích của AI chuẩn Design System */
    .explain-box {
        background: rgba(0, 242, 254, 0.04) !important;
        border-left: 4px solid #00F2FE !important;
        padding: 14px 18px !important;
        border-radius: 4px 12px 12px 4px !important;
        margin-top: 15px !important;
    }
    
    /* 6. Typography Token */
    .neon-text-teal {
        color: #00F2FE !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
        font-size: 1.1rem;
        font-weight: 700;
    }
    .neon-text-green {
        color: #2ecc71 !important;
        font-weight: 700;
    }
    .neon-text-red {
        color: #e74c3c !important;
        font-weight: 700;
    }
    
    /* 7. Nâng cấp kích thước nút Radio to hơn dễ tap trên mobile */
    div[data-testid="stRadio"] label {
        font-size: 16px !important;
        padding: 8px 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# Kiểm tra trạng thái đăng nhập hệ thống (Milestone 0)
if "auth" not in st.session_state:
    render_login_screen()
else:
    # Hiển thị thanh Profile học viên bên thanh Sidebar trái
    render_sidebar_profile()
    
    # Khởi tạo trạng thái chuyển trang điều hướng (Milestone 1 & 2)
    if 'page' not in st.session_state:
        st.session_state['page'] = 'list'
    if 'current_episode' not in st.session_state:
        st.session_state['current_episode'] = None
    if 'submitted_quiz' not in st.session_state:
        st.session_state['submitted_quiz'] = False

    # ==========================================
    # GIAO DIỆN 1: DANH SÁCH SHOW & TẬP PODCAST
    # ==========================================
    if st.session_state['page'] == 'list':
        st.title("⚡ Khóa học nghe hiểu tiếng Anh qua Podcast")
        st.caption("Khám phá các bài học nghe hiểu thông minh được cá nhân hóa tự động bằng công nghệ AI.")
        
        # Ô nhập liên kết kênh (Show URL)
        input_show_url = st.text_input(
            "Dán đường dẫn Apple Podcast của Show tổng tại đây:",
            placeholder="Ví dụ: https://podcasts.apple.com/vn/podcast/5-minute-english-talk/id1820739470"
        )
        
        if st.button("🔍 Quét danh sách bài học"):
            if input_show_url:
                with st.spinner("Hệ thống đang đồng bộ hóa RSS Feed và phân tích cấu trúc kênh..."):
                    show_data = get_episode_list_from_show(input_show_url)
                    if show_data:
                        st.session_state['podcast_show_title'] = show_data['show_title']
                        st.session_state['podcast_show_image'] = show_data['show_image']
                        st.session_state['podcast_episodes'] = show_data['episodes']
                        st.success(f"Đã nạp thành công dữ liệu kênh: {show_data['show_title']}")
                    else:
                        st.error("Không tải được RSS từ link Show này, vui lòng kiểm tra lại!")
            else:
                st.warning("Vui lòng điền đường dẫn Apple Podcast hợp lệ.")
                
        # Hiển thị danh mục các tập phim nếu đã quét dữ liệu thành công
        if 'podcast_episodes' in st.session_state:
            st.write("---")
            st.subheader(f"📚 Danh sách bài học: {st.session_state['podcast_show_title']}")
            
            # Render dạng thẻ Glassmorphic Card danh mục
            for index, ep in enumerate(st.session_state['podcast_episodes']):
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>Bài {len(st.session_state['podcast_episodes']) - index}: {ep['title']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Nút bấm chuyển sang xem chi tiết bài học
                    if st.button("🎧 Bắt đầu học bài này", key=f"btn_ep_{index}"):
                        st.session_state['current_episode'] = ep
                        st.session_state['submitted_quiz'] = False # Reset trạng thái làm bài mới
                        st.session_state['page'] = 'detail'
                        st.rerun()

    # ==========================================
    # GIAO DIỆN 2: TRANG CHI TIẾT BÀI HỌC (DETAIL PAGE)
    # ==========================================
    elif st.session_state['page'] == 'detail' and st.session_state['current_episode']:
        current_ep = st.session_state['current_episode']
        
        # Thanh điều hướng trên cùng trang
        if st.button("⬅️ Quay lại danh sách tập"):
            st.session_state['page'] = 'list'
            st.session_state['current_episode'] = None
            st.rerun()
            
        st.title(current_ep['title'])
        
        # Cột bố cục hiển thị hình ảnh đại diện và trình nghe nhạc nhúng (Milestone 2)
        col1, col2 = st.columns([1, 2])
        with col1:
            if current_ep.get('image'):
                st.image(current_ep['image'], use_container_width=True)
        with col2:
            st.markdown("**Trình nghe nhạc học tập độc quyền:**")
            # Trích xuất tìm link audio .mp3 từ mã nguồn Apple Podcast Web
            with st.spinner("Đang kết nối đến cổng phân phối âm thanh..."):
                real_audio_url = get_audio_url_from_apple(current_ep['apple_url'])
                
            if real_audio_url:
                st.audio(real_audio_url)
            else:
                st.error("Không thể bóc tách link âm thanh từ tập podcast này.")
                
        # --- PHẦN 1: TRANSCRIPT KHÔNG GIAN HỌC TẬP ---
        st.write("---")
        st.subheader("📝 Văn bản dịch bài nghe (Transcript)")
        
        # Kiểm tra và sinh Transcript/Quiz tự động từ AI Engine nếu chưa tồn tại
        if 'last_processed_url' not in st.session_state or st.session_state['last_processed_url'] != current_ep['apple_url']:
            if real_audio_url:
                with st.spinner("AI đang tiến hành rã băng giọng nói thành văn bản bằng Whisper..."):
                    transcript = transcribe_audio_with_whisper(real_audio_url)
                    st.session_state['current_transcript'] = transcript
                    
                with st.spinner("Mô hình Llama-3.1 đang biên soạn đề trắc nghiệm nghe hiểu 10 câu..."):
                    quiz_list = generate_quiz_from_transcript(transcript)
                    st.session_state['groq_quiz_data'] = quiz_list
                    
                st.session_state['last_processed_url'] = current_ep['apple_url']
                st.session_state['submitted_quiz'] = False
            else:
                st.warning("Không có tệp âm thanh hợp lệ để AI xử lý chuyển đổi ngôn ngữ.")
                
        if 'current_transcript' in st.session_state:
            with st.expander("👁️ Nhấn vào đây để xem chi tiết toàn bộ bài đọc"):
                st.write(st.session_state['current_transcript'])
                
        # --- PHẦN 2: BỘ CÂU HỎI TRẮC NGHIỆM ĐÃ TRÒ CHƠI HÓA (MILESTONE 4 GAMIFIED UI) ---
        st.write("---")
        st.subheader("🎯 Bài tập trắc nghiệm kiểm tra nghe hiểu")
        
        if 'groq_quiz_data' in st.session_state and st.session_state['groq_quiz_data']:
            user_answers = {}
            
            # Vòng lặp duyệt và hiển thị từng câu hỏi độc lập
            for item in st.session_state['groq_quiz_data']:
                q_id = item['question_number']
                options_list = [f"{k}: {v}" for k, v in item['options'].items()]
                
                # Biến xác định lớp CSS để gán hiệu ứng màu sắc sau khi Nộp bài
                card_class = "glass-card" # Mặc định là xám mờ tinh tế
                
                if st.session_state['submitted_quiz']:
                    # Lấy đáp án học viên chọn từ trạng thái lưu trữ session_state
                    saved_ans = st.session_state.get(f"user_ans_stored_{q_id}", "")
                    if saved_ans == item['correct_answer']:
                        card_class = "correct-card" # Đổi sang viền xanh lá
                    else:
                        card_class = "incorrect-card" # Đổi sang viền đỏ
                
                # Sử dụng container html để render giao diện khung Card tùy chỉnh màu động
                st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                
                # Tiêu đề câu hỏi
                st.markdown(f"<span class='neon-text-teal'>**Câu {q_id}: {item['question']}**</span>", unsafe_allow_html=True)
                
                # Trình lựa chọn Radio Button lớn, trực quan
                user_choice = st.radio(
                    "Chọn đáp án:", 
                    options_list, 
                    key=f"q_{q_id}", 
                    label_visibility="collapsed",
                    disabled=st.session_state['submitted_quiz'] # Khóa đáp án sau khi đã chấm điểm
                )
                user_answers[q_id] = user_choice[0] if user_choice else ""
                
                # Hiển thị phần kết quả chi tiết & giải thích ngay bên trong thẻ Card nếu đã bấm Nộp bài
                if st.session_state['submitted_quiz']:
                    saved_ans = st.session_state.get(f"user_ans_stored_{q_id}", "")
                    if saved_ans == item['correct_answer']:
                        st.markdown(f"🏅 **Kết quả:** <span class='neon-text-green'>Chính xác! (Bạn chọn: {saved_ans})</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"💥 **Kết quả:** <span class='neon-text-red'>Chưa chính xác! (Bạn chọn: {saved_ans} — Đáp án đúng: {item['correct_answer']})</span>", unsafe_allow_html=True)
                    
                    # Box giải thích AI phong cách viền Teal và Icon bóng đèn nổi bật
                    st.markdown(f"""
                    <div class="explain-box">
                        <strong>💡 AI Giải thích chi tiết:</strong><br/>
                        {item['explanation']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown('</div>', unsafe_allow_html=True) # Đóng thẻ div Card
                
            # Nút bấm Nộp bài kích hoạt tính toán kết quả và đổi màu giao diện
            if not st.session_state['submitted_quiz']:
                if st.button("💯 Nộp bài và xem kết quả"):
                    # Lưu lại các đáp án đã chọn vào session để giữ trạng thái khi Streamlit rerun
                    score = 0
                    for item in st.session_state['groq_quiz_data']:
                        q_id = item['question_number']
                        st.session_state[f"user_ans_stored_{q_id}"] = user_answers[q_id]
                        if user_answers[q_id] == item['correct_answer']:
                            score += 1
                    
                    st.session_state['last_score'] = score
                    st.session_state['submitted_quiz'] = True
                    st.rerun() # Refresh để gán class CSS màu sắc ngay lập tức
                    
            else:
                # Banner tổng điểm xuất hiện sinh động dưới cùng sau khi hoàn tất
                total_q = len(st.session_state['groq_quiz_data'])
                score = st.session_state.get('last_score', 0)
                st.markdown(f"""
                <div style="background: rgba(0, 242, 254, 0.1); padding: 20px; border-radius: 12px; border: 1px dashed #00F2FE; text-align: center; margin-top: 20px;">
                    <span style="font-size: 20px; font-weight: 700; color: #00F2FE;">📊 BÁO CÁO KẾT QUẢ BÀI LÀM</span><br/>
                    <span style="font-size: 32px; font-weight: 800; color: #ffffff;">{score} / {total_q}</span> <span style="font-size: 18px; color: #E0E0E0;">Câu đúng</span>
                </div>
                """, unsafe_allow_html=True)
import streamlit as st
from config import client
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

# Thiết lập cấu hình nền tảng trang
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM (ĐỒNG BỘ M0, M2 & NÂNG CẤP M3) ---
st.markdown("""
<style>
    /* 1. Thiết lập giao diện Dark Mode toàn ứng dụng */
    .stApp {
        background-color: #0D0D0D !important;
        color: #E0E0E0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 2. Cấu trúc thẻ Glassmorphic Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* 3. Khung hiển thị từng tập bài học thuộc Milestone 2 */
    .episode-box {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }
    
    .neon-text-teal {
        color: #00F2FE !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    
    /* 4. Thẻ nhãn trạng thái Đã học / Chưa học */
    .badge-status {
        padding: 4px 10px !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }
    .badge-learned {
        background: rgba(0, 242, 254, 0.15) !important;
        color: #00F2FE !important;
        border: 1px solid #00F2FE;
    }
    .badge-unlearned {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #9CA3AF !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 5. Khung cuộn Transcript chuyên dụng cho Milestone 3 */
    .transcript-container {
        max-height: 250px !important;
        overflow-y: auto !important;
        padding: 15px !important;
        background: rgba(0, 0, 0, 0.4) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        color: #CCCCCC !important;
    }
    
    /* Custom thanh cuộn của Transcript */
    .transcript-container::-webkit-scrollbar {
        width: 6px;
    }
    .transcript-container::-webkit-scrollbar-thumb {
        background: rgba(0, 242, 254, 0.3);
        border-radius: 4px;
    }
    
    /* Custom giao diện Audio Player nhúng của Streamlit */
    div.stAudio > audio {
        width: 100% !important;
        border-radius: 10px !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #0D0D0D !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- KIỂM TRA ĐĂNG NHẬP (GATEKEEPER - GIỮ NGUYÊN LOGIC GỐC M0) ---
if "auth" not in st.session_state:
    st.markdown('<div class="glass-card" style="margin-top: 50px; text-align: center;">', unsafe_allow_html=True)
    render_login_screen()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    render_sidebar_profile()

    # Quản lý State Machine điều hướng chọn bài tập
    if "selected_episode" not in st.session_state:
        st.session_state["selected_episode"] = None

    # Danh sách lưu tạm tiêu đề đã làm bài xong để cập nhật badge UI động
    if "mock_learned_titles" not in st.session_state:
        st.session_state["mock_learned_titles"] = {"6 Minute English: Innovation", "6 Minute English: Technology"}

    # ==========================================
    # GIAO DIỆN 1: DANH SÁCH KHÁM PHÁ SHOW & EPISODE LIST (MILESTONE 2)
    # ==========================================
    if st.session_state["selected_episode"] is None:
        st.title("⚡ Khám phá nội dung Podcast")
        
        # Ô nhập liệu URL của Show cần học
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        show_url_input = st.text_input(
            "Nhập Link Show của kênh Podcast (Ví dụ: Kênh 6 Minute English):",
            value="https://podcasts.apple.com/vn/podcast/5-minute-english-talk/id1820739470"
        )
        
        if st.button("🔍 Quét danh sách bài học"):
            with st.spinner("Hệ thống đang cào cấu trúc RSS Feed của Show..."):
                scraped_data = get_episode_list_from_show(show_url_input)
                if scraped_data:
                    st.session_state["current_show"] = scraped_data
                else:
                    st.error("Không tải được RSS từ link Show này, vui lòng kiểm tra lại!")
        st.markdown('</div>', unsafe_allow_html=True)

        # Hiển thị cấu trúc danh mục nếu có dữ liệu Show hợp lệ
        if "current_show" in st.session_state:
            show = st.session_state["current_show"]
            
            # Khối Show Card lớn kết hợp ảnh bìa nổi bật phía trên
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_cover, col_details = st.columns([1, 2])
            with col_cover:
                if show["show_image"]:
                    st.image(show["show_image"], use_container_width=True)
            with col_details:
                st.markdown(f"## {show['show_title']}")
                st.caption(f"Tổng số tập bài học phân tách được: {len(show['episodes'])}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Thanh công cụ tìm kiếm tối giản đầu trang danh sách tập
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            search_query = st.text_input("🔍 Nhập từ khóa lọc nhanh tiêu đề bài tập:", value="")
            
            st.write("### 📜 Danh sách các tập bài học hiện có:")
            
            for ep in show["episodes"]:
                # Cơ chế kiểm tra từ khóa Search Filter
                if search_query.lower() not in ep["title"].lower():
                    continue
                
                # Xác định trạng thái để áp dụng Badge tương ứng
                is_learned = ep["title"] in st.session_state["mock_learned_titles"]
                badge_text = "✅ Đã học" if is_learned else "⬜ Chưa học"
                badge_class = "badge-learned" if is_learned else "badge-unlearned"
                
                # Render khối bao ngoài của tập
                st.markdown(f"""
                <div class="episode-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-weight: 600; color: #FFF; width: 70%;">{ep['title']}</div>
                        <div><span class="badge-status {badge_class}">{badge_text}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Nút bấm chuyển tiếp hướng người dùng sang giao diện chi tiết của tập phim
                if st.button("📖 Vào học tập này", key=f"btn_{ep['title']}"):
                    st.session_state["selected_episode"] = ep
                    # Dọn dẹp cache cũ khi chuyển tập để ép chạy xử lý tập mới hoàn toàn
                    if "current_guid" in st.session_state and st.session_state["current_guid"] != ep["title"]:
                        if 'groq_transcript' in st.session_state: del st.session_state['groq_transcript']
                        if 'groq_quiz_data' in st.session_state: del st.session_state['groq_quiz_data']
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 2: TRANG CHI TIẾT BÀI TẬP (DETAIL PAGE - NÂNG CẤP MILESTONE 3)
    # ==========================================
    else:
        current_ep = st.session_state["selected_episode"]
        
        if st.button("⬅️ Quay lại danh sách tập"):
            st.session_state["selected_episode"] = None
            st.rerun()
            
        st.title("📖 Trang Chi Tiết Bài Học")
        st.markdown(f"<h3 class='neon-text-teal'>{current_ep['title']}</h3>", unsafe_allow_html=True)

        # --- LUỒNG XỬ LÝ AI NGẦM ---
        if "current_guid" not in st.session_state or st.session_state["current_guid"] != current_ep["title"]:
            with st.status("Hệ thống đang nạp âm thanh và xử lý nội dung AI...", expanded=True) as status:
                try:
                    audio_url = get_audio_url_from_apple(current_ep["apple_url"])
                    if not audio_url:
                        st.error("Không thể bóc tách link âm thanh từ tập podcast này.")
                        st.stop()
                    
                    # Lưu link audio vào session_state phục vụ trình phát nhúng st.audio
                    st.session_state['current_audio_url'] = audio_url
                        
                    transcript_text = transcribe_audio_with_whisper(audio_url)
                    quiz_data = generate_quiz_from_transcript(transcript_text)
                    
                    st.session_state['groq_transcript'] = transcript_text
                    st.session_state['groq_quiz_data'] = quiz_data
                    st.session_state["current_guid"] = current_ep["title"]
                    status.update(label="AI Biên soạn thành công!", state="complete")
                except Exception as e:
                    status.update(label="Lỗi xử lý AI!", state="error")
                    st.error(f"Chi tiết: {e}")
                    st.stop()

        # ----------------------------------------------------
        # THÀNH PHẦN 1: EMBEDDED PLAYER (TRÌNH PHÁT NHÚNG TRÊN CÙNG)
        # ----------------------------------------------------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎧 Trình phát Audio trực tuyến")
        if 'current_audio_url' in st.session_state and st.session_state['current_audio_url']:
            st.audio(st.session_state['current_audio_url'])
        else:
            audio_url_fallback = get_audio_url_from_apple(current_ep["apple_url"])
            st.session_state['current_audio_url'] = audio_url_fallback
            st.audio(audio_url_fallback)
        st.caption("Trải nghiệm đa nhiệm: Nghe trực tiếp, cuộn văn bản và chọn đáp án trắc nghiệm song song không cần chuyển tab.")
        st.markdown('</div>', unsafe_allow_html=True)

        # ----------------------------------------------------
        # THÀNH PHẦN 2: TRANSCRIPT VĂN BẢN (KHUNG SCROLL Ở GIỮA)
        # ----------------------------------------------------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📝 Văn bản bài nghe (Transcript)")
        
        # Tạo khung bao cố định chiều cao bằng CSS token để hỗ trợ tự động cuộn (Best-effort scroll)
        transcript_html = f"""
        <div class="transcript-container">
            {st.session_state['groq_transcript']}
        </div>
        """
        st.markdown(transcript_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ----------------------------------------------------
        # THÀNH PHẦN 3: ĐỀ THI AI QUIZ TRẮC NGHIỆM (Ở DƯỚI CÙNG)
        # ----------------------------------------------------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Bài kiểm tra trắc nghiệm nâng cao")
        
        user_answers = {}
        for item in st.session_state['groq_quiz_data']:
            q_id = item['question_number']
            st.markdown(f"<span class='neon-text-teal'>**Câu {q_id}: {item['question']}**</span>", unsafe_allow_html=True)
            options_list = [f"{k}: {v}" for k, v in item['options'].items()]
            user_choice = st.radio("Chọn:", options_list, key=f"q_{q_id}", label_visibility="collapsed")
            user_answers[q_id] = user_choice[0]
            st.write("---")
            
        if st.button("💯 Nộp bài"):
            score = 0
            for item in st.session_state['groq_quiz_data']:
                q_id = item['question_number']
                if user_answers[q_id] == item['correct_answer']:
                    score += 1
                    st.success(f"✅ Câu {q_id}: Chính xác! (Đáp án: {item['correct_answer']})")
                else:
                    st.error(f"❌ Câu {q_id}: Sai rồi. Bạn chọn {user_answers[q_id]} - Đáp án đúng là: {item['correct_answer']}")
                st.info(f"💡 Giải thích: {item['explanation']}")
                
            st.markdown(f"""
            <div style="background: rgba(0, 242, 254, 0.1); padding: 15px; border-radius: 12px; border: 1px dashed #00F2FE; text-align: center;">
                <span style="font-size: 18px; font-weight: 700; color: #00F2FE;">📊 Kết quả bài làm: {score} / {len(st.session_state['groq_quiz_data'])} Câu Đúng</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Ghi nhận tiêu đề này vào danh sách đã học để cập nhật hiển thị badge
            st.session_state["mock_learned_titles"].add(current_ep["title"])
            
        st.markdown('</div>', unsafe_allow_html=True)
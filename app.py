import streamlit as st
from config import client
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple
from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

# Config cấu hình trang định dạng
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM (MILESTONE 0: DARK MODE & GLASSMORPHISM) ---
st.markdown("""
<style>
    /* 1. Thiết lập hình nền tối toàn app và font chữ hiện đại */
    .stApp {
        background-color: #0D0D0D !important;
        color: #E0E0E0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 2. Định nghĩa các CSS Class Token theo Design System */
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
    
    .neon-text-teal {
        color: #00F2FE !important;
        text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    
    .neon-text-blue {
        color: #4FACFE !important;
        text-shadow: 0 0 10px rgba(79, 172, 254, 0.3);
    }

    /* 3. Tùy biến lại các phần tử mặc định của Streamlit */
    /* Tiêu đề ứng dụng */
    h1 {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Thanh Sidebar bên trái */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Custom lại ô Nhập văn bản (Text Input) */
    div[data-testid="stTextInput"] input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #00F2FE !important;
        box-shadow: 0 0 0 2px rgba(0, 242, 254, 0.2) !important;
    }
    
    /* Custom lại tất cả các Button chính (Bo tròn lớn, hiệu ứng hover mượt) */
    div.stButton > button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #0D0D0D !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        width: 100% !important; /* Mobile-friendly */
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4) !important;
        color: #000000 !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Tùy biến vùng Expander (Transcript) */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
    }
    
    /* Tùy biến Radio buttons trắc nghiệm */
    div[data-testid="stRadio"] label {
        color: #D1D5DB !important;
    }
    
    /* Hộp thông báo trạng thái (Alerts) */
    div[data-testid="stNotification"] {
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
</style>
""", unsafe_allow_html=True)


# --- KIỂM TRA ĐĂNG NHẬP (GATEKEEPER) ---
if "auth" not in st.session_state:
    # Bọc màn hình login cũ vào khung Container căn giữa để tạo form glassmorphism đẹp mắt
    st.markdown('<div class="glass-card" style="margin-top: 50px; text-align: center;">', unsafe_allow_html=True)
    render_login_screen()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # 1. Render khu vực thành viên bên thanh bên
    render_sidebar_profile()
    
    # 2. Giao diện trang chính (Bọc toàn bộ khu vực cấu hình vào thẻ Glassmorphism Card)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.title("⚡ Trợ lý AI Biên soạn Quiz Nghe hiểu")
    st.caption("Ứng dụng độc quyền cho hệ sinh thái Homestay Giáo dục Edu-Stay")

    # Mặc định điền link bài tập gốc của bạn
    url_input = st.text_input(
        "Dán link bài học Apple Podcast tại đây:", 
        value="https://podcasts.apple.com/vn/podcast/how-to-end-a-conversation-politely-in-english-sound/id1820739470?i=1000760146111"
    )

    if st.button("🚀 Bắt đầu Biên soạn câu hỏi (Groq LPU)"):
        if not client:
            st.error("Hệ thống chưa kết nối được Cloud AI của Groq. Vui lòng check Secrets!")
        else:
            with st.status("AI đang bóc băng âm thanh và làm đề...", expanded=True) as status:
                # Gọi Module Scraper
                audio_url = get_audio_url_from_apple(url_input)
                if not audio_url:
                    st.error("Không bóc được file âm thanh gốc. Thử lại link khác.")
                    st.stop()
                
                # Gọi Module AI để xử lý chuyển hóa text & tạo quiz
                transcript_text = transcribe_audio_with_whisper(audio_url)
                st.session_state['groq_transcript'] = transcript_text
                
                quiz_data = generate_quiz_from_transcript(transcript_text)
                st.session_state['groq_quiz_data'] = quiz_data
                
                status.update(label="AI Đã xử lý xong bài tập!", state="complete")
    st.markdown('</div>', unsafe_allow_html=True) # Kết thúc block cấu hình đầu vào

    # --- RENDER VÙNG HIỂN THỊ BÀI TẬP VÀ CHẤM ĐIỂM ---
    if 'groq_quiz_data' in st.session_state:
        # Transcript và Đề bài được đưa vào một vùng riêng biệt có chiều sâu
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.expander("编️ Nhấp vào đây để xem toàn bộ nội dung bài đọc (Transcript)"):
            st.write(st.session_state['groq_transcript'])
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("✍️ Trả lời 10 câu hỏi trắc nghiệm bên dưới:")
        user_answers = {}
        
        # Vòng lặp dựng các Widget câu hỏi động
        for item in st.session_state['groq_quiz_data']:
            st.markdown(f"<span class='neon-text-teal'>**Câu {item['id']}: {item['question']}**</span>", unsafe_allow_html=True)
            options_list = [f"{k}: {v}" for k, v in item['options'].items()]
            user_choice = st.radio("Chọn:", options_list, key=f"q_{item['id']}", label_visibility="collapsed")
            user_answers[item['id']] = user_choice[0] # Lấy ký tự A, B, C, hoặc D ở đầu chuỗi
            st.write("---")
            
        if st.button("💯 Nộp bài"):
            score = 0
            for item in st.session_state['groq_quiz_data']:
                q_id = item['id']
                if user_answers[q_id] == item['correct']:
                    score += 1
                    st.success(f"✅ Câu {q_id}: Chính xác! (Đáp án: {item['correct']})")
                else:
                    st.error(f"❌ Câu {q_id}: Sai rồi. Bạn chọn {user_answers[q_id]} - Đáp án đúng là: {item['correct']}")
                st.info(f"💡 Giải thích: {item['explain']}")
                
            # Đắp thêm một Badge bọc ngoài cho tổng điểm (Metrics) thêm phần ấn tượng
            st.markdown('<div style="background: rgba(0, 242, 254, 0.1); padding: 15px; border-radius: 10px; border: 1px dashed #00F2FE; margin-top: 20px;">', unsafe_allow_html=True)
            st.metric("Kết quả làm bài:", f"{score} / 10")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) # Kết thúc block đề bài

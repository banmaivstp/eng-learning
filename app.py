import streamlit as st
from config import client
from modules.auth import render_login_screen, render_sidebar_profile
from modules.scraper import get_audio_url_from_apple
from modules.ai_engine import transcribe_audio_with_whisper, generate_quiz_from_transcript

st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- KIỂM TRA ĐĂNG NHẬP (GATEKEEPER) ---
if "auth" not in st.session_state:
    render_login_screen()
else:
    # 1. Render khu vực thành viên bên thanh bên
    render_sidebar_profile()
    
    # 2. Giao diện trang chính
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

    # --- RENDER VÙNG HIỂN THỊ BÀI TẬP VÀ CHẤM ĐIỂM ---
    if 'groq_quiz_data' in st.session_state:
        with st.expander("📝 Nhấp vào đây để xem toàn bộ nội dung bài đọc (Transcript)"):
            st.write(st.session_state['groq_transcript'])
            
        st.subheader("✍️ Trả lời 10 câu hỏi trắc nghiệm bên dưới:")
        user_answers = {}
        
        # Vòng lặp dựng các Widget câu hỏi động
        for item in st.session_state['groq_quiz_data']:
            st.markdown(f"**Câu {item['id']}: {item['question']}**")
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
                
            st.metric("Kết quả làm bài:", f"{score} / 10")
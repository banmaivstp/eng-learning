import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import re
from groq import Groq
import json
from streamlit_oauth import OAuth2Component
from supabase import create_client, Client
import jwt

# --- 1. CẤU HÌNH KẾT NỐI HỆ THỐNG (Đọc ngầm hoàn toàn từ Secrets) ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

# Khởi tạo các kết nối Cloud dịch vụ
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

# Thiết lập cổng Google OAuth2
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL
)

st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- 2. XỬ LÝ ĐĂNG NHẬP GMAIL & GHI DỮ LIỆU VÀO SUPABASE ---
if "auth" not in st.session_state:
    st.title("⚡ Hệ thống Học tiếng Anh Edu-Stay AI")
    st.caption("Vui lòng xác thực tài khoản để bắt đầu bài học nghe hiểu.")
    
    # Nút bấm đăng nhập - Ép cố định redirect_uri về URL chuẩn
    result = oauth2.authorize_button(
        name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
        redirect_uri="https://eng-learning.streamlit.app/",
        scope="openid email profile",
        key="google_auth"
    )
    
    if result and "token" in result:
        st.session_state["auth"] = result
        
        # Giải mã lấy thông tin Profile an toàn qua thư viện PyJWT
        id_token = result["token"]["id_token"]
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        user_id = payload.get("sub")
        email = payload.get("email")
        full_name = payload.get("name")
        avatar_url = payload.get("picture")
        
        # 💾 TIẾN HÀNH LƯU/CẬP NHẬT VÀO DATABASE SUPABASE
        if supabase:
            try:
                user_data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "avatar_url": avatar_url
                }
                supabase.table("users_profile").upsert(user_data).execute()
            except Exception as db_err:
                st.warning(f"Lưu lịch sử đăng nhập lỗi nhẹ: {db_err}")
                
        st.rerun()

else:
    # --- INTERFACE SAU KHI ĐĂNG NHẬP THÀNH CÔNG ---
    id_token = st.session_state["auth"]["token"]["id_token"]
    user_profile = jwt.decode(id_token, options={"verify_signature": False})
    
    # Hiển thị thanh Sidebar thông tin học viên
    st.sidebar.image(user_profile.get("picture", ""), width=60)
    st.sidebar.markdown(f"Học viên: **{user_profile.get('name')}**")
    st.sidebar.caption(f"Email: {user_profile.get('email')}")
    
    if st.sidebar.button("🚪 Đăng xuất"):
        del st.session_state["auth"]
        st.rerun()
        
    # --- 🎬 NỘI DUNG CHÍNH CỦA ỨNG DỤNG AI ---
    st.title("⚡ Trợ lý AI Biên soạn Quiz Nghe hiểu")
    st.caption("Ứng dụng độc quyền cho hệ sinh thái Homestay Giáo dục Edu-Stay")

    def get_audio_url_from_apple(apple_url):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(apple_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                if "contentUrl" in script.text:
                    return json.loads(script.text).get("contentUrl")
            match = re.search(r'https://[^"]+\.(?:mp3|m4a|mp4)', response.text)
            if match:
                return match.group(0)
        except:
            return None
        return None

    url_input = st.text_input(
        "Dán link bài học Apple Podcast tại đây:", 
        value="https://podcasts.apple.com/vn/podcast/how-to-end-a-conversation-politely-in-english-sound/id1820739470?i=1000760146111"
    )

    if st.button("🚀 Bắt đầu Biên soạn câu hỏi (Groq LPU)"):
        if not client:
            st.error("Hệ thống chưa kết nối được Cloud AI của Groq. Vui lòng check Secrets!")
        else:
            with st.status("AI đang bóc băng âm thanh và làm đề...", expanded=True) as status:
                
                audio_url = get_audio_url_from_apple(url_input)
                if not audio_url:
                    st.error("Không bóc được file âm thanh gốc. Thử lại link khác.")
                    st.stop()
                
                # Download file vào bộ nhớ tạm
                audio_res = requests.get(audio_url)
                temp_file = "temp_podcast.mp3"
                with open(temp_file, "wb") as f:
                    f.write(audio_res.content)
                
                # Gọi Whisper chuyển âm thanh thành chữ
                with open(temp_file, "rb") as file:
                    translation = client.audio.transcriptions.create(
                        file=(temp_file, file.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                
                transcript_text = translation
                st.session_state['groq_transcript'] = transcript_text
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                # Gọi mô hình Llama 3.1 thế hệ mới tạo câu hỏi trắc nghiệm
                prompt = f"""
                Based on the following English transcript, generate exactly 10 multiple-choice questions to test listening comprehension.
                You MUST reply strictly with a JSON object containing a "quiz" key, which holds an array of 10 questions.
                
                Expected JSON schema:
                {{
                    "quiz": [
                        {{
                            "id": 1,
                            "question": "Question text?",
                            "options": {{"A": "Opt 1", "B": "Opt 2", "C": "Opt 3", "D": "Opt 4"}},
                            "correct": "A",
                            "explain": "Giải thích chi tiết đáp án bằng tiếng Việt."
                        }}
                    ]
                }}
                Transcript: {transcript_text}
                """
                
                chat_completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",  
                    messages=[
                        {"role": "system", "content": "You are a backend server that outputs strictly JSON. No markdown code blocks."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                quiz_json = json.loads(chat_completion.choices[0].message.content)
                st.session_state['groq_quiz_data'] = quiz_json["quiz"]
                status.update(label="AI Đã xử lý xong bài tập!", state="complete")

    # --- HIỂN THỊ BÀI TẬP VÀ CHẤM ĐIỂM ---
    if 'groq_quiz_data' in st.session_state:
        with st.expander("📝 Nhấp vào đây để xem toàn bộ nội dung bài đọc (Transcript)"):
            st.write(st.session_state['groq_transcript'])
            
        st.subheader("✍️ Trả lời 10 câu hỏi trắc nghiệm bên dưới:")
        user_answers = {}
        
        for item in st.session_state['groq_quiz_data']:
            st.markdown(f"**Câu {item['id']}: {item['question']}**")
            options_list = [f"{k}: {v}" for k, v in item['options'].items()]
            user_choice = st.radio("Chọn:", options_list, key=f"q_{item['id']}", label_visibility="collapsed")
            user_answers[item['id']] = user_choice[0]
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

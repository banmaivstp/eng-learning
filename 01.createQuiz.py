import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import re
from groq import Groq
import json

# --- CẤU HÌNH API KEY MIỄN PHÍ TỪ GROQ ---
# Hãy thay thế bằng API Key thực tế của bạn lấy từ console.groq.com

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Khởi tạo Client Kết nối với Groq Cloud
# if GROQ_API_KEY != "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
    # client = Groq(api_key=GROQ_API_KEY)
# else:
    # client = None

st.set_page_config(page_title="Groq Free Audio Quiz", page_icon="⚡", layout="centered")
st.title("⚡ Hệ thống AI Offline-Cloud tạo Quiz Miễn Phí")
st.caption("Ứng dụng nền tảng Groq Cloud để xử lý Tốc độ cao - Không cần Credit Card")

# --- HÀM BÓC TÁCH FILE AUDIO GỐC TỪ LINK APPLE PODCAST ---
def get_audio_url_from_apple(apple_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(apple_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm trong các thẻ script cấu trúc dạng JSON-LD của Apple
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            if "contentUrl" in script.text:
                data = json.loads(script.text)
                return data.get("contentUrl")
                
        # Phương án dự phòng dùng Regex tìm trực tiếp link đuôi .mp3/.m4a trong source code
        match = re.search(r'https://[^"]+\.(?:mp3|m4a|mp4)', response.text)
        if match:
            return match.group(0)
    except Exception as e:
        st.error(f"Lỗi khi quét cấu trúc link Apple: {e}")
    return None

# --- GIAO DIỆN CHÍNH ---
url_input = st.text_input(
    "Đường link Apple Podcast cần xử lý:", 
    value="https://podcasts.apple.com/vn/podcast/how-to-end-a-conversation-politely-in-english-sound/id1820739470?i=1000760146111"
)

if st.button("🚀 Kích hoạt quy trình AI (Groq Free)"):
    if client is None:
        st.error("Vui lòng điền GROQ_API_KEY của bạn vào code trước khi chạy!")
    else:
        with st.status("Hệ thống Groq AI đang xử lý...", expanded=True) as status:
            
            # Bước 1: Crawl link audio từ Apple
            status.update(label="1. Đang bóc tách link cấu trúc của Apple Podcast...", state="running")
            audio_url = get_audio_url_from_apple(url_input)
            
            if not audio_url:
                st.error("Không thể tự động lấy file audio từ link này. Có thể Apple đã đổi cấu hình chặn crawl.")
                st.stop()
            
            st.write(f"Tìm thấy file nguồn âm thanh: `{audio_url}`")
            
            # Bước 2: Tải file về bộ nhớ tạm và đẩy lên Whisper của Groq
            status.update(label="2. Đang tải âm thanh và bóc băng thành chữ (Groq Whisper-v3)...", state="running")
            
            audio_res = requests.get(audio_url)
            temp_file = "temp_downloaded_podcast.mp3"
            with open(temp_file, "wb") as f:
                f.write(audio_res.content)
            
            # Gọi API Whisper miễn phí của Groq để xử lý âm thanh sang văn bản tiếng Anh
            with open(temp_file, "rb") as file:
                translation = client.audio.transcriptions.create(
                    file=(temp_file, file.read()),
                    model="whisper-large-v3", # Bản Whisper mạnh nhất hiện tại
                    response_format="text"
                )
            
            transcript_text = translation
            st.session_state['groq_transcript'] = transcript_text
            
            # Xóa file tạm ngay lập tức để giải phóng dung lượng ổ cứng laptop
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            # Bước 3: Đẩy Văn bản vào Llama 3 trên Groq để sinh chính xác 10 câu Quiz trắc nghiệm định dạng JSON
            status.update(label="3. Đang dùng Llama 3 (Cloud) biên soạn 10 câu hỏi trắc nghiệm ngữ cảnh...", state="running")
            
            prompt = f"""
            Based on the following English transcript, generate exactly 10 multiple-choice questions to test listening comprehension.
            The questions should focus on the main ideas, specific vocabulary, and polite English phrases mentioned.
            
            You MUST reply strictly with a JSON object containing a "quiz" key, which holds an array of 10 questions. Do not include markdown blocks like ```json or any conversational text before/after.
            
            Expected JSON schema:
            {{
                "quiz": [
                    {{
                        "id": 1,
                        "question": "Question text here?",
                        "options": {{"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"}},
                        "correct": "A",
                        "explain": "Giải thích bằng tiếng Việt chi tiết tại sao đáp án này đúng dựa vào bài nghe."
                    }}
                ]
            }}

            Transcript:
            {transcript_text}
            """
            
            # Gọi mô hình Llama 3 tốc độ siêu cao của Groq
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a precise backend system that outputs strictly JSON. Never output markdown code blocks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"} # Ép Groq trả về cấu trúc JSON sạch
            )
            
            # Parse chuỗi kết quả thành Object JSON trong Python
            raw_content = chat_completion.choices[0].message.content
            quiz_json = json.loads(raw_content)
            
            st.session_state['groq_quiz_data'] = quiz_json["quiz"]
            status.update(label="Xử lý hoàn tất thành công!", state="complete")

# --- PHẦN HIỂN THỊ GIAO DIỆN LÀM BÀI VÀ CHẤM ĐIỂM ---
if 'groq_quiz_data' in st.session_state:
    st.success("🎉 AI đã biên soạn xong bộ 10 câu hỏi nghe hiểu!")
    
    with st.expander("📝 Xem nội dung Văn bản Bài nghe (Transcript)"):
        st.write(st.session_state['groq_transcript'])
        
    st.subheader("✍️ Bài tập trắc nghiệm nghe hiểu (10 câu):")
    
    user_answers = {}
    
    # Hiển thị lần lượt 10 câu hỏi dạng nút bấm Radio
    for item in st.session_state['groq_quiz_data']:
        st.markdown(f"**Câu {item['id']}: {item['question']}**")
        options_list = [f"{k}: {v}" for k, v in item['options'].items()]
        user_choice = st.radio(
            f"Chọn đáp án:", 
            options_list, 
            key=f"groq_q_{item['id']}", 
            label_visibility="collapsed"
        )
        user_answers[item['id']] = user_choice[0] # Lấy ký tự đầu tiên 'A', 'B', 'C', 'D'
        st.write("---")
        
    # Logic chấm điểm khi bấm nút Nộp bài
    if st.button("💯 Nộp bài và Kiểm tra kết quả"):
        score = 0
        total = len(st.session_state['groq_quiz_data'])
        
        st.subheader("📊 Kết quả chi tiết từ Trợ lý AI:")
        for item in st.session_state['groq_quiz_data']:
            q_id = item['id']
            ans = user_answers[q_id]
            correct_ans = item['correct']
            
            if ans == correct_ans:
                score += 1
                st.markdown(f"✅ **Câu {q_id}: CHÍNH XÁC!** (Bạn chọn: {ans})")
            else:
                st.markdown(f"❌ **Câu {q_id}: CHƯA ĐÚNG.** (Bạn chọn: {ans} — Đáp án đúng: **{correct_ans}**)")
            st.caption(f"💡 *Giải thích:* {item['explain']}")
            st.write("")
            
        st.metric(label="Điểm số cuối cùng của bạn", value=f"{score}/{total}")
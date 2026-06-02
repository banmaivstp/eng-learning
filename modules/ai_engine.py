import os
import requests
import json
import logging
from config import client

# Khởi tạo bộ định danh logger riêng cho module xử lý AI Engine
logger = logging.getLogger("modules.ai_engine")

def transcribe_audio_with_whisper(audio_url: str) -> str:
    """Tải âm thanh tạm thời và chuyển giọng nói thành văn bản thông qua Whisper-large-v3"""
    logger.info(f"🎙️ Bắt đầu tải tệp âm thanh từ URL để gửi tới Whisper: {audio_url}")
    audio_res = requests.get(audio_url)
    temp_file = "temp_podcast.mp3"
    
    with open(temp_file, "wb") as f:
        f.write(audio_res.content)
    logger.debug("💾 Đã lưu tệp âm thanh tạm thời xuống đĩa cục bộ (temp_podcast.mp3).")
        
    try:
        logger.info("⏳ Đang gửi yêu cầu Transcribe tới Groq Cloud Whisper API...")
        with open(temp_file, "rb") as file:
            translation = client.audio.transcriptions.create(
                file=(temp_file, file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        transcript_text = translation
        logger.info("✅ Chuyển đổi giọng nói sang văn bản thành công!")
        logger.debug(f"Độ dài Transcript trích xuất: {len(transcript_text)} ký tự.")
    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình gọi API Whisper: {str(e)}")
        raise e
    finally:
        # Đảm bảo luôn dọn dẹp file rác khỏi ổ đĩa cục bộ kể cả khi gặp lỗi
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.debug("🧹 Đã dọn dẹp và giải phóng file âm thanh tạm thời khỏi hệ thống.")
            
    return transcript_text

def generate_quiz_from_transcript(transcript_text: str) -> list:
    """Gọi mô hình Llama-3.1-8b-instant thiết lập cấu trúc đề trắc nghiệm chuẩn JSON mới"""
    logger.info("🧠 Khởi chạy tiến trình sinh đề trắc nghiệm thông minh từ văn bản Transcript...")
    
    prompt = f"""
    Based on the following English transcript, generate exactly 10 multiple-choice questions to test listening comprehension.
    You MUST reply strictly with a JSON object containing a "quiz" key, which holds an array of 10 questions.
    
    Expected JSON schema:
    {{
        "quiz": [
            {{
                "question_number": 1,
                "question": "Question text?",
                "options": {{"A": "Opt 1", "B": "Opt 2", "C": "Opt 3", "D": "Opt 4"}},
                "correct_answer": "A",
                "explanation": "Giải thích chi tiết đáp án bằng tiếng Việt."
            }}
        ]
    }}
    Transcript: {transcript_text}
    """
    
    try:
        logger.info("⏳ Đang gửi cấu trúc Prompt tới Llama-3.1-8b-instant...")
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[
                {"role": "system", "content": "You are a backend server that outputs strictly JSON. No markdown code blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        raw_output = chat_completion.choices[0].message.content
        logger.debug("📥 Đã nhận phản hồi dạng thô từ LLM.")
        
        parsed_json = json.loads(raw_output)
        quiz_data = parsed_json.get("quiz", [])
        
        logger.info(f"✅ Đã biên soạn hoàn tất bộ đề Quiz với {len(quiz_data)} câu hỏi trắc nghiệm bài bản.")
        return quiz_data
        
    except json.JSONDecodeError as json_err:
        logger.error(f"💥 Lỗi phân tách cú pháp JSON từ đầu ra của LLM: {str(json_err)}")
        return []
    except Exception as general_err:
        logger.error(f"❌ Sự cố không xác định khi gọi AI sinh đề Quiz: {str(general_err)}")
        return []
import os
import requests
import json
from config import client

def transcribe_audio_with_whisper(audio_url: str) -> str:
    """Tải âm thanh tạm thời và chuyển giọng nói thành văn bản thông qua Whisper-large-v3"""
    audio_res = requests.get(audio_url)
    temp_file = "temp_podcast.mp3"
    
    with open(temp_file, "wb") as f:
        f.write(audio_res.content)
        
    try:
        with open(temp_file, "rb") as file:
            translation = client.audio.transcriptions.create(
                file=(temp_file, file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        transcript_text = translation
    finally:
        # Đảm bảo luôn dọn dẹp file rác khỏi ổ đĩa cục bộ kể cả khi gặp lỗi
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    return transcript_text

def generate_quiz_from_transcript(transcript_text: str) -> list:
    """Gọi mô hình Llama-3.1-8b-instant thiết lập cấu trúc đề trắc nghiệm chuẩn JSON"""
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
    return quiz_json["quiz"]
import requests
from bs4 import BeautifulSoup
import re
import json

def get_audio_url_from_apple(apple_url: str) -> str:
    """Cào cấu trúc trang Apple Podcast để lấy link trực tiếp file âm thanh gốc"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(apple_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cách 1: Tìm trong thẻ Json-LD cấu trúc dữ liệu
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            if "contentUrl" in script.text:
                return json.loads(script.text).get("contentUrl")
                
        # Cách 2: Quét Regex tìm chuỗi URL có định dạng file âm thanh
        match = re.search(r'https://[^"]+\.(?:mp3|m4a|mp4)', response.text)
        if match:
            return match.group(0)
    except:
        return None
    return None

# --- KHOẢNG TRỐNG ĐỂ VIẾT TIẾP ENHANCEMENT 1 ---
# def get_episode_list_from_show(show_url: str):
#     """Hàm cào danh sách postcast từ link show tổng"""
#     pass
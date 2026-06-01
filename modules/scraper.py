import requests
from bs4 import BeautifulSoup
import re
import json
import xml.etree.ElementTree as ET

def get_audio_url_from_apple(apple_url: str) -> str:
    """
    Bóc tách và tìm link trực tiếp file âm thanh (.mp3/.m4a) từ tập phim.
    Hỗ trợ xử lý cả link web Apple Podcast và link chuyển hướng trực tiếp từ RSS Feed.
    """
    if not apple_url:
        return None
        
    # Loại bỏ khoảng trắng thừa
    apple_url = apple_url.strip()
    
    # --- BƯỚC 1: KIỂM TRA NẾU LINK ĐÃ LÀ FILE ÂM THANH TRỰC TIẾP ---
    # Rất nhiều link từ RSS Feed trỏ thẳng tới file media .mp3 của máy chủ phát sóng
    if re.search(r'\.(?:mp3|m4a|mp4|aac|ogg)(?:\?|$)', apple_url, re.IGNORECASE):
        return apple_url
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # --- BƯỚC 2: XỬ LÝ LƯU LƯỢNG CHUYỂN HƯỚNG (FOLLOW REDIRECTS) ---
        # Gửi request và cho phép tự động chuyển hướng để lấy URL đích thực sự
        response = requests.get(apple_url, headers=headers, timeout=15, allow_redirects=True)
        final_url = response.url
        
        # Kiểm tra nếu sau khi chuyển hướng, URL đích đã biến thành file âm thanh trực tiếp
        if re.search(r'\.(?:mp3|m4a|mp4|aac|ogg)(?:\?|$)', final_url, re.IGNORECASE):
            return final_url
            
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # --- BƯỚC 3: CÀO CẤU TRÚC HTML (Nếu URL cuối vẫn là trang Web) ---
        # Cách 3.1: Tìm trong thẻ Json-LD cấu trúc dữ liệu của Apple
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.text)
                if isinstance(data, dict) and "contentUrl" in data:
                    return data["contentUrl"]
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "contentUrl" in item:
                            return item["contentUrl"]
            except:
                continue
                
        # Cách 3.2: Tìm trong các thuộc tính HTML5 nhúng (Thẻ audio)
        audio_tag = soup.find('audio')
        if audio_tag and audio_tag.get('src'):
            return audio_tag.get('src')
            
        # Cách 3.3: Quét Regex tìm đuôi mở rộng file âm thanh xuất hiện trong mã nguồn
        match = re.search(r'https://[^\\\"]+\.(?:mp3|m4a|mp4|aac)[^\\\"]*', html_text, re.IGNORECASE)
        if match:
            return match.group(0)
            
    except Exception as e:
        print(f"⚠️ Lỗi cào link audio chi tiết: {e}")
        return None
        
    return None

def get_episode_list_from_show(show_url: str) -> dict:
    """
    Hàm lấy danh sách tập bài học chuẩn xác bằng cách bóc tách ID của Show
    và sử dụng API Lookup chính thức từ Apple iTunes để lấy RSS Feed gốc.
    """
    if not show_url:
        return None
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        id_match = re.search(r'/id(\d+)', show_url)
        rss_url = None
        
        if id_match:
            show_id = id_match.group(1)
            lookup_url = f"https://itunes.apple.com/lookup?id={show_id}&entity=podcast"
            lookup_res = requests.get(lookup_url, headers=headers, timeout=10)
            
            if lookup_res.status_code == 200:
                lookup_data = lookup_res.json()
                if lookup_data.get("resultCount", 0) > 0:
                    rss_url = lookup_data["results"][0].get("feedUrl")
        
        if not rss_url:
            print("⚠️ API Lookup không phản hồi, chuyển sang phương án quét Regex thô...")
            res = requests.get(show_url, headers=headers, timeout=15)
            html_content = res.text
            
            rss_match = re.search(r'\"rssUrl\"\s*:\s*\"(https://[^\"]+)\"', html_content)
            if rss_match:
                rss_url = rss_match.group(1)
            else:
                rss_match_fallback = re.search(r'(https://[^\\\"]+feed[^\\\"]*\.xml[^\\\"]*)', html_content, re.IGNORECASE)
                if rss_match_fallback:
                    rss_url = rss_match_fallback.group(1)
                    
        if not rss_url:
            print("⚠️ Không tìm thấy URL RSS Feed hợp lệ cho Show này.")
            return None
            
        rss_url = rss_url.replace("\\/", "/").replace("\\u002F", "/")
        print(f"✅ Đường dẫn RSS Feed được xử lý: {rss_url}")
        
        rss_res = requests.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(rss_res.content)
        channel = root.find('channel')
        
        if channel is None:
            return None
            
        show_title = channel.find('title').text if channel.find('title') is not None else "Podcast Show"
        
        show_image = ""
        img_tag = channel.find('image')
        if img_tag is not None and img_tag.find('url') is not None:
            show_image = img_tag.find('url').text
        else:
            itunes_img = channel.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            if itunes_img is not None:
                show_image = itunes_img.get('href')

        episodes = []
        for item in channel.findall('item'):
            title = item.find('title').text if item.find('title') is not None else "Untitled Episode"
            
            # ƯU TIÊN LẤY LINK FILE AM THANH TRỰC TIẾP TỪ THẺ ENCLOSURE CỦA RSS FEED
            enclosure = item.find('enclosure')
            link = ""
            if enclosure is not None and enclosure.get('url'):
                link = enclosure.get('url')
            else:
                link = item.find('link').text if item.find('link') is not None else ""
            
            ep_image = ""
            itunes_ep_img = item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            if itunes_ep_img is not None:
                ep_image = itunes_ep_img.get('href')
            else:
                ep_image = show_image
                
            episodes.append({
                "title": title,
                "apple_url": link,
                "image": ep_image
            })
            
        return {
            "show_title": show_title,
            "show_image": show_image,
            "episodes": episodes
        }
    except Exception as e:
        print(f"⚠️ Lỗi xử lý cào RSS Show chi tiết: {e}")
        return None
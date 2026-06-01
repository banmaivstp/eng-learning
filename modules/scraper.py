import requests
from bs4 import BeautifulSoup
import re
import json
import xml.etree.ElementTree as ET

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
        match = re.search(r'https://[^\"]+\.(?:mp3|m4a|mp4)', response.text)
        if match:
            return match.group(0)
    except:
        return None
    return None

def get_episode_list_from_show(show_url: str) -> dict:
    """
    Hàm cào danh sách các tập bài học từ link Show tổng thông qua việc bóc tách 
    đường dẫn RSS Feed nhúng trong mã nguồn HTML.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(show_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm link RSS Feed dạng xml trong thẻ head
        rss_link_tag = soup.find('link', type='application/rss+xml')
        if not rss_link_tag or not rss_link_tag.get('href'):
            match = re.search(r'https://[^\s"]+/feed\.xml|https://feeds\.[^\s"]+', response.text)
            rss_url = match.group(0) if match else None
        else:
            rss_url = rss_link_tag.get('href')
            
        if not rss_url:
            return None

        # Đọc và phân tách cây dữ liệu XML từ RSS Feed nhận được
        feed_res = requests.get(rss_url, headers=headers)
        root = ET.fromstring(feed_res.content)
        channel = root.find('channel')
        
        show_title = channel.find('title').text if channel.find('title') is not None else "Podcast Show"
        
        # Lấy ảnh bìa đại diện cho Show lớn (Xử lý namespace itunes hoặc thẻ image tiêu chuẩn)
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
            link = item.find('link').text if item.find('link') is not None else ""
            
            # Lấy ảnh bìa riêng của từng tập (nếu có), nếu không có dùng fallback về ảnh show chính
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
        print(f"Lỗi hệ thống cào RSS Show: {e}")
        return None
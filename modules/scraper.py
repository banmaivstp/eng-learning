import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlencode, urljoin, parse_qs, urlunparse

logger = logging.getLogger("modules.scraper")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


# ==========================================================
# AUDIO URL
# ==========================================================

def get_audio_url_from_apple(apple_url: str) -> str:
    """
    Tìm link audio trực tiếp từ Apple Podcast episode.
    """
    if not apple_url:
        return None

    apple_url = apple_url.strip()
    logger.info(f"🔍 Tìm audio URL: {apple_url}")

    if re.search(r"\.(mp3|m4a|aac|ogg|mp4)(\?|$)", apple_url, re.IGNORECASE):
        logger.info("✅ URL đã là media file")
        return apple_url

    try:
        response = session.get(apple_url, timeout=20, allow_redirects=True)
        response.raise_for_status()
        final_url = response.url

        if re.search(r"\.(mp3|m4a|aac|ogg|mp4)(\?|$)", final_url, re.IGNORECASE):
            logger.info("✅ Redirect tới media file")
            return final_url

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if "contentUrl" in data:
                        return data["contentUrl"]
                    media = data.get("associatedMedia")
                    if isinstance(media, dict) and media.get("contentUrl"):
                        return media["contentUrl"]
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("contentUrl"):
                            return item["contentUrl"]
            except Exception:
                continue

        audio_tag = soup.find("audio")
        if audio_tag and audio_tag.get("src"):
            return audio_tag["src"]

        source_tag = soup.find("source")
        if source_tag and source_tag.get("src"):
            return source_tag["src"]

        matches = re.findall(
            r'https://[^\s"\']+\.(?:mp3|m4a|aac|ogg|mp4)(?:\?[^\s"\']*)?',
            html, re.IGNORECASE
        )
        if matches:
            return matches[0]

        logger.warning("⚠️ Không tìm được audio URL")
        return apple_url

    except Exception as e:
        logger.error(f"🚨 Lỗi lấy audio URL: {e}")
        return apple_url


# ==========================================================
# RSS URL
# ==========================================================

def _get_rss_url(show_url: str) -> str:
    """
    Tìm RSS Feed bằng Apple Lookup API.
    """
    try:
        match = re.search(r"/id(\d+)", show_url)
        if not match:
            return None

        show_id = match.group(1)
        lookup_url = f"https://itunes.apple.com/lookup?id={show_id}&entity=podcast"
        logger.info(f"📡 Lookup Apple API show_id={show_id}")

        res = session.get(lookup_url, timeout=15)
        res.raise_for_status()
        data = res.json()

        if data.get("resultCount", 0) > 0:
            rss_url = data["results"][0].get("feedUrl")
            if rss_url:
                logger.info(f"✅ RSS Feed: {rss_url}")
                return rss_url

    except Exception as e:
        logger.warning(f"⚠️ Apple Lookup API lỗi: {e}")

    return None


# ==========================================================
# RSS PAGINATION — DETECT HOST & FETCH ALL PAGES
# ==========================================================

def _detect_host(rss_url: str) -> str:
    """
    Nhận diện podcast host từ RSS URL để áp dụng đúng pagination strategy.
    """
    url_lower = rss_url.lower()
    host_patterns = [
        ("buzzsprout",  "buzzsprout"),
        ("libsyn",      "libsyn"),
        ("libsynpro",   "libsynpro"),
        ("megaphone",   "megaphone"),
        ("simplecast",  "simplecast"),
        ("podbean",     "podbean"),
        ("spreaker",    "spreaker"),
        ("transistor",  "transistor"),
        ("anchor",      "anchor"),
        ("spotify",     "anchor"),      # Anchor đã đổi tên thành Spotify for Podcasters
        ("acast",       "acast"),
        ("omnycontent", "omny"),
        ("omny.fm",     "omny"),
        ("squarespace", "squarespace"),
        ("soundcloud",  "soundcloud"),
        ("podtrac",     "podtrac"),     # redirect tracker, không page
        ("feedburner",  "feedburner"),
        ("sticher",     "stitcher"),
    ]
    for pattern, host_name in host_patterns:
        if pattern in url_lower:
            logger.debug(f"🏠 Detected host: {host_name} (pattern='{pattern}')")
            return host_name
    logger.debug("🏠 Host không nhận dạng được — dùng strategy mặc định.")
    return "unknown"


def _fetch_all_rss_items(rss_url: str) -> tuple[str, str, str, list]:
    """
    Fetch toàn bộ episodes từ RSS, xử lý pagination theo từng host.

    Returns:
        (show_title, show_image, show_description, items_list)
        items_list: list[Element] — các <item> node từ XML

    Pagination strategies:
        - Buzzsprout  : không cần page, feed đủ (thường)
        - Libsyn      : thêm ?libsyn_limit=0 để lấy tất cả
        - Megaphone   : feed đủ, không page
        - Simplecast  : feed đủ theo default
        - Podbean     : feed đủ
        - Spreaker    : thêm ?limit=all hoặc loop page
        - Omny        : hỗ trợ ?page=N, loop đến hết
        - Acast       : feed đủ
        - unknown     : thử ?paged=1,2,... và atom:link[@rel=next]
    """
    host = _detect_host(rss_url)

    # --- Strategy theo host ---
    if host == "libsyn":
        # Libsyn hỗ trợ limit=0 để trả về tất cả items
        rss_url_full = _append_param(rss_url, "libsyn_limit", "0")
        logger.info(f"📄 Libsyn strategy: fetching with libsyn_limit=0")
        return _fetch_single_feed(rss_url_full)

    elif host == "omny":
        # Omny hỗ trợ pagination qua ?page=N (1-indexed)
        logger.info("📄 Omny strategy: paginated fetch")
        return _fetch_paginated_omny(rss_url)

    elif host in ("buzzsprout", "megaphone", "simplecast", "podbean",
                  "transistor", "acast", "unknown", "podtrac",
                  "feedburner", "soundcloud", "squarespace", "spreaker"):
        # Các host này hoặc trả đủ hoặc cần thử atom:link[@rel=next]
        logger.info(f"📄 {host} strategy: single fetch + atom:link next fallback")
        return _fetch_with_atom_next(rss_url)

    else:
        logger.info(f"📄 Default strategy: single fetch + atom:link next")
        return _fetch_with_atom_next(rss_url)


def _append_param(url: str, key: str, value: str) -> str:
    """Thêm hoặc override query parameter vào URL."""
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[key] = [value]
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse(parsed._replace(query=new_query))


def _parse_feed(xml_content: bytes) -> tuple[ET.Element, ET.Element]:
    """Parse XML và trả về (root, channel). Raise nếu lỗi."""
    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS không có <channel>")
    return root, channel


def _extract_meta(channel: ET.Element) -> tuple[str, str]:
    """Trích xuất show_title và show_image từ channel element."""
    title_tag = channel.find("title")
    show_title = title_tag.text if title_tag is not None else "Podcast"

    show_image = ""
    image_tag = channel.find("image")
    if image_tag is not None and image_tag.find("url") is not None:
        show_image = image_tag.find("url").text or ""
    else:
        itunes_img = channel.find(
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}image"
        )
        if itunes_img is not None:
            show_image = itunes_img.get("href", "")

    return show_title, show_image


def _fetch_single_feed(rss_url: str) -> tuple[str, str, list]:
    """Fetch 1 RSS URL, trả về (show_title, show_image, items)."""
    rss_url = rss_url.replace("\\/", "/").replace("\\u002F", "/")
    res = session.get(rss_url, timeout=20)
    res.raise_for_status()
    root, channel = _parse_feed(res.content)
    show_title, show_image = _extract_meta(channel)
    items = channel.findall("item")
    logger.debug(f"  → _fetch_single_feed: {len(items)} items từ {rss_url[:80]}")
    return show_title, show_image, items


def _get_atom_next(root: ET.Element, channel: ET.Element) -> str | None:
    """
    Tìm URL trang tiếp theo từ atom:link[@rel='next'].
    Nhiều feed dùng Atom namespace để khai báo pagination.
    """
    ATOM_NS = "http://www.w3.org/2005/Atom"
    # Tìm ở cả root lẫn channel
    for scope in (root, channel):
        for link in scope.findall(f"{{{ATOM_NS}}}link"):
            if link.get("rel") == "next":
                href = link.get("href", "").strip()
                if href:
                    return href
    return None


def _fetch_with_atom_next(rss_url: str, max_pages: int = 20) -> tuple[str, str, list]:
    """
    Fetch RSS với fallback atom:link[@rel='next'] pagination.
    Dừng khi không còn trang next hoặc trang trả về 0 items mới.
    """
    all_items = []
    seen_urls = set()
    show_title = "Podcast"
    show_image = ""
    current_url = rss_url.replace("\\/", "/").replace("\\u002F", "/")

    for page_num in range(1, max_pages + 1):
        logger.info(f"  📃 Fetching page {page_num}: {current_url[:80]}...")
        try:
            res = session.get(current_url, timeout=20)
            res.raise_for_status()
            root, channel = _parse_feed(res.content)
        except Exception as e:
            logger.warning(f"  ⚠️ Lỗi fetch page {page_num}: {e}")
            break

        if page_num == 1:
            show_title, show_image = _extract_meta(channel)

        items = channel.findall("item")
        new_items = 0
        for item in items:
            # Dedup theo enclosure URL hoặc title
            enclosure = item.find("enclosure")
            ep_url = enclosure.get("url", "") if enclosure is not None else ""
            title_el = item.find("title")
            ep_title = title_el.text or "" if title_el is not None else ""
            dedup_key = ep_url or ep_title
            if dedup_key and dedup_key not in seen_urls:
                seen_urls.add(dedup_key)
                all_items.append(item)
                new_items += 1

        logger.debug(f"    Page {page_num}: {len(items)} items, {new_items} new → total {len(all_items)}")

        if new_items == 0:
            logger.info(f"  ✅ Không có item mới ở page {page_num} — dừng pagination.")
            break

        next_url = _get_atom_next(root, channel)
        if not next_url:
            logger.info(f"  ✅ Không có atom:link next ở page {page_num} — feed đã hết.")
            break

        current_url = next_url

    logger.info(f"  📦 Tổng cộng {len(all_items)} items sau {page_num} page(s).")
    return show_title, show_image, all_items


def _fetch_paginated_omny(rss_url: str, max_pages: int = 50) -> tuple[str, str, list]:
    """
    Omny Studio dùng ?page=N (bắt đầu từ 1).
    Dừng khi page trả về 0 items.
    """
    all_items = []
    seen_urls = set()
    show_title = "Podcast"
    show_image = ""

    # Strip page param nếu đã có
    base_url = re.sub(r'[?&]page=\d+', '', rss_url).rstrip('?&')

    for page_num in range(1, max_pages + 1):
        sep = "&" if "?" in base_url else "?"
        page_url = f"{base_url}{sep}page={page_num}"
        logger.info(f"  📃 Omny page {page_num}: {page_url[:80]}...")

        try:
            res = session.get(page_url, timeout=20)
            res.raise_for_status()
            root, channel = _parse_feed(res.content)
        except Exception as e:
            logger.warning(f"  ⚠️ Omny page {page_num} lỗi: {e}")
            break

        if page_num == 1:
            show_title, show_image = _extract_meta(channel)

        items = channel.findall("item")
        if not items:
            logger.info(f"  ✅ Omny page {page_num} trống — dừng.")
            break

        new_items = 0
        for item in items:
            enclosure = item.find("enclosure")
            ep_url = enclosure.get("url", "") if enclosure is not None else ""
            title_el = item.find("title")
            ep_title = title_el.text or "" if title_el is not None else ""
            dedup_key = ep_url or ep_title
            if dedup_key and dedup_key not in seen_urls:
                seen_urls.add(dedup_key)
                all_items.append(item)
                new_items += 1

        logger.debug(f"    Omny page {page_num}: {len(items)} items, {new_items} new → total {len(all_items)}")

        if new_items == 0:
            logger.info(f"  ✅ Không có item mới — dừng Omny pagination.")
            break

    logger.info(f"  📦 Omny tổng cộng {len(all_items)} items.")
    return show_title, show_image, all_items


# ==========================================================
# ITEM PARSER — trích xuất episode data từ XML item element
# ==========================================================

def _parse_item(item: ET.Element, fallback_image: str) -> dict:
    """
    Trích xuất thông tin episode từ một <item> XML element.
    Trả về dict: title, apple_url, image.
    """
    # Title
    title = "Untitled Episode"
    title_tag = item.find("title")
    if title_tag is not None and title_tag.text:
        title = title_tag.text.strip()

    # Audio URL — ưu tiên enclosure, fallback link
    episode_url = ""
    enclosure = item.find("enclosure")
    if enclosure is not None and enclosure.get("url"):
        episode_url = enclosure.get("url")
    else:
        link_tag = item.find("link")
        if link_tag is not None and link_tag.text:
            episode_url = link_tag.text.strip()

    # Episode image — ưu tiên itunes:image, fallback show image
    ep_image = fallback_image
    itunes_ep_img = item.find(
        "{http://www.itunes.com/dtds/podcast-1.0.dtd}image"
    )
    if itunes_ep_img is not None and itunes_ep_img.get("href"):
        ep_image = itunes_ep_img.get("href")

    return {
        "title": title,
        "apple_url": episode_url,
        "image": ep_image,
    }


# ==========================================================
# PUBLIC API — SHOW
# ==========================================================

def get_episode_list_from_show(show_url: str) -> dict:
    """
    Lấy toàn bộ danh sách episodes từ Apple Podcast show URL.

    Xử lý:
    1. Lấy RSS feed URL qua Apple iTunes Lookup API
    2. Detect podcast host từ RSS URL
    3. Fetch tất cả episodes với pagination phù hợp theo host
    4. Parse từng item thành dict chuẩn

    Returns:
        {
            "show_title": str,
            "show_image": str,
            "episodes": [{"title", "apple_url", "image"}, ...]
        }
        hoặc None nếu lỗi.
    """
    if not show_url:
        return None

    logger.info(f"📥 Đang tải show: {show_url}")

    try:
        # Bước 1: Lấy RSS URL
        rss_url = _get_rss_url(show_url)
        if not rss_url:
            logger.error("❌ Không lấy được RSS Feed")
            return None

        # Bước 2 + 3: Fetch toàn bộ items với pagination
        show_title, show_image, all_items = _fetch_all_rss_items(rss_url)

        # Bước 4: Parse từng item
        episodes = [_parse_item(item, show_image) for item in all_items]

        logger.info(f"✅ Đã lấy {len(episodes)} episodes — show: '{show_title}'")

        return {
            "show_title": show_title,
            "show_image": show_image,
            "episodes": episodes
        }

    except Exception as e:
        logger.error(f"🚨 Lỗi scraper: {e}")
        return None

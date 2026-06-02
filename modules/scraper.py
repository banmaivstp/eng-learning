import requests
from bs4 import BeautifulSoup
import re
import json
import logging
import xml.etree.ElementTree as ET

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

    # Nếu đã là mp3/m4a
    if re.search(
        r"\.(mp3|m4a|aac|ogg|mp4)(\?|$)",
        apple_url,
        re.IGNORECASE
    ):
        logger.info("✅ URL đã là media file")
        return apple_url

    try:

        response = session.get(
            apple_url,
            timeout=20,
            allow_redirects=True
        )

        response.raise_for_status()

        final_url = response.url

        if re.search(
            r"\.(mp3|m4a|aac|ogg|mp4)(\?|$)",
            final_url,
            re.IGNORECASE
        ):
            logger.info("✅ Redirect tới media file")
            return final_url

        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # ==================================================
        # JSON-LD
        # ==================================================

        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):
            try:

                if not script.string:
                    continue

                data = json.loads(script.string)

                if isinstance(data, dict):

                    if "contentUrl" in data:
                        return data["contentUrl"]

                    media = data.get("associatedMedia")

                    if isinstance(media, dict):
                        if media.get("contentUrl"):
                            return media["contentUrl"]

                elif isinstance(data, list):

                    for item in data:
                        if (
                            isinstance(item, dict)
                            and item.get("contentUrl")
                        ):
                            return item["contentUrl"]

            except Exception:
                continue

        # ==================================================
        # audio tag
        # ==================================================

        audio_tag = soup.find("audio")

        if audio_tag and audio_tag.get("src"):
            return audio_tag["src"]

        source_tag = soup.find("source")

        if source_tag and source_tag.get("src"):
            return source_tag["src"]

        # ==================================================
        # regex fallback
        # ==================================================

        matches = re.findall(
            r'https://[^\s"\']+\.(?:mp3|m4a|aac|ogg|mp4)(?:\?[^\s"\']*)?',
            html,
            re.IGNORECASE
        )

        if matches:
            return matches[0]

        logger.warning("⚠️ Không tìm được audio URL")

        return apple_url

    except Exception as e:

        logger.error(
            f"🚨 Lỗi lấy audio URL: {e}"
        )

        return apple_url


# ==========================================================
# RSS URL
# ==========================================================

def _get_rss_url(show_url: str) -> str:
    """
    Tìm RSS Feed bằng Apple Lookup API.
    """

    try:

        match = re.search(
            r"/id(\d+)",
            show_url
        )

        if not match:
            return None

        show_id = match.group(1)

        lookup_url = (
            f"https://itunes.apple.com/lookup"
            f"?id={show_id}&entity=podcast"
        )

        logger.info(
            f"📡 Lookup Apple API show_id={show_id}"
        )

        res = session.get(
            lookup_url,
            timeout=15
        )

        res.raise_for_status()

        data = res.json()

        if data.get("resultCount", 0) > 0:

            rss_url = (
                data["results"][0]
                .get("feedUrl")
            )

            if rss_url:
                logger.info(
                    f"✅ RSS Feed: {rss_url}"
                )
                return rss_url

    except Exception as e:

        logger.warning(
            f"⚠️ Apple Lookup API lỗi: {e}"
        )

    return None


# ==========================================================
# SHOW
# ==========================================================

def get_episode_list_from_show(show_url: str) -> dict:

    if not show_url:
        return None

    logger.info(
        f"📥 Đang tải show: {show_url}"
    )

    try:

        rss_url = _get_rss_url(show_url)

        if not rss_url:

            logger.error(
                "❌ Không lấy được RSS Feed"
            )

            return None

        rss_url = (
            rss_url
            .replace("\\/", "/")
            .replace("\\u002F", "/")
        )

        rss_res = session.get(
            rss_url,
            timeout=20
        )

        rss_res.raise_for_status()

        xml_content = rss_res.content

        try:
            root = ET.fromstring(xml_content)

        except ET.ParseError as e:

            logger.error(
                f"🚨 RSS XML lỗi format: {e}"
            )

            return None

        channel = root.find("channel")

        if channel is None:

            logger.error(
                "❌ RSS không có channel"
            )

            return None

        show_title = "Podcast"

        title_tag = channel.find("title")

        if title_tag is not None:
            show_title = title_tag.text

        show_image = ""

        image_tag = channel.find("image")

        if (
            image_tag is not None
            and image_tag.find("url") is not None
        ):
            show_image = image_tag.find("url").text

        else:

            itunes_img = channel.find(
                "{http://www.itunes.com/dtds/podcast-1.0.dtd}image"
            )

            if itunes_img is not None:
                show_image = itunes_img.get("href", "")

        episodes = []

        for item in channel.findall("item"):

            title = "Untitled Episode"

            title_tag = item.find("title")

            if (
                title_tag is not None
                and title_tag.text
            ):
                title = title_tag.text

            enclosure = item.find("enclosure")

            episode_url = ""

            if (
                enclosure is not None
                and enclosure.get("url")
            ):
                episode_url = enclosure.get("url")

            else:

                link_tag = item.find("link")

                if (
                    link_tag is not None
                    and link_tag.text
                ):
                    episode_url = link_tag.text

            ep_image = show_image

            itunes_ep_img = item.find(
                "{http://www.itunes.com/dtds/podcast-1.0.dtd}image"
            )

            if (
                itunes_ep_img is not None
                and itunes_ep_img.get("href")
            ):
                ep_image = itunes_ep_img.get("href")

            episodes.append({
                "title": title,
                "apple_url": episode_url,
                "image": ep_image
            })

        logger.info(
            f"✅ Đã lấy {len(episodes)} episodes"
        )

        return {
            "show_title": show_title,
            "show_image": show_image,
            "episodes": episodes
        }

    except Exception as e:

        logger.error(
            f"🚨 Lỗi scraper: {e}"
        )

        return None
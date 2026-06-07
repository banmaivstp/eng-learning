"""
views/podcast_list_view.py
===========================
TẦNG GIAO DIỆN (VIEW) — Màn hình "Danh sách bài học".
Hiển thị tất cả episodes của một show đã chọn.

Luồng điều hướng:
    show_list_view → (click show card) → podcast_list_view → (click episode) → quiz_detail_view

Quy tắc code:
    - KHÔNG thay đổi logic DB/scraper — chỉ thay đổi UI
    - CSS được inject qua views/podcast_list_css.py (inject_podcast_list_view_css) — KHÔNG thêm CSS inline lớn
    - Log đầy đủ theo level: DEBUG, INFO, WARNING, ERROR
    - Không cuộn trang quá nhiều — tối ưu "vùng đất vàng"
"""

import streamlit as st
import logging

# TẦNG STYLE: Import CSS độc lập của màn hình này
from views.podcast_list_css import inject_podcast_list_view_css

logger = logging.getLogger("views.podcast_list_view")


# =====================================================
# SAMPLE EPISODES — fallback khi DB chưa có episode nào
# =====================================================
SAMPLE_EPISODES = [
    {
        "id": "ep-sample-1",
        "title": 'Bài 156: Stop Saying "Okay" All the Time — Sound More Natural in English',
        "audio_url": None,
        "duration": "07:12",
        "created_at": "2026-06-01"
    },
    {
        "id": "ep-sample-2",
        "title": 'Bài 155: Stop Saying "Maybe" All the Time | Sound More Natural in English',
        "audio_url": None,
        "duration": "06:48",
        "created_at": "2026-05-28"
    },
    {
        "id": "ep-sample-3",
        "title": 'Bài 154: Stop Saying "Really" All the Time — Sound More Natural in English',
        "audio_url": None,
        "duration": "08:55",
        "created_at": "2026-05-21"
    },
]


def _fetch_episodes_from_db(supabase_client, show_id: str) -> list:
    """
    Truy vấn danh sách episodes từ Supabase theo show_id.
    Trả về list dicts: id, title, audio_url, created_at.
    Fallback: SAMPLE_EPISODES nếu lỗi hoặc DB rỗng.
    """
    if not supabase_client:
        logger.warning("⚠️ podcast_list_view: supabase_client = None — dùng sample episodes.")
        return SAMPLE_EPISODES

    if not show_id or show_id.startswith("sample-"):
        logger.info("ℹ️ podcast_list_view: show_id là sample — dùng sample episodes.")
        return SAMPLE_EPISODES

    try:
        logger.debug(f"🔍 podcast_list_view: Query episodes cho show_id='{show_id}'")
        res = supabase_client.table("episodes").select(
            "id, title, audio_url, created_at"
        ).eq("show_id", show_id).order("created_at", desc=True).execute()

        if res.data:
            logger.info(f"✅ podcast_list_view: Fetched {len(res.data)} episodes cho show '{show_id}'.")
            return res.data
        else:
            logger.info(f"ℹ️ podcast_list_view: Không có episode nào cho show '{show_id}' — dùng sample.")
            return SAMPLE_EPISODES

    except Exception as e:
        logger.error(f"🚨 podcast_list_view: Lỗi query Supabase 'episodes': {e}")
        return SAMPLE_EPISODES


def _render_episode_row(ep: dict, ep_idx: int, show_cover: str | None):
    """
    Render một hàng episode theo pattern st.columns() — giống dashboard Recent Shows.
    - Cột trái (col_info): HTML visual [thumbnail + badge + title + duration]
    - Cột phải (col_btn):  st.button() thật, styled thành pill cyan qua CSS .pcl-start-btn-wrap

    Không dùng overlay button ẩn hay CSS absolute/opacity hack.

    Args:
        ep: dict episode từ DB hoặc sample
        ep_idx: index để tạo unique key cho button
        show_cover: cover image URL của show (dùng làm thumb episode)
    """
    import html as _html

    ep_id       = ep.get("id", f"ep-{ep_idx}")
    ep_title    = _html.escape(ep.get("title", f"Episode {ep_idx + 1}"))
    ep_duration = ep.get("duration", "")
    badge_num   = ep_idx + 1

    # Thumbnail
    if show_cover:
        safe_cover = _html.escape(show_cover, quote=True)
        thumb_html = f'<img src="{safe_cover}" class="pcl-ep-thumb" alt="ep"/>'
    else:
        thumb_html = '<div class="pcl-ep-thumb-placeholder">&#127911;</div>'

    safe_dur = _html.escape(str(ep_duration)) if ep_duration else ""
    duration_html = (
        f'<div class="pcl-ep-duration">'
        f'<span class="pcl-ep-duration-icon">&#127911;</span> {safe_dur}</div>'
        if safe_dur else ""
    )

    col_info, col_btn = st.columns([3.6, 1.0], gap="small")

    with col_info:
        ep_html = (
            f'<div class="pcl-episode-row">'
            + thumb_html
            + '<div class="pcl-ep-info">'
            + f'<div class="pcl-ep-badge">B&#224;i {badge_num}</div>'
            + f'<div class="pcl-ep-title">{ep_title}</div>'
            + duration_html
            + '</div></div>'
        )
        st.markdown(ep_html, unsafe_allow_html=True)

    with col_btn:
        st.markdown('<div class="pcl-start-btn-wrap">', unsafe_allow_html=True)
        btn_key = f"pcl_ep_{ep_id}_{ep_idx}"
        if st.button("▶ Start", key=btn_key, use_container_width=False):
            logger.info(f"🎯 podcast_list_view: Chọn episode '{ep_title}' (id={ep_id})")
            st.session_state["selected_episode"] = ep
            st.session_state["current_page"] = "Episode Detail"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def render_podcast_list_page(supabase_client=None):
    """
    Màn hình chính: hiển thị danh sách episodes của show đã chọn.

    Điều kiện tiên quyết:
        st.session_state["selected_show"] phải được set trước khi gọi hàm này
        (được set bởi show_list_view khi user click vào một show card).

    Args:
        supabase_client: Supabase client từ config.py

    Logs:
        [INFO]  Khi function được gọi và hoàn thành
        [DEBUG] Từng bước render: header, fetch, rows
        [WARNING] Khi thiếu show_id hoặc dùng sample data
        [ERROR]  Khi lỗi Supabase
    """
    logger.info("📋 podcast_list_view: render_podcast_list_page() — START.")

    # Inject CSS tầng Style độc lập của màn hình này
    inject_podcast_list_view_css()

    # ─────────────────────────────────────────────
    # 0. LẤY THÔNG TIN SHOW ĐÃ CHỌN TỪ SESSION
    # ─────────────────────────────────────────────
    selected_show = st.session_state.get("selected_show", {})
    if not selected_show:
        logger.warning("⚠️ podcast_list_view: Không có selected_show trong session. Redirect về show list.")
        st.warning("Không có show nào được chọn. Vui lòng quay lại thư viện.")
        if st.button("← Your Library", key="pcl_back_no_show"):
            st.session_state["current_page"] = "Học tập"
            st.rerun()
        return

    show_id = selected_show.get("id", "")
    show_title = selected_show.get("title", "Untitled Show")
    show_cover = selected_show.get("cover_image", None)
    show_ep_count = selected_show.get("episode_count", 0)

    logger.debug(f"📺 podcast_list_view: show='{show_title}', id='{show_id}', cover={'yes' if show_cover else 'no'}")

    # ─────────────────────────────────────────────
    # 1. PAGE HEADER — Back button + Show info
    # ─────────────────────────────────────────────

    # Đã xoá đoạn HTML hiển thị text tĩnh để tránh trùng lặp chữ (Yêu cầu số 1)

    # Đổi chữ hiển thị của Streamlit Button thành "← Your Library" (Yêu cầu số 2)
    if st.button("← Your Library", key="pcl_back_btn", use_container_width=False):
        logger.info("📌 podcast_list_view: User quay lại show list.")
        st.session_state["current_page"] = "Học tập"
        st.rerun()

    # Page title + show subtitle
    cover_html = (
        f'<img src="{show_cover}" class="pcl-header-cover" alt="cover"/>'
        if show_cover
        else '<div class="pcl-header-cover-placeholder">📚</div>'
    )

    st.markdown(f"""
    <div class="pcl-page-header">
        <div class="pcl-header-icon-area">{cover_html}</div>
        <div class="pcl-header-text">
            <div class="pcl-page-title">📚 Danh sách bài học</div>
            <div class="pcl-page-show-name">{show_title}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    logger.debug("📝 podcast_list_view: Rendered page header.")

    # ─────────────────────────────────────────────
    # 2. SEARCH BAR + SORT DROPDOWN (UI only)
    # ─────────────────────────────────────────────
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_query = st.text_input(
            label="Tìm bài học",
            placeholder="🔍  Tìm bài học...",
            label_visibility="collapsed",
            key="pcl_search_input"
        )
    with col_sort:
        sort_option = st.selectbox(
            label="Sắp xếp",
            options=["Mới nhất", "Cũ nhất"],
            label_visibility="collapsed",
            key="pcl_sort_select"
        )
    logger.debug(f"🔍 podcast_list_view: search='{search_query}', sort='{sort_option}'")

    # ─────────────────────────────────────────────
    # 3. FETCH EPISODES
    # ─────────────────────────────────────────────
    episodes = _fetch_episodes_from_db(supabase_client, show_id)
    logger.debug(f"📦 podcast_list_view: Fetched {len(episodes)} episodes.")

    # Apply search filter
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        episodes = [ep for ep in episodes if q in ep.get("title", "").lower()]
        logger.debug(f"🔍 podcast_list_view: After filter '{q}': {len(episodes)} episodes.")

    # Apply sort
    if sort_option == "Cũ nhất":
        episodes = list(reversed(episodes))
        logger.debug("📊 podcast_list_view: Sorted ascending (oldest first).")

    # ─────────────────────────────────────────────
    # 4. EPISODE COUNT LABEL
    # ─────────────────────────────────────────────
    count_label = len(episodes)
    st.markdown(f'<div class="pcl-count-label">{count_label} bài học</div>', unsafe_allow_html=True)
    logger.debug(f"🔢 podcast_list_view: Hiển thị {count_label} episodes.")

    # ─────────────────────────────────────────────
    # 5. EPISODE LIST
    # ─────────────────────────────────────────────
    if not episodes:
        logger.info("ℹ️ podcast_list_view: Không có episode nào để hiển thị.")
        st.markdown("""
        <div class="pcl-empty-state">
            <div class="pcl-empty-icon">🎧</div>
            <div class="pcl-empty-title">Chưa có bài học</div>
            <div class="pcl-empty-sub">Chưa có bài học nào trong show này.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        logger.debug(f"📋 podcast_list_view: Rendering {len(episodes)} episode rows.")
        for idx, ep in enumerate(episodes):
            _render_episode_row(ep, idx, show_cover)
            logger.debug(f"✅ podcast_list_view: Episode [{idx}] rendered — '{ep.get('title', '')[:50]}'")

    logger.info("✅ podcast_list_view: render_podcast_list_page() — DONE.")

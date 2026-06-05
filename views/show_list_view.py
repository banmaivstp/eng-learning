import streamlit as st
import logging

logger = logging.getLogger("views.show_list_view")

# =====================================================
# DỮ LIỆU MẪU — fallback khi DB chưa có show nào
# Production: dữ liệu thực từ Supabase table "shows"
# =====================================================
SAMPLE_SHOWS = [
    {"id": "sample-1", "title": "English Listening Daily",  "cover_image": None, "icon": "🎙️", "episode_count": 12},
    {"id": "sample-2", "title": "Daily Conversations",      "cover_image": None, "icon": "🧠", "episode_count": 12},
    {"id": "sample-3", "title": "Business English Podcast", "cover_image": None, "icon": "☕", "episode_count": 18},
    {"id": "sample-4", "title": "Real Life English",        "cover_image": None, "icon": "🌆", "episode_count": 12},
    {"id": "sample-5", "title": "Speak Better Every Day",   "cover_image": None, "icon": "🎧", "episode_count": 12},
    {"id": "sample-6", "title": "Travel & Culture Stories", "cover_image": None, "icon": "🏔️", "episode_count": 12},
]


def _fetch_shows_from_db(supabase_client) -> list:
    """
    Truy vấn danh sách shows từ Supabase table 'shows'.
    Trả về list dicts: id, title, cover_image, apple_show_url, episode_count, icon.
    Fallback: SAMPLE_SHOWS nếu lỗi hoặc DB rỗng.
    """
    if not supabase_client:
        logger.warning("⚠️ show_list_view: supabase_client = None — sử dụng sample data.")
        return SAMPLE_SHOWS

    try:
        logger.debug("🔍 show_list_view: Querying Supabase table 'shows'...")
        res = supabase_client.table("shows").select(
            "id, title, cover_image, apple_show_url, created_at"
        ).order("created_at", desc=True).execute()

        if res.data:
            logger.info(f"✅ show_list_view: Fetched {len(res.data)} shows from DB.")
            shows_with_count = []
            for show in res.data:
                try:
                    ep_res = supabase_client.table("episodes").select(
                        "id", count="exact"
                    ).eq("show_id", show["id"]).execute()
                    episode_count = ep_res.count if ep_res.count is not None else 0
                    logger.debug(f"📊 show_list_view: '{show['title']}' — {episode_count} episodes.")
                except Exception as ep_err:
                    logger.warning(f"⚠️ show_list_view: Không đếm được episodes cho show {show.get('id')}: {ep_err}")
                    episode_count = 0
                shows_with_count.append({
                    **show,
                    "episode_count": episode_count,
                    "icon": "🎙️"
                })
            return shows_with_count
        else:
            logger.info("ℹ️ show_list_view: Bảng 'shows' rỗng — dùng sample data.")
            return SAMPLE_SHOWS

    except Exception as e:
        logger.error(f"🚨 show_list_view: Lỗi query Supabase 'shows': {e}")
        return SAMPLE_SHOWS


def _render_show_card(show: dict, card_idx: int):
    """
    Render một show card theo mockup.
    Dùng CSS class sl-show-card (prefix sl- không conflict với code cũ).
    Kỹ thuật: HTML card + Streamlit button trong suốt overlay để bắt click.
    """
    cover = show.get("cover_image")
    icon = show.get("icon", "🎙️")
    title = show.get("title", "Untitled Show")
    ep_count = show.get("episode_count", 0)
    ep_label = f"{ep_count} Episode{'s' if ep_count != 1 else ''}"

    if cover:
        thumb_html = f'<img src="{cover}" class="sl-show-thumb" alt="{title}"/>'
    else:
        thumb_html = f'<div class="sl-show-thumb-placeholder">{icon}</div>'

    # Render card HTML
    st.markdown(f"""
    <div class="sl-show-card">
        {thumb_html}
        <div class="sl-show-info">
            <div class="sl-show-title">{title}</div>
            <div class="sl-show-episodes">{ep_label}</div>
        </div>
        <div class="sl-show-more-btn" title="More options">⋯</div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit button ẩn để bắt click (overlay kỹ thuật)
    btn_key = f"sl_card_{show.get('id', 'x')}_{card_idx}"
    if st.button(f"▶ {title}", key=btn_key, use_container_width=True):
        logger.info(f"🎯 show_list_view: User chọn show: '{title}' (id={show.get('id')})")
        st.session_state["selected_show"] = show
        st.session_state["current_page"] = "Show Detail"
        st.rerun()


def _render_add_show_section(supabase_client):
    """
    Phần thêm show mới qua Apple Podcast URL.
    Logic scraper/DB giữ nguyên từ bản cũ — chỉ thay đổi UI.
    """
    logger.debug("🔧 show_list_view: Rendering Add Show expander.")
    with st.expander("➕  Add New Show  —  Paste Apple Podcast URL", expanded=False):
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            input_url = st.text_input(
                label="Apple Podcast URL",
                placeholder="https://podcasts.apple.com/...",
                label_visibility="collapsed",
                key="sl_add_show_url_input"
            )
        with col_btn:
            scan_clicked = st.button("🔍 Scan", use_container_width=True, key="sl_scan_show_btn")

        if scan_clicked:
            if not input_url or not input_url.strip():
                logger.warning("⚠️ show_list_view: Scan clicked nhưng URL rỗng.")
                st.warning("Vui lòng dán link Apple Podcast trước khi quét.")
            else:
                logger.info(f"🔍 show_list_view: Bắt đầu scrape: {input_url}")
                with st.spinner("AI đang quét dữ liệu bài học..."):
                    try:
                        from modules.scraper import get_episode_list_from_show
                        show_data = get_episode_list_from_show(input_url)
                        if show_data:
                            ep_count = len(show_data.get("episodes", []))
                            logger.info(f"✅ show_list_view: Scrape OK — {ep_count} episodes.")
                            st.success(f"✅ Đồng bộ thành công! Tìm thấy {ep_count} episodes.")
                            st.rerun()
                        else:
                            logger.warning("⚠️ show_list_view: Scraper trả về rỗng/None.")
                            st.error("Không tìm thấy dữ liệu — kiểm tra lại URL.")
                    except Exception as scrape_err:
                        logger.error(f"🚨 show_list_view: Scraper lỗi: {scrape_err}")
                        st.error(f"Lỗi khi quét: {scrape_err}")


def render_podcast_discover_page(supabase_client=None):
    """
    Màn hình 'Your Podcast Library' — render khi sidebar Discover được click.
    - Layout: page header + search bar + add-show expander + grid 2 cột.
    - Logic DB, scraper, điều hướng KHÔNG thay đổi so với bản gốc.
    - Tham số supabase_client khớp với cách gọi từ app.py:
        render_podcast_discover_page(supabase_client=supabase)

    Logs:
        [INFO]  Khi function được gọi và hoàn thành
        [DEBUG] Từng bước render: header, fetch, grid, từng card
        [WARNING] Khi dùng sample data hoặc URL rỗng
        [ERROR]  Khi lỗi Supabase / Scraper
    """
    logger.info("📻 show_list_view: render_podcast_discover_page() — START.")

    # ─────────────────────────────────────────────
    # 1. PAGE HEADER
    # ─────────────────────────────────────────────
    st.markdown("""
    <div class="sl-page-header">
        <div class="sl-page-title">Your Podcast Library</div>
        <div class="sl-page-sub">All the shows you've saved in one place.</div>
    </div>
    """, unsafe_allow_html=True)
    logger.debug("📝 show_list_view: Rendered page header.")

    # ─────────────────────────────────────────────
    # 2. SEARCH BAR
    # ─────────────────────────────────────────────
    search_query = st.text_input(
        label="Search shows",
        placeholder="🔍  Search shows...",
        label_visibility="collapsed",
        key="sl_search_input"
    )
    logger.debug(f"🔍 show_list_view: search_query='{search_query}'")

    # ─────────────────────────────────────────────
    # 3. ADD SHOW SECTION
    # ─────────────────────────────────────────────
    _render_add_show_section(supabase_client)

    # ─────────────────────────────────────────────
    # 4. FETCH DATA
    # ─────────────────────────────────────────────
    shows = _fetch_shows_from_db(supabase_client)
    logger.debug(f"📦 show_list_view: Total shows loaded: {len(shows)}")

    # Filter theo search
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        shows = [s for s in shows if q in s.get("title", "").lower()]
        logger.debug(f"🔍 show_list_view: After filter '{q}': {len(shows)} shows remain.")

    # ─────────────────────────────────────────────
    # 5. RENDER GRID 2 CỘT
    # ─────────────────────────────────────────────
    if not shows:
        logger.info("ℹ️ show_list_view: Empty state — không có show để hiển thị.")
        st.markdown("""
        <div class="sl-empty-state">
            <div class="sl-empty-icon">🎧</div>
            <div class="sl-empty-title">No shows yet</div>
            <div class="sl-empty-sub">Paste an Apple Podcast URL above<br/>to add your first show.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        logger.debug(f"🗂️ show_list_view: Rendering {len(shows)} shows in 2-col grid.")
        # Render từng hàng: 2 card/hàng
        for row_idx in range(0, len(shows), 2):
            col_left, col_right = st.columns(2, gap="medium")

            with col_left:
                _render_show_card(shows[row_idx], row_idx)
                logger.debug(f"✅ show_list_view: Card [{row_idx}] rendered — '{shows[row_idx]['title']}'")

            if row_idx + 1 < len(shows):
                with col_right:
                    _render_show_card(shows[row_idx + 1], row_idx + 1)
                    logger.debug(f"✅ show_list_view: Card [{row_idx+1}] rendered — '{shows[row_idx+1]['title']}'")

    logger.info("✅ show_list_view: render_podcast_discover_page() — DONE.")

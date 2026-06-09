# ==========================================
# FILE: views/show_list_view.py
# TẦNG VIEW — Màn hình Your Podcast Library
# ==========================================
import streamlit as st
import logging

from views.show_list_css import inject_show_list_card_button_css
# FIX: Import hàm Model tập trung thay vì tự query trong View
from modules.database import get_episode_count_by_show_id

logger = logging.getLogger("views.show_list_view")


def _fetch_shows_from_db(supabase_client) -> list:
    """
    Truy vấn danh sách shows từ Supabase table 'shows'.
    Trả về [] nếu DB rỗng, lỗi, hoặc không có client — không dùng sample data.
    """
    if not supabase_client:
        logger.warning("⚠️ show_list_view: supabase_client = None.")
        return []

    try:
        logger.debug("🔍 show_list_view: Querying Supabase table 'shows'...")
        res = supabase_client.table("shows").select(
            "id, title, cover_image, apple_show_url, created_at"
        ).order("created_at", desc=True).execute()

        if res.data:
            logger.info(f"✅ show_list_view: Fetched {len(res.data)} shows from DB.")
            shows_with_count = []
            for show in res.data:
                episode_count = get_episode_count_by_show_id(supabase_client, show["id"])
                logger.debug(f"📊 show_list_view: '{show['title']}' — {episode_count} episodes.")
                shows_with_count.append({
                    **show,
                    "episode_count": episode_count,
                    "icon": "🎙️"
                })
            return shows_with_count
        else:
            logger.info("ℹ️ show_list_view: Bảng 'shows' rỗng.")
            return []

    except Exception as e:
        logger.error(f"🚨 show_list_view: Lỗi query Supabase 'shows': {e}")
        return []


def _render_show_card_v4(show: dict, card_idx: int):
    """
    Render show card v4 — col_info (HTML visual) + col_btn (pill button).

    FIX LỖI EPISODE LIST:
    - selected_show phải chứa ĐỦ các field mà podcast_list_view cần:
      id, title, cover_image, apple_show_url, episode_count
    - Trước đây: show dict từ DB có thể thiếu field nếu query SELECT không đủ cột
    - Nay: đảm bảo build selected_show dict đầy đủ trước khi set vào session_state
    UI giữ nguyên 100%.
    """
    cover = show.get("cover_image")
    icon = show.get("icon", "🎙️")
    title = show.get("title", "Untitled Show")
    ep_count = show.get("episode_count", 0)
    ep_label = f"{ep_count} Episode{'s' if ep_count != 1 else ''}"
    show_id = show.get("id", f"show_{card_idx}")

    logger.debug(
        f"🃏 show_list_view: _render_show_card_v4[{card_idx}] — '{title}', "
        f"cover={'yes' if cover else 'no'}, episodes={ep_count}"
    )

    if cover:
        thumb_html = f'<img src="{cover}" class="sl-show-thumb" alt="{title}"/>'
    else:
        thumb_html = f'<div class="sl-show-thumb-placeholder">{icon}</div>'

    col_info, col_btn = st.columns([3.2, 1.0], gap="small")

    with col_info:
        st.markdown(f"""
        <div class="sl-show-card">
            {thumb_html}
            <div class="sl-show-info">
                <div class="sl-show-title">{title}</div>
                <div class="sl-show-episodes">{ep_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown('<div class="sl-open-btn-wrap">', unsafe_allow_html=True)
        if st.button("▶ Open", key=f"slv4_{show_id}_{card_idx}", use_container_width=False):
            logger.info(f"🎯 show_list_view: User clicked Open card[{card_idx}] — '{title}' (id={show_id})")

            # FIX: Build selected_show dict đầy đủ, đảm bảo podcast_list_view
            # nhận được show_id hợp lệ để query episodes.
            # Trước đây: set trực tiếp `show` dict có thể thiếu field hoặc
            # có field thừa không nhất quán giữa DB row và sample data.
            selected_show = {
                "id":             show_id,
                "title":          title,
                "cover_image":    cover,
                "apple_show_url": show.get("apple_show_url", ""),
                "episode_count":  ep_count,
                "icon":           icon,
            }
            st.session_state["selected_show"] = selected_show
            st.session_state["current_page"] = "Show Detail"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def _render_add_show_section(supabase_client):
    """
    Phần thêm show mới qua Apple Podcast URL.

    Luồng 3 bước:
      Bước 1 — Scraper : gọi get_episode_list_from_show() thu thập RSS data
      Bước 2 — DB Sync : lưu show + episodes vào Supabase
      Bước 3 — Rerun   : st.rerun() reload page, grid render lại từ DB sạch

    MAPPING FIELD (scraper → DB schema episodes):
      scraper["apple_url"]  → episodes.audio_url
      scraper["title"]      → episodes.title
      scraper["image"]      → không có cột tương ứng → bỏ qua
      Duplicate check       → dùng (show_id, title)
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
                return

            logger.info(f"🔍 show_list_view: Bắt đầu scrape: {input_url}")
            with st.spinner("AI đang quét dữ liệu bài học..."):

                # ── BƯỚC 1: Scraper ──
                try:
                    from modules.scraper import get_episode_list_from_show
                    show_data = get_episode_list_from_show(input_url.strip())
                except Exception as scrape_err:
                    logger.error(f"🚨 show_list_view: Scraper exception: {scrape_err}")
                    st.error(f"Lỗi khi quét: {scrape_err}")
                    return

                if not show_data:
                    logger.warning("⚠️ show_list_view: Scraper trả về rỗng/None.")
                    st.error("Không tìm thấy dữ liệu — kiểm tra lại URL.")
                    return

                episodes_raw = show_data.get("episodes", [])
                ep_total = len(episodes_raw)
                logger.info(
                    f"✅ show_list_view: Scrape OK — "
                    f"'{show_data.get('show_title')}', {ep_total} episodes."
                )

                # ── BƯỚC 2: DB Sync ──
                if not supabase_client:
                    logger.warning("show_list_view: supabase_client=None, bỏ qua DB sync.")
                    st.info(
                        f"Đã quét được \"{show_data['show_title']}\" ({ep_total} tập) "
                        "nhưng không thể lưu do chưa kết nối DB."
                    )
                    st.rerun()
                    return

                try:
                    import uuid

                    # 2a. Upsert Show — check trùng theo apple_show_url
                    existing_show = supabase_client.table("shows").select("id").eq(
                        "apple_show_url", input_url.strip()
                    ).execute()

                    if existing_show.data:
                        show_id = existing_show.data[0]["id"]
                        logger.info(f"show_list_view: Show đã tồn tại, reuse id={show_id}")
                    else:
                        show_id = str(uuid.uuid4())
                        supabase_client.table("shows").insert({
                            "id": show_id,
                            "title": show_data["show_title"],
                            "cover_image": show_data.get("show_image"),
                            "apple_show_url": input_url.strip()
                        }).execute()
                        logger.info(
                            f"show_list_view: Inserted new show "
                            f"id={show_id}, title='{show_data['show_title']}'"
                        )

                    # 2b. Insert Episodes — chỉ insert tập chưa tồn tại
                    existing_ep_res = supabase_client.table("episodes").select(
                        "title"
                    ).eq("show_id", show_id).execute()
                    existing_titles = {
                        row["title"] for row in (existing_ep_res.data or [])
                    }
                    logger.debug(
                        f"show_list_view: {len(existing_titles)} episodes đã có trong DB cho show này."
                    )

                    inserted = 0
                    skipped = 0
                    for ep in episodes_raw:
                        ep_title = ep.get("title", "").strip()
                        if ep_title in existing_titles:
                            skipped += 1
                            continue
                        supabase_client.table("episodes").insert({
                            "id": str(uuid.uuid4()),
                            "show_id": show_id,
                            "title": ep_title,
                            "audio_url": ep.get("apple_url", ""),
                        }).execute()
                        inserted += 1

                    logger.info(
                        f"show_list_view: Sync done — "
                        f"{inserted} inserted, {skipped} skipped / {ep_total} total."
                    )
                    st.success(
                        f"✅ Đã thêm \"{show_data['show_title']}\" "
                        f"({inserted} tập mới) vào thư viện!"
                    )

                except Exception as db_err:
                    logger.error(f"🚨 show_list_view: DB sync error: {db_err}")
                    st.warning(f"Lấy dữ liệu thành công nhưng lưu DB gặp sự cố: {db_err}")

                # ── BƯỚC 3: Reload page ──
                st.rerun()


def render_podcast_discover_page(supabase_client=None):
    """
    Màn hình 'Your Podcast Library' — render khi sidebar Discover được click.
    """
    logger.info("📻 show_list_view: render_podcast_discover_page() — START.")

    # 0. Inject CSS
    inject_show_list_card_button_css()

    # 1. Page header
    st.markdown("""
    <div class="sl-page-header">
        <div class="sl-page-title">Your Podcast Library</div>
        <div class="sl-page-sub">All the shows you've saved in one place.</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Search bar
    search_query = st.text_input(
        label="Search shows",
        placeholder="🔍  Search shows...",
        label_visibility="collapsed",
        key="sl_search_input"
    )

    # 3. Add show section
    _render_add_show_section(supabase_client)

    # 4. Fetch data từ DB — lưu vào all_shows để phân biệt "DB rỗng" vs "filter rỗng"
    all_shows = _fetch_shows_from_db(supabase_client)
    logger.debug(f"📦 show_list_view: Total shows loaded: {len(all_shows)}")

    # 5. Filter theo search
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        shows = [s for s in all_shows if q in s.get("title", "").lower()]
    else:
        shows = all_shows

    # 6. Render grid 2 cột
    # Phân biệt 2 trạng thái rỗng:
    # - all_shows rỗng  → DB chưa có show nào → hiển thị hướng dẫn thêm show
    # - shows rỗng sau filter → search không khớp → hiển thị "no results"
    db_is_empty = len(all_shows) == 0
    search_active = bool(search_query and search_query.strip())

    if db_is_empty:
        st.markdown("""
        <div class="sl-empty-state">
            <div class="sl-empty-icon">🎧</div>
            <div class="sl-empty-title">No show.</div>
            <div class="sl-empty-sub">Please click on <span style="color:#00F2FE;font-weight:700;">Add New Show</span> for updating.</div>
        </div>
        """, unsafe_allow_html=True)
    elif search_active and not shows:
        st.markdown("""
        <div class="sl-empty-state">
            <div class="sl-empty-icon">🔍</div>
            <div class="sl-empty-title">No results found.</div>
            <div class="sl-empty-sub">Try a different keyword.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        logger.debug(f"🗂️ show_list_view: Rendering {len(shows)} shows in 2-col grid.")
        for row_idx in range(0, len(shows), 2):
            col_left, col_right = st.columns(2, gap="medium")
            with col_left:
                _render_show_card_v4(shows[row_idx], row_idx)
            if row_idx + 1 < len(shows):
                with col_right:
                    _render_show_card_v4(shows[row_idx + 1], row_idx + 1)

    logger.info("✅ show_list_view: render_podcast_discover_page() — DONE.")

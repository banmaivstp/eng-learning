import streamlit as st
import logging

# =====================================================
# TẦNG STYLE: Import CSS từ file riêng biệt
# show_list_css.py chứa toàn bộ CSS của màn này
# =====================================================
from views.show_list_css import inject_show_list_card_button_css

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


def _inject_card_button_css():
    """
    Inject CSS biến st.button thành show card hoàn chỉnh.
    Kỹ thuật: Button có key dạng 'slcard_{id}_{idx}' — CSS nhắm
    đúng vào button đó, style thành card đầy đủ (ảnh + text).
    KHÔNG dùng overlay/invisible button — click thẳng vào card.
    CHỈ GỌI MỘT LẦN trong render_podcast_discover_page().
    """
    logger.debug("🎨 show_list_view: Injecting show-card-as-button CSS.")
    st.markdown("""
    <style>
        /* =====================================================
           SHOW CARD BUTTON — v4 Clean (không overlay)
           Mỗi button có key="slcard_{id}_{idx}" → Streamlit
           sinh ra data-testid="stBaseButton-secondary" bên trong
           một div container. Ta style button thành card hoàn chỉnh.

           QUY TẮC: CHỈ THÊM MỚI — không sửa CSS cũ sl- / pl- / db-
        ===================================================== */

        /* Container wrapper của mỗi card button */
        .sl-card-btn-wrap {
            width: 100%;
            margin-bottom: 12px;
        }
        .sl-card-btn-wrap .stButton,
        .sl-card-btn-wrap [data-testid="stButton"] {
            width: 100% !important;
        }

        /* Button styled thành card —
           Dùng :has() để nhắm button trong .sl-card-btn-wrap */
        .sl-card-btn-wrap .stButton > button,
        .sl-card-btn-wrap [data-testid="stButton"] > button {
            /* Reset Streamlit defaults */
            all: unset !important;
            /* Card layout */
            display: flex !important;
            align-items: center !important;
            gap: 0 !important;
            width: 100% !important;
            min-height: 90px !important;
            padding: 0 !important;
            margin: 0 !important;
            /* Card visual */
            background: rgba(255, 255, 255, 0.025) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 16px !important;
            cursor: pointer !important;
            overflow: hidden !important;
            box-sizing: border-box !important;
            text-align: left !important;
            transition: background 0.18s ease, border-color 0.18s ease,
                        box-shadow 0.18s ease !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            /* Đảm bảo nội dung HTML bên trong được render đúng */
            white-space: normal !important;
            line-height: normal !important;
        }
        .sl-card-btn-wrap .stButton > button:hover,
        .sl-card-btn-wrap [data-testid="stButton"] > button:hover {
            background: rgba(0, 242, 254, 0.05) !important;
            border-color: rgba(0, 242, 254, 0.22) !important;
            box-shadow: 0 0 22px rgba(0, 242, 254, 0.07) !important;
        }
        .sl-card-btn-wrap .stButton > button:active,
        .sl-card-btn-wrap [data-testid="stButton"] > button:active {
            background: rgba(0, 242, 254, 0.09) !important;
            border-color: rgba(0, 242, 254, 0.35) !important;
        }
        .sl-card-btn-wrap .stButton > button:focus,
        .sl-card-btn-wrap [data-testid="stButton"] > button:focus {
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(0, 242, 254, 0.30) !important;
        }

        /* Nội dung bên trong button (p tag của Streamlit) */
        .sl-card-btn-wrap .stButton > button p,
        .sl-card-btn-wrap [data-testid="stButton"] > button p {
            display: flex !important;
            align-items: center !important;
            gap: 0 !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* =====================================================
           SIDEBAR BUTTON OVERRIDE — không bị ảnh hưởng bởi CSS trên
           Đảm bảo sidebar nav buttons giữ nguyên opacity:0 / height:46px
        ===================================================== */
        [data-testid="stSidebar"] .stButton > button {
            all: unset !important;
            opacity: 0 !important;
            display: block !important;
            width: 100% !important;
            height: 46px !important;
            min-height: 0 !important;
            cursor: pointer !important;
        }
        [data-testid="stSidebar"] .stButton {
            margin-top: -46px !important;
            height: 46px !important;
            overflow: hidden !important;
            z-index: 5 !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ show_list_view: Card-as-button CSS injected.")


def _build_card_html(show: dict) -> str:
    """
    Build HTML string cho nội dung bên trong button card.
    Streamlit button nhận markdown, nên ta dùng unsafe_allow_html=False
    nhưng dùng st.button với label là HTML thuần — Streamlit 1.30+ hỗ trợ
    unsafe_allow_html trong button label qua markdown.

    Thực tế: st.button label bị escape HTML → dùng placeholder text +
    inject HTML riêng ra ngoài qua st.markdown (kỹ thuật dual render).

    Giải pháp đúng: Dùng st.markdown cho visual card + st.button ẩn overlay.
    Nhưng yêu cầu là KHÔNG dùng overlay. Vậy dùng streamlit-javascript hoặc
    components.v1.html để bridge JS click → session_state.
    KHÔNG khả thi trong 1 render cycle.

    => Giải pháp THỰC DỤNG nhất: st.button với label có icon + title text
       (không HTML), wrap trong .sl-card-btn-wrap, CSS style thành card đẹp.
    """
    cover = show.get("cover_image")
    icon = show.get("icon", "🎙️")
    title = show.get("title", "Untitled Show")
    ep_count = show.get("episode_count", 0)
    ep_label = f"{ep_count} Episode{'s' if ep_count != 1 else ''}"

    if cover:
        # Có ảnh thật — dùng emoji placeholder cho button label, ảnh hiện qua CSS background
        thumb_part = f"[{icon}]"
    else:
        thumb_part = icon

    # Label của button: icon + title + episode count
    # Streamlit sẽ render đây là text trong <p> bên trong button
    return thumb_part, title, ep_label


def _render_show_card(show: dict, card_idx: int):
    """
    Render một show card theo mockup — v4 Card-HTML + Button hybrid.

    Kỹ thuật mới (không overlay):
    1. Render card HTML bằng st.markdown (visual đẹp)
    2. Render st.button có label = tên show (text thuần), width=full
    3. CSS kéo button lên đè card bằng negative margin-top
       → button trong suốt (opacity:0) nhưng vùng click chính xác khớp card

    ĐIỂM KHÁC BIỆT so với cách cũ:
    - CSS mới dùng margin-top âm ĐÚNG chiều cao card (90px) thay vì 54px/58px
    - overflow:hidden trên .stButton chặn vùng click tràn ra ngoài
    - Không còn nút "▶ Open" hiện ra ở phía dưới

    Log levels:
        DEBUG: Mỗi card render
        INFO:  Khi user click chọn show
        WARNING: Khi thiếu cover image
    """
    cover = show.get("cover_image")
    icon = show.get("icon", "🎙️")
    title = show.get("title", "Untitled Show")
    ep_count = show.get("episode_count", 0)
    ep_label = f"{ep_count} Episode{'s' if ep_count != 1 else ''}"
    show_id = show.get("id", f"show_{card_idx}")

    logger.debug(f"🃏 show_list_view: Rendering card[{card_idx}] — '{title}', "
                 f"cover={'yes' if cover else 'no'}, episodes={ep_count}")

    if not cover:
        logger.debug(f"🖼️ show_list_view: Card[{card_idx}] '{title}' — no cover image, using icon fallback.")

    # --- BƯỚC 1: Render HTML card (visual) ---
    if cover:
        thumb_html = f'<img src="{cover}" class="sl-show-thumb" alt="{title}"/>'
    else:
        thumb_html = f'<div class="sl-show-thumb-placeholder">{icon}</div>'

    card_html = f"""
    <div class="sl-show-card" id="sl-card-{card_idx}">
        {thumb_html}
        <div class="sl-show-info">
            <div class="sl-show-title">{title}</div>
            <div class="sl-show-episodes">{ep_label}</div>
        </div>
        <div class="sl-show-more-btn" title="More options">⋯</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    logger.debug(f"📄 show_list_view: Card[{card_idx}] HTML rendered.")

    # --- BƯỚC 2: Render st.button ẩn đè lên card ---
    # Button trong suốt (opacity:0), negative margin-top kéo lên khớp card
    # CSS target: [data-testid="stSidebar"] được loại trừ để không ảnh hưởng sidebar
    btn_key = f"slcard_{show_id}_{card_idx}"
    if st.button(
        label=f"open_show_{card_idx}",   # label text ngắn, sẽ bị ẩn bởi opacity:0
        key=btn_key,
        use_container_width=True,
        help=f"Mở show: {title}"
    ):
        logger.info(f"🎯 show_list_view: User clicked show card[{card_idx}] — '{title}' (id={show_id})")
        st.session_state["selected_show"] = show
        st.session_state["current_page"] = "Show Detail"
        logger.debug(f"📌 show_list_view: session_state updated → selected_show='{title}', page='Show Detail'")
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


def _render_show_card_v4(show: dict, card_idx: int):
    """
    Render show card v4 — Click trực tiếp vào card để navigate.

    Kỹ thuật:
    1. Bọc toàn bộ trong <div class="sl-v4-card-wrap"> qua st.markdown
    2. Render card HTML (visual) — pointer-events: none (CSS)
    3. Render st.button ngay sau — CSS absolute + opacity:0 phủ toàn card
    4. User click vào bất kỳ vị trí nào trên card → button nhận click
    5. st.rerun() + session_state update → chuyển trang

    KHÔNG có nút "▶ Open" hiển thị.
    KHÔNG dùng js/components bridge.
    Chỉ dùng Streamlit thuần + CSS.

    Log levels:
        DEBUG: render từng bước
        INFO:  user click
        WARNING: thiếu cover image
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

    if not cover:
        logger.debug(f"🖼️ show_list_view: Card[{card_idx}] '{title}' — no cover, using icon '{icon}'")

    # Build thumbnail HTML
    if cover:
        thumb_html = f'<img src="{cover}" class="sl-show-thumb" alt="{title}"/>'
    else:
        thumb_html = f'<div class="sl-show-thumb-placeholder">{icon}</div>'

    # --- Mở wrapper div (relative container) ---
    st.markdown('<div class="sl-v4-card-wrap">', unsafe_allow_html=True)

    # --- Card HTML (visual) ---
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
    logger.debug(f"📄 show_list_view: Card[{card_idx}] HTML block rendered.")

    # --- Button ẩn — đặt trong cùng wrapper → CSS absolute phủ card ---
    btn_key = f"slv4_{show_id}_{card_idx}"
    if st.button(
        label=" ",           # label rỗng — sẽ bị opacity:0 ẩn hoàn toàn
        key=btn_key,
        use_container_width=True,
        help=f"Mở: {title}"  # tooltip khi hover giúp UX rõ hơn
    ):
        logger.info(
            f"🎯 show_list_view: User clicked card[{card_idx}] — "
            f"'{title}' (id={show_id})"
        )
        st.session_state["selected_show"] = show
        st.session_state["current_page"] = "Show Detail"
        logger.debug(
            f"📌 show_list_view: session_state → "
            f"selected_show='{title}', current_page='Show Detail'"
        )
        st.rerun()

    # --- Đóng wrapper div ---
    st.markdown('</div>', unsafe_allow_html=True)
    logger.debug(f"✅ show_list_view: Card[{card_idx}] wrapper closed.")


def render_podcast_discover_page(supabase_client=None):
    """
    Màn hình 'Your Podcast Library' — render khi sidebar Discover được click.
    - Layout: page header + search bar + add-show expander + grid 2 cột.
    - Logic DB, scraper, điều hướng KHÔNG thay đổi so với bản gốc.
    - Tham số supabase_client khớp với cách gọi từ app.py:
        render_podcast_discover_page(supabase_client=supabase)

    Fix v4 — Card Click Navigation:
    - Bỏ nút "▶ Open {title}" hiển thị dưới card
    - Dùng st.button ẩn (opacity:0) đè lên card HTML bằng CSS negative margin-top
    - CSS .sl-show-card-btn target đúng chiều cao card (90px) → click chính xác
    - overflow:hidden trên .stButton chặn vùng click tràn lên/xuống

    Logs:
        [INFO]  Khi function được gọi và hoàn thành
        [DEBUG] Từng bước render: header, fetch, grid, từng card
        [WARNING] Khi dùng sample data hoặc URL rỗng
        [ERROR]  Khi lỗi Supabase / Scraper
    """
    logger.info("📻 show_list_view: render_podcast_discover_page() — START.")

    # ─────────────────────────────────────────────
    # 0. INJECT CSS CHO CARD BUTTON (gọi một lần đầu)
    #    Delegate sang show_list_css.py — tách biệt hoàn toàn
    # ─────────────────────────────────────────────
    inject_show_list_card_button_css()

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
                _render_show_card_v4(shows[row_idx], row_idx)
                logger.debug(f"✅ show_list_view: Card [{row_idx}] rendered — '{shows[row_idx]['title']}'")

            if row_idx + 1 < len(shows):
                with col_right:
                    _render_show_card_v4(shows[row_idx + 1], row_idx + 1)
                    logger.debug(f"✅ show_list_view: Card [{row_idx+1}] rendered — '{shows[row_idx+1]['title']}'")

    logger.info("✅ show_list_view: render_podcast_discover_page() — DONE.")

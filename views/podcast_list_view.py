# ==========================================
# FILE: views/podcast_list_view.py
# TẦNG VIEW — Màn hình Episode List của một Show
# ==========================================
import streamlit as st
import logging

# TẦNG MODEL — dùng hàm tập trung, không tự query DB trong View
from modules.database import get_episodes_by_show_id

logger = logging.getLogger("views.podcast_list_view")


# =====================================================
# TẦNG STYLE — CSS riêng cho màn này (prefix: pcl-)
# =====================================================

def _inject_podcast_list_css():
    """
    Inject CSS riêng cho Episode List view.
    Prefix 'pcl-' để không conflict với sl-, db-, sb-.
    """
    st.markdown("""
    <style>
        /* ── BACK BUTTON ── */
        .pcl-back-wrap button {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            color: #94A3B8 !important;
            border-radius: 10px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 6px 14px !important;
            min-height: unset !important;
            height: 34px !important;
            transition: border-color 0.15s ease, color 0.15s ease !important;
        }
        .pcl-back-wrap button:hover {
            border-color: rgba(0,242,254,0.40) !important;
            color: #00F2FE !important;
        }

        /* ── PAGE HEADER ── */
        .pcl-header {
            display: flex;
            align-items: center;
            gap: 18px;
            margin: 14px 0 22px 0;
        }
        .pcl-cover {
            width: 80px;
            height: 80px;
            border-radius: 14px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .pcl-cover-placeholder {
            width: 80px;
            height: 80px;
            border-radius: 14px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,242,254,0.12) 0%, rgba(79,172,254,0.07) 100%);
            border: 1px solid rgba(0,242,254,0.14);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 34px;
        }
        .pcl-show-meta { flex: 1; overflow: hidden; }
        .pcl-show-title {
            font-size: 20px;
            font-weight: 800;
            color: #F1F5F9 !important;
            line-height: 1.25;
            margin-bottom: 5px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .pcl-ep-count {
            font-size: 13px;
            font-weight: 600;
            color: #00F2FE !important;
        }

        /* ── EPISODE ITEM ── */
        .pcl-ep-item {
            display: flex;
            align-items: center;
            gap: 14px;
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.055);
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            transition: background 0.16s ease, border-color 0.16s ease;
        }
        .pcl-ep-item:hover {
            background: rgba(0,242,254,0.04) !important;
            border-color: rgba(0,242,254,0.18) !important;
        }
        .pcl-ep-num {
            min-width: 30px;
            height: 30px;
            border-radius: 8px;
            background: rgba(0,242,254,0.08);
            border: 1px solid rgba(0,242,254,0.14);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            color: #00F2FE !important;
            flex-shrink: 0;
        }
        .pcl-ep-title {
            flex: 1;
            font-size: 14px;
            font-weight: 600;
            color: #E2E8F0 !important;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* Nút Start bên phải mỗi episode */
        .pcl-start-wrap {
            display: flex;
            align-items: center;
        }
        .pcl-start-wrap button {
            background: rgba(0,242,254,0.10) !important;
            color: #00F2FE !important;
            border: 1px solid rgba(0,242,254,0.28) !important;
            border-radius: 18px !important;
            font-size: 11.5px !important;
            font-weight: 700 !important;
            padding: 5px 12px !important;
            min-height: unset !important;
            height: 30px !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            width: auto !important;
            transition: background 0.14s ease, border-color 0.14s ease !important;
        }
        .pcl-start-wrap button:hover {
            background: rgba(0,242,254,0.20) !important;
            border-color: rgba(0,242,254,0.55) !important;
            color: #ffffff !important;
        }

        /* ── EMPTY STATE ── */
        .pcl-empty {
            text-align: center;
            padding: 56px 20px;
            color: #475569 !important;
        }
        .pcl-empty-icon { font-size: 48px; margin-bottom: 14px; }
        .pcl-empty-title {
            font-size: 17px;
            font-weight: 700;
            color: #94A3B8 !important;
            margin-bottom: 6px;
        }
        .pcl-empty-sub {
            font-size: 13px;
            color: #475569 !important;
            line-height: 1.5;
        }

        /* ── DIVIDER ── */
        .pcl-divider {
            height: 1px;
            background: rgba(255,255,255,0.06);
            margin: 16px 0 20px 0;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ podcast_list_view: CSS injected.")


# =====================================================
# RENDER HELPERS
# =====================================================

def _render_header(show: dict):
    """Render show cover + title + episode count."""
    cover = show.get("cover_image")
    title = show.get("title", "Untitled Show")
    ep_count = show.get("episode_count", 0)
    icon = show.get("icon", "🎙️")

    if cover:
        cover_html = f'<img src="{cover}" class="pcl-cover" alt="{title}"/>'
    else:
        cover_html = f'<div class="pcl-cover-placeholder">{icon}</div>'

    st.markdown(f"""
    <div class="pcl-header">
        {cover_html}
        <div class="pcl-show-meta">
            <div class="pcl-show-title">{title}</div>
            <div class="pcl-ep-count">{ep_count} Episode{"s" if ep_count != 1 else ""}</div>
        </div>
    </div>
    <hr class="pcl-divider"/>
    """, unsafe_allow_html=True)


def _render_episode_row(ep: dict, idx: int):
    """
    Render 1 episode dưới dạng row: số thứ tự + tiêu đề + nút Start.
    Khi user click Start → set selected_episode + navigate Episode Detail.
    """
    ep_id    = ep.get("id", "")
    ep_title = ep.get("title", f"Episode {idx + 1}")

    col_info, col_btn = st.columns([4.5, 1.0], gap="small")

    with col_info:
        st.markdown(f"""
        <div class="pcl-ep-item">
            <div class="pcl-ep-num">{idx + 1}</div>
            <div class="pcl-ep-title">{ep_title}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown('<div class="pcl-start-wrap">', unsafe_allow_html=True)
        if st.button("▶ Start", key=f"pcl_ep_{ep_id}_{idx}", use_container_width=False):
            logger.info(
                f"🎯 podcast_list_view: User clicked Start ep[{idx}] "
                f"'{ep_title}' (id={ep_id})"
            )
            st.session_state["selected_episode"] = ep
            st.session_state["current_page"] = "Episode Detail"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# PUBLIC ENTRY POINT
# =====================================================

def render_podcast_list_page(supabase_client=None):
    """
    Màn hình Episode List của show đã chọn.
    Gọi từ app.py khi current_page == "Show Detail".

    FIX LỖI EPISODE LIST TRỐNG:
    - Root cause: podcast_list_view không có → app.py route "Show Detail"
      không render được danh sách episode vì thiếu View này.
    - Fix: tạo View này và dùng get_episodes_by_show_id() từ tầng Model
      để query episodes chính xác theo show_id từ session_state["selected_show"].
    - selected_show["id"] được đảm bảo đầy đủ bởi _render_show_card_v4() đã fix.
    """
    logger.info("📋 podcast_list_view: render_podcast_list_page() — START.")

    # 0. CSS
    _inject_podcast_list_css()

    # 1. Lấy show từ session state
    show = st.session_state.get("selected_show")

    if not show or not show.get("id"):
        logger.warning("⚠️ podcast_list_view: selected_show rỗng hoặc thiếu id.")
        st.warning("Không tìm thấy show. Vui lòng quay lại thư viện.")
        st.markdown('<div class="pcl-back-wrap">', unsafe_allow_html=True)
        if st.button("← Quay lại", key="pcl_back_no_show"):
            st.session_state["current_page"] = "Học tập"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    show_id = str(show["id"])
    logger.debug(f"📋 podcast_list_view: show_id={show_id}, title='{show.get('title')}'")

    # 2. Back button
    st.markdown('<div class="pcl-back-wrap">', unsafe_allow_html=True)
    if st.button("← Thư viện", key="pcl_back_btn"):
        logger.info("⬅️ podcast_list_view: Back → Học tập.")
        st.session_state["current_page"] = "Học tập"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Show header
    _render_header(show)

    # 4. Query episodes từ Model
    # FIX: Dùng get_episodes_by_show_id() — hàm tập trung ở tầng Model,
    # query đúng cột, đúng filter, trả về list sạch.
    # Trước đây: không có View này → show mới thêm không hiển thị episode.
    episodes = get_episodes_by_show_id(supabase_client, show_id)

    # Cập nhật lại episode_count trong show nếu DB trả về số thực tế
    if episodes:
        actual_count = len(episodes)
        if show.get("episode_count", 0) != actual_count:
            show["episode_count"] = actual_count
            st.session_state["selected_show"] = show

    logger.info(f"✅ podcast_list_view: {len(episodes)} episodes loaded cho show '{show.get('title')}'.")

    # 5. Render episode list
    if not episodes:
        st.markdown("""
        <div class="pcl-empty">
            <div class="pcl-empty-icon">🎧</div>
            <div class="pcl-empty-title">Chưa có episode nào</div>
            <div class="pcl-empty-sub">
                Show này chưa có tập bài học.<br/>
                Hãy thử scan lại từ Apple Podcast URL.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        logger.debug(f"🗂️ podcast_list_view: Rendering {len(episodes)} episode rows.")
        for idx, ep in enumerate(episodes):
            _render_episode_row(ep, idx)

    logger.info("✅ podcast_list_view: render_podcast_list_page() — DONE.")

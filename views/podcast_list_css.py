"""
views/podcast_list_css.py
==========================
TẦNG STYLE ĐỘC LẬP — CSS cho màn hình Podcast List (Episode List).

Quy tắc:
    - File này CHỈ chứa CSS, không chứa logic hay UI render.
    - Được import và gọi từ views/podcast_list_view.py hoặc app.py.
    - Tất cả selector dùng prefix "pcl-" để tránh xung đột với màn hình khác.
"""

import streamlit as st


def inject_podcast_list_view_css():
    """Inject toàn bộ CSS cho màn hình danh sách episodes (podcast_list_view)."""
    st.markdown("""
    <style>
    /* =============================================
       PCL — PAGE HEADER
    ============================================= */
    .pcl-page-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding: 12px 14px;
        background: linear-gradient(135deg, rgba(0,242,254,0.04) 0%, rgba(10,20,40,0.92) 100%);
        border: 1px solid rgba(0,242,254,0.12);
        border-radius: 14px;
    }
    .pcl-header-cover {
        width: 52px;
        height: 52px;
        border-radius: 10px;
        object-fit: cover;
        border: 1px solid rgba(255,255,255,0.1);
        flex-shrink: 0;
    }
    .pcl-header-cover-placeholder {
        width: 52px;
        height: 52px;
        border-radius: 10px;
        background: rgba(0,242,254,0.08);
        border: 1px solid rgba(0,242,254,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .pcl-header-text { flex: 1; overflow: hidden; }
    .pcl-page-title {
        font-size: 16px;
        font-weight: 800;
        color: #F1F5F9;
        margin-bottom: 2px;
    }
    .pcl-page-show-name {
        font-size: 12px;
        font-weight: 500;
        color: #64748B;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* =============================================
       PCL — COUNT LABEL
    ============================================= */
    .pcl-count-label {
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        margin: 10px 0 6px 2px;
        letter-spacing: 0.02em;
    }

    /* =============================================
       PCL — EPISODE ROW
    ============================================= */
    .pcl-episode-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        margin-bottom: 6px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        cursor: pointer;
        transition: border-color 0.18s, background 0.18s;
        position: relative;
    }
    .pcl-episode-row:hover {
        border-color: rgba(0,242,254,0.25);
        background: rgba(0,242,254,0.04);
    }
    .pcl-ep-thumb {
        width: 44px;
        height: 44px;
        border-radius: 8px;
        object-fit: cover;
        border: 1px solid rgba(255,255,255,0.08);
        flex-shrink: 0;
    }
    .pcl-ep-thumb-placeholder {
        width: 44px;
        height: 44px;
        border-radius: 8px;
        background: rgba(0,242,254,0.07);
        border: 1px solid rgba(0,242,254,0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .pcl-ep-info { flex: 1; overflow: hidden; }
    .pcl-ep-badge {
        font-size: 10px;
        font-weight: 700;
        color: #00F2FE;
        margin-bottom: 2px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .pcl-ep-title {
        font-size: 13px;
        font-weight: 600;
        color: #E2E8F0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.35;
    }
    .pcl-ep-duration {
        font-size: 11px;
        color: #475569;
        margin-top: 3px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .pcl-ep-duration-icon { font-size: 10px; }

    .pcl-ep-play-btn {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(0,242,254,0.08);
        border: 1px solid rgba(0,242,254,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00F2FE;
        transition: background 0.15s;
    }
    .pcl-ep-play-btn svg {
        width: 14px;
        height: 14px;
    }
    .pcl-episode-row:hover .pcl-ep-play-btn {
        background: rgba(0,242,254,0.18);
    }

    /* Ẩn Streamlit overlay button — chỉ để nhận click */
    div[data-testid="stButton"] button[kind="secondary"][data-key^="pcl_ep_"] {
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
        z-index: 2 !important;
    }

    /* =============================================
       PCL — EMPTY STATE
    ============================================= */
    .pcl-empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #475569;
    }
    .pcl-empty-icon { font-size: 36px; margin-bottom: 10px; }
    .pcl-empty-title {
        font-size: 16px;
        font-weight: 700;
        color: #64748B;
        margin-bottom: 4px;
    }
    .pcl-empty-sub { font-size: 13px; color: #334155; }
    </style>
    """, unsafe_allow_html=True)

import streamlit as st
import logging

logger = logging.getLogger("views.dashboard_css")

# =====================================================
# DASHBOARD CSS — TÁCH ĐỘC LẬP TỪ views/styles.py
# Quy tắc: CHỈ THÊM MỚI, KHÔNG SỬA inject_global_css()
#          và KHÔNG SỬA inject_sidebar_css()
# =====================================================


def inject_dashboard_css():
    """
    Inject CSS riêng biệt cho màn hình Dashboard — Gen Z Dark UI.
    CHỈ THÊM MỚI — không đụng inject_global_css() / inject_sidebar_css().
    Đồng thời fix Bug: sb-bottom-section position:sticky thay fixed
    để không chặn sidebar toggle button của Streamlit.
    """
    logger.debug("🎨 Injecting Dashboard CSS + Sidebar Bug Fix.")
    st.markdown("""
    <style>
        /* =====================================================
           BUG FIX: sb-bottom-section position:sticky
           Lý do: position:fixed + left:0 + z-index:100 che
           toggle button sidebar của Streamlit → sidebar không
           mở lại được. Fix: sticky + left:auto + z-index thấp.
        ===================================================== */
        .sb-bottom-section {
            position: sticky !important;
            bottom: 0 !important;
            left: auto !important;
            width: auto !important;
            z-index: 10 !important;
        }

        /* =====================================================
           DASHBOARD — TITLE
        ===================================================== */
        .db-title {
            font-size: 28px;
            font-weight: 800;
            color: #F1F5F9 !important;
            letter-spacing: -0.5px;
            line-height: 1.1;
            margin-bottom: 16px;
        }

        /* =====================================================
           STREAK CARD
        ===================================================== */
        .db-streak-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, #1a0a00 0%, #2d1500 40%, #1a0800 100%);
            border: 1px solid rgba(255, 120, 0, 0.35);
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 14px;
            box-shadow: 0 0 30px rgba(255, 100, 0, 0.12);
            position: relative;
            overflow: hidden;
        }
        .db-streak-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at 80% 50%, rgba(255,100,0,0.08) 0%, transparent 65%);
            pointer-events: none;
        }
        .db-streak-left {
            display: flex;
            align-items: center;
            gap: 14px;
            z-index: 1;
        }
        .db-streak-fire-icon {
            font-size: 36px;
            line-height: 1;
            filter: drop-shadow(0 0 8px rgba(255,120,0,0.6));
        }
        .db-streak-text-group {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        .db-streak-title {
            font-size: 20px;
            font-weight: 800;
            color: #F97316 !important;
            letter-spacing: -0.3px;
            line-height: 1.1;
        }
        .db-streak-sub {
            font-size: 13px;
            color: #94A3B8 !important;
        }
        .db-streak-fire-deco {
            font-size: 52px;
            line-height: 1;
            opacity: 0.55;
            filter: drop-shadow(0 0 12px rgba(255,100,0,0.4));
            z-index: 1;
        }

        /* =====================================================
           STUDY TIME CHART CARD WRAPPER
        ===================================================== */
        .db-card {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 16px 20px 10px 20px;
            margin-bottom: 4px;
        }
        .db-card-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
        }
        .db-card-title {
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9 !important;
        }
        .db-card-title span {
            font-weight: 400;
            color: #94A3B8 !important;
            font-size: 14px;
        }
        .db-card-total {
            font-size: 13px;
            font-weight: 700;
            color: #00F2FE !important;
        }

        /* =====================================================
           PROGRESS OVERVIEW
        ===================================================== */
        .db-progress-title {
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9 !important;
            margin-bottom: 10px;
            margin-top: 4px;
            letter-spacing: -0.2px;
        }
        .db-metric-card {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 14px 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            text-align: center;
        }
        .db-metric-icon {
            font-size: 22px;
            line-height: 1;
            margin-bottom: 2px;
        }
        .db-metric-label {
            font-size: 10.5px;
            color: #64748B !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            line-height: 1.3;
        }
        .db-metric-value {
            font-size: 24px;
            font-weight: 800;
            color: #F1F5F9 !important;
            letter-spacing: -0.5px;
            line-height: 1;
        }
        .db-metric-delta {
            font-size: 11.5px;
            font-weight: 600;
            color: #22C55E !important;
        }

        /* =====================================================
           DISCOVER SHOWS — CỘT PHẢI
        ===================================================== */
        .db-discover-title {
            font-size: 18px;
            font-weight: 700;
            color: #F1F5F9 !important;
            letter-spacing: -0.2px;
            margin-bottom: 12px;
        }
        .db-url-row {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 10px;
        }
        .db-url-icon { font-size: 16px; }
        .db-url-placeholder {
            font-size: 13.5px;
            color: #475569 !important;
        }
        .db-show-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 4px;
        }
        .db-show-thumb-placeholder {
            width: 52px;
            height: 52px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(0,242,254,0.12) 0%, rgba(79,172,254,0.08) 100%);
            border: 1px solid rgba(0,242,254,0.12);
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }
        .db-show-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 2px;
            overflow: hidden;
        }
        .db-show-title {
            font-size: 13.5px;
            font-weight: 600;
            color: #F1F5F9 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .db-show-episodes {
            font-size: 12px;
            color: #64748B !important;
        }
        .db-learn-btn {
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: #00F2FE;
            color: #020617 !important;
            font-size: 12.5px;
            font-weight: 700;
            padding: 7px 13px;
            border-radius: 10px;
            white-space: nowrap;
            box-shadow: 0 0 10px rgba(0,242,254,0.35);
        }

        /* =====================================================
           LEARN BUTTON — Style đè st.button() thành pill cyan
           giống mockup: nền #00F2FE, chữ đen, bo tròn pill.
           Bọc bằng div.db-learn-btn-wrap trong dashboard_view.py
        ===================================================== */
        .db-learn-btn-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            padding-top: 10px;
            padding-bottom: 4px;
        }
        .db-learn-btn-wrap button {
            background: #00F2FE !important;
            color: #020617 !important;
            border: none !important;
            border-radius: 20px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            padding: 6px 12px !important;
            box-shadow: 0 0 10px rgba(0,242,254,0.4) !important;
            min-height: unset !important;
            height: 32px !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            letter-spacing: 0.01em !important;
            width: auto !important;
        }
        .db-learn-btn-wrap button:hover {
            background: #67f7ff !important;
            color: #020617 !important;
            box-shadow: 0 0 18px rgba(0,242,254,0.65) !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Dashboard CSS (db-) injected successfully.")

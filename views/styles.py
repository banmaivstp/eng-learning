import streamlit as st
import logging

logger = logging.getLogger("views.styles")

# =====================================================
# RE-EXPORT — Tương thích ngược với app.py
# CSS đã được tách ra file riêng biệt theo kiến trúc MVC:
#   views/dashboard_css.py  → inject_dashboard_css()
#   views/show_list_css.py  → inject_show_list_css()
# Import lại tại đây để app.py không cần đổi import.
# =====================================================
from views.dashboard_css import inject_dashboard_css  # noqa: F401  (re-export)
from views.show_list_css import inject_show_list_css   # noqa: F401  (re-export)

def inject_global_css():
    logger.debug("🎨 Injecting CSS system.")
    st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            overflow: hidden !important;
            height: 100vh !important;
        }
        .stApp {
            background:
                radial-gradient(circle at 50% 25%, rgba(0, 242, 254, 0.08), transparent 45%),
                linear-gradient(180deg, #020617 0%, #00030c 100%) !important;
            color: #F8FAFC !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        #MainMenu, footer, header { visibility: hidden !important; }
        .block-container {
            max-width: 850px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            box-sizing: border-box !important;
        }
        [data-testid="stVerticalBlock"] { gap: 0rem !important; }
        .element-container { margin-bottom: 0rem !important; }
        div[data-testid="stVerticalBlock"] > div { margin-bottom: 0px !important; margin-top: 0px !important; }

        /* CYBER GRID */
        .stApp::before {
            content: ""; position: fixed; inset: 0; pointer-events: none;
            background-image:
                linear-gradient(rgba(0, 242, 254, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 242, 254, 0.02) 1px, transparent 1px);
            background-size: 50px 50px; z-index: 1;
        }

        /* =====================================================
           NAVBAR
        ===================================================== */
        .navbar {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 24px; border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(20px); background: rgba(255,255,255,0.02);
            margin-bottom: 10px;
        }
        .login-brand { font-size: 18px; font-weight: 800; letter-spacing: -0.5px; color: #FFF !important; }
        .login-brand span { color: #00F2FE !important; }
        .navbar-links { display: flex; align-items: center; gap: 24px; color: #94A3B8; font-size: 13.5px; font-weight: 500; }
        .navbar-links span:hover { color: #00F2FE !important; cursor: pointer; }
        .signin-btn {
            padding: 5px 14px; border-radius: 10px;
            border: 1px solid rgba(0,242,254,0.4);
            background: rgba(0,242,254,0.08); color: #00F2FE !important; font-weight: 600;
        }

        /* =====================================================
           CARD — top và bottom ghép quanh vùng columns của nút
        ===================================================== */
        .login-card-top {
            width: 100%;
            max-width: 440px;
            margin: 0 auto;
            padding: 24px 24px 20px 24px;
            box-sizing: border-box;
            text-align: center;
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-bottom: none;
            border-radius: 20px 20px 0 0;
            background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
            box-shadow: 0 -10px 40px rgba(0,0,0,0.4);
        }
        .login-card-bottom {
            width: 100%;
            max-width: 440px;
            margin: 0 auto;
            height: 20px;
            box-sizing: border-box;
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-top: none;
            border-radius: 0 0 20px 20px;
            background: rgba(255,255,255,0.01);
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        }

        /* VÙNG CỘT CHỨA NÚT GOOGLE */
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe) {
            max-width: 440px !important;
            width: 100% !important;
            margin: 0 auto !important;
            padding: 12px 0 12px 0 !important;
            background: rgba(255,255,255,0.01) !important;
            border-left: 1px solid rgba(0, 242, 254, 0.25) !important;
            border-right: 1px solid rgba(0, 242, 254, 0.25) !important;
            box-sizing: border-box !important;
            gap: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe)
            > [data-testid="stColumn"]:first-child,
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe)
            > [data-testid="stColumn"]:last-child {
            display: none !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe)
            > [data-testid="stColumn"]:nth-child(2) {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
            padding: 0 24px !important;
            box-sizing: border-box !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe) iframe {
            width: 100% !important;
            max-width: 320px !important;
            display: block !important;
            margin: 0 auto !important;
        }

        /* =====================================================
           HERO CONTENT
        ===================================================== */
        .robot-avatar-circle {
            width: 48px; height: 48px; margin: 0 auto 10px auto;
            background: rgba(0,242,254,0.08); border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            border: 1px solid rgba(0,242,254,0.3);
        }
        .robot-avatar-circle svg { fill: #00F2FE; width: 20px; height: 20px; }
        .hero-title { font-size: 28px; font-weight: 800; line-height: 1.1; letter-spacing: -0.5px; color: #FFF !important; }
        .hero-accent { color: #00F2FE !important; }
        .hero-line { width: 35px; height: 2.5px; border-radius: 999px; margin: 10px auto; background: #00F2FE; }
        .hero-sub-title-top { font-size: 11.5px; color: #38BDF8 !important; font-weight: 700; letter-spacing: 0.8px; margin-bottom: 4px; text-transform: uppercase; }
        .hero-sub-title-main { font-size: 14px; color: #CBD5E1 !important; font-weight: 400; margin-bottom: 12px; }
        .hero-secure-text { color: #94A3B8 !important; font-size: 11px; letter-spacing: 0.2px; font-weight: 500; }

        /* =====================================================
           FEATURES
        ===================================================== */
        .feature-box {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 12px 14px !important;
            text-align: left !important;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            background: rgba(255,255,255,0.01);
            margin: 0px !important;
            box-sizing: border-box;
        }
        .feature-icon-circle {
            flex-shrink: 0 !important;
            width: 32px;
            height: 32px;
            margin: 0 !important;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0,242,254,0.05);
            border-radius: 50%;
        }
        .feature-icon-circle svg {
            fill: none;
            stroke: #00F2FE;
            stroke-width: 1.8;
            width: 16px;
            height: 16px;
        }
        .feature-text-group {
            display: flex;
            flex-direction: column;
        }
        .feature-heading {
            font-size: 13px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.2;
        }
        .feature-caption {
            color: #94A3B8 !important;
            font-size: 11.5px;
            margin-top: 2px;
            line-height: 1.2;
        }

        /* =====================================================
           FOOTER
        ===================================================== */
        .footer-center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding-top: 15px;
            color: #64748B !important;
            font-size: 11px;
            width: 100%;
            border-top: 1px solid rgba(255,255,255,0.04);
            margin-top: 10px;
        }
        .footer-center-links {
            display: flex;
            gap: 16px;
            font-weight: 600;
        }
        .footer-center-links span {
            cursor: pointer;
            color: #94A3B8 !important;
        }
        .footer-center-links span:hover {
            color: #00F2FE !important;
        }

    </style>
    """, unsafe_allow_html=True)


# =====================================================
# SIDEBAR CSS — THÊM MỚI (KHÔNG THAY ĐỔI CSS CŨ)
# Inject CSS riêng biệt cho Sidebar Gen Z Dark UI
# Quy tắc: CHỈ THÊM MỚI, KHÔNG SỬA ĐỔI inject_global_css()
# v3: Fix layout — profile top, nav gap đúng, bottom fixed ở đáy
# =====================================================
def inject_sidebar_css():
    """
    Inject CSS riêng biệt cho Sidebar Gen Z Dark UI — v3 Layout Fix.
    - Profile section cố định ở đầu
    - Nav menu ngay sau profile với gap hợp lý
    - Settings + Logout fixed cứng ở đáy sidebar (position: fixed)
    - Không chỉnh sửa inject_global_css() cũ
    """
    logger.debug("🎨 Injecting Sidebar Gen Z CSS v3 — layout fixed.")
    st.markdown("""
    <style>
        /* =====================================================
           SIDEBAR WRAPPER — Nền tối cyber dark
        ===================================================== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060D1A 0%, #040A14 60%, #030812 100%) !important;
            border-right: 1px solid rgba(0, 242, 254, 0.08) !important;
        }

        /* Bỏ padding mặc định của Streamlit trong sidebar */
        [data-testid="stSidebar"] > div:first-child {
            padding: 0 !important;
            overflow-x: hidden !important;
        }

        /* Đảm bảo sidebar content không overflow theo chiều ngang */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        /* =====================================================
           ẨN NÚT STREAMLIT MẶC ĐỊNH — giữ click area, bỏ visual
           Kỹ thuật: overlay button trong suốt đặt đè lên HTML div
        ===================================================== */
        [data-testid="stSidebar"] .stButton > button {
            opacity: 0 !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            width: 100% !important;
            display: block !important;
            pointer-events: auto !important;
        }

        /* Wrapper stButton: kéo ngược lên đè lên div HTML phía trên */
        [data-testid="stSidebar"] .stButton {
            margin-top: -54px !important;
            margin-bottom: 0 !important;
            height: 54px !important;
            position: relative !important;
            z-index: 5 !important;
        }

        /* =====================================================
           PROFILE SECTION — Ở đầu sidebar, padding rộng
        ===================================================== */
        .sb-profile-section {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 32px 18px 20px 18px;
            background: transparent;
        }

        /* Avatar với viền neon gradient xoay — giống mockup */
        .sb-avatar-ring {
            flex-shrink: 0;
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 40%, #a78bfa 100%);
            padding: 3px;
            box-shadow:
                0 0 0 1px rgba(0, 242, 254, 0.15),
                0 0 20px rgba(0, 242, 254, 0.5),
                0 0 50px rgba(0, 242, 254, 0.15);
        }
        .sb-avatar-img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
            display: block;
            border: 2.5px solid #060D1A;
        }
        .sb-avatar-placeholder {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: #0F1929;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            border: 2.5px solid #060D1A;
        }

        /* Thông tin tên + badge */
        .sb-profile-info {
            display: flex;
            flex-direction: column;
            gap: 7px;
            overflow: hidden;
            flex: 1;
        }
        .sb-user-name {
            font-size: 17px;
            font-weight: 700;
            color: #F1F5F9 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: -0.3px;
            line-height: 1.2;
        }
        .sb-streak-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11.5px;
            font-weight: 700;
            color: #FF6B35 !important;
            background: rgba(255, 107, 53, 0.1);
            border: 1px solid rgba(255, 107, 53, 0.28);
            border-radius: 20px;
            padding: 3px 10px;
            width: fit-content;
            letter-spacing: 0.1px;
        }

        /* =====================================================
           DIVIDER — Khoảng cách profile và nav
        ===================================================== */
        .sb-divider {
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(0, 242, 254, 0.12) 20%,
                rgba(0, 242, 254, 0.18) 50%,
                rgba(0, 242, 254, 0.12) 80%,
                transparent 100%
            );
            margin: 4px 16px 20px 16px;
        }

        /* =====================================================
           NAV SECTION — Menu items ngay sau divider
        ===================================================== */
        .sb-nav-section {
            padding: 0 10px;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        /* Mỗi nav item: flex row, viền trong suốt mặc định */
        .sb-nav-item {
            display: flex;
            align-items: center;
            gap: 13px;
            padding: 14px 14px;
            border-radius: 14px;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease;
            border: 1px solid transparent;
            position: relative;
            min-height: 52px;
            box-sizing: border-box;
        }
        .sb-nav-item:hover {
            background: rgba(0, 242, 254, 0.05) !important;
            border-color: rgba(0, 242, 254, 0.12) !important;
        }

        /* Active state: viền neon + nền mờ */
        .sb-nav-active {
            background: rgba(0, 242, 254, 0.07) !important;
            border: 1px solid rgba(0, 242, 254, 0.3) !important;
            box-shadow: inset 0 0 20px rgba(0, 242, 254, 0.03), 0 0 12px rgba(0, 242, 254, 0.06) !important;
        }

        /* Icon */
        .sb-nav-icon {
            flex-shrink: 0;
            width: 22px;
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #4B6070;
            transition: color 0.18s ease;
        }
        .sb-nav-icon svg { stroke: currentColor; }
        .sb-nav-icon-active { color: #00F2FE !important; }

        /* Label */
        .sb-nav-label {
            flex: 1;
            font-size: 15px;
            font-weight: 500;
            color: #7A92A8 !important;
            letter-spacing: -0.1px;
            line-height: 1;
        }
        .sb-nav-label-active {
            color: #EEF4FA !important;
            font-weight: 650;
        }

        /* Chevron */
        .sb-nav-chevron {
            color: #3A5068;
            display: flex;
            align-items: center;
            flex-shrink: 0;
        }
        .sb-nav-chevron svg { stroke: currentColor; }

        /* =====================================================
           BOTTOM SECTION — Fixed cứng ở đáy sidebar
           Dùng position: fixed để luôn dính đáy màn hình
           bất kể chiều cao content phía trên
        ===================================================== */
        .sb-bottom-section {
            position: fixed;
            bottom: 0;
            left: 0;
            /* Lấy đúng width của sidebar Streamlit (~21rem mặc định) */
            width: var(--sidebar-width, 21rem);
            padding: 0 10px 28px 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            /* Nền mờ để không chồng lên content nav khi scroll */
            background: linear-gradient(
                to bottom,
                transparent 0%,
                rgba(4, 10, 20, 0.96) 18%,
                rgba(3, 8, 18, 1) 100%
            );
            z-index: 100;
            box-sizing: border-box;
        }

        /* Nút Settings và Logout — full width trong bottom section */
        .sb-bottom-btn {
            display: flex;
            align-items: center;
            gap: 13px;
            padding: 14px 16px;
            border-radius: 14px;
            font-size: 14.5px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease;
            min-height: 52px;
            box-sizing: border-box;
            width: 100%;
        }

        .sb-settings-btn {
            color: #8FA8BE !important;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .sb-settings-btn:hover {
            background: rgba(255, 255, 255, 0.055) !important;
            border-color: rgba(255, 255, 255, 0.12) !important;
        }
        .sb-settings-btn .sb-nav-icon { color: #5A7890; }

        .sb-logout-btn {
            color: #F87171 !important;
            background: rgba(248, 113, 113, 0.06);
            border: 1px solid rgba(248, 113, 113, 0.18);
        }
        .sb-logout-btn:hover {
            background: rgba(248, 113, 113, 0.11) !important;
            border-color: rgba(248, 113, 113, 0.3) !important;
        }
        .sb-logout-btn .sb-nav-icon { color: #F87171; }

        /* Padding bottom cho nav section để không bị che bởi bottom fixed */
        .sb-nav-bottom-padding {
            height: 160px;
        }

        /* =====================================================
           Dọn dẹp margin/padding thừa của Streamlit elements
           trong sidebar — chỉ áp dụng cho sidebar
        ===================================================== */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            margin: 0 !important;
            line-height: 1 !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            width: 100% !important;
        }

        /* =====================================================
           SIDEBAR ENHANCEMENT v4 — Mockup alignment
           QUY TẮC: CHỈ THÊM MỚI — KHÔNG SỬA CSS CŨ PHÍA TRÊN
           Mục tiêu: Profile sát top hơn, avatar lớn hơn, Pro badge,
           nav item visual rõ hơn, button overlay chính xác hơn
        ===================================================== */

        /* --- PROFILE: đẩy sát top sidebar, giảm padding-top --- */
        .sb-profile-section {
            padding: 20px 18px 16px 18px !important;
        }

        /* --- AVATAR: lớn hơn (~80px) + glow neon xanh mạnh hơn theo mockup --- */
        .sb-avatar-ring {
            width: 80px !important;
            height: 80px !important;
            padding: 3px !important;
            box-shadow:
                0 0 0 2px rgba(0, 242, 254, 0.25),
                0 0 18px rgba(0, 242, 254, 0.7),
                0 0 45px rgba(0, 242, 254, 0.25) !important;
        }

        /* --- USERNAME: font to hơn, trắng sắc nét hơn --- */
        .sb-user-name {
            font-size: 19px !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            letter-spacing: -0.4px !important;
        }

        /* --- PRO BADGE: thêm badge "👑 Pro" màu cyan, tương tự mockup --- */
        .sb-pro-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 700;
            color: #00F2FE !important;
            background: rgba(0, 242, 254, 0.10);
            border: 1px solid rgba(0, 242, 254, 0.35);
            border-radius: 20px;
            padding: 3px 10px;
            width: fit-content;
            letter-spacing: 0.2px;
        }

        /* --- DIVIDER: sát hơn với profile --- */
        .sb-divider {
            margin: 2px 16px 16px 16px !important;
        }

        /* --- NAV SECTION: giảm gap giữa các item một chút --- */
        .sb-nav-section {
            padding: 0 8px !important;
            gap: 4px !important;
        }

        /* --- NAV ITEM: cao hơn, bo tròn đẹp hơn --- */
        .sb-nav-item {
            padding: 13px 16px !important;
            border-radius: 16px !important;
            min-height: 54px !important;
            gap: 14px !important;
        }

        /* --- ACTIVE NAV: viền neon sáng hơn, rõ nét hơn như mockup --- */
        .sb-nav-active {
            background: rgba(0, 242, 254, 0.09) !important;
            border: 1.5px solid rgba(0, 242, 254, 0.45) !important;
            box-shadow:
                inset 0 0 24px rgba(0, 242, 254, 0.04),
                0 0 16px rgba(0, 242, 254, 0.10) !important;
        }

        /* --- ICON ACTIVE: neon sáng hơn --- */
        .sb-nav-icon-active {
            color: #00F2FE !important;
            filter: drop-shadow(0 0 4px rgba(0, 242, 254, 0.7));
        }

        /* --- LABEL: font đẹp hơn --- */
        .sb-nav-label {
            font-size: 15.5px !important;
            font-weight: 500 !important;
        }
        .sb-nav-label-active {
            font-weight: 700 !important;
            color: #F0F9FF !important;
        }

        /* --- BUTTON OVERLAY: Streamlit button đè lên nav-item HTML ---
             Điều chỉnh margin-top để khớp với chiều cao nav-item 54px */
        [data-testid="stSidebar"] .stButton {
            margin-top: -58px !important;
            height: 58px !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            height: 58px !important;
        }

        /* --- BOTTOM BUTTONS: bo góc đẹp hơn, tương thích mockup --- */
        .sb-bottom-btn {
            border-radius: 16px !important;
            min-height: 54px !important;
            padding: 14px 18px !important;
        }

        /* --- SIDEBAR WIDTH: đảm bảo bottom section khớp width --- */
        [data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 280px !important;
        }
        .sb-bottom-section {
            width: 260px !important;
        }

    </style>
    """, unsafe_allow_html=True)

# =====================================================
# DASHBOARD CSS — ĐÃ TÁCH RA views/dashboard_css.py
# Hàm inject_dashboard_css() được re-export ở đầu file.
# Body giữ lại dưới đây để tham khảo lịch sử — KHÔNG thực thi.
# =====================================================
def _inject_dashboard_css_legacy():
    """
    [LEGACY — ĐÃ TÁCH] CSS Dashboard nay nằm tại views/dashboard_css.py.
    Hàm inject_dashboard_css() được import và re-export ở đầu styles.py.
    Hàm này KHÔNG được gọi — giữ lại chỉ để tra cứu.
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

    </style>
    """, unsafe_allow_html=True)


# =====================================================
# SIDEBAR TOGGLE FIX — HÀM MỚI ĐỘC LẬP
# Quy tắc: CHỈ THÊM MỚI — không sửa bất kỳ hàm cũ nào
# Mục đích: Fix nút mở/đóng sidebar luôn hiển thị và bấm được
# Nguyên nhân bug: inject_global_css() đặt overflow:hidden trên
#   html/body + header {visibility:hidden} ẩn toàn bộ thanh header
#   chứa nút toggle → sidebar đóng xong không mở lại được.
# =====================================================
def inject_sidebar_toggle_fix():
    """
    Fix cứng nút toggle sidebar của Streamlit luôn hiển thị,
    bất kể overflow/visibility CSS từ inject_global_css() cũ.
    GỌI HÀM NÀY SAU TẤT CẢ inject_*_css() khác trong app.py.
    """
    logger.debug("🔧 Injecting sidebar toggle visibility fix.")
    st.markdown("""
    <style>
        /* =====================================================
           SIDEBAR TOGGLE FIX v1
           Lý do inject_global_css() cũ gây bug:
             1. html,body { overflow: hidden } → clip nút toggle
             2. header { visibility: hidden } → ẩn nút collapse
             3. .sb-bottom-section { position:fixed; left:0 } →
                che đè nút hamburger khi sidebar đã đóng
           Giải pháp: Override lại đúng các element liên quan,
           không sửa inject_global_css() để tránh ảnh hưởng Login.
        ===================================================== */

        /* 1. Cho phép header container hiển thị lại (chỉ phần toggle) */
        header[data-testid="stHeader"] {
            visibility: visible !important;
            height: auto !important;
            background: transparent !important;
            pointer-events: none !important; /* Không block click vào content */
        }

        /* 2. Chỉ cho phép nút toggle sidebar pointer-events */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            pointer-events: auto !important;
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
        }

        /* 3. Nút collapse (khi sidebar đang mở — nút X/arrow bên trong sidebar) */
        [data-testid="stSidebarCollapseButton"] {
            position: relative !important;
            z-index: 99999 !important;
        }
        [data-testid="stSidebarCollapseButton"] button {
            background: rgba(0, 242, 254, 0.08) !important;
            border: 1px solid rgba(0, 242, 254, 0.2) !important;
            border-radius: 8px !important;
            color: #00F2FE !important;
            pointer-events: auto !important;
            cursor: pointer !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover {
            background: rgba(0, 242, 254, 0.15) !important;
        }
        [data-testid="stSidebarCollapseButton"] button svg {
            stroke: #00F2FE !important;
            fill: #00F2FE !important;
        }

        /* 4. Nút hamburger/expand (khi sidebar đang đóng — nằm ở top-left màn hình) */
        [data-testid="collapsedControl"] {
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 99999 !important;
            background: rgba(6, 13, 26, 0.92) !important;
            border: 1px solid rgba(0, 242, 254, 0.25) !important;
            border-radius: 10px !important;
            padding: 6px !important;
            backdrop-filter: blur(12px) !important;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.15) !important;
        }
        [data-testid="collapsedControl"] button {
            pointer-events: auto !important;
            cursor: pointer !important;
            background: transparent !important;
            border: none !important;
        }
        [data-testid="collapsedControl"] button svg {
            stroke: #00F2FE !important;
            fill: #00F2FE !important;
        }
        [data-testid="collapsedControl"]:hover {
            background: rgba(0, 242, 254, 0.1) !important;
            border-color: rgba(0, 242, 254, 0.4) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.25) !important;
        }

        /* 5. Đảm bảo overflow không clip nút toggle (override global css cũ) */
        html, body {
            overflow: clip !important; /* 'clip' thay 'hidden': không tạo scroll context mới */
        }

        /* 6. Đảm bảo stApp không clip overflow theo chiều ngang */
        .stApp {
            overflow-x: clip !important;
            overflow-y: clip !important;
        }

        /* 7. Fix lại sb-bottom-section để không che nút toggle */
        .sb-bottom-section {
            position: sticky !important;
            bottom: 0 !important;
            left: auto !important;
            width: auto !important;
            z-index: 50 !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Sidebar toggle fix injected successfully.")


# =====================================================
# PODCAST LIST CSS — THÊM MỚI (KHÔNG THAY ĐỔI CSS CŨ)
# Quy tắc: CHỈ THÊM MỚI — không sửa bất kỳ hàm nào cũ
# Màn hình: Your Podcast Library (Discover / Show List)
# =====================================================
def inject_podcast_list_css():
    """
    Inject CSS riêng cho màn hình Podcast Library — Gen Z Dark UI.
    CHỈ THÊM MỚI — không đụng inject_global_css() / inject_sidebar_css()
    / inject_dashboard_css() / inject_sidebar_toggle_fix().
    """
    logger.debug("🎨 Injecting Podcast List CSS (Show Library UI).")
    st.markdown("""
    <style>
        /* =====================================================
           PODCAST LIBRARY — PAGE HEADER
        ===================================================== */
        .pl-page-title {
            font-size: 34px;
            font-weight: 900;
            color: #F1F5F9 !important;
            letter-spacing: -0.8px;
            line-height: 1.1;
            margin-bottom: 6px;
        }
        .pl-page-subtitle {
            font-size: 14px;
            color: #64748B !important;
            font-weight: 400;
            margin-bottom: 20px;
            letter-spacing: 0.1px;
        }

        /* =====================================================
           SEARCH BAR ROW
        ===================================================== */
        .pl-search-row {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 11px 16px;
            margin-bottom: 24px;
            transition: border-color 0.2s ease;
        }
        .pl-search-row:hover {
            border-color: rgba(0, 242, 254, 0.2);
        }
        .pl-search-icon {
            font-size: 16px;
            flex-shrink: 0;
            color: #475569;
        }
        .pl-search-placeholder {
            font-size: 14px;
            color: #475569 !important;
            font-weight: 400;
        }

        /* =====================================================
           ADD NEW SHOW EXPANDER BUTTON
        ===================================================== */
        .pl-add-show-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 242, 254, 0.07);
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-radius: 12px;
            padding: 10px 18px;
            color: #00F2FE !important;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 20px;
            transition: background 0.2s ease, box-shadow 0.2s ease;
        }
        .pl-add-show-btn:hover {
            background: rgba(0, 242, 254, 0.12);
            box-shadow: 0 0 14px rgba(0, 242, 254, 0.2);
        }

        /* =====================================================
           SHOW GRID — 2 CỘT DESKTOP, 1 CỘT MOBILE
        ===================================================== */
        .pl-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }
        @media (max-width: 600px) {
            .pl-grid { grid-template-columns: 1fr; }
        }

        /* =====================================================
           SHOW CARD — Mỗi ô trong grid
        ===================================================== */
        .pl-show-card {
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 16px 18px;
            position: relative;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            min-height: 90px;
        }
        .pl-show-card:hover {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.06) !important;
        }

        /* Cover image thumbnail — 80x80 bo tròn */
        .pl-show-thumb {
            width: 80px;
            height: 80px;
            border-radius: 12px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.07);
            background: linear-gradient(135deg, rgba(0,242,254,0.12) 0%, rgba(79,172,254,0.08) 100%);
        }
        /* Fallback placeholder khi không có ảnh */
        .pl-show-thumb-placeholder {
            width: 80px;
            height: 80px;
            border-radius: 12px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,242,254,0.10) 0%, rgba(79,172,254,0.06) 100%);
            border: 1px solid rgba(0,242,254,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
        }

        /* Text info bên phải thumbnail */
        .pl-show-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow: hidden;
        }
        .pl-show-title {
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.25;
            /* Wrap tối đa 2 dòng */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .pl-show-episodes {
            font-size: 13px;
            font-weight: 600;
            color: #00F2FE !important;
            letter-spacing: 0.1px;
        }

        /* Nút ⋯ góc phải trên */
        .pl-show-more-btn {
            position: absolute;
            top: 14px;
            right: 14px;
            color: #3A5068 !important;
            font-size: 18px;
            line-height: 1;
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 6px;
            transition: color 0.15s ease, background 0.15s ease;
        }
        .pl-show-more-btn:hover {
            color: #00F2FE !important;
            background: rgba(0,242,254,0.08);
        }

        /* =====================================================
           LIST VIEW (Mobile) — 1 cột dạng row
        ===================================================== */
        .pl-list-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 6px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            position: relative;
            transition: background 0.15s ease;
        }
        .pl-list-item:last-child { border-bottom: none; }
        .pl-list-item:hover { background: rgba(255,255,255,0.02); border-radius: 10px; }

        .pl-list-thumb {
            width: 56px;
            height: 56px;
            border-radius: 10px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.07);
            background: linear-gradient(135deg, rgba(0,242,254,0.10), rgba(79,172,254,0.06));
        }
        .pl-list-thumb-placeholder {
            width: 56px;
            height: 56px;
            border-radius: 10px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,242,254,0.10), rgba(79,172,254,0.06));
            border: 1px solid rgba(0,242,254,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .pl-list-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 3px;
            overflow: hidden;
        }
        .pl-list-title {
            font-size: 14.5px;
            font-weight: 700;
            color: #F1F5F9 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .pl-list-episodes {
            font-size: 12.5px;
            font-weight: 600;
            color: #00F2FE !important;
        }
        .pl-list-more-btn {
            color: #3A5068 !important;
            font-size: 18px;
            flex-shrink: 0;
            padding: 4px 6px;
            border-radius: 6px;
            cursor: pointer;
        }

        /* =====================================================
           EMPTY STATE — Khi chưa có show nào trong DB
        ===================================================== */
        .pl-empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #475569 !important;
        }
        .pl-empty-icon { font-size: 48px; margin-bottom: 14px; }
        .pl-empty-title {
            font-size: 18px;
            font-weight: 700;
            color: #94A3B8 !important;
            margin-bottom: 8px;
        }
        .pl-empty-sub {
            font-size: 14px;
            color: #475569 !important;
        }

        /* =====================================================
           LOADING STATE
        ===================================================== */
        .pl-loading-text {
            text-align: center;
            color: #64748B !important;
            font-size: 14px;
            padding: 30px 0;
        }

        /* =====================================================
           SECTION HEADER (khi có thêm show mới)
        ===================================================== */
        .pl-section-label {
            font-size: 13px;
            font-weight: 700;
            color: #475569 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin: 16px 0 10px 4px;
        }

        /* =====================================================
           INPUT BOX cho Add Show (expander nội dung)
        ===================================================== */
        /* Streamlit expander override cho sidebar context */
        [data-testid="stExpander"] {
            background: rgba(255,255,255,0.02) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 14px !important;
            margin-bottom: 20px !important;
        }
        [data-testid="stExpander"] summary {
            color: #94A3B8 !important;
            font-weight: 600 !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Podcast List CSS injected successfully.")

# =====================================================
# SHOW LIST VIEW CSS — ĐÃ TÁCH RA views/show_list_css.py
# Hàm inject_show_list_css() được re-export ở đầu file.
# Body giữ lại dưới đây để tham khảo lịch sử — KHÔNG thực thi.
# =====================================================
def _inject_show_list_css_legacy():
    """
    [LEGACY — ĐÃ TÁCH] CSS Show List nay nằm tại views/show_list_css.py.
    Hàm inject_show_list_css() được import và re-export ở đầu styles.py.
    Hàm này KHÔNG được gọi — giữ lại chỉ để tra cứu.
    """
    logger.debug("🎨 Injecting Show List CSS (sl- prefix) — Milestone 2.")
    st.markdown("""
    <style>
        /* =====================================================
           PAGE HEADER — "Your Podcast Library"
        ===================================================== */
        .sl-page-header {
            margin-bottom: 20px;
            padding-bottom: 4px;
        }
        .sl-page-title {
            font-size: 28px;
            font-weight: 800;
            color: #F1F5F9 !important;
            letter-spacing: -0.6px;
            line-height: 1.15;
            margin-bottom: 4px;
        }
        .sl-page-sub {
            font-size: 14px;
            color: #64748B !important;
            font-weight: 400;
        }

        /* =====================================================
           SHOW CARD — Grid item (desktop 2 cột)
           Prefix sl- để không đụng .pl-show-card cũ
        ===================================================== */
        .sl-show-card {
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 16px 18px;
            position: relative;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            min-height: 88px;
            box-sizing: border-box;
            margin-bottom: 2px;
        }
        .sl-show-card:hover {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.06) !important;
        }

        /* Cover image thumbnail */
        .sl-show-thumb {
            width: 72px;
            height: 72px;
            border-radius: 12px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        /* Fallback placeholder emoji */
        .sl-show-thumb-placeholder {
            width: 72px;
            height: 72px;
            border-radius: 12px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,242,254,0.10) 0%, rgba(79,172,254,0.06) 100%);
            border: 1px solid rgba(0,242,254,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
        }

        /* Text block bên phải thumbnail */
        .sl-show-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow: hidden;
        }
        .sl-show-title {
            font-size: 15px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .sl-show-episodes {
            font-size: 13px;
            font-weight: 600;
            color: #00F2FE !important;
            letter-spacing: 0.1px;
        }

        /* Nút ⋯ góc phải trên card */
        .sl-show-more-btn {
            position: absolute;
            top: 12px;
            right: 12px;
            color: #3A5068 !important;
            font-size: 18px;
            line-height: 1;
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 6px;
            transition: color 0.15s ease, background 0.15s ease;
        }
        .sl-show-more-btn:hover {
            color: #00F2FE !important;
            background: rgba(0,242,254,0.08);
        }

        /* =====================================================
           OPEN BUTTON — Streamlit button overlay trên card
           Dùng kỹ thuật negative margin-top giống sidebar nav
        ===================================================== */
        .sl-card-wrapper .stButton > button {
            opacity: 0 !important;
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            z-index: 5 !important;
        }
        .sl-card-wrapper {
            position: relative;
        }

        /* =====================================================
           EMPTY STATE
        ===================================================== */
        .sl-empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #475569 !important;
        }
        .sl-empty-icon { font-size: 52px; margin-bottom: 16px; }
        .sl-empty-title {
            font-size: 18px;
            font-weight: 700;
            color: #94A3B8 !important;
            margin-bottom: 8px;
        }
        .sl-empty-sub {
            font-size: 14px;
            color: #475569 !important;
            line-height: 1.5;
        }

        /* =====================================================
           SEARCH INPUT — Override Streamlit text_input style
           chỉ trong context màn hình show list
        ===================================================== */
        /* Không override global — chỉ nhắm vào block-container context */

        /* =====================================================
           ADD SHOW EXPANDER — Style riêng cho Show List
        ===================================================== */
        .sl-add-row {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(0, 242, 254, 0.04);
            border: 1px solid rgba(0, 242, 254, 0.15);
            border-radius: 14px;
            margin-bottom: 16px;
        }
        .sl-add-icon { font-size: 18px; }
        .sl-add-label {
            font-size: 13.5px;
            font-weight: 600;
            color: #00F2FE !important;
        }

        /* =====================================================
           SECTION LABEL — "Your Shows", "Recently Added" v.v.
        ===================================================== */
        .sl-section-label {
            font-size: 13px;
            font-weight: 700;
            color: #475569 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin: 8px 0 12px 2px;
        }

        /* =====================================================
           CARD WRAPPER — bao ngoài card HTML + button overlay
           Đảm bảo button Streamlit được ẩn hoàn toàn và
           overlay chính xác lên card (position: relative + absolute)
        ===================================================== */
        .sl-card-wrapper {
            position: relative !important;
            display: block !important;
            margin-bottom: 12px !important;
        }
        /* Ẩn button Streamlit bên trong sl-card-wrapper:
           opacity:0 giữ nguyên vùng click, text "_" không hiển thị */
        .sl-card-wrapper > div[data-testid="stButton"],
        .sl-card-wrapper div[data-testid="stButton"] {
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 10 !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"] > button,
        .sl-card-wrapper div[data-testid="stButton"] > button {
            opacity: 0 !important;
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 16px !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            z-index: 10 !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        /* Đặt card HTML lên trước button nhưng pointer-events:none
           để click xuyên qua HTML card xuống button overlay */
        .sl-card-wrapper .sl-show-card {
            pointer-events: none !important;
            margin-bottom: 0 !important;
            position: relative !important;
            z-index: 1 !important;
        }
        /* Hover effect vẫn hoạt động qua CSS :has() selector */
        .sl-card-wrapper:hover .sl-show-card {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.06) !important;
        }

        /* =====================================================
           COVER IMAGE ENHANCED — Gradient overlay cho fallback
        ===================================================== */
        .sl-show-thumb-placeholder {
            background: linear-gradient(135deg,
                rgba(79, 172, 254, 0.15) 0%,
                rgba(0, 242, 254, 0.08) 50%,
                rgba(147, 51, 234, 0.10) 100%) !important;
            border: 1px solid rgba(0, 242, 254, 0.15) !important;
        }
        /* Cover image có shadow để nổi hơn trên nền tối */
        .sl-show-thumb {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        }

        /* =====================================================
           PAGE HEADER — Căn chỉnh theo mockup:
           Title + subtitle bên trái, search bar bên phải
           (Streamlit không cho layout inline nên dùng flexbox
            trên sl-page-header + ẩn mặc định search input vào row)
        ===================================================== */
        .sl-page-title {
            font-size: 32px !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            letter-spacing: -0.8px !important;
            line-height: 1.1 !important;
            margin-bottom: 6px !important;
        }
        .sl-page-sub {
            font-size: 14px !important;
            color: #475569 !important;
            font-weight: 400 !important;
            margin-bottom: 20px !important;
        }

        /* =====================================================
           SEARCH INPUT — Override Streamlit text_input style
           Target theo data-testid của input có key="sl_search_input"
        ===================================================== */
        [data-testid="stTextInput"] input[aria-label="Search shows"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #F1F5F9 !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
        }
        [data-testid="stTextInput"] input[aria-label="Search shows"]:focus {
            border-color: rgba(0, 242, 254, 0.35) !important;
            box-shadow: 0 0 0 3px rgba(0, 242, 254, 0.08) !important;
        }
        [data-testid="stTextInput"] input[aria-label="Search shows"]::placeholder {
            color: #475569 !important;
        }

        /* =====================================================
           GRID ROW — Đảm bảo gap giữa 2 cột card đồng đều
        ===================================================== */
        .sl-card-wrapper + .sl-card-wrapper {
            margin-top: 0 !important;
        }

        /* =====================================================
           EXPANDER (Add Show) — Style theo mockup
        ===================================================== */
        [data-testid="stExpander"] {
            background: rgba(0, 242, 254, 0.02) !important;
            border: 1px solid rgba(0, 242, 254, 0.10) !important;
            border-radius: 14px !important;
            margin-bottom: 16px !important;
        }
        [data-testid="stExpander"] summary {
            color: #00F2FE !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
        }

        /* =====================================================
           FIX v3 — SHOW CARD OPEN BUTTON
           Quy tắc: CHỈ THÊM MỚI — không sửa CSS cũ phía trên.

           Vấn đề cũ: invisible button overlay gây click sai vùng.
           Giải pháp mới: button Streamlit hiển thị thật, style thành
           nút nhỏ gọn nằm dưới card, màu neon phù hợp dark UI.
        ===================================================== */

        /* --- SHOW CARD: margin-bottom nhỏ hơn để không kéo cách xa button --- */
        .sl-show-card {
            margin-bottom: 4px !important;
            pointer-events: auto !important;  /* card HTML không cần pointer-events:none nữa */
            cursor: default !important;
        }

        /* --- OPEN BUTTON: style nút mở show — nằm ngay dưới card --- */
        /* Target nút có label bắt đầu bằng "▶ Open" trong context show list */
        [data-testid="stMainBlockContainer"] button[kind="secondary"]:is([data-testid="stBaseButton-secondary"]) {
            /* Reset về mặc định trước — override CSS ẩn cũ nếu còn sót */
            opacity: 1 !important;
            position: static !important;
            height: auto !important;
            min-height: 36px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #00F2FE !important;
            background: rgba(0, 242, 254, 0.06) !important;
            border: 1px solid rgba(0, 242, 254, 0.20) !important;
            border-radius: 10px !important;
            padding: 6px 14px !important;
            margin-top: 0 !important;
            margin-bottom: 14px !important;
            cursor: pointer !important;
            letter-spacing: 0.1px !important;
            transition: background 0.15s ease, border-color 0.15s ease !important;
        }
        [data-testid="stMainBlockContainer"] button[kind="secondary"]:is([data-testid="stBaseButton-secondary"]):hover {
            background: rgba(0, 242, 254, 0.12) !important;
            border-color: rgba(0, 242, 254, 0.40) !important;
            color: #ffffff !important;
        }

        /* --- WRAPPER CŨ sl-card-wrapper: reset để không ảnh hưởng nếu còn sót --- */
        .sl-card-wrapper {
            position: static !important;
        }
        .sl-card-wrapper .sl-show-card {
            pointer-events: auto !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"],
        .sl-card-wrapper div[data-testid="stButton"] {
            position: static !important;
            width: 100% !important;
            height: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: auto !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"] > button,
        .sl-card-wrapper div[data-testid="stButton"] > button {
            opacity: 1 !important;
            position: static !important;
            height: auto !important;
            min-height: 36px !important;
        }

        /* =====================================================
           FIX v3 — SIDEBAR NAV BUTTON OVERLAP
           Vấn đề: margin-top:-58px kéo button quá cao, overlap
           sang item phía trên → click "Discover" bị hiểu là "Quiz".

           Giải pháp: Giảm margin-top về đúng chiều cao nav-item
           thực tế = 46px (padding 13px*2 + line-height ~20px).
           Đồng thời clamp height button bằng height nav-item.
        ===================================================== */
        [data-testid="stSidebar"] .stButton {
            margin-top: -46px !important;  /* khớp với min-height nav-item thực tế */
            height: 46px !important;
            overflow: hidden !important;   /* chặn vùng click tràn ra ngoài */
            z-index: 5 !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            height: 46px !important;
            min-height: 0 !important;
            max-height: 46px !important;
            overflow: hidden !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Show List CSS (sl-) injected successfully — v3: card open-btn fix + sidebar overlap fix.")


# =====================================================
# PODCAST LIST VIEW CSS — THÊM MỚI (Milestone 2 - Episode List)
# Quy tắc: CHỈ THÊM MỚI vào file — KHÔNG thay đổi code cũ
# Màn hình: "Danh sách bài học" của một show đã chọn
# Prefix CSS: "pcl-" (podcast_list)
# =====================================================
def inject_podcast_list_view_css():
    """
    Inject CSS riêng cho màn hình Episode List (podcast_list_view).
    Prefix 'pcl-' để tránh conflict với sl-, pl-, db-, sb-.
    CHỈ THÊM MỚI — không sửa bất kỳ hàm inject_*_css() cũ nào.
    """
    import streamlit as st
    import logging
    _logger = logging.getLogger("views.styles")
    _logger.debug("🎨 Injecting Podcast List View CSS (pcl- prefix) — Episode List screen.")
    st.markdown("""
    <style>
        /* =====================================================
           BACK BUTTON ROW — nút quay lại + label "Your Library"
        ===================================================== */
        .pcl-back-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            cursor: pointer;
            width: fit-content;
        }
        .pcl-back-arrow {
            font-size: 18px;
            color: #64748B !important;
            line-height: 1;
        }
        .pcl-back-label {
            font-size: 14px;
            font-weight: 600;
            color: #64748B !important;
            letter-spacing: 0.1px;
        }
        .pcl-back-row:hover .pcl-back-arrow,
        .pcl-back-row:hover .pcl-back-label {
            color: #00F2FE !important;
        }

        /* Ẩn Streamlit back button (để click area vào .pcl-back-row HTML thay thế) */
        /* Sử dụng kỹ thuật: render st.button sau markdown, margin-top âm để overlap */

        /* =====================================================
           PAGE HEADER — Cover nhỏ + Title + Show name
        ===================================================== */
        .pcl-page-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .pcl-header-icon-area {
            flex-shrink: 0;
        }
        .pcl-header-cover {
            width: 56px;
            height: 56px;
            border-radius: 12px;
            object-fit: cover;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            display: block;
        }
        .pcl-header-cover-placeholder {
            width: 56px;
            height: 56px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(0,242,254,0.12) 0%, rgba(79,172,254,0.08) 50%, rgba(147,51,234,0.08) 100%);
            border: 1px solid rgba(0, 242, 254, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            flex-shrink: 0;
        }
        .pcl-header-text {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
            overflow: hidden;
        }
        .pcl-page-title {
            font-size: 22px;
            font-weight: 800;
            color: #F1F5F9 !important;
            letter-spacing: -0.4px;
            line-height: 1.1;
        }
        .pcl-page-show-name {
            font-size: 13.5px;
            font-weight: 500;
            color: #64748B !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* =====================================================
           SEARCH + SORT ROW — Override Streamlit inputs
        ===================================================== */
        /* Search input */
        [data-testid="stTextInput"] input[aria-label="Tìm bài học"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #F1F5F9 !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
            transition: border-color 0.2s ease !important;
        }
        [data-testid="stTextInput"] input[aria-label="Tìm bài học"]:focus {
            border-color: rgba(0, 242, 254, 0.35) !important;
            box-shadow: 0 0 0 3px rgba(0, 242, 254, 0.08) !important;
        }
        [data-testid="stTextInput"] input[aria-label="Tìm bài học"]::placeholder {
            color: #475569 !important;
        }

        /* Sort selectbox */
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #94A3B8 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
            border-color: rgba(0, 242, 254, 0.25) !important;
        }

        /* =====================================================
           COUNT LABEL — "3 bài học"
        ===================================================== */
        .pcl-count-label {
            font-size: 13px;
            font-weight: 600;
            color: #475569 !important;
            letter-spacing: 0.2px;
            margin: 8px 0 12px 2px;
        }

        /* =====================================================
           EPISODE ROW — layout hàng ngang: thumb | info | play
        ===================================================== */
        .pcl-episode-row {
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 2px;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            position: relative;
        }
        .pcl-episode-row:hover {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 18px rgba(0, 242, 254, 0.06) !important;
        }

        /* Episode thumbnail — square dùng ảnh cover của show */
        .pcl-ep-thumb {
            width: 72px;
            height: 72px;
            border-radius: 10px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
        }
        .pcl-ep-thumb-placeholder {
            width: 72px;
            height: 72px;
            border-radius: 10px;
            flex-shrink: 0;
            background: linear-gradient(135deg,
                rgba(79, 172, 254, 0.18) 0%,
                rgba(0, 242, 254, 0.10) 50%,
                rgba(147, 51, 234, 0.12) 100%);
            border: 1px solid rgba(0, 242, 254, 0.14);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }

        /* Episode info block */
        .pcl-ep-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow: hidden;
        }
        .pcl-ep-badge {
            font-size: 11.5px;
            font-weight: 700;
            color: #00F2FE !important;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        .pcl-ep-title {
            font-size: 15px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .pcl-ep-duration {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 13px;
            font-weight: 600;
            color: #00F2FE !important;
            letter-spacing: 0.1px;
        }
        .pcl-ep-duration-icon {
            font-size: 13px;
        }

        /* Play button circle — góc phải */
        .pcl-ep-play-btn {
            flex-shrink: 0;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: rgba(0, 242, 254, 0.08);
            border: 1.5px solid rgba(0, 242, 254, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #00F2FE !important;
            transition: background 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            box-shadow: 0 0 8px rgba(0, 242, 254, 0.1);
        }
        .pcl-ep-play-btn svg {
            width: 20px;
            height: 20px;
            stroke: #00F2FE;
        }
        .pcl-episode-row:hover .pcl-ep-play-btn {
            background: rgba(0, 242, 254, 0.16) !important;
            border-color: rgba(0, 242, 254, 0.6) !important;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.3) !important;
        }

        /* =====================================================
           OVERLAY BUTTON — Streamlit button ẩn đè lên episode row
           Kỹ thuật: margin-top âm để button nằm đè lên HTML div
        ===================================================== */
        .pcl-episode-row + div[data-testid="stButton"],
        .pcl-episode-row ~ div[data-testid="stButton"] {
            margin-top: -74px !important;
            height: 74px !important;
            overflow: hidden !important;
            position: relative !important;
            z-index: 5 !important;
            margin-bottom: 10px !important;
        }
        .pcl-episode-row + div[data-testid="stButton"] > button,
        .pcl-episode-row ~ div[data-testid="stButton"] > button {
            opacity: 0 !important;
            width: 100% !important;
            height: 74px !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            font-size: 0 !important;
            color: transparent !important;
        }

        /* =====================================================
           BACK BUTTON — style ẩn, overlap vào back-row HTML
        ===================================================== */
        .pcl-back-row + div[data-testid="stButton"],
        .pcl-back-row ~ div:first-of-type[data-testid="stButton"] {
            margin-top: -28px !important;
            height: 28px !important;
            overflow: hidden !important;
            z-index: 5 !important;
        }
        .pcl-back-row + div[data-testid="stButton"] > button {
            opacity: 0 !important;
            width: 200px !important;
            height: 28px !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            cursor: pointer !important;
            font-size: 0 !important;
        }

        /* =====================================================
           EMPTY STATE
        ===================================================== */
        .pcl-empty-state {
            text-align: center;
            padding: 60px 20px;
        }
        .pcl-empty-icon {
            font-size: 52px;
            margin-bottom: 16px;
        }
        .pcl-empty-title {
            font-size: 18px;
            font-weight: 700;
            color: #94A3B8 !important;
            margin-bottom: 8px;
        }
        .pcl-empty-sub {
            font-size: 14px;
            color: #475569 !important;
            line-height: 1.5;
        }

        /* =====================================================
           RESPONSIVE — Mobile (max 600px)
        ===================================================== */
        @media (max-width: 600px) {
            .pcl-page-title { font-size: 18px !important; }
            .pcl-ep-thumb, .pcl-ep-thumb-placeholder { width: 58px !important; height: 58px !important; }
            .pcl-ep-title { font-size: 13.5px !important; }
            .pcl-header-cover, .pcl-header-cover-placeholder { width: 44px !important; height: 44px !important; }
        }

    </style>
    """, unsafe_allow_html=True)
    _logger.debug("✅ Podcast List View CSS (pcl-) injected successfully.")



# =====================================================
# QUIZ DETAIL VIEW CSS — THÊM MỚI (Milestone 3+4+5)
# Quy tắc: CHỈ THÊM MỚI vào file — KHÔNG thay đổi code cũ
# Màn hình: Audio Player + Transcript Highlight + Quiz Tapping
# Prefix CSS: "qd-" (quiz_detail)
# =====================================================
def inject_quiz_detail_css():
    """
    Inject CSS riêng cho màn hình Quiz Detail — Audio Player + Transcript + Quiz.
    Prefix 'qd-' để tránh conflict với sl-, pl-, db-, sb-, pcl-.
    CHỌ THÊM MỚI — không sửa bất kỳ hàm inject_*_css() cũ nào.
    Milestone 3: Audio Player custom HTML5
    Milestone 4: Transcript Highlight interactive
    Milestone 5: Quiz Tapping large tap targets
    """
    logger.debug("🎨 Injecting Quiz Detail CSS (qd- prefix) — Milestone 3+4+5.")
    st.markdown("""
    <style>
        /* =====================================================
           BACK ROW — nút quay lại đầu màn hình
        ===================================================== */
        .qd-back-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            cursor: pointer;
            width: fit-content;
        }
        .qd-back-arrow {
            font-size: 18px;
            color: #64748B !important;
        }
        .qd-back-label {
            font-size: 14px;
            font-weight: 600;
            color: #64748B !important;
        }
        .qd-back-row:hover .qd-back-arrow,
        .qd-back-row:hover .qd-back-label {
            color: #00F2FE !important;
        }

        /* Back button Streamlit — ẩn, dùng HTML làm visual */
        .qd-back-row + div[data-testid="stButton"] > button {
            opacity: 0 !important;
            height: 28px !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            margin-top: -28px !important;
            width: 200px !important;
            font-size: 0 !important;
        }

        /* =====================================================
           PLAYER SECTION WRAPPER
        ===================================================== */
        .qd-player-section {
            margin-bottom: 18px;
        }

        /* =====================================================
           SECTION HEADER — "Transcript", "Question"
        ===================================================== */
        .qd-section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        .qd-section-icon {
            font-size: 18px;
            line-height: 1;
        }
        .qd-section-title {
            font-size: 18px;
            font-weight: 700;
            color: #F1F5F9 !important;
            letter-spacing: -0.2px;
        }

        /* Hide/Show button style */
        .qd-transcript-section button[kind="secondary"] {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: #64748B !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 4px 10px !important;
            border-radius: 8px !important;
            min-height: 30px !important;
        }
        .qd-transcript-section button[kind="secondary"]:hover {
            color: #00F2FE !important;
            border-color: rgba(0,242,254,0.3) !important;
        }

        /* =====================================================
           TRANSCRIPT BOX — scrollable container
        ===================================================== */
        .qd-transcript-box {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 12px 4px;
            max-height: 280px;
            overflow-y: auto;
            margin-bottom: 0px;
            /* Scrollbar styling */
            scrollbar-width: thin;
            scrollbar-color: rgba(0,242,254,0.2) transparent;
        }
        .qd-transcript-box::-webkit-scrollbar {
            width: 4px;
        }
        .qd-transcript-box::-webkit-scrollbar-track {
            background: transparent;
        }
        .qd-transcript-box::-webkit-scrollbar-thumb {
            background: rgba(0,242,254,0.2);
            border-radius: 2px;
        }

        /* =====================================================
           SENTENCE ROW — từng dòng transcript, update: gap: 12px;margin-bottom: 2px;
        ===================================================== */
        .qd-sentence-row {
            display: flex;
            align-items: flex-start;
            gap: 5px;
            padding: 8px 14px;
            border-radius: 10px;
            margin-bottom: 0px;
            cursor: pointer;
            transition: background 0.15s ease;
            border-left: 3px solid transparent;
        }
        .qd-sentence-row:hover {
            background: rgba(255,255,255,0.03) !important;
        }

        /* Active sentence — highlight neon cyan */
        .qd-sentence-active {
            background: rgba(0,242,254,0.07) !important;
            border-left-color: #00F2FE !important;
        }
        .qd-sentence-active .qd-sentence-text {
            color: #00F2FE !important;
            font-weight: 700 !important;
        }
        .qd-sentence-active .qd-timestamp {
            color: #00F2FE !important;
            opacity: 0.8;
        }

        /* Inactive sentence — mờ nhẹ */
        .qd-sentence-inactive .qd-sentence-text {
            color: #94A3B8 !important;
            font-weight: 400 !important;
        }
        .qd-sentence-inactive .qd-timestamp {
            color: #3A5068 !important;
        }

        .qd-timestamp {
            font-size: 12px;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            flex-shrink: 0;
            margin-top: 2px;
            min-width: 36px;
            letter-spacing: 0.2px;
        }
        .qd-sentence-text {
            font-size: 14.5px;
            line-height: 1.55;
            transition: color 0.15s ease, font-weight 0.15s ease;
        }

        /* =====================================================
           SENTENCE NAVIGATION
        ===================================================== */
        .qd-sentence-progress {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .qd-sentence-progress-label {
            font-size: 13px;
            font-weight: 600;
            color: #64748B !important;
        }

        /* Prev/Next buttons */
        .qd-transcript-section .stButton > button {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: #94A3B8 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            min-height: 36px !important;
            transition: all 0.15s ease !important;
        }
        .qd-transcript-section .stButton > button:hover {
            background: rgba(0,242,254,0.06) !important;
            border-color: rgba(0,242,254,0.25) !important;
            color: #00F2FE !important;
        }

        /* =====================================================
           QUIZ SECTION WRAPPER : margin-top: 4px;
        ===================================================== */
        .qd-quiz-section {
            margin-top: 0px;
        }

        /* =====================================================
           QUIZ PROGRESS BAR: margin-bottom: 14px;
        ===================================================== */
        .qd-quiz-progress {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            margin-top: 10px;
        }
        .qd-quiz-progress-label {
            font-size: 12px;
            font-weight: 700;
            color: #475569 !important;
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .qd-quiz-progress-bar {
            flex: 1;
            height: 4px;
            background: rgba(255,255,255,0.06);
            border-radius: 2px;
            overflow: hidden;
        }
        .qd-quiz-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00F2FE, #4FACFE);
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        /* =====================================================
           QUESTION TEXT
        ===================================================== */
        .qd-question-text {
            font-size: 17px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.5;
            margin-bottom: 16px;
            letter-spacing: -0.2px;
        }

        /* =====================================================
           OPTION CARDS — Tapping targets lớn, tương phản cao
        ===================================================== */
        .qd-option-card {
            display: flex;
            align-items: center;
            gap: 14px;
            background: rgba(255,255,255,0.03);
            border: 1.5px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 2px;
            cursor: pointer;
            transition: all 0.15s ease;
            min-height: 54px;
        }
        .qd-option-card:hover {
            background: rgba(0,242,254,0.05) !important;
            border-color: rgba(0,242,254,0.25) !important;
        }

        /* Selected option — filled neon border */
        .qd-option-selected {
            background: rgba(0,242,254,0.10) !important;
            border-color: rgba(0,242,254,0.55) !important;
            box-shadow: 0 0 0 1px rgba(0,242,254,0.15), 0 0 16px rgba(0,242,254,0.12) !important;
        }
        .qd-option-selected .qd-option-key {
            background: #00F2FE !important;
            color: #020617 !important;
        }
        .qd-option-selected .qd-option-text {
            color: #E0F7FA !important;
            font-weight: 700 !important;
        }

        .qd-option-key {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 800;
            color: #94A3B8 !important;
            flex-shrink: 0;
            letter-spacing: 0;
            transition: all 0.15s ease;
        }
        .qd-option-text {
            font-size: 15px;
            font-weight: 500;
            color: #CBD5E1 !important;
            line-height: 1.4;
            transition: color 0.15s ease, font-weight 0.15s ease;
        }

        /* Streamlit buttons beneath option cards — invisible overlay */
        .qd-quiz-section .stButton > button {
            opacity: 0 !important;
            height: 58px !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            width: 100% !important;
            margin-top: -62px !important;
            margin-bottom: 1px !important;
            font-size: 0 !important;
        }

        /* Nav buttons (Câu trước / Câu tiếp) — visible */
        .qd-quiz-section [data-testid="stButton"]:has(button[data-testid="stBaseButton-secondary"]):not(:has(button[style])) {
            /* keep visible — only overlay option buttons */
        }

        /* =====================================================
           SUBMIT PREVIEW SCREEN
        ===================================================== */
        .qd-submit-preview {
            text-align: center;
            padding: 30px 20px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
            margin-bottom: 16px;
        }
        .qd-submit-icon {
            font-size: 44px;
            margin-bottom: 10px;
        }
        .qd-submit-title {
            font-size: 20px;
            font-weight: 800;
            color: #F1F5F9 !important;
            margin-bottom: 6px;
        }
        .qd-submit-sub {
            font-size: 14px;
            color: #64748B !important;
        }
        .qd-submit-sub strong {
            color: #00F2FE !important;
        }

        /* =====================================================
           RESULT CARD
        ===================================================== */
        .qd-result-card {
            background: linear-gradient(135deg, rgba(0,242,254,0.06) 0%, rgba(10,20,40,0.95) 100%);
            border: 1px solid rgba(0,242,254,0.22);
            border-radius: 20px;
            padding: 28px 20px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 0 30px rgba(0,242,254,0.08);
        }
        .qd-result-icon {
            font-size: 52px;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 12px rgba(0,242,254,0.4));
        }
        .qd-result-score {
            font-size: 56px;
            font-weight: 900;
            color: #00F2FE !important;
            letter-spacing: -2px;
            line-height: 1;
            margin-bottom: 6px;
        }
        .qd-result-label {
            font-size: 18px;
            font-weight: 700;
            color: #F1F5F9 !important;
            margin-bottom: 6px;
        }
        .qd-result-detail {
            font-size: 14px;
            color: #64748B !important;
        }

        /* =====================================================
           ANSWER REVIEW CARDS
        ===================================================== */
        .qd-answer-card {
            background: rgba(255,255,255,0.025);
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            border-left: 4px solid transparent;
        }
        .qd-answer-correct {
            border-left-color: #22C55E !important;
            background: rgba(34,197,94,0.05) !important;
        }
        .qd-answer-wrong {
            border-left-color: #EF4444 !important;
            background: rgba(239,68,68,0.05) !important;
        }
        .qd-answer-q {
            font-size: 14px;
            font-weight: 700;
            color: #F1F5F9 !important;
            margin-bottom: 6px;
            line-height: 1.4;
        }
        .qd-answer-detail {
            font-size: 13px;
            color: #94A3B8 !important;
            margin-bottom: 6px;
        }
        .qd-answer-detail strong {
            color: #F1F5F9 !important;
        }
        .qd-answer-explain {
            font-size: 13px;
            color: #64748B !important;
            line-height: 1.5;
            padding: 8px 12px;
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
        }

        /* =====================================================
           EMPTY STATES
        ===================================================== */
        .qd-empty-quiz {
            text-align: center;
            padding: 40px 20px;
            color: #475569 !important;
            font-size: 14px;
            font-weight: 500;
        }

        /* =====================================================
           QUIZ SECTION — Nav buttons style override
           (Visible buttons cho navigation giữa câu hỏi)
        ===================================================== */
        .qd-quiz-section .stButton:last-of-type > button,
        .qd-quiz-section .stButton:nth-last-of-type(2) > button {
            /* Reset về visible cho nav buttons cuối section */
            opacity: 1 !important;
            margin-top: 0 !important;
            height: auto !important;
            min-height: 40px !important;
            font-size: 13px !important;
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            margin-bottom: 0px !important;
            padding: 8px 14px !important;
        }

        /* Submit button — primary */
        .qd-quiz-section button[kind="primary"] {
            opacity: 1 !important;
            margin-top: 0 !important;
            height: auto !important;
            min-height: 46px !important;
            background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
            color: #020617 !important;
            font-weight: 800 !important;
            font-size: 15px !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: 0 0 20px rgba(0,242,254,0.3) !important;
            margin-bottom: 40px !important;
            margin-top: -40px !important;
        }
        .qd-quiz-section button[kind="primary"]:hover {
            box-shadow: 0 0 30px rgba(0,242,254,0.5) !important;
        }

        /* Retry button */
        .qd-quiz-section .stButton:last-child > button {
            opacity: 1 !important;
            margin-top: 0 !important;
            height: auto !important;
            min-height: 44px !important;
            font-size: 14px !important;
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: #94A3B8 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            margin-bottom: 40px !important;
            margin-top: -40px !important;
        }

        /* =====================================================
           RESPONSIVE — Mobile
        ===================================================== */
        @media (max-width: 600px) {
            .qd-question-text { font-size: 15px !important; }
            .qd-option-text { font-size: 14px !important; }
            .qd-result-score { font-size: 44px !important; }
            .qd-sentence-text { font-size: 13.5px !important; }
            .qd-option-card { padding: 12px 14px !important; min-height: 50px !important; }
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Quiz Detail CSS (qd-) injected successfully.")


# =====================================================
# PATCH v20260606: Quiz Detail View UI Fixes
# CHỈ THÊM MỚI — không sửa code cũ để tránh ảnh hưởng UI Login/các màn khác
# Fixes:
#   1. Ẩn hoàn toàn back button text Streamlit dưới back row HTML (chống overlap)
#   2. Rút gọn chiều cao player (height 195px → compact)
#   3. Chuyển quiz options sang dạng radio button thuần — bỏ duplicate text
#   4. Ẩn inline option card HTML, chỉ hiện Streamlit radio-style buttons
# =====================================================

def inject_quiz_detail_patch_css():
    """
    CSS patch bổ sung cho quiz_detail_view — áp dụng SAU inject_quiz_detail_css().
    Chỉ thêm mới, không sửa bất kỳ selector cũ nào.
    v20260606-r2: radio row overlay + compact player fix
    """
    logger.debug("🎨 Injecting Quiz Detail PATCH CSS (v20260606-r2).")
    st.markdown("""
    <style>
        /* =====================================================
           FIX 1: ẨN DUPLICATE BACK BUTTON
        ===================================================== */
        .qd-back-row ~ div[data-testid="stButton"] > button,
        .qd-back-row + div > div[data-testid="stButton"] > button {
            opacity: 0 !important;
            pointer-events: auto !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 160px !important;
            height: 32px !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            font-size: 0 !important;
            cursor: pointer !important;
            z-index: 10 !important;
        }

        /* =====================================================
           FIX 2: COMPACT PLAYER IFRAME HEIGHT
        ===================================================== */
        .qd-player-section iframe,
        .qd-player-section [data-testid="stCustomComponentV1"] iframe {
            max-height: 190px !important;
        }

        /* =====================================================
           FIX 3: RADIO ROW — invisible Streamlit button overlay
           Mỗi option: HTML radio row (hiện) + st.button ẩn overlay lên trên để nhận click
           Button cao 42px (= chiều cao radio row) và margin-top âm để kéo lên đúng vị trí
        ===================================================== */
        .qd-quiz-section .stButton > button {
            opacity: 0 !important;
            pointer-events: auto !important;
            height: 42px !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin-top: -44px !important;
            margin-bottom: 0px !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            font-size: 0 !important;
            cursor: pointer !important;
            width: 100% !important;
            display: block !important;
            border-radius: 8px !important;
        }

        /* =====================================================
           FIX 4: NAV BUTTONS (← Câu trước / Câu tiếp →) — visible
        ===================================================== */
        .qd-quiz-nav .stButton > button {
            opacity: 1 !important;
            margin-top: 8px !important;
            height: auto !important;
            min-height: 40px !important;
            font-size: 13px !important;
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: #94A3B8 !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            margin-bottom: 4px !important;
            padding: 8px 14px !important;
            pointer-events: auto !important;
            cursor: pointer !important;
        }
        .qd-quiz-nav .stButton > button:hover {
            background: rgba(0,242,254,0.06) !important;
            border-color: rgba(0,242,254,0.25) !important;
            color: #00F2FE !important;
        }

        /* =====================================================
           FIX 5: SUBMIT + RETRY buttons — visible, cũ: min-height: 40px, font-size: 15px
        ===================================================== */
        .qd-quiz-section button[kind="primary"] {
            opacity: 1 !important;
            margin-top: 0 !important;
            height: auto !important;
            min-height: 40px !important;
            background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
            color: #020617 !important;
            font-weight: 800 !important;
            font-size: 13px !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: 0 0 20px rgba(0,242,254,0.3) !important;
            pointer-events: auto !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Quiz Detail PATCH CSS (v20260606-r2) injected.")

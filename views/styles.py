import streamlit as st
import logging

logger = logging.getLogger("views.styles")

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
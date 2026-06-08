import streamlit as st
import logging

logger = logging.getLogger("views.sidebar_css")

# =====================================================
# SIDEBAR CSS — Tách độc lập từ styles.py
# Toàn bộ CSS phong cách Gen Z Dark UI cho Sidebar
# Bao gồm: v3 Layout Fix + v4 Enhancement + Dashboard Bug Fix
# QUY TẮC: KHÔNG THAY ĐỔI LOGIC — CHỈ BÓC TÁCH VỊ TRÍ
# =====================================================

def inject_sidebar_css():
    """
    Inject CSS riêng biệt cho Sidebar Gen Z Dark UI — v3 Layout Fix.
    - Profile section cố định ở đầu
    - Nav menu ngay sau profile với gap hợp lý
    - Settings + Logout fixed cứng ở đáy sidebar (position: fixed)
    - Không chỉnh sửa inject_global_css() cũ

    Bao gồm luôn:
    - v4 Enhancement: avatar lớn hơn, Pro badge, active nav rõ hơn
    - Dashboard Bug Fix: sb-bottom-section sticky thay fixed
      (tránh che sidebar toggle button của Streamlit)
    """
    logger.debug("🎨 Injecting Sidebar Gen Z CSS (sidebar_css.py) — v3+v4+bugfix.")
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
            height: 54px !important; /* Ép nút thật có chiều cao bằng đúng item HTML */
            min-height: 54px !important;
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
        
        /* Vị trí cần sửa 1: Tìm khối selector [data-testid="stSidebar"] .stButton (khoảng dòng 55-61 trong file gốc).
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
            width: 50px;
            height: 50px;
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
            width: 45px !important;
            height: 45px !important;
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
            margin-top: -54px !important;
            height: 54px !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            height: 54px !important;
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

        /* =====================================================
           BUG FIX: sb-bottom-section position:sticky
           Lý do: position:fixed + left:0 + z-index:100 che
           toggle button sidebar của Streamlit → sidebar không
           mở lại được. Fix: sticky + left:auto + z-index thấp.
           (Tích hợp từ inject_dashboard_css bug fix)
        ===================================================== */
        .sb-bottom-section {
            position: sticky !important;
            bottom: 0 !important;
            left: auto !important;
            width: auto !important;
            z-index: 10 !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Sidebar CSS (sidebar_css.py) injected successfully.")


# =====================================================
# SIDEBAR TOGGLE FIX — Tách từ styles.py
# Mục đích: Fix nút mở/đóng sidebar luôn hiển thị và bấm được
# Nguyên nhân bug: inject_global_css() đặt overflow:hidden trên
#   html/body + header {visibility:hidden} ẩn toàn bộ thanh header
#   chứa nút toggle → sidebar đóng xong không mở lại được.
# GỌI HÀM NÀY SAU TẤT CẢ inject_*_css() khác trong app.py.
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

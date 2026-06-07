import streamlit as st
import logging
import jwt

# =====================================================
# TẦNG GIAO DIỆN (VIEW): views/sidebar_view.py
# Import CSS từ tầng Style độc lập — views/sidebar_css.py
# Quy tắc: KHÔNG thay đổi bất kỳ logic hay content nào so với bản gốc.
# =====================================================
from views.sidebar_css import inject_sidebar_css, inject_sidebar_toggle_fix

logger = logging.getLogger("views.sidebar_view")

# =====================================================
# ICON SVGs cho từng mục menu (Inline SVG)
# =====================================================
ICON_DASHBOARD = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
  <rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
  <rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
  <rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/>
</svg>"""

ICON_DISCOVER = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="6" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
  <circle cx="8" cy="13" r="2" stroke="currentColor" stroke-width="2"/>
  <path d="M13 10h5M13 13h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>"""

ICON_QUIZ = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 18v-2a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <circle cx="12" cy="8" r="3" stroke="currentColor" stroke-width="2"/>
  <path d="M8 18h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>"""

ICON_SETTINGS = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2"/>
</svg>"""

ICON_LOGOUT = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>"""

ICON_CHEVRON = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


def _get_user_profile_from_session() -> dict:
    """Trích xuất thông tin profile user từ session để hiển thị trên Sidebar."""
    auth_data = st.session_state.get("auth", {})
    token_data = auth_data.get("token", {}) if isinstance(auth_data, dict) else {}
    id_token = None

    if isinstance(token_data, dict):
        id_token = token_data.get("id_token")
    if not id_token and isinstance(auth_data, dict):
        id_token = auth_data.get("id_token")

    if not id_token:
        logger.warning("⚠️ sidebar_view: Không tìm thấy id_token trong session.")
        return {}

    try:
        profile = jwt.decode(id_token, options={"verify_signature": False})
        logger.debug(f"✅ sidebar_view: Decoded profile for {profile.get('email')}")
        return profile
    except Exception as e:
        logger.error(f"🚨 sidebar_view: Lỗi decode id_token: {e}")
        return {}


def render_sidebar_navigation(supabase_client=None):
    """
    Quản lý trạng thái chuyển trang (st.session_state.current_page)
    và render toàn bộ Sidebar theo chuẩn UI Gen Z Dark Mode.
    Logic điều hướng giữ nguyên hoàn toàn.
    """
    logger.debug("🎯 Rendering sidebar navigation layout (v2 - Gen Z UI).")

    # --- Khởi tạo state mặc định ---
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
        logger.debug("📌 sidebar_view: Khởi tạo current_page = Dashboard")

    # --- Lấy profile từ session ---
    profile = _get_user_profile_from_session()
    user_name = profile.get("name", "Học viên")
    user_avatar = profile.get("picture", "")
    user_email = profile.get("email", "")

    # --- Lấy streak count ---
    streak_count = 0
    if supabase_client and profile.get("sub"):
        try:
            streak_res = supabase_client.table("user_streaks").select("current_streak").eq(
                "user_id", profile.get("sub")
            ).execute()
            if streak_res.data:
                streak_count = streak_res.data[0].get("current_streak", 0)
                logger.debug(f"🔥 sidebar_view: streak={streak_count} cho user {profile.get('sub')}")
        except Exception as e:
            logger.error(f"🚨 sidebar_view: Lỗi fetch streak: {e}")

    # =========================================================
    # RENDER SIDEBAR HTML (Toàn bộ UI được inject qua markdown)
    # =========================================================

    # --- PROFILE SECTION ---
    avatar_html = (
        f'<img src="{user_avatar}" class="sb-avatar-img" alt="avatar"/>'
        if user_avatar
        else '<div class="sb-avatar-placeholder">👤</div>'
    )

    # Mockup: Pro badge (cyan) ở trên, streak badge ở dưới (nếu có)
    streak_display = f'<div class="sb-streak-badge">🔥 {streak_count} ngày</div>' if streak_count > 0 else ""

    st.sidebar.markdown(f"""
    <div class="sb-profile-section">
        <div class="sb-avatar-ring">
            {avatar_html}
        </div>
        <div class="sb-profile-info">
            <div class="sb-user-name">{user_name}</div>
            <div class="sb-pro-badge">👑 Pro</div>
            {streak_display}
        </div>
    </div>
    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    logger.debug(f"🖼️ sidebar_view: Đã render profile section — user={user_name}, streak={streak_count}, pro_badge=True.")

    # --- MENU NAVIGATION ---
    # Xác định trang đang active
    current = st.session_state.get("current_page", "Dashboard")

    # Render từng mục menu dưới dạng HTML thuần (ảo), dùng st.sidebar.button để nhận click
    st.sidebar.markdown('<div class="sb-nav-section">', unsafe_allow_html=True)

    # --- DASHBOARD ---
    is_active_dash = current == "Dashboard"
    st.sidebar.markdown(f"""
    <div class="sb-nav-item {'sb-nav-active' if is_active_dash else ''}">
        <span class="sb-nav-icon {'sb-nav-icon-active' if is_active_dash else ''}">{ICON_DASHBOARD}</span>
        <span class="sb-nav-label {'sb-nav-label-active' if is_active_dash else ''}">Dashboard</span>
        <span class="sb-nav-chevron">{ICON_CHEVRON}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Dashboard", key="nav_dashboard", use_container_width=True):
        logger.info("📌 sidebar_view: Chuyển trang → Dashboard")
        st.session_state.current_page = "Dashboard"
        st.rerun()

    # --- DISCOVER (Danh sách bài học) ---
    is_active_disc = current == "Học tập"
    st.sidebar.markdown(f"""
    <div class="sb-nav-item {'sb-nav-active' if is_active_disc else ''}">
        <span class="sb-nav-icon {'sb-nav-icon-active' if is_active_disc else ''}">{ICON_DISCOVER}</span>
        <span class="sb-nav-label {'sb-nav-label-active' if is_active_disc else ''}">Discover</span>
        <span class="sb-nav-chevron">{ICON_CHEVRON}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Discover", key="nav_discover", use_container_width=True):
        logger.info("📌 sidebar_view: Chuyển trang → Học tập")
        st.session_state.current_page = "Học tập"
        st.rerun()

    # --- QUIZ ROOM ---
    is_active_quiz = current == "Quiz"
    st.sidebar.markdown(f"""
    <div class="sb-nav-item {'sb-nav-active' if is_active_quiz else ''}">
        <span class="sb-nav-icon {'sb-nav-icon-active' if is_active_quiz else ''}">{ICON_QUIZ}</span>
        <span class="sb-nav-label {'sb-nav-label-active' if is_active_quiz else ''}">Quiz Room</span>
        <span class="sb-nav-chevron">{ICON_CHEVRON}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Quiz Room", key="nav_quiz", use_container_width=True):
        logger.info("📌 sidebar_view: Chuyển trang → Quiz")
        st.session_state.current_page = "Quiz"
        st.rerun()

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # --- PADDING ĐỆM — tránh nội dung nav bị che bởi bottom fixed section ---
    st.sidebar.markdown('<div class="sb-nav-bottom-padding"></div>', unsafe_allow_html=True)

    # --- BOTTOM ACTIONS (Settings + Logout) ---
    st.sidebar.markdown('<div class="sb-bottom-section">', unsafe_allow_html=True)

    st.sidebar.markdown(f"""
    <div class="sb-bottom-btn sb-settings-btn">
        <span class="sb-nav-icon">{ICON_SETTINGS}</span>
        <span>Settings</span>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("⚙️ Settings", key="nav_settings", use_container_width=True):
        logger.info("📌 sidebar_view: Settings clicked (placeholder)")
        # Placeholder — chưa có trang Settings trong MVP
        pass

    st.sidebar.markdown(f"""
    <div class="sb-bottom-btn sb-logout-btn">
        <span class="sb-nav-icon">{ICON_LOGOUT}</span>
        <span>Log out</span>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("→ Log out", key="nav_logout", use_container_width=True):
        logger.info("🚪 sidebar_view: User đăng xuất — xóa session.")
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # --- LOG SYSTEM STATUS (ngầm, không hiển thị ra UI) ---
    if supabase_client:
        logger.debug("✅ sidebar_view: Supabase connected.")
    else:
        logger.warning("⚠️ sidebar_view: Supabase client = None.")

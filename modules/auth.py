import streamlit as st
from streamlit_oauth import OAuth2Component
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from modules.database import upsert_user_profile

# Khởi tạo OAuth2
oauth2 = OAuth2Component(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, "", "", "", "")

def render_login_screen():
    st.markdown("""
    <div class="login-container">
        <div class="login-logo">⚡ Edu-Stay AI</div>
        <div class="login-tagline">Hệ thống luyện nghe Tiếng Anh · Powered by Groq & Whisper</div>
    </div>
    """, unsafe_allow_html=True)

    # Căn giữa nút login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        redirect_uri = "https://eng-learning.streamlit.app/"
        result = oauth2.authorize_button(
            name="🔑 Đăng nhập bằng Gmail",
            redirect_uri=redirect_uri,
            scope="openid email profile",
            key="google_auth",
        )

    if result and "token" in result:
        user_info = result.get("user_info")
        if user_info:
            st.session_state["auth"] = result
            st.session_state["user_info"] = user_info
            upsert_user_profile(user_info)
            st.rerun()

def render_sidebar_profile():
    if "user_info" in st.session_state:
        user = st.session_state["user_info"]

        # Avatar
        pic = user.get("picture")
        if pic:
            st.sidebar.image(pic, width=64)

        # Name & email
        st.sidebar.markdown(
            f'<div class="sidebar-name">{user.get("name", "")}</div>'
            f'<div class="sidebar-email">{user.get("email", "")}</div>',
            unsafe_allow_html=True
        )
        st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Học viên label
        st.sidebar.markdown(
            '<span style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.08em;">Học viên</span>',
            unsafe_allow_html=True
        )

        if st.sidebar.button("🚪 Đăng xuất"):
            del st.session_state["auth"]
            del st.session_state["user_info"]
            st.rerun()

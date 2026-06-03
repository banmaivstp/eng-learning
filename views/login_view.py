import streamlit as st
from config import oauth2

def render_login_form():
    # 1. Navbar
    st.markdown("""
        <div class="navbar">
            <div class="login-brand">🤖 Edu-Stay <span>AI</span></div>
            <div class="navbar-links">
                <span>Features</span><span>How it works</span><span>Pricing</span>
                <div class="signin-btn">Sign in</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # 2. Card header (phần trên nút)
    st.markdown("""
        <div class="login-card-top">
            <div class="robot-avatar-circle">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M12 2a2 2 0 0 1 2 2v1h3a3 3 0 0 1 3 3v4a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2v4a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-4a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2V8a3 3 0 0 1 3-3h3V4a2 2 0 0 1 2-2zm6 6H6v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V8zm-9 3a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zm6 0a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zm-6 4h6v1.5H9V15z"/>
                </svg>
            </div>
            <div class="hero-title">Edu-Stay <span class="hero-accent">AI</span></div>
            <div class="hero-line"></div>
            <div class="hero-sub-title-top">AI-Powered English Learning</div>
            <div class="hero-sub-title-main">Learn smarter. Listen better. Speak confidently.</div>
            <div class="hero-secure-text">🔒 Secure • ⚡ Fast • No password needed</div>
        </div>""", unsafe_allow_html=True)

    # 3. Nút Google — dùng columns để căn giữa tự nhiên theo Streamlit
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        result = oauth2.authorize_button(
            name="Continue with Google",
            redirect_uri=st.secrets["REDIRECT_URI"],
            scope="openid email profile",
            key="google_auth",
            pkce="S256",
            extras_params={"prompt": "select_account", "access_type": "offline"},
            use_container_width=True,
        )

    # 4. Card footer (phần dưới nút — đóng card về mặt visual)
    st.markdown("""<div class="login-card-bottom"></div>""", unsafe_allow_html=True)

    # 👇 KHOẢNG TRỐNG GIỮA CARD VÀ FEATURES - TĂNG GẤP ĐÔI (70px)
    st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)

    # 5. Features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon-circle"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
                <div class="feature-text-group">
                    <div class="feature-heading">One-Tap Access</div>
                    <div class="feature-caption">Login in seconds</div>
                </div>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon-circle"><svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
                <div class="feature-text-group">
                    <div class="feature-heading">100% Secure</div>
                    <div class="feature-caption">Google OAuth 2.0</div>
                </div>
            </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon-circle"><svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg></div>
                <div class="feature-text-group">
                    <div class="feature-heading">Track Progress</div>
                    <div class="feature-caption">Smart learning with AI</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # 6. Footer
    st.markdown("""
        <div class="footer-center-container">
            <div class="footer-center-links">
                <span>Privacy Policy</span><span>Terms of Service</span>
            </div>
            <div>© 2026 Edu-Stay AI • All rights reserved</div>
        </div>""", unsafe_allow_html=True)

    return result
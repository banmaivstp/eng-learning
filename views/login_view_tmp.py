import streamlit as st
from config import oauth2
# Import trực tiếp từ file CSS vừa tách thay vì dùng styles.py
from login_css import inject_login_css

def render_login_form():
    # Nhúng CSS chuyên biệt dành riêng cho Login View
    inject_login_css()

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
                    <path d="M12 2a2 2 0 0 1 2 2v1h3a3 3 0 0 1 3 3v4a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2v4a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-4a2 2 0 0 1-2-2v-2a2 2 0 0 1 2-2V8a3 3 0 0 1 3-3h3V4a2 2 0 0 1 2-2zm6 6H6v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V8zm-9 3a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zm6 0a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z"/>
                </svg>
            </div>
            <div class="hero-sub-title-top">Welcome to Edu-Stay</div>
            <div class="hero-title">Smarter Learning<br>With <span class="hero-accent">AI Inside</span>.</div>
            <div class="hero-line"></div>
            <div class="hero-sub-title-main">Hệ thống gợi ý lộ trình học tiếng Anh thông minh cá nhân hóa tối đa.</div>
            <div class="hero-secure-text">🔒 Đăng nhập an toàn & bảo mật</div>
        </div>""", unsafe_allow_html=True)

    # 3. Khu vực render nút Login bằng Google OAuth
    # (Để trống phần code setup oauth của bạn tại đây)
    
    # 4. Card bottom (phần dưới nút) và Features
    st.markdown("""
        <div class="login-card-bottom"></div>
    """, unsafe_allow_html=True)
    
    st.write("") # Tạo khoảng cách nhẹ
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="feature-box">
                <div class="feature-icon-circle"><svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-14h-9l1-8z"/></svg></div>
                <div class="feature-text-group">
                    <div class="feature-heading">⚡ Siêu Tốc</div>
                    <div class="feature-caption">Phản hồi dưới 2 giây</div>
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

    # 5. Footer
    st.markdown("""
        <div class="footer-center-container">
            <div class="footer-center-links">
                <span>Điều khoản</span><span>Bảo mật</span><span>Hỗ trợ</span>
            </div>
            <div>© 2026 Edu-Stay AI. Built for the future of learning.</div>
        </div>
    """, unsafe_allow_html=True)
import streamlit as st

def inject_login_css():
    """
    Nhúng toàn bộ CSS chuyên biệt cho giao diện Đăng nhập (Login View).
    Giúp login_view.py chạy độc lập không cần styles.py.
    """
    st.markdown("""
    <style>
        /* =====================================================
           GLOBAL DESIGN & CYBER BACKGROUND
        ===================================================== */
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

        /* CYBER GRID EFFECT */
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
           LOGIN CARD (TOP & BOTTOM OVERLAYS)
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

        /* OAUTH BUTTON CONTAINER (HACKING STREAMLIT LAYOUT) */
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
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe) > [data-testid="stColumn"]:first-child,
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe) > [data-testid="stColumn"]:last-child {
            display: none !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlock"] iframe) > [data-testid="stColumn"]:nth-child(2) {
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
           FEATURES LIST
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
        .feature-text-group { display: flex; flex-direction: column; }
        .feature-heading { font-size: 13px; font-weight: 700; color: #F1F5F9 !important; line-height: 1.2; }
        .feature-caption { color: #94A3B8 !important; font-size: 11.5px; margin-top: 2px; line-height: 1.2; }

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
        .footer-center-links { display: flex; gap: 16px; font-weight: 600; }
        .footer-center-links span { cursor: pointer; color: #94A3B8 !important; }
        .footer-center-links span:hover { color: #00F2FE !important; }
    </style>
    """, unsafe_allow_html=True)
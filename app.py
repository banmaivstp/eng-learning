# ==========================================
# FILE: app.py
# ==========================================
import streamlit as st
import time
import pandas as pd
import logging
from config import client, supabase
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.database import (
    save_learning_history, 
    get_cached_episode_data,
    get_user_analytics,
    evaluate_user_badges
)
# Import Design System từ Tầng View
from views.styles import (
    inject_global_css, 
    inject_dashboard_css, 
    inject_sidebar_toggle_fix, 
    inject_podcast_list_css, 
    inject_show_list_css, 
    inject_podcast_list_view_css, 
    inject_quiz_detail_css, 
    inject_quiz_detail_patch_css
)
from views.dashboard_view import render_dashboard_screen
from views.show_list_view import render_podcast_discover_page
from views.podcast_list_view import render_podcast_list_page
from views.quiz_detail_view import render_quiz_detail_page

# Khởi tạo Logger định danh cho luồng điều phối chính app
logger = logging.getLogger("app_main")

# Cấu hình thiết lập nền tảng ứng dụng
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="wide")

# Nhúng toàn bộ tài nguyên CSS toàn cục của hệ thống
inject_global_css()
inject_dashboard_css()
inject_sidebar_toggle_fix()
inject_podcast_list_css()
inject_show_list_css()
inject_podcast_list_view_css()
inject_quiz_detail_css()
inject_quiz_detail_patch_css()

# Kiểm tra trạng thái Session người dùng
if "auth" not in st.session_state:
    logger.debug("❌ app_main: User session unauthenticated. Redirecting to login portal.")
    
    from views.login_view import render_login_form
    from modules.auth import process_user_login_data
    
    oauth_result = render_login_form()
    
    if oauth_result:
        auth_data = process_user_login_data(oauth_result)
        if auth_data:
            st.session_state["auth"] = auth_data
            st.toast("🎉 Đăng nhập thành công!", icon="🚀")
            time.sleep(0.5)
            st.rerun()
else:
    logger.debug("✅ app_main: User authenticated. Handling workspace components.")
    
    from modules.auth import get_logged_in_user_id
    from views.sidebar_view import render_sidebar_navigation
    
    # Render sidebar theo đúng cấu trúc cũ
    sidebar_action = render_sidebar_navigation(supabase=supabase)
    
    if sidebar_action == "LOGOUT":
        st.session_state.clear()
        logger.info("🚪 Người dùng đã đăng xuất thành công. Xóa session.")
        st.rerun()

    # Trích xuất định danh qua logic architecture mới
    user_id = get_logged_in_user_id(st.session_state["auth"])

    # Kiểm tra liên kết dữ liệu hệ thống phụ trợ (Giữ nguyên phần sidebar debug gốc của bạn)
    st.sidebar.write("---")
    st.sidebar.markdown("⚙️ **Kết nối hệ thống:**")
    if supabase:
        try:
            st.sidebar.success("Supabase Kết Nối Tốt")
        except:
            st.sidebar.error("Supabase Lỗi Kết Nối")
    else:
        st.sidebar.error("Supabase Chưa Cấu Hình")

    # =========================================================================
    # LỚP ĐIỀU PHỐI TRANG CHỨC NĂNG (ROUTER THEO FILE GỐC CHẠY TỐT)
    # =========================================================================
    current_page = st.session_state.get("page", "dashboard")
    logger.debug(f"🔀 app_main: Directing request into workspace page view: -> [{current_page}]")

    if current_page == "dashboard":
        analytics_data = {
            "streak_days": 0,
            "total_episodes": 0,
            "total_hours": 0.0,
            "avg_score": 0.0,
            "weekly_progress": [0.0] * 7,
            "recent_history": []
        }
        if user_id:
            try:
                analytics_data = get_user_analytics(str(user_id))
            except Exception as db_err:
                logger.error(f"🚨 Không thể tải dữ liệu phân tích từ Supabase: {str(db_err)}")
        
        render_dashboard_screen(user_analytics_data=analytics_data)

    elif current_page == "discover":
        logger.info("📻 app_main: Rendering Podcast Library (Discover page).")
        render_podcast_discover_page(supabase_client=supabase)

    elif current_page == "show_detail":
        logger.info("📋 app_main: Rendering Episode List.")
        render_podcast_list_page(supabase_client=supabase)

    elif current_page == "detail":
        logger.info("🎬 app_main: Rendering Quiz Detail.")
        render_quiz_detail_page(supabase_client=supabase, user_id=str(user_id) if user_id else None)
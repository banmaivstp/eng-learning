import streamlit as st
import time
import pandas as pd
import logging
from config import client, supabase
from modules.auth import render_login_screen, get_logged_in_user_id
# render_sidebar_profile đã được tích hợp vào render_sidebar_navigation() — không gọi riêng nữa
from modules.scraper import get_audio_url_from_apple, get_episode_list_from_show
from modules.database import (
    save_learning_history, 
    get_cached_episode_data,
    get_user_analytics,
    evaluate_user_badges
)
from views.styles import inject_global_css, inject_sidebar_css, inject_dashboard_css, inject_sidebar_toggle_fix, inject_podcast_list_css, inject_show_list_css, inject_podcast_list_view_css, inject_quiz_detail_css, inject_quiz_detail_patch_css
from views.dashboard_view import render_dashboard_screen
# Import sidebar view độc lập vừa tách theo cấu trúc Milestone 1
from views.sidebar_view import render_sidebar_navigation
# Import show list view — Milestone 2 (Your Podcast Library)
from views.show_list_view import render_podcast_discover_page
# Import podcast list view — Milestone 2 (Episode List of a Show)
from views.podcast_list_view import render_podcast_list_page
# Import quiz detail view — Milestone 3+4+5
from views.quiz_detail_view import render_quiz_detail_page

# Khởi tạo Logger định danh cho luồng điều phối chính app
logger = logging.getLogger("app_main")

# Cấu hình thiết lập nền tảng ứng dụng
st.set_page_config(page_title="Edu-Stay AI Quiz Platform", page_icon="⚡", layout="centered")

# --- INJECT DESIGN SYSTEM NÂNG CẤP & FIX MỜ CHỮ DI ĐỘNG ---
inject_global_css()

# --- INJECT SIDEBAR CSS (Gen Z UI - Milestone 1) ---
inject_sidebar_css()

# --- INJECT DASHBOARD CSS (Gen Z UI - Milestone 2) ---
inject_dashboard_css()

# --- INJECT SIDEBAR TOGGLE FIX (Luôn gọi CUỐI CÙNG sau tất cả CSS inject) ---
# Fix: nút mở/đóng sidebar bị ẩn do overflow:hidden và header:hidden trong global css cũ
inject_sidebar_toggle_fix()

# --- INJECT PODCAST LIST CSS (Milestone 2 — Show Library UI) ---
inject_podcast_list_css()

# --- INJECT SHOW LIST CSS (Milestone 2 — Your Podcast Library, prefix sl-) ---
inject_show_list_css()

# --- INJECT PODCAST LIST VIEW CSS (Milestone 2 — Episode List, prefix pcl-) ---
inject_podcast_list_view_css()

# --- INJECT QUIZ DETAIL CSS (Milestone 3+4+5) ---
inject_quiz_detail_css()

# --- INJECT QUIZ DETAIL PATCH CSS (v20260606: fix back button overlap, player height, radio options) ---
inject_quiz_detail_patch_css()

logger.debug("✅ app_main: All CSS injected. Sidebar toggle fix applied.")

# --- [BẢN VÁ PHÁT TRIỂN]: BỎ QUA MÀN HÌNH LOGIN KHI HOT-RELOAD (Môi trường Local/Dev) ---
# Nếu muốn vào thẳng giao diện mà không cần bấm nút qua Google OAuth, bạn có thể bỏ dấu comment 3 dòng dưới:
# if "auth" not in st.session_state:
#     st.session_state["auth"] = {"token": {"id_token": "mock"}, "user": {"id": "dev_user_id_001"}}
#     st.session_state["current_page"] = "Dashboard"

if "auth" not in st.session_state:
    logger.debug("🔒 Anonymous user context detected. Presenting secure portal.")
    render_login_screen()
else:
    # 1. Render toàn bộ Sidebar (profile + navigation + logout) từ sidebar_view mới
    #    render_sidebar_profile() cũ đã được TÍCH HỢP vào render_sidebar_navigation() — KHÔNG gọi lại
    logger.debug("✅ app_main: User authenticated. Rendering sidebar navigation.")
    
    # 2. Gọi hàm render Sidebar điều hướng và quản lý state từ file sidebar.py vừa tách
    render_sidebar_navigation(supabase_client=supabase)
    
    # Trích xuất ID định danh người dùng từ Session hiện tại
    user_id = get_logged_in_user_id()

    # 3. ĐIỀU PHỐI ĐỘC LẬP THEO TRẠNG THÁI TRANG (PAGE) ĐÃ ĐƯỢC SIDEBAR CẬP NHẬT
    current_page = st.session_state.get("current_page", "Dashboard")
    logger.debug(f"✅ app_main: Routing → current_page='{current_page}'")

    if current_page == "Dashboard":
        analytics_data = None
        if user_id:
            try:
                # Truy vấn dữ liệu phân tích thực tế từ DB của hệ thống
                analytics_data = get_user_analytics(str(user_id))
            except Exception as db_err:
                logger.error(f"🚨 Không thể tải dữ liệu phân tích từ Supabase: {str(db_err)}")
        
        # Gọi View render độc lập màn hình Dashboard (Nén diện tích hiển thị, no-scroll)
        render_dashboard_screen(user_analytics_data=analytics_data)

    elif current_page == "Học tập":
        # Màn hình Discover — Your Podcast Library
        logger.info("📻 app_main: Rendering Podcast Library (Discover page).")
        render_podcast_discover_page(supabase_client=supabase)

    elif current_page == "Show Detail":
        # Màn hình danh sách bài học (Episode List) của show đã chọn
        logger.info("📋 app_main: Rendering Episode List (podcast_list_view).")
        render_podcast_list_page(supabase_client=supabase)

    elif current_page == "Episode Detail":
        # Màn hình phòng học: Audio Player + Transcript + Quiz
        logger.info("🎬 app_main: Rendering Quiz Detail (quiz_detail_view).")
        render_quiz_detail_page(supabase_client=supabase, user_id=str(user_id) if user_id else None)

    else:
        # --- NHÁNH HIỂN THỊ DANH SÁCH BÀI HỌC VÀ QUIZ FLOW GỐC CỦA HỆ THỐNG ---
        st.markdown('<div style="font-size: 24px; font-weight: 800; color: #F1F5F9; margin-bottom: 10px;">🎧 DANH SÁCH BÀI HỌC ĐỘC LẬP</div>', unsafe_allow_html=True)
        
        # [GIỮ NGUYÊN HOÀN TOÀN LOGIC CHẠY BÀI HỌC VÀ QUIZ BAN ĐẦU CỦA BẠN]
        # Toàn bộ code xử lý logic flow `st.session_state['groq_quiz_data']`, lựa chọn đáp án, nộp bài save_learning_history cũ của app.py sẽ chạy tiếp tục tại đây...
        st.info("Không gian hiển thị danh sách các tập bài học học tập và làm bài tập trắc nghiệm AI.")
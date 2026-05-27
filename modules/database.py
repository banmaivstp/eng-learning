import streamlit as st
from config import supabase

def upsert_user_profile(user_data: dict):
    """Ghi nhận dữ liệu người dùng từ Google token vào Supabase"""
    if supabase:
        try:
            supabase.table("users_profile").upsert(user_data).execute()
        except Exception as db_err:
            st.warning(f"Lưu lịch sử đăng nhập lỗi nhẹ: {db_err}")

# --- KHOẢNG TRỐNG ĐỂ VIẾT TIẾP ENHANCEMENT 3 ---
# def save_learning_history(user_id, episode_id, score, duration):
#     pass
#
# def get_user_dashboard_data(user_id):
#     pass
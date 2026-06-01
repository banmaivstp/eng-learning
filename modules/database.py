import streamlit as st
from config import supabase
from datetime import datetime, date

def upsert_user_profile(user_data: dict):
    """Đồng bộ thông tin đăng nhập Google của học viên vào bảng public.profiles"""
    if supabase:
        try:
            profile_payload = {
                "id": user_data["id"], # UUID từ auth
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "avatar_url": user_data["avatar_url"]
            }
            # Sử dụng schema public tường minh để tránh lỗi định tuyến
            supabase.table("profiles").upsert(profile_payload).execute()
        except Exception as db_err:
            st.warning(f"Lưu thông tin profile lỗi nhẹ: {db_err}")

def save_learning_history(user_id: str, episode_id: str, score: int, duration_seconds: int):
    """
    Lưu lịch sử làm bài vào public.learning_history và cập nhật chuỗi ngày học 
    vào bảng public.user_streaks chuẩn định dạng UUID.
    """
    if not supabase:
        raise Exception("Kết nối cơ sở dữ liệu Supabase chưa được cấu hình!")

    # --- 1. GHI LỊCH SỬ BÀI LÀM (learning_history) ---
    # Chú ý: episode_id phải truyền vào chuỗi định dạng UUID hợp lệ lấy từ bảng episodes
    history_data = {
        "user_id": user_id,             
        "episode_id": episode_id,     
        "score": int(score),
        "duration_seconds": int(duration_seconds),
        "completed_at": datetime.now().isoformat()
    }
    
    try:
        history_res = supabase.table("learning_history").insert(history_data).execute()
        if not history_res.data:
            raise Exception("Supabase không phản hồi dữ liệu sau khi chèn lịch sử.")
    except Exception as err:
        raise Exception(f"Lỗi chèn dữ liệu bảng public.learning_history: {err}")

    # --- 2. XỬ LÝ CHUỖI NGÀY HỌC TẬP (user_streaks) ---
    today_date = date.today().isoformat()
    
    try:
        # Lấy thông tin Streak hiện tại của User
        streak_res = supabase.table("user_streaks").select("*").eq("user_id", user_id).execute()
        
        current_streak = 0
        longest_streak = 0
        
        if streak_res.data:
            streak_record = streak_res.data[0]
            current_streak = streak_record.get("current_streak", 0) or 0
            longest_streak = streak_record.get("longest_streak", 0) or 0
            last_active_str = streak_record.get("last_active_date")
            
            if last_active_str:
                last_active = date.fromisoformat(last_active_str)
                delta_days = (date.today() - last_active).days
                
                if delta_days == 1:
                    current_streak += 1  # Học tiếp tục ngày hôm sau
                elif delta_days > 1:
                    current_streak = 1   # Bị ngắt quãng chuỗi -> Reset về 1
                # Nếu delta_days == 0 -> Giữ nguyên chuỗi ngày hiện tại
            else:
                current_streak = 1
        else:
            current_streak = 1

        # Cập nhật kỷ lục chuỗi ngày học dài nhất (longest_streak)
        if current_streak > longest_streak:
            longest_streak = current_streak

        # Thực hiện lệnh Upsert vào bảng user_streaks
        streak_payload = {
            "user_id": user_id,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_active_date": today_date
        }
        
        supabase.table("user_streaks").upsert(streak_payload).execute()
        
        # Hiển thị hiệu ứng chúc mừng thành tích học tập
        if current_streak >= 1:
            st.toast(f"🔥 Xuất sắc! Bạn đang giữ chuỗi {current_streak} ngày học liên tục.", icon="🚀")
            
    except Exception as streak_err:
        st.warning(f"Không thể cập nhật chuỗi ngày học (user_streaks): {streak_err}")
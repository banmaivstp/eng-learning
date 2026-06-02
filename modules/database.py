import streamlit as st
from config import supabase
from datetime import datetime, date

def upsert_user_profile(user_data: dict):
    """Đồng bộ thông tin đăng nhập Google của học viên vào bảng public.profiles"""
    if supabase:
        try:
            profile_payload = {
                "id": str(user_data["id"]), 
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "avatar_url": user_data["avatar_url"]
            }
            supabase.table("profiles").upsert(profile_payload).execute()
        except Exception as db_err:
            st.warning(f"Lưu thông tin profile lỗi nhẹ: {db_err}")

def save_learning_history(user_id: str, episode_id: str, score: int, duration_seconds: int):
    """
    Lưu lịch sử làm bài vào public.learning_history và cập nhật chuỗi ngày học 
    vào bảng public.user_streaks.
    """
    if not supabase:
        raise Exception("Kết nối cơ sở dữ liệu Supabase chưa được cấu hình!")

    # Chuyển đổi các ID sang dạng chuỗi (Text) tường minh
    user_id_str = str(user_id)
    episode_id_str = str(episode_id)

    # --- 1. GHI LỊCH SỬ BÀI LÀM (learning_history) ---
    try:
        supabase.table("learning_history").insert({
            "user_id": user_id_str,
            "episode_id": episode_id_str,
            "score": score,
            "duration_seconds": duration_seconds
        }).execute()
        print("[DEBUG] Đã lưu thành công vào learning_history")
    except Exception as e:
        print(f"[DEBUG LỖI] Không thể lưu learning_history: {e}")
        raise e

    # --- 2. TÍNH TOÁN VÀ CẬP NHẬT TỔNG ĐIỂM (profiles.total_score) ---
    current_total_score = 0  # Dòng số 43 của bạn nằm ở đây, giờ đã an toàn ngoài khối try
    try:
        profile_res = supabase.table("profiles").select("total_score").eq("id", user_id_str).execute()
        if profile_res.data:
            current_total_score = profile_res.data[0].get("total_score", 0)
        
        # Cộng dồn điểm mới và cập nhật lại vào bảng profiles
        new_total_score = current_total_score + score
        supabase.table("profiles").update({"total_score": new_total_score}).eq("id", user_id_str).execute()
        print(f"[DEBUG] Đã cập nhật tổng điểm mới: {new_total_score}")
    except Exception as score_err:
        print(f"[DEBUG LỖI] Lỗi cập nhật điểm tích lũy: {score_err}")

    # --- 3. CẬP NHẬT CHUỖI NGÀY HỌC (user_streaks) ---
    try:
        today_str = date.today().isoformat()
        streak_res = supabase.table("user_streaks").select("*").eq("user_id", user_id_str).execute()
        
        if not streak_res.data:
            # Nếu chưa từng có bản ghi streak, tạo mới mặc định ngày đầu tiên
            supabase.table("user_streaks").insert({
                "user_id": user_id_str,
                "current_streak": 1,
                "longest_streak": 1,
                "last_active_date": today_str
            }).execute()
        else:
            streak_data = streak_res.data[0]
            last_date_str = streak_data.get("last_active_date")
            curr_streak = streak_data.get("current_streak", 0)
            long_streak = streak_data.get("longest_streak", 0)
            
            if last_date_str:
                last_active = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                days_diff = (date.today() - last_active).days
                
                if days_diff == 1:
                    # Học liên tiếp ngày hôm sau -> Tăng streak
                    curr_streak += 1
                elif days_diff > 1:
                    # Bị ngắt quãng ngày -> Reset về 1
                    curr_streak = 1
                # Nếu days_diff == 0 (học nhiều bài cùng ngày) -> Giữ nguyên streak
            else:
                curr_streak = 1
                
            if curr_streak > long_streak:
                long_streak = curr_streak
                
            supabase.table("user_streaks").update({
                "current_streak": curr_streak,
                "longest_streak": long_streak,
                "last_active_date": today_str
            }).eq("user_id", user_id_str).execute()
            
    except Exception as streak_err:
        print(f"[DEBUG LỖI] Không thể cập nhật Streak: {streak_err}")
        
# =====================================================================
# MILESTONE 6: CƠ CHẾ CACHE QUIZ & TRANSCRIPT TỪ DATABASE
# =====================================================================
def get_cached_episode_data(episode_id: str) -> dict:
    """
    Kiểm tra xem tập bài học đã được xử lý qua AI và lưu cache chưa.
    Trả về dict chứa audio_url, transcript và quiz_json nếu có, ngược lại trả về None.
    """
    print(f"\n[DEBUG CACHE] >>>>>>>>>> BẮT ĐẦU: Kiểm tra Cache cho Episode ID: {episode_id} <<<<<<<<<<", flush=True)
    if not supabase:
        print("[DEBUG CACHE] ⚠️ Thất bại: Kết nối Supabase chưa được khởi tạo (supabase is None).", flush=True)
        return None
        
    try:
        start_time = datetime.now()
        res = supabase.table("episodes").select("audio_url, transcript, quiz_json").eq("id", str(episode_id)).execute()
        duration = (datetime.now() - start_time).total_seconds()
        
        if res.data:
            record = res.data[0]
            transcript = record.get("transcript")
            quiz_json = record.get("quiz_json")
            
            # Điều kiện trúng cache: Phải có cả transcript và dữ liệu quiz_json
            if transcript and quiz_json:
                print(f"[DEBUG CACHE] 🎉 HIT (Trúng Cache)! Tìm thấy dữ liệu trong DB. Thời gian truy vấn: {duration:.4f} giây.", flush=True)
                print(f"[DEBUG CACHE] - Độ dài Transcript: {len(transcript)} ký tự.", flush=True)
                print(f"[DEBUG CACHE] - Kiểu dữ liệu Quiz ẩn trong DB: {type(quiz_json)}", flush=True)
                print("[DEBUG CACHE] >>>>>>>>>> KẾT THÚC: Kiểm tra Cache thành công <<<<<<<<<<\n", flush=True)
                return {
                    "audio_url": record.get("audio_url"),
                    "transcript": transcript,
                    "quiz_json": quiz_json
                }
            else:
                print(f"[DEBUG CACHE] 💨 MISS (Trượt Cache): Bản ghi tồn tại nhưng transcript hoặc quiz_json bị rỗng.", flush=True)
        else:
            print(f"[DEBUG CACHE] 💨 MISS (Trượt Cache): Không tìm thấy bản ghi nào khớp với ID {episode_id} trong bảng 'episodes'.", flush=True)
            
    except Exception as e:
        print(f"[DEBUG CACHE 🚨 LỖI HỆ THỐNG]: Không thể truy vấn bảng episodes để lấy dữ liệu cache: {str(e)}", flush=True)
        
    print("[DEBUG CACHE] >>>>>>>>>> KẾT THÚC: Luồng kiểm tra trả về trạng thái không có cache <<<<<<<<<<\n", flush=True)
    return None
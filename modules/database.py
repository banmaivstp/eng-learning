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
    vào bảng public.user_streaks theo Thuật toán 20260527.
    """
    if not supabase:
        raise Exception("Kết nối cơ sở dữ liệu Supabase chưa được cấu hình!")

    user_id_str = str(user_id)
    episode_id_str = str(episode_id)
    today_str = date.today().isoformat()

    print(f"\n[DEBUG HISTORY] 📥 Bắt đầu lưu lịch sử học tập...", flush=True)
    print(f"[DEBUG HISTORY] -> User ID: {user_id_str} | Episode ID: {episode_id_str} | Score: {score} | Duration: {duration_seconds}s", flush=True)

    try:
        # --- 1. GHI LỊCH SỬ BÀI LÀM ---
        history_payload = {
            "user_id": user_id_str,
            "episode_id": episode_id_str,
            "score": int(score),
            "duration_seconds": int(duration_seconds)
        }
        hist_res = supabase.table("learning_history").insert(history_payload).execute()
        print(f"[DEBUG HISTORY] ✅ Đã lưu bản ghi vào learning_history thành công.", flush=True)

        # --- 2. XỬ LÝ THUẬT TOÁN STREAK (CHUỖI NGÀY HỌC LIÊN TIẾP 20260527) ---
        print(f"[DEBUG STREAK] 🔥 Bắt đầu tính toán chuỗi Streak cho ngày: {today_str}", flush=True)
        streak_res = supabase.table("user_streaks").select("*").eq("user_id", user_id_str).execute()

        if not streak_res.data:
            print(f"[DEBUG STREAK] 🆕 Chưa có dữ liệu cũ. Tạo mới dòng Streak ban đầu cho User.", flush=True)
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
                print(f"[DEBUG STREAK] -> Ngày học cuối cùng: {last_date_str} (Khoảng cách: {days_diff} ngày)", flush=True)
                
                if days_diff == 1:
                    # Trường hợp 2: Ngày kế tiếp -> Tăng chuỗi ngày học liên tiếp
                    curr_streak += 1
                    print(f"[DEBUG STREAK] -> Tiếp tục chuỗi ngày học liên tiếp! Tăng lên: {curr_streak}", flush=True)
                elif days_diff > 1:
                    # Trường hợp 3: Đứt chuỗi -> Reset tính lại từ đầu
                    curr_streak = 1
                    print(f"[DEBUG STREAK] -> Bị đứt chuỗi ngày liên tiếp. Reset về 1 ngày.", flush=True)
                # Trường hợp 1: days_diff == 0 (Học nhiều bài cùng ngày) -> Giữ nguyên chuỗi ngày học hiện tại
            else:
                curr_streak = 1
                
            if curr_streak > long_streak:
                long_streak = curr_streak
                print(f"[DEBUG STREAK] 🏆 Đạt kỷ lục chuỗi ngày học mới (Longest Streak): {long_streak}", flush=True)
                
            supabase.table("user_streaks").update({
                "current_streak": curr_streak,
                "longest_streak": long_streak,
                "last_active_date": today_str
            }).eq("user_id", user_id_str).execute()
            print(f"[DEBUG STREAK] ✅ Đồng bộ và cập nhật user_streaks thành công.", flush=True)

    except Exception as e:
        print(f"[DEBUG HISTORY 🚨 LỖI]: Quá trình lưu lịch sử / tính streak gặp sự cố: {str(e)}", flush=True)
        raise e

def get_cached_episode_data(episode_id: str) -> dict:
    """Kiểm tra xem tập Podcast đã từng được xử lý qua AI pipeline chưa"""
    if not supabase:
        return None
    try:
        res = supabase.table("episodes").select("audio_url, transcript, quiz_json").eq("id", str(episode_id)).execute()
        if res.data:
            record = res.data[0]
            if record.get("transcript") and record.get("quiz_json"):
                return record
    except Exception:
        pass
    return None

# =====================================================================
# MILESTONE 7: DASHBOARD & ANALYTICS DATA LAYER FUNCTIONS
# =====================================================================

def get_user_analytics(user_id: str) -> dict:
    """
    Truy vấn toàn bộ số liệu học tập thực tế từ Supabase để chuyển đổi thành biểu đồ Dashboard.
    """
    user_id_str = str(user_id)
    print(f"\n[DEBUG ANALYTICS] 📊 Khởi tạo truy vấn phân tích số liệu học tập cho User: {user_id_str}", flush=True)
    
    analytics = {
        "total_episodes": 0,
        "total_minutes": 0.0,
        "total_hours": 0.0,
        "avg_score": 0.0,
        "latest_score": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "weekly_data": [0.0] * 7  # Mảng chứa số phút học từ Thứ 2 -> Chủ Nhật
    }
    
    if not supabase:
        print("[DEBUG ANALYTICS] ⚠️ Hủy truy vấn: Client kết nối Supabase rỗng.", flush=True)
        return analytics

    try:
        # 1. Truy vấn thông tin Streak
        streak_res = supabase.table("user_streaks").select("current_streak, longest_streak").eq("user_id", user_id_str).execute()
        if streak_res.data:
            analytics["current_streak"] = streak_res.data[0].get("current_streak", 0)
            analytics["longest_streak"] = streak_res.data[0].get("longest_streak", 0)
            print(f"[DEBUG ANALYTICS] -> Lấy thành công Streak: {analytics['current_streak']} ngày", flush=True)

        # 2. Truy vấn dữ liệu lịch sử làm bài học
        history_res = supabase.table("learning_history").select("episode_id, score, duration_seconds, completed_at").eq("user_id", user_id_str).order("completed_at", desc=False).execute()
        
        if history_res.data:
            records = history_res.data
            total_records = len(records)
            
            # Đếm tổng số tập bài học khác biệt duy nhất (Distinct)
            distinct_episodes = len(set([r.get("episode_id") for r in records]))
            analytics["total_episodes"] = distinct_episodes
            
            # Tính tổng số giây và điểm số tích lũy
            total_seconds = sum([r.get("duration_seconds") or 0 for r in records])
            total_score = sum([r.get("score") or 0 for r in records])
            
            analytics["total_minutes"] = round(total_seconds / 60, 1)
            analytics["total_hours"] = round(total_seconds / 3600, 2)
            # Tính điểm trung bình quy đổi hệ 10 điểm
            analytics["avg_score"] = round(total_score / total_records, 1) if total_records > 0 else 0.0
            analytics["latest_score"] = records[-1].get("score", 0)
            
            # 3. Phân bổ số phút học tập vào mảng 7 ngày trong tuần (Thứ 2 = Index 0 -> Chủ nhật = Index 6)
            for r in records:
                completed_at_str = r.get("completed_at")
                duration = r.get("duration_seconds") or 0
                if completed_at_str:
                    try:
                        clean_date_str = completed_at_str.split("+")[0]
                        dt = datetime.fromisoformat(clean_date_str)
                        weekday_idx = dt.weekday()  # Monday = 0, Sunday = 6
                        analytics["weekly_data"][weekday_idx] += (duration / 60)
                    except Exception:
                        pass
                        
            analytics["weekly_data"] = [round(m, 1) for m in analytics["weekly_data"]]
            print(f"[DEBUG ANALYTICS] -> Phân bổ thời gian tuần (T2->CN): {analytics['weekly_data']}", flush=True)
            
    except Exception as e:
        print(f"[DEBUG ANALYTICS 🚨 LỖI]: Thất bại khi tổng hợp số liệu: {str(e)}", flush=True)

    print("[DEBUG ANALYTICS] 🏁 Hoàn thành kết xuất dữ liệu phân tích thành công.\n", flush=True)
    return analytics

def evaluate_user_badges(analytics: dict) -> list:
    """
    Xác định danh hiệu đạt được (Badges) dựa trên các cột mốc dữ liệu học tập của học viên.
    """
    badges = []
    
    # Danh hiệu 1: Bước đi đầu tiên
    if analytics["total_episodes"] >= 1:
        badges.append({"icon": "🌱", "name": "First Step", "desc": "Hoàn thành bài tập nghe hiểu đầu tiên thành công."})
    
    # Danh hiệu 2: Mộc sách chăm chỉ (Vượt qua 5 bài khác biệt)
    if analytics["total_episodes"] >= 5:
        badges.append({"icon": "📚", "name": "Bookworm Explorer", "desc": "Kiên trì chinh phục thành công 5 bài học."})
        
    # Danh hiệu 3: Bậc thầy thời gian (Thời gian học tập tích lũy trên 1 giờ)
    if analytics["total_hours"] >= 1.0:
        badges.append({"icon": "⏱️", "name": "Time Master", "desc": "Tích lũy hơn 1 giờ đồng hồ luyện nghe tiếng Anh."})
        
    # Danh hiệu 4: Ngọn lửa rực cháy (Chuỗi ngày học liên tiếp dài từ 3 ngày trở lên)
    if analytics["longest_streak"] >= 3:
        badges.append({"icon": "🔥", "name": "On Fire Streak", "desc": "Giữ vững chuỗi học tập liên tục từ 3 ngày trở lên."})
        
    # Danh hiệu 5: Điểm số hoàn hảo (Có bài học gần nhất đạt điểm tối đa 10/10)
    if analytics["latest_score"] == 10:
        badges.append({"icon": "🏆", "name": "Perfect Score", "desc": "Xuất sắc đạt điểm số 10/10 tuyệt đối trong bài làm."})
        
    return badges
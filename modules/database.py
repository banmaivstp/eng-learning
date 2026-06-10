# ==========================================
# FILE: modules/database.py
# TẦNG MODEL — Truy xuất dữ liệu từ Supabase
# ==========================================
import logging
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st
from config import supabase

logger = logging.getLogger("modules.database")

# =====================================================
# PROFILE LAYER
# =====================================================

def upsert_user_profile(user_data: dict):
    """
    Đồng bộ thông tin user vào bảng users_profile trên Supabase
    """
    if not supabase:
        return

    try:
        payload = {
            "id": str(user_data["id"]),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "avatar_url": user_data.get("avatar_url"),
            "last_sign_in_at": datetime.utcnow().isoformat()
        }

        supabase.table("users_profile").upsert(payload).execute()
        logger.info(f"✅ User synced thành công: {payload['email']}")

    except Exception as e:
        logger.exception(f"upsert_user_profile error: {e}")
        st.warning(f"Lỗi lưu hồ sơ đồng bộ: {e}")


# =====================================================
# STREAK LAYER
# =====================================================

def update_streak(user_id: str):
    if not supabase:
        return

    today = date.today()

    try:
        streak_res = (
            supabase.table("user_streaks")
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
        )

        if not streak_res.data:
            supabase.table("user_streaks").insert({
                "user_id": str(user_id),
                "current_streak": 1,
                "longest_streak": 1,
                "last_active_date": today.isoformat()
            }).execute()
            return

        streak_data = streak_res.data[0]
        last_active_str = streak_data.get("last_active_date")
        current_streak = streak_data.get("current_streak", 0)
        longest_streak = streak_data.get("longest_streak", 0)

        if last_active_str:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        else:
            last_active = None

        if last_active == today:
            return
        elif last_active == today - timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1

        if current_streak > longest_streak:
            longest_streak = current_streak

        supabase.table("user_streaks").update({
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_active_date": today.isoformat()
        }).eq("user_id", str(user_id)).execute()

        logger.info(f"🔥 Streak updated cho user {user_id}: {current_streak} days")

    except Exception as e:
        logger.exception(f"update_streak error: {e}")


# =====================================================
# LEARNING HISTORY LAYER
# =====================================================

def save_learning_history(user_id: str, episode_id: str, score: int, duration_seconds: int = 0):
    if not supabase:
        return

    try:
        payload = {
            "user_id": str(user_id),
            "episode_id": str(episode_id),
            "score": score,
            "duration_seconds": duration_seconds,
            "completed_at": datetime.utcnow().isoformat()
        }

        supabase.table("learning_history").insert(payload).execute()
        logger.info(f"💾 Saved learning history cho user {user_id}")

        update_streak(user_id)

    except Exception as e:
        logger.exception(f"save_learning_history error: {e}")


# =====================================================
# CACHE DATA LAYER
# =====================================================

def get_cached_episode_data(episode_id: str):
    """
    Truy vấn cache episode theo episode_id.
    Chỉ trả về row nếu CẢ HAI transcript VÀ quiz_json đều có dữ liệu.
    """
    if not supabase:
        return None

    try:
        res = (
            supabase.table("episodes")
            .select("audio_url,transcript,quiz_json")
            .eq("id", str(episode_id))
            .execute()
        )

        if not res.data:
            return None

        row = res.data[0]

        if row.get("transcript") and row.get("quiz_json"):
            return row

        return None

    except Exception as e:
        logger.exception(f"get_cached_episode_data error: {e}")
        return None


# =====================================================
# EPISODES LAYER — THÊM MỚI ĐỂ FIX LỖI EPISODE LIST
# =====================================================

def get_episodes_by_show_id(supabase_client, show_id: str) -> list:
    """
    Truy vấn danh sách episodes thuộc một show theo show_id.

    LÝ DO THÊM HÀM NÀY (không sửa code cũ):
    - podcast_list_view.py cần query episodes theo show_id
    - Tập trung logic DB vào tầng Model thay vì rải rác trong View
    - Fix lỗi: show mới thêm có episodes trong DB nhưng View không load được
      vì thiếu hàm Model tập trung, dẫn đến query sai hoặc bị bỏ qua

    Returns:
        list of dicts: [{"id", "title", "audio_url", "created_at"}, ...]
        Trả về [] nếu lỗi hoặc không có episode.
    """
    client = supabase_client or supabase
    if not client:
        logger.warning("get_episodes_by_show_id: No supabase client available.")
        return []

    if not show_id:
        logger.warning("get_episodes_by_show_id: show_id rỗng.")
        return []

    try:
        logger.debug(f"📋 get_episodes_by_show_id: Querying show_id={show_id}")
        res = (
            client.table("episodes")
            .select("id, title, audio_url, created_at")
            .eq("show_id", str(show_id))
            .order("created_at", desc=True)
            .execute()
        )

        episodes = res.data or []
        logger.info(f"✅ get_episodes_by_show_id: {len(episodes)} episodes cho show {show_id}")
        return episodes

    except Exception as e:
        logger.exception(f"get_episodes_by_show_id error: {e}")
        return []


def get_episode_count_by_show_id(supabase_client, show_id: str) -> int:
    """
    Đếm số episodes của một show — dùng head=True để Supabase trả .count chính xác.

    LÝ DO THÊM HÀM NÀY:
    - Bug trong _fetch_shows_from_db(): dùng count="exact" nhưng KHÔNG dùng head=True
      → supabase-py client chỉ populate .count khi dùng head=True hoặc execute() với
      prefer=count header đúng cách. Kết quả: .count = None → episode_count = 0 sai.
    - Tách logic đếm ra Model để View không cần tự query DB.
    """
    client = supabase_client or supabase
    if not client or not show_id:
        return 0

    try:
        res = (
            client.table("episodes")
            .select("id", count="exact")
            .eq("show_id", str(show_id))
            .execute()
        )
        # supabase-py trả về .count khi select với count="exact"
        count = res.count if res.count is not None else len(res.data or [])
        logger.debug(f"📊 get_episode_count_by_show_id: show={show_id} → {count} eps")
        return count

    except Exception as e:
        logger.exception(f"get_episode_count_by_show_id error: {e}")
        return 0


def get_show_by_episode_id(supabase_client, episode_id: str) -> dict:
    """
    Lấy thông tin show (id, title, cover_image) dựa vào episode_id.

    LÝ DO THÊM HÀM NÀY:
    - quiz_detail_view cần hiển thị logo + tên show trong audio player,
      nhưng selected_show từ session_state có thể thiếu cover_image hoặc title
      (tuỳ vào podcast_list_view set key gì khi navigate).
    - Tập trung toàn bộ logic DB vào tầng Model — View không query trực tiếp.
    - Thực hiện JOIN 1 bước: episodes → shows, tránh 2 lần query riêng.

    Returns:
        dict {"id", "title", "cover_image"} hoặc {} nếu lỗi / không tìm thấy.
    """
    client = supabase_client or supabase
    if not client or not episode_id:
        logger.warning("get_show_by_episode_id: thiếu client hoặc episode_id.")
        return {}

    try:
        res = (
            client.table("episodes")
            .select("show_id, shows(id, title, cover_image)")
            .eq("id", str(episode_id))
            .execute()
        )

        if not res.data:
            logger.warning(f"get_show_by_episode_id: không tìm thấy episode {episode_id}")
            return {}

        show_data = res.data[0].get("shows") or {}
        logger.info(f"✅ get_show_by_episode_id: title='{show_data.get('title')}', cover={'✓' if show_data.get('cover_image') else '✗'}")
        return show_data

    except Exception as e:
        logger.exception(f"get_show_by_episode_id error: {e}")
        return {}


# =====================================================
# ANALYTICS ENGINE LAYER (DASHBOARD METRICS)
# =====================================================

def get_user_analytics(user_id: str) -> dict:
    analytics = {
        "streak_days": 0,
        "longest_streak": 0,
        "total_episodes": 0,
        "total_hours": 0.0,
        "avg_score": 0.0,
        "weekly_data": [0.0] * 7,
        "recent_history": []
    }

    if not supabase:
        return analytics

    try:
        streak_res = supabase.table("user_streaks").select("*").eq("user_id", str(user_id)).execute()
        if streak_res.data:
            analytics["streak_days"] = streak_res.data[0].get("current_streak", 0)
            analytics["longest_streak"] = streak_res.data[0].get("longest_streak", 0)

        history_res = (
            supabase.table("learning_history")
            .select("score, duration_seconds, completed_at, episodes(title, show_id, shows(title, cover_image))")
            .eq("user_id", str(user_id))
            .order("completed_at", desc=True)
            .execute()
        )

        if not history_res.data:
            return analytics

        df = pd.DataFrame(history_res.data)

        analytics["total_episodes"] = len(df)
        total_seconds = df["duration_seconds"].sum()
        analytics["total_hours"] = round(total_seconds / 3600, 1)
        analytics["avg_score"] = round(df["score"].mean(), 1) if not df.empty else 0.0

        seen_shows = set()
        recent_list = []
        for _, row in df.iterrows():
            ep = row.get("episodes") or {}
            show_id = ep.get("show_id")
            show_info = ep.get("shows") or {}
            show_title = show_info.get("title") or ep.get("title") or "Bài học không tên"
            cover = show_info.get("cover_image") or ""

            key = show_id or show_title
            if key in seen_shows:
                continue
            seen_shows.add(key)

            completed_dt = row.get("completed_at", "")
            try:
                dt_obj = datetime.fromisoformat(completed_dt.replace("Z", "+00:00"))
                formatted_date = dt_obj.strftime("%d/%m/%Y")
            except Exception:
                formatted_date = str(completed_dt)[:10]

            recent_list.append({
                "show_id":    show_id,
                "show_title": show_title,
                "cover_image": cover,
                "score": int(row["score"]),
                "date": formatted_date
            })
            if len(recent_list) >= 5:
                break
        analytics["recent_history"] = recent_list

        df["completed_at"] = pd.to_datetime(df["completed_at"])
        df["week"] = df["completed_at"].dt.isocalendar().week
        df["year"] = df["completed_at"].dt.isocalendar().year
        df["dow"] = df["completed_at"].dt.dayofweek

        now = datetime.utcnow()
        current_week = now.isocalendar()[1]
        current_year = now.isocalendar()[0]

        weekly = [0.0] * 7
        current_week_df = df[(df["week"] == current_week) & (df["year"] == current_year)]

        for _, row in current_week_df.iterrows():
            weekly[int(row["dow"])] += (row["duration_seconds"] / 60)

        analytics["weekly_data"] = [round(x, 1) for x in weekly]
        return analytics

    except Exception as e:
        logger.exception(f"analytics error: {e}")
        return analytics


# =====================================================
# BADGES SYSTEM LAYER
# =====================================================

def evaluate_user_badges(analytics: dict) -> list:
    badges = []

    if analytics["total_episodes"] >= 1:
        badges.append({
            "icon": "🌱",
            "name": "First Step",
            "desc": "Hoàn thành bài đầu tiên"
        })

    if analytics["total_episodes"] >= 5:
        badges.append({
            "icon": "📚",
            "name": "Bookworm",
            "desc": "Hoàn thành 5 bài học"
        })

    if analytics["total_hours"] >= 1:
        badges.append({
            "icon": "⏱️",
            "name": "Time Master",
            "desc": "Luyện nghe hơn 1 giờ"
        })

    if analytics["longest_streak"] >= 3:
        badges.append({
            "icon": "🔥",
            "name": "Unstoppable",
            "desc": "Duy trì chuỗi học tập 3 ngày"
        })

    return badges

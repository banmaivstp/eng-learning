# ==========================================
# FILE: modules/database.py
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
        # Chuyển ID sang kiểu text tường minh str() tương thích 100% cấu trúc cột TEXT của database cấu hình
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

def get_cached_episode_data(show_url: str, episode_title: str):
    if not supabase:
        return None

    try:
        show_res = supabase.table("shows").select("id").eq("apple_show_url", show_url).execute()
        if not show_res.data:
            return None
        
        show_id = show_res.data[0]["id"]

        ep_res = (
            supabase.table("episodes")
            .select("*")
            .eq("show_id", show_id)
            .eq("title", episode_title)
            .execute()
        )

        if ep_res.data:
            return ep_res.data[0]
        return None

    except Exception as e:
        logger.exception(f"get_cached_episode_data error: {e}")
        return None


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
            .select("score, duration_seconds, completed_at, episodes(title)")
            .eq("user_id", str(user_id))
            .order("completed_at", ascending=False)
            .execute()
        )

        if not history_res.data:
            return analytics

        df = pd.DataFrame(history_res.data)
        
        analytics["total_episodes"] = len(df)
        total_seconds = df["duration_seconds"].sum()
        analytics["total_hours"] = round(total_seconds / 3600, 1)
        analytics["avg_score"] = round(df["score"].mean(), 1) if not df.empty else 0.0

        recent_list = []
        for _, row in df.head(5).iterrows():
            ep_title = row.get("episodes", {}).get("title") if row.get("episodes") else "Bài học không tên"
            completed_dt = row.get("completed_at", "")
            try:
                dt_obj = datetime.fromisoformat(completed_dt.replace("Z", "+00:00"))
                formatted_date = dt_obj.strftime("%d/%m/%Y")
            except:
                formatted_date = str(completed_dt)[:10]

            recent_list.append({
                "title": ep_title,
                "score": int(row["score"]),
                "date": formatted_date
            })
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
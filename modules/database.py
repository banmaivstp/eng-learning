import logging
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from config import supabase

logger = logging.getLogger("modules.database")


# =====================================================
# PROFILE
# =====================================================

def upsert_user_profile(user_data: dict):
    """
    Đồng bộ thông tin user vào bảng users_profile
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

        supabase.table(
            "users_profile"
        ).upsert(
            payload
        ).execute()

        logger.info(
            f"✅ User synced: {payload['email']}"
        )

    except Exception as e:

        logger.exception(
            f"upsert_user_profile error: {e}"
        )

        st.warning(
            f"Lỗi lưu profile: {e}"
        )


# =====================================================
# STREAK
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

            payload = {
                "user_id": str(user_id),
                "current_streak": 1,
                "longest_streak": 1,
                "last_active_date": today.isoformat()
            }

            supabase.table(
                "user_streaks"
            ).insert(
                payload
            ).execute()

            return

        record = streak_res.data[0]

        current_streak = record.get(
            "current_streak",
            0
        )

        longest_streak = record.get(
            "longest_streak",
            0
        )

        last_active_date = record.get(
            "last_active_date"
        )

        if not last_active_date:

            current_streak = 1

        else:

            last_date = pd.to_datetime(
                last_active_date
            ).date()

            days_diff = (
                today - last_date
            ).days

            if days_diff == 0:

                return

            elif days_diff == 1:

                current_streak += 1

            else:

                current_streak = 1

        longest_streak = max(
            longest_streak,
            current_streak
        )

        payload = {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_active_date": today.isoformat()
        }

        (
            supabase.table("user_streaks")
            .update(payload)
            .eq("user_id", str(user_id))
            .execute()
        )

    except Exception as e:

        logger.exception(
            f"update_streak error: {e}"
        )


# =====================================================
# LEARNING HISTORY
# =====================================================

def save_learning_history(
    user_id: str,
    episode_id: str,
    score: int,
    duration_seconds: int
):

    if not supabase:
        raise Exception(
            "Supabase chưa được cấu hình"
        )

    try:

        payload = {
            "user_id": str(user_id),
            "episode_id": str(episode_id),
            "score": score,
            "duration_seconds": duration_seconds,
            "completed_at": datetime.utcnow().isoformat()
        }

        (
            supabase.table("learning_history")
            .insert(payload)
            .execute()
        )

        logger.info(
            f"✅ Saved learning history user={user_id}"
        )

        update_streak(user_id)

    except Exception as e:

        logger.exception(
            f"save_learning_history error: {e}"
        )

        raise


# =====================================================
# EPISODE CACHE
# =====================================================

def get_cached_episode_data(
    episode_id: str
):

    if not supabase:
        return None

    try:

        res = (
            supabase.table("episodes")
            .select(
                "audio_url,transcript,quiz_json"
            )
            .eq("id", str(episode_id))
            .execute()
        )

        if not res.data:
            return None

        row = res.data[0]

        if (
            row.get("transcript")
            and row.get("quiz_json")
        ):
            return row

        return None

    except Exception as e:

        logger.exception(
            f"cache error: {e}"
        )

        return None


# =====================================================
# ANALYTICS
# =====================================================

def get_user_analytics(
    user_id: str
):

    analytics = {
        "current_streak": 0,
        "longest_streak": 0,
        "total_episodes": 0,
        "total_minutes": 0,
        "total_hours": 0.0,
        "avg_score": 0.0,
        "latest_score": 0,
        "weekly_data": [0] * 7
    }

    if not supabase:
        return analytics

    try:

        user_id = str(user_id)

        # STREAK

        streak_res = (
            supabase.table("user_streaks")
            .select(
                "current_streak,longest_streak"
            )
            .eq("user_id", user_id)
            .execute()
        )

        if streak_res.data:

            analytics["current_streak"] = (
                streak_res.data[0].get(
                    "current_streak",
                    0
                )
            )

            analytics["longest_streak"] = (
                streak_res.data[0].get(
                    "longest_streak",
                    0
                )
            )

        # HISTORY

        history_res = (
            supabase.table("learning_history")
            .select(
                "score,duration_seconds,created_at"
            )
            .eq("user_id", user_id)
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        if not history_res.data:

            return analytics

        df = pd.DataFrame(
            history_res.data
        )

        analytics["total_episodes"] = len(df)

        total_seconds = (
            df["duration_seconds"]
            .fillna(0)
            .sum()
        )

        analytics["total_minutes"] = int(
            total_seconds / 60
        )

        analytics["total_hours"] = round(
            total_seconds / 3600,
            1
        )

        analytics["avg_score"] = round(
            df["score"].mean(),
            1
        )

        analytics["latest_score"] = int(
            df.iloc[0]["score"]
        )

        # WEEKLY DATA

        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["created_at"]
        )

        weekly = [0] * 7

        today = datetime.utcnow()

        current_week = (
            today.isocalendar().week
        )

        current_year = today.year

        df["week"] = (
            df["created_at"]
            .dt.isocalendar()
            .week
        )

        df["year"] = (
            df["created_at"]
            .dt.year
        )

        df["dow"] = (
            df["created_at"]
            .dt.dayofweek
        )

        current_week_df = df[
            (df["week"] == current_week)
            &
            (df["year"] == current_year)
        ]

        for _, row in current_week_df.iterrows():

            weekly[
                int(row["dow"])
            ] += (
                row["duration_seconds"] / 60
            )

        analytics["weekly_data"] = [
            round(x, 1)
            for x in weekly
        ]

        return analytics

    except Exception as e:

        logger.exception(
            f"analytics error: {e}"
        )

        return analytics


# =====================================================
# BADGES
# =====================================================

def evaluate_user_badges(
    analytics: dict
):

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
            "name": "On Fire",
            "desc": "Học liên tiếp 3 ngày"
        })

    return badges
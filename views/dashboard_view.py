import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger("views.dashboard_view")


def render_dashboard_screen(user_analytics_data=None):
    """
    Render giao diện Dashboard theo chuẩn mockup Gen Z Dark UI.
    Layout 2 cột: [Dashboard + Streak + Chart + Progress] | [Recent Shows]
    """
    logger.debug("📊 Rendering Dashboard screen — Gen Z UI v2.")

    # =====================================================
    # 1. FALLBACK DATA
    # =====================================================
    if not user_analytics_data:
        logger.warning("⚠️ dashboard_view: Không có analytics data — dùng fallback.")
        user_analytics_data = {
            "streak_count":   0,
            "current_streak": 0,
            "total_episodes": 0,
            "total_hours":    0.0,
            "avg_score":      0.0,
            "average_score":  0.0,
            "weekly_data":    [0.0] * 7,
            "recent_history": [],
        }

    # Lấy giá trị — tương thích cả key cũ lẫn mới từ database.py
    streak         = user_analytics_data.get("current_streak") or user_analytics_data.get("streak_count", 0)
    total_eps      = user_analytics_data.get("total_episodes", 0)
    total_hours    = user_analytics_data.get("total_hours", 0.0)
    avg_score      = user_analytics_data.get("avg_score") or user_analytics_data.get("average_score", 0.0)
    weekly_raw     = user_analytics_data.get("weekly_data", [0.0] * 7)
    recent_history = user_analytics_data.get("recent_history", [])

    # Đảm bảo weekly_data luôn đủ 7 phần tử
    if len(weekly_raw) < 7:
        weekly_raw = list(weekly_raw) + [0.0] * (7 - len(weekly_raw))
    total_minutes = sum(weekly_raw[:7])

    logger.debug(
        f"📊 dashboard_view: streak={streak}, eps={total_eps}, "
        f"hours={total_hours}, avg_score={avg_score}, "
        f"weekly_total={total_minutes:.1f}min, recent_shows={len(recent_history)}"
    )

    # =====================================================
    # 2. LAYOUT — 2 CỘT THEO MOCKUP
    # =====================================================
    col_left, col_right = st.columns([1.15, 0.85], gap="medium")

    # ─────────────────────────────────────────────────
    #  CỘT TRÁI: Dashboard + Streak + Chart + Progress
    # ─────────────────────────────────────────────────
    with col_left:

        # --- HEADER TITLE ---
        st.markdown('<div class="db-title">Dashboard</div>', unsafe_allow_html=True)
        logger.debug("📊 dashboard_view: Rendered header.")

        # --- STREAK CARD ---
        streak_label = f"{streak} Days Streak" if streak > 0 else "Start your streak today!"
        streak_sub   = "Keep it up! You're on fire!" if streak > 0 else "Complete your first lesson to begin."
        st.markdown(f"""
        <div class="db-streak-card">
            <div class="db-streak-left">
                <div class="db-streak-fire-icon">🔥</div>
                <div class="db-streak-text-group">
                    <div class="db-streak-title">{streak_label}</div>
                    <div class="db-streak-sub">{streak_sub}</div>
                </div>
            </div>
            <div class="db-streak-fire-deco">🔥</div>
        </div>
        """, unsafe_allow_html=True)
        logger.debug(f"📊 dashboard_view: Rendered streak card — streak={streak}.")

        # --- STUDY TIME CHART CARD HEADER ---
        st.markdown(f"""
        <div class="db-card">
            <div class="db-card-header">
                <div class="db-card-title">Study Time <span>(minutes)</span></div>
                <div class="db-card-total">Total: {total_minutes:.0f} mins</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- BIỂU ĐỒ ---
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        chart_df = pd.DataFrame({
            "Day":     days,
            "Minutes": [round(v, 1) for v in weekly_raw[:7]]
        })

        try:
            import altair as alt
            logger.debug("📊 dashboard_view: Rendering Altair bar chart (cyan neon).")
            chart = (
                alt.Chart(chart_df)
                .mark_bar(
                    cornerRadiusTopLeft=4,
                    cornerRadiusTopRight=4,
                    color="#00F2FE",
                    opacity=0.9,
                )
                .encode(
                    x=alt.X("Day:N", sort=days, axis=alt.Axis(
                        labelColor="#64748B",
                        tickColor="#1E293B",
                        domainColor="#1E293B",
                        labelFontSize=11,
                        labelFont="Inter, sans-serif",
                    )),
                    y=alt.Y("Minutes:Q", axis=alt.Axis(
                        labelColor="#64748B",
                        tickColor="#1E293B",
                        domainColor="#1E293B",
                        gridColor="rgba(255,255,255,0.04)",
                        labelFontSize=11,
                        labelFont="Inter, sans-serif",
                    )),
                    tooltip=[
                        alt.Tooltip("Day:N", title="Day"),
                        alt.Tooltip("Minutes:Q", title="Minutes", format=".0f"),
                    ],
                )
                .properties(height=180, background="transparent")
                .configure_view(strokeWidth=0, fill="transparent")
            )
            st.altair_chart(chart, use_container_width=True)
            logger.debug(f"📊 dashboard_view: Altair chart rendered — weekly={weekly_raw[:7]}.")
        except Exception as chart_err:
            logger.warning(f"⚠️ dashboard_view: Altair render failed ({chart_err}), fallback to bar_chart.")
            chart_fallback = pd.DataFrame({
                "Day":     days,
                "Minutes": [round(v, 1) for v in weekly_raw[:7]]
            }).set_index("Day")
            st.bar_chart(chart_fallback, height=190, use_container_width=True)

        # --- PROGRESS OVERVIEW TITLE ---
        st.markdown('<div class="db-progress-title">Progress Overview</div>', unsafe_allow_html=True)

        # --- 3 METRIC CARDS ---
        # avg_score từ database.py: thang 0–10 → convert sang %
        avg_pct     = round(avg_score * 10) if avg_score <= 10 else round(avg_score)
        score_label = "Excellent!" if avg_pct >= 80 else ("Good!" if avg_pct >= 60 else "Keep going!")

        m1, m2, m3 = st.columns(3, gap="small")

        with m1:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-icon">📖</div>
                <div class="db-metric-label">LESSONS<br/>COMPLETED</div>
                <div class="db-metric-value">{total_eps}</div>
                <div class="db-metric-delta">+0 this week</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-icon">🎯</div>
                <div class="db-metric-label">AVG.<br/>SCORE</div>
                <div class="db-metric-value">{avg_pct}%</div>
                <div class="db-metric-delta">{score_label}</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-icon">🏆</div>
                <div class="db-metric-label">QUIZZES<br/>COMPLETED</div>
                <div class="db-metric-value">{total_eps}</div>
                <div class="db-metric-delta">+0 this week</div>
            </div>
            """, unsafe_allow_html=True)

        logger.debug(
            f"📊 dashboard_view: Rendered progress overview — "
            f"eps={total_eps}, avg_pct={avg_pct}%."
        )

    # ─────────────────────────────────────────────────
    #  CỘT PHẢI: Recent Shows
    #  FIX 1: Toàn bộ render list NẰM TRONG with col_right (indent đúng)
    #  FIX 2: Dùng st.button() thật thay HTML button để navigate được
    # ─────────────────────────────────────────────────
    with col_right:

        # --- HEADER ---
        st.markdown('<div class="db-discover-title">Recent Shows</div>', unsafe_allow_html=True)

        # --- DANH SÁCH SHOWS — render từng item riêng biệt ---
        if not recent_history:
            st.markdown(
                '<div style="color:#475569; font-size:13px; padding:12px 4px;">'
                '📭 Bạn chưa học bài nào. Hãy bắt đầu ngay!</div>',
                unsafe_allow_html=True
            )
        else:
            for i, show in enumerate(recent_history):
                border_style = (
                    "border-bottom: 1px solid rgba(255,255,255,0.05);"
                    if i < len(recent_history) - 1 else ""
                )
                cover = show.get("cover_image", "")
                thumb_html = (
                    f'<img src="{cover}" style="width:52px;height:52px;border-radius:10px;object-fit:cover;flex-shrink:0;">'
                    if cover else
                    '<div class="db-show-thumb-placeholder">🎧</div>'
                )

                # Dùng st.columns để đặt HTML info (cột trái) và st.button (cột phải) ngang hàng.
                # CSS db-show-row-wrap xóa gap mặc định giữa 2 cột để trông liền mạch.
                col_info, col_btn = st.columns([2.8, 1.2], gap="small")

                with col_info:
                    st.markdown(f"""
                    <div class="db-show-item" style="{border_style}">
                        {thumb_html}
                        <div class="db-show-info">
                            <div class="db-show-title">{show['show_title']}</div>
                            <div class="db-show-episodes">Last: {show['date']} · Score: {show['score']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_btn:
                    st.markdown('<div class="db-learn-btn-wrap">', unsafe_allow_html=True)
                    btn_key = f"db_continue_show_{i}_{show.get('show_id', show['show_title'])}"
                    if st.button("⚡Learn", key=btn_key, use_container_width=False):
                        logger.info(
                            f"🖱️ dashboard_view: User clicked Learn → show='{show['show_title']}' "
                            f"show_id='{show.get('show_id')}'"
                        )
                        st.session_state["selected_show"] = {
                            "id":            show.get("show_id", ""),
                            "title":         show.get("show_title", ""),
                            "cover_image":   show.get("cover_image", None),
                            "episode_count": 0,
                        }
                        st.session_state["current_page"] = "Show Detail"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                logger.debug(f"📊 dashboard_view: Rendered recent show[{i}] = {show['show_title']}")

    logger.info("✅ dashboard_view: Dashboard screen rendered successfully.")

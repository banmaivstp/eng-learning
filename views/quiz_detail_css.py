"""
views/quiz_detail_css.py
=========================
TẦNG STYLE ĐỘC LẬP — CSS cho màn hình Quiz Detail (Audio Player + Transcript + Quiz).

Quy tắc:
    - File này CHỈ chứa CSS, không chứa logic hay UI render.
    - Được import và gọi từ views/quiz_detail_view.py hoặc app.py.
    - Tất cả selector dùng prefix "qd-" để tránh xung đột với màn hình khác.
    - Bao gồm cả patch CSS v20260606 (fix back button overlap, player height, radio options).
"""

import streamlit as st


def inject_quiz_detail_css():
    """Inject toàn bộ CSS cho màn hình Quiz Detail."""
    st.markdown("""
    <style>
    /* =============================================
       QD — PLAYER SECTION
    ============================================= */
    .qd-player-section {
        margin-bottom: 10px;
    }

    /* =============================================
       QD — TRANSCRIPT SECTION
    ============================================= */
    .qd-transcript-section {
        margin-bottom: 10px;
    }
    .qd-section-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .qd-section-icon { font-size: 15px; }
    .qd-section-title {
        font-size: 14px;
        font-weight: 700;
        color: #E2E8F0;
    }

    .qd-transcript-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 10px 12px;
        max-height: 220px;
        overflow-y: auto;
    }
    .qd-transcript-box::-webkit-scrollbar { width: 4px; }
    .qd-transcript-box::-webkit-scrollbar-track { background: transparent; }
    .qd-transcript-box::-webkit-scrollbar-thumb { background: rgba(0,242,254,0.2); border-radius: 2px; }

    .qd-sentence-row {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 5px 6px;
        border-radius: 6px;
        margin-bottom: 2px;
        cursor: pointer;
        transition: background 0.15s;
    }
    .qd-sentence-active {
        background: rgba(0,242,254,0.10);
        border-left: 2px solid #00F2FE;
    }
    .qd-sentence-inactive { border-left: 2px solid transparent; }
    .qd-sentence-inactive:hover { background: rgba(255,255,255,0.03); }

    .qd-timestamp {
        font-size: 10px;
        font-weight: 700;
        color: #00F2FE;
        white-space: nowrap;
        margin-top: 2px;
        min-width: 32px;
    }
    .qd-sentence-text {
        font-size: 13px;
        color: #CBD5E1;
        line-height: 1.5;
    }
    .qd-sentence-active .qd-sentence-text { color: #F1F5F9; font-weight: 600; }

    .qd-sentence-progress {
        text-align: center;
        padding: 4px 0;
    }
    .qd-sentence-progress-label {
        font-size: 11px;
        color: #475569;
        font-weight: 600;
    }

    /* =============================================
       QD — QUIZ SECTION
    ============================================= */
    .qd-quiz-section {
        margin-bottom: 10px;
    }
    .qd-quiz-progress-label {
        font-size: 12px;
        color: #64748B;
        margin-left: auto;
        font-weight: 600;
    }
    .qd-quiz-progress {
        margin-bottom: 8px;
    }
    .qd-quiz-progress-bar {
        height: 3px;
        background: rgba(255,255,255,0.07);
        border-radius: 2px;
        overflow: hidden;
    }
    .qd-quiz-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00F2FE, #4FACFE);
        border-radius: 2px;
        transition: width 0.3s ease;
    }

    .qd-question-text {
        font-size: 14px;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.55;
        margin-bottom: 10px;
        padding: 10px 12px;
        background: rgba(0,242,254,0.04);
        border: 1px solid rgba(0,242,254,0.10);
        border-radius: 10px;
    }

    /* Options container */
    .qd-quiz-options-container {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 10px;
    }

    /* Streamlit button overrides for quiz options */
    .qd-quiz-options-container div[data-testid="stButton"] button {
        text-align: left !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        white-space: normal !important;
        height: auto !important;
        line-height: 1.4 !important;
    }

    .qd-quiz-nav {
        display: flex;
        gap: 8px;
        margin-top: 6px;
    }

    /* =============================================
       QD — SUBMIT PREVIEW
    ============================================= */
    .qd-submit-preview {
        text-align: center;
        padding: 20px 16px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(0,242,254,0.12);
        border-radius: 14px;
        margin-bottom: 12px;
    }
    .qd-submit-icon { font-size: 32px; margin-bottom: 6px; }
    .qd-submit-title {
        font-size: 18px;
        font-weight: 800;
        color: #F1F5F9;
        margin-bottom: 4px;
    }
    .qd-submit-sub {
        font-size: 13px;
        color: #64748B;
    }

    /* =============================================
       QD — RESULT CARD
    ============================================= */
    .qd-result-card {
        text-align: center;
        padding: 20px 16px 16px 16px;
        background: linear-gradient(135deg, rgba(0,242,254,0.06) 0%, rgba(10,20,40,0.95) 100%);
        border: 1px solid rgba(0,242,254,0.18);
        border-radius: 16px;
        margin-bottom: 14px;
    }
    .qd-result-icon { font-size: 36px; margin-bottom: 6px; }
    .qd-result-score {
        font-size: 42px;
        font-weight: 900;
        color: #00F2FE;
        line-height: 1;
        margin-bottom: 4px;
    }
    .qd-result-label {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 4px;
    }
    .qd-result-detail {
        font-size: 13px;
        color: #64748B;
    }

    /* Answer review cards */
    .qd-answer-card {
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 6px;
        border: 1px solid transparent;
    }
    .qd-answer-correct {
        background: rgba(34, 197, 94, 0.07);
        border-color: rgba(34, 197, 94, 0.20);
    }
    .qd-answer-wrong {
        background: rgba(239, 68, 68, 0.07);
        border-color: rgba(239, 68, 68, 0.20);
    }
    .qd-answer-q {
        font-size: 13px;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 4px;
        line-height: 1.4;
    }
    .qd-answer-detail {
        font-size: 12px;
        color: #94A3B8;
        margin-bottom: 3px;
    }
    .qd-answer-explain {
        font-size: 12px;
        color: #64748B;
        font-style: italic;
    }

    /* =============================================
       QD — EMPTY QUIZ
    ============================================= */
    .qd-empty-quiz {
        text-align: center;
        padding: 30px 16px;
        font-size: 14px;
        color: #475569;
    }

    /* =============================================
       QD — PATCH v20260606
       Fix: back button overlap, player iframe height,
            radio option text alignment
    ============================================= */

    /* Đảm bảo back button không bị overlap bởi player iframe */
    div[data-testid="stButton"] button[kind="secondary"][data-key="qd_back_btn"],
    div[data-testid="stButton"] button[kind="secondary"][data-key="qd_back_no_ep"] {
        position: relative !important;
        z-index: 10 !important;
        margin-bottom: 8px !important;
    }

    /* Fix iframe player height — tránh bị cắt nội dung */
    iframe[title="streamlit_component"] {
        min-height: 142px !important;
    }

    /* Radio / option buttons: căn trái, không uppercase */
    .qd-quiz-options-container div[data-testid="stButton"] button {
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

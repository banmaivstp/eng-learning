import streamlit as st
import logging

logger = logging.getLogger("views.show_list_css")

# =====================================================
# SHOW LIST VIEW CSS — TÁCH ĐỘC LẬP TỪ views/styles.py
# Prefix CSS: "sl-" (show_list) — không conflict với pl-, db-, sb-
# Quy tắc: CHỈ THÊM MỚI — KHÔNG thay đổi code cũ
# =====================================================


def inject_show_list_css():
    """
    Inject CSS riêng cho màn hình Your Podcast Library (show_list_view).
    Sử dụng prefix 'sl-' cho tất cả class names để tránh conflict với
    các CSS đã có (.pl-, .db-, .sb-, v.v.).
    CHỈ THÊM MỚI — không sửa inject_global_css(), inject_sidebar_css(),
    inject_dashboard_css(), inject_podcast_list_css().
    """
    logger.debug("🎨 Injecting Show List CSS (sl- prefix) — Milestone 2.")
    st.markdown("""
    <style>
        /* =====================================================
           PAGE HEADER — "Your Podcast Library"
        ===================================================== */
        .sl-page-header {
            margin-bottom: 20px;
            padding-bottom: 4px;
        }
        .sl-page-title {
            font-size: 28px;
            font-weight: 800;
            color: #F1F5F9 !important;
            letter-spacing: -0.6px;
            line-height: 1.15;
            margin-bottom: 4px;
        }
        .sl-page-sub {
            font-size: 14px;
            color: #64748B !important;
            font-weight: 400;
        }

        /* =====================================================
           SHOW CARD — Grid item (desktop 2 cột)
           Prefix sl- để không đụng .pl-show-card cũ
        ===================================================== */
        .sl-show-card {
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 16px 18px;
            position: relative;
            cursor: pointer;
            transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
            min-height: 88px;
            box-sizing: border-box;
            margin-bottom: 2px;
        }
        .sl-show-card:hover {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.06) !important;
        }

        /* Cover image thumbnail */
        .sl-show-thumb {
            width: 72px;
            height: 72px;
            border-radius: 12px;
            object-fit: cover;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        /* Fallback placeholder emoji */
        .sl-show-thumb-placeholder {
            width: 72px;
            height: 72px;
            border-radius: 12px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(0,242,254,0.10) 0%, rgba(79,172,254,0.06) 100%);
            border: 1px solid rgba(0,242,254,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
        }

        /* Text block bên phải thumbnail */
        .sl-show-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow: hidden;
        }
        .sl-show-title {
            font-size: 15px;
            font-weight: 700;
            color: #F1F5F9 !important;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .sl-show-episodes {
            font-size: 13px;
            font-weight: 600;
            color: #00F2FE !important;
            letter-spacing: 0.1px;
        }

        /* Nút ⋯ góc phải trên card */
        .sl-show-more-btn {
            position: absolute;
            top: 12px;
            right: 12px;
            color: #3A5068 !important;
            font-size: 18px;
            line-height: 1;
            cursor: pointer;
            padding: 4px 6px;
            border-radius: 6px;
            transition: color 0.15s ease, background 0.15s ease;
        }
        .sl-show-more-btn:hover {
            color: #00F2FE !important;
            background: rgba(0,242,254,0.08);
        }

        /* =====================================================
           OPEN BUTTON — Streamlit button overlay trên card
           Dùng kỹ thuật negative margin-top giống sidebar nav
        ===================================================== */
        .sl-card-wrapper .stButton > button {
            opacity: 0 !important;
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            z-index: 5 !important;
        }
        .sl-card-wrapper {
            position: relative;
        }

        /* =====================================================
           EMPTY STATE
        ===================================================== */
        .sl-empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #475569 !important;
        }
        .sl-empty-icon { font-size: 52px; margin-bottom: 16px; }
        .sl-empty-title {
            font-size: 18px;
            font-weight: 700;
            color: #94A3B8 !important;
            margin-bottom: 8px;
        }
        .sl-empty-sub {
            font-size: 14px;
            color: #475569 !important;
            line-height: 1.5;
        }

        /* =====================================================
           SEARCH INPUT — Override Streamlit text_input style
           chỉ trong context màn hình show list
        ===================================================== */
        /* Không override global — chỉ nhắm vào block-container context */

        /* =====================================================
           ADD SHOW EXPANDER — Style riêng cho Show List
        ===================================================== */
        .sl-add-row {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(0, 242, 254, 0.04);
            border: 1px solid rgba(0, 242, 254, 0.15);
            border-radius: 14px;
            margin-bottom: 16px;
        }
        .sl-add-icon { font-size: 18px; }
        .sl-add-label {
            font-size: 13.5px;
            font-weight: 600;
            color: #00F2FE !important;
        }

        /* =====================================================
           SECTION LABEL — "Your Shows", "Recently Added" v.v.
        ===================================================== */
        .sl-section-label {
            font-size: 13px;
            font-weight: 700;
            color: #475569 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin: 8px 0 12px 2px;
        }

        /* =====================================================
           CARD WRAPPER — bao ngoài card HTML + button overlay
           Đảm bảo button Streamlit được ẩn hoàn toàn và
           overlay chính xác lên card (position: relative + absolute)
        ===================================================== */
        .sl-card-wrapper {
            position: relative !important;
            display: block !important;
            margin-bottom: 12px !important;
        }
        /* Ẩn button Streamlit bên trong sl-card-wrapper:
           opacity:0 giữ nguyên vùng click, text "_" không hiển thị */
        .sl-card-wrapper > div[data-testid="stButton"],
        .sl-card-wrapper div[data-testid="stButton"] {
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 10 !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"] > button,
        .sl-card-wrapper div[data-testid="stButton"] > button {
            opacity: 0 !important;
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 16px !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            z-index: 10 !important;
            font-size: 0 !important;
            color: transparent !important;
        }
        /* Đặt card HTML lên trước button nhưng pointer-events:none
           để click xuyên qua HTML card xuống button overlay */
        .sl-card-wrapper .sl-show-card {
            pointer-events: none !important;
            margin-bottom: 0 !important;
            position: relative !important;
            z-index: 1 !important;
        }
        /* Hover effect vẫn hoạt động qua CSS :has() selector */
        .sl-card-wrapper:hover .sl-show-card {
            background: rgba(0, 242, 254, 0.04) !important;
            border-color: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.06) !important;
        }

        /* =====================================================
           COVER IMAGE ENHANCED — Gradient overlay cho fallback
        ===================================================== */
        .sl-show-thumb-placeholder {
            background: linear-gradient(135deg,
                rgba(79, 172, 254, 0.15) 0%,
                rgba(0, 242, 254, 0.08) 50%,
                rgba(147, 51, 234, 0.10) 100%) !important;
            border: 1px solid rgba(0, 242, 254, 0.15) !important;
        }
        /* Cover image có shadow để nổi hơn trên nền tối */
        .sl-show-thumb {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        }

        /* =====================================================
           PAGE HEADER — Căn chỉnh theo mockup:
           Title + subtitle bên trái, search bar bên phải
           (Streamlit không cho layout inline nên dùng flexbox
            trên sl-page-header + ẩn mặc định search input vào row)
        ===================================================== */
        .sl-page-title {
            font-size: 32px !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #F1F5F9 0%, #CBD5E1 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            letter-spacing: -0.8px !important;
            line-height: 1.1 !important;
            margin-bottom: 6px !important;
        }
        .sl-page-sub {
            font-size: 14px !important;
            color: #475569 !important;
            font-weight: 400 !important;
            margin-bottom: 20px !important;
        }

        /* =====================================================
           SEARCH INPUT — Override Streamlit text_input style
           Target theo data-testid của input có key="sl_search_input"
        ===================================================== */
        [data-testid="stTextInput"] input[aria-label="Search shows"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #F1F5F9 !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
        }
        [data-testid="stTextInput"] input[aria-label="Search shows"]:focus {
            border-color: rgba(0, 242, 254, 0.35) !important;
            box-shadow: 0 0 0 3px rgba(0, 242, 254, 0.08) !important;
        }
        [data-testid="stTextInput"] input[aria-label="Search shows"]::placeholder {
            color: #475569 !important;
        }

        /* =====================================================
           GRID ROW — Đảm bảo gap giữa 2 cột card đồng đều
        ===================================================== */
        .sl-card-wrapper + .sl-card-wrapper {
            margin-top: 0 !important;
        }

        /* =====================================================
           EXPANDER (Add Show) — Style theo mockup
        ===================================================== */
        [data-testid="stExpander"] {
            background: rgba(0, 242, 254, 0.02) !important;
            border: 1px solid rgba(0, 242, 254, 0.10) !important;
            border-radius: 14px !important;
            margin-bottom: 16px !important;
        }
        [data-testid="stExpander"] summary {
            color: #00F2FE !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
        }

        /* =====================================================
           FIX v3 — SHOW CARD OPEN BUTTON
           Quy tắc: CHỈ THÊM MỚI — không sửa CSS cũ phía trên.

           Vấn đề cũ: invisible button overlay gây click sai vùng.
           Giải pháp mới: button Streamlit hiển thị thật, style thành
           nút nhỏ gọn nằm dưới card, màu neon phù hợp dark UI.
        ===================================================== */

        /* --- SHOW CARD: margin-bottom nhỏ hơn để không kéo cách xa button --- */
        .sl-show-card {
            margin-bottom: 4px !important;
            pointer-events: auto !important;  /* card HTML không cần pointer-events:none nữa */
            cursor: default !important;
        }

        /* --- OPEN BUTTON: style nút mở show — nằm ngay dưới card --- */
        /* Target nút có label bắt đầu bằng "▶ Open" trong context show list */
        [data-testid="stMainBlockContainer"] button[kind="secondary"]:is([data-testid="stBaseButton-secondary"]) {
            /* Reset về mặc định trước — override CSS ẩn cũ nếu còn sót */
            opacity: 1 !important;
            position: static !important;
            height: auto !important;
            min-height: 36px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #00F2FE !important;
            background: rgba(0, 242, 254, 0.06) !important;
            border: 1px solid rgba(0, 242, 254, 0.20) !important;
            border-radius: 10px !important;
            padding: 6px 14px !important;
            margin-top: 0 !important;
            margin-bottom: 14px !important;
            cursor: pointer !important;
            letter-spacing: 0.1px !important;
            transition: background 0.15s ease, border-color 0.15s ease !important;
        }
        [data-testid="stMainBlockContainer"] button[kind="secondary"]:is([data-testid="stBaseButton-secondary"]):hover {
            background: rgba(0, 242, 254, 0.12) !important;
            border-color: rgba(0, 242, 254, 0.40) !important;
            color: #ffffff !important;
        }

        /* --- WRAPPER CŨ sl-card-wrapper: reset để không ảnh hưởng nếu còn sót --- */
        .sl-card-wrapper {
            position: static !important;
        }
        .sl-card-wrapper .sl-show-card {
            pointer-events: auto !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"],
        .sl-card-wrapper div[data-testid="stButton"] {
            position: static !important;
            width: 100% !important;
            height: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: auto !important;
        }
        .sl-card-wrapper > div[data-testid="stButton"] > button,
        .sl-card-wrapper div[data-testid="stButton"] > button {
            opacity: 1 !important;
            position: static !important;
            height: auto !important;
            min-height: 36px !important;
        }

        /* =====================================================
           FIX v3 — SIDEBAR NAV BUTTON OVERLAP
           Vấn đề: margin-top:-58px kéo button quá cao, overlap
           sang item phía trên → click "Discover" bị hiểu là "Quiz".

           Giải pháp: Giảm margin-top về đúng chiều cao nav-item
           thực tế = 46px (padding 13px*2 + line-height ~20px).
           Đồng thời clamp height button bằng height nav-item.
        ===================================================== */
        [data-testid="stSidebar"] .stButton {
            margin-top: -46px !important;  /* khớp với min-height nav-item thực tế */
            height: 46px !important;
            overflow: hidden !important;   /* chặn vùng click tràn ra ngoài */
            z-index: 5 !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            height: 46px !important;
            min-height: 0 !important;
            max-height: 46px !important;
            overflow: hidden !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ Show List CSS (sl-) injected successfully — v3: card open-btn fix + sidebar overlap fix.")


def inject_show_list_card_button_css():
    """
    CSS v4 — Show card click fix (card HTML + button overlay).

    Chiến lược:
    - Mỗi card = 1 div HTML (visual) + 1 st.button ngay bên dưới
    - st.button bị kéo lên đè lên card bằng margin-top âm
    - Button opacity:0 → không nhìn thấy, nhưng vẫn nhận click
    - overflow:hidden trên wrapper ngăn vùng click tràn ra ngoài
    - Chiều cao card thực = padding 16px*2 + content ~58px ≈ 90px
      → margin-top: -90px, height: 90px

    QUY TẮC: CHỈ THÊM MỚI — không sửa CSS cũ trong styles.py
    Prefix class: sl-v4- để không conflict với sl- cũ
    """
    logger.debug("🎨 show_list_css: Injecting Card CSS v4.")
    st.markdown("""
    <style>
        /* =====================================================
           SHOW CARD v4 — Invisible overlay button
           Kỹ thuật: HTML card (visual) + button ẩn đè lên trên

           CRITICAL: Chỉ target button bên trong .sl-v4-card-wrap
           KHÔNG target sidebar buttons (đã bảo vệ bằng :not selector)
        ===================================================== */

        /* Wrapper bao ngoài: relative để button con dùng absolute */
        .sl-v4-card-wrap {
            position: relative !important;
            display: block !important;
            width: 100% !important;
            margin-bottom: 14px !important;
        }

        /* Card HTML: pointer-events none → click xuyên qua xuống button */
        .sl-v4-card-wrap .sl-show-card {
            pointer-events: none !important;
            margin-bottom: 0 !important;
            position: relative !important;
            z-index: 1 !important;
        }

        /* Hover effect qua parent selector */
        .sl-v4-card-wrap:hover .sl-show-card {
            background: rgba(0, 242, 254, 0.05) !important;
            border-color: rgba(0, 242, 254, 0.22) !important;
            box-shadow: 0 0 22px rgba(0, 242, 254, 0.07) !important;
        }
        .sl-v4-card-wrap:active .sl-show-card {
            background: rgba(0, 242, 254, 0.09) !important;
            border-color: rgba(0, 242, 254, 0.35) !important;
        }

        /* stButton wrapper bên trong sl-v4-card-wrap:
           absolute, phủ toàn bộ vùng card, z-index cao hơn card HTML */
        .sl-v4-card-wrap > div[data-testid="stButton"],
        .sl-v4-card-wrap .stButton {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 10 !important;
            pointer-events: auto !important;
        }

        /* Button element: trong suốt, phủ toàn bộ wrapper */
        .sl-v4-card-wrap > div[data-testid="stButton"] > button,
        .sl-v4-card-wrap .stButton > button {
            opacity: 0 !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 16px !important;
            background: transparent !important;
            box-shadow: none !important;
            cursor: pointer !important;
            z-index: 10 !important;
            font-size: 0 !important;
            color: transparent !important;
            pointer-events: auto !important;
        }

        /* =====================================================
           BẢO VỆ SIDEBAR BUTTONS — không bị ảnh hưởng
           sidebar buttons đã được inject_sidebar_css() style sẵn
        ===================================================== */
        [data-testid="stSidebar"] .sl-v4-card-wrap {
            display: none !important; /* sidebar không có card-wrap */
        }

        /* =====================================================
           STREAMLIT COLUMN GAP — đảm bảo 2 cột card đều nhau
        ===================================================== */
        .sl-v4-card-wrap + .sl-v4-card-wrap {
            margin-top: 0 !important;
        }

        /* =====================================================
           CARD v4 — COLUMNS LAYOUT (giống dashboard Recent Shows)
           sl-show-card bỏ pointer-events trick, chỉ còn visual.
           Nút mở nằm trong col_btn riêng, không overlay.
        ===================================================== */

        /* Card visual — reset pointer-events về auto, bỏ hacks cũ */
        .sl-show-card {
            pointer-events: auto !important;
            margin-bottom: 12px !important;
            cursor: default !important;
        }

        /* Căn giữa dọc col_btn (cột chứa nút Open) với col_info bên trái.
           Streamlit render st.columns thành stHorizontalBlock > stColumn.
           Target stColumn cuối (col_btn) để flex-center theo trục dọc. */
        [data-testid="stHorizontalBlock"]:has(.sl-open-btn-wrap)
        > [data-testid="stColumn"]:last-child {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* =====================================================
           OPEN BUTTON — Pill cyan, giống db-learn-btn-wrap
           Bọc bằng div.sl-open-btn-wrap trong _render_show_card_v4
        ===================================================== */
        .sl-open-btn-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding-bottom: 12px;   /* bù margin-bottom của sl-show-card */
        }
        .sl-open-btn-wrap button {
            background: rgba(0, 242, 254, 0.10) !important;
            color: #00F2FE !important;
            border: 1px solid rgba(0, 242, 254, 0.30) !important;
            border-radius: 20px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            padding: 6px 12px !important;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.15) !important;
            min-height: unset !important;
            height: 32px !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            letter-spacing: 0.01em !important;
            width: auto !important;
            transition: background 0.15s ease, border-color 0.15s ease,
                        box-shadow 0.15s ease !important;
        }
        .sl-open-btn-wrap button:hover {
            background: rgba(0, 242, 254, 0.20) !important;
            border-color: rgba(0, 242, 254, 0.55) !important;
            color: #ffffff !important;
            box-shadow: 0 0 18px rgba(0, 242, 254, 0.35) !important;
        }
        .sl-open-btn-wrap button:active {
            background: rgba(0, 242, 254, 0.28) !important;
        }

    </style>
    """, unsafe_allow_html=True)
    logger.debug("✅ show_list_css: Card CSS v4 injected.")
